"""Inject / propagate a UUID trace-id on every request."""

from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Honor an incoming `X-Trace-Id` header, or mint a fresh one.

    Stashes the value on `request.state.trace_id` for downstream middleware
    and the exception handlers to read.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        raise NotImplementedError(
            "read X-Trace-Id header → fallback uuid4 → bind to request.state.trace_id "
            "and structlog contextvars → call_next → echo header on response"
        )
