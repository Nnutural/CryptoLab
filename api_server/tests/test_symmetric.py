"""Tests for /api/v1/symmetric/* (AES / SM4 / RC6) — key_id based."""

from __future__ import annotations

import base64
import os
import time
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
import pytest

from app.main import app

USER_ID: int | None = None


@pytest.fixture
async def client(
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        c.headers.update(await auth_headers(c, "symmetric-user"))
        yield c


async def _user_id(client: httpx.AsyncClient) -> int:
    r = await client.get("/api/v1/auth/me")
    return r.json()["data"]["user_id"]


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def hx(data: str) -> bytes:
    return bytes.fromhex(data)


async def _keygen(client: httpx.AsyncClient, algo: str, key_size: int = 16) -> str:
    r = await client.post(
        "/api/v1/symmetric/keygen",
        json={"algorithm": algo, "key_size": key_size},
    )
    assert r.status_code == 200
    return r.json()["data"]["key_id"]


async def encrypt(client: httpx.AsyncClient, algo: str, payload: dict) -> dict:
    response = await client.post(f"/api/v1/symmetric/{algo}/encrypt", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    return body["data"]


async def decrypt(client: httpx.AsyncClient, algo: str, payload: dict) -> dict:
    response = await client.post(f"/api/v1/symmetric/{algo}/decrypt", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    return body["data"]


async def test_aes128_ecb_nist_vector(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", hx("2b7e151628aed2a6abf7158809cf4f3c"))
    plaintext = hx("6bc1bee22e409f96e93d7e117393172a")
    data = await encrypt(client, "aes", {
        "algorithm": "aes", "mode": "ECB", "padding": "None",
        "key_id": kid, "plaintext_b64": b64(plaintext),
    })
    assert base64.b64decode(data["ciphertext_b64"]) == hx("3ad77bb40d7a3660a89ecaf32466ef97")


async def test_aes128_cbc_nist_vector(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", hx("2b7e151628aed2a6abf7158809cf4f3c"))
    plaintext = hx("6bc1bee22e409f96e93d7e117393172a")
    data = await encrypt(client, "aes", {
        "algorithm": "aes", "mode": "CBC", "padding": "None",
        "key_id": kid,
        "iv_hex": "000102030405060708090a0b0c0d0e0f",
        "plaintext_b64": b64(plaintext),
    })
    assert base64.b64decode(data["ciphertext_b64"]) == hx("7649abac8119b246cee98e9b12e9197d")


async def test_aes128_ctr_nist_vector(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", hx("2b7e151628aed2a6abf7158809cf4f3c"))
    plaintext = hx("6bc1bee22e409f96e93d7e117393172a")
    data = await encrypt(client, "aes", {
        "algorithm": "aes", "mode": "CTR", "padding": "None",
        "key_id": kid,
        "iv_hex": "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff",
        "plaintext_b64": b64(plaintext),
    })
    assert base64.b64decode(data["ciphertext_b64"]) == hx("874d6191b620e3261bef6864990db6ce")


async def test_aes128_gcm_nist_vector(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", hx("feffe9928665731c6d6a8f9467308308"))
    plaintext = hx(
        "d9313225f88406e5a55909c5aff5269a"
        "86a7a9531534f7da2e4c303d8a318a72"
        "1c3c0c95956809532fcf0e2449a6b525"
        "b16aedf5aa0de657ba637b391aafd255"
    )
    expected = hx(
        "42831ec2217774244b7221b784d0d49c"
        "e3aa212f2c02a4e035c17e2329aca12e"
        "21d514b25466931c7d8f6a5aac84aa05"
        "1ba30b396a0aac973d58e091473f5985"
        "4d5c2af327cd64a62cf35abd2ba6fab4"
    )
    data = await encrypt(client, "aes", {
        "algorithm": "aes", "mode": "GCM", "padding": "None",
        "key_id": kid,
        "iv_hex": "cafebabefacedbaddecaf888",
        "plaintext_b64": b64(plaintext),
    })
    assert base64.b64decode(data["ciphertext_b64"]) == expected


async def test_sm4_ecb_gb_t_vector(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "sm4", hx("0123456789abcdeffedcba9876543210"))
    data = await encrypt(client, "sm4", {
        "algorithm": "sm4", "mode": "ECB", "padding": "None",
        "key_id": kid,
        "plaintext_b64": b64(hx("0123456789abcdeffedcba9876543210")),
    })
    assert base64.b64decode(data["ciphertext_b64"]) == hx("681edf34d206965e86b3e94f536e4246")


async def test_rc6_ecb_paper_vector(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "rc6", bytes(16))
    data = await encrypt(client, "rc6", {
        "algorithm": "rc6", "mode": "ECB", "padding": "None",
        "key_id": kid,
        "plaintext_b64": b64(bytes(16)),
    })
    assert base64.b64decode(data["ciphertext_b64"]) == hx("8fc3a53656b1f778c129df4e9848a41e")


async def test_aes_gcm_tag_error_returns_3002(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", bytes(16))
    enc_req = {
        "algorithm": "aes", "mode": "GCM", "padding": "None",
        "key_id": kid, "iv_hex": "00" * 12,
        "plaintext_b64": b64(b"hello"),
    }
    encrypted = await encrypt(client, "aes", enc_req)
    broken = bytearray(base64.b64decode(encrypted["ciphertext_b64"]))
    broken[-1] ^= 1
    response = await client.post(
        "/api/v1/symmetric/aes/decrypt",
        json={**enc_req, "ciphertext_b64": b64(bytes(broken))},
    )
    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_cbc_bad_pkcs7_returns_3002(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", bytes(16))
    enc_req = {
        "algorithm": "aes", "mode": "CBC", "padding": "PKCS7",
        "key_id": kid, "iv_hex": "11" * 16,
        "plaintext_b64": b64(b"hello"),
    }
    encrypted = await encrypt(client, "aes", enc_req)
    broken = bytearray(base64.b64decode(encrypted["ciphertext_b64"]))
    broken[-1] ^= 1
    response = await client.post(
        "/api/v1/symmetric/aes/decrypt",
        json={**enc_req, "ciphertext_b64": b64(bytes(broken))},
    )
    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_keygen_returns_key_id(client: httpx.AsyncClient) -> None:
    r = await client.post(
        "/api/v1/symmetric/keygen",
        json={"algorithm": "aes", "key_size": 32},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert "key_id" in data
    assert data["algorithm"] == "aes"
    assert data["key_type"] == "symmetric"


async def test_aes_ctr_one_megabyte_roundtrip_under_500ms(
    client: httpx.AsyncClient, store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    kid = store_sym_key(uid, "aes", hx("2b7e151628aed2a6abf7158809cf4f3c"))
    plaintext = os.urandom(1024 * 1024)
    enc_req = {
        "algorithm": "aes", "mode": "CTR", "padding": "None",
        "key_id": kid,
        "iv_hex": "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff",
        "plaintext_b64": b64(plaintext),
    }

    start = time.perf_counter()
    encrypted = await encrypt(client, "aes", enc_req)
    decrypted = await decrypt(client, "aes", {
        **enc_req, "ciphertext_b64": encrypted["ciphertext_b64"],
    })
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert base64.b64decode(decrypted["plaintext_b64"]) == plaintext
    assert elapsed_ms < 500
