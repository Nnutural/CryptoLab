//! ECB — Electronic Codebook (NIST SP 800-38A §6.1).
//!
//! Caution: ECB leaks plaintext patterns. The CryptoLab attack-demo module
//! (`/api/v1/demos/ecb_image_leak`) exists specifically to illustrate this.

use crate::error::CryptoResult;
use crate::modes::Padding;
use crate::traits::SymmetricCipher;

/// Encrypt `plaintext` block-by-block with `cipher`, applying `padding`.
pub fn encrypt<C: SymmetricCipher>(
    _cipher: &C,
    _plaintext: &[u8],
    _padding: Padding,
) -> CryptoResult<Vec<u8>> {
    todo!("pad → for each block: encrypt_block in place")
}

/// Inverse of [`encrypt`].
pub fn decrypt<C: SymmetricCipher>(
    _cipher: &C,
    _ciphertext: &[u8],
    _padding: Padding,
) -> CryptoResult<Vec<u8>> {
    todo!("for each block: decrypt_block in place → unpad")
}
