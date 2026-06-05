//! GCM — Galois/Counter Mode (NIST SP 800-38D).
//!
//! Combines CTR confidentiality with GHASH-based authentication. Tag length
//! defaults to 128 bits; shorter tags are NOT supported by this impl to
//! avoid the SP 800-38D Appendix C edge cases.

use crate::error::CryptoResult;
use crate::traits::SymmetricCipher;

/// Authentication tag length in bytes.
pub const TAG_LEN: usize = 16;

/// AES-GCM encrypt. Returns `ciphertext || tag` concatenated.
pub fn encrypt<C: SymmetricCipher>(
    _cipher: &C,
    _plaintext: &[u8],
    _iv: &[u8],
    _aad: &[u8],
) -> CryptoResult<Vec<u8>> {
    todo!("derive H = E_K(0^128); J0 = (iv || 0x00000001) for 12-byte IV; CTR + GHASH")
}

/// AES-GCM decrypt. Verifies tag constant-time before returning plaintext.
pub fn decrypt<C: SymmetricCipher>(
    _cipher: &C,
    _ciphertext_with_tag: &[u8],
    _iv: &[u8],
    _aad: &[u8],
) -> CryptoResult<Vec<u8>> {
    todo!("split tag; recompute GHASH; subtle::ConstantTimeEq compare; CTR decrypt only on success")
}

/// GHASH over the field GF(2^128) with reduction polynomial x^128 + x^7 + x^2 + x + 1.
pub fn ghash(_h: &[u8; 16], _data: &[u8]) -> [u8; 16] {
    todo!("multiply each 128-bit block of data by H in GF(2^128), accumulating into Y")
}
