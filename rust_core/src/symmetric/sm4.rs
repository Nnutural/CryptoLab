//! SM4 (GB/T 32907-2016 / GM/T 0002-2012).
//!
//! 128-bit block, 128-bit key, 32-round non-linear iteration + reversed
//! permutation. S-Box is the official OSCCA value.

use crate::error::{CryptoError, CryptoResult};
use crate::traits::SymmetricCipher;

/// SM4 block size in bytes.
pub const BLOCK_SIZE: usize = 16;
/// SM4 key size in bytes.
pub const KEY_SIZE: usize = 16;

/// SM4 cipher with expanded round keys cached.
pub struct Sm4 {
    /// 32 round keys, each a u32.
    _round_keys: [u32; 32],
}

impl Sm4 {
    /// Multi-block encrypt with mode + padding.
    pub fn encrypt_mode(
        &self,
        _plaintext: &[u8],
        _mode: &str,
        _iv: Option<&[u8]>,
        _padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        todo!("dispatch to crate::modes")
    }

    /// Multi-block decrypt with mode + padding.
    pub fn decrypt_mode(
        &self,
        _ciphertext: &[u8],
        _mode: &str,
        _iv: Option<&[u8]>,
        _padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        todo!("dispatch to crate::modes")
    }
}

impl SymmetricCipher for Sm4 {
    const BLOCK_SIZE: usize = BLOCK_SIZE;
    const KEY_SIZE: usize = KEY_SIZE;

    fn new(key: &[u8]) -> CryptoResult<Self> {
        if key.len() != KEY_SIZE {
            return Err(CryptoError::InvalidKeyLength {
                expected: KEY_SIZE,
                actual: key.len(),
            });
        }
        let _ = key;
        todo!("Key expansion using system parameter FK and constant parameter CK")
    }

    fn encrypt_block(&self, _block: &mut [u8]) -> CryptoResult<()> {
        todo!("32-round non-linear iteration; T transform = L(τ(.))")
    }

    fn decrypt_block(&self, _block: &mut [u8]) -> CryptoResult<()> {
        todo!("Same as encrypt but with reversed round keys")
    }
}

/// Entry point used by the FFI layer.
pub fn encrypt_dispatch(
    plaintext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    padding: &str,
) -> CryptoResult<Vec<u8>> {
    let cipher = Sm4::new(key)?;
    cipher.encrypt_mode(plaintext, mode, iv, padding)
}

/// Entry point used by the FFI layer.
pub fn decrypt_dispatch(
    ciphertext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    padding: &str,
) -> CryptoResult<Vec<u8>> {
    let cipher = Sm4::new(key)?;
    cipher.decrypt_mode(ciphertext, mode, iv, padding)
}

#[cfg(test)]
mod tests {
    // GB/T 32907-2016 Appendix A test vectors live here once Sm4 is implemented.
}
