"""Tests for /api/v1/pubkey/* (RSA / ECC / ECDSA)."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

import httpx
import pytest

from app.main import app

SECP160R1_N = int("0100000000000000000001f4c8f927aed3ca752257", 16)
ECDSA_VECTOR_D = "9717619397619fc8e6c73ca2d0c2ba2a2c4e2a45"
ECDSA_VECTOR_R = "00b28dc7224bae71617117ae60160360e0ff801830"
ECDSA_VECTOR_S = "006767d5ffbfae5b56aa6c0381107e06a4a5413027"

_RSA_KEYPAIR: dict[str, str] | None = None


@pytest.fixture
async def client(
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        test_client.headers.update(await auth_headers(test_client, "pubkey-user"))
        yield test_client


async def rsa_keypair(client: httpx.AsyncClient) -> dict[str, str]:
    global _RSA_KEYPAIR
    if _RSA_KEYPAIR is None:
        response = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 65537})
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 1000
        _RSA_KEYPAIR = body["data"]
    return _RSA_KEYPAIR


async def test_rsa_oaep_encrypt_decrypt_roundtrip(client: httpx.AsyncClient) -> None:
    key = await rsa_keypair(client)
    encrypted = await client.post(
        "/api/v1/pubkey/rsa/encrypt",
        json={"plaintext": "hello", "n_hex": key["n_hex"], "e_hex": key["e_hex"]},
    )
    assert encrypted.status_code == 200
    ciphertext_hex = encrypted.json()["data"]["ciphertext_hex"]

    decrypted = await client.post(
        "/api/v1/pubkey/rsa/decrypt",
        json={
            "ciphertext_hex": ciphertext_hex,
            "n_hex": key["n_hex"],
            "d_hex": key["d_hex"],
            "p_hex": key["p_hex"],
            "q_hex": key["q_hex"],
        },
    )

    assert decrypted.status_code == 200
    assert decrypted.json()["data"]["plaintext"] == "hello"


async def test_rsa_pss_sign_verify_roundtrip(client: httpx.AsyncClient) -> None:
    key = await rsa_keypair(client)
    signed = await client.post(
        "/api/v1/pubkey/rsa/sign",
        json={
            "message": "hello",
            "n_hex": key["n_hex"],
            "d_hex": key["d_hex"],
            "p_hex": key["p_hex"],
            "q_hex": key["q_hex"],
        },
    )
    assert signed.status_code == 200

    verified = await client.post(
        "/api/v1/pubkey/rsa/verify",
        json={
            "message": "hello",
            "signature_hex": signed.json()["data"]["signature_hex"],
            "n_hex": key["n_hex"],
            "e_hex": key["e_hex"],
        },
    )
    assert verified.status_code == 200
    assert verified.json()["data"]["valid"] is True


async def test_tampered_oaep_ciphertext_returns_3002(client: httpx.AsyncClient) -> None:
    key = await rsa_keypair(client)
    encrypted = await client.post(
        "/api/v1/pubkey/rsa/encrypt",
        json={"plaintext": "hello", "n_hex": key["n_hex"], "e_hex": key["e_hex"]},
    )
    broken = bytearray.fromhex(encrypted.json()["data"]["ciphertext_hex"])
    broken[-1] ^= 1
    response = await client.post(
        "/api/v1/pubkey/rsa/decrypt",
        json={
            "ciphertext_hex": broken.hex(),
            "n_hex": key["n_hex"],
            "d_hex": key["d_hex"],
            "p_hex": key["p_hex"],
            "q_hex": key["q_hex"],
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_tampered_pss_signature_verifies_false(client: httpx.AsyncClient) -> None:
    key = await rsa_keypair(client)
    signed = await client.post(
        "/api/v1/pubkey/rsa/sign",
        json={
            "message": "hello",
            "n_hex": key["n_hex"],
            "d_hex": key["d_hex"],
            "p_hex": key["p_hex"],
            "q_hex": key["q_hex"],
        },
    )
    broken = bytearray.fromhex(signed.json()["data"]["signature_hex"])
    broken[0] ^= 1
    response = await client.post(
        "/api/v1/pubkey/rsa/verify",
        json={
            "message": "hello",
            "signature_hex": broken.hex(),
            "n_hex": key["n_hex"],
            "e_hex": key["e_hex"],
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["valid"] is False


async def test_rsa_keygen_rejects_e_3(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 3})

    assert response.status_code == 422
    assert response.json()["code"] == 2001


async def test_ecc_keygen_outputs_private_scalar_in_range(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})

    assert response.status_code == 200
    data = response.json()["data"]
    d = int(data["d_hex"], 16)
    assert 1 <= d < SECP160R1_N
    assert len(bytes.fromhex(data["qx_hex"])) == 20
    assert len(bytes.fromhex(data["qy_hex"])) == 20


async def test_ecdsa_rfc6979_secp160r1_regression_vector(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "sample", "d_hex": ECDSA_VECTOR_D, "curve": "secp160r1"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["r_hex"] == ECDSA_VECTOR_R
    assert data["s_hex"] == ECDSA_VECTOR_S


async def test_ecdsa_sign_verify_roundtrip(client: httpx.AsyncClient) -> None:
    key_response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
    key = key_response.json()["data"]
    signed = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "hello", "d_hex": key["d_hex"], "curve": "secp160r1"},
    )
    sig = signed.json()["data"]

    verified = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "hello",
            "r_hex": sig["r_hex"],
            "s_hex": sig["s_hex"],
            "qx_hex": key["qx_hex"],
            "qy_hex": key["qy_hex"],
            "curve": "secp160r1",
        },
    )

    assert verified.status_code == 200
    assert verified.json()["data"]["valid"] is True


async def test_ecdsa_tampered_message_verifies_false(client: httpx.AsyncClient) -> None:
    key_response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
    key = key_response.json()["data"]
    signed = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "hello", "d_hex": key["d_hex"], "curve": "secp160r1"},
    )
    sig = signed.json()["data"]
    response = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "hell0",
            "r_hex": sig["r_hex"],
            "s_hex": sig["s_hex"],
            "qx_hex": key["qx_hex"],
            "qy_hex": key["qy_hex"],
            "curve": "secp160r1",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["valid"] is False


async def test_ecdsa_tampered_signature_verifies_false(client: httpx.AsyncClient) -> None:
    key_response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
    key = key_response.json()["data"]
    signed = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "hello", "d_hex": key["d_hex"], "curve": "secp160r1"},
    )
    sig = signed.json()["data"]
    bad_r = (bytearray.fromhex(sig["r_hex"]))
    bad_r[-1] ^= 1
    response = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "hello",
            "r_hex": bad_r.hex(),
            "s_hex": sig["s_hex"],
            "qx_hex": key["qx_hex"],
            "qy_hex": key["qy_hex"],
            "curve": "secp160r1",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["valid"] is False


async def test_unsupported_curve_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/pubkey/ecc/keygen",
        json={"curve": "secp256r1"},
    )

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


async def test_ecdsa_two_http_calls_end_to_end(client: httpx.AsyncClient) -> None:
    key_response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
    key: dict[str, Any] = key_response.json()["data"]
    sign_response = await client.post(
        "/api/v1/pubkey/ecdsa/sign",
        json={"message": "chain", "d_hex": key["d_hex"], "curve": "secp160r1"},
    )
    signature = sign_response.json()["data"]
    verify_response = await client.post(
        "/api/v1/pubkey/ecdsa/verify",
        json={
            "message": "chain",
            "r_hex": signature["r_hex"],
            "s_hex": signature["s_hex"],
            "qx_hex": key["qx_hex"],
            "qy_hex": key["qy_hex"],
            "curve": "secp160r1",
        },
    )

    assert sign_response.status_code == 200
    assert verify_response.status_code == 200
    assert verify_response.json()["data"]["valid"] is True
