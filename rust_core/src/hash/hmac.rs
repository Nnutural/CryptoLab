//! HMAC (RFC 2104) — Keyed-Hashing for Message Authentication.

use crate::error::CryptoResult;

/// HMAC-SHA-256.
///
/// Tag length is fixed at 32 bytes. For verification use
/// `subtle::ConstantTimeEq` — never `==`.
pub fn hmac_sha256(_key: &[u8], _message: &[u8]) -> CryptoResult<Vec<u8>> {
    todo!("compute H((K' ⊕ opad) || H((K' ⊕ ipad) || m)) per RFC 2104")
}

/// HMAC-SHA-1 (educational; SHA-1 is broken — do not use in new code).
pub fn hmac_sha1(_key: &[u8], _message: &[u8]) -> CryptoResult<Vec<u8>> {
    todo!("HMAC over SHA-1; same construction as hmac_sha256 with a different inner hash")
}
