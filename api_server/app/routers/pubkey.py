"""Public-key endpoints: RSA, ECC, ECDSA."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
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

router = APIRouter()


# ----- RSA -----

@router.post("/rsa/keygen", response_model=APIResponse[RsaKeyResult])
async def rsa_keygen(
    _req: RsaKeygenRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[RsaKeyResult]:
    raise NotImplementedError("services.pubkey_service.rsa_keygen(req, user)")


@router.post("/rsa/encrypt", response_model=APIResponse[RsaEncryptResult])
async def rsa_encrypt(
    _req: RsaEncryptRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[RsaEncryptResult]:
    raise NotImplementedError("services.pubkey_service.rsa_encrypt(req, user)")


@router.post("/rsa/decrypt", response_model=APIResponse[RsaEncryptResult])
async def rsa_decrypt(
    _req: RsaDecryptRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[RsaEncryptResult]:
    raise NotImplementedError("services.pubkey_service.rsa_decrypt(req, user)")


@router.post("/rsa/sign", response_model=APIResponse[RsaSignResult])
async def rsa_sign(
    _req: RsaSignRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[RsaSignResult]:
    raise NotImplementedError("services.pubkey_service.rsa_sign(req, user)")


@router.post("/rsa/verify", response_model=APIResponse[RsaVerifyResult])
async def rsa_verify(
    _req: RsaVerifyRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[RsaVerifyResult]:
    raise NotImplementedError("services.pubkey_service.rsa_verify(req, user)")


# ----- ECC / ECDSA -----

@router.post("/ecc/keygen", response_model=APIResponse[EccKeyResult])
async def ecc_keygen(
    _req: EccKeygenRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[EccKeyResult]:
    raise NotImplementedError("services.pubkey_service.ecc_keygen(req, user)")


@router.post("/ecdsa/sign", response_model=APIResponse[EcdsaSignResult])
async def ecdsa_sign(
    _req: EcdsaSignRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[EcdsaSignResult]:
    raise NotImplementedError("services.pubkey_service.ecdsa_sign(req, user)")


@router.post("/ecdsa/verify", response_model=APIResponse[EcdsaVerifyResult])
async def ecdsa_verify(
    _req: EcdsaVerifyRequest,
    _user: User = Depends(get_current_user),
) -> APIResponse[EcdsaVerifyResult]:
    raise NotImplementedError("services.pubkey_service.ecdsa_verify(req, user)")
