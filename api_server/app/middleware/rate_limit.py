"""Redis-backed sliding-window rate limiter.

Counter key:  `rate_limit:{ip}:{path}`
Window:       60 seconds (configurable)
Algorithm:    INCR + EXPIRE atomically via Lua / pipeline.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject once the per-IP per-path budget is exhausted."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        raise NotImplementedError(
            "key = f'rate_limit:{ip}:{path}' → INCR + EXPIRE 60 → "
            "if > settings.rate_limit_per_minute raise CryptoAPIException(RATE_LIMITED)"
        )
