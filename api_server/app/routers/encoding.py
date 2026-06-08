"""Base64 / UTF-8 encoding endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Path, Request

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.schemas.common import APIResponse
from app.schemas.encoding import DecodeRequest, DecodeResponse, EncodeRequest, EncodeResponse
from app.services import encoding_service

router = APIRouter()

OP = Path(..., pattern="^(encode|decode)$")


@router.post("/base64/{op}", response_model=APIResponse[EncodeResponse | DecodeResponse])
async def base64(
    request: Request,
    op: str = OP,
    req: EncodeRequest | DecodeRequest | None = None,
) -> APIResponse[EncodeResponse | DecodeResponse]:
    """Base64 encode / decode."""
    if op == "encode":
        if not isinstance(req, EncodeRequest):
            raise CryptoAPIException(StatusCode.PARAM_MISSING, "EncodeRequest.data is required")
        result = await encoding_service.base64_encode(req)
    else:
        if not isinstance(req, DecodeRequest):
            raise CryptoAPIException(StatusCode.PARAM_MISSING, "DecodeRequest.encoded is required")
        result = await encoding_service.base64_decode(req)

    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=result,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )


@router.post("/utf8/{op}", response_model=APIResponse[EncodeResponse | DecodeResponse])
async def utf8(
    request: Request,
    op: str = OP,
    req: EncodeRequest | DecodeRequest | None = None,
) -> APIResponse[EncodeResponse | DecodeResponse]:
    """UTF-8 encode (str → bytes) / decode (bytes → str)."""
    if op == "encode":
        if not isinstance(req, EncodeRequest):
            raise CryptoAPIException(StatusCode.PARAM_MISSING, "EncodeRequest.data is required")
        result = await encoding_service.utf8_encode_op(req)
    else:
        if not isinstance(req, EncodeRequest | DecodeRequest):
            raise CryptoAPIException(
                StatusCode.PARAM_MISSING,
                "EncodeRequest.data or DecodeRequest.encoded is required",
            )
        result = await encoding_service.utf8_decode_op(req)

    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=result,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
