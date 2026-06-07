"""Public-key endpoints: RSA, ECC, ECDSA."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
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


@router.post("/rsa/keygen", response_model=APIResponse[RsaKeygenResponse])
async def rsa_keygen(
    request: Request,
    req: RsaKeygenRequest,
) -> APIResponse[RsaKeygenResponse]:
    result = await pubkey_service.rsa_keygen(req)
    return _ok(request, result)


@router.post("/rsa/encrypt", response_model=APIResponse[RsaEncryptResponse])
async def rsa_encrypt(
    request: Request,
    req: RsaEncryptRequest,
) -> APIResponse[RsaEncryptResponse]:
    result = await pubkey_service.rsa_encrypt(req)
    return _ok(request, result)


@router.post("/rsa/decrypt", response_model=APIResponse[RsaDecryptResponse])
async def rsa_decrypt(
    request: Request,
    req: RsaDecryptRequest,
) -> APIResponse[RsaDecryptResponse]:
    result = await pubkey_service.rsa_decrypt(req)
    return _ok(request, result)


@router.post("/rsa/sign", response_model=APIResponse[RsaSignResponse])
async def rsa_sign(
    request: Request,
    req: RsaSignRequest,
) -> APIResponse[RsaSignResponse]:
    result = await pubkey_service.rsa_sign(req)
    return _ok(request, result)


@router.post("/rsa/verify", response_model=APIResponse[RsaVerifyResponse])
async def rsa_verify(
    request: Request,
    req: RsaVerifyRequest,
) -> APIResponse[RsaVerifyResponse]:
    result = await pubkey_service.rsa_verify(req)
    return _ok(request, result)


@router.post("/ecc/keygen", response_model=APIResponse[EccKeygenResponse])
async def ecc_keygen(
    request: Request,
    req: EccKeygenRequest,
) -> APIResponse[EccKeygenResponse]:
    result = await pubkey_service.ecc_keygen(req)
    return _ok(request, result)


@router.post("/ecdsa/sign", response_model=APIResponse[EcdsaSignResponse])
async def ecdsa_sign(
    request: Request,
    req: EcdsaSignRequest,
) -> APIResponse[EcdsaSignResponse]:
    result = await pubkey_service.ecdsa_sign(req)
    return _ok(request, result)


@router.post("/ecdsa/verify", response_model=APIResponse[EcdsaVerifyResponse])
async def ecdsa_verify(
    request: Request,
    req: EcdsaVerifyRequest,
) -> APIResponse[EcdsaVerifyResponse]:
    result = await pubkey_service.ecdsa_verify(req)
    return _ok(request, result)


def _ok(
    request: Request,
    data: (
        RsaKeygenResponse
        | RsaEncryptResponse
        | RsaDecryptResponse
        | RsaSignResponse
        | RsaVerifyResponse
        | EccKeygenResponse
        | EcdsaSignResponse
        | EcdsaVerifyResponse
    ),
) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
