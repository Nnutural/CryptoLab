//! SHA-2 family (FIPS 180-4): SHA-224, SHA-256, SHA-384, SHA-512.

use crate::error::{CryptoError, CryptoResult};
use crate::traits::HashAlgorithm;

const SHA256_BLOCK_SIZE: usize = 64;
const SHA512_BLOCK_SIZE: usize = 128;

const SHA224_IV: [u32; 8] = [
    0xc105_9ed8,
    0x367c_d507,
    0x3070_dd17,
    0xf70e_5939,
    0xffc0_0b31,
    0x6858_1511,
    0x64f9_8fa7,
    0xbefa_4fa4,
];

const SHA256_IV: [u32; 8] = [
    0x6a09_e667,
    0xbb67_ae85,
    0x3c6e_f372,
    0xa54f_f53a,
    0x510e_527f,
    0x9b05_688c,
    0x1f83_d9ab,
    0x5be0_cd19,
];

const SHA384_IV: [u64; 8] = [
    0xcbbb_9d5d_c105_9ed8,
    0x629a_292a_367c_d507,
    0x9159_015a_3070_dd17,
    0x152f_ecd8_f70e_5939,
    0x6733_2667_ffc0_0b31,
    0x8eb4_4a87_6858_1511,
    0xdb0c_2e0d_64f9_8fa7,
    0x47b5_481d_befa_4fa4,
];

const SHA512_IV: [u64; 8] = [
    0x6a09_e667_f3bc_c908,
    0xbb67_ae85_84ca_a73b,
    0x3c6e_f372_fe94_f82b,
    0xa54f_f53a_5f1d_36f1,
    0x510e_527f_ade6_82d1,
    0x9b05_688c_2b3e_6c1f,
    0x1f83_d9ab_fb41_bd6b,
    0x5be0_cd19_137e_2179,
];

const K256: [u32; 64] = [
    0x428a_2f98,
    0x7137_4491,
    0xb5c0_fbcf,
    0xe9b5_dba5,
    0x3956_c25b,
    0x59f1_11f1,
    0x923f_82a4,
    0xab1c_5ed5,
    0xd807_aa98,
    0x1283_5b01,
    0x2431_85be,
    0x550c_7dc3,
    0x72be_5d74,
    0x80de_b1fe,
    0x9bdc_06a7,
    0xc19b_f174,
    0xe49b_69c1,
    0xefbe_4786,
    0x0fc1_9dc6,
    0x240c_a1cc,
    0x2de9_2c6f,
    0x4a74_84aa,
    0x5cb0_a9dc,
    0x76f9_88da,
    0x983e_5152,
    0xa831_c66d,
    0xb003_27c8,
    0xbf59_7fc7,
    0xc6e0_0bf3,
    0xd5a7_9147,
    0x06ca_6351,
    0x1429_2967,
    0x27b7_0a85,
    0x2e1b_2138,
    0x4d2c_6dfc,
    0x5338_0d13,
    0x650a_7354,
    0x766a_0abb,
    0x81c2_c92e,
    0x9272_2c85,
    0xa2bf_e8a1,
    0xa81a_664b,
    0xc24b_8b70,
    0xc76c_51a3,
    0xd192_e819,
    0xd699_0624,
    0xf40e_3585,
    0x106a_a070,
    0x19a4_c116,
    0x1e37_6c08,
    0x2748_774c,
    0x34b0_bcb5,
    0x391c_0cb3,
    0x4ed8_aa4a,
    0x5b9c_ca4f,
    0x682e_6ff3,
    0x748f_82ee,
    0x78a5_636f,
    0x84c8_7814,
    0x8cc7_0208,
    0x90be_fffa,
    0xa450_6ceb,
    0xbef9_a3f7,
    0xc671_78f2,
];

const K512: [u64; 80] = [
    0x428a_2f98_d728_ae22,
    0x7137_4491_23ef_65cd,
    0xb5c0_fbcf_ec4d_3b2f,
    0xe9b5_dba5_8189_dbbc,
    0x3956_c25b_f348_b538,
    0x59f1_11f1_b605_d019,
    0x923f_82a4_af19_4f9b,
    0xab1c_5ed5_da6d_8118,
    0xd807_aa98_a303_0242,
    0x1283_5b01_4570_6fbe,
    0x2431_85be_4ee4_b28c,
    0x550c_7dc3_d5ff_b4e2,
    0x72be_5d74_f27b_896f,
    0x80de_b1fe_3b16_96b1,
    0x9bdc_06a7_25c7_1235,
    0xc19b_f174_cf69_2694,
    0xe49b_69c1_9ef1_4ad2,
    0xefbe_4786_384f_25e3,
    0x0fc1_9dc6_8b8c_d5b5,
    0x240c_a1cc_77ac_9c65,
    0x2de9_2c6f_592b_0275,
    0x4a74_84aa_6ea6_e483,
    0x5cb0_a9dc_bd41_fbd4,
    0x76f9_88da_8311_53b5,
    0x983e_5152_ee66_dfab,
    0xa831_c66d_2db4_3210,
    0xb003_27c8_98fb_213f,
    0xbf59_7fc7_beef_0ee4,
    0xc6e0_0bf3_3da8_8fc2,
    0xd5a7_9147_930a_a725,
    0x06ca_6351_e003_826f,
    0x1429_2967_0a0e_6e70,
    0x27b7_0a85_46d2_2ffc,
    0x2e1b_2138_5c26_c926,
    0x4d2c_6dfc_5ac4_2aed,
    0x5338_0d13_9d95_b3df,
    0x650a_7354_8baf_63de,
    0x766a_0abb_3c77_b2a8,
    0x81c2_c92e_47ed_aee6,
    0x9272_2c85_1482_353b,
    0xa2bf_e8a1_4cf1_0364,
    0xa81a_664b_bc42_3001,
    0xc24b_8b70_d0f8_9791,
    0xc76c_51a3_0654_be30,
    0xd192_e819_d6ef_5218,
    0xd699_0624_5565_a910,
    0xf40e_3585_5771_202a,
    0x106a_a070_32bb_d1b8,
    0x19a4_c116_b8d2_d0c8,
    0x1e37_6c08_5141_ab53,
    0x2748_774c_df8e_eb99,
    0x34b0_bcb5_e19b_48a8,
    0x391c_0cb3_c5c9_5a63,
    0x4ed8_aa4a_e341_8acb,
    0x5b9c_ca4f_7763_e373,
    0x682e_6ff3_d6b2_b8a3,
    0x748f_82ee_5def_b2fc,
    0x78a5_636f_4317_2f60,
    0x84c8_7814_a1f0_ab72,
    0x8cc7_0208_1a64_39ec,
    0x90be_fffa_2363_1e28,
    0xa450_6ceb_de82_bde9,
    0xbef9_a3f7_b2c6_7915,
    0xc671_78f2_e372_532b,
    0xca27_3ece_ea26_619c,
    0xd186_b8c7_21c0_c207,
    0xeada_7dd6_cde0_eb1e,
    0xf57d_4f7f_ee6e_d178,
    0x06f0_67aa_7217_6fba,
    0x0a63_7dc5_a2c8_98a6,
    0x113f_9804_bef9_0dae,
    0x1b71_0b35_131c_471b,
    0x28db_77f5_2304_7d84,
    0x32ca_ab7b_40c7_2493,
    0x3c9e_be0a_15c9_bebc,
    0x431d_67c4_9c10_0d4c,
    0x4cc5_d4be_cb3e_42b6,
    0x597f_299c_fc65_7e2a,
    0x5fcb_6fab_3ad6_faec,
    0x6c44_198c_4a47_5817,
];

/// Streaming SHA-256 hasher following FIPS 180-4 §6.2.
#[derive(Debug, Clone)]
pub struct Sha256 {
    state: [u32; 8],
    buffer: [u8; SHA256_BLOCK_SIZE],
    buffer_len: usize,
    length_bytes: u64,
}

impl Default for Sha256 {
    fn default() -> Self {
        Self::new()
    }
}

impl Sha256 {
    /// Create a new SHA-256 streaming hasher using the FIPS 180-4 initial IV.
    pub fn new() -> Self {
        Self {
            state: SHA256_IV,
            buffer: [0u8; SHA256_BLOCK_SIZE],
            buffer_len: 0,
            length_bytes: 0,
        }
    }

    /// Absorb bytes into the SHA-256 state.
    pub fn update(&mut self, data: &[u8]) {
        update256_state(
            &mut self.state,
            &mut self.buffer,
            &mut self.buffer_len,
            &mut self.length_bytes,
            data,
        );
    }

    /// Finalize SHA-256 and return the 32-byte digest.
    pub fn finalize(self) -> [u8; 32] {
        finalize256_state(self.state, self.buffer, self.buffer_len, self.length_bytes)
    }
}

impl HashAlgorithm for Sha256 {
    const DIGEST_SIZE: usize = 32;
    const BLOCK_SIZE: usize = SHA256_BLOCK_SIZE;

    fn reset(&mut self) {
        *self = Self::new();
    }

    fn update(&mut self, data: &[u8]) {
        Sha256::update(self, data);
    }

    fn finalize_into(self, out: &mut [u8]) -> CryptoResult<()> {
        if out.len() != Self::DIGEST_SIZE {
            return Err(CryptoError::InvalidInputLength(format!(
                "SHA-256 output buffer must be {} bytes, got {}",
                Self::DIGEST_SIZE,
                out.len()
            )));
        }
        out.copy_from_slice(&self.finalize());
        Ok(())
    }
}

/// One-shot SHA-224 digest per FIPS 180-4 §6.3.
pub fn sha224(data: &[u8]) -> [u8; 28] {
    let digest = sha256_with_iv(data, SHA224_IV);
    let mut out = [0u8; 28];
    out.copy_from_slice(&digest[..28]);
    out
}

/// One-shot SHA-256 digest per FIPS 180-4 §6.2.
pub fn sha256(data: &[u8]) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hasher.finalize()
}

/// One-shot SHA-384 digest per FIPS 180-4 §6.5.
pub fn sha384(data: &[u8]) -> [u8; 48] {
    let digest = sha512_with_iv(data, SHA384_IV);
    let mut out = [0u8; 48];
    out.copy_from_slice(&digest[..48]);
    out
}

/// One-shot SHA-512 digest per FIPS 180-4 §6.4.
pub fn sha512(data: &[u8]) -> [u8; 64] {
    sha512_with_iv(data, SHA512_IV)
}

fn sha256_with_iv(data: &[u8], iv: [u32; 8]) -> [u8; 32] {
    let mut state = iv;
    let mut buffer = [0u8; SHA256_BLOCK_SIZE];
    let mut buffer_len = 0usize;
    let mut length_bytes = 0u64;
    update256_state(
        &mut state,
        &mut buffer,
        &mut buffer_len,
        &mut length_bytes,
        data,
    );
    finalize256_state(state, buffer, buffer_len, length_bytes)
}

fn update256_state(
    state: &mut [u32; 8],
    buffer: &mut [u8; SHA256_BLOCK_SIZE],
    buffer_len: &mut usize,
    length_bytes: &mut u64,
    data: &[u8],
) {
    *length_bytes = length_bytes.wrapping_add(data.len() as u64);
    let mut input = data;

    if *buffer_len > 0 {
        let take = (SHA256_BLOCK_SIZE - *buffer_len).min(input.len());
        buffer[*buffer_len..*buffer_len + take].copy_from_slice(&input[..take]);
        *buffer_len += take;
        input = &input[take..];
        if *buffer_len == SHA256_BLOCK_SIZE {
            compress256(state, buffer);
            *buffer_len = 0;
        }
    }

    let mut chunks = input.chunks_exact(SHA256_BLOCK_SIZE);
    for chunk in &mut chunks {
        compress256(state, chunk);
    }

    let rem = chunks.remainder();
    if !rem.is_empty() {
        buffer[..rem.len()].copy_from_slice(rem);
        *buffer_len = rem.len();
    }
}

fn finalize256_state(
    mut state: [u32; 8],
    mut buffer: [u8; SHA256_BLOCK_SIZE],
    mut buffer_len: usize,
    length_bytes: u64,
) -> [u8; 32] {
    let bit_len = length_bytes.wrapping_mul(8);
    buffer[buffer_len] = 0x80;
    buffer_len += 1;

    if buffer_len > 56 {
        buffer[buffer_len..].fill(0);
        compress256(&mut state, &buffer);
        buffer = [0u8; SHA256_BLOCK_SIZE];
        buffer_len = 0;
    }

    buffer[buffer_len..56].fill(0);
    buffer[56..64].copy_from_slice(&bit_len.to_be_bytes());
    compress256(&mut state, &buffer);

    let mut out = [0u8; 32];
    for (i, word) in state.iter().enumerate() {
        out[i * 4..(i + 1) * 4].copy_from_slice(&word.to_be_bytes());
    }
    out
}

fn compress256(state: &mut [u32; 8], block: &[u8]) {
    let mut w = [0u32; 64];
    for (i, chunk) in block.chunks_exact(4).take(16).enumerate() {
        w[i] = u32::from_be_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]);
    }
    for i in 16..64 {
        w[i] = small_sigma1_32(w[i - 2])
            .wrapping_add(w[i - 7])
            .wrapping_add(small_sigma0_32(w[i - 15]))
            .wrapping_add(w[i - 16]);
    }

    let mut a = state[0];
    let mut b = state[1];
    let mut c = state[2];
    let mut d = state[3];
    let mut e = state[4];
    let mut f = state[5];
    let mut g = state[6];
    let mut h = state[7];

    for i in 0..64 {
        let t1 = h
            .wrapping_add(big_sigma1_32(e))
            .wrapping_add(ch32(e, f, g))
            .wrapping_add(K256[i])
            .wrapping_add(w[i]);
        let t2 = big_sigma0_32(a).wrapping_add(maj32(a, b, c));
        h = g;
        g = f;
        f = e;
        e = d.wrapping_add(t1);
        d = c;
        c = b;
        b = a;
        a = t1.wrapping_add(t2);
    }

    state[0] = state[0].wrapping_add(a);
    state[1] = state[1].wrapping_add(b);
    state[2] = state[2].wrapping_add(c);
    state[3] = state[3].wrapping_add(d);
    state[4] = state[4].wrapping_add(e);
    state[5] = state[5].wrapping_add(f);
    state[6] = state[6].wrapping_add(g);
    state[7] = state[7].wrapping_add(h);
}

fn sha512_with_iv(data: &[u8], iv: [u64; 8]) -> [u8; 64] {
    let mut state = iv;

    let mut chunks = data.chunks_exact(SHA512_BLOCK_SIZE);
    for chunk in &mut chunks {
        compress512(&mut state, chunk);
    }

    let rem = chunks.remainder();
    let bit_len = (data.len() as u128).wrapping_mul(8);
    let mut final_blocks = [0u8; SHA512_BLOCK_SIZE * 2];
    final_blocks[..rem.len()].copy_from_slice(rem);
    final_blocks[rem.len()] = 0x80;

    let total_len = if rem.len() + 1 + 16 <= SHA512_BLOCK_SIZE {
        SHA512_BLOCK_SIZE
    } else {
        SHA512_BLOCK_SIZE * 2
    };
    final_blocks[total_len - 16..total_len].copy_from_slice(&bit_len.to_be_bytes());

    for block in final_blocks[..total_len].chunks_exact(SHA512_BLOCK_SIZE) {
        compress512(&mut state, block);
    }

    let mut out = [0u8; 64];
    for (i, word) in state.iter().enumerate() {
        out[i * 8..(i + 1) * 8].copy_from_slice(&word.to_be_bytes());
    }
    out
}

fn compress512(state: &mut [u64; 8], block: &[u8]) {
    let mut w = [0u64; 80];
    for (i, chunk) in block.chunks_exact(8).take(16).enumerate() {
        w[i] = u64::from_be_bytes([
            chunk[0], chunk[1], chunk[2], chunk[3], chunk[4], chunk[5], chunk[6], chunk[7],
        ]);
    }
    for i in 16..80 {
        w[i] = small_sigma1_64(w[i - 2])
            .wrapping_add(w[i - 7])
            .wrapping_add(small_sigma0_64(w[i - 15]))
            .wrapping_add(w[i - 16]);
    }

    let mut a = state[0];
    let mut b = state[1];
    let mut c = state[2];
    let mut d = state[3];
    let mut e = state[4];
    let mut f = state[5];
    let mut g = state[6];
    let mut h = state[7];

    for i in 0..80 {
        let t1 = h
            .wrapping_add(big_sigma1_64(e))
            .wrapping_add(ch64(e, f, g))
            .wrapping_add(K512[i])
            .wrapping_add(w[i]);
        let t2 = big_sigma0_64(a).wrapping_add(maj64(a, b, c));
        h = g;
        g = f;
        f = e;
        e = d.wrapping_add(t1);
        d = c;
        c = b;
        b = a;
        a = t1.wrapping_add(t2);
    }

    state[0] = state[0].wrapping_add(a);
    state[1] = state[1].wrapping_add(b);
    state[2] = state[2].wrapping_add(c);
    state[3] = state[3].wrapping_add(d);
    state[4] = state[4].wrapping_add(e);
    state[5] = state[5].wrapping_add(f);
    state[6] = state[6].wrapping_add(g);
    state[7] = state[7].wrapping_add(h);
}

#[inline]
fn ch32(x: u32, y: u32, z: u32) -> u32 {
    (x & y) ^ (!x & z)
}

#[inline]
fn maj32(x: u32, y: u32, z: u32) -> u32 {
    (x & y) ^ (x & z) ^ (y & z)
}

#[inline]
fn big_sigma0_32(x: u32) -> u32 {
    x.rotate_right(2) ^ x.rotate_right(13) ^ x.rotate_right(22)
}

#[inline]
fn big_sigma1_32(x: u32) -> u32 {
    x.rotate_right(6) ^ x.rotate_right(11) ^ x.rotate_right(25)
}

#[inline]
fn small_sigma0_32(x: u32) -> u32 {
    x.rotate_right(7) ^ x.rotate_right(18) ^ (x >> 3)
}

#[inline]
fn small_sigma1_32(x: u32) -> u32 {
    x.rotate_right(17) ^ x.rotate_right(19) ^ (x >> 10)
}

#[inline]
fn ch64(x: u64, y: u64, z: u64) -> u64 {
    (x & y) ^ (!x & z)
}

#[inline]
fn maj64(x: u64, y: u64, z: u64) -> u64 {
    (x & y) ^ (x & z) ^ (y & z)
}

#[inline]
fn big_sigma0_64(x: u64) -> u64 {
    x.rotate_right(28) ^ x.rotate_right(34) ^ x.rotate_right(39)
}

#[inline]
fn big_sigma1_64(x: u64) -> u64 {
    x.rotate_right(14) ^ x.rotate_right(18) ^ x.rotate_right(41)
}

#[inline]
fn small_sigma0_64(x: u64) -> u64 {
    x.rotate_right(1) ^ x.rotate_right(8) ^ (x >> 7)
}

#[inline]
fn small_sigma1_64(x: u64) -> u64 {
    x.rotate_right(19) ^ x.rotate_right(61) ^ (x >> 6)
}

#[cfg(test)]
mod tests {
    use super::{sha224, sha256, sha384, sha512, Sha256};
    use rand::rngs::StdRng;
    use rand::{RngCore, SeedableRng};

    const LONG_448: &[u8] = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";

    #[test]
    fn sha256_nist_short_vectors() {
        assert_eq!(
            hex::encode(sha256(b"")),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(
            hex::encode(sha256(b"abc")),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
        assert_eq!(
            hex::encode(sha256(LONG_448)),
            "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
        );
    }

    #[test]
    fn sha224_nist_short_vectors() {
        assert_eq!(
            hex::encode(sha224(b"")),
            "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f"
        );
        assert_eq!(
            hex::encode(sha224(b"abc")),
            "23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7"
        );
        assert_eq!(
            hex::encode(sha224(LONG_448)),
            "75388b16512776cc5dba5da1fd890150b0c6455cb4f58b1952522525"
        );
    }

    #[test]
    fn sha512_nist_short_vectors() {
        assert_eq!(
            hex::encode(sha512(b"")),
            concat!(
                "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36c",
                "e9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
            )
        );
        assert_eq!(
            hex::encode(sha512(b"abc")),
            concat!(
                "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55",
                "d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
            )
        );
        assert_eq!(
            hex::encode(sha512(LONG_448)),
            concat!(
                "204a8fc6dda82f0a0ced7beb8e08a41657c16ef468b228a8279be331",
                "a703c33596fd15c13b1b07f9aa1d3bea57789ca031ad85c7a71dd70354ec631238ca3445"
            )
        );
    }

    #[test]
    fn sha384_nist_short_vectors() {
        assert_eq!(
            hex::encode(sha384(b"")),
            concat!(
                "38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6",
                "e1da274edebfe76f65fbd51ad2f14898b95b"
            )
        );
        assert_eq!(
            hex::encode(sha384(b"abc")),
            concat!(
                "cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a",
                "43ff5bed8086072ba1e7cc2358baeca134c825a7"
            )
        );
        assert_eq!(
            hex::encode(sha384(LONG_448)),
            concat!(
                "3391fdddfc8dc7393707a65b1b4709397cf8b1d162af05abfe8f450d",
                "e5f36bc6b0455a8520bc4e6f5fe95b1fe3c8452b"
            )
        );
    }

    #[test]
    fn sha256_streaming_matches_one_shot_for_random_1mb() {
        let mut rng = StdRng::seed_from_u64(0x256);
        let mut input = vec![0u8; 1024 * 1024];
        rng.fill_bytes(&mut input);

        let one_shot = sha256(&input);
        let mut streaming = Sha256::new();
        for chunk in input.chunks(7919) {
            streaming.update(chunk);
        }
        assert_eq!(streaming.finalize(), one_shot);
    }

    #[cfg(feature = "reference-validation")]
    #[test]
    fn sha2_reference_validation_against_rustcrypto() {
        use sha2::Digest;

        let inputs: [&[u8]; 4] = [b"", b"abc", LONG_448, b"CryptoLab SHA-2 reference check"];

        for input in inputs {
            assert_eq!(
                sha224(input).as_slice(),
                sha2::Sha224::digest(input).as_slice()
            );
            assert_eq!(
                sha256(input).as_slice(),
                sha2::Sha256::digest(input).as_slice()
            );
            assert_eq!(
                sha384(input).as_slice(),
                sha2::Sha384::digest(input).as_slice()
            );
            assert_eq!(
                sha512(input).as_slice(),
                sha2::Sha512::digest(input).as_slice()
            );
        }
    }
}
