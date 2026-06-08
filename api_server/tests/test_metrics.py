"""Tests for algorithm_metrics collection and querying."""

from __future__ import annotations

import asyncio
import base64
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy import func, select

from app.db.session import get_session_factory
from app.models.algorithm_metric import AlgorithmMetric
from app.services import metrics_service


async def _authed_headers(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    username: str = "metrics-user",
) -> dict[str, str]:
    return await auth_headers(client, username)


def _count_metrics(algorithm: str | None = None, operation: str | None = None) -> int:
    statement = select(func.count()).select_from(AlgorithmMetric)
    if algorithm is not None:
        statement = statement.where(AlgorithmMetric.algorithm == algorithm)
    if operation is not None:
        statement = statement.where(AlgorithmMetric.operation == operation)
    with get_session_factory()() as db:
        return int(db.execute(statement).scalar_one())


async def _wait_for_count(
    expected: int,
    *,
    algorithm: str | None = None,
    operation: str | None = None,
    timeout_s: float = 1.0,
) -> int:
    deadline = time.perf_counter() + timeout_s
    last_count = _count_metrics(algorithm, operation)
    while last_count < expected and time.perf_counter() < deadline:
        await asyncio.sleep(0.02)
        last_count = _count_metrics(algorithm, operation)
    return last_count


async def test_record_schedules_async_insert() -> None:
    await metrics_service.record(
        "aes",
        "encrypt",
        data_size_bytes=16,
        duration_ns=1234,
        sampling_rate=1.0,
    )

    count = await _wait_for_count(1, algorithm="aes", operation="encrypt")

    assert count == 1


async def test_record_respects_zero_sampling_rate() -> None:
    await metrics_service.record(
        "aes",
        "encrypt",
        data_size_bytes=16,
        duration_ns=1234,
        sampling_rate=0.0,
    )
    await asyncio.sleep(0.05)

    assert _count_metrics("aes", "encrypt") == 0


async def test_metrics_query_requires_jwt(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/metrics")

    assert response.status_code == 401
    assert response.json()["code"] == 4101


async def test_metrics_query_filters_and_limits(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> None:
    now = datetime.now(UTC)
    with get_session_factory()() as db:
        db.add_all(
            [
                AlgorithmMetric(
                    algorithm="aes",
                    operation="encrypt",
                    data_size_bytes=16,
                    duration_ns=100,
                    recorded_at=now - timedelta(minutes=2),
                ),
                AlgorithmMetric(
                    algorithm="aes",
                    operation="decrypt",
                    data_size_bytes=16,
                    duration_ns=200,
                    recorded_at=now - timedelta(minutes=1),
                ),
                AlgorithmMetric(
                    algorithm="sha256",
                    operation="digest",
                    data_size_bytes=32,
                    duration_ns=300,
                    recorded_at=now,
                ),
            ]
        )
        db.commit()

    headers = await _authed_headers(client, auth_headers, "metrics-query-user")
    response = await client.get(
        "/api/v1/metrics",
        params={"algorithm": "aes", "operation": "encrypt", "limit": 10},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1000
    assert body["data"] == [
        {
            "algorithm": "aes",
            "operation": "encrypt",
            "duration_ns": 100,
            "recorded_at": body["data"][0]["recorded_at"],
        }
    ]


async def test_symmetric_api_records_sampled_metric(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    store_sym_key: Callable,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METRICS_SAMPLING_RATE", "1.0")
    headers = await _authed_headers(client, auth_headers, "metrics-aes-user")
    client.headers.update(headers)
    user_id = (await client.get("/api/v1/auth/me")).json()["data"]["user_id"]
    key_id = store_sym_key(user_id, "aes", bytes(16))

    response = await client.post(
        "/api/v1/symmetric/aes/encrypt",
        json={
            "algorithm": "aes",
            "mode": "ECB",
            "padding": "PKCS7",
            "key_id": key_id,
            "plaintext_b64": base64.b64encode(b"hello metrics").decode("ascii"),
        },
    )

    assert response.status_code == 200
    count = await _wait_for_count(1, algorithm="aes", operation="encrypt")
    assert count == 1


async def test_benchmark_records_metric_with_forced_sampling(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METRICS_SAMPLING_RATE", "0.0")
    headers = await _authed_headers(client, auth_headers, "metrics-benchmark-user")
    response = await client.get("/api/v1/benchmark/sha256", headers=headers)

    assert response.status_code == 200
    count = await _wait_for_count(1, algorithm="sha256", operation="digest")
    assert count == 1


async def test_metrics_collection_does_not_wait_for_insert(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    store_sym_key: Callable,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers = await _authed_headers(client, auth_headers, "metrics-latency-user")
    client.headers.update(headers)
    user_id = (await client.get("/api/v1/auth/me")).json()["data"]["user_id"]
    key_id = store_sym_key(user_id, "aes", bytes(16))
    payload = {
        "algorithm": "aes",
        "mode": "ECB",
        "padding": "PKCS7",
        "key_id": key_id,
        "plaintext_b64": base64.b64encode(b"latency sample block").decode("ascii"),
    }

    async def slow_insert(_metric: metrics_service.MetricRecord) -> None:
        await asyncio.sleep(0.2)

    monkeypatch.setenv("METRICS_SAMPLING_RATE", "1.0")
    monkeypatch.setattr(metrics_service, "_insert", slow_insert)

    start = time.perf_counter()
    response = await client.post("/api/v1/symmetric/aes/encrypt", json=payload)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 150
