//! ECB — Electronic Codebook (NIST SP 800-38A §6.1).
//!
//! Caution: ECB leaks plaintext patterns. The CryptoLab attack-demo module
//! (`/api/v1/demos/ecb_image_leak`) exists specifically to illustrate this.

use crate::error::{CryptoError, CryptoResult};
use crate::modes::Padding;
use crate::traits::SymmetricCipher;

/// Encrypt `plaintext` block-by-block with `cipher`, applying `padding`.
pub fn encrypt<C: SymmetricCipher>(
    cipher: &C,
    plaintext: &[u8],
    padding: Padding,
) -> CryptoResult<Vec<u8>> {
    let mut out = plaintext.to_vec();
    padding.pad(&mut out, C::BLOCK_SIZE)?;
    for block in out.chunks_exact_mut(C::BLOCK_SIZE) {
        cipher.encrypt_block(block)?;
    }
    Ok(out)
}

/// Inverse of [`encrypt`].
pub fn decrypt<C: SymmetricCipher>(
    cipher: &C,
    ciphertext: &[u8],
    padding: Padding,
) -> CryptoResult<Vec<u8>> {
    if ciphertext.len() % C::BLOCK_SIZE != 0 {
        return Err(CryptoError::InvalidInputLength(format!(
            "ECB ciphertext length {} is not a multiple of block size {}",
            ciphertext.len(),
            C::BLOCK_SIZE
        )));
    }
    let mut out = ciphertext.to_vec();
    for block in out.chunks_exact_mut(C::BLOCK_SIZE) {
        cipher.decrypt_block(block)?;
    }
    padding.unpad(&mut out, C::BLOCK_SIZE)?;
    Ok(out)
}
