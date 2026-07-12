"""Runnable positive-flow demo of the TruAgents Python SDK.

Steps:
  1. Read CLIENT_ID / CLIENT_SECRET / BASE_URL from env.
  2. Mint an access token via `client_credentials` (via TokenManager).
  3. GET /api/v1/unsubscribe/email with the fresh token.
  4. Force a rotation by expiring the cache and re-fetching the token.
  5. GET /api/v1/unsubscribe/email with the rotated token.

Exit codes:
  0 — every step OK.
  1 — unexpected outcome.
  2 — env missing.

Usage:
  export CLIENT_ID=...
  export CLIENT_SECRET=...
  python examples/oauth_flow.py
"""

from __future__ import annotations

import os
import sys

from truagents import Client, errors

DEFAULT_BASE_URL = "https://api.dev-truagents.com"


def read_env() -> tuple[str, str, str]:
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    base_url = os.environ.get("BASE_URL", DEFAULT_BASE_URL)
    if not client_id or not client_secret:
        print("Missing CLIENT_ID / CLIENT_SECRET", file=sys.stderr)
        sys.exit(2)
    return client_id, client_secret, base_url


def _prefix(value: str) -> str:
    return f"{value[:12]}..." if value else "<none>"


def main() -> int:
    client_id, client_secret, base_url = read_env()
    print(f"Step 1: env resolved — CLIENT_ID={_prefix(client_id)} BASE_URL={base_url}")

    with Client(
        client_id=client_id, client_secret=client_secret, base_url=base_url
    ) as client:
        try:
            step2_token = client._token_manager.get_access_token()
            print(f"Step 2: mint OK — access_token={_prefix(step2_token)}")

            step3 = client.list_email_unsubscribes()
            print(
                f"Step 3: GET /api/v1/unsubscribe/email OK — items_count={len(step3.data)}"
            )

            client._token_manager._expire_now()
            step4_token = client._token_manager.get_access_token()
            print(f"Step 4: refresh rotation OK — new_token={_prefix(step4_token)}")

            step5 = client.list_email_unsubscribes()
            print(
                f"Step 5: GET with rotated token OK — items_count={len(step5.data)}"
            )
        except errors.TruAgentsError as err:
            print(f"Unexpected error: {err.code} {err}", file=sys.stderr)
            return 1

    print("All 5 positive-flow steps completed as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
