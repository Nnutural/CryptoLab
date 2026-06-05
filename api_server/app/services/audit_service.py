"""Audit-log emission and querying.

Privacy: only SHA-256 of input/output payloads are persisted, never plaintext.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation_log import OperationLog
from app.models.user import User


async def log(
    _db: AsyncSession,
    *,
    _trace_id: UUID,
    _user: User | None,
    _operation: str,
    _algorithm: str | None,
    _key_id: UUID | None,
    _input_bytes: bytes | None,
    _output_bytes: bytes | None,
    _status_code: int,
    _duration_ms: float,
    _client_ip: str | None,
    _user_agent: str | None,
) -> None:
    raise NotImplementedError(
        "compute sha256(input/output) → INSERT into operation_logs "
        "(append-only, no UPDATE/DELETE allowed)"
    )


async def query(
    _db: AsyncSession,
    *,
    _user: User,
    _algorithm: str | None = None,
    _since: datetime | None = None,
    _until: datetime | None = None,
    _limit: int = 100,
) -> list[OperationLog]:
    raise NotImplementedError(
        "SELECT * with predicates; admins see all rows, users see only their own"
    )
