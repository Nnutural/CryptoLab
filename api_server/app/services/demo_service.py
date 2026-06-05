"""Implementations of the four vulnerability-demo endpoints."""

from __future__ import annotations

from app.schemas.demos import (
    EcbImageLeakRequest,
    EcbImageLeakResult,
    EcdsaKReuseRequest,
    EcdsaKReuseResult,
    Pbkdf2ImpactRequest,
    Pbkdf2ImpactResult,
    RsaLowExponentRequest,
    RsaLowExponentResult,
)


async def ecb_image_leak(_req: EcbImageLeakRequest) -> EcbImageLeakResult:
    raise NotImplementedError(
        "decode image → encrypt raw pixel bytes with AES-128-ECB "
        "→ re-wrap pixels into a PNG/BMP showing the leak"
    )


async def ecdsa_k_reuse(_req: EcdsaKReuseRequest) -> EcdsaKReuseResult:
    raise NotImplementedError(
        "sign m1 and m2 with the same k → k = (e1 - e2)/(s1 - s2) → d = (s1·k - e1)/r"
    )


async def rsa_low_exponent(_req: RsaLowExponentRequest) -> RsaLowExponentResult:
    raise NotImplementedError(
        "use e=3 unpadded → ciphertext = m^3 → integer cube root recovers m"
    )


async def pbkdf2_impact(_req: Pbkdf2ImpactRequest) -> Pbkdf2ImpactResult:
    raise NotImplementedError(
        "loop over [1_000, 10_000, 100_000, 1_000_000] iterations, time each "
        "→ return mapping for the front-end chart"
    )
