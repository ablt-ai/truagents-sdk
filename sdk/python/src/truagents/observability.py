"""Observability hooks for the TruAgents SDK.

Partners register `on_request`, `on_response`, `on_error` callbacks on a `Hooks`
dataclass; the client fires them around every HTTP call (token endpoint or
resource endpoint). Hook exceptions never propagate — a broken hook must not
break an SDK call.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

_LOGGER = logging.getLogger("truagents.observability")


@dataclass(frozen=True)
class Request:
    """Immutable snapshot of an outgoing request the SDK exposes to hooks."""

    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None


@dataclass(frozen=True)
class Response:
    """Immutable snapshot of an incoming response the SDK exposes to hooks."""

    status_code: int
    headers: dict[str, str]
    body: bytes


RequestHook = Callable[[Request], None]
ResponseHook = Callable[[Response, float], None]
ErrorHook = Callable[[Exception, Request], None]


@dataclass(frozen=True)
class Hooks:
    on_request: RequestHook | None = None
    on_response: ResponseHook | None = None
    on_error: ErrorHook | None = None

    def emit_request(self, req: Request) -> None:
        if self.on_request is None:
            return
        try:
            self.on_request(req)
        except Exception:
            _LOGGER.warning("on_request hook raised — swallowed", exc_info=True)

    def emit_response(self, resp: Response, elapsed_ms: float) -> None:
        if self.on_response is None:
            return
        try:
            self.on_response(resp, elapsed_ms)
        except Exception:
            _LOGGER.warning("on_response hook raised — swallowed", exc_info=True)

    def emit_error(self, exc: Exception, req: Request) -> None:
        if self.on_error is None:
            return
        try:
            self.on_error(exc, req)
        except Exception:
            _LOGGER.warning("on_error hook raised — swallowed", exc_info=True)
