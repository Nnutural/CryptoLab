"""Public-key endpoints: RSA, ECC, ECDSA — key_id based."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.common import APIResponse
from app.schemas.pubkey import (
    EccKeygenRequest,
    EccKeygenResponse,
    EcdsaSignRequest,
    EcdsaSignResponse,
    EcdsaVerifyRequest,
    EcdsaVerifyResponse,
    RsaDecryptRequest,
    RsaDecryptResponse,
    RsaEncryptRequest,
    RsaEncryptResponse,
    RsaKeygenRequest,
    RsaKeygenResponse,
    RsaSignRequest,
    RsaSignResponse,
    RsaVerifyRequest,
    RsaVerifyResponse,
)
from app.services import pubkey_service

router = APIRouter()
USER_DEP = Depends(get_current_user)
DB_DEP = Depends(get_db)


@router.post("/rsa/keygen", response_model=APIResponse[RsaKeygenResponse])
async def rsa_keygen(
    request: Request,
    req: RsaKeygenRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[RsaKeygenResponse]:
    result = await pubkey_service.rsa_keygen(db, user, req)
    return _ok(request, result)


@router.post("/rsa/encrypt", response_model=APIResponse[RsaEncryptResponse])
async def rsa_encrypt(
    request: Request,
    req: RsaEncryptRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[RsaEncryptResponse]:
    result = await pubkey_service.rsa_encrypt(db, user, req)
    return _ok(request, result)


@router.post("/rsa/decrypt", response_model=APIResponse[RsaDecryptResponse])
async def rsa_decrypt(
    request: Request,
    req: RsaDecryptRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[RsaDecryptResponse]:
    result = await pubkey_service.rsa_decrypt(db, user, req)
    return _ok(request, result)


@router.post("/rsa/sign", response_model=APIResponse[RsaSignResponse])
async def rsa_sign(
    request: Request,
    req: RsaSignRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[RsaSignResponse]:
    result = await pubkey_service.rsa_sign(db, user, req)
    return _ok(request, result)


@router.post("/rsa/verify", response_model=APIResponse[RsaVerifyResponse])
async def rsa_verify(
    request: Request,
    req: RsaVerifyRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[RsaVerifyResponse]:
    result = await pubkey_service.rsa_verify(db, user, req)
    return _ok(request, result)


@router.post("/ecc/keygen", response_model=APIResponse[EccKeygenResponse])
async def ecc_keygen(
    request: Request,
    req: EccKeygenRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[EccKeygenResponse]:
    result = await pubkey_service.ecc_keygen(db, user, req)
    return _ok(request, result)


@router.post("/ecdsa/sign", response_model=APIResponse[EcdsaSignResponse])
async def ecdsa_sign(
    request: Request,
    req: EcdsaSignRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[EcdsaSignResponse]:
    result = await pubkey_service.ecdsa_sign(db, user, req)
    return _ok(request, result)


@router.post("/ecdsa/verify", response_model=APIResponse[EcdsaVerifyResponse])
async def ecdsa_verify(
    request: Request,
    req: EcdsaVerifyRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[EcdsaVerifyResponse]:
    result = await pubkey_service.ecdsa_verify(db, user, req)
    return _ok(request, result)


def _ok(request: Request, data: object) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
