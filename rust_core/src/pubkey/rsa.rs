//! RSA-1024 hand implementation (RFC 8017 / PKCS #1 v2.2).
//!
//! Key generation flow:
//!   1. p, q ← random 512-bit primes (Miller-Rabin)
//!   2. n = p·q,  φ(n) = (p-1)(q-1)
//!   3. e = 65537  (smaller e is rejected — see attack-demo /rsa_low_exponent)
//!   4. d = e⁻¹ mod φ(n)
//!   5. Pre-compute CRT params dP, dQ, qInv for the private-op fast path.
//!
//! Padding schemes:
//!   - "pkcs1v15" — PKCS #1 v1.5 (legacy; vulnerable to Bleichenbacher)
//!   - "oaep"     — OAEP-MGF1-SHA256 (default; recommended)
//!   - "pss"      — PSS-MGF1-SHA256 (signing default)

use crate::error::{CryptoError, CryptoResult};

/// Generate a fresh RSA keypair of `bits` bits with public exponent `e`.
///
/// Returns big-endian byte representations of `(n, e, d, p, q)`.
/// `bits` must be a multiple of 8 and ≥ 1024.
/// `e` must be odd and ≥ 65537 (per [`crate::CLAUDE.md`] security red lines).
pub fn keygen(
    bits: usize,
    e: u64,
) -> CryptoResult<(Vec<u8>, Vec<u8>, Vec<u8>, Vec<u8>, Vec<u8>)> {
    if bits < 1024 {
        return Err(CryptoError::InvalidParameter(format!(
            "RSA key size {bits} bit < 1024"
        )));
    }
    if e < 65537 || e % 2 == 0 {
        return Err(CryptoError::InvalidParameter(format!(
            "RSA exponent {e} is unsafe (< 65537 or even)"
        )));
    }
    todo!("see module doc: prime gen → n,φ → d via mod_inverse → emit BE bytes")
}

/// RSA encrypt under the chosen padding ("oaep" or "pkcs1v15").
pub fn encrypt(
    _plaintext: &[u8],
    _n: &[u8],
    _e: &[u8],
    _padding: &str,
) -> CryptoResult<Vec<u8>> {
    todo!("pad plaintext to k bytes; m = OS2IP; c = m^e mod n; I2OSP back to bytes")
}

/// RSA decrypt under the chosen padding.
pub fn decrypt(
    _ciphertext: &[u8],
    _n: &[u8],
    _d: &[u8],
    _padding: &str,
) -> CryptoResult<Vec<u8>> {
    todo!("OS2IP ciphertext; m = c^d mod n (CRT fast path); strip padding constant-time")
}

/// RSA sign under PSS (recommended) or PKCS#1 v1.5 (legacy).
pub fn sign(
    _message: &[u8],
    _n: &[u8],
    _d: &[u8],
    _scheme: &str,
) -> CryptoResult<Vec<u8>> {
    todo!("EMSA-PSS-ENCODE or EMSA-PKCS1-v1_5; private op with CRT + blinding")
}

/// RSA verify. Returns `Ok(())` on match, `Err(SignatureInvalid)` otherwise.
pub fn verify(
    _message: &[u8],
    _signature: &[u8],
    _n: &[u8],
    _e: &[u8],
    _scheme: &str,
) -> CryptoResult<()> {
    todo!("public op then EMSA-PSS-VERIFY / strict PKCS#1 v1.5 byte equality")
}
