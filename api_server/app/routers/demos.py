"""Vulnerability demonstration endpoints.

Each demo is deliberately INSECURE — exposes a well-known flaw so it can be
shown live in the assignment report. The front-end gates each demo behind a
red "教学演示，请勿在生产中使用" banner.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
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

router = APIRouter()


@router.post("/ecb_image_leak", response_model=APIResponse[EcbImageLeakResult])
async def ecb_image_leak(
    _req: EcbImageLeakRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[EcbImageLeakResult]:
    """Encrypt an image with AES-ECB so the pattern remains visible."""
    raise NotImplementedError("services.demo_service.ecb_image_leak(req)")


@router.post("/ecdsa_k_reuse", response_model=APIResponse[EcdsaKReuseResult])
async def ecdsa_k_reuse(
    _req: EcdsaKReuseRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[EcdsaKReuseResult]:
    """Two ECDSA signatures with the same k → recover d."""
    raise NotImplementedError("services.demo_service.ecdsa_k_reuse(req)")


@router.post("/rsa_low_exponent", response_model=APIResponse[RsaLowExponentResult])
async def rsa_low_exponent(
    _req: RsaLowExponentRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[RsaLowExponentResult]:
    """e=3 + short message → cube root attack recovers plaintext."""
    raise NotImplementedError("services.demo_service.rsa_low_exponent(req)")


@router.post("/pbkdf2_iteration_impact", response_model=APIResponse[Pbkdf2ImpactResult])
async def pbkdf2_impact(
    _req: Pbkdf2ImpactRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[Pbkdf2ImpactResult]:
    """Time PBKDF2 for 1k / 10k / 100k / 1M iterations and show the impact curve."""
    raise NotImplementedError("services.demo_service.pbkdf2_impact(req)")
