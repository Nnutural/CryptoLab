"""Composite application scenarios built from CryptoLab primitives."""

from __future__ import annotations

import base64
import binascii
import hmac
import secrets
import time
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.security import AuthenticatedUser
from app.core.status_codes import StatusCode
from app.schemas.scenarios import (
    MAX_FILE_BYTES,
    SecureReceiveRequest,
    SecureReceiveResponse,
    SecureSendRequest,
    SecureSendResponse,
)
from app.services import key_service

SUPPORTED_ALG = {
    "kem": "RSA-OAEP-SHA256",
    "aead": "AES-256-GCM",
    "sig": "ECDSA-secp160r1-SHA256",
    "transport": "base64",
}


async def secure_file_send(
    req: SecureSendRequest,
    db: Session | None = None,
    user: AuthenticatedUser | None = None,
) -> SecureSendResponse:
    """Package a file for secure transport using RSA-OAEP + AES-GCM + ECDSA."""
    start = time.perf_counter()
    plaintext = _b64decode(req.file_b64, "file_b64")
    if len(plaintext) > MAX_FILE_BYTES:
        raise CryptoAPIException(
            StatusCode.PARAM_MISSING,
            "file exceeds 10 MiB limit",
            http_status=422,
        )

    if req.receiver_rsa_public_key_id and db and user:
        pub_mat = key_service.fetch_and_decrypt_json(
            db, user, req.receiver_rsa_public_key_id, "public"
        )
        n = _from_hex(pub_mat["n_hex"], "n_hex")
        e = _from_hex(pub_mat["e_hex"], "e_hex")
    else:
        assert req.receiver_rsa_public_pem is not None
        n = _from_hex(req.receiver_rsa_public_pem["n_hex"], "receiver_rsa_public_pem.n_hex")
        e = _from_hex(req.receiver_rsa_public_pem["e_hex"], "receiver_rsa_public_pem.e_hex")

    if req.sender_ecdsa_private_key_id and db and user:
        priv_mat = key_service.fetch_and_decrypt_json(
            db, user, req.sender_ecdsa_private_key_id, "private"
        )
        sender_d = _from_hex(priv_mat["d_hex"], "d_hex")
    else:
        assert req.sender_ecdsa_private_hex is not None
        sender_d = _from_hex(req.sender_ecdsa_private_hex, "sender_ecdsa_private_hex")

    try:
        import cryptolab_core

        session_key = secrets.token_bytes(32)
        iv = secrets.token_bytes(12)
        enc_session_key = cryptolab_core.rsa_encrypt_oaep(session_key, n, e)
        ciphertext_with_tag = cryptolab_core.aes_encrypt(
            plaintext, session_key, "GCM", iv, None, "None",
        )
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        file_digest = cryptolab_core.sha256_digest(plaintext)
        r, s = cryptolab_core.ecdsa_sign(file_digest, sender_d, req.sender_ecdsa_curve)
    except ValueError as exc:
        raise CryptoAPIException(_status_for_core_error(str(exc)), str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "secure file send failed") from exc

    envelope: dict[str, Any] = {
        "alg": SUPPORTED_ALG.copy(),
        "enc_session_key_b64": _b64encode(enc_session_key),
        "iv_hex": iv.hex(),
        "ciphertext_b64": _b64encode(ciphertext),
        "tag_hex": tag.hex(),
        "file_sha256_hex": file_digest.hex(),
        "signature": {"r_hex": r.hex(), "s_hex": s.hex()},
    }
    return SecureSendResponse(
        envelope=envelope,
        sender_summary={
            "duration_ms": (time.perf_counter() - start) * 1000,
            "file_size_bytes": len(plaintext),
        },
    )


async def secure_file_receive(
    req: SecureReceiveRequest,
    db: Session | None = None,
    user: AuthenticatedUser | None = None,
) -> SecureReceiveResponse:
    """Open and verify a secure-file-transfer envelope."""
    start = time.perf_counter()
    envelope = req.envelope
    if envelope.get("alg") != SUPPORTED_ALG:
        raise CryptoAPIException(
            StatusCode.ALGORITHM_UNSUPPORTED,
            "unsupported_algorithm",
            data={"error": "unsupported_algorithm"},
            http_status=422,
        )

    if req.receiver_rsa_private_key_id and db and user:
        priv_mat = key_service.fetch_and_decrypt_json(
            db, user, req.receiver_rsa_private_key_id, "private"
        )
        rsa_n = _from_hex(priv_mat["n_hex"], "n_hex")
        rsa_d = _from_hex(priv_mat["d_hex"], "d_hex")
        rsa_p = _from_hex(priv_mat["p_hex"], "p_hex")
        rsa_q = _from_hex(priv_mat["q_hex"], "q_hex")
    else:
        assert req.receiver_rsa_private is not None
        private = req.receiver_rsa_private
        rsa_n = _from_hex(private["n_hex"], "receiver_rsa_private.n_hex")
        rsa_d = _from_hex(private["d_hex"], "receiver_rsa_private.d_hex")
        rsa_p = _from_hex(private["p_hex"], "receiver_rsa_private.p_hex")
        rsa_q = _from_hex(private["q_hex"], "receiver_rsa_private.q_hex")

    if req.sender_ecdsa_public_key_id and db and user:
        pub_mat = key_service.fetch_and_decrypt_json(
            db, user, req.sender_ecdsa_public_key_id, "public"
        )
        ecc_qx = _from_hex(pub_mat["qx_hex"], "qx_hex")
        ecc_qy = _from_hex(pub_mat["qy_hex"], "qy_hex")
        ecc_curve = pub_mat.get("curve", "secp160r1")
    else:
        assert req.sender_ecdsa_public is not None
        public = req.sender_ecdsa_public
        ecc_qx = _from_hex(public["qx_hex"], "sender_ecdsa_public.qx_hex")
        ecc_qy = _from_hex(public["qy_hex"], "sender_ecdsa_public.qy_hex")
        ecc_curve = public.get("curve", "secp160r1")

    try:
        import cryptolab_core

        enc_session_key = _b64decode(
            _required_str(envelope, "enc_session_key_b64"),
            "envelope.enc_session_key_b64",
        )
        iv = _from_hex(_required_str(envelope, "iv_hex"), "envelope.iv_hex")
        ciphertext = _b64decode(
            _required_str(envelope, "ciphertext_b64"),
            "envelope.ciphertext_b64",
        )
        tag = _from_hex(_required_str(envelope, "tag_hex"), "envelope.tag_hex")
        expected_digest_hex = _required_str(envelope, "file_sha256_hex")
        signature = _required_dict(envelope, "signature")
        r = _from_hex(_required_str(signature, "r_hex"), "envelope.signature.r_hex")
        s = _from_hex(_required_str(signature, "s_hex"), "envelope.signature.s_hex")

        session_key = cryptolab_core.rsa_decrypt_oaep(
            enc_session_key, rsa_n, rsa_d, rsa_p, rsa_q,
        )
        if len(session_key) != 32:
            raise CryptoAPIException(
                StatusCode.DECRYPT_FAILED,
                "decrypted session key length invalid",
            )

        plaintext = cryptolab_core.aes_decrypt(
            ciphertext + tag, session_key, "GCM", iv, None, "None",
        )
        digest = cryptolab_core.sha256_digest(plaintext)
        digest_ok = hmac.compare_digest(digest.hex(), expected_digest_hex)
        if not digest_ok:
            raise CryptoAPIException(StatusCode.DECRYPT_FAILED, "file digest mismatch")

        signature_ok = bool(
            cryptolab_core.ecdsa_verify(digest, r, s, ecc_qx, ecc_qy, ecc_curve)
        )
        if not signature_ok:
            raise CryptoAPIException(StatusCode.SIGNATURE_INVALID)
    except CryptoAPIException:
        raise
    except ValueError as exc:
        raise CryptoAPIException(_status_for_receive_value_error(str(exc)), str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "secure file receive failed") from exc

    return SecureReceiveResponse(
        plaintext_b64=_b64encode(plaintext),
        verification={
            "kem_ok": True,
            "aead_ok": True,
            "digest_ok": True,
            "signature_ok": True,
        },
        duration_ms=(time.perf_counter() - start) * 1000,
    )


def _b64decode(value: str, field: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise CryptoAPIException(
            StatusCode.ENCODING_ERROR,
            f"{field} must be standard Base64",
        ) from exc


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _from_hex(value: str, field: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, f"{field} must be hexadecimal") from exc


def _required_str(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str):
        raise CryptoAPIException(StatusCode.PARAM_MISSING, f"{key} is required")
    return value


def _required_dict(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key)
    if not isinstance(value, dict):
        raise CryptoAPIException(StatusCode.PARAM_MISSING, f"{key} is required")
    return value


def _status_for_core_error(message: str) -> StatusCode:
    lowered = message.lower()
    if "key length" in lowered:
        return StatusCode.KEY_LENGTH_INVALID
    if "unsupported" in lowered:
        return StatusCode.ALGORITHM_UNSUPPORTED
    if "authentication failed" in lowered:
        return StatusCode.DECRYPT_FAILED
    return StatusCode.CRYPTO_LIB_ERROR


def _status_for_receive_value_error(message: str) -> StatusCode:
    lowered = message.lower()
    if "authentication failed" in lowered or "invalid padding" in lowered:
        return StatusCode.DECRYPT_FAILED
    if "signature" in lowered:
        return StatusCode.SIGNATURE_INVALID
    if "unsupported" in lowered:
        return StatusCode.ALGORITHM_UNSUPPORTED
    return StatusCode.DECRYPT_FAILED
