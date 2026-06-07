"""Tests for /api/v1/scenarios/secure_file_transfer/* — raw material mode."""

from __future__ import annotations

import base64
import copy
import os
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client(
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        c.headers.update(await auth_headers(c, "scenario-user"))
        yield c


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


async def _gen_rsa(client: httpx.AsyncClient) -> dict:
    """Generate RSA keypair and export public material."""
    r = await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 65537})
    assert r.status_code == 200
    data = r.json()["data"]
    pub_r = await client.get(f"/api/v1/keys/{data['public_key_id']}/public")
    return {**data, "public_material": pub_r.json()["data"]["material"]}


async def _gen_ecdsa(client: httpx.AsyncClient) -> dict:
    """Generate ECC keypair and export public material."""
    r = await client.post("/api/v1/pubkey/ecc/keygen", json={"curve": "secp160r1"})
    assert r.status_code == 200
    data = r.json()["data"]
    pub_r = await client.get(f"/api/v1/keys/{data['public_key_id']}/public")
    return {**data, "public_material": pub_r.json()["data"]["material"]}


async def send_file(client: httpx.AsyncClient, file_bytes: bytes) -> tuple[dict, dict, dict]:
    """Send using key_id mode. Returns (send_data, rsa_keys, ecdsa_keys)."""
    rsa = await _gen_rsa(client)
    ecdsa = await _gen_ecdsa(client)
    response = await client.post(
        "/api/v1/scenarios/secure_file_transfer/send",
        json={
            "file_b64": b64(file_bytes),
            "receiver_rsa_public_key_id": rsa["public_key_id"],
            "sender_ecdsa_private_key_id": ecdsa["private_key_id"],
            "sender_ecdsa_curve": "secp160r1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    return body["data"], rsa, ecdsa


async def receive_file(
    client: httpx.AsyncClient, envelope: dict, rsa: dict, ecdsa: dict,
) -> httpx.Response:
    """Receive using key_id mode."""
    return await client.post(
        "/api/v1/scenarios/secure_file_transfer/receive",
        json={
            "envelope": envelope,
            "receiver_rsa_private_key_id": rsa["private_key_id"],
            "sender_ecdsa_public_key_id": ecdsa["public_key_id"],
        },
    )


async def test_secure_file_transfer_roundtrip_128k(client: httpx.AsyncClient) -> None:
    plaintext = os.urandom(128 * 1024)
    sent, rsa, ecdsa = await send_file(client, plaintext)
    response = await receive_file(client, sent["envelope"], rsa, ecdsa)

    assert response.status_code == 200
    data = response.json()["data"]
    assert base64.b64decode(data["plaintext_b64"]) == plaintext
    assert data["verification"] == {
        "kem_ok": True, "aead_ok": True, "digest_ok": True, "signature_ok": True,
    }


async def test_send_envelope_has_required_fields(client: httpx.AsyncClient) -> None:
    sent, _, _ = await send_file(client, b"field check")
    envelope = sent["envelope"]
    assert envelope["alg"] == {
        "kem": "RSA-OAEP-SHA256",
        "aead": "AES-256-GCM",
        "sig": "ECDSA-secp160r1-SHA256",
        "transport": "base64",
    }
    for key in [
        "enc_session_key_b64", "iv_hex", "ciphertext_b64",
        "tag_hex", "file_sha256_hex", "signature",
    ]:
        assert key in envelope
    assert set(envelope["signature"]) == {"r_hex", "s_hex"}


async def test_receive_rejects_tampered_ciphertext_with_3002(client: httpx.AsyncClient) -> None:
    sent, rsa, ecdsa = await send_file(client, b"ciphertext tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    broken = bytearray(base64.b64decode(envelope["ciphertext_b64"]))
    broken[-1] ^= 1
    envelope["ciphertext_b64"] = b64(bytes(broken))
    response = await receive_file(client, envelope, rsa, ecdsa)
    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_receive_rejects_tampered_tag_with_3002(client: httpx.AsyncClient) -> None:
    sent, rsa, ecdsa = await send_file(client, b"tag tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    broken = bytearray.fromhex(envelope["tag_hex"])
    broken[-1] ^= 1
    envelope["tag_hex"] = broken.hex()
    response = await receive_file(client, envelope, rsa, ecdsa)
    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_receive_rejects_tampered_digest_with_3002(client: httpx.AsyncClient) -> None:
    sent, rsa, ecdsa = await send_file(client, b"digest tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    digest = bytearray.fromhex(envelope["file_sha256_hex"])
    digest[0] ^= 1
    envelope["file_sha256_hex"] = digest.hex()
    response = await receive_file(client, envelope, rsa, ecdsa)
    assert response.status_code == 400
    assert response.json()["code"] == 3002


async def test_receive_rejects_tampered_signature_with_3003(client: httpx.AsyncClient) -> None:
    sent, rsa, ecdsa = await send_file(client, b"signature tamper" * 32)
    envelope = copy.deepcopy(sent["envelope"])
    sig_s = bytearray.fromhex(envelope["signature"]["s_hex"])
    sig_s[-1] ^= 1
    envelope["signature"]["s_hex"] = sig_s.hex()
    response = await receive_file(client, envelope, rsa, ecdsa)
    assert response.status_code == 400
    assert response.json()["code"] == 3003


async def test_receive_rejects_unsupported_algorithm_with_422(
    client: httpx.AsyncClient,
) -> None:
    sent, rsa, ecdsa = await send_file(client, b"unsupported algorithm")
    envelope = copy.deepcopy(sent["envelope"])
    envelope["alg"]["kem"] = "RSA-PKCS1v1.5"
    response = await receive_file(client, envelope, rsa, ecdsa)
    assert response.status_code == 422
    assert response.json()["code"] == 2004
