"""Redis-compatible fixed-window rate limiter."""

from __future__ import annotations

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.cache import CacheBackend
from app.core.config import get_settings
from app.core.status_codes import DEFAULT_MESSAGES, HTTP_FOR_STATUS, StatusCode
from app.schemas.common import APIResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests once the per-IP per-prefix budget is exhausted."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if request.method == "OPTIONS" or not path.startswith("/api/v1/"):
            return await call_next(request)

        settings = get_settings()
        limit = (
            settings.login_rate_limit_per_minute
            if path == "/api/v1/auth/login"
            else settings.rate_limit_per_minute
        )
        cache_key = f"rate_limit:{_client_ip(request)}:{_path_prefix(path)}"
        count, ttl = await _cache(request).incr_with_ttl(
            cache_key,
            settings.rate_limit_window_seconds,
        )
        if count > limit:
            retry_after = str(max(1, ttl))
            trace_id = getattr(
                request.state,
                "trace_id",
                "00000000-0000-0000-0000-000000000000",
            )
            body = APIResponse(
                code=StatusCode.RATE_LIMIT_EXCEEDED,
                message=DEFAULT_MESSAGES[StatusCode.RATE_LIMIT_EXCEEDED],
                data={"retry_after": int(retry_after)},
                trace_id=trace_id,
            ).model_dump(mode="json")
            return JSONResponse(
                status_code=HTTP_FOR_STATUS[StatusCode.RATE_LIMIT_EXCEEDED],
                content=body,
                headers={"Retry-After": retry_after},
            )
        return await call_next(request)


def _cache(request: Request) -> CacheBackend:
    cache = getattr(request.app.state, "cache", None)
    if cache is None:
        raise RuntimeError("cache backend is not initialized")
    return cache


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client is not None else "unknown"


def _path_prefix(path: str) -> str:
    if path == "/api/v1/auth/login":
        return path
    parts = path.strip("/").split("/")
    if len(parts) >= 4:
        return "/" + "/".join(parts[:4])
    return path
