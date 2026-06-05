"""Key-store orchestration: wrap with KEK, persist, list, revoke.

Threat model: the database may be compromised; the KEK lives only in env.
A leaked DB dump therefore does not yield usable private keys.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.key_store import KeyStore
from app.models.user import User


async def store(
    _db: AsyncSession,
    _user: User,
    _key_type: str,
    _algorithm: str,
    _key_material: bytes,
    _label: str | None = None,
) -> KeyStore:
    raise NotImplementedError(
        "iv = OsRng(12) → (ct, tag) = AES-256-GCM(KEK, iv, key_material) "
        "→ INSERT into key_store"
    )


async def fetch(_db: AsyncSession, _user: User, _key_id: UUID) -> bytes:
    raise NotImplementedError(
        "SELECT row → assert user_id matches → AES-256-GCM decrypt → return plaintext key bytes"
    )


async def list_for_user(_db: AsyncSession, _user: User) -> list[KeyStore]:
    raise NotImplementedError("SELECT * WHERE user_id = user.id AND deleted_at IS NULL")


async def revoke(_db: AsyncSession, _user: User, _key_id: UUID) -> None:
    raise NotImplementedError("UPDATE key_store SET deleted_at = now() WHERE id = key_id AND user_id = user.id")
