"""Hash / HMAC / PBKDF2 DTOs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HashRequest(BaseModel):
    """Request to hash a UTF-8 source string."""

    data: str


class HashResponse(BaseModel):
    """Hex-encoded digest for a named hash algorithm."""

    digest_hex: str
    algorithm: str


class HmacRequest(BaseModel):
    """Request to compute HMAC over UTF-8 key and message strings."""

    key: str
    message: str
    algorithm: Literal["sha1", "sha256"]


class HmacResponse(BaseModel):
    """Hex-encoded HMAC tag for the selected algorithm."""

    mac_hex: str
    algorithm: str


class Pbkdf2Request(BaseModel):
    """Request to derive key bytes from UTF-8 password and salt strings."""

    password: str
    salt: str = Field(..., min_length=1)
    iterations: int = Field(..., ge=1000)
    key_len: int = Field(..., ge=1, le=64)


class Pbkdf2Response(BaseModel):
    """Hex-encoded PBKDF2-HMAC-SHA256 output."""

    derived_key_hex: str
    iterations: int
    warning: str | None = None
