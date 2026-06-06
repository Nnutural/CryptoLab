//! SHA-3 family (FIPS 202): SHA3-256 and SHA3-512.
//!
//! Teaching project note: the Keccak sponge construction is explained in the
//! corresponding report chapter; this file wraps the RustCrypto `sha3` crate
//! as the production implementation to avoid duplicating Keccak-f[1600].

use ::sha3::{Digest, Sha3_256, Sha3_512};

/// One-shot SHA3-256 digest per NIST FIPS 202.
pub fn sha3_256(data: &[u8]) -> [u8; 32] {
    let digest = Sha3_256::digest(data);
    let mut out = [0u8; 32];
    out.copy_from_slice(&digest);
    out
}

/// One-shot SHA3-512 digest per NIST FIPS 202.
pub fn sha3_512(data: &[u8]) -> [u8; 64] {
    let digest = Sha3_512::digest(data);
    let mut out = [0u8; 64];
    out.copy_from_slice(&digest);
    out
}

#[cfg(test)]
mod tests {
    use super::{sha3_256, sha3_512};

    #[test]
    fn fips_202_sha3_256_vectors() {
        assert_eq!(
            hex::encode(sha3_256(b"")),
            "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
        );
        assert_eq!(
            hex::encode(sha3_256(b"abc")),
            "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"
        );
    }

    #[test]
    fn fips_202_sha3_512_vectors() {
        assert_eq!(
            hex::encode(sha3_512(b"")),
            concat!(
                "a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc",
                "1475c80a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26"
            )
        );
        assert_eq!(
            hex::encode(sha3_512(b"abc")),
            concat!(
                "b751850b1a57168a5693cd924b6b096e08f621827444f70d884f5d0240d2712e",
                "10e116e9192af3c91a7ec57647e3934057340b4cf408d5a56592f8274eec53f0"
            )
        );
    }
}
