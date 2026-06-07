"""Vulnerability-demo DTOs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class EcbImageLeakRequest(BaseModel):
    image_b64: str
    key_hex: str

    @field_validator("key_hex")
    @classmethod
    def validate_aes128_key(cls, value: str) -> str:
        try:
            key = bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("key_hex must be hexadecimal") from exc
        if len(key) != 16:
            raise ValueError("key_hex must encode a 16-byte AES-128 key")
        return value


class EcbImageLeakResponse(BaseModel):
    banner: str
    original_png_b64: str
    ecb_encrypted_png_b64: str
    cbc_encrypted_png_b64: str
    block_count: int
    duplicate_block_ratio: float


class EcdsaKReuseRequest(BaseModel):
    message1: str
    message2: str
    curve: Literal["secp160r1"] = "secp160r1"

    @model_validator(mode="after")
    def messages_must_differ(self) -> EcdsaKReuseRequest:
        if self.message1 == self.message2:
            raise ValueError("message1 and message2 must be different")
        return self


class EcdsaKReuseResponse(BaseModel):
    banner: str
    private_key_hex: str
    public_key: dict[str, str]
    reused_k_hex: str
    signature1: dict[str, str]
    signature2: dict[str, str]
    r_equal: bool
    recovered_d_hex: str
    recovery_matches_original: bool


class RsaLowExponentRequest(BaseModel):
    message: str = "BUPT2026"
    bits: Literal[1024] = 1024

    @model_validator(mode="after")
    def message_must_fit_cube_attack(self) -> RsaLowExponentRequest:
        message_int = int.from_bytes(self.message.encode("utf-8"), "big")
        if message_int.bit_length() * 3 >= self.bits:
            raise ValueError("message_too_long_for_cube_attack")
        return self


class RsaLowExponentResponse(BaseModel):
    banner: str
    n_hex: str
    e: int
    ciphertext_hex: str
    message_bits: int
    n_bits: int
    cube_safe: bool
    recovered_plaintext: str
    recovery_matches_original: bool


class Pbkdf2IterationImpactRequest(BaseModel):
    password: str = "password"
    salt_hex: str = "73616c747361"
    key_len: int = Field(default=32, ge=1, le=64)
    iterations_list: list[int] = Field(
        default_factory=lambda: [1_000, 10_000, 100_000, 1_000_000]
    )

    @field_validator("salt_hex")
    @classmethod
    def validate_salt_hex(cls, value: str) -> str:
        try:
            bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("salt_hex must be hexadecimal") from exc
        return value

    @field_validator("iterations_list")
    @classmethod
    def validate_iterations(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("iterations_list must not be empty")
        if any(iterations < 1 for iterations in value):
            raise ValueError("iterations must be positive")
        return value


class Pbkdf2IterationImpactResponse(BaseModel):
    banner: str
    measurements: list[dict[str, int | str | float]]
    ratio_1m_over_100k: float
    verdict: str


# Compatibility aliases for the pre-Phase-E placeholder module.
EcbImageLeakResult = EcbImageLeakResponse
EcdsaKReuseResult = EcdsaKReuseResponse
RsaLowExponentResult = RsaLowExponentResponse
Pbkdf2ImpactRequest = Pbkdf2IterationImpactRequest
Pbkdf2ImpactResult = Pbkdf2IterationImpactResponse
