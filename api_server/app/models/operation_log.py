"""`operation_logs` table — see design doc §4.3 Table 3.

Append-only (no UPDATE/DELETE policy enforced via SQL trigger in alembic
migration). Stores ONLY SHA-256 of input/output bytes, never plaintext.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, Double, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class OperationLog(Base, TimestampMixin):
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trace_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=True
    )
    operation: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    algorithm: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    key_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_ms: Mapped[float] = mapped_column(Double, nullable=False)
    client_ip: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="logs")
