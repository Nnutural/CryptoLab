//! 仅供教学演示，禁止在 production code path 调用。

use num_bigint::BigUint;
use num_integer::Integer;
use num_traits::{One, Zero};

use crate::bigint::CryptoBigInt;
use crate::error::{CryptoError, CryptoResult};
use crate::hash::sha2::sha256;
use crate::pubkey::ecc::{scalar_mul_point, Curve};
use crate::pubkey::rsa::RsaKeyPair;

/// RSA 教学路径：无填充直接幂运算 `c = m^e mod n`。
///
/// 调用方保证 `m < n`；此函数不做 PKCS#1 / OAEP 包裹，只用于小指数攻击演示。
pub fn rsa_unsafe_encrypt_raw(msg: &BigUint, n: &BigUint, e: &BigUint) -> BigUint {
    msg.modpow(e, n)
}

/// 整数立方根，返回 `floor(c^(1/3))`。
///
/// 使用 Newton 迭代，收敛到不再下降后再做一次边界修正。
pub fn integer_cube_root(c: &BigUint) -> BigUint {
    if c.is_zero() || *c == BigUint::one() {
        return c.clone();
    }

    let three = BigUint::from(3u32);
    let two = BigUint::from(2u32);
    let mut x = BigUint::one() << c.bits().div_ceil(3);

    loop {
        let x_squared = &x * &x;
        let next = ((&two * &x) + (c / x_squared)) / &three;
        if next >= x {
            break;
        }
        x = next;
    }

    let one = BigUint::one();
    while {
        let candidate = &x + &one;
        &candidate * &candidate * &candidate <= *c
    } {
        x += &one;
    }
    while &x * &x * &x > *c {
        x -= &one;
    }
    x
}

/// 教学路径：允许 `e < 65537` 的 RSA keygen；其余约束与生产 keygen 一致。
pub fn rsa_unsafe_generate_keypair(bits: usize, e: u64) -> CryptoResult<RsaKeyPair> {
    if bits < 1024 || bits % 2 != 0 {
        return Err(CryptoError::InvalidParameter(format!(
            "RSA key size must be an even value >= 1024 bits, got {bits}"
        )));
    }
    if e < 3 || e % 2 == 0 {
        return Err(CryptoError::InvalidParameter(format!(
            "RSA exponent {e} is invalid for the demo path"
        )));
    }

    let e_big = BigUint::from(e);
    let one = BigUint::one();
    loop {
        let p = CryptoBigInt::random_prime(bits / 2)?.0;
        let mut q = CryptoBigInt::random_prime(bits / 2)?.0;
        while q == p {
            q = CryptoBigInt::random_prime(bits / 2)?.0;
        }

        let p_minus_one = &p - &one;
        let q_minus_one = &q - &one;
        if e_big.gcd(&p_minus_one) != one || e_big.gcd(&q_minus_one) != one {
            continue;
        }

        let n = &p * &q;
        let phi = &p_minus_one * &q_minus_one;
        let d = CryptoBigInt(e_big.clone())
            .mod_inverse(&CryptoBigInt(phi))
            .ok_or_else(|| CryptoError::BigIntError("RSA d inverse missing".to_string()))?
            .0;
        let dp = &d % &p_minus_one;
        let dq = &d % &q_minus_one;
        let qinv = CryptoBigInt(q.clone())
            .mod_inverse(&CryptoBigInt(p.clone()))
            .ok_or_else(|| CryptoError::BigIntError("RSA q inverse missing".to_string()))?
            .0;
        return Ok(RsaKeyPair {
            n,
            e: e_big,
            d,
            p,
            q,
            dp,
            dq,
            qinv,
        });
    }
}

/// ECDSA 教学路径：使用调用方给定的 `k` 签名，绕过 RFC 6979。
pub fn ecdsa_sign_with_explicit_k(
    msg: &[u8],
    d: &BigUint,
    k: &BigUint,
    curve: &Curve,
) -> CryptoResult<(BigUint, BigUint)> {
    validate_scalar(d, &curve.n, "ECDSA private scalar")?;
    validate_scalar(k, &curve.n, "ECDSA nonce k")?;

    let h = hash_to_scalar(msg, &curve.n);
    let r_point = scalar_mul_point(curve, &curve.g, k)?;
    if r_point.infinity {
        return Err(CryptoError::InvalidParameter(
            "ECDSA explicit k produced point at infinity".to_string(),
        ));
    }
    let r = &r_point.x % &curve.n;
    if r.is_zero() {
        return Err(CryptoError::InvalidParameter(
            "ECDSA explicit k produced r = 0".to_string(),
        ));
    }

    let k_inv = CryptoBigInt(k.clone())
        .mod_inverse(&CryptoBigInt(curve.n.clone()))
        .ok_or_else(|| CryptoError::BigIntError("ECDSA k inverse missing".to_string()))?
        .0;
    let s = (k_inv * (&h + &r * d)) % &curve.n;
    if s.is_zero() {
        return Err(CryptoError::InvalidParameter(
            "ECDSA explicit k produced s = 0".to_string(),
        ));
    }
    Ok((r, s))
}

/// ECDSA 教学路径：从 `k` 重用攻击数据反解私钥 `d`。
///
/// 公式：`k = (h1 - h2) * (s1 - s2)^-1 mod n`，
/// `d = (s1 * k - h1) * r^-1 mod n`。
pub fn ecdsa_recover_d_from_k_reuse(
    r: &BigUint,
    s1: &BigUint,
    s2: &BigUint,
    h1: &BigUint,
    h2: &BigUint,
    curve: &Curve,
) -> CryptoResult<BigUint> {
    validate_scalar(r, &curve.n, "ECDSA r")?;
    validate_scalar(s1, &curve.n, "ECDSA s1")?;
    validate_scalar(s2, &curve.n, "ECDSA s2")?;

    let s_diff = mod_sub(s1, s2, &curve.n);
    let h_diff = mod_sub(&(h1 % &curve.n), &(h2 % &curve.n), &curve.n);
    let s_diff_inv = CryptoBigInt(s_diff)
        .mod_inverse(&CryptoBigInt(curve.n.clone()))
        .ok_or_else(|| CryptoError::BigIntError("ECDSA s difference inverse missing".to_string()))?
        .0;
    let k = (h_diff * s_diff_inv) % &curve.n;
    validate_scalar(&k, &curve.n, "recovered ECDSA k")?;

    let r_inv = CryptoBigInt(r.clone())
        .mod_inverse(&CryptoBigInt(curve.n.clone()))
        .ok_or_else(|| CryptoError::BigIntError("ECDSA r inverse missing".to_string()))?
        .0;
    let numerator = mod_sub(&((s1 * &k) % &curve.n), &(h1 % &curve.n), &curve.n);
    Ok((numerator * r_inv) % &curve.n)
}

fn validate_scalar(value: &BigUint, n: &BigUint, label: &str) -> CryptoResult<()> {
    if value.is_zero() || value >= n {
        return Err(CryptoError::InvalidParameter(format!(
            "{label} out of range"
        )));
    }
    Ok(())
}

fn hash_to_scalar(message: &[u8], n: &BigUint) -> BigUint {
    bits2int(&sha256(message), n.bits() as usize)
}

fn bits2int(bytes: &[u8], qlen: usize) -> BigUint {
    let mut value = BigUint::from_bytes_be(bytes);
    let blen = bytes.len() * 8;
    if blen > qlen {
        value >>= blen - qlen;
    }
    value
}

fn mod_sub(a: &BigUint, b: &BigUint, modulus: &BigUint) -> BigUint {
    if a >= b {
        (a - b) % modulus
    } else {
        (a + modulus - b) % modulus
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::pubkey::ecc::{curve, to_fixed_bytes};

    #[test]
    fn cube_root_exact_and_floor_cases() {
        let exact = BigUint::from(12_167u32);
        assert_eq!(integer_cube_root(&exact), BigUint::from(23u32));
        assert_eq!(integer_cube_root(&(exact + 10u32)), BigUint::from(23u32));
    }

    #[test]
    fn raw_rsa_encrypt_is_plain_modpow() {
        let msg = BigUint::from(42u32);
        let n = BigUint::from(3233u32);
        let e = BigUint::from(17u32);
        assert_eq!(rsa_unsafe_encrypt_raw(&msg, &n, &e), msg.modpow(&e, &n));
    }

    #[test]
    fn ecdsa_recover_d_from_reused_k() {
        let curve = curve("secp160r1").expect("curve");
        let d = BigUint::from_bytes_be(
            &hex::decode("9717619397619fc8e6c73ca2d0c2ba2a2c4e2a45").expect("valid hex"),
        );
        let k = BigUint::from(123_456_789u64);
        let msg1 = b"message one";
        let msg2 = b"message two";
        let (r1, s1) = ecdsa_sign_with_explicit_k(msg1, &d, &k, &curve).expect("sign1");
        let (r2, s2) = ecdsa_sign_with_explicit_k(msg2, &d, &k, &curve).expect("sign2");
        assert_eq!(r1, r2);
        let h1 = hash_to_scalar(msg1, &curve.n);
        let h2 = hash_to_scalar(msg2, &curve.n);
        let recovered =
            ecdsa_recover_d_from_k_reuse(&r1, &s1, &s2, &h1, &h2, &curve).expect("recover");
        assert_eq!(to_fixed_bytes(&recovered, 21), to_fixed_bytes(&d, 21));
    }
}
