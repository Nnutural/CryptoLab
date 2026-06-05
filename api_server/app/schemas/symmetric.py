"""Symmetric-cipher DTOs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ModeName = Literal["ECB", "CBC", "CTR", "GCM"]
PaddingName = Literal["pkcs7", "zero", "ansi_x923", "none"]


class SymmetricEncryptRequest(BaseModel):
    plaintext_b64: str = Field(..., description="Plaintext bytes, base64-encoded")
    key_b64: str = Field(..., description="Key bytes, base64-encoded")
    mode: ModeName
    iv_b64: str | None = Field(default=None, description="IV/nonce (base64); required for non-ECB")
    aad_b64: str | None = Field(default=None, description="Additional authenticated data (GCM only)")
    padding: PaddingName = "pkcs7"
    verbose: bool = Field(default=False, description="Return per-round state (admin/debug only)")


class SymmetricDecryptRequest(BaseModel):
    ciphertext_b64: str
    key_b64: str
    mode: ModeName
    iv_b64: str | None = None
    aad_b64: str | None = None
    padding: PaddingName = "pkcs7"


class SymmetricResult(BaseModel):
    output_b64: str
    duration_ms: float
    rounds: list[dict[str, str]] | None = Field(
        default=None, description="Populated when verbose=true was honored"
    )
