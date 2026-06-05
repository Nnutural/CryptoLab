"""HTTP-side throughput probe."""

from __future__ import annotations

from app.schemas.benchmark import BenchmarkResult


async def measure(_algo: str) -> BenchmarkResult:
    raise NotImplementedError(
        "for a fixed payload (1MB), call cryptolab_core.<algo> N times in a tight loop, "
        "report total_ms, MB/s, ns/op"
    )
