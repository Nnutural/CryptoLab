"""Asynchronous audit-log middleware."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import AuthenticatedUser
from app.services.audit_service import AuditRecord, record_operation_log

AUDITED_PREFIXES: tuple[str, ...] = (
    "/api/v1/symmetric/",
    "/api/v1/pubkey/",
    "/api/v1/scenarios/",
)
_AUDIT_TASKS: set[asyncio.Task[None]] = set()


class AuditMiddleware(BaseHTTPMiddleware):
    """Record a privacy-preserving audit row after cryptographic requests."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started_ns = time.perf_counter_ns()
        request_body = await request.body()
        request._body = request_body

        response = await call_next(request)
        response_body = b"".join([chunk async for chunk in response.body_iterator])
        duration_ms = (time.perf_counter_ns() - started_ns) / 1_000_000
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.3f}"

        if _should_audit(request.url.path):
            user = getattr(request.state, "user", None)
            user_id = user.id if isinstance(user, AuthenticatedUser) else None
            payload = _json_body(request_body)
            operation = _operation_from_path(request.url.path)
            task = asyncio.create_task(
                record_operation_log(
                    AuditRecord(
                        trace_id=getattr(
                            request.state,
                            "trace_id",
                            "00000000-0000-0000-0000-000000000000",
                        ),
                        user_id=user_id,
                        operation=operation,
                        algorithm=_algorithm_from_path(request.url.path, payload),
                        key_id=None,
                        input_bytes=request_body,
                        output_bytes=response_body,
                        status_code=response.status_code,
                        duration_ms=duration_ms,
                        client_ip=_client_ip(request),
                        user_agent=request.headers.get("User-Agent"),
                    )
                )
            )
            _AUDIT_TASKS.add(task)
            task.add_done_callback(_AUDIT_TASKS.discard)

        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
            background=response.background,
        )


def _should_audit(path: str) -> bool:
    return path.startswith(AUDITED_PREFIXES)


def _json_body(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _operation_from_path(path: str) -> str:
    parts = path.strip("/").split("/")
    if len(parts) >= 5 and parts[2] in {"symmetric", "pubkey"}:
        return f"{parts[3]}_{parts[4]}"
    if "secure_file_transfer" in parts:
        return f"secure_file_transfer_{parts[-1]}"
    return parts[-1] if parts else "unknown"


def _algorithm_from_path(path: str, payload: dict[str, Any]) -> str | None:
    parts = path.strip("/").split("/")
    if len(parts) >= 5 and parts[2] == "symmetric":
        algo = parts[3].upper()
        mode = str(payload.get("mode", "")).upper()
        key_hex = str(payload.get("key_hex", ""))
        bits = len(key_hex) * 4 if key_hex else None
        return f"{algo}-{bits}-{mode}" if bits and mode else f"{algo}-{mode or 'unknown'}"
    if len(parts) >= 5 and parts[2] == "pubkey":
        family = parts[3]
        action = parts[4]
        if family == "rsa":
            if action == "keygen":
                return f"RSA-{payload.get('bits', 'unknown')}-keygen"
            if action in {"encrypt", "decrypt"}:
                return "RSA-OAEP"
            if action in {"sign", "verify"}:
                return "RSA-PSS"
        if family == "ecc":
            return f"ECC-{payload.get('curve', 'unknown')}"
        if family == "ecdsa":
            return f"ECDSA-{payload.get('curve', 'unknown')}"
    if path.startswith("/api/v1/scenarios/secure_file_transfer/"):
        return "RSA-OAEP-SHA256+AES-256-GCM+ECDSA-secp160r1-SHA256"
    return None


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client is not None else None
