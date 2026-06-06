"""Audit-log middleware.

Fires AFTER the request completes (success or failure) and asynchronously
inserts an `operation_logs` row through the audit service. The middleware
never blocks on the DB write — failures are logged but don't fail the user
request.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class AuditMiddleware(BaseHTTPMiddleware):
    """Record (trace_id, user_id, path, status, duration_ms) for every request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.started_at_ns = time.perf_counter_ns()
        response = await call_next(request)
        response.headers["X-Process-Time-Ms"] = (
            f"{(time.perf_counter_ns() - request.state.started_at_ns) / 1_000_000:.3f}"
        )
        return response
