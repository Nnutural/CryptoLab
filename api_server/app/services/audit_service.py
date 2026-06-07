"""Audit-log emission and querying."""

from __future__ import annotations

import binascii
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.logging import get_logger
from app.core.security import AuthenticatedUser, redact_sensitive
from app.core.status_codes import StatusCode
from app.db.session import get_session_factory
from app.models.operation_log import OperationLog

logger = get_logger(__name__)


@dataclass(frozen=True)
class AuditRecord:
    """Immutable data needed for one operation_logs INSERT."""

    trace_id: str
    user_id: int | None
    operation: str
    algorithm: str | None
    key_id: str | None
    input_bytes: bytes | None
    output_bytes: bytes | None
    status_code: int
    duration_ms: float
    client_ip: str | None
    user_agent: str | None


async def record_operation_log(record: AuditRecord) -> None:
    """Insert one append-only audit row; never raise into business flow."""
    try:
        session_factory = get_session_factory()
        with session_factory() as db:
            db.add(
                OperationLog(
                    trace_id=record.trace_id,
                    user_id=record.user_id,
                    operation=record.operation,
                    algorithm=record.algorithm,
                    key_id=record.key_id,
                    input_hash=_sha256_hex(record.input_bytes),
                    output_hash=_sha256_hex(record.output_bytes),
                    status_code=record.status_code,
                    duration_ms=record.duration_ms,
                    client_ip=record.client_ip,
                    user_agent=record.user_agent,
                )
            )
            db.commit()
    except Exception as exc:  # pragma: no cover - verified by log path in integration
        logger.error(
            "audit log insert failed",
            error=type(exc).__name__,
            record=redact_sensitive(record.__dict__),
        )


def query_logs(
    db: Session,
    *,
    user: AuthenticatedUser,
    requested_user_id: int | None = None,
    algorithm: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[OperationLog]:
    """Query audit rows; non-admin users are constrained to their own rows."""
    try:
        statement: Select[tuple[OperationLog]] = select(OperationLog)
        if user.role != "admin":
            statement = statement.where(OperationLog.user_id == user.id)
        elif requested_user_id is not None:
            statement = statement.where(OperationLog.user_id == requested_user_id)
        if algorithm:
            statement = statement.where(OperationLog.algorithm == algorithm)
        if since:
            statement = statement.where(OperationLog.created_at >= since)
        if until:
            statement = statement.where(OperationLog.created_at <= until)
        statement = statement.order_by(OperationLog.created_at.desc()).offset(offset).limit(limit)
        return list(db.execute(statement).scalars().all())
    except SQLAlchemyError as exc:
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "audit_query_failed") from exc


def _sha256_hex(data: bytes | None) -> str | None:
    if data is None:
        return None
    try:
        import cryptolab_core

        return cryptolab_core.sha256_digest(data).hex()
    except (ImportError, AttributeError, ValueError, binascii.Error) as exc:
        raise RuntimeError("sha256_digest failed for audit log") from exc


def row_to_item(row: OperationLog) -> dict[str, Any]:
    """Serialize an OperationLog row for the API schema."""
    return {
        "id": row.id,
        "trace_id": row.trace_id,
        "user_id": row.user_id,
        "operation": row.operation,
        "algorithm": row.algorithm,
        "key_id": row.key_id,
        "input_hash": row.input_hash,
        "output_hash": row.output_hash,
        "status_code": row.status_code,
        "duration_ms": row.duration_ms,
        "client_ip": row.client_ip,
        "created_at": row.created_at,
    }
