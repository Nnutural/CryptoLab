"""Tests for /api/v1/keys/*."""

from __future__ import annotations

from uuid import uuid4

import httpx

from app.db.session import get_session_factory
from app.models.key_store import KeyStore


async def test_key_list_filters_to_owner(client: httpx.AsyncClient) -> None:
    user1 = await _register_and_login(client, "key-user-1")
    user2 = await _register_and_login(client, "key-user-2")

    key1 = str(uuid4())
    key2 = str(uuid4())
    with get_session_factory()() as db:
        db.add_all(
            [
                KeyStore(
                    id=key1,
                    user_id=user1["user_id"],
                    key_type="private",
                    algorithm="RSA-1024",
                    key_material_encrypted=b"ct1",
                    iv=b"iv-1",
                    auth_tag=b"tag1",
                    label="mine",
                ),
                KeyStore(
                    id=key2,
                    user_id=user2["user_id"],
                    key_type="private",
                    algorithm="RSA-1024",
                    key_material_encrypted=b"ct2",
                    iv=b"iv-2",
                    auth_tag=b"tag2",
                    label="other",
                ),
            ]
        )
        db.commit()

    client.headers.update(user1["headers"])
    response = await client.get("/api/v1/keys")

    assert response.status_code == 200
    data = response.json()["data"]
    assert [item["id"] for item in data] == [key1]
    assert data[0]["label"] == "mine"


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
