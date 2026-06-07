"""Vulnerability demonstration endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas import demos as demos_schema
from app.services import demos_service

router = APIRouter()


@router.post("/ecb_image_leak")
async def ecb_image_leak(
    req: demos_schema.EcbImageLeakRequest,
    _access: None = Depends(demos_service.demo_access_dependency),
) -> object:
    """Encrypt an image with AES-ECB so the pattern remains visible."""
    return demos_service.ok(await demos_service.EcbImageLeakService(req))


@router.post("/ecdsa_k_reuse")
async def ecdsa_k_reuse(
    req: demos_schema.EcdsaKReuseRequest,
    _access: None = Depends(demos_service.demo_access_dependency),
) -> object:
    """Two ECDSA signatures with the same k recover the private key."""
    return demos_service.ok(await demos_service.EcdsaKReuseService(req))


@router.post("/rsa_low_exponent")
async def rsa_low_exponent(
    req: demos_schema.RsaLowExponentRequest,
    _access: None = Depends(demos_service.demo_access_dependency),
) -> object:
    """Raw RSA with e=3 lets a short message be recovered by cube root."""
    return demos_service.ok(await demos_service.RsaLowExponentService(req))


@router.post("/pbkdf2_iteration_impact")
async def pbkdf2_iteration_impact(
    req: demos_schema.Pbkdf2IterationImpactRequest,
    _access: None = Depends(demos_service.demo_access_dependency),
) -> object:
    """Time PBKDF2 at several iteration counts."""
    return demos_service.ok(await demos_service.Pbkdf2IterationImpactService(req))
