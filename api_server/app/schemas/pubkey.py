"""Public-key DTOs (RSA + ECC + ECDSA) — key_id based."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

EccCurve = Literal["secp160r1"]


class RsaKeygenRequest(BaseModel):
    bits: Literal[1024] = 1024
    e: int = Field(default=65537, ge=65537)
    label: str | None = None

    @classmethod
    def validate_exponent(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError("RSA exponent must be odd")
        return value


class RsaKeygenResponse(BaseModel):
    private_key_id: str
    public_key_id: str
    algorithm: str = "rsa"
    bits: int


class RsaEncryptRequest(BaseModel):
    plaintext: str
    key_id: str


class RsaEncryptResponse(BaseModel):
    ciphertext_hex: str


class RsaDecryptRequest(BaseModel):
    ciphertext_hex: str
    key_id: str


class RsaDecryptResponse(BaseModel):
    plaintext: str


class RsaSignRequest(BaseModel):
    message: str
    key_id: str


class RsaSignResponse(BaseModel):
    signature_hex: str


class RsaVerifyRequest(BaseModel):
    message: str
    signature_hex: str
    key_id: str


class RsaVerifyResponse(BaseModel):
    valid: bool


class EccKeygenRequest(BaseModel):
    curve: EccCurve = "secp160r1"
    label: str | None = None


class EccKeygenResponse(BaseModel):
    private_key_id: str
    public_key_id: str
    algorithm: str = "ecc"
    curve: EccCurve


class EcdsaSignRequest(BaseModel):
    message: str
    key_id: str
    curve: EccCurve = "secp160r1"


class EcdsaSignResponse(BaseModel):
    r_hex: str
    s_hex: str
    curve: str


class EcdsaVerifyRequest(BaseModel):
    message: str
    r_hex: str
    s_hex: str
    key_id: str
    curve: EccCurve = "secp160r1"


class EcdsaVerifyResponse(BaseModel):
    valid: bool
    curve: str
