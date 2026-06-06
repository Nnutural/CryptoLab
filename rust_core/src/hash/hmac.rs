//! HMAC (RFC 2104) — Keyed-Hashing for Message Authentication.

use subtle::ConstantTimeEq;

use crate::hash::sha1::Sha1;
use crate::hash::sha2::Sha256;
use crate::traits::HashAlgorithm;

/// Compute HMAC generically over any [`HashAlgorithm`] per RFC 2104.
pub fn hmac<H: HashAlgorithm>(key: &[u8], message: &[u8]) -> Vec<u8> {
    let mut key_block = vec![0u8; H::BLOCK_SIZE];
    if key.len() > H::BLOCK_SIZE {
        let hashed_key = H::digest(key);
        key_block[..hashed_key.len()].copy_from_slice(&hashed_key);
    } else {
        key_block[..key.len()].copy_from_slice(key);
    }

    let mut ipad = vec![0x36u8; H::BLOCK_SIZE];
    let mut opad = vec![0x5cu8; H::BLOCK_SIZE];
    for i in 0..H::BLOCK_SIZE {
        ipad[i] ^= key_block[i];
        opad[i] ^= key_block[i];
    }

    let mut inner = H::default();
    inner.update(&ipad);
    inner.update(message);
    let mut inner_digest = vec![0u8; H::DIGEST_SIZE];
    let inner_result = inner.finalize_into(&mut inner_digest);
    debug_assert!(inner_result.is_ok());

    let mut outer = H::default();
    outer.update(&opad);
    outer.update(&inner_digest);
    let mut tag = vec![0u8; H::DIGEST_SIZE];
    let outer_result = outer.finalize_into(&mut tag);
    debug_assert!(outer_result.is_ok());
    tag
}

/// Compute HMAC-SHA-1 per RFC 2104 / RFC 2202. Educational use only.
pub fn hmac_sha1(key: &[u8], message: &[u8]) -> [u8; 20] {
    let tag = hmac::<Sha1>(key, message);
    let mut out = [0u8; 20];
    out.copy_from_slice(&tag);
    out
}

/// Compute HMAC-SHA-256 per RFC 2104 / RFC 4231.
pub fn hmac_sha256(key: &[u8], message: &[u8]) -> [u8; 32] {
    let tag = hmac::<Sha256>(key, message);
    let mut out = [0u8; 32];
    out.copy_from_slice(&tag);
    out
}

/// Verify an HMAC-SHA-256 tag using constant-time comparison.
pub fn verify_hmac_sha256(key: &[u8], message: &[u8], tag: &[u8]) -> bool {
    hmac_sha256(key, message).ct_eq(tag).into()
}

#[cfg(test)]
mod tests {
    use super::{hmac_sha1, hmac_sha256, verify_hmac_sha256};

    #[test]
    fn rfc_2202_hmac_sha1_vectors() {
        assert_eq!(
            hex::encode(hmac_sha1(&[0x0b; 20], b"Hi There")),
            "b617318655057264e28bc0b6fb378c8ef146be00"
        );
        assert_eq!(
            hex::encode(hmac_sha1(b"Jefe", b"what do ya want for nothing?")),
            "effcdf6ae5eb2fa2d27416d5f184df9c259a7c79"
        );
        assert_eq!(
            hex::encode(hmac_sha1(&[0xaa; 20], &[0xdd; 50])),
            "125d7342b9ac11cd91a39af48aa17b4f63f175d3"
        );
    }

    #[test]
    fn rfc_4231_hmac_sha256_vectors() {
        assert_eq!(
            hex::encode(hmac_sha256(&[0x0b; 20], b"Hi There")),
            "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        );
        assert_eq!(
            hex::encode(hmac_sha256(b"Jefe", b"what do ya want for nothing?")),
            "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
        );
        assert_eq!(
            hex::encode(hmac_sha256(&[0xaa; 20], &[0xdd; 50])),
            "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe"
        );
    }

    #[test]
    fn verify_hmac_sha256_uses_constant_time_compare_path() {
        let tag = hmac_sha256(b"key", b"message");
        assert!(verify_hmac_sha256(b"key", b"message", &tag));
        assert!(!verify_hmac_sha256(b"key", b"message2", &tag));
    }
}
