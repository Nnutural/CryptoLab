"""Public-key DTOs (RSA + ECC + ECDSA)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

RsaPadding = Literal["pkcs1v15", "oaep"]
RsaSignScheme = Literal["pkcs1v15", "pss"]
EccCurve = Literal["secp160r1"]


# ----- RSA -----

class RsaKeygenRequest(BaseModel):
    bits: int = Field(default=1024, ge=1024, le=4096)
    e: int = Field(default=65537, ge=65537)
    label: str | None = None


class RsaKeyResult(BaseModel):
    key_id: str
    n_b64: str
    e_b64: str
    # Private key bytes are NOT echoed; consumers fetch them through key_service.


class RsaEncryptRequest(BaseModel):
    key_id: str
    plaintext_b64: str
    padding: RsaPadding = "oaep"


class RsaDecryptRequest(BaseModel):
    key_id: str
    ciphertext_b64: str
    padding: RsaPadding = "oaep"


class RsaEncryptResult(BaseModel):
    output_b64: str
    duration_ms: float


class RsaSignRequest(BaseModel):
    key_id: str
    message_b64: str
    scheme: RsaSignScheme = "pss"


class RsaSignResult(BaseModel):
    signature_b64: str
    duration_ms: float


class RsaVerifyRequest(BaseModel):
    key_id: str
    message_b64: str
    signature_b64: str
    scheme: RsaSignScheme = "pss"


class RsaVerifyResult(BaseModel):
    valid: bool
    duration_ms: float


# ----- ECC / ECDSA -----

class EccKeygenRequest(BaseModel):
    curve: EccCurve = "secp160r1"
    label: str | None = None


class EccKeyResult(BaseModel):
    key_id: str
    curve: EccCurve
    px_b64: str
    py_b64: str


class EcdsaSignRequest(BaseModel):
    key_id: str
    message_b64: str


class EcdsaSignResult(BaseModel):
    r_b64: str
    s_b64: str
    duration_ms: float


class EcdsaVerifyRequest(BaseModel):
    key_id: str
    message_b64: str
    r_b64: str
    s_b64: str


class EcdsaVerifyResult(BaseModel):
    valid: bool
    duration_ms: float
