"""User account orchestration: register / login / logout / me."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.cache import CacheBackend
from app.core.exceptions import CryptoAPIException
from app.core.security import (
    AuthenticatedUser,
    hash_password,
    issue_access_token,
    verify_password,
)
from app.core.status_codes import StatusCode
from app.models.user import User
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

DUMMY_SALT = b"\x00" * 16
DUMMY_HASH = "00" * 32


def register(db: Session, req: RegisterRequest) -> RegisterResponse:
    """Create a new user with a PBKDF2-SHA256 password hash."""
    salt = secrets.token_bytes(16)
    password_hash = hash_password(req.password, salt)
    user = User(
        username=req.username,
        password_hash=password_hash,
        salt=salt,
        role="user",
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise CryptoAPIException(
            StatusCode.AUTH_USERNAME_EXISTS,
            "username_already_exists",
            http_status=409,
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "user_register_failed") from exc
    return RegisterResponse(user_id=user.id, created_at=user.created_at)


def login(db: Session, req: LoginRequest) -> LoginResponse:
    """Verify credentials and mint an access token."""
    user = db.execute(select(User).where(User.username == req.username)).scalar_one_or_none()
    if user is None:
        _dummy_verify(req.password)
        raise CryptoAPIException(StatusCode.AUTH_LOGIN_FAILED)
    if not verify_password(req.password, user.salt, user.password_hash):
        raise CryptoAPIException(StatusCode.AUTH_LOGIN_FAILED)

    try:
        user.last_login_at = datetime.now(UTC)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "user_login_update_failed") from exc

    token, _jti, _expires_at = issue_access_token(
        subject=str(user.id),
        username=user.username,
        role=user.role,
    )
    return LoginResponse(access_token=token, expires_in=_ttl_seconds(_expires_at))


async def logout(cache: CacheBackend, user: AuthenticatedUser) -> None:
    """Blacklist the current JWT until its natural expiry."""
    ttl = _ttl_seconds(user.expires_at)
    if ttl > 0:
        await cache.setex(f"jwt_blacklist:{user.jti}", ttl, "1")


def me(db: Session, user: AuthenticatedUser) -> CurrentUserResponse:
    """Return the current user's public profile."""
    row = db.get(User, user.id)
    if row is None:
        raise CryptoAPIException(StatusCode.AUTH_TOKEN_INVALID)
    return CurrentUserResponse(
        user_id=row.id,
        username=row.username,
        role=row.role,
        created_at=row.created_at,
        last_login_at=row.last_login_at,
    )


def _dummy_verify(password: str) -> None:
    verify_password(password, DUMMY_SALT, DUMMY_HASH)


def _ttl_seconds(expires_at: datetime) -> int:
    return max(0, int((expires_at - datetime.now(UTC)).total_seconds()))
