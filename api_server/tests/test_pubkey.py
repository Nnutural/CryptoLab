"""Tests for /api/v1/pubkey/* (RSA / ECC / ECDSA) — key_id based."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
import pytest

from app.main import app

ECDSA_VECTOR_D = "9717619397619fc8e6c73ca2d0c2ba2a2c4e2a45"
ECDSA_VECTOR_R = "00b28dc7224bae71617117ae60160360e0ff801830"
ECDSA_VECTOR_S = "006767d5ffbfae5b56aa6c0381107e06a4a5413027"


@pytest.fixture
async def client(
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        c.headers.update(await auth_headers(c, "pubkey-user"))
        yield c


async def _user_id(client: httpx.AsyncClient) -> int:
    r = await client.get("/api/v1/auth/me")
    return r.json()["data"]["user_id"]


async def _rsa_keygen(client: httpx.AsyncClient) -> dict:
    r = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 65537})
    assert r.status_code == 200
    return r.json()["data"]


async def _ecc_keygen(client: httpx.AsyncClient) -> dict:
    r = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
    assert r.status_code == 200
    return r.json()["data"]


async def test_rsa_oaep_encrypt_decrypt_roundtrip(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    encrypted = await client.post(
        "/api/v1/pubkey/rsa/encrypt",
        json={"plaintext": "hello", "key_id": key["public_key_id"]},
    )
    assert encrypted.status_code == 200

    decrypted = await client.post(
        "/api/v1/pubkey/rsa/decrypt",
        json={
            "ciphertext_hex": encrypted.json()["data"]["ciphertext_hex"],
            "key_id": key["private_key_id"],
        },
    )
    assert decrypted.status_code == 200
    assert decrypted.json()["data"]["plaintext"] == "hello"


async def test_rsa_pss_sign_verify_roundtrip(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    signed = await client.post(
        "/api/v1/pubkey/rsa/sign",
        json={"message": "hello", "key_id": key["private_key_id"]},
    )
    assert signed.status_code == 200

    verified = await client.post(
        "/api/v1/pubkey/rsa/verify",
        json={
            "message": "hello",
            "signature_hex": signed.json()["data"]["signature_hex"],
            "key_id": key["public_key_id"],
        },
    )
    assert verified.status_code == 200
    assert verified.json()["data"]["valid"] is True


async def test_tampered_oaep_ciphertext_returns_3002(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    encrypted = await client.post(
        "/api/v1/pubkey/rsa/encrypt",
        json={"plaintext": "hello", "key_id": key["public_key_id"]},
    )
    broken = bytearray.fromhex(encrypted.json()["data"]["ciphertext_hex"])
    broken[-1] ^= 1
    response = await client.post(
        "/api/v1/pubkey/rsa/decrypt",
        json={"ciphertext_hex": broken.hex(), "key_id": key["private_key_id"]},
    )
    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_tampered_pss_signature_verifies_false(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    signed = await client.post(
        "/api/v1/pubkey/rsa/sign",
        json={"message": "hello", "key_id": key["private_key_id"]},
    )
    broken = bytearray.fromhex(signed.json()["data"]["signature_hex"])
    broken[0] ^= 1
    response = await client.post(
        "/api/v1/pubkey/rsa/verify",
        json={
            "message": "hello",
            "signature_hex": broken.hex(),
            "key_id": key["public_key_id"],
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["valid"] is False


async def test_rsa_keygen_rejects_e_3(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 3})
    assert response.status_code == 422
    assert response.json()["code"] == 2001


async def test_rsa_keygen_returns_key_ids(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    assert "private_key_id" in key
    assert "public_key_id" in key
    assert key["algorithm"] == "rsa"
    assert key["bits"] == 1024


async def test_ecc_keygen_returns_key_ids(client: httpx.AsyncClient) -> None:
    key = await _ecc_keygen(client)
    assert "private_key_id" in key
    assert "public_key_id" in key
    assert key["algorithm"] == "ecc"
    assert key["curve"] == "secp160r1"


async def test_ecdsa_rfc6979_secp160r1_regression_vector(
    client: httpx.AsyncClient, store_key_pair: Callable,
) -> None:
    uid = await _user_id(client)
    priv_id, _pub_id = store_key_pair(
        uid, "ecc",
        {"d_hex": ECDSA_VECTOR_D, "curve": "secp160r1"},
        {"qx_hex": "00" * 20, "qy_hex": "00" * 20, "curve": "secp160r1"},
    )
    response = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "sample", "key_id": priv_id, "curve": "secp160r1"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["r_hex"] == ECDSA_VECTOR_R
    assert data["s_hex"] == ECDSA_VECTOR_S


async def test_ecdsa_sign_verify_roundtrip(client: httpx.AsyncClient) -> None:
    key = await _ecc_keygen(client)
    signed = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "hello", "key_id": key["private_key_id"], "curve": "secp160r1"},
    )
    assert signed.status_code == 200
    sig = signed.json()["data"]

    verified = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "hello",
            "r_hex": sig["r_hex"],
            "s_hex": sig["s_hex"],
            "key_id": key["public_key_id"],
            "curve": "secp160r1",
        },
    )
    assert verified.status_code == 200
    assert verified.json()["data"]["valid"] is True


async def test_ecdsa_tampered_message_verifies_false(client: httpx.AsyncClient) -> None:
    key = await _ecc_keygen(client)
    signed = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "hello", "key_id": key["private_key_id"], "curve": "secp160r1"},
    )
    sig = signed.json()["data"]
    response = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "hell0",
            "r_hex": sig["r_hex"],
            "s_hex": sig["s_hex"],
            "key_id": key["public_key_id"],
            "curve": "secp160r1",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["valid"] is False


async def test_ecdsa_tampered_signature_verifies_false(client: httpx.AsyncClient) -> None:
    key = await _ecc_keygen(client)
    signed = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "hello", "key_id": key["private_key_id"], "curve": "secp160r1"},
    )
    sig = signed.json()["data"]
    bad_r = bytearray.fromhex(sig["r_hex"])
    bad_r[-1] ^= 1
    response = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "hello",
            "r_hex": bad_r.hex(),
            "s_hex": sig["s_hex"],
            "key_id": key["public_key_id"],
            "curve": "secp160r1",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["valid"] is False


async def test_unsupported_curve_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp256r1"})
    assert response.status_code == 422
    assert response.json()["code"] == 2001


@pytest.mark.slow
async def test_rsa_1024_keygen_performance(client: httpx.AsyncClient) -> None:
    start = time.perf_counter()
    response = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 65537})
    elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert response.json()["code"] == 1000
    assert elapsed < 10


async def test_key_type_mismatch_returns_4203(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    response = await client.post(
        "/api/v1/pubkey/rsa/encrypt",
        json={"plaintext": "hello", "key_id": key["private_key_id"]},
    )
    assert response.status_code == 400
    assert response.json()["code"] == 4203


async def test_key_not_found_returns_4202(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/pubkey/rsa/encrypt",
        json={"plaintext": "hello", "key_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == 4202


async def test_public_key_export(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    response = await client.get(f"/api/v1/keys/{key['public_key_id']}/public")
    assert response.status_code == 200
    mat = response.json()["data"]["material"]
    assert "n_hex" in mat
    assert "e_hex" in mat


async def test_private_key_export_denied(client: httpx.AsyncClient) -> None:
    key = await _rsa_keygen(client)
    response = await client.get(f"/api/v1/keys/{key['private_key_id']}/public")
    assert response.status_code == 403
    assert response.json()["code"] == 4204
