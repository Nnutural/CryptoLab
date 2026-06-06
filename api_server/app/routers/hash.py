"""Hash, HMAC, and PBKDF2 endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Path, Request

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.schemas.common import APIResponse
from app.schemas.hash import (
    HashRequest,
    HashResponse,
    HmacRequest,
    HmacResponse,
    Pbkdf2Request,
    Pbkdf2Response,
)
from app.services import hash_service

router = APIRouter()

ALGO = Path(..., pattern="^(sha1|sha224|sha256|sha384|sha512|sha3_256|sha3_512|ripemd160)$")
HMAC_ALGO = Path(..., pattern="^(sha1|sha256)$")


@router.post("/hmac/{algo}", response_model=APIResponse[HmacResponse])
async def hmac(
    request: Request,
    req: HmacRequest,
    algo: str = HMAC_ALGO,
) -> APIResponse[HmacResponse]:
    """HMAC under the chosen inner hash."""
    result = await hash_service.hmac(algo, req)
    return _ok(request, result)


@router.post("/pbkdf2", response_model=APIResponse[Pbkdf2Response])
async def pbkdf2(
    request: Request,
    req: Pbkdf2Request,
) -> APIResponse[Pbkdf2Response]:
    """Password-based key derivation with PBKDF2-HMAC-SHA256."""
    result = await hash_service.pbkdf2(req)
    return _ok(request, result)


@router.post("/{algo}", response_model=APIResponse[HashResponse])
async def hash_(
    request: Request,
    req: HashRequest,
    algo: str = ALGO,
) -> APIResponse[HashResponse]:
    """Compute a one-shot hash of the input bytes."""
    result = await hash_service.hash_(algo, req)
    return _ok(request, result)


def _ok(request: Request, data: HashResponse | HmacResponse | Pbkdf2Response) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
