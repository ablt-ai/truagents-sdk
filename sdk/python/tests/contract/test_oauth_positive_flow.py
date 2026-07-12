"""Contract test — runs steps 1-5 of the oauth positive flow via the SDK.

Requires staging credentials (`CLIENT_ID`, `CLIENT_SECRET` env vars). Skips
locally when either is absent; runs in CI where secrets are injected. The
7-step family-revoke regression stays in fenix's internal `oauth-test/`.
"""

from __future__ import annotations

from truagents import Client
from truagents.observability import Hooks, Request


def test_five_step_positive_flow(client_id: str, client_secret: str, base_url: str) -> None:
    token_posts: list[Request] = []
    hooks = Hooks(
        on_request=lambda req: (
            token_posts.append(req)
            if req.url.endswith("/oauth/token")
            else None
        )
    )

    with Client(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url,
        hooks=hooks,
    ) as client:
        first = client.list_email_unsubscribes()
        assert first is not None
        assert isinstance(first.data, list)

        # test/demo escape hatch — not part of public SDK API; do not copy into production
        client._token_manager._expire_now()

        second = client.list_email_unsubscribes()
        assert second is not None
        assert isinstance(second.data, list)

    assert len(token_posts) >= 2, (
        f"expected at least 2 /oauth/token POSTs (mint + refresh), got {len(token_posts)}"
    )
