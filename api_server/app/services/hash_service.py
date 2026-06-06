"""Bridge for hash / HMAC / PBKDF2 to the Rust core."""

from __future__ import annotations

from collections.abc import Callable

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import StatusCode
from app.schemas.hash import (
    HashRequest,
    HashResponse,
    HmacRequest,
    HmacResponse,
    Pbkdf2Request,
    Pbkdf2Response,
)


async def hash_(algo: str, req: HashRequest) -> HashResponse:
    """Compute a hash digest by dispatching to the Rust FFI layer."""
    try:
        import cryptolab_core

        functions: dict[str, Callable[[bytes], bytes]] = {
            "sha1": cryptolab_core.sha1_digest,
            "sha224": cryptolab_core.sha224_digest,
            "sha256": cryptolab_core.sha256_digest,
            "sha384": cryptolab_core.sha384_digest,
            "sha512": cryptolab_core.sha512_digest,
            "sha3_256": cryptolab_core.sha3_256_digest,
            "sha3_512": cryptolab_core.sha3_512_digest,
            "ripemd160": cryptolab_core.ripemd160_digest,
        }
        digest = functions[algo](req.data.encode("utf-8"))
    except KeyError as exc:
        raise CryptoAPIException(StatusCode.ALGORITHM_UNSUPPORTED) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    return HashResponse(digest_hex=digest.hex(), algorithm=algo)


async def hmac(algo: str, req: HmacRequest) -> HmacResponse:
    """Compute HMAC through the Rust FFI layer."""
    if req.algorithm != algo:
        raise CryptoAPIException(
            StatusCode.ALGORITHM_UNSUPPORTED,
            "HMAC request algorithm must match the URL path",
        )

    try:
        import cryptolab_core

        key = req.key.encode("utf-8")
        message = req.message.encode("utf-8")
        if algo == "sha1":
            mac = cryptolab_core.hmac_sha1(key, message)
        elif algo == "sha256":
            mac = cryptolab_core.hmac_sha256(key, message)
        else:
            raise CryptoAPIException(StatusCode.ALGORITHM_UNSUPPORTED)
    except CryptoAPIException:
        raise
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    return HmacResponse(mac_hex=mac.hex(), algorithm=algo)


async def pbkdf2(req: Pbkdf2Request) -> Pbkdf2Response:
    """Derive a key with PBKDF2-HMAC-SHA256 through the Rust FFI layer."""
    try:
        import cryptolab_core

        derived = cryptolab_core.pbkdf2_hmac_sha256(
            req.password.encode("utf-8"),
            req.salt.encode("utf-8"),
            req.iterations,
            req.key_len,
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.PARAM_MISSING, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    warning = None
    if req.iterations < 100_000:
        warning = "PBKDF2 iterations below 100000 are not recommended for production use"
    if len(req.salt.encode("utf-8")) < 8:
        salt_warning = "PBKDF2 salt shorter than 8 bytes is accepted only for test vectors"
        warning = f"{warning}; {salt_warning}" if warning else salt_warning

    return Pbkdf2Response(
        derived_key_hex=derived.hex(),
        iterations=req.iterations,
        warning=warning,
    )
