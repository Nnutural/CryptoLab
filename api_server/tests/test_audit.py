"""Tests for /api/v1/audit/logs."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable

import httpx

HEX64 = re.compile(r"^[0-9a-f]{64}$")


async def test_audit_log_emitted_on_encrypt(
    client: httpx.AsyncClient,
    auth_headers: Callable,
    store_sym_key: Callable,
) -> None:
    headers = await auth_headers(client, "audit-user")
    client.headers.update(headers)

    me = await client.get("/api/v1/auth/me")
    uid = me.json()["data"]["user_id"]

    kid = store_sym_key(uid, "aes", bytes(16))

    encrypted = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "GCM",
            "padding": "None",
            "key_id": kid,
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
    assert row["algorithm"] == "AES-GCM"
    assert HEX64.fullmatch(row["input_hash"])
    assert HEX64.fullmatch(row["output_hash"])
    assert row["key_id"] == kid
