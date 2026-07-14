"""Typed exception hierarchy for the TruAgents SDK.

Two branches under a common `TruAgentsError` base:

- `AuthError` — RFC 6749-style OAuth failures raised by TokenManager.
- `APIError` — HTTP failures raised by resource methods on the client.

`NetworkError` wraps transport-layer exceptions (`httpx.TransportError` etc.).
"""

from __future__ import annotations

import math
import time
from datetime import UTC
from email.utils import parsedate_to_datetime
from typing import Any, Literal

import httpx


class TruAgentsError(Exception):
    """Base class for all SDK errors.

    Subclasses that add typed constructor arguments beyond the base class
    must override `__reduce__` so `pickle.dumps` -> `pickle.loads` reconstructs
    via those arguments. Without `__reduce__`, `Exception.args` carries only
    the formatted message and unpickling calls the subclass with a single
    positional string, dropping the typed fields (or raising `TypeError` for
    multi-arg constructors). See `AuthError.__reduce__`,
    `AuthRateLimited.__reduce__`, `APIError.__reduce__`,
    `RateLimited.__reduce__`, and `NetworkError.__reduce__` for the pattern.
    """

    code: str = "TRUAGENTS_ERROR"


class AuthError(TruAgentsError):
    """OAuth-token-endpoint failure. Mirrors RFC 6749 error responses."""

    code = "AUTH_ERROR"

    def __init__(self, http_status: int, error: str, error_description: str) -> None:
        self.http_status = http_status
        self.error = error
        self.error_description = error_description
        super().__init__(f"HTTP {http_status} error={error} error_description={error_description}")

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        return (type(self), (self.http_status, self.error, self.error_description))


class InvalidClient(AuthError):
    code = "INVALID_CLIENT"


class InvalidGrant(AuthError):
    code = "INVALID_GRANT"


class TokenExpired(AuthError):
    code = "TOKEN_EXPIRED"


class APIError(TruAgentsError):
    """Non-2xx response from a resource endpoint."""

    code = "API_ERROR"

    def __init__(self, http_status: int, body: str) -> None:
        self.http_status = http_status
        self.body = body
        super().__init__(f"HTTP {http_status} body={body}")

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        return (type(self), (self.http_status, self.body))


class RateLimitedMixin:
    """Structural marker for rate-limited errors carrying `Retry-After`.

    Used as a mixin because `RateLimited` must remain under `APIError` and
    `AuthRateLimited` under `AuthError` — no shared concrete base is possible.
    Concrete subclasses assign `retry_after` in their `__init__` and are
    responsible for their own `__reduce__` per `TruAgentsError` policy.
    """

    retry_after: float


class RateLimited(APIError, RateLimitedMixin):
    code = "RATE_LIMITED"

    def __init__(self, http_status: int, body: str, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(http_status, body)

    def __str__(self) -> str:
        return f"HTTP {self.http_status} body={self.body} retry_after={self.retry_after}s"

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        return (type(self), (self.http_status, self.body, self.retry_after))


class AuthRateLimited(AuthError, RateLimitedMixin):
    code = "AUTH_RATE_LIMITED"

    def __init__(
        self,
        http_status: int,
        error: str,
        error_description: str,
        retry_after: float,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(http_status, error, error_description)

    def __str__(self) -> str:
        return (
            f"HTTP {self.http_status} error={self.error} "
            f"error_description={self.error_description} "
            f"retry_after={self.retry_after}s"
        )

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        return (
            type(self),
            (self.http_status, self.error, self.error_description, self.retry_after),
        )


class NotFound(APIError):
    code = "NOT_FOUND"


class InvalidRequest(APIError):
    code = "INVALID_REQUEST"


class ServerError(APIError):
    code = "SERVER_ERROR"


class NetworkError(TruAgentsError):
    """Raised when the transport layer fails to complete a request.

    `cause` carries the underlying `httpx` transport exception. That exception
    may reference the originating request including its POST body (which for
    the token endpoint contains `client_secret`). See `SECURITY.md` §
    "Serialization of exceptions" before serializing a `NetworkError`.
    """

    code = "NETWORK_ERROR"

    def __init__(self, cause: Exception) -> None:
        self.cause = cause
        super().__init__(f"Network error: {cause}")

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        return (type(self), (self.cause,))


def _parse_retry_after(header_value: str | None) -> float:
    """Parse the `Retry-After` header. Returns 0.0 when absent or unparseable.

    Guards against `nan` / `inf` — a malformed 429 with `Retry-After: nan`
    would otherwise flow into `time.sleep(nan)` and raise `ValueError` from
    inside the retry loop as an untyped exception.
    """
    if not header_value:
        return 0.0
    try:
        seconds = float(header_value)
    except ValueError:
        pass
    else:
        if not math.isfinite(seconds):
            return 0.0
        return seconds
    try:
        target = parsedate_to_datetime(header_value)
    except (TypeError, ValueError):
        return 0.0
    if target is None:
        return 0.0
    now = time.time()
    target_ts = target.astimezone(UTC).timestamp()
    return max(target_ts - now, 0.0)


def _decode_body(response: httpx.Response) -> str:
    try:
        return response.text
    except UnicodeDecodeError:
        return response.content.decode(errors="replace")


def _extract_oauth_error_fields(response: httpx.Response) -> tuple[str, str]:
    try:
        body = response.json()
    except ValueError:
        return "unknown_error", ""
    if not isinstance(body, dict):
        return "unknown_error", ""
    return (
        str(body.get("error", "unknown_error")),
        str(body.get("error_description", "")),
    )


def classify_http_error(response: httpx.Response, kind: Literal["oauth", "api"]) -> TruAgentsError:
    """Map an HTTP response to the appropriate SDK exception subclass."""
    status = response.status_code
    if kind == "oauth":
        error, description = _extract_oauth_error_fields(response)
        if status == 429:
            return AuthRateLimited(
                status,
                error,
                description,
                _parse_retry_after(response.headers.get("Retry-After")),
            )
        if status == 400 and error == "invalid_grant":
            return InvalidGrant(status, error, description)
        if status == 401:
            return InvalidClient(status, error, description)
        return AuthError(status, error, description)

    body = _decode_body(response)
    if status == 400:
        return InvalidRequest(status, body)
    if status == 401:
        return TokenExpired(status, "token_expired", body)
    if status == 404:
        return NotFound(status, body)
    if status == 429:
        return RateLimited(status, body, _parse_retry_after(response.headers.get("Retry-After")))
    if 500 <= status < 600:
        return ServerError(status, body)
    return APIError(status, body)
