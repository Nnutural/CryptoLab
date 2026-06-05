//! SHA-1 (RFC 3174 / FIPS 180-4 §6.1). Educational use only — SHA-1 is
//! cryptographically broken (Shattered, 2017) and must not be used for new
//! signatures.

use crate::error::CryptoResult;
use crate::traits::HashAlgorithm;

/// Digest length in bytes (160 bits).
pub const DIGEST_SIZE: usize = 20;
/// Internal block size in bytes (512 bits).
pub const BLOCK_SIZE: usize = 64;

/// SHA-1 streaming hasher.
#[derive(Debug, Default, Clone)]
pub struct Sha1 {
    /// 5-word internal state (h0..h4).
    _state: [u32; 5],
    /// Buffered partial block.
    _buffer: Vec<u8>,
    /// Total bits processed (for length-encoding).
    _length: u64,
}

impl HashAlgorithm for Sha1 {
    const DIGEST_SIZE: usize = DIGEST_SIZE;
    const BLOCK_SIZE: usize = BLOCK_SIZE;

    fn reset(&mut self) {
        todo!("reset to SHA-1 initial state H0")
    }

    fn update(&mut self, _data: &[u8]) {
        todo!("buffer + process full 512-bit blocks via compression function")
    }

    fn finalize_into(self, _out: &mut [u8]) -> CryptoResult<()> {
        todo!("MD-padding + big-endian length encoding + final compression")
    }
}

/// One-shot SHA-1.
pub fn digest(_data: &[u8]) -> Vec<u8> {
    todo!("Sha1::digest convenience")
}
