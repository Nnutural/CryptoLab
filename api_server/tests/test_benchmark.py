"""Tests for /api/v1/benchmark/*."""

from __future__ import annotations

import httpx


async def test_benchmark_returns_throughput(
    client: httpx.AsyncClient,
    auth_headers,
) -> None:
    client.headers.update(await auth_headers(client, "benchmark-user"))
    response = await client.get("/api/v1/benchmark/sha256")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["algorithm"] == "sha256"
    assert data["iterations"] > 0
    assert data["throughput_mb_per_s"] > 0
