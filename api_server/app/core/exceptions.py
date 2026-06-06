"""Unified exception type + FastAPI handlers.

Services / routers raise [`CryptoAPIException`]; the global handler converts
it into a uniform `APIResponse` JSON body — never let a raw stack trace leak
to clients.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.status_codes import DEFAULT_MESSAGES, HTTP_FOR_STATUS, StatusCode
from app.schemas.common import APIResponse


class CryptoAPIException(Exception):
    """Single business exception type. Services raise this; handlers serialize."""

    def __init__(
        self,
        code: StatusCode | int,
        message: str | None = None,
        *,
        data: dict[str, Any] | None = None,
    ) -> None:
        self.code = int(code)
        self.message = message or DEFAULT_MESSAGES.get(self.code, "Error")
        self.data = data
        super().__init__(self.message)


def install_exception_handlers(app: FastAPI) -> None:
    """Wire the handlers into a FastAPI app."""

    @app.exception_handler(CryptoAPIException)
    async def handle_crypto(request: Request, exc: CryptoAPIException) -> JSONResponse:
        return _envelope(request, exc.code, exc.message, exc.data)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _envelope(
            request,
            StatusCode.PARAM_MISSING,
            "Request validation failed",
            data={"errors": exc.errors()},
            http_status=422,
        )

    @app.exception_handler(Exception)
    async def handle_unknown(request: Request, exc: Exception) -> JSONResponse:
        # Never echo `str(exc)` to the client — it may leak DB / file paths.
        # The real error is logged structurally by the audit middleware.
        return _envelope(request, StatusCode.INTERNAL, DEFAULT_MESSAGES[StatusCode.INTERNAL])


def _envelope(
    request: Request,
    code: int,
    message: str,
    data: dict[str, Any] | None = None,
    http_status: int | None = None,
) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None) or "00000000-0000-0000-0000-000000000000"
    body = APIResponse(code=code, message=message, data=data, trace_id=trace_id).model_dump(
        mode="json"
    )
    return JSONResponse(status_code=http_status or HTTP_FOR_STATUS.get(code, 500), content=body)
