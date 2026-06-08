"""Tests for /api/v1/encoding/* (Base64 / UTF-8)."""

from __future__ import annotations

import base64
import secrets
from collections.abc import AsyncIterator

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


async def test_base64_encode_hello(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/encoding/base64/encode", json={"data": "hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert body["data"]["encoded"] == "aGVsbG8="


async def test_base64_decode_hello(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/encoding/base64/decode",
        json={"encoded": "aGVsbG8="},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert base64.b64decode(body["data"]["data"]) == b"hello"


async def test_base64_decode_invalid_returns_encoding_error(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/encoding/base64/decode",
        json={"encoded": "Zm9v*"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == 2003


async def test_base64_empty_roundtrip(client: httpx.AsyncClient) -> None:
    encoded_response = await client.post("/api/v1/encoding/base64/encode", json={"data": ""})
    assert encoded_response.status_code == 200
    encoded = encoded_response.json()["data"]["encoded"]
    assert encoded == ""

    decoded_response = await client.post(
        "/api/v1/encoding/base64/decode",
        json={"encoded": encoded},
    )
    assert decoded_response.status_code == 200
    assert decoded_response.json()["data"]["data"] == ""


async def test_base64_random_binary_decode_roundtrip(client: httpx.AsyncClient) -> None:
    payload = secrets.token_bytes(1024)
    encoded = base64.b64encode(payload).decode("ascii")

    response = await client.post("/api/v1/encoding/base64/decode", json={"encoded": encoded})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert base64.b64decode(body["data"]["data"]) == payload


async def test_utf8_encode_chinese_returns_base64_bytes(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/encoding/utf8/encode", json={"data": "你好"})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert base64.b64decode(body["data"]["encoded"]) == "你好".encode("utf-8")


async def test_utf8_decode_base64_bytes_returns_text(client: httpx.AsyncClient) -> None:
    text = "a你𝄞"
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")

    response = await client.post("/api/v1/encoding/utf8/decode", json={"data": encoded})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert body["data"]["data"] == text


async def test_utf8_decode_invalid_returns_encoding_error(client: httpx.AsyncClient) -> None:
    overlong_nul = base64.b64encode(bytes([0xC0, 0x80])).decode("ascii")

    response = await client.post("/api/v1/encoding/utf8/decode", json={"data": overlong_nul})

    assert response.status_code == 400
    assert response.json()["code"] == 2003
