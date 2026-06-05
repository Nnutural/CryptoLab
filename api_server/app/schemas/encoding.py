"""Encoding (Base64 / UTF-8) DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class EncodingRequest(BaseModel):
    # For encode: bytes are sent as base64; for decode: encoded text as plain str.
    data_b64: str | None = None
    text: str | None = None


class EncodingResult(BaseModel):
    output: str
    duration_ms: float
