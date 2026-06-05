//! CBC — Cipher Block Chaining (NIST SP 800-38A §6.2).

use crate::error::CryptoResult;
use crate::modes::Padding;
use crate::traits::SymmetricCipher;

/// CBC encrypt: `C_i = E_K(P_i ⊕ C_{i-1})`, with `C_{-1} = IV`.
pub fn encrypt<C: SymmetricCipher>(
    _cipher: &C,
    _plaintext: &[u8],
    _iv: &[u8],
    _padding: Padding,
) -> CryptoResult<Vec<u8>> {
    todo!("xor plaintext block with prev ciphertext (or IV) → encrypt_block")
}

/// CBC decrypt: `P_i = D_K(C_i) ⊕ C_{i-1}`.
pub fn decrypt<C: SymmetricCipher>(
    _cipher: &C,
    _ciphertext: &[u8],
    _iv: &[u8],
    _padding: Padding,
) -> CryptoResult<Vec<u8>> {
    todo!("decrypt_block → xor with prev ciphertext (or IV) → unpad")
}
