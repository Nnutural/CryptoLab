"""Audit-log query endpoint."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.audit import OperationLogItem
from app.schemas.common import APIResponse
from app.services import audit_service

router = APIRouter()
USER_DEP = Depends(get_current_user)
DB_DEP = Depends(get_db)
USER_ID_QUERY = Query(default=None)
ALGORITHM_QUERY = Query(default=None)
SINCE_QUERY = Query(default=None)
UNTIL_QUERY = Query(default=None)
LIMIT_QUERY = Query(default=100, ge=1, le=1000)
OFFSET_QUERY = Query(default=0, ge=0)


@router.get("/logs", response_model=APIResponse[list[OperationLogItem]])
async def list_logs(
    request: Request,
    user=USER_DEP,
    db: Session = DB_DEP,
    user_id: int | None = USER_ID_QUERY,
    algorithm: str | None = ALGORITHM_QUERY,
    since: datetime | None = SINCE_QUERY,
    until: datetime | None = UNTIL_QUERY,
    limit: int = LIMIT_QUERY,
    offset: int = OFFSET_QUERY,
) -> APIResponse[list[dict]]:
    """Paginated audit query. Admin sees all rows; users see only their own."""
    rows = audit_service.query_logs(
        db,
        user=user,
        requested_user_id=user_id,
        algorithm=algorithm,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=[audit_service.row_to_item(row) for row in rows],
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
