"""Algorithm performance metrics query endpoint."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.common import APIResponse
from app.schemas.metrics import AlgorithmMetricItem
from app.services import metrics_service

router = APIRouter()
USER_DEP = Depends(get_current_user)
DB_DEP = Depends(get_db)
ALGORITHM_QUERY = Query(default=None)
OPERATION_QUERY = Query(default=None)
SINCE_QUERY = Query(default=None)
UNTIL_QUERY = Query(default=None)
LIMIT_QUERY = Query(default=200, ge=1, le=1000)


@router.get("", response_model=APIResponse[list[AlgorithmMetricItem]])
async def list_metrics(
    request: Request,
    _user=USER_DEP,
    db: Session = DB_DEP,
    algorithm: str | None = ALGORITHM_QUERY,
    operation: str | None = OPERATION_QUERY,
    since: datetime | None = SINCE_QUERY,
    until: datetime | None = UNTIL_QUERY,
    limit: int = LIMIT_QUERY,
) -> APIResponse[list[dict[str, object]]]:
    rows = metrics_service.query_metrics(
        db,
        algorithm=algorithm,
        operation=operation,
        since=since,
        until=until,
        limit=limit,
    )
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=[metrics_service.row_to_item(row) for row in rows],
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
