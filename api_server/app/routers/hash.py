"""Hash, HMAC, and PBKDF2 endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.hash import (
    HashRequest,
    HashResult,
    HmacRequest,
    Pbkdf2Request,
)

router = APIRouter()

ALGO = Path(..., regex="^(sha1|sha224|sha256|sha384|sha512|sha3_256|sha3_512|ripemd160)$")
HMAC_ALGO = Path(..., regex="^(sha1|sha256)$")


@router.post("/{algo}", response_model=APIResponse[HashResult])
async def hash_(
    algo: str = ALGO,
    _req: HashRequest | None = None,
    _user: User = Depends(get_current_user),
) -> APIResponse[HashResult]:
    """Compute a one-shot hash of the input bytes."""
    raise NotImplementedError("services.hash_service.hash(algo, req)")


@router.post("/hmac/{algo}", response_model=APIResponse[HashResult])
async def hmac(
    algo: str = HMAC_ALGO,
    _req: HmacRequest | None = None,
    _user: User = Depends(get_current_user),
) -> APIResponse[HashResult]:
    """HMAC under the chosen inner hash."""
    raise NotImplementedError("services.hash_service.hmac(algo, req, user)")


@router.post("/pbkdf2", response_model=APIResponse[HashResult])
async def pbkdf2(
    _req: Pbkdf2Request,
    _user: User = Depends(get_current_user),
) -> APIResponse[HashResult]:
    """Password-based key derivation. Iterations < 100k are rejected."""
    raise NotImplementedError("services.hash_service.pbkdf2(req)")
