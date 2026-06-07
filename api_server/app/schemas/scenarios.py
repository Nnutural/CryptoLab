"""Composite scenario DTOs."""

from __future__ import annotations

import base64
import binascii
from typing import Any, Literal

from pydantic import BaseModel, field_validator

MAX_FILE_BYTES = 10 * 1024 * 1024


class SecureSendRequest(BaseModel):
    file_b64: str
    receiver_rsa_public_pem: dict[str, str]
    sender_ecdsa_private_hex: str
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

    @field_validator("receiver_rsa_public_pem")
    @classmethod
    def validate_receiver_public(cls, value: dict[str, str]) -> dict[str, str]:
        _require_hex_dict(value, ("n_hex", "e_hex"), "receiver_rsa_public_pem")
        return value

    @field_validator("sender_ecdsa_private_hex")
    @classmethod
    def validate_sender_private(cls, value: str) -> str:
        _decode_hex(value, "sender_ecdsa_private_hex")
        return value


class SecureSendResponse(BaseModel):
    envelope: dict[str, Any]
    sender_summary: dict[str, int | float]


class SecureReceiveRequest(BaseModel):
    envelope: dict[str, Any]
    receiver_rsa_private: dict[str, str]
    sender_ecdsa_public: dict[str, str]

    @field_validator("receiver_rsa_private")
    @classmethod
    def validate_receiver_private(cls, value: dict[str, str]) -> dict[str, str]:
        _require_hex_dict(value, ("n_hex", "d_hex", "p_hex", "q_hex"), "receiver_rsa_private")
        return value

    @field_validator("sender_ecdsa_public")
    @classmethod
    def validate_sender_public(cls, value: dict[str, str]) -> dict[str, str]:
        _require_hex_dict(value, ("qx_hex", "qy_hex"), "sender_ecdsa_public")
        curve = value.get("curve", "secp160r1")
        if curve != "secp160r1":
            raise ValueError("sender_ecdsa_public.curve must be secp160r1")
        return value


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
