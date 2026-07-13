"""OAuth token acquisition, caching, and refresh.

`TokenManager` mints and rotates access tokens against the TruAgents
`/oauth/token` endpoint. It caches the current token in memory and refreshes it
`refresh_threshold_seconds` before the server-side expiry so that a subsequent
caller never blocks on a synchronous token round-trip inside the API request.

Concurrency:

- Sync path (`get_access_token`): `_thread_lock` is held for the entire mint
  sequence including the blocking network POST. Cold-start callers all block
  on lock acquisition; the first caller mints, subsequent callers observe the
  fresh cache and return without a redundant round-trip.
- Async path (`get_access_token_async`): `_async_lock` is held end-to-end
  including the `await`, so concurrent coroutines collapse to a single mint.
  `_thread_lock` is only taken briefly for the initial cache read and the
  final state swap — no `await` inside a `_thread_lock` critical section.

Recovery from family-revoke (RFC 6749 §5.2 `invalid_grant`) is automatic: if a
cached refresh token is rejected, the manager drops it and mints a fresh
`client_credentials` grant transparently. Only the second attempt's outcome
surfaces to the caller.

Observability: the `/oauth/token` response body is never handed to
`on_response` hooks verbatim — it is replaced with a static redaction sentinel
so partner hooks logging `Response.body` cannot leak `access_token` /
`refresh_token`. Status, headers, and timing still flow through unchanged.
"""

from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass

import httpx

from truagents import errors
from truagents.observability import Hooks, Request, Response

DEFAULT_REFRESH_THRESHOLD_SECONDS = 60.0
TOKEN_PATH = "/oauth/token"
_MINT_CLIENT_CREDENTIALS = "client_credentials"
_MINT_REFRESH_TOKEN = "refresh_token"
_REDACTED_TOKEN_BODY = b"<redacted: token endpoint response>"


@dataclass
class _TokenState:
    access_token: str
    refresh_token: str | None
    expires_at: float


class TokenManager:
    """Cache-plus-refresh manager for TruAgents OAuth tokens."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = "https://api.truagents.com",
        timeout: float = 30.0,
        refresh_threshold_seconds: float = DEFAULT_REFRESH_THRESHOLD_SECONDS,
        hooks: Hooks | None = None,
        http_client: httpx.Client | None = None,
        async_http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._refresh_threshold_seconds = refresh_threshold_seconds
        self._hooks = hooks or Hooks()
        self._state: _TokenState | None = None
        self._thread_lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._http_client_provided = http_client is not None
        self._async_http_client_provided = async_http_client is not None
        self._http_client = http_client
        self._async_http_client = async_http_client

    def get_access_token(self) -> str:
        """Return a valid access token, minting or refreshing if needed.

        `_thread_lock` is held for the entire mint sequence so concurrent
        threads on a cold start do not each issue a redundant token POST.
        Subsequent callers with a warm cache acquire the lock, observe a
        fresh `_state`, and release without touching the network.
        """
        with self._thread_lock:
            cached = self._peek_valid_access_token()
            if cached is not None:
                return cached
            refresh_token = self._state.refresh_token if self._state is not None else None
            if refresh_token is not None:
                try:
                    state = self._issue_refresh(refresh_token)
                except errors.InvalidGrant:
                    state = self._issue_client_credentials()
            else:
                state = self._issue_client_credentials()
            self._state = state
            return state.access_token

    async def get_access_token_async(self) -> str:
        """Return a valid access token via the async transport.

        `_async_lock` serialises concurrent coroutines end-to-end so a
        thundering herd of awaits collapses into one network round-trip.
        `_thread_lock` is only taken briefly around state reads/writes and
        never spans an `await`.
        """
        async with self._async_lock:
            with self._thread_lock:
                cached = self._peek_valid_access_token()
                if cached is not None:
                    return cached
                refresh_token = self._state.refresh_token if self._state is not None else None
            if refresh_token is not None:
                try:
                    state = await self._issue_refresh_async(refresh_token)
                except errors.InvalidGrant:
                    state = await self._issue_client_credentials_async()
            else:
                state = await self._issue_client_credentials_async()
            with self._thread_lock:
                self._state = state
            return state.access_token

    def close(self) -> None:
        if self._http_client is not None and not self._http_client_provided:
            self._http_client.close()
            self._http_client = None

    async def aclose(self) -> None:
        if self._async_http_client is not None and not self._async_http_client_provided:
            await self._async_http_client.aclose()
            self._async_http_client = None

    def _expire_now(self) -> None:
        """Test/demo escape hatch — force the next call to refresh or re-mint.

        Not part of the public API. Partners never touch this in production;
        `TokenManager` auto-refreshes at `refresh_threshold_seconds` before the
        server-side expiry. Present so `examples/oauth_flow.py` and contract
        tests can exercise the refresh path without waiting `expires_in`
        seconds.
        """
        with self._thread_lock:
            if self._state is None:
                return
            self._state.expires_at = 0.0

    def _peek_valid_access_token(self) -> str | None:
        """Read cached access token if still fresh. Caller holds `_thread_lock`."""
        state = self._state
        if state is None:
            return None
        if state.expires_at - time.time() < self._refresh_threshold_seconds:
            return None
        return state.access_token

    def _get_or_create_sync_client(self) -> httpx.Client:
        if self._http_client is None:
            self._http_client = httpx.Client(timeout=self._timeout)
        return self._http_client

    def _get_or_create_async_client(self) -> httpx.AsyncClient:
        if self._async_http_client is None:
            self._async_http_client = httpx.AsyncClient(timeout=self._timeout)
        return self._async_http_client

    def _build_form(self, kind: str, *, refresh_token: str | None = None) -> dict[str, str]:
        if kind == _MINT_REFRESH_TOKEN:
            return {
                "grant_type": _MINT_REFRESH_TOKEN,
                "refresh_token": refresh_token or "",
            }
        return {
            "grant_type": _MINT_CLIENT_CREDENTIALS,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

    def _issue_client_credentials(self) -> _TokenState:
        body = self._post_token(self._build_form(_MINT_CLIENT_CREDENTIALS))
        return self._state_from_body(body)

    def _issue_refresh(self, refresh_token: str) -> _TokenState:
        body = self._post_token(self._build_form(_MINT_REFRESH_TOKEN, refresh_token=refresh_token))
        return self._state_from_body(body)

    async def _issue_client_credentials_async(self) -> _TokenState:
        body = await self._post_token_async(self._build_form(_MINT_CLIENT_CREDENTIALS))
        return self._state_from_body(body)

    async def _issue_refresh_async(self, refresh_token: str) -> _TokenState:
        body = await self._post_token_async(
            self._build_form(_MINT_REFRESH_TOKEN, refresh_token=refresh_token),
        )
        return self._state_from_body(body)

    def _post_token(self, form: dict[str, str]) -> dict:
        client = self._get_or_create_sync_client()
        url = f"{self._base_url}{TOKEN_PATH}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        snapshot = Request(method="POST", url=url, headers=headers, body=None)
        self._hooks.emit_request(snapshot)
        start = time.time()
        try:
            response = client.post(url, data=form, headers=headers, timeout=self._timeout)
        except httpx.TransportError as exc:
            err = errors.NetworkError(exc)
            self._hooks.emit_error(err, snapshot)
            raise err from exc
        elapsed_ms = (time.time() - start) * 1000.0
        self._emit_response_snapshot(response, elapsed_ms)
        return self._parse_or_raise(response, snapshot)

    async def _post_token_async(self, form: dict[str, str]) -> dict:
        client = self._get_or_create_async_client()
        url = f"{self._base_url}{TOKEN_PATH}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        snapshot = Request(method="POST", url=url, headers=headers, body=None)
        self._hooks.emit_request(snapshot)
        start = time.time()
        try:
            response = await client.post(url, data=form, headers=headers, timeout=self._timeout)
        except httpx.TransportError as exc:
            err = errors.NetworkError(exc)
            self._hooks.emit_error(err, snapshot)
            raise err from exc
        elapsed_ms = (time.time() - start) * 1000.0
        self._emit_response_snapshot(response, elapsed_ms)
        return self._parse_or_raise(response, snapshot)

    def _emit_response_snapshot(self, response: httpx.Response, elapsed_ms: float) -> None:
        self._hooks.emit_response(
            Response(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=_REDACTED_TOKEN_BODY,
            ),
            elapsed_ms,
        )

    def _parse_or_raise(self, response: httpx.Response, snapshot: Request) -> dict:
        if response.status_code != 200:
            err = errors.classify_http_error(response, "oauth")
            self._hooks.emit_error(err, snapshot)
            raise err
        try:
            body = response.json()
        except ValueError as exc:
            err = errors.AuthError(200, "malformed_response", str(exc))
            self._hooks.emit_error(err, snapshot)
            raise err from exc
        if not isinstance(body, dict):
            err = errors.AuthError(200, "malformed_response", "token response was not a JSON object")
            self._hooks.emit_error(err, snapshot)
            raise err
        return body

    def _state_from_body(self, body: dict) -> _TokenState:
        access_token = self._require_field(body, "access_token")
        expires_in = self._require_field(body, "expires_in")
        try:
            expires_in_seconds = float(expires_in)
        except (TypeError, ValueError) as exc:
            raise errors.AuthError(
                200,
                "malformed_response",
                f"expires_in must be numeric, got {expires_in!r}",
            ) from exc
        refresh_token = body.get("refresh_token")
        return _TokenState(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=time.time() + expires_in_seconds,
        )

    @staticmethod
    def _require_field(body: dict, field_name: str) -> str:
        if field_name not in body:
            raise errors.AuthError(
                200,
                "malformed_response",
                f"token response missing '{field_name}' — got keys={list(body.keys())}",
            )
        return body[field_name]
