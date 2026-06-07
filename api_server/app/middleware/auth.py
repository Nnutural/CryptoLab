"""JWT authentication middleware and current-user dependency."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.cache import CacheBackend
from app.core.exceptions import CryptoAPIException
from app.core.security import AuthenticatedUser, decode_access_token
from app.core.status_codes import DEFAULT_MESSAGES, HTTP_FOR_STATUS, StatusCode
from app.schemas.common import APIResponse

PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/health",
        "/healthz",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)

PUBLIC_PREFIXES: tuple[str, ...] = (
    "/api/v1/encoding/",
    "/api/v1/hash/",
    "/api/v1/demos/",
    "/docs/",
)

PROTECTED_PREFIXES: tuple[str, ...] = (
    "/api/v1/symmetric/",
    "/api/v1/pubkey/",
    "/api/v1/scenarios/",
    "/api/v1/audit/",
    "/api/v1/keys",
    "/api/v1/benchmark/",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Verify bearer tokens and attach an AuthenticatedUser to request.state."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if request.method == "OPTIONS" or _is_public_path(path) or not _is_protected_path(path):
            request.state.user = None
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if authorization is None:
            return _auth_error(request, StatusCode.AUTH_TOKEN_MISSING)

        try:
            scheme, token = authorization.split(" ", 1)
        except ValueError:
            return _auth_error(request, StatusCode.AUTH_TOKEN_MALFORMED)
        if scheme.lower() != "bearer" or not token.strip():
            return _auth_error(request, StatusCode.AUTH_TOKEN_MALFORMED)

        try:
            claims = decode_access_token(token.strip())
        except jwt.ExpiredSignatureError:
            return _auth_error(request, StatusCode.AUTH_TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            return _auth_error(request, StatusCode.AUTH_TOKEN_INVALID)

        jti = _claim_str(claims, "jti")
        if not jti:
            return _auth_error(request, StatusCode.AUTH_TOKEN_INVALID)
        cache = _cache(request)
        if await cache.get(f"jwt_blacklist:{jti}") is not None:
            return _auth_error(request, StatusCode.AUTH_TOKEN_BLACKLISTED)

        user = _user_from_claims(claims, token.strip())
        if user is None:
            return _auth_error(request, StatusCode.AUTH_TOKEN_INVALID)
        request.state.user = user
        return await call_next(request)


async def get_current_user(request: Request) -> AuthenticatedUser:
    """FastAPI dependency returning the middleware-attached user."""
    user = getattr(request.state, "user", None)
    if not isinstance(user, AuthenticatedUser):
        raise CryptoAPIException(StatusCode.AUTH_TOKEN_MISSING)
    return user


def _is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES)


def _is_protected_path(path: str) -> bool:
    return path in PROTECTED_PREFIXES or path.startswith(PROTECTED_PREFIXES)


def _auth_error(request: Request, code: StatusCode) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000")
    body = APIResponse(
        code=code,
        message=DEFAULT_MESSAGES[code],
        data=None,
        trace_id=trace_id,
    ).model_dump(mode="json")
    return JSONResponse(status_code=HTTP_FOR_STATUS[code], content=body)


def _cache(request: Request) -> CacheBackend:
    cache = getattr(request.app.state, "cache", None)
    if cache is None:
        raise RuntimeError("cache backend is not initialized")
    return cache


def _claim_str(claims: dict[str, Any], key: str) -> str | None:
    value = claims.get(key)
    return str(value) if value is not None else None


def _user_from_claims(claims: dict[str, Any], token: str) -> AuthenticatedUser | None:
    subject = _claim_str(claims, "sub")
    username = _claim_str(claims, "username")
    role = _claim_str(claims, "role") or "user"
    jti = _claim_str(claims, "jti")
    exp = claims.get("exp")
    if subject is None or username is None or jti is None or exp is None:
        return None
    try:
        user_id = int(subject)
        expires_at = datetime.fromtimestamp(int(exp), tz=UTC)
    except (TypeError, ValueError, OSError):
        return None
    return AuthenticatedUser(
        id=user_id,
        username=username,
        role=role,
        jti=jti,
        token=token,
        expires_at=expires_at,
    )
