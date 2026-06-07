"""Quick HTTP-side benchmark endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Request

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.middleware.auth import get_current_user
from app.schemas.benchmark import BenchmarkResult
from app.schemas.common import APIResponse
from app.services import benchmark_service

router = APIRouter()
USER_DEP = Depends(get_current_user)


@router.get("/{algo}", response_model=APIResponse[BenchmarkResult])
async def benchmark(
    request: Request,
    algo: str = Path(..., description="Algorithm name, e.g. sha256"),
    _user=USER_DEP,
) -> APIResponse[BenchmarkResult]:
    """Run a small in-process throughput probe for algo."""
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=benchmark_service.measure(algo),
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
