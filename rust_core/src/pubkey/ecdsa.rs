//! ECDSA (FIPS 186-5).
//!
//! **Important**: per the CryptoLab security policy, `k` is ALWAYS derived
//! deterministically per RFC 6979. We do NOT expose a `k`-accepting overload
//! — re-used / biased `k` enables private-key recovery (Sony PS3 case).

use crate::error::CryptoResult;

/// ECDSA sign. Returns `(r, s)` big-endian.
pub fn sign(_message: &[u8], _d: &[u8], _curve: &str) -> CryptoResult<(Vec<u8>, Vec<u8>)> {
    todo!("hash → e; k = RFC6979(d, m); R = k·G; r = Rx mod n; s = k^-1 (e + r·d) mod n")
}

/// ECDSA verify. Returns `Ok(())` on valid, `Err(SignatureInvalid)` otherwise.
pub fn verify(
    _message: &[u8],
    _r: &[u8],
    _s: &[u8],
    _px: &[u8],
    _py: &[u8],
    _curve: &str,
) -> CryptoResult<()> {
    todo!("u1 = e·s^-1, u2 = r·s^-1; X = u1·G + u2·Q; r ?= Xx mod n")
}
