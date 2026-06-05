"""Audit-log DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OperationLogItem(BaseModel):
    id: int
    trace_id: UUID
    user_id: int | None
    operation: str
    algorithm: str | None
    key_id: UUID | None
    input_hash: str | None
    output_hash: str | None
    status_code: int
    duration_ms: float
    client_ip: str | None
    created_at: datetime
