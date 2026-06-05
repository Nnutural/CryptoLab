//! CryptoLab core — hand-written cryptographic primitives.
//!
//! Layer L2 of the CryptoLab architecture. This crate is deliberately HTTP-
//! agnostic: it knows nothing about FastAPI, requests, or JSON. The only
//! "outside world" coupling lives in [`ffi`], which exposes selected
//! functions to Python via PyO3.
//!
//! Module map:
//! - [`bigint`]   — cryptographic big-integer wrapper (Miller-Rabin, mod-pow, ...)
//! - [`encoding`] — Base64 / UTF-8 codecs
//! - [`hash`]     — SHA-1/2/3, RIPEMD-160, HMAC, PBKDF2
//! - [`modes`]    — ECB / CBC / CTR / GCM block-cipher modes
//! - [`pubkey`]   — RSA / ECC / ECDSA
//! - [`symmetric`]— AES / SM4 / RC6 block ciphers
//! - [`traits`]   — `SymmetricCipher`, `HashAlgorithm`, `PublicKeyAlgorithm`
//! - [`error`]    — the unified `CryptoError` type
//! - [`ffi`]      — PyO3 bindings (the ONLY module that touches Python)

#![forbid(unsafe_code)]
#![warn(missing_docs, clippy::all)]
#![allow(clippy::module_inception)]

pub mod bigint;
pub mod encoding;
pub mod error;
pub mod hash;
pub mod modes;
pub mod pubkey;
pub mod symmetric;
pub mod traits;

pub mod ffi;

pub use error::{CryptoError, CryptoResult};

use pyo3::prelude::*;

/// The PyO3 module entry point. Keep this thin — every binding lives in
/// [`ffi`] so the algorithm modules stay HTTP/Python-agnostic.
#[pymodule]
fn cryptolab_core(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    ffi::register(py, m)
}
