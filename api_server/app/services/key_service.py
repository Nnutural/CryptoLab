"""Key-store CRUD: store, fetch, decrypt, ownership, and revoke."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.kek import envelope_decrypt, envelope_encrypt, key_id_to_aad
from app.core.security import AuthenticatedUser
from app.core.status_codes import StatusCode
from app.models.key_store import KeyStore


def store_symmetric_key(
    db: Session,
    user: AuthenticatedUser,
    algorithm: str,
    key_material: bytes,
    label: str | None = None,
) -> str:
    """Encrypt and persist a symmetric key. Returns the key_id."""
    key_id = str(uuid4())
    aad = key_id_to_aad(key_id)
    ct, iv, tag = envelope_encrypt(key_material, aad)
    row = KeyStore(
        id=key_id,
        user_id=user.id,
        key_type="symmetric",
        algorithm=algorithm,
        key_material_encrypted=ct,
        iv=iv,
        auth_tag=tag,
        label=label,
    )
    try:
        db.add(row)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "key_store_insert") from exc
    return key_id


def store_key_pair(
    db: Session,
    user: AuthenticatedUser,
    algorithm: str,
    private_material: dict[str, str],
    public_material: dict[str, str],
    label: str | None = None,
) -> tuple[str, str]:
    """Store an asymmetric key pair as two linked rows. Returns (priv_id, pub_id)."""
    priv_id = str(uuid4())
    pub_id = str(uuid4())

    priv_bytes = json.dumps(private_material, separators=(",", ":")).encode()
    pub_bytes = json.dumps(public_material, separators=(",", ":")).encode()

    priv_aad = key_id_to_aad(priv_id)
    pub_aad = key_id_to_aad(pub_id)

    priv_ct, priv_iv, priv_tag = envelope_encrypt(priv_bytes, priv_aad)
    pub_ct, pub_iv, pub_tag = envelope_encrypt(pub_bytes, pub_aad)

    priv_row = KeyStore(
        id=priv_id,
        user_id=user.id,
        key_type="private",
        algorithm=algorithm,
        key_material_encrypted=priv_ct,
        iv=priv_iv,
        auth_tag=priv_tag,
        paired_key_id=pub_id,
        label=f"{label} (private)" if label else None,
    )
    pub_row = KeyStore(
        id=pub_id,
        user_id=user.id,
        key_type="public",
        algorithm=algorithm,
        key_material_encrypted=pub_ct,
        iv=pub_iv,
        auth_tag=pub_tag,
        paired_key_id=priv_id,
        label=f"{label} (public)" if label else None,
    )
    try:
        db.add(priv_row)
        db.add(pub_row)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "key_pair_insert") from exc
    return priv_id, pub_id


def _fetch_owned_row(db: Session, user: AuthenticatedUser, key_id: str) -> KeyStore:
    """Fetch a key row with ownership check BEFORE any decryption."""
    try:
        row = db.get(KeyStore, key_id)
    except SQLAlchemyError as exc:
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "key_fetch") from exc
    if row is None or row.deleted_at is not None:
        raise CryptoAPIException(StatusCode.KEY_NOT_FOUND)
    if row.user_id != user.id:
        raise CryptoAPIException(StatusCode.KEY_NOT_OWNED)
    return row


def fetch_and_decrypt(
    db: Session,
    user: AuthenticatedUser,
    key_id: str,
    expected_type: str | None = None,
) -> bytes:
    """Ownership-check then KEK-decrypt the key material. Returns plaintext bytes."""
    row = _fetch_owned_row(db, user, key_id)
    if expected_type is not None and row.key_type != expected_type:
        raise CryptoAPIException(StatusCode.KEY_TYPE_MISMATCH)
    aad = key_id_to_aad(key_id)
    try:
        return envelope_decrypt(row.key_material_encrypted, row.iv, row.auth_tag, aad)
    except Exception as exc:
        raise CryptoAPIException(StatusCode.DECRYPT_FAILED, "envelope_decrypt") from exc


def fetch_and_decrypt_json(
    db: Session,
    user: AuthenticatedUser,
    key_id: str,
    expected_type: str | None = None,
) -> dict[str, str]:
    """Like fetch_and_decrypt but JSON-parses the result."""
    raw = fetch_and_decrypt(db, user, key_id, expected_type)
    return json.loads(raw)


def fetch_public_material(
    db: Session,
    user: AuthenticatedUser,
    key_id: str,
) -> tuple[dict[str, str], KeyStore]:
    """Decrypt and return public key material. Only public-type keys allowed."""
    row = _fetch_owned_row(db, user, key_id)
    if row.key_type != "public":
        raise CryptoAPIException(StatusCode.KEY_PRIVATE_ACCESS_DENIED)
    aad = key_id_to_aad(key_id)
    try:
        raw = envelope_decrypt(row.key_material_encrypted, row.iv, row.auth_tag, aad)
    except Exception as exc:
        raise CryptoAPIException(StatusCode.DECRYPT_FAILED, "envelope_decrypt") from exc
    return json.loads(raw), row


def fetch_row_meta(db: Session, user: AuthenticatedUser, key_id: str) -> KeyStore:
    """Return key row metadata (no decryption). Ownership-checked."""
    return _fetch_owned_row(db, user, key_id)


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


def revoke(db: Session, user: AuthenticatedUser, key_id: str) -> None:
    """Soft-delete a user-owned key."""
    row = _fetch_owned_row(db, user, key_id)
    try:
        row.deleted_at = datetime.now(UTC)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "key_revoke_failed") from exc
