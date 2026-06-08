"""`algorithm_metrics` table, see design doc section 4.3 Table 4."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

ID_TYPE = BigInteger().with_variant(Integer, "sqlite")


class AlgorithmMetric(Base):
    __tablename__ = "algorithm_metrics"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    algorithm: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    operation: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    data_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
