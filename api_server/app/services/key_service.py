"""Key-store query and revoke operations."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.security import AuthenticatedUser
from app.core.status_codes import StatusCode
from app.models.key_store import KeyStore


def list_for_user(db: Session, user: AuthenticatedUser) -> list[KeyStore]:
    """List non-deleted keys owned by the current user."""
    try:
        return list(
            db.execute(
                select(KeyStore).where(
                    KeyStore.user_id == user.id,
                    KeyStore.deleted_at.is_(None),
                )
            )
            .scalars()
            .all()
        )
    except SQLAlchemyError as exc:
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "key_list_failed") from exc


def revoke(db: Session, user: AuthenticatedUser, key_id: UUID) -> None:
    """Soft-delete a user-owned key."""
    try:
        row = db.get(KeyStore, str(key_id))
        if row is None or row.user_id != user.id or row.deleted_at is not None:
            raise CryptoAPIException(StatusCode.KEY_MISMATCH, "key_not_found")
        row.deleted_at = datetime.now(UTC)
        db.commit()
    except CryptoAPIException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "key_revoke_failed") from exc
