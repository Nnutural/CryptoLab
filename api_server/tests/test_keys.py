"""Tests for /api/v1/keys/*."""

from __future__ import annotations

from collections.abc import Callable

import httpx


async def test_key_list_filters_to_owner(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    user1 = await _register_and_login(client, "key-user-1")
    user2 = await _register_and_login(client, "key-user-2")

    kid1 = store_sym_key(user1["user_id"], "aes", bytes(16), "mine")
    store_sym_key(user2["user_id"], "aes", bytes(16), "other")

    client.headers.update(user1["headers"])
    response = await client.get("/api/v1/keys")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == kid1
    assert data[0]["label"] == "mine"


async def test_key_revoke(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    user = await _register_and_login(client, "key-revoke-user")
    kid = store_sym_key(user["user_id"], "aes", bytes(16))
    client.headers.update(user["headers"])

    response = await client.delete(f"/api/v1/keys/{kid}")
    assert response.status_code == 200

    listing = await client.get("/api/v1/keys")
    assert len(listing.json()["data"]) == 0


async def test_key_not_owned_returns_4201(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    user1 = await _register_and_login(client, "owner-1")
    user2 = await _register_and_login(client, "owner-2")
    kid = store_sym_key(user1["user_id"], "aes", bytes(16))

    client.headers.update(user2["headers"])
    response = await client.delete(f"/api/v1/keys/{kid}")
    assert response.status_code == 403
    assert response.json()["code"] == 4201


async def test_soft_deleted_key_not_usable(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    user = await _register_and_login(client, "soft-del-user")
    kid = store_sym_key(user["user_id"], "aes", bytes(16))
    client.headers.update(user["headers"])

    await client.delete(f"/api/v1/keys/{kid}")

    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes", "mode": "ECB", "padding": "PKCS7",
            "key_id": kid, "plaintext_b64": "aGVsbG8=",
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == 4202


async def _register_and_login(client: httpx.AsyncClient, username: str) -> dict:
    password = "Str0ngPass!"
    registered = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": password},
    )
    logged_in = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return {
        "user_id": registered.json()["data"]["user_id"],
        "headers": {"Authorization": f"Bearer {logged_in.json()['data']['access_token']}"},
    }
