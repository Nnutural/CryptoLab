//! Cryptographic big-integer wrapper.
//!
//! Modular exponentiation delegates to [`num_bigint::BigUint::modpow`], which
//! uses optimized modular arithmetic suitable for RSA-sized operands. Prime
//! generation and Miller-Rabin witnesses are sampled exclusively from `OsRng`.

use num_bigint::{BigInt, BigUint, RandBigInt, Sign};
use num_integer::Integer;
use num_traits::{One, Signed, Zero};
use rand::rngs::OsRng;
use rand::RngCore;

use crate::error::{CryptoError, CryptoResult};

/// A non-negative big integer with crypto-flavored operations attached.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
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

    /// Compute `self^exp mod modulus` using the optimized `num-bigint` path.
    pub fn mod_pow(&self, exp: &Self, modulus: &Self) -> CryptoResult<Self> {
        if modulus.0.is_zero() {
            return Err(CryptoError::BigIntError(
                "modular exponentiation with zero modulus".to_string(),
            ));
        }
        Ok(Self(self.0.modpow(&exp.0, &modulus.0)))
    }

    /// Modular inverse via extended Euclidean algorithm.
    ///
    /// Returns `None` when `gcd(self, modulus) != 1` or `modulus == 0`.
    pub fn mod_inverse(&self, modulus: &Self) -> Option<Self> {
        if modulus.0.is_zero() {
            return None;
        }

        let mut t = BigInt::zero();
        let mut new_t = BigInt::one();
        let mut r = BigInt::from_biguint(Sign::Plus, modulus.0.clone());
        let mut new_r = BigInt::from_biguint(Sign::Plus, (&self.0 % &modulus.0).clone());

        while !new_r.is_zero() {
            let q = &r / &new_r;
            let next_t = &t - &q * &new_t;
            t = new_t;
            new_t = next_t;

            let next_r = &r - q * &new_r;
            r = new_r;
            new_r = next_r;
        }

        if r != BigInt::one() {
            return None;
        }
        if t.is_negative() {
            t += BigInt::from_biguint(Sign::Plus, modulus.0.clone());
        }
        t.to_biguint().map(Self)
    }

    /// Greatest common divisor.
    pub fn gcd(&self, other: &Self) -> Self {
        Self(self.0.gcd(&other.0))
    }

    /// Miller-Rabin probabilistic primality test with `rounds` witnesses.
    pub fn is_prime_miller_rabin(&self, rounds: u32) -> bool {
        let n = &self.0;
        let zero = BigUint::zero();
        let one = BigUint::one();
        let two = BigUint::from(2u32);

        if *n < two {
            return false;
        }
        const SMALL_PRIMES: [u32; 6] = [2, 3, 5, 7, 11, 13];
        for p in SMALL_PRIMES {
            let p_big = BigUint::from(p);
            if *n == p_big {
                return true;
            }
            if n % &p_big == zero {
                return false;
            }
        }

        let n_minus_one = n - &one;
        let mut d = n_minus_one.clone();
        let mut s = 0u32;
        while (&d & &one).is_zero() {
            d >>= 1usize;
            s += 1;
        }

        let mut rng = OsRng;
        'witness: for _ in 0..rounds {
            let a = rng.gen_biguint_range(&two, &n_minus_one);
            let mut x = a.modpow(&d, n);
            if x == one || x == n_minus_one {
                continue;
            }
            for _ in 1..s {
                x = x.modpow(&two, n);
                if x == n_minus_one {
                    continue 'witness;
                }
            }
            return false;
        }
        true
    }

    /// Generate a `bits`-bit random prime using OS CSPRNG + Miller-Rabin.
    pub fn random_prime(bits: usize) -> CryptoResult<Self> {
        if bits < 2 {
            return Err(CryptoError::InvalidParameter(
                "prime bit length must be at least 2".to_string(),
            ));
        }
        let byte_len = (bits + 7) / 8;
        let excess_bits = byte_len * 8 - bits;
        let mut rng = OsRng;

        loop {
            let mut bytes = vec![0u8; byte_len];
            rng.fill_bytes(&mut bytes);
            if excess_bits > 0 {
                bytes[0] &= 0xff >> excess_bits;
            }
            let top_bit = 7usize.saturating_sub(excess_bits);
            bytes[0] |= 1u8 << top_bit;
            bytes[byte_len - 1] |= 1;

            let candidate = Self(BigUint::from_bytes_be(&bytes));
            if candidate.is_prime_miller_rabin(40) {
                return Ok(candidate);
            }
        }
    }

    /// Uniform random in `[0, upper_bound)`.
    pub fn random_below(upper_bound: &Self) -> CryptoResult<Self> {
        if upper_bound.0.is_zero() {
            return Err(CryptoError::InvalidParameter(
                "random_below upper bound must be positive".to_string(),
            ));
        }
        let mut rng = OsRng;
        Ok(Self(rng.gen_biguint_below(&upper_bound.0)))
    }
}

#[cfg(test)]
mod tests {
    use super::CryptoBigInt;
    use num_bigint::BigUint;
    use num_traits::One;

    #[test]
    fn mod_inverse_self_check() {
        let a = CryptoBigInt(BigUint::from(17u32));
        let n = CryptoBigInt(BigUint::from(3120u32));
        let inv = a.mod_inverse(&n).expect("inverse exists");
        assert_eq!((&a.0 * &inv.0) % &n.0, BigUint::one());
    }

    #[test]
    fn miller_rabin_accepts_first_100_odd_primes() {
        let primes = [
            3u32, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79,
            83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
            173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263,
            269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367,
            373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
            467, 479, 487, 491, 499, 503, 509, 521, 523, 541,
        ];
        for prime in primes {
            assert!(CryptoBigInt(BigUint::from(prime)).is_prime_miller_rabin(8));
        }
    }

    #[ignore = "512-bit prime generation is intentionally slow"]
    #[test]
    fn random_512_bit_prime_is_prime() {
        let p = CryptoBigInt::random_prime(512).expect("prime");
        assert_eq!(p.0.bits(), 512);
        assert!(p.is_prime_miller_rabin(40));
    }
}
