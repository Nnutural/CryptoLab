//! Base64 — RFC 4648 §4. Standard alphabet, with `=` padding.

use crate::error::CryptoResult;

/// Encode arbitrary bytes as standard Base64 with `=` padding.
pub fn encode(_data: &[u8]) -> String {
    todo!("RFC 4648 §4 standard alphabet; 3-byte → 4-char grouping with padding")
}

/// Decode standard Base64 (with or without padding). URL-safe variant uses
/// the same code path with an alternate alphabet table.
pub fn decode(_encoded: &str) -> CryptoResult<Vec<u8>> {
    todo!("strip whitespace, validate alphabet, 4-char → 3-byte grouping")
}
