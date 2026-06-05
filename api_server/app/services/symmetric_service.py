"""Bridge from API DTOs to the Rust symmetric primitives."""

from __future__ import annotations

from app.models.user import User
from app.schemas.symmetric import (
    SymmetricDecryptRequest,
    SymmetricEncryptRequest,
    SymmetricResult,
)


async def encrypt(_algo: str, _req: SymmetricEncryptRequest, _user: User) -> SymmetricResult:
    raise NotImplementedError(
        "decode b64 fields → dispatch to cryptolab_core.{aes,sm4,rc6}_encrypt "
        "→ time it → emit audit log → return SymmetricResult"
    )


async def decrypt(_algo: str, _req: SymmetricDecryptRequest, _user: User) -> SymmetricResult:
    raise NotImplementedError("inverse of encrypt; on AuthenticationFailed → DECRYPT_FAILED")
