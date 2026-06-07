"""HTTP-side throughput probe."""

from __future__ import annotations

import time

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import StatusCode
from app.schemas.benchmark import BenchmarkResult


def measure(algo: str) -> BenchmarkResult:
    """Run a small deterministic in-process benchmark."""
    payload = b"\x00" * 4096
    iterations = 128
    normalized = algo.lower()
    try:
        import cryptolab_core

        if normalized not in {"sha256", "sha-256"}:
            raise CryptoAPIException(StatusCode.ALGORITHM_UNSUPPORTED)
        start_ns = time.perf_counter_ns()
        for _ in range(iterations):
            cryptolab_core.sha256_digest(payload)
        duration_ns = time.perf_counter_ns() - start_ns
    except CryptoAPIException:
        raise
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "benchmark_failed") from exc

    total_ms = duration_ns / 1_000_000
    total_mb = len(payload) * iterations / (1024 * 1024)
    return BenchmarkResult(
        algorithm="sha256",
        data_size_bytes=len(payload),
        iterations=iterations,
        total_ms=total_ms,
        throughput_mb_per_s=total_mb / max(total_ms / 1000, 1e-9),
        ns_per_op=duration_ns / iterations,
    )
