"""Quick HTTP-side benchmark endpoint.

Heavier criterion benches live under `benchmarks/`; this one exists so the
front-end can render an in-browser throughput card without spinning up Cargo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.benchmark import BenchmarkResult
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/{algo}", response_model=APIResponse[BenchmarkResult])
async def benchmark(
    algo: str = Path(..., description="Algorithm name, e.g. aes-256-gcm, sha256, rsa-1024"),
    _user: User = Depends(get_current_user),
) -> APIResponse[BenchmarkResult]:
    """Run a small in-process throughput probe for `algo`."""
    raise NotImplementedError("services.benchmark_service.measure(algo)")
