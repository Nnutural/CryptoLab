"""Symmetric encryption endpoints — AES / SM4 / RC6."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.symmetric import (
    SymmetricDecryptRequest,
    SymmetricEncryptRequest,
    SymmetricResult,
)

router = APIRouter()

ALGO = Path(..., regex="^(aes|sm4|rc6)$", description="Algorithm name")


@router.post("/{algo}/encrypt", response_model=APIResponse[SymmetricResult])
async def encrypt(
    algo: str = ALGO,
    _req: SymmetricEncryptRequest | None = None,
    _user: User = Depends(get_current_user),
) -> APIResponse[SymmetricResult]:
    """Encrypt plaintext with the chosen algorithm + mode + padding."""
    raise NotImplementedError(
        "services.symmetric_service.encrypt(algo, req, user) "
        "→ wraps cryptolab_core.{aes,sm4,rc6}_encrypt"
    )


@router.post("/{algo}/decrypt", response_model=APIResponse[SymmetricResult])
async def decrypt(
    algo: str = ALGO,
    _req: SymmetricDecryptRequest | None = None,
    _user: User = Depends(get_current_user),
) -> APIResponse[SymmetricResult]:
    """Decrypt ciphertext."""
    raise NotImplementedError("services.symmetric_service.decrypt(algo, req, user)")
