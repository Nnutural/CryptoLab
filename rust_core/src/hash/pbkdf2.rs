//! PBKDF2 (RFC 8018 / NIST SP 800-132) — password-based key derivation.
//!
//! Iterations should be at least 100,000 for new deployments. The Rust core
//! enforces the RFC validity floor; the HTTP schema applies the stricter
//! product-facing floor used by this teaching service.

use crate::error::{CryptoError, CryptoResult};
use crate::hash::hmac::hmac_sha256;

const H_LEN: usize = 32;

/// PBKDF2-HMAC-SHA-256 per RFC 8018 §5.2.
///
/// `key_len` is the desired derived-key length in bytes and must satisfy
/// `1 <= key_len <= (2^32 - 1) * hLen`, where `hLen = 32`.
pub fn pbkdf2_hmac_sha256(
    password: &[u8],
    salt: &[u8],
    iterations: u32,
    key_len: usize,
) -> CryptoResult<Vec<u8>> {
    if iterations == 0 {
        return Err(CryptoError::InvalidParameter(
            "PBKDF2 iterations must be at least 1".to_string(),
        ));
    }
    if key_len == 0 {
        return Err(CryptoError::InvalidParameter(
            "PBKDF2 key_len must be greater than 0".to_string(),
        ));
    }

    let max_len = (u32::MAX as u64) * (H_LEN as u64);
    if (key_len as u64) > max_len {
        return Err(CryptoError::InvalidParameter(format!(
            "PBKDF2 key_len must be <= {max_len}"
        )));
    }

    let blocks = key_len.div_ceil(H_LEN);
    let mut derived = Vec::with_capacity(blocks * H_LEN);
    let mut salt_block = Vec::with_capacity(salt.len() + 4);

    for block_index in 1..=blocks {
        salt_block.clear();
        salt_block.extend_from_slice(salt);
        salt_block.extend_from_slice(&(block_index as u32).to_be_bytes());

        let mut u = hmac_sha256(password, &salt_block);
        let mut t = u;
        for _ in 1..iterations {
            u = hmac_sha256(password, &u);
            for i in 0..H_LEN {
                t[i] ^= u[i];
            }
        }
        derived.extend_from_slice(&t);
    }

    derived.truncate(key_len);
    Ok(derived)
}

#[cfg(test)]
mod tests {
    use super::pbkdf2_hmac_sha256;

    #[test]
    fn pbkdf2_hmac_sha256_known_vectors() {
        // Vectors cross-checked against Python hashlib.pbkdf2_hmac("sha256", ...)
        // and RustCrypto pbkdf2/Hmac<Sha256> reference outputs.
        assert_eq!(
            hex::encode(pbkdf2_hmac_sha256(b"password", b"salt", 1, 32).expect("valid vector")),
            "120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b"
        );
        assert_eq!(
            hex::encode(pbkdf2_hmac_sha256(b"password", b"salt", 2, 32).expect("valid vector")),
            "ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43"
        );
        assert_eq!(
            hex::encode(pbkdf2_hmac_sha256(b"password", b"salt", 4096, 32).expect("valid vector")),
            "c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a"
        );
    }

    #[test]
    fn rejects_invalid_parameters() {
        assert!(pbkdf2_hmac_sha256(b"password", b"salt", 0, 32).is_err());
        assert!(pbkdf2_hmac_sha256(b"password", b"salt", 1, 0).is_err());
    }
}
