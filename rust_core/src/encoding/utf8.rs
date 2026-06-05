//! UTF-8 — RFC 3629 transformation of Unicode codepoints.
//!
//! Rust's `str` is already UTF-8, but the assignment asks us to demonstrate
//! the codec end-to-end (including overlong-encoding rejection).

use crate::error::{CryptoError, CryptoResult};

/// Encode a Rust string into raw UTF-8 bytes.
pub fn encode(_text: &str) -> Vec<u8> {
    todo!("walk codepoints; emit 1/2/3/4-byte sequences per RFC 3629 §3")
}

/// Decode raw bytes into a Rust `String`, rejecting overlong forms /
/// surrogate halves / invalid continuation bytes.
pub fn decode(_data: &[u8]) -> CryptoResult<String> {
    let _ = CryptoError::EncodingError; // silence unused-import noise pre-impl
    todo!("strict RFC 3629 decoder; on any violation return EncodingError")
}
