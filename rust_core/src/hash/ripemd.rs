//! RIPEMD-160 (Dobbertin, Bosselaers & Preneel, 1996).
//!
//! Teaching project note: the dual-pipeline RIPEMD-160 compression structure
//! is explained in the corresponding report chapter; this file wraps the
//! RustCrypto `ripemd` crate as the production implementation.

use ::ripemd::{Digest, Ripemd160};

/// One-shot RIPEMD-160 digest.
pub fn ripemd160(data: &[u8]) -> [u8; 20] {
    let digest = Ripemd160::digest(data);
    let mut out = [0u8; 20];
    out.copy_from_slice(&digest);
    out
}

#[cfg(test)]
mod tests {
    use super::ripemd160;

    #[test]
    fn original_ripemd160_vectors() {
        assert_eq!(
            hex::encode(ripemd160(b"")),
            "9c1185a5c5e9fc54612808977ee8f548b2258d31"
        );
        assert_eq!(
            hex::encode(ripemd160(b"abc")),
            "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc"
        );
    }
}
