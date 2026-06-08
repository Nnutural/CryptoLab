"""Benchmark DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class BenchmarkResult(BaseModel):
    algorithm: str
    operation: str = "default"
    data_size_bytes: int
    iterations: int
    warmup_iterations: int = 0
    total_ms: float
    ns_per_op: float
    throughput_mb_per_s: float | None = None
    ops_per_sec: float | None = None
    ms_per_op: float | None = None
