"""Application-level status codes, separate from HTTP status codes."""

from __future__ import annotations

from enum import IntEnum


class StatusCode(IntEnum):
    """Business status code used in the uniform API response envelope."""

    OK = 1000

    PARAM_MISSING = 2001
    KEY_LENGTH_INVALID = 2002
    ENCODING_ERROR = 2003
    ALGORITHM_UNSUPPORTED = 2004
    PADDING_INVALID = 2005

    ENCRYPT_FAILED = 3001
    DECRYPT_FAILED = 3002
    SIGNATURE_INVALID = 3003
    KEY_MISMATCH = 3004

    UNAUTHENTICATED = 4001
    TOKEN_EXPIRED = 4002
    FORBIDDEN = 4003
    AUTH_TOKEN_MISSING = 4101
    AUTH_TOKEN_MALFORMED = 4102
    AUTH_TOKEN_INVALID = 4103
    AUTH_TOKEN_EXPIRED = 4104
    AUTH_TOKEN_BLACKLISTED = 4105
    AUTH_LOGIN_FAILED = 4106
    AUTH_USERNAME_EXISTS = 4107

    KEY_NOT_OWNED = 4201
    KEY_NOT_FOUND = 4202
    KEY_TYPE_MISMATCH = 4203
    KEY_PRIVATE_ACCESS_DENIED = 4204

    INTERNAL = 5000
    RATE_LIMIT_EXCEEDED = 5001
    DATABASE_ERROR = 5002
    CRYPTO_LIB_ERROR = 5003


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
    StatusCode.AUTH_TOKEN_MISSING: "Authorization token missing",
    StatusCode.AUTH_TOKEN_MALFORMED: "Authorization header is malformed",
    StatusCode.AUTH_TOKEN_INVALID: "Authorization token is invalid",
    StatusCode.AUTH_TOKEN_EXPIRED: "Authorization token has expired",
    StatusCode.AUTH_TOKEN_BLACKLISTED: "Authorization token has been revoked",
    StatusCode.AUTH_LOGIN_FAILED: "Invalid username or password",
    StatusCode.AUTH_USERNAME_EXISTS: "Username already exists",
    StatusCode.KEY_NOT_OWNED: "Key not owned by current user",
    StatusCode.KEY_NOT_FOUND: "Key not found",
    StatusCode.KEY_TYPE_MISMATCH: "Key type does not match the operation",
    StatusCode.KEY_PRIVATE_ACCESS_DENIED: "Cannot export private or symmetric key material",
    StatusCode.INTERNAL: "Internal server error",
    StatusCode.RATE_LIMIT_EXCEEDED: "Too many requests",
    StatusCode.DATABASE_ERROR: "Database error",
    StatusCode.CRYPTO_LIB_ERROR: "Cryptographic library error",
}


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
    StatusCode.AUTH_TOKEN_MISSING: 401,
    StatusCode.AUTH_TOKEN_MALFORMED: 401,
    StatusCode.AUTH_TOKEN_INVALID: 401,
    StatusCode.AUTH_TOKEN_EXPIRED: 401,
    StatusCode.AUTH_TOKEN_BLACKLISTED: 401,
    StatusCode.AUTH_LOGIN_FAILED: 401,
    StatusCode.AUTH_USERNAME_EXISTS: 409,
    StatusCode.KEY_NOT_OWNED: 403,
    StatusCode.KEY_NOT_FOUND: 404,
    StatusCode.KEY_TYPE_MISMATCH: 400,
    StatusCode.KEY_PRIVATE_ACCESS_DENIED: 403,
    StatusCode.INTERNAL: 500,
    StatusCode.RATE_LIMIT_EXCEEDED: 429,
    StatusCode.DATABASE_ERROR: 500,
    StatusCode.CRYPTO_LIB_ERROR: 500,
}
