"""Vulnerability-demo DTOs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EcbImageLeakRequest(BaseModel):
    image_b64: str
    image_format: str = Field(default="png", pattern="^(png|bmp)$")


class EcbImageLeakResult(BaseModel):
    encrypted_image_b64: str
    explanation: str  # rendered as the front-end's "原理说明" pane


class EcdsaKReuseRequest(BaseModel):
    message1_b64: str
    message2_b64: str


class EcdsaKReuseResult(BaseModel):
    r_b64: str
    s1_b64: str
    s2_b64: str
    recovered_d_b64: str
    explanation: str


class RsaLowExponentRequest(BaseModel):
    message_b64: str
    e: int = 3
    bits: int = 1024


class RsaLowExponentResult(BaseModel):
    ciphertext_b64: str
    recovered_plaintext_b64: str
    explanation: str


class Pbkdf2ImpactRequest(BaseModel):
    password_b64: str
    salt_b64: str
    dk_len: int = 32


class Pbkdf2ImpactResult(BaseModel):
    iterations_to_ms: dict[int, float]
    explanation: str
