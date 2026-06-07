"""Tests for /api/v1/scenarios/secure_file_transfer/*."""

from __future__ import annotations

import base64
import copy
import os
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
import pytest

from app.main import app

_RSA_KEYPAIR: dict[str, str] | None = None
_ECDSA_KEYPAIR: dict[str, str] | None = None


@pytest.fixture
async def client(
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        test_client.headers.update(await auth_headers(test_client, "scenario-user"))
        yield test_client


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


async def rsa_keypair(client: httpx.AsyncClient) -> dict[str, str]:
    global _RSA_KEYPAIR
    if _RSA_KEYPAIR is None:
        response = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 65537})
        assert response.status_code == 200
        _RSA_KEYPAIR = response.json()["data"]
    return _RSA_KEYPAIR


async def ecdsa_keypair(client: httpx.AsyncClient) -> dict[str, str]:
    global _ECDSA_KEYPAIR
    if _ECDSA_KEYPAIR is None:
        response = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
        assert response.status_code == 200
        _ECDSA_KEYPAIR = response.json()["data"]
    return _ECDSA_KEYPAIR


async def send_file(client: httpx.AsyncClient, file_bytes: bytes) -> dict:
    rsa = await rsa_keypair(client)
    ecdsa = await ecdsa_keypair(client)
    response = await client.post(
        "/api/v1/scenarios/secure_file_transfer/send",
        json={
            "file_b64": b64(file_bytes),
            "receiver_rsa_public_pem": {"n_hex": rsa["n_hex"], "e_hex": rsa["e_hex"]},
            "sender_ecdsa_private_hex": ecdsa["d_hex"],
            "sender_ecdsa_curve": "secp160r1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    return body["data"]


async def receive_file(client: httpx.AsyncClient, envelope: dict) -> httpx.Response:
    rsa = await rsa_keypair(client)
    ecdsa = await ecdsa_keypair(client)
    return await client.post(
        "/api/v1/scenarios/secure_file_transfer/receive",
        json={
            "envelope": envelope,
            "receiver_rsa_private": {
                "n_hex": rsa["n_hex"],
                "d_hex": rsa["d_hex"],
                "p_hex": rsa["p_hex"],
                "q_hex": rsa["q_hex"],
            },
            "sender_ecdsa_public": {
                "qx_hex": ecdsa["qx_hex"],
                "qy_hex": ecdsa["qy_hex"],
                "curve": "secp160r1",
            },
        },
    )


async def test_secure_file_transfer_roundtrip_128k(client: httpx.AsyncClient) -> None:
    plaintext = os.urandom(128 * 1024)
    sent = await send_file(client, plaintext)
    response = await receive_file(client, sent["envelope"])

    assert response.status_code == 200
    data = response.json()["data"]
    assert base64.b64decode(data["plaintext_b64"]) == plaintext
    assert data["verification"] == {
        "kem_ok": True,
        "aead_ok": True,
        "digest_ok": True,
        "signature_ok": True,
    }


async def test_send_envelope_has_required_fields(client: httpx.AsyncClient) -> None:
    sent = await send_file(client, b"field check")
    envelope = sent["envelope"]

    assert envelope["alg"] == {
        "kem": "RSA-OAEP-SHA256",
        "aead": "AES-256-GCM",
        "sig": "ECDSA-secp160r1-SHA256",
        "transport": "base64",
    }
    for key in [
        "enc_session_key_b64",
        "iv_hex",
        "ciphertext_b64",
        "tag_hex",
        "file_sha256_hex",
        "signature",
    ]:
        assert key in envelope
    assert set(envelope["signature"]) == {"r_hex", "s_hex"}


async def test_receive_rejects_tampered_ciphertext_with_3002(client: httpx.AsyncClient) -> None:
    sent = await send_file(client, b"ciphertext tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    broken = bytearray(base64.b64decode(envelope["ciphertext_b64"]))
    broken[-1] ^= 1
    envelope["ciphertext_b64"] = b64(bytes(broken))

    response = await receive_file(client, envelope)

    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_receive_rejects_tampered_tag_with_3002(client: httpx.AsyncClient) -> None:
    sent = await send_file(client, b"tag tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    broken = bytearray.fromhex(envelope["tag_hex"])
    broken[-1] ^= 1
    envelope["tag_hex"] = broken.hex()

    response = await receive_file(client, envelope)

    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_receive_rejects_tampered_digest_with_3002(client: httpx.AsyncClient) -> None:
    sent = await send_file(client, b"digest tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    digest = bytearray.fromhex(envelope["file_sha256_hex"])
    digest[0] ^= 1
    envelope["file_sha256_hex"] = digest.hex()

    response = await receive_file(client, envelope)

    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_receive_rejects_tampered_signature_with_3003(client: httpx.AsyncClient) -> None:
    sent = await send_file(client, b"signature tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    sig_s = bytearray.fromhex(envelope["signature"]["s_hex"])
    sig_s[-1] ^= 1
    envelope["signature"]["s_hex"] = sig_s.hex()

    response = await receive_file(client, envelope)

    assert response.status_code == 400
    assert response.json()["code"] == 3003


async def test_receive_rejects_unsupported_algorithm_with_422(client: httpx.AsyncClient) -> None:
    sent = await send_file(client, b"unsupported algorithm")
    envelope = copy.deepcopy(sent["envelope"])
    envelope["alg"]["kem"] = "RSA-PKCS1v1.5"

    response = await receive_file(client, envelope)

    assert response.status_code == 422
    assert response.json()["code"] == 2004
    assert response.json()["message"] == "unsupported_algorithm"


async def test_send_rejects_file_over_10_mib_with_422(client: httpx.AsyncClient) -> None:
    rsa = await rsa_keypair(client)
    ecdsa = await ecdsa_keypair(client)
    response = await client.post(
        "/api/v1/scenarios/secure_file_transfer/send",
        json={
            "file_b64": b64(b"\x00" * (10 * 1024 * 1024 + 1)),
            "receiver_rsa_public_pem": {"n_hex": rsa["n_hex"], "e_hex": rsa["e_hex"]},
            "sender_ecdsa_private_hex": ecdsa["d_hex"],
            "sender_ecdsa_curve": "secp160r1",
        },
    )

    assert response.status_code == 422
    assert response.json()["code"] == 2001
