"""Symmetric-cipher DTOs."""

from __future__ import annotations

import base64
import binascii
from typing import Literal

from pydantic import BaseModel, Field, model_validator

AlgorithmName = Literal["aes", "sm4", "rc6"]
ModeName = Literal["ECB", "CBC", "CTR", "GCM"]
PaddingName = Literal["PKCS7", "Zero", "X923", "None"]


class _SymmetricBase(BaseModel):
    algorithm: AlgorithmName
    mode: ModeName
    padding: PaddingName = "PKCS7"
    key_hex: str
    iv_hex: str | None = None
    aad_b64: str | None = None

    @model_validator(mode="after")
    def validate_lengths(self) -> _SymmetricBase:
        key = _decode_hex(self.key_hex, "key_hex")
        if len(key) not in {16, 24, 32}:
            raise ValueError("key length must be 16, 24, or 32 bytes")
        if self.algorithm in {"sm4", "rc6"} and len(key) != 16:
            raise ValueError(f"{self.algorithm.upper()} key length must be 16 bytes")

        if self.mode in {"CBC", "CTR"}:
            iv = self._required_iv()
            if len(iv) != 16:
                raise ValueError(f"{self.mode} IV must be 16 bytes")
        elif self.mode == "GCM":
            iv = self._required_iv()
            if len(iv) != 12:
                raise ValueError("GCM IV must be 12 bytes")
            if self.algorithm == "rc6":
                raise ValueError("RC6 does not support GCM")
        elif self.iv_hex is not None:
            _decode_hex(self.iv_hex, "iv_hex")

        if self.aad_b64 is not None:
            _decode_b64(self.aad_b64, "aad_b64")
        return self

    def key_bytes(self) -> bytes:
        return _decode_hex(self.key_hex, "key_hex")

    def iv_bytes(self) -> bytes | None:
        if self.iv_hex is None:
            return None
        return _decode_hex(self.iv_hex, "iv_hex")

    def aad_bytes(self) -> bytes | None:
        if self.aad_b64 is None:
            return None
        return _decode_b64(self.aad_b64, "aad_b64")

    def _required_iv(self) -> bytes:
        if self.iv_hex is None:
            raise ValueError(f"{self.mode} requires iv_hex")
        return _decode_hex(self.iv_hex, "iv_hex")


class SymmetricEncryptRequest(_SymmetricBase):
    """Encrypt bytes carried as standard Base64."""

    plaintext_b64: str

    def plaintext_bytes(self) -> bytes:
        return _decode_b64(self.plaintext_b64, "plaintext_b64")


class SymmetricDecryptRequest(_SymmetricBase):
    """Decrypt bytes carried as standard Base64.

    For GCM, ``ciphertext_b64`` contains ``ciphertext || 16-byte tag``.
    """

    ciphertext_b64: str

    def ciphertext_bytes(self) -> bytes:
        return _decode_b64(self.ciphertext_b64, "ciphertext_b64")


class SymmetricEncryptResponse(BaseModel):
    ciphertext_b64: str
    algorithm: str
    mode: str
    duration_ms: float = Field(..., ge=0)


class SymmetricDecryptResponse(BaseModel):
    plaintext_b64: str
    algorithm: str
    mode: str
    duration_ms: float = Field(..., ge=0)


def _decode_hex(value: str, field: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc


def _decode_b64(value: str, field: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise ValueError(f"{field} must be standard Base64") from exc
