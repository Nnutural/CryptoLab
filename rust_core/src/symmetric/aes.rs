//! AES-128 / 192 / 256 (NIST FIPS 197).
//!
//! Hand-written SPN cipher. Sub-stages: SubBytes (S-Box), ShiftRows,
//! MixColumns (GF(2^8)), AddRoundKey, and KeyExpansion.

use crate::error::{CryptoError, CryptoResult};
use crate::modes::{cbc, ctr, ecb, gcm, Padding};
use crate::traits::{EncryptionTrace, RoundState, SymmetricCipher};
use serde::Serialize;
use std::time::Instant;

/// AES block size in bytes (independent of key length).
pub const BLOCK_SIZE: usize = 16;

/// Supported key sizes in bytes (128 / 192 / 256 bits).
pub const KEY_SIZES: [usize; 3] = [16, 24, 32];

/// AES single-block encryption trace for verbose teaching mode.
#[derive(Debug, Clone, Serialize)]
pub struct AesTrace {
    /// Key size in bits: 128 / 192 / 256.
    pub key_size_bits: usize,
    /// Number of AES rounds: 10 / 12 / 14.
    pub total_rounds: usize,
    /// Plaintext block as 32 lowercase hex chars.
    pub plaintext_hex: String,
    /// Round keys as `(total_rounds + 1)` 16-byte hex strings.
    pub round_keys_hex: Vec<String>,
    /// State after initial AddRoundKey[0].
    pub initial_add_round_key: String,
    /// Per-round snapshots after each AES step.
    pub rounds: Vec<AesRoundTrace>,
    /// Ciphertext block as 32 lowercase hex chars.
    pub ciphertext_hex: String,
    /// Best-effort timing measurements in nanoseconds.
    pub timings_ns: AesTimings,
}

/// One AES round's post-step states.
#[derive(Debug, Clone, Serialize)]
pub struct AesRoundTrace {
    /// 1-based round index.
    pub round_index: usize,
    /// State after SubBytes.
    pub after_sub_bytes: String,
    /// State after ShiftRows.
    pub after_shift_rows: String,
    /// State after MixColumns, omitted for the final round.
    pub after_mix_columns: Option<String>,
    /// State after AddRoundKey.
    pub after_add_round_key: String,
}

/// AES verbose timing data.
#[derive(Debug, Clone, Serialize)]
pub struct AesTimings {
    /// Key expansion time.
    pub key_expansion_ns: u64,
    /// Per-round encryption time, length equals `total_rounds`.
    pub per_round_ns: Vec<u64>,
    /// Total trace encryption time, including key expansion.
    pub total_ns: u64,
}

const S_BOX: [u8; 256] = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab,
    0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4,
    0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71,
    0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2,
    0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6,
    0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb,
    0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45,
    0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44,
    0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a,
    0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49,
    0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d,
    0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25,
    0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e,
    0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1,
    0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb,
    0x16,
];

const INV_S_BOX: [u8; 256] = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7,
    0xfb, 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde,
    0xe9, 0xcb, 0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42,
    0xfa, 0xc3, 0x4e, 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49,
    0x6d, 0x8b, 0xd1, 0x25, 0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c,
    0xcc, 0x5d, 0x65, 0xb6, 0x92, 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15,
    0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84, 0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7,
    0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06, 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02,
    0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b, 0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc,
    0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73, 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad,
    0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e, 0x47, 0xf1, 0x1a, 0x71, 0x1d,
    0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b, 0xfc, 0x56, 0x3e, 0x4b,
    0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4, 0x1f, 0xdd, 0xa8,
    0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f, 0x60, 0x51,
    0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef, 0xa0,
    0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c,
    0x7d,
];

const RCON: [u8; 15] = [
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d,
];

/// AES cipher with expanded round keys cached.
#[derive(Debug, Clone)]
pub struct Aes {
    /// Expanded round keys, layout: `(Nr + 1) * BLOCK_SIZE` bytes.
    round_keys: Vec<u8>,
    /// Number of rounds (10 for AES-128, 12 for AES-192, 14 for AES-256).
    rounds: usize,
}

impl Aes {
    /// Encrypt arbitrary-length plaintext under the chosen mode + padding.
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
            "CBC" => cbc::encrypt(self, plaintext, required_iv(iv)?, padding),
            "CTR" => ctr::xor_keystream(self, plaintext, required_iv(iv)?, 0),
            "GCM" => gcm::encrypt(self, plaintext, required_iv(iv)?, aad.unwrap_or(&[])),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported AES mode: {other}"
            ))),
        }
    }

    /// Decrypt arbitrary-length ciphertext under the chosen mode + padding.
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
            "CBC" => cbc::decrypt(self, ciphertext, required_iv(iv)?, padding),
            "CTR" => ctr::xor_keystream(self, ciphertext, required_iv(iv)?, 0),
            "GCM" => gcm::decrypt(self, ciphertext, required_iv(iv)?, aad.unwrap_or(&[])),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported AES mode: {other}"
            ))),
        }
    }
}

impl SymmetricCipher for Aes {
    const BLOCK_SIZE: usize = BLOCK_SIZE;
    const KEY_SIZE: usize = 32;

    fn new(key: &[u8]) -> CryptoResult<Self> {
        if !KEY_SIZES.contains(&key.len()) {
            return Err(CryptoError::InvalidKeyLength {
                expected: 32,
                actual: key.len(),
            });
        }
        let nk = key.len() / 4;
        let rounds = nk + 6;
        Ok(Self {
            round_keys: expand_key(key, nk, rounds),
            rounds,
        })
    }

    fn encrypt_block(&self, block: &mut [u8]) -> CryptoResult<()> {
        if block.len() != BLOCK_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "AES block must be 16 bytes, got {}",
                block.len()
            )));
        }
        let mut state = [0u8; BLOCK_SIZE];
        state.copy_from_slice(block);

        add_round_key(&mut state, self.round_key(0));
        for round in 1..self.rounds {
            sub_bytes(&mut state);
            shift_rows(&mut state);
            mix_columns(&mut state);
            add_round_key(&mut state, self.round_key(round));
        }
        sub_bytes(&mut state);
        shift_rows(&mut state);
        add_round_key(&mut state, self.round_key(self.rounds));

        block.copy_from_slice(&state);
        Ok(())
    }

    fn decrypt_block(&self, block: &mut [u8]) -> CryptoResult<()> {
        if block.len() != BLOCK_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "AES block must be 16 bytes, got {}",
                block.len()
            )));
        }
        let mut state = [0u8; BLOCK_SIZE];
        state.copy_from_slice(block);

        add_round_key(&mut state, self.round_key(self.rounds));
        for round in (1..self.rounds).rev() {
            inv_shift_rows(&mut state);
            inv_sub_bytes(&mut state);
            add_round_key(&mut state, self.round_key(round));
            inv_mix_columns(&mut state);
        }
        inv_shift_rows(&mut state);
        inv_sub_bytes(&mut state);
        add_round_key(&mut state, self.round_key(0));

        block.copy_from_slice(&state);
        Ok(())
    }

    fn encrypt_with_trace(&self, block: &mut [u8]) -> CryptoResult<EncryptionTrace> {
        self.encrypt_block(block)?;
        Ok(EncryptionTrace {
            rounds: vec![RoundState {
                round: self.rounds,
                state: block.to_vec(),
                note: "after final AddRoundKey",
            }],
            round_keys: self.round_keys.chunks(BLOCK_SIZE).map(|k| k.to_vec()).collect(),
            timings_ns: Vec::new(),
        })
    }
}

impl Aes {
    fn round_key(&self, round: usize) -> &[u8] {
        let start = round * BLOCK_SIZE;
        &self.round_keys[start..start + BLOCK_SIZE]
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

/// Encrypt one AES block and capture every intermediate state for verbose mode.
pub fn encrypt_block_with_trace(
    plaintext: &[u8; BLOCK_SIZE],
    key: &[u8],
) -> CryptoResult<(Vec<u8>, AesTrace)> {
    let total_start = Instant::now();
    let key_start = Instant::now();
    let cipher = Aes::new(key)?;
    let key_expansion_ns = nanos_u64(key_start.elapsed().as_nanos());

    let mut state = *plaintext;
    add_round_key(&mut state, cipher.round_key(0));
    let initial_add_round_key = hex::encode(state);

    let mut rounds = Vec::with_capacity(cipher.rounds);
    let mut per_round_ns = Vec::with_capacity(cipher.rounds);
    for round in 1..=cipher.rounds {
        let round_start = Instant::now();

        sub_bytes(&mut state);
        let after_sub_bytes = hex::encode(state);

        shift_rows(&mut state);
        let after_shift_rows = hex::encode(state);

        let after_mix_columns = if round == cipher.rounds {
            None
        } else {
            mix_columns(&mut state);
            Some(hex::encode(state))
        };

        add_round_key(&mut state, cipher.round_key(round));
        let after_add_round_key = hex::encode(state);

        per_round_ns.push(nanos_u64(round_start.elapsed().as_nanos()));
        rounds.push(AesRoundTrace {
            round_index: round,
            after_sub_bytes,
            after_shift_rows,
            after_mix_columns,
            after_add_round_key,
        });
    }

    let ciphertext = state.to_vec();
    let trace = AesTrace {
        key_size_bits: key.len() * 8,
        total_rounds: cipher.rounds,
        plaintext_hex: hex::encode(plaintext),
        round_keys_hex: cipher
            .round_keys
            .chunks(BLOCK_SIZE)
            .map(hex::encode)
            .collect(),
        initial_add_round_key,
        rounds,
        ciphertext_hex: hex::encode(&ciphertext),
        timings_ns: AesTimings {
            key_expansion_ns,
            per_round_ns,
            total_ns: nanos_u64(total_start.elapsed().as_nanos()),
        },
    };

    Ok((ciphertext, trace))
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

fn required_iv(iv: Option<&[u8]>) -> CryptoResult<&[u8]> {
    iv.ok_or_else(|| CryptoError::InvalidIvLength {
        expected: BLOCK_SIZE,
        actual: 0,
    })
}

fn expand_key(key: &[u8], nk: usize, rounds: usize) -> Vec<u8> {
    let total_words = 4 * (rounds + 1);
    let mut words = vec![[0u8; 4]; total_words];
    for i in 0..nk {
        words[i].copy_from_slice(&key[i * 4..i * 4 + 4]);
    }
    for i in nk..total_words {
        let mut temp = words[i - 1];
        if i % nk == 0 {
            temp = sub_word(rot_word(temp));
            temp[0] ^= RCON[i / nk];
        } else if nk > 6 && i % nk == 4 {
            temp = sub_word(temp);
        }
        for (j, value) in temp.iter().enumerate() {
            words[i][j] = words[i - nk][j] ^ value;
        }
    }

    let mut out = Vec::with_capacity(total_words * 4);
    for word in words {
        out.extend_from_slice(&word);
    }
    out
}

fn rot_word(word: [u8; 4]) -> [u8; 4] {
    [word[1], word[2], word[3], word[0]]
}

fn sub_word(mut word: [u8; 4]) -> [u8; 4] {
    for b in &mut word {
        *b = S_BOX[*b as usize];
    }
    word
}

fn add_round_key(state: &mut [u8; BLOCK_SIZE], key: &[u8]) {
    for i in 0..BLOCK_SIZE {
        state[i] ^= key[i];
    }
}

fn sub_bytes(state: &mut [u8; BLOCK_SIZE]) {
    for b in state {
        *b = S_BOX[*b as usize];
    }
}

fn inv_sub_bytes(state: &mut [u8; BLOCK_SIZE]) {
    for b in state {
        *b = INV_S_BOX[*b as usize];
    }
}

fn shift_rows(state: &mut [u8; BLOCK_SIZE]) {
    let tmp = *state;
    for r in 0..4 {
        for c in 0..4 {
            state[r + 4 * c] = tmp[r + 4 * ((c + r) % 4)];
        }
    }
}

fn inv_shift_rows(state: &mut [u8; BLOCK_SIZE]) {
    let tmp = *state;
    for r in 0..4 {
        for c in 0..4 {
            state[r + 4 * c] = tmp[r + 4 * ((c + 4 - r) % 4)];
        }
    }
}

fn mix_columns(state: &mut [u8; BLOCK_SIZE]) {
    for c in 0..4 {
        let i = 4 * c;
        let a0 = state[i];
        let a1 = state[i + 1];
        let a2 = state[i + 2];
        let a3 = state[i + 3];
        state[i] = gf_mul(a0, 2) ^ gf_mul(a1, 3) ^ a2 ^ a3;
        state[i + 1] = a0 ^ gf_mul(a1, 2) ^ gf_mul(a2, 3) ^ a3;
        state[i + 2] = a0 ^ a1 ^ gf_mul(a2, 2) ^ gf_mul(a3, 3);
        state[i + 3] = gf_mul(a0, 3) ^ a1 ^ a2 ^ gf_mul(a3, 2);
    }
}

fn inv_mix_columns(state: &mut [u8; BLOCK_SIZE]) {
    for c in 0..4 {
        let i = 4 * c;
        let a0 = state[i];
        let a1 = state[i + 1];
        let a2 = state[i + 2];
        let a3 = state[i + 3];
        state[i] = gf_mul(a0, 14) ^ gf_mul(a1, 11) ^ gf_mul(a2, 13) ^ gf_mul(a3, 9);
        state[i + 1] = gf_mul(a0, 9) ^ gf_mul(a1, 14) ^ gf_mul(a2, 11) ^ gf_mul(a3, 13);
        state[i + 2] = gf_mul(a0, 13) ^ gf_mul(a1, 9) ^ gf_mul(a2, 14) ^ gf_mul(a3, 11);
        state[i + 3] = gf_mul(a0, 11) ^ gf_mul(a1, 13) ^ gf_mul(a2, 9) ^ gf_mul(a3, 14);
    }
}

fn gf_mul(mut a: u8, mut b: u8) -> u8 {
    let mut p = 0u8;
    for _ in 0..8 {
        if (b & 1) != 0 {
            p ^= a;
        }
        let carry = a & 0x80;
        a <<= 1;
        if carry != 0 {
            a ^= 0x1b;
        }
        b >>= 1;
    }
    p
}

fn nanos_u64(nanos: u128) -> u64 {
    nanos.min(u128::from(u64::MAX)) as u64
}

#[cfg(test)]
mod tests {
    use super::Aes;
    use crate::modes::{cbc, ctr, ecb, gcm, Padding};
    use crate::traits::SymmetricCipher;

    fn hx(s: &str) -> Vec<u8> {
        hex::decode(s).expect("valid hex")
    }

    #[test]
    fn aes128_ecb_nist_sp_800_38a_f_1_1() {
        let key = hx("2b7e151628aed2a6abf7158809cf4f3c");
        let plaintext = hx(concat!(
            "6bc1bee22e409f96e93d7e117393172a",
            "ae2d8a571e03ac9c9eb76fac45af8e51",
            "30c81c46a35ce411e5fbc1191a0a52ef",
            "f69f2445df4f9b17ad2b417be66c3710"
        ));
        let expected = hx(concat!(
            "3ad77bb40d7a3660a89ecaf32466ef97",
            "f5d3d58503b9699de785895a96fdbaaf",
            "43b1cd7f598ece23881b00e3ed030688",
            "7b0c785e27e8ad3f8223207104725dd4"
        ));
        let cipher = Aes::new(&key).expect("valid AES key");
        let ciphertext = ecb::encrypt(&cipher, &plaintext, Padding::None).expect("encrypt");
        assert_eq!(ciphertext, expected);
        assert_eq!(
            ecb::decrypt(&cipher, &ciphertext, Padding::None).expect("decrypt"),
            plaintext
        );
    }

    #[test]
    fn aes128_cbc_nist_sp_800_38a_f_2_1() {
        let key = hx("2b7e151628aed2a6abf7158809cf4f3c");
        let iv = hx("000102030405060708090a0b0c0d0e0f");
        let plaintext = hx(concat!(
            "6bc1bee22e409f96e93d7e117393172a",
            "ae2d8a571e03ac9c9eb76fac45af8e51",
            "30c81c46a35ce411e5fbc1191a0a52ef",
            "f69f2445df4f9b17ad2b417be66c3710"
        ));
        let expected = hx(concat!(
            "7649abac8119b246cee98e9b12e9197d",
            "5086cb9b507219ee95db113a917678b2",
            "73bed6b8e3c1743b7116e69e22229516",
            "3ff1caa1681fac09120eca307586e1a7"
        ));
        let cipher = Aes::new(&key).expect("valid AES key");
        let ciphertext = cbc::encrypt(&cipher, &plaintext, &iv, Padding::None).expect("encrypt");
        assert_eq!(ciphertext, expected);
        assert_eq!(
            cbc::decrypt(&cipher, &ciphertext, &iv, Padding::None).expect("decrypt"),
            plaintext
        );
    }

    #[test]
    fn aes128_ctr_nist_sp_800_38a_f_5_1() {
        let key = hx("2b7e151628aed2a6abf7158809cf4f3c");
        let iv = hx("f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff");
        let plaintext = hx(concat!(
            "6bc1bee22e409f96e93d7e117393172a",
            "ae2d8a571e03ac9c9eb76fac45af8e51",
            "30c81c46a35ce411e5fbc1191a0a52ef",
            "f69f2445df4f9b17ad2b417be66c3710"
        ));
        let expected = hx(concat!(
            "874d6191b620e3261bef6864990db6ce",
            "9806f66b7970fdff8617187bb9fffdff",
            "5ae4df3edbd5d35e5b4f09020db03eab",
            "1e031dda2fbe03d1792170a0f3009cee"
        ));
        let cipher = Aes::new(&key).expect("valid AES key");
        let ciphertext = ctr::xor_keystream(&cipher, &plaintext, &iv, 0).expect("encrypt");
        assert_eq!(ciphertext, expected);
        assert_eq!(
            ctr::xor_keystream(&cipher, &ciphertext, &iv, 0).expect("decrypt"),
            plaintext
        );
    }

    #[test]
    fn aes128_gcm_nist_sp_800_38d_cases() {
        let cipher = Aes::new(&[0u8; 16]).expect("valid AES key");
        let out = gcm::encrypt(&cipher, &[], &[0u8; 12], &[]).expect("gcm encrypt");
        assert_eq!(hex::encode(out), "58e2fccefa7e3061367f1d57a4e7455a");
        let out = gcm::encrypt(&cipher, &[0u8; 16], &[0u8; 12], &[]).expect("gcm encrypt");
        assert_eq!(
            hex::encode(out),
            "0388dace60b6a392f328c2b971b2fe78ab6e47d42cec13bdf53a67b21257bddf"
        );

        let key = hx("feffe9928665731c6d6a8f9467308308");
        let iv = hx("cafebabefacedbaddecaf888");
        let plaintext = hx(concat!(
            "d9313225f88406e5a55909c5aff5269a",
            "86a7a9531534f7da2e4c303d8a318a72",
            "1c3c0c95956809532fcf0e2449a6b525",
            "b16aedf5aa0de657ba637b391aafd255"
        ));
        let expected_ciphertext = hx(concat!(
            "42831ec2217774244b7221b784d0d49c",
            "e3aa212f2c02a4e035c17e2329aca12e",
            "21d514b25466931c7d8f6a5aac84aa05",
            "1ba30b396a0aac973d58e091473f5985"
        ));
        let cipher = Aes::new(&key).expect("valid AES key");
        let out = gcm::encrypt(&cipher, &plaintext, &iv, &[]).expect("gcm encrypt");
        assert_eq!(&out[..plaintext.len()], expected_ciphertext.as_slice());
        assert_eq!(
            hex::encode(&out[plaintext.len()..]),
            "4d5c2af327cd64a62cf35abd2ba6fab4"
        );
        assert_eq!(gcm::decrypt(&cipher, &out, &iv, &[]).expect("gcm decrypt"), plaintext);
    }

    #[test]
    fn aes192_and_aes256_ecb_vectors() {
        let mut block = hx("00112233445566778899aabbccddeeff");
        let cipher = Aes::new(&hx("000102030405060708090a0b0c0d0e0f1011121314151617"))
            .expect("valid AES-192 key");
        cipher.encrypt_block(&mut block).expect("encrypt");
        assert_eq!(hex::encode(&block), "dda97ca4864cdfe06eaf70a0ec0d7191");

        let mut block = hx("00112233445566778899aabbccddeeff");
        let cipher = Aes::new(&hx(
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
        ))
        .expect("valid AES-256 key");
        cipher.encrypt_block(&mut block).expect("encrypt");
        assert_eq!(hex::encode(&block), "8ea2b7ca516745bfeafc49904b496089");
    }
}

#[cfg(test)]
mod trace {
    use super::{encrypt_block_with_trace, BLOCK_SIZE};

    fn block(hex: &str) -> [u8; BLOCK_SIZE] {
        hex::decode(hex)
            .expect("valid hex")
            .try_into()
            .expect("16-byte block")
    }

    fn bytes(hex: &str) -> Vec<u8> {
        hex::decode(hex).expect("valid hex")
    }

    #[test]
    fn fips_197_aes128_trace_matches_every_intermediate_state() {
        let plaintext = block("00112233445566778899aabbccddeeff");
        let key = bytes("000102030405060708090a0b0c0d0e0f");
        let (ciphertext, trace) = encrypt_block_with_trace(&plaintext, &key).expect("trace");

        assert_eq!(hex::encode(ciphertext), "69c4e0d86a7b0430d8cdb78070b4c55a");
        assert_eq!(trace.key_size_bits, 128);
        assert_eq!(trace.total_rounds, 10);
        assert_eq!(trace.plaintext_hex, "00112233445566778899aabbccddeeff");
        assert_eq!(trace.initial_add_round_key, "00102030405060708090a0b0c0d0e0f0");
        assert_eq!(trace.ciphertext_hex, "69c4e0d86a7b0430d8cdb78070b4c55a");

        let expected_round_keys = [
            "000102030405060708090a0b0c0d0e0f",
            "d6aa74fdd2af72fadaa678f1d6ab76fe",
            "b692cf0b643dbdf1be9bc5006830b3fe",
            "b6ff744ed2c2c9bf6c590cbf0469bf41",
            "47f7f7bc95353e03f96c32bcfd058dfd",
            "3caaa3e8a99f9deb50f3af57adf622aa",
            "5e390f7df7a69296a7553dc10aa31f6b",
            "14f9701ae35fe28c440adf4d4ea9c026",
            "47438735a41c65b9e016baf4aebf7ad2",
            "549932d1f08557681093ed9cbe2c974e",
            "13111d7fe3944a17f307a78b4d2b30c5",
        ];
        assert_eq!(trace.round_keys_hex, expected_round_keys);

        let expected_rounds = [
            (
                1,
                "63cab7040953d051cd60e0e7ba70e18c",
                "6353e08c0960e104cd70b751bacad0e7",
                Some("5f72641557f5bc92f7be3b291db9f91a"),
                "89d810e8855ace682d1843d8cb128fe4",
            ),
            (
                2,
                "a761ca9b97be8b45d8ad1a611fc97369",
                "a7be1a6997ad739bd8c9ca451f618b61",
                Some("ff87968431d86a51645151fa773ad009"),
                "4915598f55e5d7a0daca94fa1f0a63f7",
            ),
            (
                3,
                "3b59cb73fcd90ee05774222dc067fb68",
                "3bd92268fc74fb735767cbe0c0590e2d",
                Some("4c9c1e66f771f0762c3f868e534df256"),
                "fa636a2825b339c940668a3157244d17",
            ),
            (
                4,
                "2dfb02343f6d12dd09337ec75b36e3f0",
                "2d6d7ef03f33e334093602dd5bfb12c7",
                Some("6385b79ffc538df997be478e7547d691"),
                "247240236966b3fa6ed2753288425b6c",
            ),
            (
                5,
                "36400926f9336d2d9fb59d23c42c3950",
                "36339d50f9b539269f2c092dc4406d23",
                Some("f4bcd45432e554d075f1d6c51dd03b3c"),
                "c81677bc9b7ac93b25027992b0261996",
            ),
            (
                6,
                "e847f56514dadde23f77b64fe7f7d490",
                "e8dab6901477d4653ff7f5e2e747dd4f",
                Some("9816ee7400f87f556b2c049c8e5ad036"),
                "c62fe109f75eedc3cc79395d84f9cf5d",
            ),
            (
                7,
                "b415f8016858552e4bb6124c5f998a4c",
                "b458124c68b68a014b99f82e5f15554c",
                Some("c57e1c159a9bd286f05f4be098c63439"),
                "d1876c0f79c4300ab45594add66ff41f",
            ),
            (
                8,
                "3e175076b61c04678dfc2295f6a8bfc0",
                "3e1c22c0b6fcbf768da85067f6170495",
                Some("baa03de7a1f9b56ed5512cba5f414d23"),
                "fde3bad205e5d0d73547964ef1fe37f1",
            ),
            (
                9,
                "5411f4b56bd9700e96a0902fa1bb9aa1",
                "54d990a16ba09ab596bbf40ea111702f",
                Some("e9f74eec023020f61bf2ccf2353c21c7"),
                "bd6e7c3df2b5779e0b61216e8b10b689",
            ),
            (
                10,
                "7a9f102789d5f50b2beffd9f3dca4ea7",
                "7ad5fda789ef4e272bca100b3d9ff59f",
                None,
                "69c4e0d86a7b0430d8cdb78070b4c55a",
            ),
        ];

        assert_eq!(trace.rounds.len(), expected_rounds.len());
        for (actual, expected) in trace.rounds.iter().zip(expected_rounds) {
            assert_eq!(actual.round_index, expected.0);
            assert_eq!(actual.after_sub_bytes, expected.1);
            assert_eq!(actual.after_shift_rows, expected.2);
            assert_eq!(actual.after_mix_columns.as_deref(), expected.3);
            assert_eq!(actual.after_add_round_key, expected.4);
        }
        assert_eq!(trace.timings_ns.per_round_ns.len(), 10);
    }

    #[test]
    fn aes192_and_aes256_trace_shapes_match_key_size() {
        let plaintext = block("00112233445566778899aabbccddeeff");

        let (ciphertext, trace) = encrypt_block_with_trace(
            &plaintext,
            &bytes("000102030405060708090a0b0c0d0e0f1011121314151617"),
        )
        .expect("AES-192 trace");
        assert_eq!(hex::encode(ciphertext), "dda97ca4864cdfe06eaf70a0ec0d7191");
        assert_eq!(trace.key_size_bits, 192);
        assert_eq!(trace.total_rounds, 12);
        assert_eq!(trace.round_keys_hex.len(), 13);
        assert_eq!(trace.rounds.len(), 12);
        assert!(trace.rounds.last().expect("final round").after_mix_columns.is_none());

        let (ciphertext, trace) = encrypt_block_with_trace(
            &plaintext,
            &bytes("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"),
        )
        .expect("AES-256 trace");
        assert_eq!(hex::encode(ciphertext), "8ea2b7ca516745bfeafc49904b496089");
        assert_eq!(trace.key_size_bits, 256);
        assert_eq!(trace.total_rounds, 14);
        assert_eq!(trace.round_keys_hex.len(), 15);
        assert_eq!(trace.rounds.len(), 14);
        assert!(trace.rounds.last().expect("final round").after_mix_columns.is_none());
    }
}
