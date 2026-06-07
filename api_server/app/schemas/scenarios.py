"""Composite scenario DTOs — with optional key_id support."""

from __future__ import annotations

import base64
import binascii
from typing import Any, Literal

from pydantic import BaseModel, field_validator, model_validator

MAX_FILE_BYTES = 10 * 1024 * 1024


class SecureSendRequest(BaseModel):
    file_b64: str
    receiver_rsa_public_pem: dict[str, str] | None = None
    receiver_rsa_public_key_id: str | None = None
    sender_ecdsa_private_hex: str | None = None
    sender_ecdsa_private_key_id: str | None = None
    sender_ecdsa_curve: Literal["secp160r1"] = "secp160r1"

    @field_validator("file_b64")
    @classmethod
    def validate_file_b64(cls, value: str) -> str:
        try:
            decoded = base64.b64decode(value.encode("ascii"), validate=True)
        except (binascii.Error, UnicodeEncodeError) as exc:
            raise ValueError("file_b64 must be standard Base64") from exc
        if len(decoded) > MAX_FILE_BYTES:
            raise ValueError("file exceeds 10 MiB limit")
        return value

    @model_validator(mode="after")
    def check_key_sources(self) -> SecureSendRequest:
        no_rsa = self.receiver_rsa_public_pem is None and self.receiver_rsa_public_key_id is None
        if no_rsa:
            raise ValueError("receiver_rsa_public_pem or receiver_rsa_public_key_id required")
        no_ecdsa = (
            self.sender_ecdsa_private_hex is None and self.sender_ecdsa_private_key_id is None
        )
        if no_ecdsa:
            raise ValueError("sender_ecdsa_private_hex or sender_ecdsa_private_key_id required")
        if self.receiver_rsa_public_pem is not None:
            _require_hex_dict(
                self.receiver_rsa_public_pem, ("n_hex", "e_hex"), "receiver_rsa_public_pem",
            )
        if self.sender_ecdsa_private_hex is not None:
            _decode_hex(self.sender_ecdsa_private_hex, "sender_ecdsa_private_hex")
        return self


class SecureSendResponse(BaseModel):
    envelope: dict[str, Any]
    sender_summary: dict[str, int | float]


class SecureReceiveRequest(BaseModel):
    envelope: dict[str, Any]
    receiver_rsa_private: dict[str, str] | None = None
    receiver_rsa_private_key_id: str | None = None
    sender_ecdsa_public: dict[str, str] | None = None
    sender_ecdsa_public_key_id: str | None = None

    @model_validator(mode="after")
    def check_key_sources(self) -> SecureReceiveRequest:
        no_rsa = self.receiver_rsa_private is None and self.receiver_rsa_private_key_id is None
        if no_rsa:
            raise ValueError("receiver_rsa_private or receiver_rsa_private_key_id required")
        no_ecdsa = self.sender_ecdsa_public is None and self.sender_ecdsa_public_key_id is None
        if no_ecdsa:
            raise ValueError("sender_ecdsa_public or sender_ecdsa_public_key_id required")
        if self.receiver_rsa_private is not None:
            _require_hex_dict(
                self.receiver_rsa_private,
                ("n_hex", "d_hex", "p_hex", "q_hex"),
                "receiver_rsa_private",
            )
        if self.sender_ecdsa_public is not None:
            _require_hex_dict(self.sender_ecdsa_public, ("qx_hex", "qy_hex"), "sender_ecdsa_public")
            curve = self.sender_ecdsa_public.get("curve", "secp160r1")
            if curve != "secp160r1":
                raise ValueError("sender_ecdsa_public.curve must be secp160r1")
        return self


class SecureReceiveResponse(BaseModel):
    plaintext_b64: str
    verification: dict[str, bool]
    duration_ms: float


def _require_hex_dict(value: dict[str, str], keys: tuple[str, ...], field: str) -> None:
    for key in keys:
        if key not in value:
            raise ValueError(f"{field}.{key} is required")
        _decode_hex(value[key], f"{field}.{key}")


def _decode_hex(value: str, field: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
