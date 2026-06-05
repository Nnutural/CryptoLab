//! Unified error type for the entire crate.
//!
//! Every algorithm module returns `CryptoResult<T>`. The PyO3 boundary in
//! [`crate::ffi`] converts `CryptoError` into a Python exception so callers
//! see a meaningful `ValueError` / `RuntimeError` instead of a panic.

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::PyErr;
use thiserror::Error;

/// Result alias used throughout the crate.
pub type CryptoResult<T> = Result<T, CryptoError>;

/// All errors that a CryptoLab primitive may surface.
#[derive(Debug, Error)]
pub enum CryptoError {
    /// Key length does not match the algorithm's requirement.
    #[error("invalid key length: expected {expected} bytes, got {actual}")]
    InvalidKeyLength {
        /// expected key length in bytes
        expected: usize,
        /// actual length supplied
        actual: usize,
    },

    /// Initialization vector length is wrong for the chosen mode.
    #[error("invalid IV length: expected {expected} bytes, got {actual}")]
    InvalidIvLength {
        /// expected IV length in bytes
        expected: usize,
        /// actual length supplied
        actual: usize,
    },

    /// Plaintext / ciphertext length is not a multiple of the block size.
    #[error("invalid input length: {0}")]
    InvalidInputLength(String),

    /// Padding bytes are malformed (PKCS#7 / X.923 / Zero).
    #[error("invalid padding")]
    InvalidPadding,

    /// Authentication tag (e.g. GCM, HMAC) did not verify.
    /// Production code MUST NOT leak any additional detail here.
    #[error("authentication failed")]
    AuthenticationFailed,

    /// A bigint operation failed (e.g. modular inverse does not exist).
    #[error("big-integer operation failed: {0}")]
    BigIntError(String),

    /// Encoding / decoding error (Base64 alphabet, invalid UTF-8 byte sequence).
    #[error("encoding error: {0}")]
    EncodingError(String),

    /// Signature verification reported a mismatch.
    #[error("signature verification failed")]
    SignatureInvalid,

    /// Asymmetric key pair is malformed (RSA n/e/d inconsistent, ECC point off-curve, ...).
    #[error("invalid key: {0}")]
    InvalidKey(String),

    /// Algorithm parameters out of range (e.g. PBKDF2 iter < 1, RSA key size < 1024).
    #[error("invalid parameter: {0}")]
    InvalidParameter(String),

    /// A random source returned an error.
    #[error("random source failure: {0}")]
    RandomError(String),

    /// Generic catch-all for things that genuinely shouldn't happen.
    /// Use sparingly — prefer a more specific variant.
    #[error("internal error: {0}")]
    Internal(String),
}

impl From<CryptoError> for PyErr {
    fn from(err: CryptoError) -> PyErr {
        match err {
            // Caller-side errors → ValueError.
            CryptoError::InvalidKeyLength { .. }
            | CryptoError::InvalidIvLength { .. }
            | CryptoError::InvalidInputLength(_)
            | CryptoError::InvalidPadding
            | CryptoError::InvalidKey(_)
            | CryptoError::InvalidParameter(_)
            | CryptoError::EncodingError(_) => PyValueError::new_err(err.to_string()),

            // Crypto-truth errors (auth/signature failure) → ValueError to
            // align with Python's `hmac.HMAC.verify` convention.
            CryptoError::AuthenticationFailed | CryptoError::SignatureInvalid => {
                PyValueError::new_err(err.to_string())
            }

            // Genuine internal failures → RuntimeError.
            CryptoError::BigIntError(_)
            | CryptoError::RandomError(_)
            | CryptoError::Internal(_) => PyRuntimeError::new_err(err.to_string()),
        }
    }
}

impl From<getrandom::Error> for CryptoError {
    fn from(err: getrandom::Error) -> Self {
        CryptoError::RandomError(err.to_string())
    }
}
