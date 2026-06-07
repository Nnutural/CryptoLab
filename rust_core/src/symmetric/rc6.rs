//! RC6-32/20/16 (Rivest et al., 1998).
//!
//! Parameters are fixed to the AES-candidate profile used in the paper:
//! four 32-bit words per block, 20 rounds, and 128-bit keys for this project.

use crate::error::{CryptoError, CryptoResult};
use crate::modes::{cbc, ecb, Padding};
use crate::traits::SymmetricCipher;

/// RC6 block size in bytes.
pub const BLOCK_SIZE: usize = 16;
/// Project-supported RC6 key size in bytes.
pub const KEY_SIZE: usize = 16;
/// Number of rounds.
pub const ROUNDS: usize = 20;

const P32: u32 = 0xb7e1_5163;
const Q32: u32 = 0x9e37_79b9;
const LG_W: u32 = 5;
const SUBKEYS: usize = 2 * ROUNDS + 4;

/// RC6 cipher with expanded round subkeys.
#[derive(Clone)]
pub struct Rc6 {
    /// Expanded subkey table S[0..=2r+3].
    round_keys: Vec<u32>,
}

impl Rc6 {
    /// Multi-block encrypt with mode + padding.
    pub fn encrypt_mode(
        &self,
        plaintext: &[u8],
        mode: &str,
        iv: Option<&[u8]>,
        _aad: Option<&[u8]>,
        padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        let padding = Padding::parse(padding)?;
        match mode.to_ascii_uppercase().as_str() {
            "ECB" => ecb::encrypt(self, plaintext, padding),
            "CBC" => cbc::encrypt(self, plaintext, required_iv(iv)?, padding),
            "CTR" | "GCM" => Err(CryptoError::InvalidParameter(
                "RC6 currently supports ECB and CBC only".to_string(),
            )),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported RC6 mode: {other}"
            ))),
        }
    }

    /// Multi-block decrypt with mode + padding.
    pub fn decrypt_mode(
        &self,
        ciphertext: &[u8],
        mode: &str,
        iv: Option<&[u8]>,
        _aad: Option<&[u8]>,
        padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        let padding = Padding::parse(padding)?;
        match mode.to_ascii_uppercase().as_str() {
            "ECB" => ecb::decrypt(self, ciphertext, padding),
            "CBC" => cbc::decrypt(self, ciphertext, required_iv(iv)?, padding),
            "CTR" | "GCM" => Err(CryptoError::InvalidParameter(
                "RC6 currently supports ECB and CBC only".to_string(),
            )),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported RC6 mode: {other}"
            ))),
        }
    }
}

impl SymmetricCipher for Rc6 {
    const BLOCK_SIZE: usize = BLOCK_SIZE;
    const KEY_SIZE: usize = KEY_SIZE;

    fn new(key: &[u8]) -> CryptoResult<Self> {
        if key.len() != KEY_SIZE {
            return Err(CryptoError::InvalidKeyLength {
                expected: KEY_SIZE,
                actual: key.len(),
            });
        }

        let c = key.len() / 4;
        let mut l = vec![0u32; c];
        for (i, chunk) in key.chunks(4).enumerate() {
            l[i] = u32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]);
        }

        let mut s = vec![0u32; SUBKEYS];
        s[0] = P32;
        for i in 1..SUBKEYS {
            s[i] = s[i - 1].wrapping_add(Q32);
        }

        let mut a = 0u32;
        let mut b = 0u32;
        let mut i = 0usize;
        let mut j = 0usize;
        for _ in 0..(3 * SUBKEYS.max(c)) {
            s[i] = s[i].wrapping_add(a).wrapping_add(b).rotate_left(3);
            a = s[i];
            l[j] = l[j]
                .wrapping_add(a)
                .wrapping_add(b)
                .rotate_left(a.wrapping_add(b) & 31);
            b = l[j];
            i = (i + 1) % SUBKEYS;
            j = (j + 1) % c;
        }

        Ok(Self { round_keys: s })
    }

    fn encrypt_block(&self, block: &mut [u8]) -> CryptoResult<()> {
        if block.len() != BLOCK_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "RC6 block must be {BLOCK_SIZE} bytes, got {}",
                block.len()
            )));
        }

        let (mut a, mut b, mut c, mut d) = read_words(block);
        b = b.wrapping_add(self.round_keys[0]);
        d = d.wrapping_add(self.round_keys[1]);

        for i in 1..=ROUNDS {
            let t = b
                .wrapping_mul(b.wrapping_mul(2).wrapping_add(1))
                .rotate_left(LG_W);
            let u = d
                .wrapping_mul(d.wrapping_mul(2).wrapping_add(1))
                .rotate_left(LG_W);
            a = (a ^ t)
                .rotate_left(u & 31)
                .wrapping_add(self.round_keys[2 * i]);
            c = (c ^ u)
                .rotate_left(t & 31)
                .wrapping_add(self.round_keys[2 * i + 1]);
            let old_a = a;
            a = b;
            b = c;
            c = d;
            d = old_a;
        }

        a = a.wrapping_add(self.round_keys[2 * ROUNDS + 2]);
        c = c.wrapping_add(self.round_keys[2 * ROUNDS + 3]);
        write_words(block, a, b, c, d);
        Ok(())
    }

    fn decrypt_block(&self, block: &mut [u8]) -> CryptoResult<()> {
        if block.len() != BLOCK_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "RC6 block must be {BLOCK_SIZE} bytes, got {}",
                block.len()
            )));
        }

        let (mut a, mut b, mut c, mut d) = read_words(block);
        c = c.wrapping_sub(self.round_keys[2 * ROUNDS + 3]);
        a = a.wrapping_sub(self.round_keys[2 * ROUNDS + 2]);

        for i in (1..=ROUNDS).rev() {
            let old_d = d;
            d = c;
            c = b;
            b = a;
            a = old_d;

            let u = d
                .wrapping_mul(d.wrapping_mul(2).wrapping_add(1))
                .rotate_left(LG_W);
            let t = b
                .wrapping_mul(b.wrapping_mul(2).wrapping_add(1))
                .rotate_left(LG_W);
            c = c
                .wrapping_sub(self.round_keys[2 * i + 1])
                .rotate_right(t & 31)
                ^ u;
            a = a
                .wrapping_sub(self.round_keys[2 * i])
                .rotate_right(u & 31)
                ^ t;
        }

        d = d.wrapping_sub(self.round_keys[1]);
        b = b.wrapping_sub(self.round_keys[0]);
        write_words(block, a, b, c, d);
        Ok(())
    }
}

fn read_words(block: &[u8]) -> (u32, u32, u32, u32) {
    (
        u32::from_le_bytes([block[0], block[1], block[2], block[3]]),
        u32::from_le_bytes([block[4], block[5], block[6], block[7]]),
        u32::from_le_bytes([block[8], block[9], block[10], block[11]]),
        u32::from_le_bytes([block[12], block[13], block[14], block[15]]),
    )
}

fn write_words(block: &mut [u8], a: u32, b: u32, c: u32, d: u32) {
    block[0..4].copy_from_slice(&a.to_le_bytes());
    block[4..8].copy_from_slice(&b.to_le_bytes());
    block[8..12].copy_from_slice(&c.to_le_bytes());
    block[12..16].copy_from_slice(&d.to_le_bytes());
}

fn required_iv(iv: Option<&[u8]>) -> CryptoResult<&[u8]> {
    let iv = iv.ok_or(CryptoError::InvalidIvLength {
        expected: BLOCK_SIZE,
        actual: 0,
    })?;
    if iv.len() != BLOCK_SIZE {
        return Err(CryptoError::InvalidIvLength {
            expected: BLOCK_SIZE,
            actual: iv.len(),
        });
    }
    Ok(iv)
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
    let cipher = Rc6::new(key)?;
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
    let cipher = Rc6::new(key)?;
    cipher.decrypt_mode(ciphertext, mode, iv, aad, padding)
}

#[cfg(test)]
mod tests {
    use super::Rc6;
    use crate::traits::SymmetricCipher;

    fn hx(s: &str) -> Vec<u8> {
        hex::decode(s).expect("valid hex")
    }

    #[test]
    fn rc6_paper_appendix_b_zero_vector() {
        let key = [0u8; 16];
        let mut block = [0u8; 16];
        let cipher = Rc6::new(&key).expect("valid key");
        cipher.encrypt_block(&mut block).expect("encrypt");
        assert_eq!(block.to_vec(), hx("8fc3a53656b1f778c129df4e9848a41e"));
        cipher.decrypt_block(&mut block).expect("decrypt");
        assert_eq!(block, [0u8; 16]);
    }
}
