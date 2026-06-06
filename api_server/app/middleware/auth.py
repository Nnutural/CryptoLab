"""JWT authentication middleware + `get_current_user` dependency."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.status_codes import DEFAULT_MESSAGES, HTTP_FOR_STATUS, StatusCode
from app.models.user import User
from app.schemas.common import APIResponse

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

PHASE_PUBLIC_PREFIXES: tuple[str, ...] = (
    "/api/v1/encoding/",
    "/api/v1/hash/",
)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Verify `Authorization: Bearer <jwt>` and attach `request.state.user`.

    Public paths in `PUBLIC_PATHS` are skipped. Anything else without a valid
    token short-circuits with 4001 UNAUTHENTICATED.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith(PHASE_PUBLIC_PREFIXES):
            request.state.user = None
            return await call_next(request)

        trace_id = getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000")
        body = APIResponse(
            code=StatusCode.UNAUTHENTICATED,
            message=DEFAULT_MESSAGES[StatusCode.UNAUTHENTICATED],
            data=None,
            trace_id=trace_id,
        ).model_dump(mode="json")
        return JSONResponse(
            status_code=HTTP_FOR_STATUS[StatusCode.UNAUTHENTICATED],
            content=body,
        )


async def get_current_user(_request: Request) -> User:
    """FastAPI dependency: returns the user previously attached by middleware."""
    user = getattr(_request.state, "user", None)
    if user is None:
        raise RuntimeError("authenticated user missing from request state")
    return user
