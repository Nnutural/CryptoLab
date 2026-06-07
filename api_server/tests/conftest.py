"""Shared pytest fixtures for API tests."""

from __future__ import annotations

import importlib
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
import pytest

from app.db.session import reset_database
from app.main import app

importlib.import_module("app.models")


class FakeRedisCache:
    """fakeredis-backed adapter matching app.core.cache.CacheBackend."""

    def __init__(self) -> None:
        import fakeredis.aioredis

        self._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async def incr_with_ttl(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        count = int(await self._redis.incr(key))
        remaining = int(await self._redis.ttl(key))
        if remaining < 0:
            await self._redis.expire(key, ttl_seconds)
            remaining = ttl_seconds
        return count, remaining

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        await self._redis.setex(key, ttl_seconds, value)

    async def get(self, key: str) -> str | None:
        value = await self._redis.get(key)
        return str(value) if value is not None else None

    async def ttl(self, key: str) -> int:
        return int(await self._redis.ttl(key))

    async def flushdb(self) -> None:
        await self._redis.flushdb()

    async def close(self) -> None:
        await self._redis.aclose()


@pytest.fixture(autouse=True)
async def isolated_state() -> AsyncIterator[None]:
    """Give every test a fresh DB schema and fakeredis instance."""
    reset_database("sqlite://")
    cache = FakeRedisCache()
    app.state.cache = cache
    yield
    await cache.close()


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Unauthenticated client bound to the FastAPI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]]:
    """Return a helper that registers and logs in a test user."""

    async def _make(client: httpx.AsyncClient, username: str = "user") -> dict[str, str]:
        password = "Str0ngPass!"
        await client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password},
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make
