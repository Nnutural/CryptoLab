"""JWT middleware behavior tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import jwt

from app.core.config import get_settings
from app.core.security import new_jti


async def test_missing_token_returns_distinct_401(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/symmetric/aes/encrypt", json={})

    assert response.status_code == 401
    assert response.json()["code"] == 4101


async def test_malformed_token_returns_distinct_401(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        headers={"Authorization": "Token abc"},
        json={},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 4102


async def test_invalid_token_returns_distinct_401(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        headers={"Authorization": "Bearer not-a-jwt"},
        json={},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 4103


async def test_expired_token_returns_distinct_401(client: httpx.AsyncClient) -> None:
    settings = get_settings()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "1",
            "username": "expired",
            "role": "user",
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int((now - timedelta(hours=1)).timestamp()),
            "jti": new_jti(),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 4104


async def test_blacklisted_token_returns_distinct_401(
    client: httpx.AsyncClient,
    auth_headers,
) -> None:
    client.headers.update(await auth_headers(client, "blacklist-user"))
    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 200

    response = await client.post("/api/v1/symmetric/aes/encrypt", json={})

    assert response.status_code == 401
    assert response.json()["code"] == 4105
