# truagents — Python SDK for the TruAgents Unsubscribe API

[![PyPI version](https://img.shields.io/pypi/v/truagents.svg)](https://pypi.org/project/truagents/)
[![Python versions](https://img.shields.io/pypi/pyversions/truagents.svg)](https://pypi.org/project/truagents/)
[![CI](https://github.com/ablt-ai/truagents-sdk/actions/workflows/contract-python.yml/badge.svg)](https://github.com/ablt-ai/truagents-sdk/actions/workflows/contract-python.yml)

Official Python SDK for the [TruAgents Unsubscribe API](https://docs.truagents.com).
Handles OAuth token acquisition and refresh, retries, rate limiting, and
observability so you can focus on the business logic.

## Install

```bash
pip install truagents
```

Requires Python `>= 3.11`.

## Quickstart (sync)

```python
from truagents import Client

with Client(client_id="...", client_secret="...") as client:
    resp = client.list_email_unsubscribes()
    for record in resp.data:
        print(record.email, record.unsubscribed)
```

## Quickstart (async)

```python
import asyncio

from truagents import AsyncClient


async def main() -> None:
    async with AsyncClient(client_id="...", client_secret="...") as client:
        resp = await client.list_email_unsubscribes()
        for record in resp.data:
            print(record.email, record.unsubscribed)


asyncio.run(main())
```

## Authentication

`TokenManager` (owned by the client) mints an access token via
`client_credentials` on the first request and refreshes it via `refresh_token`
`refresh_threshold_seconds` before the server-side expiry (default: 60s).
Concurrent callers are de-duplicated: a thundering herd of sync threads or
async coroutines results in a single `/oauth/token` round-trip.

If the cached refresh token is rejected with `invalid_grant` (RFC 6749 §5.2
family revoke), the manager transparently drops it and re-mints via
`client_credentials`. Partners never see the intermediate `InvalidGrant`.

**A mid-flight `TokenExpired` (HTTP 401) on an API endpoint is NOT
auto-remedied.** It signals that your credentials were revoked externally and
you need to investigate. This is a deliberate design decision — silently
re-minting on 401 would mask real revocations.

## Retries + rate limiting

Every request goes through a shared `RetryPolicy`:

| Failure                          | Retry?                                    |
|----------------------------------|-------------------------------------------|
| `NetworkError`                   | Yes — up to `max_attempts` with exp. back-off |
| `ServerError` (5xx)              | Yes — up to `max_attempts` with exp. back-off |
| `RateLimited` (HTTP 429)         | Yes — honours `Retry-After` (capped at 60s) |
| `InvalidRequest` (HTTP 400)      | No                                        |
| `NotFound` (HTTP 404)            | No                                        |
| `TokenExpired` (HTTP 401)        | No                                        |

Override defaults by constructing your own `RetryPolicy`:

```python
from truagents import Client, RetryPolicy

policy = RetryPolicy(max_attempts=5, base_delay=0.1, retry_after_cap=30.0)
client = Client(client_id="...", client_secret="...", retry=policy)
```

## Observability hooks

`Hooks` fire around every HTTP call (token endpoint and API endpoint alike).
Broken hooks never break an SDK call — they are logged and swallowed.

```python
from truagents import Client, Hooks
from truagents.observability import Request, Response


def log_request(req: Request) -> None:
    print(f"-> {req.method} {req.url}")


def log_response(resp: Response, elapsed_ms: float) -> None:
    print(f"<- {resp.status_code} ({elapsed_ms:.0f}ms)")


hooks = Hooks(on_request=log_request, on_response=log_response)
client = Client(client_id="...", client_secret="...", hooks=hooks)
```

## Error handling

All SDK exceptions inherit from `truagents.errors.TruAgentsError`.

| Exception            | Raised when                                        |
|----------------------|----------------------------------------------------|
| `AuthError`          | Base of OAuth token endpoint failures.             |
| `InvalidClient`      | Token endpoint returned 401 (bad client_id/secret). |
| `InvalidGrant`       | Token endpoint returned 400 `invalid_grant`. Almost always caught + recovered internally. |
| `TokenExpired`       | API endpoint returned 401 (external revocation).    |
| `APIError`           | Base of API endpoint failures.                     |
| `InvalidRequest`     | API endpoint returned 400.                         |
| `NotFound`           | API endpoint returned 404.                         |
| `RateLimited`        | API endpoint returned 429. Carries `retry_after`.  |
| `ServerError`        | API endpoint returned 5xx.                         |
| `NetworkError`       | Transport failure (DNS, connection reset, timeout). Wraps the underlying `httpx` exception. |

Every subclass carries a `code` class variable (e.g. `"INVALID_CLIENT"`) so
you can log it without importing the class.

## Version stability

The SDK is at `0.x`. Minor bumps may introduce breaking changes. See
[`docs/versioning.md`](../../docs/versioning.md) at the repository root for
the full policy and the `1.0.0` promotion criteria.

## Links

- Homepage: <https://github.com/ablt-ai/truagents-sdk>
- Docs: <https://docs.truagents.com>
- Issues: <https://github.com/ablt-ai/truagents-sdk/issues>
- License: Apache 2.0 (see [`LICENSE`](../../LICENSE))
