"""JWT authentication middleware + `get_current_user` dependency."""

from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.models.user import User  # noqa: F401  (used by dependency below)


# Paths that bypass JWT entirely.
PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/healthz",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Verify `Authorization: Bearer <jwt>` and attach `request.state.user`.

    Public paths in `PUBLIC_PATHS` are skipped. Anything else without a valid
    token short-circuits with 4001 UNAUTHENTICATED.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        raise NotImplementedError(
            "skip PUBLIC_PATHS → parse Bearer token → decode_access_token "
            "→ load user from DB → set request.state.user → call_next"
        )


async def get_current_user(_request: Request) -> User:
    """FastAPI dependency: returns the user previously attached by middleware."""
    raise NotImplementedError("return request.state.user, else raise UNAUTHENTICATED")
