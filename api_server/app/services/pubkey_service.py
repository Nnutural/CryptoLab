"""Bridge for RSA / ECC / ECDSA, including KEK-wrapping of private material."""

from __future__ import annotations

from app.models.user import User
from app.schemas.pubkey import (
    EccKeygenRequest,
    EccKeyResult,
    EcdsaSignRequest,
    EcdsaSignResult,
    EcdsaVerifyRequest,
    EcdsaVerifyResult,
    RsaDecryptRequest,
    RsaEncryptRequest,
    RsaEncryptResult,
    RsaKeygenRequest,
    RsaKeyResult,
    RsaSignRequest,
    RsaSignResult,
    RsaVerifyRequest,
    RsaVerifyResult,
)


# ----- RSA -----

async def rsa_keygen(_req: RsaKeygenRequest, _user: User) -> RsaKeyResult:
    raise NotImplementedError(
        "cryptolab_core.rsa_keygen → wrap (d,p,q) with KEK via key_service.store"
    )


async def rsa_encrypt(_req: RsaEncryptRequest, _user: User) -> RsaEncryptResult:
    raise NotImplementedError("load (n,e) from key_service → core.rsa_encrypt")


async def rsa_decrypt(_req: RsaDecryptRequest, _user: User) -> RsaEncryptResult:
    raise NotImplementedError("load + unwrap (n,d) → core.rsa_decrypt")


async def rsa_sign(_req: RsaSignRequest, _user: User) -> RsaSignResult:
    raise NotImplementedError("load + unwrap (n,d) → core.rsa_sign")


async def rsa_verify(_req: RsaVerifyRequest, _user: User) -> RsaVerifyResult:
    raise NotImplementedError("load (n,e) → core.rsa_verify")


# ----- ECC / ECDSA -----

async def ecc_keygen(_req: EccKeygenRequest, _user: User) -> EccKeyResult:
    raise NotImplementedError("core.ecc_keygen → wrap d with KEK")


async def ecdsa_sign(_req: EcdsaSignRequest, _user: User) -> EcdsaSignResult:
    raise NotImplementedError("load + unwrap d → core.ecdsa_sign")


async def ecdsa_verify(_req: EcdsaVerifyRequest, _user: User) -> EcdsaVerifyResult:
    raise NotImplementedError("load (px,py) → core.ecdsa_verify")
