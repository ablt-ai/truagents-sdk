import httpx
import pytest

from truagents import errors
from truagents.retry import DEFAULT_RETRY_POLICY, RetryPolicy


class TestComputeBackoff:
    def test_first_attempt_uses_base_delay(self):
        assert RetryPolicy().compute_backoff(1) == 0.25

    def test_second_attempt_doubles(self):
        assert RetryPolicy().compute_backoff(2) == 0.5

    def test_third_attempt_quadruples(self):
        assert RetryPolicy().compute_backoff(3) == 1.0

    def test_far_attempt_clamps_to_max_delay(self):
        assert RetryPolicy().compute_backoff(20) == 30.0

    def test_custom_max_delay_respected(self):
        policy = RetryPolicy(max_delay=2.0)
        assert policy.compute_backoff(20) == 2.0


class TestShouldRetry:
    def test_network_error_retries(self):
        err = errors.NetworkError(httpx.ConnectError("dns"))
        assert RetryPolicy().should_retry(err, 1) is True
        assert RetryPolicy().should_retry(err, 2) is True

    def test_network_error_stops_after_max_attempts(self):
        err = errors.NetworkError(httpx.ConnectError("dns"))
        assert RetryPolicy(max_attempts=3).should_retry(err, 3) is False

    def test_server_error_retries(self):
        err = errors.ServerError(500, "")
        assert RetryPolicy().should_retry(err, 1) is True
        assert RetryPolicy().should_retry(err, 2) is True

    def test_rate_limited_retries(self):
        err = errors.RateLimited(429, "", retry_after=2.0)
        assert RetryPolicy().should_retry(err, 1) is True

    def test_auth_rate_limited_retries(self):
        err = errors.AuthRateLimited(429, "too_many_requests", "x", 5.0)
        assert RetryPolicy().should_retry(err, 1) is True

    def test_not_found_never_retries(self):
        err = errors.NotFound(404, "")
        assert RetryPolicy().should_retry(err, 1) is False

    def test_invalid_request_never_retries(self):
        err = errors.InvalidRequest(400, "")
        assert RetryPolicy().should_retry(err, 1) is False

    def test_token_expired_never_retries(self):
        err = errors.TokenExpired(401, "token_expired", "")
        assert RetryPolicy().should_retry(err, 1) is False

    def test_generic_exception_never_retries(self):
        assert RetryPolicy().should_retry(ValueError("nope"), 1) is False


class TestNextDelay:
    def test_rate_limited_returns_retry_after(self):
        err = errors.RateLimited(429, "", retry_after=5.0)
        assert RetryPolicy().next_delay(err, 1) == 5.0

    def test_auth_rate_limited_honours_retry_after(self):
        err = errors.AuthRateLimited(429, "too_many_requests", "x", 12.5)
        assert RetryPolicy().next_delay(err, 1) == 12.5

    def test_rate_limited_caps_at_retry_after_cap(self):
        err = errors.RateLimited(429, "", retry_after=120.0)
        assert RetryPolicy().next_delay(err, 1) == 60.0

    def test_rate_limited_negative_becomes_zero(self):
        err = errors.RateLimited(429, "", retry_after=-3.0)
        assert RetryPolicy().next_delay(err, 1) == 0.0

    def test_network_error_uses_exponential_backoff(self):
        err = errors.NetworkError(httpx.ConnectError("dns"))
        policy = RetryPolicy()
        assert policy.next_delay(err, 1) == policy.compute_backoff(1)
        assert policy.next_delay(err, 2) == policy.compute_backoff(2)

    def test_server_error_uses_exponential_backoff(self):
        err = errors.ServerError(500, "")
        policy = RetryPolicy()
        assert policy.next_delay(err, 2) == policy.compute_backoff(2)


def test_default_policy_uses_documented_values():
    assert DEFAULT_RETRY_POLICY.max_attempts == 3
    assert DEFAULT_RETRY_POLICY.base_delay == 0.25
    assert DEFAULT_RETRY_POLICY.retry_after_cap == 60.0


def test_policy_is_frozen():
    with pytest.raises(AttributeError):
        DEFAULT_RETRY_POLICY.max_attempts = 5  # type: ignore[misc]
