"""`algorithm_metrics` table — see design doc §4.3 Table 4."""

from __future__ import annotations

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AlgorithmMetric(Base, TimestampMixin):
    __tablename__ = "algorithm_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    algorithm: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    data_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    operation: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    memory_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
