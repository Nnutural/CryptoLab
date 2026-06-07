"""Bridge from API DTOs to the Rust symmetric primitives."""

from __future__ import annotations

import base64
import time
from collections.abc import Callable

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import StatusCode
from app.schemas.symmetric import (
    SymmetricDecryptRequest,
    SymmetricDecryptResponse,
    SymmetricEncryptRequest,
    SymmetricEncryptResponse,
)


async def encrypt(algo: str, req: SymmetricEncryptRequest) -> SymmetricEncryptResponse:
    """Encrypt by dispatching to cryptolab_core through the selected algorithm."""
    if req.algorithm != algo:
        raise CryptoAPIException(
            StatusCode.ALGORITHM_UNSUPPORTED,
            "Request algorithm must match the URL path",
        )

    try:
        import cryptolab_core

        functions: dict[str, Callable[..., bytes]] = {
            "aes": cryptolab_core.aes_encrypt,
            "sm4": cryptolab_core.sm4_encrypt,
            "rc6": cryptolab_core.rc6_encrypt,
        }
        start = time.perf_counter()
        ciphertext = functions[algo](
            req.plaintext_bytes(),
            req.key_bytes(),
            req.mode,
            req.iv_bytes(),
            req.aad_bytes(),
            req.padding,
        )
        duration_ms = (time.perf_counter() - start) * 1000
    except KeyError as exc:
        raise CryptoAPIException(StatusCode.ALGORITHM_UNSUPPORTED) from exc
    except ValueError as exc:
        raise CryptoAPIException(_status_for_encrypt_error(str(exc)), str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    return SymmetricEncryptResponse(
        ciphertext_b64=base64.b64encode(ciphertext).decode("ascii"),
        algorithm=algo,
        mode=req.mode,
        duration_ms=duration_ms,
    )


async def decrypt(algo: str, req: SymmetricDecryptRequest) -> SymmetricDecryptResponse:
    """Decrypt by dispatching to cryptolab_core through the selected algorithm."""
    if req.algorithm != algo:
        raise CryptoAPIException(
            StatusCode.ALGORITHM_UNSUPPORTED,
            "Request algorithm must match the URL path",
        )

    try:
        import cryptolab_core

        functions: dict[str, Callable[..., bytes]] = {
            "aes": cryptolab_core.aes_decrypt,
            "sm4": cryptolab_core.sm4_decrypt,
            "rc6": cryptolab_core.rc6_decrypt,
        }
        start = time.perf_counter()
        plaintext = functions[algo](
            req.ciphertext_bytes(),
            req.key_bytes(),
            req.mode,
            req.iv_bytes(),
            req.aad_bytes(),
            req.padding,
        )
        duration_ms = (time.perf_counter() - start) * 1000
    except KeyError as exc:
        raise CryptoAPIException(StatusCode.ALGORITHM_UNSUPPORTED) from exc
    except ValueError as exc:
        raise CryptoAPIException(_status_for_decrypt_error(str(exc)), str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    return SymmetricDecryptResponse(
        plaintext_b64=base64.b64encode(plaintext).decode("ascii"),
        algorithm=algo,
        mode=req.mode,
        duration_ms=duration_ms,
    )


def _status_for_encrypt_error(message: str) -> StatusCode:
    lowered = message.lower()
    if "key length" in lowered:
        return StatusCode.KEY_LENGTH_INVALID
    if "padding" in lowered:
        return StatusCode.PADDING_INVALID
    if "unsupported" in lowered:
        return StatusCode.ALGORITHM_UNSUPPORTED
    if "iv length" in lowered or "invalid parameter" in lowered:
        return StatusCode.PARAM_MISSING
    return StatusCode.ENCRYPT_FAILED


def _status_for_decrypt_error(message: str) -> StatusCode:
    lowered = message.lower()
    if "authentication failed" in lowered or "invalid padding" in lowered:
        return StatusCode.DECRYPT_FAILED
    if "key length" in lowered:
        return StatusCode.KEY_LENGTH_INVALID
    if "padding" in lowered:
        return StatusCode.PADDING_INVALID
    if "unsupported" in lowered:
        return StatusCode.ALGORITHM_UNSUPPORTED
    if "iv length" in lowered or "invalid input length" in lowered or "invalid parameter" in lowered:
        return StatusCode.PARAM_MISSING
    return StatusCode.DECRYPT_FAILED
