//! Cryptographic big-integer wrapper.
//!
//! Thin wrapper around [`num_bigint::BigUint`] that adds the operations RSA
//! and ECC actually need: Montgomery-style modular exponentiation, modular
//! inverse via extended Euclid, Miller-Rabin primality testing, and CSPRNG
//! prime generation. Concrete impls are left as `todo!()` at init time.

use num_bigint::BigUint;

use crate::error::CryptoResult;

/// A non-negative big integer with crypto-flavored operations attached.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CryptoBigInt(pub BigUint);

impl CryptoBigInt {
    /// Construct from big-endian bytes.
    pub fn from_bytes_be(bytes: &[u8]) -> Self {
        Self(BigUint::from_bytes_be(bytes))
    }

    /// Serialize as big-endian bytes (no leading zero).
    pub fn to_bytes_be(&self) -> Vec<u8> {
        self.0.to_bytes_be()
    }

    /// Compute `self^exp mod modulus` using Montgomery (or square-and-multiply).
    ///
    /// MUST be constant-time with respect to `exp` to defend against timing
    /// attacks on RSA private exponents.
    pub fn mod_pow(&self, _exp: &Self, _modulus: &Self) -> CryptoResult<Self> {
        todo!("Montgomery modular exponentiation — see RFC 8017 §5.1.2")
    }

    /// Modular inverse via extended Euclidean algorithm.
    ///
    /// Returns `None` when `gcd(self, modulus) != 1`.
    pub fn mod_inverse(&self, _modulus: &Self) -> CryptoResult<Option<Self>> {
        todo!("extended Euclid; see HAC §14.61")
    }

    /// Greatest common divisor.
    pub fn gcd(&self, _other: &Self) -> Self {
        todo!("binary GCD")
    }

    /// Miller-Rabin probabilistic primality test with `rounds` witnesses.
    ///
    /// For RSA-1024 use at least 40 rounds (false-positive ≤ 2⁻⁸⁰).
    pub fn is_prime_miller_rabin(&self, _rounds: u32) -> bool {
        todo!("Miller-Rabin; sample witnesses from OsRng")
    }

    /// Generate a `bits`-bit random prime using OS CSPRNG + Miller-Rabin.
    pub fn random_prime(_bits: usize) -> CryptoResult<Self> {
        todo!("rejection sampling against random_below + is_prime_miller_rabin")
    }

    /// Uniform random in `[0, upper_bound)`.
    pub fn random_below(_upper_bound: &Self) -> CryptoResult<Self> {
        todo!("OsRng-backed uniform sampling")
    }
}
