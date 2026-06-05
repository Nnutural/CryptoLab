"""Hash / HMAC / PBKDF2 DTOs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HashRequest(BaseModel):
    data_b64: str
    verbose: bool = False


class HmacRequest(BaseModel):
    key_b64: str
    message_b64: str


class Pbkdf2Request(BaseModel):
    password_b64: str
    salt_b64: str
    iterations: int = Field(..., ge=1, le=10_000_000)
    dk_len: int = Field(..., ge=1, le=4096)


class HashResult(BaseModel):
    digest_hex: str
    digest_b64: str
    duration_ms: float
