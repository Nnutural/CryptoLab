"""Audit-log middleware.

Fires AFTER the request completes (success or failure) and asynchronously
inserts an `operation_logs` row through the audit service. The middleware
never blocks on the DB write — failures are logged but don't fail the user
request.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class AuditMiddleware(BaseHTTPMiddleware):
    """Record (trace_id, user_id, path, status, duration_ms) for every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        raise NotImplementedError(
            "start = perf_counter; resp = await call_next; "
            "asyncio.create_task(audit_service.log(...)) "
            "with redacted payload; return resp"
        )
