"""Tests for /api/v1/audit/logs."""

from __future__ import annotations

import asyncio
import re

import httpx

HEX64 = re.compile(r"^[0-9a-f]{64}$")


async def test_audit_log_emitted_on_encrypt(
    client: httpx.AsyncClient,
    auth_headers,
) -> None:
    client.headers.update(await auth_headers(client, "audit-user"))
    encrypted = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "GCM",
            "padding": "None",
            "key_hex": "00" * 16,
            "iv_hex": "00" * 12,
            "plaintext_b64": "aGVsbG8=",
        },
    )
    assert encrypted.status_code == 200
    trace_id = encrypted.headers["X-Trace-Id"]

    logs = []
    for _ in range(20):
        response = await client.get("/api/v1/audit/logs", params={"limit": 5})
        logs = response.json()["data"]
        if logs:
            break
        await asyncio.sleep(0.05)

    assert logs
    row = logs[0]
    assert row["trace_id"] == trace_id
    assert row["operation"] == "aes_encrypt"
    assert row["algorithm"] == "AES-128-GCM"
    assert HEX64.fullmatch(row["input_hash"])
    assert HEX64.fullmatch(row["output_hash"])
    assert row["input_hash"] != "hello"
    assert row["output_hash"] != encrypted.json()["data"]["ciphertext_b64"]
