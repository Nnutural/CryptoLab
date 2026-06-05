"""Declarative base and reusable mixins."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Project-wide declarative base."""


class TimestampMixin:
    """Adds `created_at` (and only `created_at`) — operation_logs is append-only."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
