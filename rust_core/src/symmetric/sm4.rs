//! SM4 block cipher (GB/T 32907-2016).
//!
//! This is a direct implementation of the 128-bit block / 128-bit key
//! construction: FK/CK key expansion, 32 nonlinear rounds, and reverse round
//! keys for decryption.

use crate::error::{CryptoError, CryptoResult};
use crate::modes::{cbc, ctr, ecb, gcm, Padding};
use crate::traits::SymmetricCipher;

/// SM4 block size in bytes.
pub const BLOCK_SIZE: usize = 16;
/// SM4 key size in bytes.
pub const KEY_SIZE: usize = 16;

const SBOX: [u8; 256] = [
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c,
    0x05, 0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86,
    0x06, 0x99, 0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed,
    0xcf, 0xac, 0x62, 0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa,
    0x75, 0x8f, 0x3f, 0xa6, 0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c,
    0x19, 0xe6, 0x85, 0x4f, 0xa8, 0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb,
    0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35, 0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25,
    0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87, 0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52,
    0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e, 0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38,
    0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1, 0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34,
    0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3, 0x1d, 0xf6, 0xe2, 0x2e, 0x82,
    0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f, 0xd5, 0xdb, 0x37, 0x45,
    0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51, 0x8d, 0x1b, 0xaf,
    0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8, 0x0a, 0xc1,
    0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0, 0x89,
    0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39,
    0x48,
];

const FK: [u32; 4] = [0xa3b1_bac6, 0x56aa_3350, 0x677d_9197, 0xb270_22dc];
const CK: [u32; 32] = [
    0x0007_0e15, 0x1c23_2a31, 0x383f_464d, 0x545b_6269, 0x7077_7e85, 0x8c93_9aa1,
    0xa8af_b6bd, 0xc4cb_d2d9, 0xe0e7_eef5, 0xfc03_0a11, 0x181f_262d, 0x343b_4249,
    0x5057_5e65, 0x6c73_7a81, 0x888f_969d, 0xa4ab_b2b9, 0xc0c7_ced5, 0xdce3_eaf1,
    0xf8ff_060d, 0x141b_2229, 0x3037_3e45, 0x4c53_5a61, 0x686f_767d, 0x848b_9299,
    0xa0a7_aeb5, 0xbcc3_cad1, 0xd8df_e6ed, 0xf4fb_0209, 0x1017_1e25, 0x2c33_3a41,
    0x484f_565d, 0x646b_7279,
];

/// SM4 cipher with expanded round keys cached.
#[derive(Clone)]
pub struct Sm4 {
    /// 32 round keys, each a u32.
    round_keys: [u32; 32],
}

impl Sm4 {
    /// Multi-block encrypt with mode + padding.
    pub fn encrypt_mode(
        &self,
        plaintext: &[u8],
        mode: &str,
        iv: Option<&[u8]>,
        aad: Option<&[u8]>,
        padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        let padding = Padding::parse(padding)?;
        match mode.to_ascii_uppercase().as_str() {
            "ECB" => ecb::encrypt(self, plaintext, padding),
            "CBC" => cbc::encrypt(self, plaintext, required_iv(iv, BLOCK_SIZE)?, padding),
            "CTR" => ctr::xor_keystream(self, plaintext, required_iv(iv, BLOCK_SIZE)?, 0),
            "GCM" => gcm::encrypt(self, plaintext, required_iv(iv, 12)?, aad.unwrap_or(&[])),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported SM4 mode: {other}"
            ))),
        }
    }

    /// Multi-block decrypt with mode + padding.
    pub fn decrypt_mode(
        &self,
        ciphertext: &[u8],
        mode: &str,
        iv: Option<&[u8]>,
        aad: Option<&[u8]>,
        padding: &str,
    ) -> CryptoResult<Vec<u8>> {
        let padding = Padding::parse(padding)?;
        match mode.to_ascii_uppercase().as_str() {
            "ECB" => ecb::decrypt(self, ciphertext, padding),
            "CBC" => cbc::decrypt(self, ciphertext, required_iv(iv, BLOCK_SIZE)?, padding),
            "CTR" => ctr::xor_keystream(self, ciphertext, required_iv(iv, BLOCK_SIZE)?, 0),
            "GCM" => gcm::decrypt(self, ciphertext, required_iv(iv, 12)?, aad.unwrap_or(&[])),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported SM4 mode: {other}"
            ))),
        }
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

        let mut k = [0u32; 36];
        for i in 0..4 {
            k[i] = u32::from_be_bytes([
                key[i * 4],
                key[i * 4 + 1],
                key[i * 4 + 2],
                key[i * 4 + 3],
            ]) ^ FK[i];
        }

        let mut round_keys = [0u32; 32];
        for i in 0..32 {
            k[i + 4] = k[i] ^ t_key(k[i + 1] ^ k[i + 2] ^ k[i + 3] ^ CK[i]);
            round_keys[i] = k[i + 4];
        }
        Ok(Self { round_keys })
    }

    fn encrypt_block(&self, block: &mut [u8]) -> CryptoResult<()> {
        if block.len() != BLOCK_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "SM4 block must be {BLOCK_SIZE} bytes, got {}",
                block.len()
            )));
        }
        crypt_block(block, self.round_keys.iter().copied())
    }

    fn decrypt_block(&self, block: &mut [u8]) -> CryptoResult<()> {
        if block.len() != BLOCK_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "SM4 block must be {BLOCK_SIZE} bytes, got {}",
                block.len()
            )));
        }
        crypt_block(block, self.round_keys.iter().rev().copied())
    }
}

fn crypt_block(block: &mut [u8], round_keys: impl Iterator<Item = u32>) -> CryptoResult<()> {
    let mut x = [0u32; 36];
    for i in 0..4 {
        x[i] = u32::from_be_bytes([
            block[i * 4],
            block[i * 4 + 1],
            block[i * 4 + 2],
            block[i * 4 + 3],
        ]);
    }
    for (i, rk) in round_keys.enumerate() {
        x[i + 4] = x[i] ^ t_round(x[i + 1] ^ x[i + 2] ^ x[i + 3] ^ rk);
    }
    let out = [x[35], x[34], x[33], x[32]];
    for (i, word) in out.iter().enumerate() {
        block[i * 4..i * 4 + 4].copy_from_slice(&word.to_be_bytes());
    }
    Ok(())
}

fn tau(x: u32) -> u32 {
    let bytes = x.to_be_bytes();
    u32::from_be_bytes([
        SBOX[bytes[0] as usize],
        SBOX[bytes[1] as usize],
        SBOX[bytes[2] as usize],
        SBOX[bytes[3] as usize],
    ])
}

fn t_round(x: u32) -> u32 {
    let b = tau(x);
    b ^ b.rotate_left(2) ^ b.rotate_left(10) ^ b.rotate_left(18) ^ b.rotate_left(24)
}

fn t_key(x: u32) -> u32 {
    let b = tau(x);
    b ^ b.rotate_left(13) ^ b.rotate_left(23)
}

fn required_iv(iv: Option<&[u8]>, expected: usize) -> CryptoResult<&[u8]> {
    let iv = iv.ok_or(CryptoError::InvalidIvLength {
        expected,
        actual: 0,
    })?;
    if iv.len() != expected {
        return Err(CryptoError::InvalidIvLength {
            expected,
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
    let cipher = Sm4::new(key)?;
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
    let cipher = Sm4::new(key)?;
    cipher.decrypt_mode(ciphertext, mode, iv, aad, padding)
}

#[cfg(test)]
mod tests {
    use super::Sm4;
    use crate::traits::SymmetricCipher;

    fn hx(s: &str) -> Vec<u8> {
        hex::decode(s).expect("valid hex")
    }

    #[test]
    fn gb_t_32907_appendix_a_single_block() {
        let key = hx("0123456789abcdeffedcba9876543210");
        let mut block = hx("0123456789abcdeffedcba9876543210");
        let cipher = Sm4::new(&key).expect("valid key");
        cipher.encrypt_block(&mut block).expect("encrypt");
        assert_eq!(block, hx("681edf34d206965e86b3e94f536e4246"));
        cipher.decrypt_block(&mut block).expect("decrypt");
        assert_eq!(block, hx("0123456789abcdeffedcba9876543210"));
    }

    #[cfg(feature = "slow-tests")]
    #[test]
    fn gb_t_32907_appendix_a_million_iterations() {
        let key = hx("0123456789abcdeffedcba9876543210");
        let mut block = hx("0123456789abcdeffedcba9876543210");
        let cipher = Sm4::new(&key).expect("valid key");
        for _ in 0..1_000_000 {
            cipher.encrypt_block(&mut block).expect("encrypt");
        }
        assert_eq!(block, hx("595298c7c6fd271f0402f804c33d3f66"));
    }
}
