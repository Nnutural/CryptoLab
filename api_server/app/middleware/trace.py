"""Inject / propagate a UUID trace-id on every request."""

from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import set_trace_id


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Honor an incoming `X-Trace-Id` header, or mint a fresh one.

    Stashes the value on `request.state.trace_id` for downstream middleware
    and the exception handlers to read.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("X-Trace-Id") or str(uuid4())
        request.state.trace_id = trace_id
        set_trace_id(trace_id)
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
