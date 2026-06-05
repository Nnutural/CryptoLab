//! AES-128 / 192 / 256 (NIST FIPS 197).
//!
//! Hand-written SPN cipher. Sub-stages: SubBytes (S-Box), ShiftRows,
//! MixColumns (GF(2^8)), AddRoundKey, KeyExpansion. Constant-time table
//! lookups are required for production use (avoid cache-timing attacks).

use crate::error::{CryptoError, CryptoResult};
use crate::traits::{EncryptionTrace, SymmetricCipher};

/// AES block size in bytes (independent of key length).
pub const BLOCK_SIZE: usize = 16;

/// Supported key sizes in bytes (128 / 192 / 256 bits).
pub const KEY_SIZES: [usize; 3] = [16, 24, 32];

/// AES cipher with expanded round keys cached.
pub struct Aes {
    /// Expanded round keys, layout: `(Nr + 1) * BLOCK_SIZE` bytes.
    _round_keys: Vec<u8>,
    /// Number of rounds (10 for AES-128, 12 for AES-192, 14 for AES-256).
    _rounds: usize,
}

impl Aes {
    /// Encrypt arbitrary-length plaintext under the chosen mode + padding.
    pub fn encrypt_mode(
        &self,
        _plaintext: &[u8],
        _mode: &str,
        _iv: Option<&[u8]>,
        _aad: Option<&[u8]>,
        _padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        todo!("dispatch to crate::modes::{ecb, cbc, ctr, gcm} using self as block primitive")
    }

    /// Decrypt arbitrary-length ciphertext under the chosen mode + padding.
    pub fn decrypt_mode(
        &self,
        _ciphertext: &[u8],
        _mode: &str,
        _iv: Option<&[u8]>,
        _aad: Option<&[u8]>,
        _padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        todo!("inverse of encrypt_mode")
    }
}

impl SymmetricCipher for Aes {
    const BLOCK_SIZE: usize = BLOCK_SIZE;
    const KEY_SIZE: usize = 32; // documented in KEY_SIZES; placeholder

    fn new(key: &[u8]) -> CryptoResult<Self> {
        if !KEY_SIZES.contains(&key.len()) {
            return Err(CryptoError::InvalidKeyLength {
                expected: 32,
                actual: key.len(),
            });
        }
        let _ = key;
        todo!("KeyExpansion (FIPS 197 §5.2) producing (Nr + 1) round keys")
    }

    fn encrypt_block(&self, _block: &mut [u8]) -> CryptoResult<()> {
        todo!("AES forward cipher: AddRoundKey → 9/11/13 × [SubBytes,ShiftRows,MixColumns,AddRoundKey] → SubBytes,ShiftRows,AddRoundKey")
    }

    fn decrypt_block(&self, _block: &mut [u8]) -> CryptoResult<()> {
        todo!("AES inverse cipher (FIPS 197 §5.3)")
    }

    fn encrypt_with_trace(&self, _block: &mut [u8]) -> CryptoResult<EncryptionTrace> {
        todo!("emit per-round state snapshots for visualization")
    }
}

/// Entry point used by the FFI layer.
pub fn encrypt_dispatch(
    plaintext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    aad: Option<&[u8]>,
    padding: &str,
) -> CryptoResult<Vec<u8>> {
    let cipher = Aes::new(key)?;
    cipher.encrypt_mode(plaintext, mode, iv, aad, padding)
}

/// Entry point used by the FFI layer.
pub fn decrypt_dispatch(
    ciphertext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    aad: Option<&[u8]>,
    padding: &str,
) -> CryptoResult<Vec<u8>> {
    let cipher = Aes::new(key)?;
    cipher.decrypt_mode(ciphertext, mode, iv, aad, padding)
}

#[cfg(test)]
mod tests {
    // NIST SP 800-38A test vectors live here once Aes is implemented.
}
