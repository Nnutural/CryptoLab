"""Bridge for Base64 / UTF-8 encoding."""

from __future__ import annotations

from app.schemas.encoding import EncodingRequest, EncodingResult


async def base64(_op: str, _req: EncodingRequest) -> EncodingResult:
    raise NotImplementedError("cryptolab_core.base64_{encode,decode}")


async def utf8(_op: str, _req: EncodingRequest) -> EncodingResult:
    raise NotImplementedError("cryptolab_core.utf8_{encode,decode}")
