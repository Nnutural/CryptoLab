"""Public-key DTOs (RSA + ECC + ECDSA)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

EccCurve = Literal["secp160r1"]


class RsaKeygenRequest(BaseModel):
    bits: Literal[1024] = 1024
    e: int = Field(default=65537, ge=65537)

    @field_validator("e")
    @classmethod
    def exponent_must_be_odd(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError("RSA exponent must be odd")
        return value


class RsaKeygenResponse(BaseModel):
    n_hex: str
    e_hex: str
    d_hex: str
    p_hex: str
    q_hex: str
    warning: str


class RsaEncryptRequest(BaseModel):
    plaintext: str
    n_hex: str
    e_hex: str


class RsaEncryptResponse(BaseModel):
    ciphertext_hex: str


class RsaDecryptRequest(BaseModel):
    ciphertext_hex: str
    n_hex: str
    d_hex: str
    p_hex: str
    q_hex: str


class RsaDecryptResponse(BaseModel):
    plaintext: str


class RsaSignRequest(BaseModel):
    message: str
    n_hex: str
    d_hex: str
    p_hex: str
    q_hex: str


class RsaSignResponse(BaseModel):
    signature_hex: str


class RsaVerifyRequest(BaseModel):
    message: str
    signature_hex: str
    n_hex: str
    e_hex: str


class RsaVerifyResponse(BaseModel):
    valid: bool


class EccKeygenRequest(BaseModel):
    curve: EccCurve = "secp160r1"


class EccKeygenResponse(BaseModel):
    curve: EccCurve
    d_hex: str
    qx_hex: str
    qy_hex: str


class EcdsaSignRequest(BaseModel):
    message: str
    d_hex: str
    curve: EccCurve = "secp160r1"


class EcdsaSignResponse(BaseModel):
    r_hex: str
    s_hex: str
    curve: str


class EcdsaVerifyRequest(BaseModel):
    message: str
    r_hex: str
    s_hex: str
    qx_hex: str
    qy_hex: str
    curve: EccCurve = "secp160r1"


class EcdsaVerifyResponse(BaseModel):
    valid: bool
    curve: str
