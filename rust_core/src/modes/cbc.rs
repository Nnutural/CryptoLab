//! CBC — Cipher Block Chaining (NIST SP 800-38A §6.2).

use crate::error::{CryptoError, CryptoResult};
use crate::modes::Padding;
use crate::traits::SymmetricCipher;

/// CBC encrypt: `C_i = E_K(P_i ⊕ C_{i-1})`, with `C_{-1} = IV`.
pub fn encrypt<C: SymmetricCipher>(
    cipher: &C,
    plaintext: &[u8],
    iv: &[u8],
    padding: Padding,
) -> CryptoResult<Vec<u8>> {
    if iv.len() != C::BLOCK_SIZE {
        return Err(CryptoError::InvalidIvLength {
            expected: C::BLOCK_SIZE,
            actual: iv.len(),
        });
    }
    let mut out = plaintext.to_vec();
    padding.pad(&mut out, C::BLOCK_SIZE)?;

    let mut prev = iv.to_vec();
    for block in out.chunks_exact_mut(C::BLOCK_SIZE) {
        for i in 0..C::BLOCK_SIZE {
            block[i] ^= prev[i];
        }
        cipher.encrypt_block(block)?;
        prev.copy_from_slice(block);
    }
    Ok(out)
}

/// CBC decrypt: `P_i = D_K(C_i) ⊕ C_{i-1}`.
pub fn decrypt<C: SymmetricCipher>(
    cipher: &C,
    ciphertext: &[u8],
    iv: &[u8],
    padding: Padding,
) -> CryptoResult<Vec<u8>> {
    if iv.len() != C::BLOCK_SIZE {
        return Err(CryptoError::InvalidIvLength {
            expected: C::BLOCK_SIZE,
            actual: iv.len(),
        });
    }
    if ciphertext.len() % C::BLOCK_SIZE != 0 {
        return Err(CryptoError::InvalidInputLength(format!(
            "CBC ciphertext length {} is not a multiple of block size {}",
            ciphertext.len(),
            C::BLOCK_SIZE
        )));
    }

    let mut out = Vec::with_capacity(ciphertext.len());
    let mut prev = iv.to_vec();
    for chunk in ciphertext.chunks_exact(C::BLOCK_SIZE) {
        let mut block = chunk.to_vec();
        cipher.decrypt_block(&mut block)?;
        for i in 0..C::BLOCK_SIZE {
            block[i] ^= prev[i];
        }
        out.extend_from_slice(&block);
        prev.copy_from_slice(chunk);
    }
    padding.unpad(&mut out, C::BLOCK_SIZE)?;
    Ok(out)
}
