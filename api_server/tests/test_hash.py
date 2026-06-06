"""Tests for /api/v1/hash/* (SHA-1/2/3, RIPEMD, HMAC, PBKDF2)."""

from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import AsyncIterator

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("algo", "factory"),
    [
        ("sha1", hashlib.sha1),
        ("sha256", hashlib.sha256),
        ("sha3_256", hashlib.sha3_256),
        ("sha3_512", hashlib.sha3_512),
    ],
)
@pytest.mark.parametrize("data", ["", "abc"])
async def test_hashlib_backed_hashes(
    client: httpx.AsyncClient,
    algo: str,
    factory: type[hashlib._Hash],
    data: str,
) -> None:
    response = await client.post(f"/api/v1/hash/{algo}", json={"data": data})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert body["data"]["algorithm"] == algo
    assert body["data"]["digest_hex"] == factory(data.encode()).hexdigest()


@pytest.mark.parametrize("data", ["", "abc"])
async def test_ripemd160_hash(
    client: httpx.AsyncClient,
    data: str,
) -> None:
    response = await client.post("/api/v1/hash/ripemd160", json={"data": data})

    assert response.status_code == 200
    body = response.json()
    if _hashlib_has_ripemd160():
        expected = hashlib.new("ripemd160", data.encode()).hexdigest()
    else:
        expected = {
            "": "9c1185a5c5e9fc54612808977ee8f548b2258d31",
            "abc": "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc",
        }[data]
    assert body["data"]["digest_hex"] == expected


@pytest.mark.parametrize(
    ("algo", "digestmod"),
    [("sha1", hashlib.sha1), ("sha256", hashlib.sha256)],
)
async def test_hmac_endpoints(
    client: httpx.AsyncClient,
    algo: str,
    digestmod: type[hashlib._Hash],
) -> None:
    key = "key"
    message = "The quick brown fox jumps over the lazy dog"
    response = await client.post(
        f"/api/v1/hash/hmac/{algo}",
        json={"key": key, "message": message, "algorithm": algo},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    expected = hmac.new(key.encode(), message.encode(), digestmod).hexdigest()
    assert body["data"]["mac_hex"] == expected


async def test_pbkdf2_matches_hashlib(client: httpx.AsyncClient) -> None:
    request = {
        "password": "password",
        "salt": "salt1234",
        "iterations": 4096,
        "key_len": 32,
    }
    response = await client.post("/api/v1/hash/pbkdf2", json=request)

    assert response.status_code == 200
    body = response.json()
    expected = hashlib.pbkdf2_hmac(
        "sha256",
        request["password"].encode(),
        request["salt"].encode(),
        request["iterations"],
        request["key_len"],
    ).hex()
    assert body["code"] == 1000
    assert body["data"]["derived_key_hex"] == expected
    assert body["data"]["warning"] is not None


async def test_pbkdf2_rejects_iterations_below_1000(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/hash/pbkdf2",
        json={"password": "password", "salt": "salt1234", "iterations": 500, "key_len": 32},
    )

    assert response.status_code == 422
    assert response.json()["code"] == 2001


async def test_sha256_one_megabyte_sanity_under_200ms(client: httpx.AsyncClient) -> None:
    data = "a" * (1024 * 1024)
    start = time.perf_counter()
    response = await client.post("/api/v1/hash/sha256", json={"data": data})
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert response.json()["data"]["digest_hex"] == hashlib.sha256(data.encode()).hexdigest()
    assert elapsed_ms < 200


def _hashlib_has_ripemd160() -> bool:
    try:
        hashlib.new("ripemd160")
    except ValueError:
        return False
    return True
