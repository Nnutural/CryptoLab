"""Service layer for the Phase E vulnerability demonstrations."""

from __future__ import annotations

import base64
import binascii
import hmac
import secrets
import time
from io import BytesIO
from typing import Any

from app.core.context import get_trace_id
from app.core.exceptions import CryptoAPIException
from app.core.logging import get_logger
from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.schemas.common import APIResponse
from app.schemas.demos import (
    EcbImageLeakRequest,
    EcbImageLeakResponse,
    EcdsaKReuseRequest,
    EcdsaKReuseResponse,
    Pbkdf2IterationImpactRequest,
    Pbkdf2IterationImpactResponse,
    RsaLowExponentRequest,
    RsaLowExponentResponse,
)

BANNER = "教学演示路径，刻意暴露不安全实现；生产环境严禁调用"  # noqa: RUF001
SECP160R1_N = int("0100000000000000000001f4c8f927aed3ca752257", 16)
SECP160R1_ORDER_LEN = (SECP160R1_N.bit_length() + 7) // 8

logger = get_logger(__name__)


def demo_access_dependency() -> None:
    """Marker dependency used by demo routers without touching ORM models."""
    return None


def ok(data: Any) -> APIResponse[Any]:
    """Wrap demo payloads without requiring router access to ORM or request state."""
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=get_trace_id(),
    )


async def EcbImageLeakService(req: EcbImageLeakRequest) -> EcbImageLeakResponse:
    """Encrypt RGB pixels under AES-ECB and AES-CBC for visual leakage comparison."""
    image_bytes = _b64decode(req.image_b64, "image_b64")
    key = _from_hex(req.key_hex, "key_hex")
    if len(key) != 16:
        raise CryptoAPIException(StatusCode.KEY_LENGTH_INVALID, "key_hex must be 16 bytes")

    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise CryptoAPIException(StatusCode.INTERNAL, "Pillow is not installed") from exc

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            original = image.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise CryptoAPIException(
            StatusCode.ENCODING_ERROR,
            "image_b64 is not a supported image",
        ) from exc

    raw = original.tobytes()
    padded = raw + (b"\x00" * ((16 - (len(raw) % 16)) % 16))

    try:
        import cryptolab_core

        logger.warning(
            "demo unsafe path start",
            demo="ecb_image_leak",
            width=original.width,
            height=original.height,
            raw_len=len(raw),
        )
        ecb_bytes = cryptolab_core.aes_encrypt(padded, key, "ECB", None, None, "None")
        cbc_bytes = cryptolab_core.aes_encrypt(padded, key, "CBC", b"\x00" * 16, None, "None")
        logger.warning(
            "demo unsafe path finish",
            demo="ecb_image_leak",
            block_count=len(ecb_bytes) // 16,
        )
    except ValueError as exc:
        raise CryptoAPIException(_status_for_encrypt_error(str(exc)), str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "AES demo encryption failed") from exc

    ecb_image = Image.frombytes("RGB", original.size, ecb_bytes[: len(raw)])
    cbc_image = Image.frombytes("RGB", original.size, cbc_bytes[: len(raw)])
    block_count, duplicate_ratio = _duplicate_block_ratio(ecb_bytes)

    return EcbImageLeakResponse(
        banner=BANNER,
        original_png_b64=_image_to_png_b64(original),
        ecb_encrypted_png_b64=_image_to_png_b64(ecb_image),
        cbc_encrypted_png_b64=_image_to_png_b64(cbc_image),
        block_count=block_count,
        duplicate_block_ratio=duplicate_ratio,
    )


async def EcdsaKReuseService(req: EcdsaKReuseRequest) -> EcdsaKReuseResponse:
    """Generate a keypair, reuse one ECDSA nonce, then recover the private key."""
    msg1 = req.message1.encode("utf-8")
    msg2 = req.message2.encode("utf-8")

    try:
        import cryptolab_core

        d, qx, qy = cryptolab_core.ecc_generate_keypair(req.curve)
        k_int = secrets.randbelow(SECP160R1_N - 1) + 1
        k = k_int.to_bytes(SECP160R1_ORDER_LEN, "big")
        h1 = _hash_to_secp160r1_scalar_bytes(cryptolab_core, msg1)
        h2 = _hash_to_secp160r1_scalar_bytes(cryptolab_core, msg2)

        logger.warning("demo unsafe path start", demo="ecdsa_k_reuse", curve=req.curve)
        r1, s1 = cryptolab_core.ecdsa_demo_sign_with_k(msg1, d, k, req.curve)
        r2, s2 = cryptolab_core.ecdsa_demo_sign_with_k(msg2, d, k, req.curve)
        r_equal = hmac.compare_digest(r1, r2)
        if not r_equal:
            raise CryptoAPIException(StatusCode.INTERNAL, "internal: k did not produce reused r")
        recovered_d = cryptolab_core.ecdsa_demo_recover_d_from_k_reuse(
            r1,
            s1,
            s2,
            h1,
            h2,
            req.curve,
        )
        recovery_matches = hmac.compare_digest(_left_pad(d, SECP160R1_ORDER_LEN), recovered_d)
        logger.warning(
            "demo unsafe path finish",
            demo="ecdsa_k_reuse",
            curve=req.curve,
            recovered=bool(recovery_matches),
        )
    except CryptoAPIException:
        raise
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "ECDSA k-reuse demo failed") from exc

    if not recovery_matches:
        raise CryptoAPIException(StatusCode.INTERNAL, "internal: recovered d did not match")

    return EcdsaKReuseResponse(
        banner=BANNER,
        private_key_hex=d.hex(),
        public_key={"qx_hex": qx.hex(), "qy_hex": qy.hex()},
        reused_k_hex=k.hex(),
        signature1={"r_hex": r1.hex(), "s_hex": s1.hex(), "h_hex": h1.hex()},
        signature2={"r_hex": r2.hex(), "s_hex": s2.hex(), "h_hex": h2.hex()},
        r_equal=bool(r_equal),
        recovered_d_hex=recovered_d.hex(),
        recovery_matches_original=bool(recovery_matches),
    )


async def RsaLowExponentService(req: RsaLowExponentRequest) -> RsaLowExponentResponse:
    """Demonstrate `e=3` raw RSA recovery by an integer cube root."""
    message_bytes = req.message.encode("utf-8")
    m_int = int.from_bytes(message_bytes, "big")

    try:
        import cryptolab_core

        last_error: Exception | None = None
        for _ in range(3):
            try:
                logger.warning(
                    "demo unsafe path start",
                    demo="rsa_low_exponent",
                    bits=req.bits,
                    e=3,
                )
                n, e, _d, _p, _q = cryptolab_core.rsa_demo_unsafe_keygen(req.bits, 3)
                break
            except ValueError as exc:
                last_error = exc
        else:
            raise CryptoAPIException(
                StatusCode.CRYPTO_LIB_ERROR,
                f"rsa_demo_unsafe_keygen failed after retries: {last_error}",
            )

        n_int = int.from_bytes(n, "big")
        cube_safe = m_int.bit_length() * 3 < n_int.bit_length()
        if not cube_safe:
            raise CryptoAPIException(StatusCode.PARAM_MISSING, "message_too_long_for_cube_attack")
        ciphertext = cryptolab_core.rsa_demo_unsafe_encrypt_raw(_int_to_be(m_int), n, e)
        recovered = cryptolab_core.rsa_demo_cube_root(ciphertext)
        logger.warning(
            "demo unsafe path finish",
            demo="rsa_low_exponent",
            n_bits=n_int.bit_length(),
            message_bits=m_int.bit_length(),
        )
    except CryptoAPIException:
        raise
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(
            StatusCode.CRYPTO_LIB_ERROR,
            "RSA low-exponent demo failed",
        ) from exc

    recovered_plaintext = _int_to_be(int.from_bytes(recovered, "big")).decode("utf-8")
    return RsaLowExponentResponse(
        banner=BANNER,
        n_hex=n.hex(),
        e=int.from_bytes(e, "big"),
        ciphertext_hex=ciphertext.hex(),
        message_bits=m_int.bit_length(),
        n_bits=n_int.bit_length(),
        cube_safe=cube_safe,
        recovered_plaintext=recovered_plaintext,
        recovery_matches_original=hmac.compare_digest(recovered_plaintext, req.message),
    )


async def Pbkdf2IterationImpactService(
    req: Pbkdf2IterationImpactRequest,
) -> Pbkdf2IterationImpactResponse:
    """Measure PBKDF2-HMAC-SHA256 duration across iteration counts."""
    salt = _from_hex(req.salt_hex, "salt_hex")
    measurements: list[dict[str, int | str | float]] = []
    durations: dict[int, float] = {}

    try:
        import cryptolab_core

        for iterations in req.iterations_list:
            logger.warning(
                "demo path start",
                demo="pbkdf2_iteration_impact",
                iterations=iterations,
            )
            start_ns = time.perf_counter_ns()
            derived = cryptolab_core.pbkdf2_hmac_sha256(
                req.password.encode("utf-8"),
                salt,
                iterations,
                req.key_len,
            )
            duration_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            logger.warning(
                "demo path finish",
                demo="pbkdf2_iteration_impact",
                iterations=iterations,
                duration_ms=duration_ms,
            )
            durations[iterations] = duration_ms
            measurements.append(
                {
                    "iterations": iterations,
                    "derived_key_hex": derived.hex(),
                    "duration_ms": duration_ms,
                }
            )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.PARAM_MISSING, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "PBKDF2 demo failed") from exc

    ratio = _duration_ratio(durations, req.iterations_list)
    return Pbkdf2IterationImpactResponse(
        banner=BANNER,
        measurements=measurements,
        ratio_1m_over_100k=ratio,
        verdict="PBKDF2 cost scales approximately linearly with the configured iteration count.",
    )


def _b64decode(value: str, field: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise CryptoAPIException(
            StatusCode.ENCODING_ERROR,
            f"{field} must be standard Base64",
        ) from exc


def _from_hex(value: str, field: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, f"{field} must be hex") from exc


def _duplicate_block_ratio(data: bytes) -> tuple[int, float]:
    blocks = [data[i : i + 16] for i in range(0, len(data), 16)]
    if not blocks:
        return 0, 0.0
    return len(blocks), (len(blocks) - len(set(blocks))) / len(blocks)


def _image_to_png_b64(image: Any) -> str:
    out = BytesIO()
    image.save(out, format="PNG")
    return base64.b64encode(out.getvalue()).decode("ascii")


def _hash_to_secp160r1_scalar_bytes(core: Any, message: bytes) -> bytes:
    digest = core.sha256_digest(message)
    value = int.from_bytes(digest, "big")
    shift = len(digest) * 8 - SECP160R1_N.bit_length()
    if shift > 0:
        value >>= shift
    return value.to_bytes(SECP160R1_ORDER_LEN, "big")


def _left_pad(value: bytes, length: int) -> bytes:
    if len(value) >= length:
        return value
    return (b"\x00" * (length - len(value))) + value


def _int_to_be(value: int) -> bytes:
    if value == 0:
        return b"\x00"
    return value.to_bytes((value.bit_length() + 7) // 8, "big")


def _duration_ratio(durations: dict[int, float], iterations_list: list[int]) -> float:
    if 1_000_000 in durations and 100_000 in durations:
        return durations[1_000_000] / max(durations[100_000], 1e-9)
    if len(iterations_list) >= 2:
        return durations[iterations_list[-1]] / max(durations[iterations_list[-2]], 1e-9)
    return 1.0


def _status_for_encrypt_error(message: str) -> StatusCode:
    lowered = message.lower()
    if "key length" in lowered:
        return StatusCode.KEY_LENGTH_INVALID
    if "unsupported" in lowered:
        return StatusCode.ALGORITHM_UNSUPPORTED
    if "iv length" in lowered or "invalid parameter" in lowered:
        return StatusCode.PARAM_MISSING
    return StatusCode.ENCRYPT_FAILED
