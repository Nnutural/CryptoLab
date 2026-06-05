//! CTR — Counter mode (NIST SP 800-38A §6.5).
//!
//! Encrypt and decrypt are the same operation: XOR the keystream produced
//! by encrypting `nonce || counter` with the data.

use crate::error::CryptoResult;
use crate::traits::SymmetricCipher;

/// CTR XOR — used for both encrypt and decrypt.
pub fn xor_keystream<C: SymmetricCipher>(
    _cipher: &C,
    _data: &[u8],
    _nonce: &[u8],
    _initial_counter: u64,
) -> CryptoResult<Vec<u8>> {
    todo!("for each block: encrypt_block(nonce || counter) → xor into data; increment counter")
}
