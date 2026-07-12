"""Configurable retry policy for transient HTTP failures.

Retries `NetworkError`, `ServerError`, and `RateLimited` up to `max_attempts`
following the retry policy. `NetworkError` and `ServerError` back off with
exponential backoff (`base_delay * 2**(attempt - 1)`, capped at `max_delay`).
`RateLimited` honours the server's `Retry-After` header, capped at
`retry_after_cap`. Never retries 4xx other than 429. Token-refresh recovery is
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
        """Exponential backoff for `NetworkError` / `ServerError`, capped at `max_delay`."""
        return min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Return True when the caller should retry.

        Retries `NetworkError`, `RateLimited`, and `ServerError` up to
        `max_attempts` total calls. `RateLimited` follows the same
        `max_attempts` budget as the transport-level failures — the
        `retry_after_cap` on `next_delay` bounds server-instructed sleeps so
        repeated 429s cannot produce pathological waits. All other 4xx
        responses (`InvalidRequest`, `NotFound`, `TokenExpired`, `AuthError`,
        …) return False immediately.
        """
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
        """Return seconds to sleep before the next attempt.

        `RateLimited` honours the server-supplied `Retry-After` value (already
        parsed into `retry_after`), clamped to `[0, retry_after_cap]`. Other
        retryable errors use `compute_backoff(attempt)`.
        """
        if isinstance(error, errors.RateLimited):
            return min(max(error.retry_after, 0.0), self.retry_after_cap)
        return self.compute_backoff(attempt)


DEFAULT_RETRY_POLICY = RetryPolicy()
