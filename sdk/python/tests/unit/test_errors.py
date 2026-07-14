import pickle
from datetime import UTC

import httpx
import pytest

from truagents import errors


def _response(
    status_code: int,
    json_body: dict | None = None,
    text: str | None = None,
    headers: dict | None = None,
) -> httpx.Response:
    if json_body is not None:
        return httpx.Response(status_code, json=json_body, headers=headers or {})
    return httpx.Response(status_code, text=text or "", headers=headers or {})


class TestBaseAndInstantiation:
    def test_truagents_error_is_catchable_as_exception(self):
        with pytest.raises(errors.TruAgentsError):
            raise errors.TruAgentsError("boom")

    def test_auth_error_carries_fields(self):
        err = errors.AuthError(400, "invalid_grant", "refresh reused")
        assert err.http_status == 400
        assert err.error == "invalid_grant"
        assert err.error_description == "refresh reused"
        assert err.code == "AUTH_ERROR"

    def test_invalid_client_and_grant_carry_code(self):
        assert errors.InvalidClient(401, "invalid_client", "").code == "INVALID_CLIENT"
        assert errors.InvalidGrant(400, "invalid_grant", "").code == "INVALID_GRANT"
        assert errors.TokenExpired(401, "token_expired", "").code == "TOKEN_EXPIRED"

    def test_api_error_carries_fields(self):
        err = errors.APIError(500, "boom")
        assert err.http_status == 500
        assert err.body == "boom"
        assert err.code == "API_ERROR"

    def test_rate_limited_carries_retry_after(self):
        err = errors.RateLimited(429, "slow down", retry_after=1.5)
        assert err.http_status == 429
        assert err.body == "slow down"
        assert err.retry_after == 1.5
        assert err.code == "RATE_LIMITED"

    def test_rate_limited_str_includes_retry_after(self):
        err = errors.RateLimited(429, "slow down", retry_after=45.0)
        rendered = str(err)
        assert "429" in rendered
        assert "slow down" in rendered
        assert "retry_after=45.0s" in rendered

    def test_not_found_invalid_request_server_error_codes(self):
        assert errors.NotFound(404, "").code == "NOT_FOUND"
        assert errors.InvalidRequest(400, "").code == "INVALID_REQUEST"
        assert errors.ServerError(500, "").code == "SERVER_ERROR"

    def test_network_error_wraps_cause(self):
        cause = httpx.ConnectError("dns fail")
        err = errors.NetworkError(cause)
        assert err.cause is cause
        assert err.code == "NETWORK_ERROR"

    def test_auth_rate_limited_is_instance_of_rate_limited_mixin(self):
        err = errors.AuthRateLimited(429, "too_many_requests", "x", 5.0)
        assert isinstance(err, errors.RateLimitedMixin)
        assert isinstance(err, errors.AuthError)
        assert err.retry_after == 5.0
        assert err.code == "AUTH_RATE_LIMITED"


class TestClassifyOAuth:
    def test_400_invalid_grant_maps_to_invalid_grant(self):
        resp = _response(400, json_body={"error": "invalid_grant", "error_description": "reused"})
        err = errors.classify_http_error(resp, "oauth")
        assert isinstance(err, errors.InvalidGrant)
        assert err.error == "invalid_grant"

    def test_400_other_error_falls_back_to_auth_error(self):
        resp = _response(400, json_body={"error": "invalid_scope", "error_description": ""})
        err = errors.classify_http_error(resp, "oauth")
        assert type(err) is errors.AuthError
        assert err.error == "invalid_scope"

    def test_401_maps_to_invalid_client(self):
        resp = _response(401, json_body={"error": "invalid_client", "error_description": "bad secret"})
        err = errors.classify_http_error(resp, "oauth")
        assert isinstance(err, errors.InvalidClient)

    def test_other_status_maps_to_auth_error(self):
        resp = _response(500, json_body={"error": "server_error", "error_description": "boom"})
        err = errors.classify_http_error(resp, "oauth")
        assert type(err) is errors.AuthError

    def test_non_json_body_uses_unknown_error(self):
        resp = _response(400, text="not json")
        err = errors.classify_http_error(resp, "oauth")
        assert err.error == "unknown_error"

    def test_429_maps_to_auth_rate_limited(self):
        resp = _response(
            429,
            json_body={"error": "too_many_requests", "error_description": "Slow down"},
            headers={"Retry-After": "42"},
        )
        err = errors.classify_http_error(resp, "oauth")
        assert isinstance(err, errors.AuthRateLimited)
        assert err.http_status == 429
        assert err.error == "too_many_requests"
        assert err.error_description == "Slow down"
        assert err.retry_after == 42.0
        assert err.code == "AUTH_RATE_LIMITED"

    def test_429_no_header_defaults_to_zero_retry_after(self):
        resp = _response(
            429,
            json_body={"error": "too_many_requests", "error_description": "Slow down"},
        )
        err = errors.classify_http_error(resp, "oauth")
        assert isinstance(err, errors.AuthRateLimited)
        assert err.retry_after == 0.0

    def test_429_takes_precedence_over_400_and_401_branches(self):
        resp = _response(
            429,
            json_body={"error": "invalid_grant", "error_description": "reused"},
            headers={"Retry-After": "7"},
        )
        err = errors.classify_http_error(resp, "oauth")
        assert isinstance(err, errors.AuthRateLimited)
        assert not isinstance(err, errors.InvalidGrant)
        assert err.retry_after == 7.0


class TestClassifyAPI:
    def test_400_maps_to_invalid_request(self):
        resp = _response(400, text="bad payload")
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.InvalidRequest)
        assert err.body == "bad payload"

    def test_401_maps_to_token_expired(self):
        resp = _response(401, text="unauth")
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.TokenExpired)

    def test_404_maps_to_not_found(self):
        resp = _response(404, text="nope")
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.NotFound)

    def test_429_with_retry_after_numeric(self):
        resp = _response(429, text="slow", headers={"Retry-After": "5"})
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.RateLimited)
        assert err.retry_after == 5.0

    def test_429_without_retry_after_defaults_to_zero(self):
        resp = _response(429, text="slow")
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.RateLimited)
        assert err.retry_after == 0.0

    def test_429_with_unparseable_retry_after_defaults_to_zero(self):
        resp = _response(429, text="slow", headers={"Retry-After": "not-a-number"})
        err = errors.classify_http_error(resp, "api")
        assert err.retry_after == 0.0

    def test_429_with_nan_retry_after_defaults_to_zero(self):
        resp = _response(429, text="slow", headers={"Retry-After": "nan"})
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.RateLimited)
        assert err.retry_after == 0.0

    def test_429_with_inf_retry_after_defaults_to_zero(self):
        resp = _response(429, text="slow", headers={"Retry-After": "inf"})
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.RateLimited)
        assert err.retry_after == 0.0

    def test_500_maps_to_server_error(self):
        resp = _response(500, text="boom")
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.ServerError)

    def test_502_maps_to_server_error(self):
        resp = _response(502, text="gateway")
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.ServerError)

    def test_418_falls_back_to_generic_api_error(self):
        resp = _response(418, text="tea")
        err = errors.classify_http_error(resp, "api")
        assert type(err) is errors.APIError


class TestRetryAfterHttpDate:
    def test_http_date_produces_positive_delay(self):
        from datetime import datetime, timedelta
        from email.utils import format_datetime

        future = datetime.now(UTC) + timedelta(seconds=10)
        header = format_datetime(future, usegmt=True)
        resp = _response(429, text="slow", headers={"Retry-After": header})
        err = errors.classify_http_error(resp, "api")
        assert isinstance(err, errors.RateLimited)
        assert err.retry_after > 0


class TestPickleRoundTrip:
    def test_auth_error_round_trips(self):
        original = errors.AuthError(400, "invalid_client", "Client not found")
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.AuthError
        assert restored.http_status == 400
        assert restored.error == "invalid_client"
        assert restored.error_description == "Client not found"
        assert str(restored) == str(original)

    def test_invalid_grant_round_trips(self):
        original = errors.InvalidGrant(400, "invalid_grant", "Token expired")
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.InvalidGrant
        assert restored.http_status == 400
        assert restored.error == "invalid_grant"
        assert restored.error_description == "Token expired"

    def test_api_error_round_trips(self):
        original = errors.APIError(500, "server exploded")
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.APIError
        assert restored.http_status == 500
        assert restored.body == "server exploded"

    def test_rate_limited_round_trips(self):
        original = errors.RateLimited(429, "slow down", 45.0)
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.RateLimited
        assert restored.http_status == 429
        assert restored.body == "slow down"
        assert restored.retry_after == 45.0
        assert str(restored) == str(original)

    def test_network_error_round_trips(self):
        original = errors.NetworkError(httpx.ConnectError("boom"))
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.NetworkError
        assert isinstance(restored.cause, httpx.ConnectError)
        assert str(restored.cause) == "boom"

    def test_not_found_inherits_api_error_reduce(self):
        original = errors.NotFound(404, "gone")
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.NotFound

    def test_server_error_inherits_api_error_reduce(self):
        original = errors.ServerError(500, "boom")
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.ServerError

    def test_auth_rate_limited_roundtrips(self):
        original = errors.AuthRateLimited(429, "too_many_requests", "Slow down", 12.5)
        restored = pickle.loads(pickle.dumps(original))
        assert type(restored) is errors.AuthRateLimited
        assert restored.http_status == 429
        assert restored.error == "too_many_requests"
        assert restored.error_description == "Slow down"
        assert restored.retry_after == 12.5
        assert str(restored) == str(original)
