"""Small async cache facade used for rate limiting and JWT blacklists."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Protocol

from app.core.config import get_settings


class CacheBackend(Protocol):
    """The subset of Redis operations required by Phase F1."""

    async def incr_with_ttl(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        """Increment a counter and return (new_count, remaining_ttl_seconds)."""

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        """Set a value with expiration."""

    async def get(self, key: str) -> str | None:
        """Return a string value if present and unexpired."""

    async def ttl(self, key: str) -> int:
        """Return the remaining TTL in seconds."""

    async def flushdb(self) -> None:
        """Clear all keys; used by tests."""

    async def close(self) -> None:
        """Release external resources."""


@dataclass
class _Entry:
    value: str | int
    expires_at: float


class MemoryCache:
    """In-process Redis-like backend for tests and single-process local runs."""

    def __init__(self) -> None:
        self._items: dict[str, _Entry] = {}
        self._lock = asyncio.Lock()

    async def incr_with_ttl(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        async with self._lock:
            self._purge_expired(key)
            now = time.monotonic()
            entry = self._items.get(key)
            if entry is None:
                self._items[key] = _Entry(value=1, expires_at=now + ttl_seconds)
                return 1, ttl_seconds
            entry.value = int(entry.value) + 1
            remaining = max(1, int(entry.expires_at - now))
            return int(entry.value), remaining

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        async with self._lock:
            self._items[key] = _Entry(value=value, expires_at=time.monotonic() + ttl_seconds)

    async def get(self, key: str) -> str | None:
        async with self._lock:
            self._purge_expired(key)
            entry = self._items.get(key)
            return str(entry.value) if entry is not None else None

    async def ttl(self, key: str) -> int:
        async with self._lock:
            self._purge_expired(key)
            entry = self._items.get(key)
            if entry is None:
                return -2
            return max(0, int(entry.expires_at - time.monotonic()))

    async def flushdb(self) -> None:
        async with self._lock:
            self._items.clear()

    async def close(self) -> None:
        await self.flushdb()

    def _purge_expired(self, key: str) -> None:
        entry = self._items.get(key)
        if entry is not None and entry.expires_at <= time.monotonic():
            self._items.pop(key, None)


class RedisCache:
    """Redis-backed implementation used when CRYPTOLAB_REDIS_URL is redis://."""

    def __init__(self, url: str) -> None:
        from redis import asyncio as redis_async

        self._redis = redis_async.from_url(url, decode_responses=True)

    async def incr_with_ttl(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.ttl(key)
            count, existing_ttl = await pipe.execute()
        if int(existing_ttl) < 0:
            await self._redis.expire(key, ttl_seconds)
            return int(count), ttl_seconds
        return int(count), int(existing_ttl)

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


def create_cache() -> CacheBackend:
    """Create the configured cache backend."""
    redis_url = get_settings().redis_url
    if redis_url.startswith("redis://") or redis_url.startswith("rediss://"):
        return RedisCache(redis_url)
    return MemoryCache()
