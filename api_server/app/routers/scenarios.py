"""Composite application scenario endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.schemas.common import APIResponse
from app.schemas.scenarios import (
    SecureReceiveRequest,
    SecureReceiveResponse,
    SecureSendRequest,
    SecureSendResponse,
)
from app.services import scenario_service

router = APIRouter()


@router.post("/secure_file_transfer/send", response_model=APIResponse[SecureSendResponse])
async def secure_file_transfer_send(
    request: Request,
    req: SecureSendRequest,
) -> APIResponse[SecureSendResponse]:
    """Build a secure file-transfer envelope."""
    return _ok(request, await scenario_service.secure_file_send(req))


@router.post("/secure_file_transfer/receive", response_model=APIResponse[SecureReceiveResponse])
async def secure_file_transfer_receive(
    request: Request,
    req: SecureReceiveRequest,
) -> APIResponse[SecureReceiveResponse]:
    """Decrypt and verify a secure file-transfer envelope."""
    return _ok(request, await scenario_service.secure_file_receive(req))


def _ok(
    request: Request,
    data: SecureSendResponse | SecureReceiveResponse,
) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
