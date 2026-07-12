import logging

from truagents.observability import Hooks, Request, Response


def _fake_request() -> Request:
    return Request(method="POST", url="https://example.com/", headers={"H": "v"}, body=b"hi")


def _fake_response() -> Response:
    return Response(status_code=200, headers={"Content-Type": "application/json"}, body=b"{}")


class TestNoOpDefaults:
    def test_default_hooks_swallow_all_events(self):
        hooks = Hooks()
        hooks.emit_request(_fake_request())
        hooks.emit_response(_fake_response(), 12.5)
        hooks.emit_error(RuntimeError("boom"), _fake_request())


class TestCallbackInvocation:
    def test_on_request_receives_request(self):
        captured: list[Request] = []
        hooks = Hooks(on_request=captured.append)
        req = _fake_request()
        hooks.emit_request(req)
        assert captured == [req]

    def test_on_response_receives_response_and_elapsed(self):
        captured: list[tuple[Response, float]] = []
        hooks = Hooks(on_response=lambda r, e: captured.append((r, e)))
        resp = _fake_response()
        hooks.emit_response(resp, 42.0)
        assert captured == [(resp, 42.0)]

    def test_on_error_receives_exception_and_request(self):
        captured: list[tuple[Exception, Request]] = []
        hooks = Hooks(on_error=lambda exc, req: captured.append((exc, req)))
        exc = ValueError("nope")
        req = _fake_request()
        hooks.emit_error(exc, req)
        assert captured == [(exc, req)]


class TestExceptionSwallowing:
    def test_broken_on_request_does_not_raise(self, caplog):
        def broken(_: Request) -> None:
            raise RuntimeError("hook broke")

        hooks = Hooks(on_request=broken)
        with caplog.at_level(logging.WARNING, logger="truagents.observability"):
            hooks.emit_request(_fake_request())
        assert any("on_request hook raised" in rec.message for rec in caplog.records)

    def test_broken_on_response_does_not_raise(self, caplog):
        def broken(_: Response, __: float) -> None:
            raise RuntimeError("hook broke")

        hooks = Hooks(on_response=broken)
        with caplog.at_level(logging.WARNING, logger="truagents.observability"):
            hooks.emit_response(_fake_response(), 1.0)
        assert any("on_response hook raised" in rec.message for rec in caplog.records)

    def test_broken_on_error_does_not_raise(self, caplog):
        def broken(_: Exception, __: Request) -> None:
            raise RuntimeError("hook broke")

        hooks = Hooks(on_error=broken)
        with caplog.at_level(logging.WARNING, logger="truagents.observability"):
            hooks.emit_error(ValueError(), _fake_request())
        assert any("on_error hook raised" in rec.message for rec in caplog.records)
