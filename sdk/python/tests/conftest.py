"""Shared fixtures for unit tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
import respx


@pytest.fixture
def respx_router() -> Iterator[respx.MockRouter]:
    """Yield a respx.MockRouter that intercepts httpx traffic globally."""
    with respx.mock(base_url="https://api.truagents.com", assert_all_called=False) as router:
        yield router
