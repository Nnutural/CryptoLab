"""KEK derivation (HKDF-SHA256) and envelope encryption for key_store rows.

HKDF is built on top of ``cryptolab_core.hmac_sha256`` — no external KDF
library is used.  The derived KEK is cached at module level so the
HKDF-Extract+Expand cost is paid only once per process lifetime.
"""

from __future__ import annotations

import math
import secrets
from typing import Any

_KEK_CACHE: bytes | None = None

HKDF_SALT = b"cryptolab-kek-v1"
HKDF_INFO = b"master-kek"
HKDF_LEN = 32
_HMAC_LEN = 32


def _hmac_sha256(key: bytes, data: bytes) -> bytes:
    import cryptolab_core

    return bytes(cryptolab_core.hmac_sha256(key, data))


def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    return _hmac_sha256(salt, ikm)


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    n = math.ceil(length / _HMAC_LEN)
    okm = b""
    t = b""
    for i in range(1, n + 1):
        t = _hmac_sha256(prk, t + info + bytes([i]))
        okm += t
    return okm[:length]


def hkdf_sha256(ikm: bytes, salt: bytes, info: bytes, length: int) -> bytes:
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)


def derive_kek(master_key: bytes) -> bytes:
    """Derive a 32-byte KEK from the master key using HKDF-SHA256."""
    return hkdf_sha256(master_key, HKDF_SALT, HKDF_INFO, HKDF_LEN)


def get_kek() -> bytes:
    """Return the cached KEK, deriving it on first call."""
    global _KEK_CACHE
    if _KEK_CACHE is not None:
        return _KEK_CACHE

    from app.core.config import get_settings

    settings = get_settings()
    raw = bytes.fromhex(settings.master_key_hex)
    if len(raw) < 32:
        raise RuntimeError("CRYPTOLAB_MASTER_KEY_HEX must be at least 32 bytes")
    _KEK_CACHE = derive_kek(raw)
    return _KEK_CACHE


def reset_kek_cache() -> None:
    """Clear the cached KEK — used by tests that switch master keys."""
    global _KEK_CACHE
    _KEK_CACHE = None


def envelope_encrypt(plaintext: bytes, key_id_bytes: bytes) -> tuple[bytes, bytes, bytes]:
    """AES-256-GCM encrypt *plaintext* under the KEK with AAD = key_id UUID bytes.

    Returns ``(ciphertext_with_tag, iv, tag)`` where *ciphertext_with_tag*
    includes the 16-byte GCM tag appended.
    """
    import cryptolab_core

    kek = get_kek()
    iv = secrets.token_bytes(12)
    ct_with_tag: bytes = cryptolab_core.aes_encrypt(
        plaintext, kek, "GCM", iv, key_id_bytes, "None"
    )
    tag = ct_with_tag[-16:]
    ciphertext = ct_with_tag[:-16]
    return ciphertext, iv, tag


def envelope_decrypt(
    ciphertext: bytes, iv: bytes, tag: bytes, key_id_bytes: bytes
) -> bytes:
    """Decrypt an envelope-encrypted value, verifying the GCM tag with AAD = key_id."""
    import cryptolab_core

    kek = get_kek()
    ct_with_tag = ciphertext + tag
    plaintext: bytes = cryptolab_core.aes_decrypt(
        ct_with_tag, kek, "GCM", iv, key_id_bytes, "None"
    )
    return plaintext


def key_id_to_aad(key_id: str) -> bytes:
    """Convert a UUID string to 16 raw bytes for use as GCM AAD."""
    from uuid import UUID

    return UUID(key_id).bytes


def _redact(data: Any) -> str:
    """Return a safe repr for logging — never the actual bytes."""
    return f"<{type(data).__name__} len={len(data)}>" if isinstance(data, bytes | str) else "***"
