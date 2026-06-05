"""Security helpers: JWT issuance, password hashing, sensitive-value redaction.

Implementation notes:
 - JWTs are HS256 with a configurable secret + short TTL + jti for blacklisting.
 - Passwords use PBKDF2-SHA256 with 10^5 iterations (per design §4.3 users table).
 - `redact_sensitive` is called by the audit middleware before logging payloads.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from app.core.config import get_settings


def issue_access_token(
    *, subject: str, role: str, extra_claims: dict[str, Any] | None = None
) -> tuple[str, str, datetime]:
    """Mint an access token; returns (token, jti, expires_at)."""
    raise NotImplementedError("issue_access_token: set iat, exp, jti, sub, role; sign HS256")


def decode_access_token(_token: str) -> dict[str, Any]:
    """Verify signature + expiry + blacklist; return claims or raise."""
    raise NotImplementedError(
        "decode_access_token: jwt.decode → check jti against Redis blacklist"
    )


def hash_password(_password: str, _salt: bytes) -> str:
    """PBKDF2-SHA256(password, salt, 100_000) → urlsafe string."""
    raise NotImplementedError("password hashing — call into Rust core for consistency")


def verify_password(_password: str, _salt: bytes, _expected_hash: str) -> bool:
    """Constant-time comparison of hash_password(password) and expected_hash."""
    raise NotImplementedError("verify_password — use hmac.compare_digest")


SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "secret",
        "key",
        "private_key",
        "jwt_secret",
        "master_key",
        "master_key_hex",
    }
)


def redact_sensitive(obj: Any) -> Any:
    """Recursively redact values whose key matches `SENSITIVE_KEYS`."""
    if isinstance(obj, dict):
        return {k: ("***REDACTED***" if k in SENSITIVE_KEYS else redact_sensitive(v))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_sensitive(v) for v in obj]
    return obj


def new_jti() -> str:
    """Fresh JWT id for blacklist lookups."""
    return str(uuid4())


# Re-exported so call sites don't need to import from datetime directly.
__all__ = [
    "issue_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
    "redact_sensitive",
    "new_jti",
    "datetime",
    "timedelta",
    "timezone",
    "get_settings",
    "jwt",
]
