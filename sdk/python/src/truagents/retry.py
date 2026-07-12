"""Configurable retry policy for transient HTTP failures.

Retries `NetworkError` and `ServerError` up to `max_attempts` with exponential
backoff. Retries `RateLimited` once, honouring `Retry-After` capped at
`retry_after_cap`. Never retries 4xx (except 429). Token-refresh recovery is
`TokenManager`'s concern, not this module's.
"""

from __future__ import annotations

from dataclasses import dataclass

from truagents import errors


@dataclass(frozen=True)
class RetryPolicy:
    """Transient-failure retry policy shared by sync and async clients."""

    max_attempts: int = 3
    base_delay: float = 0.25
    max_delay: float = 30.0
    retry_after_cap: float = 60.0

    def compute_backoff(self, attempt: int) -> float:
        return min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)

    def should_retry(self, error: Exception, attempt: int) -> bool:
        if attempt >= self.max_attempts:
            return False
        if isinstance(error, errors.NetworkError):
            return True
        if isinstance(error, errors.RateLimited):
            return True
        if isinstance(error, errors.ServerError):
            return True
        return False

    def next_delay(self, error: Exception, attempt: int) -> float:
        if isinstance(error, errors.RateLimited):
            return min(max(error.retry_after, 0.0), self.retry_after_cap)
        return self.compute_backoff(attempt)


DEFAULT_RETRY_POLICY = RetryPolicy()
