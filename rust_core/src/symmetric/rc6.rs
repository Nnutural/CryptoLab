//! RC6-32/20/16 (Rivest et al., 1998).
//!
//! Parameters w=32, r=20, b=16. Operates on four 32-bit words per block
//! (128-bit block size). Round function: data-dependent rotations + integer
//! multiplication.

use crate::error::{CryptoError, CryptoResult};
use crate::traits::SymmetricCipher;

/// RC6 block size in bytes (4 × 32-bit words).
pub const BLOCK_SIZE: usize = 16;
/// Default key size in bytes (128-bit).
pub const KEY_SIZE: usize = 16;
/// Number of rounds (paper-recommended 20).
pub const ROUNDS: usize = 20;

/// RC6 cipher with expanded round subkeys.
pub struct Rc6 {
    /// Expanded subkey table S[0..=2r+3].
    _round_keys: Vec<u32>,
}

impl Rc6 {
    /// Multi-block encrypt with mode + padding.
    pub fn encrypt_mode(
        &self,
        _plaintext: &[u8],
        _mode: &str,
        _iv: Option<&[u8]>,
        _padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        todo!("dispatch to crate::modes (ECB / CBC only — CTR/GCM optional)")
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

impl SymmetricCipher for Rc6 {
    const BLOCK_SIZE: usize = BLOCK_SIZE;
    const KEY_SIZE: usize = KEY_SIZE;

    fn new(key: &[u8]) -> CryptoResult<Self> {
        if !matches!(key.len(), 16 | 24 | 32) {
            return Err(CryptoError::InvalidKeyLength {
                expected: 16,
                actual: key.len(),
            });
        }
        let _ = key;
        todo!("key schedule: P32/Q32 magic constants, 3·max(b/4, 2r+4) iterations")
    }

    fn encrypt_block(&self, _block: &mut [u8]) -> CryptoResult<()> {
        todo!("RC6 forward round function")
    }

    fn decrypt_block(&self, _block: &mut [u8]) -> CryptoResult<()> {
        todo!("RC6 inverse round function")
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
    let cipher = Rc6::new(key)?;
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
    let cipher = Rc6::new(key)?;
    cipher.decrypt_mode(ciphertext, mode, iv, padding)
}

#[cfg(test)]
mod tests {
    // RC6 paper Appendix test vectors live here once implemented.
}
