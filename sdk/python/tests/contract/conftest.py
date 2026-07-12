from __future__ import annotations

import os

import pytest


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    return value if value else None


@pytest.fixture(scope="session")
def client_id() -> str:
    value = _env("CLIENT_ID")
    if not value:
        pytest.skip("CLIENT_ID missing — contract tests need staging credentials")
    return value


@pytest.fixture(scope="session")
def client_secret() -> str:
    value = _env("CLIENT_SECRET")
    if not value:
        pytest.skip("CLIENT_SECRET missing — contract tests need staging credentials")
    return value


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "https://api.dev-truagents.com")
