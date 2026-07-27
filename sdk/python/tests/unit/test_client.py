from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from truagents import errors
from truagents.client import AsyncClient, Client
from truagents.generated.models.email_unsubscribe_batch_request import (
    EmailUnsubscribeBatchRequest,
)
from truagents.generated.models.email_unsubscribe_item import EmailUnsubscribeItem
from truagents.generated.models.phone_unsubscribe_batch_request import (
    PhoneUnsubscribeBatchRequest,
)
from truagents.generated.models.phone_unsubscribe_item import PhoneUnsubscribeItem
from truagents.observability import Hooks, Request, Response
from truagents.retry import DEFAULT_RETRY_POLICY, RetryPolicy

BASE_URL = "https://api.dev-truagents.com"


def _token_body(access_token: str = "AT-1", expires_in: int = 3600) -> dict:
    return {
        "access_token": access_token,
        "refresh_token": "R1",
        "token_type": "Bearer",
        "expires_in": expires_in,
    }


def _list_email_body() -> dict:
    return {
        "group_id": "ug_ckxyz123",
        "data": [],
        "next_cursor": None,
        "has_more": False,
    }


def _batch_response_body() -> dict:
    return {"group_id": "ug_ckxyz123", "processed": 0, "updated": []}


def _groups_body() -> dict:
    return {"data": []}


def _email_batch() -> EmailUnsubscribeBatchRequest:
    return EmailUnsubscribeBatchRequest(items=[EmailUnsubscribeItem(email="john@example.com")])


def _phone_batch() -> PhoneUnsubscribeBatchRequest:
    return PhoneUnsubscribeBatchRequest(items=[PhoneUnsubscribeItem(phone="+15551234567")])


class TestBearerAndUserAgent:
    @respx.mock
    def test_bearer_header_present_on_api_request(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body("SECRET-TOKEN")))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        with Client("cid", "sec", base_url=BASE_URL) as client:
            client.list_email_unsubscribes()
        assert api.called
        auth = api.calls[0].request.headers["Authorization"]
        assert auth == "Bearer SECRET-TOKEN"

    @respx.mock
    def test_user_agent_header_present(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        with Client("cid", "sec", base_url=BASE_URL) as client:
            client.list_email_unsubscribes()
        ua = api.calls[0].request.headers["User-Agent"]
        assert ua.startswith("TruAgents-Python-SDK/")


class TestSyncRetry:
    @respx.mock
    def test_retries_5xx_and_succeeds(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            side_effect=[
                httpx.Response(500, text="boom"),
                httpx.Response(500, text="boom"),
                httpx.Response(200, json=_list_email_body()),
            ]
        )
        with patch("truagents.client.time.sleep") as sleep_mock:
            with Client("cid", "sec", base_url=BASE_URL) as client:
                client.list_email_unsubscribes()
        assert api.call_count == 3
        assert sleep_mock.call_count == 2

    @respx.mock
    def test_retry_after_honoured(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            side_effect=[
                httpx.Response(
                    429,
                    headers={"Retry-After": "3.5"},
                    json={"error": "rate_limited"},
                ),
                httpx.Response(200, json=_list_email_body()),
            ]
        )
        with patch("truagents.client.time.sleep") as sleep_mock:
            with Client("cid", "sec", base_url=BASE_URL) as client:
                client.list_email_unsubscribes()
        sleep_mock.assert_called_once_with(3.5)

    @respx.mock
    def test_retry_after_capped(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            side_effect=[
                httpx.Response(
                    429,
                    headers={"Retry-After": "120"},
                    json={"error": "rate_limited"},
                ),
                httpx.Response(200, json=_list_email_body()),
            ]
        )
        policy = RetryPolicy(retry_after_cap=60.0)
        with patch("truagents.client.time.sleep") as sleep_mock:
            with Client("cid", "sec", base_url=BASE_URL, retry=policy) as client:
                client.list_email_unsubscribes()
        sleep_mock.assert_called_once_with(60.0)

    @respx.mock
    def test_no_retry_on_400(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(400, json={"error": "bad", "message": "no"})
        )
        with Client("cid", "sec", base_url=BASE_URL) as client:
            with pytest.raises(errors.InvalidRequest):
                client.list_email_unsubscribes()
        assert api.call_count == 1

    @respx.mock
    def test_token_expired_not_auto_remedied(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(401, json={"error": "token_expired"})
        )
        with Client("cid", "sec", base_url=BASE_URL) as client:
            with pytest.raises(errors.TokenExpired):
                client.list_email_unsubscribes()
        assert api.call_count == 1


class TestSyncHooks:
    @respx.mock
    def test_hooks_fire_around_api_call(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        api_requests: list[Request] = []
        api_responses: list[tuple[Response, float]] = []
        hooks = Hooks(
            on_request=api_requests.append,
            on_response=lambda r, e: api_responses.append((r, e)),
        )
        with Client("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            client.list_email_unsubscribes()
        api_method_events = [r for r in api_requests if r.method == "list_email_unsubscribes"]
        api_response_events = [r for r in api_responses if r[0].status_code == 200]
        assert len(api_method_events) == 1
        assert len(api_response_events) >= 1

    @respx.mock
    def test_on_error_fires_on_4xx(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(return_value=httpx.Response(400, json={"error": "bad"}))
        seen: list[tuple[Exception, Request]] = []
        hooks = Hooks(on_error=lambda exc, req: seen.append((exc, req)))
        with Client("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            with pytest.raises(errors.InvalidRequest):
                client.list_email_unsubscribes()
        assert any(isinstance(exc, errors.InvalidRequest) for exc, _ in seen)


class TestContextManager:
    @respx.mock
    def test_close_closes_httpx_client(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        client = Client("cid", "sec", base_url=BASE_URL)
        client.list_email_unsubscribes()
        underlying = client._authenticated._client
        assert underlying is not None
        client.close()
        assert underlying.is_closed


class TestAsyncClient:
    @respx.mock
    async def test_bearer_and_ua_headers_present(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body("A-TOK")))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        async with AsyncClient("cid", "sec", base_url=BASE_URL) as client:
            await client.list_email_unsubscribes()
        assert api.calls[0].request.headers["Authorization"] == "Bearer A-TOK"
        assert api.calls[0].request.headers["User-Agent"].startswith("TruAgents-Python-SDK/")

    @respx.mock
    async def test_retries_5xx_with_asyncio_sleep_mocked(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            side_effect=[
                httpx.Response(500, text="boom"),
                httpx.Response(200, json=_list_email_body()),
            ]
        )
        with patch("truagents.client.asyncio.sleep", new_callable=AsyncMock) as sleep_mock:
            async with AsyncClient("cid", "sec", base_url=BASE_URL) as client:
                await client.list_email_unsubscribes()
        assert api.call_count == 2
        assert sleep_mock.await_count == 1

    @respx.mock
    async def test_retry_after_honoured_async(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            side_effect=[
                httpx.Response(
                    429,
                    headers={"Retry-After": "2.0"},
                    json={"error": "rate_limited"},
                ),
                httpx.Response(200, json=_list_email_body()),
            ]
        )
        with patch("truagents.client.asyncio.sleep", new_callable=AsyncMock) as sleep_mock:
            async with AsyncClient("cid", "sec", base_url=BASE_URL) as client:
                await client.list_email_unsubscribes()
        sleep_mock.assert_awaited_once_with(2.0)

    @respx.mock
    async def test_no_retry_on_400(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(400, json={"error": "bad"})
        )
        async with AsyncClient("cid", "sec", base_url=BASE_URL) as client:
            with pytest.raises(errors.InvalidRequest):
                await client.list_email_unsubscribes()
        assert api.call_count == 1

    @respx.mock
    async def test_hooks_fire_around_async_call(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        api_requests: list[Request] = []
        hooks = Hooks(on_request=api_requests.append)
        async with AsyncClient("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            await client.list_email_unsubscribes()
        assert any(r.method == "list_email_unsubscribes" for r in api_requests)

    @respx.mock
    async def test_aclose_closes_async_client(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            return_value=httpx.Response(200, json=_list_email_body())
        )
        client = AsyncClient("cid", "sec", base_url=BASE_URL)
        await client.list_email_unsubscribes()
        underlying = client._authenticated._async_client
        assert underlying is not None
        await client.aclose()
        assert underlying.is_closed


_ADD_REMOVE_CASES = [
    ("add_email_unsubscribes", "/api/v1/unsubscribe/email/add", _email_batch),
    ("remove_email_unsubscribes", "/api/v1/unsubscribe/email/remove", _email_batch),
    ("add_sms_unsubscribes", "/api/v1/unsubscribe/sms/add", _phone_batch),
    ("remove_sms_unsubscribes", "/api/v1/unsubscribe/sms/remove", _phone_batch),
    ("add_voice_unsubscribes", "/api/v1/unsubscribe/phone/add", _phone_batch),
    ("remove_voice_unsubscribes", "/api/v1/unsubscribe/phone/remove", _phone_batch),
]


class TestAddRemoveSync:
    @pytest.mark.parametrize(("method_name", "path", "batch"), _ADD_REMOVE_CASES)
    @respx.mock
    def test_add_remove_happy_path(self, method_name, path, batch):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body("SECRET-TOKEN")))
        api = respx.post(f"{BASE_URL}{path}").mock(return_value=httpx.Response(200, json=_batch_response_body()))
        seen: list[Request] = []
        hooks = Hooks(on_request=seen.append)
        with Client("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            result = getattr(client, method_name)(batch())
        assert api.called
        assert result.group_id == "ug_ckxyz123"
        assert api.calls[0].request.headers["Authorization"] == "Bearer SECRET-TOKEN"
        assert api.calls[0].request.headers["User-Agent"].startswith("TruAgents-Python-SDK/")
        assert any(r.method == method_name for r in seen)


class TestAddRemoveAsync:
    @pytest.mark.parametrize(("method_name", "path", "batch"), _ADD_REMOVE_CASES)
    @respx.mock
    async def test_add_remove_happy_path(self, method_name, path, batch):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body("SECRET-TOKEN")))
        api = respx.post(f"{BASE_URL}{path}").mock(return_value=httpx.Response(200, json=_batch_response_body()))
        seen: list[Request] = []
        hooks = Hooks(on_request=seen.append)
        async with AsyncClient("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            result = await getattr(client, method_name)(batch())
        assert api.called
        assert result.group_id == "ug_ckxyz123"
        assert api.calls[0].request.headers["Authorization"] == "Bearer SECRET-TOKEN"
        assert api.calls[0].request.headers["User-Agent"].startswith("TruAgents-Python-SDK/")
        assert any(r.method == method_name for r in seen)


class TestListUnsubscribeGroups:
    @respx.mock
    def test_list_groups_sync(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body("SECRET-TOKEN")))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe-groups").mock(
            return_value=httpx.Response(200, json=_groups_body())
        )
        seen: list[Request] = []
        hooks = Hooks(on_request=seen.append)
        with Client("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            result = client.list_unsubscribe_groups()
        assert api.called
        assert result.data == []
        assert api.calls[0].request.headers["Authorization"] == "Bearer SECRET-TOKEN"
        assert api.calls[0].request.headers["User-Agent"].startswith("TruAgents-Python-SDK/")
        assert any(r.method == "list_unsubscribe_groups" for r in seen)

    @respx.mock
    async def test_list_groups_async(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body("SECRET-TOKEN")))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe-groups").mock(
            return_value=httpx.Response(200, json=_groups_body())
        )
        seen: list[Request] = []
        hooks = Hooks(on_request=seen.append)
        async with AsyncClient("cid", "sec", base_url=BASE_URL, hooks=hooks) as client:
            result = await client.list_unsubscribe_groups()
        assert api.called
        assert result.data == []
        assert api.calls[0].request.headers["Authorization"] == "Bearer SECRET-TOKEN"
        assert any(r.method == "list_unsubscribe_groups" for r in seen)


class TestTransportErrorRetry:
    @respx.mock
    def test_transport_error_retries_then_succeeds(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(
            side_effect=[
                httpx.ConnectError("dns"),
                httpx.Response(200, json=_list_email_body()),
            ]
        )
        with patch("truagents.client.time.sleep") as sleep_mock:
            with Client("cid", "sec", base_url=BASE_URL) as client:
                client.list_email_unsubscribes()
        assert api.call_count == 2
        sleep_mock.assert_called_once()

    @respx.mock
    def test_transport_error_exhausts_and_raises(self):
        respx.post(f"{BASE_URL}/oauth/token").mock(return_value=httpx.Response(200, json=_token_body()))
        api = respx.get(f"{BASE_URL}/api/v1/unsubscribe/email").mock(side_effect=httpx.ConnectError("dns"))
        with patch("truagents.client.time.sleep"):
            with Client("cid", "sec", base_url=BASE_URL) as client:
                with pytest.raises(errors.NetworkError):
                    client.list_email_unsubscribes()
        assert api.call_count == DEFAULT_RETRY_POLICY.max_attempts
