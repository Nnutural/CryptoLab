"""Audit-log query endpoint."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.audit import OperationLogItem
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/logs", response_model=APIResponse[list[OperationLogItem]])
async def list_logs(
    _user: User = Depends(get_current_user),
    _algorithm: str | None = Query(default=None),
    _since: datetime | None = Query(default=None),
    _until: datetime | None = Query(default=None),
    _limit: int = Query(default=100, ge=1, le=1000),
) -> APIResponse[list[OperationLogItem]]:
    """Paginated, multi-dimensional audit query. Admin sees everyone; user sees self."""
    raise NotImplementedError("services.audit_service.query(user, filters)")
