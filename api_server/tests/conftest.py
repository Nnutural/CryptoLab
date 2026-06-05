"""Shared pytest fixtures: app instance, async HTTP client, throw-away DB."""

from __future__ import annotations

import pytest


@pytest.fixture
def app():
    """FastAPI app instance for tests. TODO: override get_db to use a sqlite-memory."""
    raise NotImplementedError("create_app() with DI overrides for db + redis")


@pytest.fixture
async def client(app):
    """Async HTTP client bound to the test app."""
    raise NotImplementedError("httpx.AsyncClient(app=app, base_url='http://test')")
