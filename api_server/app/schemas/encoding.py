"""Encoding (Base64 / UTF-8) DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class EncodeRequest(BaseModel):
    """Request to Base64-encode a UTF-8 source string."""

    data: str


class EncodeResponse(BaseModel):
    """Base64 output using the RFC 4648 standard alphabet and `=` padding."""

    encoded: str


class DecodeRequest(BaseModel):
    """Request to decode an RFC 4648 Base64 string."""

    encoded: str


class DecodeResponse(BaseModel):
    """Decoded bytes re-encoded as standard Base64 to avoid binary JSON text."""

    data: str
