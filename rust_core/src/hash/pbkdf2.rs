//! PBKDF2 (RFC 8018 / NIST SP 800-132) — password-based key derivation.
//!
//! Iterations must be ≥ 100_000 for new deployments. The API exposes the
//! parameter to allow the attack-demo module to show the cost difference
//! between 1k/10k/100k/1M.

use crate::error::CryptoResult;

/// PBKDF2-HMAC-SHA-256.
///
/// `dk_len` is the desired derived-key length in bytes (≤ (2^32 - 1) * hLen).
pub fn pbkdf2_hmac_sha256(
    _password: &[u8],
    _salt: &[u8],
    _iterations: u32,
    _dk_len: usize,
) -> CryptoResult<Vec<u8>> {
    todo!("F(P, S, c, i) = T_1 ⊕ ... ⊕ T_c; concatenate blocks then truncate to dk_len")
}
