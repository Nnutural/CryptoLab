"""Benchmark DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class BenchmarkResult(BaseModel):
    algorithm: str
    data_size_bytes: int
    iterations: int
    total_ms: float
    throughput_mb_per_s: float
    ns_per_op: float
