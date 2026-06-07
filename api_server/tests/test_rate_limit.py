"""Rate-limit middleware tests."""

from __future__ import annotations

import httpx


async def test_login_rate_limit_returns_429(client: httpx.AsyncClient) -> None:
    password = "Str0ngPass!"
    await client.post(
        "/api/v1/auth/register",
        json={"username": "rate-user", "password": password},
    )

    last = None
    for _ in range(6):
        last = await client.post(
            "/api/v1/auth/login",
            json={"username": "rate-user", "password": password},
        )

    assert last is not None
    assert last.status_code == 429
    assert last.json()["code"] == 5001
    assert int(last.headers["Retry-After"]) > 0
