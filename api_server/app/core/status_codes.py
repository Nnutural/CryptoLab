"""Application-level status codes (numbered per the design doc §3.2.2)."""

from __future__ import annotations

from enum import IntEnum


class StatusCode(IntEnum):
    """Business status code. Distinct from HTTP status."""

    # 1xxx — success
    OK = 1000

    # 2xxx — client parameter errors
    PARAM_MISSING = 2001
    KEY_LENGTH_INVALID = 2002
    ENCODING_ERROR = 2003
    ALGORITHM_UNSUPPORTED = 2004
    PADDING_INVALID = 2005

    # 3xxx — cryptographic failures
    ENCRYPT_FAILED = 3001
    DECRYPT_FAILED = 3002          # includes MAC verification failure
    SIGNATURE_INVALID = 3003
    KEY_MISMATCH = 3004

    # 4xxx — auth / authz
    UNAUTHENTICATED = 4001
    TOKEN_EXPIRED = 4002
    FORBIDDEN = 4003
    RATE_LIMITED = 4029

    # 5xxx — server side
    INTERNAL = 5000
    CRYPTO_LIB_ERROR = 5001
    DATABASE_ERROR = 5002


# Default English messages — Chinese variants come from i18n at the front-end.
DEFAULT_MESSAGES: dict[int, str] = {
    StatusCode.OK: "Success",
    StatusCode.PARAM_MISSING: "Required parameter missing",
    StatusCode.KEY_LENGTH_INVALID: "Key length is invalid for this algorithm",
    StatusCode.ENCODING_ERROR: "Encoding / decoding error",
    StatusCode.ALGORITHM_UNSUPPORTED: "Algorithm not supported",
    StatusCode.PADDING_INVALID: "Padding scheme is invalid",
    StatusCode.ENCRYPT_FAILED: "Encryption failed",
    StatusCode.DECRYPT_FAILED: "Decryption failed",
    StatusCode.SIGNATURE_INVALID: "Signature verification failed",
    StatusCode.KEY_MISMATCH: "Key does not match the operation",
    StatusCode.UNAUTHENTICATED: "Authentication required",
    StatusCode.TOKEN_EXPIRED: "Token has expired",
    StatusCode.FORBIDDEN: "Forbidden",
    StatusCode.RATE_LIMITED: "Too many requests",
    StatusCode.INTERNAL: "Internal server error",
    StatusCode.CRYPTO_LIB_ERROR: "Cryptographic library error",
    StatusCode.DATABASE_ERROR: "Database error",
}


# Map business codes back to HTTP status codes for the wire response.
HTTP_FOR_STATUS: dict[int, int] = {
    StatusCode.OK: 200,
    StatusCode.PARAM_MISSING: 400,
    StatusCode.KEY_LENGTH_INVALID: 400,
    StatusCode.ENCODING_ERROR: 400,
    StatusCode.ALGORITHM_UNSUPPORTED: 400,
    StatusCode.PADDING_INVALID: 400,
    StatusCode.ENCRYPT_FAILED: 400,
    StatusCode.DECRYPT_FAILED: 400,
    StatusCode.SIGNATURE_INVALID: 400,
    StatusCode.KEY_MISMATCH: 400,
    StatusCode.UNAUTHENTICATED: 401,
    StatusCode.TOKEN_EXPIRED: 401,
    StatusCode.FORBIDDEN: 403,
    StatusCode.RATE_LIMITED: 429,
    StatusCode.INTERNAL: 500,
    StatusCode.CRYPTO_LIB_ERROR: 500,
    StatusCode.DATABASE_ERROR: 500,
}
