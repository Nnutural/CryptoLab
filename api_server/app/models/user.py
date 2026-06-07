"""`users` table — see design doc §4.3 Table 1."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.key_store import KeyStore
    from app.models.operation_log import OperationLog


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    role: Mapped[str] = mapped_column(String(16), default="user")
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    keys: Mapped[list[KeyStore]] = relationship(back_populates="user")
    logs: Mapped[list[OperationLog]] = relationship(back_populates="user")
