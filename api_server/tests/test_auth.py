"""Tests for /api/v1/auth/*."""

from __future__ import annotations

import httpx


async def test_register_then_login(client: httpx.AsyncClient) -> None:
    registered = await client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "Str0ngPass!"},
    )
    assert registered.status_code == 200
    assert registered.json()["data"]["user_id"] >= 1
    assert registered.json()["data"]["created_at"]

    logged_in = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "Str0ngPass!"},
    )
    assert logged_in.status_code == 200
    data = logged_in.json()["data"]
    assert data["access_token"]
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] > 0


async def test_me_requires_login_and_returns_profile(
    client: httpx.AsyncClient,
    auth_headers,
) -> None:
    client.headers.update(await auth_headers(client, "me-user"))
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["username"] == "me-user"
    assert data["role"] == "user"
    assert "password_hash" not in data
    assert "salt" not in data


async def test_logout_blacklists_current_token(
    client: httpx.AsyncClient,
    auth_headers,
) -> None:
    client.headers.update(await auth_headers(client, "logout-user"))
    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 200

    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["code"] == 4105


async def test_register_duplicate_username_returns_409(client: httpx.AsyncClient) -> None:
    payload = {"username": "duplicate", "password": "Str0ngPass!"}
    first = await client.post("/api/v1/auth/register", json=payload)
    second = await client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["code"] == 4107


async def test_register_weak_password_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "weak", "password": "short"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == 2001


async def test_login_wrong_password_returns_401(client: httpx.AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"username": "wrong-pass", "password": "Str0ngPass!"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "wrong-pass", "password": "bad-password"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 4106


async def test_login_missing_user_returns_same_401(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "missing", "password": "bad-password"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 4106
