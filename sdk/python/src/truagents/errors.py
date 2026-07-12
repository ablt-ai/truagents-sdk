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
from typing import Literal

import httpx


class TruAgentsError(Exception):
    """Base class for all SDK errors."""

    code: str = "TRUAGENTS_ERROR"


class AuthError(TruAgentsError):
    """OAuth-token-endpoint failure. Mirrors RFC 6749 error responses."""

    code = "AUTH_ERROR"

    def __init__(self, http_status: int, error: str, error_description: str) -> None:
        self.http_status = http_status
        self.error = error
        self.error_description = error_description
        super().__init__(
            f"HTTP {http_status} error={error} error_description={error_description}"
        )


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


class RateLimited(APIError):
    code = "RATE_LIMITED"

    def __init__(self, http_status: int, body: str, retry_after: float) -> None:
        self.http_status = http_status
        self.body = body
        self.retry_after = retry_after
        Exception.__init__(
            self,
            f"HTTP {http_status} body={body} retry_after={retry_after}s",
        )


class NotFound(APIError):
    code = "NOT_FOUND"


class InvalidRequest(APIError):
    code = "INVALID_REQUEST"


class ServerError(APIError):
    code = "SERVER_ERROR"


class NetworkError(TruAgentsError):
    code = "NETWORK_ERROR"

    def __init__(self, cause: Exception) -> None:
        self.cause = cause
        super().__init__(f"Network error: {cause}")


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


def classify_http_error(
    response: httpx.Response, kind: Literal["oauth", "api"]
) -> TruAgentsError:
    """Map an HTTP response to the appropriate SDK exception subclass."""
    status = response.status_code
    if kind == "oauth":
        error, description = _extract_oauth_error_fields(response)
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
