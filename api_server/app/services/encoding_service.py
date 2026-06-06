"""Bridge for Base64 / UTF-8 encoding."""

from __future__ import annotations

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import StatusCode
from app.schemas.encoding import DecodeRequest, DecodeResponse, EncodeRequest, EncodeResponse


async def base64_encode(req: EncodeRequest) -> EncodeResponse:
    """Encode a UTF-8 string through the Rust Base64 implementation."""
    try:
        import cryptolab_core

        encoded = cryptolab_core.base64_encode(req.data.encode("utf-8"))
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EncodeResponse(encoded=encoded)


async def base64_decode(req: DecodeRequest) -> DecodeResponse:
    """Decode Base64 through Rust and return the raw bytes as Base64 text."""
    try:
        import cryptolab_core

        decoded = cryptolab_core.base64_decode(req.encoded)
        data = cryptolab_core.base64_encode(decoded)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return DecodeResponse(data=data)


async def utf8(_op: str, _req: object) -> object:
    raise NotImplementedError("cryptolab_core.utf8_{encode,decode}")
