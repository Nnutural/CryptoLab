//! GCM — Galois/Counter Mode (NIST SP 800-38D).
//!
//! Combines CTR confidentiality with GHASH-based authentication. Tag length
//! defaults to 128 bits; shorter tags are NOT supported by this impl to
//! avoid the SP 800-38D Appendix C edge cases.

use crate::error::{CryptoError, CryptoResult};
use crate::modes::ctr;
use crate::traits::SymmetricCipher;
use subtle::ConstantTimeEq;

/// Authentication tag length in bytes.
pub const TAG_LEN: usize = 16;

/// AES-GCM encrypt. Returns `ciphertext || tag` concatenated.
pub fn encrypt<C: SymmetricCipher>(
    cipher: &C,
    plaintext: &[u8],
    iv: &[u8],
    aad: &[u8],
) -> CryptoResult<Vec<u8>> {
    if C::BLOCK_SIZE != 16 {
        return Err(CryptoError::InvalidParameter(
            "GCM requires a 128-bit block cipher".to_string(),
        ));
    }
    if iv.len() != 12 {
        return Err(CryptoError::InvalidIvLength {
            expected: 12,
            actual: iv.len(),
        });
    }

    let h = hash_subkey(cipher)?;
    let j0 = j0_from_96_bit_iv(iv);
    let mut ctr0 = j0.to_vec();
    inc32(&mut ctr0);
    let ciphertext = ctr::xor_keystream(cipher, plaintext, &ctr0, 0)?;
    let tag = compute_tag(cipher, &h, &j0, aad, &ciphertext)?;

    let mut out = ciphertext;
    out.extend_from_slice(&tag);
    Ok(out)
}

/// AES-GCM decrypt. Verifies tag constant-time before returning plaintext.
pub fn decrypt<C: SymmetricCipher>(
    cipher: &C,
    ciphertext_with_tag: &[u8],
    iv: &[u8],
    aad: &[u8],
) -> CryptoResult<Vec<u8>> {
    if C::BLOCK_SIZE != 16 {
        return Err(CryptoError::InvalidParameter(
            "GCM requires a 128-bit block cipher".to_string(),
        ));
    }
    if iv.len() != 12 {
        return Err(CryptoError::InvalidIvLength {
            expected: 12,
            actual: iv.len(),
        });
    }
    if ciphertext_with_tag.len() < TAG_LEN {
        return Err(CryptoError::InvalidInputLength(
            "GCM ciphertext is shorter than tag length".to_string(),
        ));
    }

    let (ciphertext, tag) = ciphertext_with_tag.split_at(ciphertext_with_tag.len() - TAG_LEN);
    let h = hash_subkey(cipher)?;
    let j0 = j0_from_96_bit_iv(iv);
    let expected = compute_tag(cipher, &h, &j0, aad, ciphertext)?;
    if !bool::from(expected.ct_eq(tag)) {
        return Err(CryptoError::AuthenticationFailed);
    }

    let mut ctr0 = j0.to_vec();
    inc32(&mut ctr0);
    ctr::xor_keystream(cipher, ciphertext, &ctr0, 0)
}

/// GHASH over the field GF(2^128) with reduction polynomial x^128 + x^7 + x^2 + x + 1.
pub fn ghash(h: &[u8; 16], data: &[u8]) -> [u8; 16] {
    let h = u128::from_be_bytes(*h);
    let mut y = 0u128;
    for chunk in data.chunks(16) {
        let mut block = [0u8; 16];
        block[..chunk.len()].copy_from_slice(chunk);
        y ^= u128::from_be_bytes(block);
        y = gf_mul(y, h);
    }
    y.to_be_bytes()
}

fn hash_subkey<C: SymmetricCipher>(cipher: &C) -> CryptoResult<[u8; 16]> {
    let mut h = [0u8; 16];
    cipher.encrypt_block(&mut h)?;
    Ok(h)
}

fn j0_from_96_bit_iv(iv: &[u8]) -> [u8; 16] {
    let mut j0 = [0u8; 16];
    j0[..12].copy_from_slice(iv);
    j0[15] = 1;
    j0
}

fn compute_tag<C: SymmetricCipher>(
    cipher: &C,
    h: &[u8; 16],
    j0: &[u8; 16],
    aad: &[u8],
    ciphertext: &[u8],
) -> CryptoResult<[u8; 16]> {
    let mut ghash_input = Vec::new();
    ghash_input.extend_from_slice(aad);
    pad_to_block(&mut ghash_input);
    ghash_input.extend_from_slice(ciphertext);
    pad_to_block(&mut ghash_input);
    ghash_input.extend_from_slice(&((aad.len() as u64) * 8).to_be_bytes());
    ghash_input.extend_from_slice(&((ciphertext.len() as u64) * 8).to_be_bytes());

    let s = ghash(h, &ghash_input);
    let mut e_j0 = *j0;
    cipher.encrypt_block(&mut e_j0)?;
    for i in 0..16 {
        e_j0[i] ^= s[i];
    }
    Ok(e_j0)
}

fn pad_to_block(data: &mut Vec<u8>) {
    let rem = data.len() % 16;
    if rem != 0 {
        data.extend(std::iter::repeat(0u8).take(16 - rem));
    }
}

fn inc32(block: &mut [u8]) {
    let len = block.len();
    let mut counter =
        u32::from_be_bytes([block[len - 4], block[len - 3], block[len - 2], block[len - 1]]);
    counter = counter.wrapping_add(1);
    block[len - 4..].copy_from_slice(&counter.to_be_bytes());
}

fn gf_mul(mut x: u128, mut v: u128) -> u128 {
    const R: u128 = 0xe100_0000_0000_0000_0000_0000_0000_0000;
    let mut z = 0u128;
    for _ in 0..128 {
        if (x & (1 << 127)) != 0 {
            z ^= v;
        }
        let lsb = (v & 1) != 0;
        v >>= 1;
        if lsb {
            v ^= R;
        }
        x <<= 1;
    }
    z
}

#[cfg(test)]
mod tests {
    use super::{gf_mul, ghash};

    #[test]
    fn ghash_empty_is_zero() {
        assert_eq!(ghash(&[0u8; 16], &[]), [0u8; 16]);
    }

    #[test]
    fn gf_mul_identity_cases() {
        assert_eq!(gf_mul(0, 0x1234), 0);
        assert_eq!(gf_mul(0x1234, 0), 0);
    }
}
