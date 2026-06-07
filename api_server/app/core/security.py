"""Security helpers for JWTs, password hashing, and redaction."""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from app.core.config import get_settings


@dataclass(frozen=True)
class AuthenticatedUser:
    """Lightweight request user context; routers must not depend on ORM objects."""

    id: int
    username: str
    role: str
    jti: str
    token: str
    expires_at: datetime


def issue_access_token(
    *, subject: str, username: str, role: str, extra_claims: dict[str, Any] | None = None
) -> tuple[str, str, datetime]:
    """Mint an HS256 access token and return (token, jti, expires_at)."""
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(seconds=settings.jwt_access_ttl_seconds)
    jti = new_jti()
    payload: dict[str, Any] = {
        "sub": subject,
        "username": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": jti,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify JWT signature and expiry, returning decoded claims."""
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "exp", "iat", "jti"]},
    )


def hash_password(password: str, salt: bytes) -> str:
    """PBKDF2-HMAC-SHA256(password, salt) via the Rust core."""
    import cryptolab_core

    settings = get_settings()
    derived = cryptolab_core.pbkdf2_hmac_sha256(
        password.encode("utf-8"),
        salt,
        settings.password_pbkdf2_iterations,
        32,
    )
    return derived.hex()


def verify_password(password: str, salt: bytes, expected_hash: str) -> bool:
    """Constant-time password hash verification."""
    calculated = hash_password(password, salt)
    return hmac.compare_digest(calculated, expected_hash)


SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "salt",
        "secret",
        "key",
        "private_key",
        "session_key",
        "access_token",
        "authorization",
        "jwt_secret",
        "master_key",
        "master_key_hex",
        "key_material",
    }
)


def redact_sensitive(obj: Any) -> Any:
    """Recursively redact sensitive dict values before logging."""
    if isinstance(obj, dict):
        return {
            str(k): ("***REDACTED***" if str(k).lower() in SENSITIVE_KEYS else redact_sensitive(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact_sensitive(v) for v in obj]
    return obj


def new_jti() -> str:
    """Fresh JWT id for blacklist lookups."""
    return str(uuid4())
