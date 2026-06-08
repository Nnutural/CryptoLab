"""Tests for /api/v1/benchmark/*."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import httpx
import pytest

THROUGHPUT_ALGOS = [
    "aes",
    "sm4",
    "rc6",
    "sha1",
    "sha256",
    "sha3_256",
    "ripemd160",
]

FRONTEND_ALIASES = [
    "aes_ecb",
    "aes_gcm",
    "sm4_ecb",
    "rc6_ecb",
    "sha512",
    "rsa_enc",
]


@pytest.fixture
async def authed_client(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
) -> httpx.AsyncClient:
    client.headers.update(await auth_headers(client, "benchmark-user"))
    return client


@pytest.mark.parametrize("algo", THROUGHPUT_ALGOS)
async def test_throughput_benchmarks_return_metrics(
    authed_client: httpx.AsyncClient,
    algo: str,
) -> None:
    response = await authed_client.get(f"/api/v1/benchmark/{algo}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["algorithm"] in {algo, "aes", "sm4", "rc6"}
    assert data["operation"] in {"encrypt", "digest"}
    assert data["data_size_bytes"] == 1_048_576
    assert data["warmup_iterations"] == 5
    assert data["iterations"] >= 100
    assert data["total_ms"] > 0
    assert data["ns_per_op"] > 0
    assert data["throughput_mb_per_s"] > 0


async def test_hmac_benchmark_returns_ops_metric(authed_client: httpx.AsyncClient) -> None:
    response = await authed_client.get("/api/v1/benchmark/hmac")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["algorithm"] == "hmac"
    assert data["operation"] == "hmac_sha256"
    assert data["data_size_bytes"] == 1024
    assert data["iterations"] >= 1000
    assert data["total_ms"] > 0
    assert data["ops_per_sec"] > 0
    assert data["ms_per_op"] > 0
    assert data["throughput_mb_per_s"] is None


async def test_pbkdf2_benchmark_uses_10000_inner_iterations(
    authed_client: httpx.AsyncClient,
) -> None:
    response = await authed_client.get("/api/v1/benchmark/pbkdf2")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["algorithm"] == "pbkdf2"
    assert data["operation"] == "derive_10000"
    assert data["iterations"] == 10
    assert data["warmup_iterations"] == 1
    assert data["total_ms"] > 0
    assert data["ns_per_op"] > 0
    assert data["ms_per_op"] > 0
    assert data["throughput_mb_per_s"] is None


@pytest.mark.parametrize(
    ("algo", "operation", "iterations"),
    [
        ("rsa_keygen", "keygen", 10),
        ("rsa_encrypt", "encrypt", 100),
        ("rsa_decrypt", "decrypt", 50),
        ("rsa_sign", "sign", 50),
        ("rsa_verify", "verify", 100),
        ("ecdsa_sign", "sign", 50),
        ("ecdsa_verify", "verify", 100),
    ],
)
async def test_public_key_benchmarks_return_ops_metrics(
    authed_client: httpx.AsyncClient,
    algo: str,
    operation: str,
    iterations: int,
) -> None:
    response = await authed_client.get(f"/api/v1/benchmark/{algo}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["algorithm"] in {"rsa", "ecdsa"}
    assert data["operation"] == operation
    assert data["iterations"] == iterations
    assert data["total_ms"] > 0
    assert data["ns_per_op"] > 0
    assert data["ops_per_sec"] > 0
    assert data["ms_per_op"] > 0
    assert data["throughput_mb_per_s"] is None


@pytest.mark.parametrize("algo", FRONTEND_ALIASES)
async def test_frontend_benchmark_aliases_are_supported(
    authed_client: httpx.AsyncClient,
    algo: str,
) -> None:
    response = await authed_client.get(f"/api/v1/benchmark/{algo}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["iterations"] > 0
    assert data["total_ms"] > 0
    assert data["ns_per_op"] > 0


async def test_invalid_benchmark_algo_returns_4xx(authed_client: httpx.AsyncClient) -> None:
    response = await authed_client.get("/api/v1/benchmark/not_an_algorithm")

    assert 400 <= response.status_code < 500
    assert response.json()["code"] == 2004
