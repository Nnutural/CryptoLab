"""Symmetric encryption endpoints: AES / SM4 / RC6."""

from __future__ import annotations

from fastapi import APIRouter, Path, Request

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.schemas.common import APIResponse
from app.schemas.symmetric import (
    SymmetricDecryptRequest,
    SymmetricDecryptResponse,
    SymmetricEncryptRequest,
    SymmetricEncryptResponse,
)
from app.services import symmetric_service

router = APIRouter()

ALGO = Path(..., pattern="^(aes|sm4|rc6)$", description="Algorithm name")


@router.post("/{algo}/encrypt", response_model=APIResponse[SymmetricEncryptResponse])
async def encrypt(
    request: Request,
    req: SymmetricEncryptRequest,
    algo: str = ALGO,
) -> APIResponse[SymmetricEncryptResponse]:
    """Encrypt plaintext with the chosen algorithm + mode + padding."""
    result = await symmetric_service.encrypt(algo, req)
    return _ok(request, result)


@router.post("/{algo}/decrypt", response_model=APIResponse[SymmetricDecryptResponse])
async def decrypt(
    request: Request,
    req: SymmetricDecryptRequest,
    algo: str = ALGO,
) -> APIResponse[SymmetricDecryptResponse]:
    """Decrypt ciphertext."""
    result = await symmetric_service.decrypt(algo, req)
    return _ok(request, result)


def _ok(
    request: Request,
    data: SymmetricEncryptResponse | SymmetricDecryptResponse,
) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
