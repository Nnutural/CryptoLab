//! CTR — Counter mode (NIST SP 800-38A §6.5).
//!
//! Encrypt and decrypt are the same operation: XOR the keystream produced
//! by encrypting `nonce || counter` with the data.

use crate::error::{CryptoError, CryptoResult};
use crate::traits::SymmetricCipher;

/// CTR XOR — used for both encrypt and decrypt.
pub fn xor_keystream<C: SymmetricCipher>(
    cipher: &C,
    data: &[u8],
    nonce: &[u8],
    initial_counter: u64,
) -> CryptoResult<Vec<u8>> {
    if nonce.len() != C::BLOCK_SIZE {
        return Err(CryptoError::InvalidIvLength {
            expected: C::BLOCK_SIZE,
            actual: nonce.len(),
        });
    }

    let mut counter_block = nonce.to_vec();
    if initial_counter != 0 {
        add_to_last_u32(&mut counter_block, initial_counter as u32);
    }

    let mut out = Vec::with_capacity(data.len());
    for chunk in data.chunks(C::BLOCK_SIZE) {
        let mut keystream = counter_block.clone();
        cipher.encrypt_block(&mut keystream)?;
        out.extend(chunk.iter().zip(keystream.iter()).map(|(a, b)| a ^ b));
        inc32(&mut counter_block);
    }
    Ok(out)
}

fn inc32(block: &mut [u8]) {
    add_to_last_u32(block, 1);
}

fn add_to_last_u32(block: &mut [u8], value: u32) {
    let len = block.len();
    let mut counter = u32::from_be_bytes([block[len - 4], block[len - 3], block[len - 2], block[len - 1]]);
    counter = counter.wrapping_add(value);
    block[len - 4..].copy_from_slice(&counter.to_be_bytes());
}
