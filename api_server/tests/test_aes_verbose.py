"""AES verbose trace API tests."""

from __future__ import annotations

import base64
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
        c.headers.update(await auth_headers(c, "aes-verbose-user"))
        yield c


async def _user_id(client: httpx.AsyncClient) -> int:
    response = await client.get("/api/v1/auth/me")
    return response.json()["data"]["user_id"]


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def hx(value: str) -> bytes:
    return bytes.fromhex(value)


@pytest.mark.parametrize(
    ("key_hex", "key_bits", "rounds", "ciphertext_hex"),
    [
        (
            "000102030405060708090a0b0c0d0e0f",
            128,
            10,
            "69c4e0d86a7b0430d8cdb78070b4c55a",
        ),
        (
            "000102030405060708090a0b0c0d0e0f1011121314151617",
            192,
            12,
            "dda97ca4864cdfe06eaf70a0ec0d7191",
        ),
        (
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
            256,
            14,
            "8ea2b7ca516745bfeafc49904b496089",
        ),
    ],
)
async def test_verbose_aes_ecb_single_block_returns_trace_for_all_key_sizes(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
    key_hex: str,
    key_bits: int,
    rounds: int,
    ciphertext_hex: str,
) -> None:
    uid = await _user_id(client)
    key_id = store_sym_key(uid, "aes", hx(key_hex))

    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "ECB",
            "padding": "None",
            "key_id": key_id,
            "plaintext_b64": b64(hx("00112233445566778899aabbccddeeff")),
            "verbose": True,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert base64.b64decode(data["ciphertext_b64"]).hex() == ciphertext_hex
    trace = data["trace"]
    assert trace["key_size_bits"] == key_bits
    assert trace["total_rounds"] == rounds
    assert trace["plaintext_hex"] == "00112233445566778899aabbccddeeff"
    assert trace["ciphertext_hex"] == ciphertext_hex
    assert len(trace["round_keys_hex"]) == rounds + 1
    assert len(trace["rounds"]) == rounds
    assert trace["rounds"][-1]["after_mix_columns"] is None
    assert len(trace["timings_ns"]["per_round_ns"]) == rounds


async def test_verbose_aes128_trace_contains_fips_round_values(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    key_id = store_sym_key(uid, "aes", hx("000102030405060708090a0b0c0d0e0f"))

    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "ECB",
            "padding": "None",
            "key_id": key_id,
            "plaintext_b64": b64(hx("00112233445566778899aabbccddeeff")),
            "verbose": True,
        },
    )

    assert response.status_code == 200
    trace = response.json()["data"]["trace"]
    assert trace["total_rounds"] == 10
    assert trace["initial_add_round_key"] == "00102030405060708090a0b0c0d0e0f0"
    assert trace["rounds"][0]["after_sub_bytes"] == "63cab7040953d051cd60e0e7ba70e18c"
    assert trace["rounds"][0]["after_shift_rows"] == "6353e08c0960e104cd70b751bacad0e7"
    assert trace["rounds"][0]["after_mix_columns"] == "5f72641557f5bc92f7be3b291db9f91a"
    assert trace["rounds"][9]["after_add_round_key"] == "69c4e0d86a7b0430d8cdb78070b4c55a"


async def test_verbose_rejects_cbc_mode(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    key_id = store_sym_key(uid, "aes", bytes(16))
    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "CBC",
            "padding": "None",
            "key_id": key_id,
            "iv_hex": "00" * 16,
            "plaintext_b64": b64(bytes(16)),
            "verbose": True,
        },
    )
    assert response.status_code == 400
    assert response.json()["message"] == "verbose mode requires ECB mode"


async def test_verbose_rejects_non_16_byte_plaintext(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    key_id = store_sym_key(uid, "aes", bytes(16))
    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "ECB",
            "padding": "None",
            "key_id": key_id,
            "plaintext_b64": b64(bytes(15)),
            "verbose": True,
        },
    )
    assert response.status_code == 400
    assert response.json()["message"] == "verbose mode requires exactly 16 bytes plaintext"


async def test_verbose_rejects_sm4(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    key_id = store_sym_key(uid, "sm4", bytes(16))
    response = await client.post(
        "/api/v1/symmetric/sm4/encrypt",
        json={
            "algorithm": "sm4",
            "mode": "ECB",
            "padding": "None",
            "key_id": key_id,
            "plaintext_b64": b64(bytes(16)),
            "verbose": True,
        },
    )
    assert response.status_code == 400
    assert response.json()["message"] == "verbose mode is only supported for AES"


async def test_verbose_false_keeps_existing_response_shape(
    client: httpx.AsyncClient,
    store_sym_key: Callable,
) -> None:
    uid = await _user_id(client)
    key_id = store_sym_key(uid, "aes", bytes(16))
    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "ECB",
            "padding": "PKCS7",
            "key_id": key_id,
            "plaintext_b64": b64(b"backward-compatible"),
            "verbose": False,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ciphertext_b64"]
    assert data["trace"] is None
