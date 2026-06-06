//! SHA-1 (FIPS 180-4 §6.1). Educational use only — SHA-1 is
//! cryptographically broken and must not be used for new signatures.

use crate::error::{CryptoError, CryptoResult};
use crate::traits::HashAlgorithm;

/// Digest length in bytes (160 bits).
pub const DIGEST_SIZE: usize = 20;
/// Internal block size in bytes (512 bits).
pub const BLOCK_SIZE: usize = 64;

const IV: [u32; 5] = [
    0x6745_2301,
    0xefcd_ab89,
    0x98ba_dcfe,
    0x1032_5476,
    0xc3d2_e1f0,
];

/// SHA-1 streaming hasher per FIPS 180-4 §6.1.
#[derive(Debug, Clone)]
pub struct Sha1 {
    state: [u32; 5],
    buffer: [u8; BLOCK_SIZE],
    buffer_len: usize,
    length_bytes: u64,
}

impl Default for Sha1 {
    fn default() -> Self {
        Self::new()
    }
}

impl Sha1 {
    /// Create a new SHA-1 streaming hasher.
    pub fn new() -> Self {
        Self {
            state: IV,
            buffer: [0u8; BLOCK_SIZE],
            buffer_len: 0,
            length_bytes: 0,
        }
    }

    /// Absorb bytes into the SHA-1 state.
    pub fn update(&mut self, data: &[u8]) {
        self.length_bytes = self.length_bytes.wrapping_add(data.len() as u64);
        let mut input = data;

        if self.buffer_len > 0 {
            let take = (BLOCK_SIZE - self.buffer_len).min(input.len());
            self.buffer[self.buffer_len..self.buffer_len + take].copy_from_slice(&input[..take]);
            self.buffer_len += take;
            input = &input[take..];
            if self.buffer_len == BLOCK_SIZE {
                compress(&mut self.state, &self.buffer);
                self.buffer_len = 0;
            }
        }

        let mut chunks = input.chunks_exact(BLOCK_SIZE);
        for chunk in &mut chunks {
            compress(&mut self.state, chunk);
        }

        let rem = chunks.remainder();
        if !rem.is_empty() {
            self.buffer[..rem.len()].copy_from_slice(rem);
            self.buffer_len = rem.len();
        }
    }

    /// Finalize SHA-1 and return the 20-byte digest.
    pub fn finalize(self) -> [u8; DIGEST_SIZE] {
        finalize_state(self.state, self.buffer, self.buffer_len, self.length_bytes)
    }
}

impl HashAlgorithm for Sha1 {
    const DIGEST_SIZE: usize = DIGEST_SIZE;
    const BLOCK_SIZE: usize = BLOCK_SIZE;

    fn reset(&mut self) {
        *self = Self::new();
    }

    fn update(&mut self, data: &[u8]) {
        Sha1::update(self, data);
    }

    fn finalize_into(self, out: &mut [u8]) -> CryptoResult<()> {
        if out.len() != Self::DIGEST_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "SHA-1 output buffer must be {} bytes, got {}",
                Self::DIGEST_SIZE,
                out.len()
            )));
        }
        out.copy_from_slice(&self.finalize());
        Ok(())
    }
}

/// One-shot SHA-1 digest per FIPS 180-4 §6.1.
pub fn sha1(data: &[u8]) -> [u8; DIGEST_SIZE] {
    let mut hasher = Sha1::new();
    hasher.update(data);
    hasher.finalize()
}

/// Backwards-compatible one-shot SHA-1 alias used by the FFI layer.
pub fn digest(data: &[u8]) -> [u8; DIGEST_SIZE] {
    sha1(data)
}

fn finalize_state(
    mut state: [u32; 5],
    mut buffer: [u8; BLOCK_SIZE],
    mut buffer_len: usize,
    length_bytes: u64,
) -> [u8; DIGEST_SIZE] {
    let bit_len = length_bytes.wrapping_mul(8);
    buffer[buffer_len] = 0x80;
    buffer_len += 1;

    if buffer_len > 56 {
        buffer[buffer_len..].fill(0);
        compress(&mut state, &buffer);
        buffer = [0u8; BLOCK_SIZE];
        buffer_len = 0;
    }

    buffer[buffer_len..56].fill(0);
    buffer[56..64].copy_from_slice(&bit_len.to_be_bytes());
    compress(&mut state, &buffer);

    let mut out = [0u8; DIGEST_SIZE];
    for (i, word) in state.iter().enumerate() {
        out[i * 4..(i + 1) * 4].copy_from_slice(&word.to_be_bytes());
    }
    out
}

fn compress(state: &mut [u32; 5], block: &[u8]) {
    let mut w = [0u32; 80];
    for (i, chunk) in block.chunks_exact(4).take(16).enumerate() {
        w[i] = u32::from_be_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]);
    }
    for i in 16..80 {
        w[i] = (w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]).rotate_left(1);
    }

    let mut a = state[0];
    let mut b = state[1];
    let mut c = state[2];
    let mut d = state[3];
    let mut e = state[4];

    for (t, word) in w.iter().enumerate() {
        let (f, k) = match t {
            0..=19 => (((b & c) | ((!b) & d)), 0x5a82_7999),
            20..=39 => (b ^ c ^ d, 0x6ed9_eba1),
            40..=59 => (((b & c) | (b & d) | (c & d)), 0x8f1b_bcdc),
            _ => (b ^ c ^ d, 0xca62_c1d6),
        };
        let temp = a
            .rotate_left(5)
            .wrapping_add(f)
            .wrapping_add(e)
            .wrapping_add(k)
            .wrapping_add(*word);
        e = d;
        d = c;
        c = b.rotate_left(30);
        b = a;
        a = temp;
    }

    state[0] = state[0].wrapping_add(a);
    state[1] = state[1].wrapping_add(b);
    state[2] = state[2].wrapping_add(c);
    state[3] = state[3].wrapping_add(d);
    state[4] = state[4].wrapping_add(e);
}

#[cfg(test)]
mod tests {
    use super::{sha1, Sha1};
    use rand::rngs::StdRng;
    use rand::{RngCore, SeedableRng};

    const LONG_448: &[u8] = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";

    #[test]
    fn fips_180_4_classic_vectors() {
        assert_eq!(
            hex::encode(sha1(b"")),
            "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        );
        assert_eq!(
            hex::encode(sha1(b"abc")),
            "a9993e364706816aba3e25717850c26c9cd0d89d"
        );
        assert_eq!(
            hex::encode(sha1(LONG_448)),
            "84983e441c3bd26ebaae4aa1f95129e5e54670f1"
        );
    }

    #[test]
    fn million_a_vector() {
        let input = vec![b'a'; 1_000_000];
        assert_eq!(
            hex::encode(sha1(&input)),
            "34aa973cd4c4daa4f61eeb2bdbad27316534016f"
        );
    }

    #[test]
    fn streaming_matches_one_shot_for_random_1mb() {
        let mut rng = StdRng::seed_from_u64(0x51a1);
        let mut input = vec![0u8; 1024 * 1024];
        rng.fill_bytes(&mut input);

        let one_shot = sha1(&input);
        let mut streaming = Sha1::new();
        for chunk in input.chunks(4093) {
            streaming.update(chunk);
        }
        assert_eq!(streaming.finalize(), one_shot);
    }
}
