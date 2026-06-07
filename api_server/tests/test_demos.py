"""Tests for /api/v1/demos/* (vulnerability demos)."""

from __future__ import annotations

import base64
import struct
import zlib
from collections.abc import AsyncIterator

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


async def post_demo(client: httpx.AsyncClient, path: str, payload: dict[str, object]) -> dict:
    response = await client.post(f"/api/v1/demos/{path}", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert body["data"]["banner"] == "教学演示路径，刻意暴露不安全实现；生产环境严禁调用"  # noqa: RUF001
    return body["data"]


async def test_ecb_image_leak_has_repeated_blocks_and_cbc_does_not(
    client: httpx.AsyncClient,
) -> None:
    image = _pattern_bmp(256, 256)
    data = await post_demo(
        client,
        "ecb_image_leak",
        {"image_b64": b64(image), "key_hex": "00112233445566778899aabbccddeeff"},
    )

    cbc_pixels = _png_rgb_bytes(base64.b64decode(data["cbc_encrypted_png_b64"]))
    _, cbc_ratio = _duplicate_block_ratio(cbc_pixels)
    assert data["block_count"] >= (256 * 256 * 3) // 16
    assert data["duplicate_block_ratio"] > 0.01
    assert cbc_ratio < 0.001


async def test_ecdsa_k_reuse_recovers_d(client: httpx.AsyncClient) -> None:
    data = await post_demo(
        client,
        "ecdsa_k_reuse",
        {"message1": "BUPT phase E message one", "message2": "BUPT phase E message two"},
    )

    assert data["r_equal"] is True
    assert data["recovery_matches_original"] is True
    assert data["private_key_hex"].lstrip("0") == data["recovered_d_hex"].lstrip("0")


async def test_rsa_low_exponent_default_recovers_plaintext(client: httpx.AsyncClient) -> None:
    data = await post_demo(client, "rsa_low_exponent", {})

    assert data["e"] == 3
    assert data["cube_safe"] is True
    assert data["recovered_plaintext"] == "BUPT2026"
    assert data["recovery_matches_original"] is True


async def test_rsa_low_exponent_rejects_long_message(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/demos/rsa_low_exponent", json={"message": "A" * 200})

    assert response.status_code == 422
    assert response.json()["code"] == 2001
    assert "message_too_long_for_cube_attack" in str(response.json()["data"])


async def test_pbkdf2_iteration_impact_has_linear_cost(client: httpx.AsyncClient) -> None:
    data = await post_demo(
        client,
        "pbkdf2_iteration_impact",
        {"iterations_list": [10_000, 100_000], "key_len": 32},
    )

    assert len(data["measurements"]) == 2
    assert [m["iterations"] for m in data["measurements"]] == [10_000, 100_000]
    assert 5.0 <= data["ratio_1m_over_100k"] <= 20.0


def _pattern_bmp(width: int, height: int) -> bytes:
    row_padding = (4 - (width * 3) % 4) % 4
    rows = []
    for y in range(height - 1, -1, -1):
        row = bytearray()
        for x in range(width):
            if (x // 32 + y // 32) % 2 == 0:
                rgb = (0x20, 0x20, 0x20)
            else:
                rgb = (0xe0, 0xe0, 0xe0)
            row.extend((rgb[2], rgb[1], rgb[0]))
        row.extend(b"\x00" * row_padding)
        rows.append(bytes(row))
    pixel_data = b"".join(rows)
    file_size = 14 + 40 + len(pixel_data)
    header = b"BM" + struct.pack("<IHHI", file_size, 0, 0, 54)
    dib = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        height,
        1,
        24,
        0,
        len(pixel_data),
        2835,
        2835,
        0,
        0,
    )
    return header + dib + pixel_data


def _duplicate_block_ratio(data: bytes) -> tuple[int, float]:
    blocks = [data[i : i + 16] for i in range(0, len(data), 16)]
    return len(blocks), (len(blocks) - len(set(blocks))) / len(blocks)


def _png_rgb_bytes(data: bytes) -> bytes:
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset = 8
    width = 0
    height = 0
    color_type = 0
    idat = bytearray()
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
            assert bit_depth == 8
            assert color_type == 2
            assert interlace == 0
        elif chunk_type == b"IDAT":
            idat.extend(chunk)
        elif chunk_type == b"IEND":
            break

    scanlines = zlib.decompress(bytes(idat))
    stride = width * 3
    rows = []
    prev = bytearray(stride)
    pos = 0
    for _ in range(height):
        filter_type = scanlines[pos]
        pos += 1
        raw = bytearray(scanlines[pos : pos + stride])
        pos += stride
        row = _png_unfilter(filter_type, raw, prev, 3)
        rows.append(bytes(row))
        prev = row
    return b"".join(rows)


def _png_unfilter(filter_type: int, raw: bytearray, prev: bytearray, bpp: int) -> bytearray:
    out = bytearray(raw)
    for i, value in enumerate(raw):
        left = out[i - bpp] if i >= bpp else 0
        up = prev[i]
        upper_left = prev[i - bpp] if i >= bpp else 0
        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        elif filter_type == 4:
            predictor = _paeth(left, up, upper_left)
        else:
            raise AssertionError(f"unsupported PNG filter {filter_type}")
        out[i] = (value + predictor) & 0xFF
    return out


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c
