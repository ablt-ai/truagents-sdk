"""Partner-facing sync and async client wrappers.

Wrap `truagents.generated.AuthenticatedClient` and add:

- Auto-refreshing bearer-token injection via `TokenManager`.
- Retry with exponential backoff for `NetworkError` / `ServerError` and
  `Retry-After`-honouring retry once for `RateLimited`.
- A `User-Agent` header of the form `TruAgents-Python-SDK/{version}`.
- Observability hooks fired around every API request.
- Typed `truagents.errors.*` exceptions on non-2xx responses.

A `TokenExpired` on an API endpoint is NOT auto-remedied at this layer. A
mid-flight 401 signals credentials revoked externally; partners see the typed
exception (frozen contract per PRD).
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

import httpx

from truagents import errors
from truagents.__version__ import __version__
from truagents.auth import TokenManager
from truagents.generated import AuthenticatedClient
from truagents.generated.api.email_unsubscribe import (
    list_email_unsubscribes,
    push_email_unsubscribes,
)
from truagents.generated.api.sms_unsubscribe import (
    list_sms_unsubscribes,
    push_sms_unsubscribes,
)
from truagents.generated.api.voice_unsubscribe import (
    list_phone_unsubscribes,
    push_phone_unsubscribes,
)
from truagents.observability import Hooks, Request, Response
from truagents.retry import DEFAULT_RETRY_POLICY, RetryPolicy

if TYPE_CHECKING:  # pragma: no cover
    from truagents.generated.models.email_unsubscribe_batch_request import (
        EmailUnsubscribeBatchRequest,
    )
    from truagents.generated.models.email_unsubscribe_batch_response import (
        EmailUnsubscribeBatchResponse,
    )
    from truagents.generated.models.email_unsubscribe_list_response import (
        EmailUnsubscribeListResponse,
    )
    from truagents.generated.models.phone_unsubscribe_batch_request import (
        PhoneUnsubscribeBatchRequest,
    )
    from truagents.generated.models.phone_unsubscribe_batch_response import (
        PhoneUnsubscribeBatchResponse,
    )
    from truagents.generated.models.phone_unsubscribe_list_response import (
        PhoneUnsubscribeListResponse,
    )


USER_AGENT_TEMPLATE = "TruAgents-Python-SDK/{version}"
_AUTH_HEADER = "Authorization"


class _ClientBase:
    """Shared configuration surface between `Client` and `AsyncClient`."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = "https://api.truagents.com",
        timeout: float = 30.0,
        retry: RetryPolicy = DEFAULT_RETRY_POLICY,
        hooks: Hooks | None = None,
        token_manager: TokenManager | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retry = retry
        self._hooks = hooks or Hooks()
        self._token_manager = token_manager or TokenManager(
            client_id=client_id,
            client_secret=client_secret,
            base_url=self._base_url,
            timeout=timeout,
            hooks=self._hooks,
        )
        self._authenticated = AuthenticatedClient(
            base_url=self._base_url,
            token="",
            timeout=httpx.Timeout(timeout),
            headers={"User-Agent": self.user_agent},
        )

    @property
    def user_agent(self) -> str:
        return USER_AGENT_TEMPLATE.format(version=__version__)

    def _request_snapshot(self, method_name: str, token: str) -> Request:
        return Request(
            method=method_name,
            url=self._base_url,
            headers={
                "User-Agent": self.user_agent,
                _AUTH_HEADER: f"Bearer {token[:12]}..." if token else "Bearer <none>",
            },
            body=None,
        )

    def _emit_response(self, response: Any, elapsed_ms: float) -> None:
        self._hooks.emit_response(
            Response(
                status_code=int(response.status_code),
                headers=dict(response.headers),
                body=response.content,
            ),
            elapsed_ms,
        )

    def _to_httpx_response(self, response: Any) -> httpx.Response:
        return httpx.Response(
            status_code=int(response.status_code),
            headers=dict(response.headers),
            content=response.content,
        )


class Client(_ClientBase):
    """Synchronous client for the TruAgents Unsubscribe API."""

    def list_email_unsubscribes(self, **params: Any) -> EmailUnsubscribeListResponse:
        return self._call_resource_sync(
            "list_email_unsubscribes",
            lambda client: list_email_unsubscribes.sync_detailed(client=client, **params),
        )

    def push_email_unsubscribes(
        self, batch: EmailUnsubscribeBatchRequest
    ) -> EmailUnsubscribeBatchResponse:
        return self._call_resource_sync(
            "push_email_unsubscribes",
            lambda client: push_email_unsubscribes.sync_detailed(client=client, body=batch),
        )

    def list_sms_unsubscribes(self, **params: Any) -> PhoneUnsubscribeListResponse:
        return self._call_resource_sync(
            "list_sms_unsubscribes",
            lambda client: list_sms_unsubscribes.sync_detailed(client=client, **params),
        )

    def push_sms_unsubscribes(
        self, batch: PhoneUnsubscribeBatchRequest
    ) -> PhoneUnsubscribeBatchResponse:
        return self._call_resource_sync(
            "push_sms_unsubscribes",
            lambda client: push_sms_unsubscribes.sync_detailed(client=client, body=batch),
        )

    def list_voice_unsubscribes(self, **params: Any) -> PhoneUnsubscribeListResponse:
        return self._call_resource_sync(
            "list_voice_unsubscribes",
            lambda client: list_phone_unsubscribes.sync_detailed(client=client, **params),
        )

    def push_voice_unsubscribes(
        self, batch: PhoneUnsubscribeBatchRequest
    ) -> PhoneUnsubscribeBatchResponse:
        return self._call_resource_sync(
            "push_voice_unsubscribes",
            lambda client: push_phone_unsubscribes.sync_detailed(client=client, body=batch),
        )

    def close(self) -> None:
        httpx_client = self._authenticated._client
        if httpx_client is not None:
            httpx_client.close()
        self._token_manager.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _call_resource_sync(self, method_name: str, invoke: Any) -> Any:
        attempt = 0
        while True:
            attempt += 1
            token = self._token_manager.get_access_token()
            self._inject_bearer_sync(token)
            snapshot = self._request_snapshot(method_name, token)
            self._hooks.emit_request(snapshot)
            start = time.time()
            try:
                response = invoke(self._authenticated)
            except httpx.TransportError as exc:
                err = errors.NetworkError(exc)
                self._hooks.emit_error(err, snapshot)
                if not self._retry.should_retry(err, attempt):
                    raise err from exc
                time.sleep(self._retry.next_delay(err, attempt))
                continue
            elapsed_ms = (time.time() - start) * 1000.0
            self._emit_response(response, elapsed_ms)
            if 200 <= int(response.status_code) < 300:
                return response.parsed
            err = errors.classify_http_error(
                self._to_httpx_response(response), "api"
            )
            self._hooks.emit_error(err, snapshot)
            if not self._retry.should_retry(err, attempt):
                raise err
            time.sleep(self._retry.next_delay(err, attempt))

    def _inject_bearer_sync(self, token: str) -> None:
        header_value = f"Bearer {token}"
        client = self._authenticated.get_httpx_client()
        client.headers[_AUTH_HEADER] = header_value
        self._authenticated._headers[_AUTH_HEADER] = header_value


class AsyncClient(_ClientBase):
    """Asynchronous client for the TruAgents Unsubscribe API."""

    async def list_email_unsubscribes(self, **params: Any) -> EmailUnsubscribeListResponse:
        return await self._call_resource_async(
            "list_email_unsubscribes",
            lambda client: list_email_unsubscribes.asyncio_detailed(client=client, **params),
        )

    async def push_email_unsubscribes(
        self, batch: EmailUnsubscribeBatchRequest
    ) -> EmailUnsubscribeBatchResponse:
        return await self._call_resource_async(
            "push_email_unsubscribes",
            lambda client: push_email_unsubscribes.asyncio_detailed(client=client, body=batch),
        )

    async def list_sms_unsubscribes(self, **params: Any) -> PhoneUnsubscribeListResponse:
        return await self._call_resource_async(
            "list_sms_unsubscribes",
            lambda client: list_sms_unsubscribes.asyncio_detailed(client=client, **params),
        )

    async def push_sms_unsubscribes(
        self, batch: PhoneUnsubscribeBatchRequest
    ) -> PhoneUnsubscribeBatchResponse:
        return await self._call_resource_async(
            "push_sms_unsubscribes",
            lambda client: push_sms_unsubscribes.asyncio_detailed(client=client, body=batch),
        )

    async def list_voice_unsubscribes(self, **params: Any) -> PhoneUnsubscribeListResponse:
        return await self._call_resource_async(
            "list_voice_unsubscribes",
            lambda client: list_phone_unsubscribes.asyncio_detailed(client=client, **params),
        )

    async def push_voice_unsubscribes(
        self, batch: PhoneUnsubscribeBatchRequest
    ) -> PhoneUnsubscribeBatchResponse:
        return await self._call_resource_async(
            "push_voice_unsubscribes",
            lambda client: push_phone_unsubscribes.asyncio_detailed(client=client, body=batch),
        )

    async def aclose(self) -> None:
        httpx_client = self._authenticated._async_client
        if httpx_client is not None:
            await httpx_client.aclose()
        await self._token_manager.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    async def _call_resource_async(self, method_name: str, invoke: Any) -> Any:
        attempt = 0
        while True:
            attempt += 1
            token = await self._token_manager.get_access_token_async()
            self._inject_bearer_async(token)
            snapshot = self._request_snapshot(method_name, token)
            self._hooks.emit_request(snapshot)
            start = time.time()
            try:
                response = await invoke(self._authenticated)
            except httpx.TransportError as exc:
                err = errors.NetworkError(exc)
                self._hooks.emit_error(err, snapshot)
                if not self._retry.should_retry(err, attempt):
                    raise err from exc
                await asyncio.sleep(self._retry.next_delay(err, attempt))
                continue
            elapsed_ms = (time.time() - start) * 1000.0
            self._emit_response(response, elapsed_ms)
            if 200 <= int(response.status_code) < 300:
                return response.parsed
            err = errors.classify_http_error(
                self._to_httpx_response(response), "api"
            )
            self._hooks.emit_error(err, snapshot)
            if not self._retry.should_retry(err, attempt):
                raise err
            await asyncio.sleep(self._retry.next_delay(err, attempt))

    def _inject_bearer_async(self, token: str) -> None:
        header_value = f"Bearer {token}"
        client = self._authenticated.get_async_httpx_client()
        client.headers[_AUTH_HEADER] = header_value
        self._authenticated._headers[_AUTH_HEADER] = header_value
