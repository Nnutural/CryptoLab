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


async def utf8_encode_op(req: EncodeRequest) -> EncodeResponse:
    """Validate and re-encode a UTF-8 string through Rust, returning Base64 bytes."""
    try:
        import cryptolab_core

        raw = cryptolab_core.utf8_encode(req.data.encode("utf-8"))
        encoded = cryptolab_core.base64_encode(raw)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EncodeResponse(encoded=encoded)


async def utf8_decode_op(req: EncodeRequest | DecodeRequest) -> DecodeResponse:
    """Decode Base64-wrapped bytes after strict Rust UTF-8 validation."""
    encoded = req.data if isinstance(req, EncodeRequest) else req.encoded
    try:
        import cryptolab_core

        raw = cryptolab_core.base64_decode(encoded)
        decoded = cryptolab_core.utf8_decode(raw)
        data = decoded.decode("utf-8")
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return DecodeResponse(data=data)
