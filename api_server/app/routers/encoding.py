"""Base64 / UTF-8 encoding endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Path

from app.schemas.common import APIResponse
from app.schemas.encoding import EncodingRequest, EncodingResult

router = APIRouter()

OP = Path(..., regex="^(encode|decode)$")


@router.post("/base64/{op}", response_model=APIResponse[EncodingResult])
async def base64(op: str = OP, _req: EncodingRequest | None = None) -> APIResponse[EncodingResult]:
    """Base64 encode / decode."""
    raise NotImplementedError("services.encoding_service.base64(op, req)")


@router.post("/utf8/{op}", response_model=APIResponse[EncodingResult])
async def utf8(op: str = OP, _req: EncodingRequest | None = None) -> APIResponse[EncodingResult]:
    """UTF-8 encode (str → bytes) / decode (bytes → str)."""
    raise NotImplementedError("services.encoding_service.utf8(op, req)")
