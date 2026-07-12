from __future__ import annotations

import asyncio
import concurrent.futures

import httpx
import pytest
import respx
import time_machine

from truagents import errors
from truagents.auth import TokenManager
from truagents.observability import Hooks, Request, Response

BASE_URL = "https://api.dev-truagents.com"


def _token_body(access_token: str, refresh_token: str | None = "R1", expires_in: int = 3600) -> dict:
    body = {"access_token": access_token, "token_type": "Bearer", "expires_in": expires_in}
    if refresh_token is not None:
        body["refresh_token"] = refresh_token
    return body


def _make_manager(**overrides) -> TokenManager:
    kwargs = {
        "client_id": "cid",
        "client_secret": "sec",
        "base_url": BASE_URL,
    }
    kwargs.update(overrides)
    return TokenManager(**kwargs)


class TestSyncPositivePath:
    @respx.mock
    def test_fresh_mint_uses_client_credentials(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        mgr = _make_manager()
        assert mgr.get_access_token() == "A1"
        assert route.called
        request = route.calls[0].request
        assert b"grant_type=client_credentials" in request.content
        assert b"client_id=cid" in request.content
        mgr.close()

    @respx.mock
    def test_cache_hit_avoids_second_post(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        mgr = _make_manager()
        assert mgr.get_access_token() == "A1"
        assert mgr.get_access_token() == "A1"
        assert route.call_count == 1
        mgr.close()

    @respx.mock
    def test_stale_cache_triggers_refresh(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            side_effect=[
                httpx.Response(200, json=_token_body("A1", refresh_token="R1", expires_in=120)),
                httpx.Response(200, json=_token_body("A2", refresh_token="R2", expires_in=120)),
            ]
        )
        mgr = _make_manager(refresh_threshold_seconds=60.0)
        with time_machine.travel(0.0, tick=False) as traveller:
            assert mgr.get_access_token() == "A1"
            traveller.shift(90)
            assert mgr.get_access_token() == "A2"
        assert route.call_count == 2
        second_body = route.calls[1].request.content
        assert b"grant_type=refresh_token" in second_body
        assert b"refresh_token=R1" in second_body
        mgr.close()


class TestSyncFamilyRevoke:
    @respx.mock
    def test_invalid_grant_on_refresh_falls_back_to_client_credentials(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            side_effect=[
                httpx.Response(200, json=_token_body("A1", refresh_token="R1", expires_in=120)),
                httpx.Response(400, json={"error": "invalid_grant", "error_description": "reused"}),
                httpx.Response(200, json=_token_body("A2", refresh_token="R2", expires_in=120)),
            ]
        )
        mgr = _make_manager(refresh_threshold_seconds=60.0)
        with time_machine.travel(0.0, tick=False) as traveller:
            assert mgr.get_access_token() == "A1"
            traveller.shift(90)
            assert mgr.get_access_token() == "A2"
        assert route.call_count == 3
        mgr.close()

    @respx.mock
    def test_invalid_grant_followed_by_invalid_client_surfaces_invalid_client(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(
            side_effect=[
                httpx.Response(200, json=_token_body("A1", refresh_token="R1", expires_in=120)),
                httpx.Response(400, json={"error": "invalid_grant", "error_description": "reused"}),
                httpx.Response(401, json={"error": "invalid_client", "error_description": "bad secret"}),
            ]
        )
        mgr = _make_manager(refresh_threshold_seconds=60.0)
        with time_machine.travel(0.0, tick=False) as traveller:
            assert mgr.get_access_token() == "A1"
            traveller.shift(90)
            with pytest.raises(errors.InvalidClient):
                mgr.get_access_token()
        mgr.close()


class TestSyncFailures:
    @respx.mock
    def test_fresh_mint_failure_surfaces_invalid_client(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(401, json={"error": "invalid_client", "error_description": "bad"}),
        )
        mgr = _make_manager()
        with pytest.raises(errors.InvalidClient):
            mgr.get_access_token()
        mgr.close()

    @respx.mock
    def test_network_error_surfaces_network_error(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(side_effect=httpx.ConnectError("dns"))
        mgr = _make_manager()
        with pytest.raises(errors.NetworkError):
            mgr.get_access_token()
        mgr.close()

    @respx.mock
    def test_missing_access_token_field_surfaces_auth_error(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json={"expires_in": 3600}),
        )
        mgr = _make_manager()
        with pytest.raises(errors.AuthError) as excinfo:
            mgr.get_access_token()
        assert excinfo.value.error == "malformed_response"
        mgr.close()


class TestSyncConcurrency:
    @respx.mock
    def test_ten_threads_produce_one_token_post(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        mgr = _make_manager()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(lambda _: mgr.get_access_token(), range(10)))
        assert results == ["A1"] * 10
        assert route.call_count == 1
        mgr.close()


class TestAsyncPositivePath:
    @respx.mock
    async def test_fresh_mint_uses_client_credentials(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        mgr = _make_manager()
        assert await mgr.get_access_token_async() == "A1"
        assert route.called
        await mgr.aclose()

    @respx.mock
    async def test_cache_hit_avoids_second_post(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        mgr = _make_manager()
        await mgr.get_access_token_async()
        await mgr.get_access_token_async()
        assert route.call_count == 1
        await mgr.aclose()

    @respx.mock
    async def test_stale_cache_triggers_refresh(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            side_effect=[
                httpx.Response(200, json=_token_body("A1", refresh_token="R1", expires_in=120)),
                httpx.Response(200, json=_token_body("A2", refresh_token="R2", expires_in=120)),
            ]
        )
        mgr = _make_manager(refresh_threshold_seconds=60.0)
        with time_machine.travel(0.0, tick=False) as traveller:
            assert await mgr.get_access_token_async() == "A1"
            traveller.shift(90)
            assert await mgr.get_access_token_async() == "A2"
        assert route.call_count == 2
        second_body = route.calls[1].request.content
        assert b"grant_type=refresh_token" in second_body
        await mgr.aclose()


class TestAsyncFamilyRevoke:
    @respx.mock
    async def test_invalid_grant_on_refresh_falls_back_to_client_credentials(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            side_effect=[
                httpx.Response(200, json=_token_body("A1", refresh_token="R1", expires_in=120)),
                httpx.Response(400, json={"error": "invalid_grant", "error_description": "reused"}),
                httpx.Response(200, json=_token_body("A2", refresh_token="R2", expires_in=120)),
            ]
        )
        mgr = _make_manager(refresh_threshold_seconds=60.0)
        with time_machine.travel(0.0, tick=False) as traveller:
            assert await mgr.get_access_token_async() == "A1"
            traveller.shift(90)
            assert await mgr.get_access_token_async() == "A2"
        assert route.call_count == 3
        await mgr.aclose()


class TestAsyncConcurrency:
    @respx.mock
    async def test_ten_coroutines_produce_one_token_post(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        mgr = _make_manager()
        results = await asyncio.gather(*[mgr.get_access_token_async() for _ in range(10)])
        assert results == ["A1"] * 10
        assert route.call_count == 1
        await mgr.aclose()


class TestHooksInvocation:
    @respx.mock
    def test_on_request_and_on_response_fire_around_token_post(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(200, json=_token_body("A1"))
        )
        requests: list[Request] = []
        responses: list[tuple[Response, float]] = []
        hooks = Hooks(
            on_request=requests.append,
            on_response=lambda r, e: responses.append((r, e)),
        )
        mgr = _make_manager(hooks=hooks)
        mgr.get_access_token()
        assert len(requests) == 1 and requests[0].url == f"{BASE_URL}/oauth/token"
        assert len(responses) == 1 and responses[0][0].status_code == 200
        mgr.close()

    @respx.mock
    def test_on_error_fires_on_transport_failure(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(side_effect=httpx.ConnectError("dns"))
        seen: list[tuple[Exception, Request]] = []
        hooks = Hooks(on_error=lambda exc, req: seen.append((exc, req)))
        mgr = _make_manager(hooks=hooks)
        with pytest.raises(errors.NetworkError):
            mgr.get_access_token()
        assert len(seen) == 1
        assert isinstance(seen[0][0], errors.NetworkError)
        mgr.close()

    @respx.mock
    def test_token_response_body_is_redacted_in_hooks(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(
            return_value=httpx.Response(
                200, json=_token_body("SUPER-SECRET-TOKEN", refresh_token="SUPER-SECRET-REFRESH")
            )
        )
        responses: list[Response] = []
        hooks = Hooks(on_response=lambda r, _elapsed: responses.append(r))
        mgr = _make_manager(hooks=hooks)
        mgr.get_access_token()
        assert len(responses) == 1
        body = responses[0].body
        assert b"SUPER-SECRET-TOKEN" not in body
        assert b"SUPER-SECRET-REFRESH" not in body
        assert b"access_token" not in body
        assert body == b"<redacted: token endpoint response>"
        mgr.close()


class TestExpireNowEscapeHatch:
    @respx.mock
    def test_expire_now_forces_next_call_to_refresh(self):
        route = respx.post(f"{BASE_URL}/oauth/token").mock(
            side_effect=[
                httpx.Response(200, json=_token_body("A1", refresh_token="R1", expires_in=3600)),
                httpx.Response(200, json=_token_body("A2", refresh_token="R2", expires_in=3600)),
            ]
        )
        mgr = _make_manager()
        assert mgr.get_access_token() == "A1"
        mgr._expire_now()
        assert mgr.get_access_token() == "A2"
        assert route.call_count == 2
        assert b"grant_type=refresh_token" in route.calls[1].request.content
        mgr.close()
