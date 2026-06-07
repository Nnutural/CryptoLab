//! ECDSA (FIPS 186-4) with deterministic RFC 6979 nonces.
//!
//! `k` is derived with HMAC-SHA256 through [`crate::hash::hmac::hmac_sha256`].
//! No signing path accepts caller-provided randomness.

use num_bigint::BigUint;
use num_traits::{One, Zero};
use subtle::ConstantTimeEq;

use crate::bigint::CryptoBigInt;
use crate::error::{CryptoError, CryptoResult};
use crate::hash::hmac::hmac_sha256;
use crate::hash::sha2::sha256;
use crate::pubkey::ecc::{
    curve, is_on_curve, point_add, scalar_mul_point, to_fixed_bytes, AffinePoint,
};

/// ECDSA sign. Returns `(r, s)` big-endian.
pub fn sign(message: &[u8], d: &[u8], curve_name: &str) -> CryptoResult<(Vec<u8>, Vec<u8>)> {
    let curve = curve(curve_name)?;
    let d = BigUint::from_bytes_be(d);
    validate_private_scalar(&d, &curve.n)?;
    let e = hash_to_scalar(message, &curve.n);
    let order_len = order_len(&curve.n);

    let mut retry = 0u32;
    loop {
        let k = rfc6979_generate_k(&d, message, &curve.n, retry);
        let r_point = scalar_mul_point(&curve, &curve.g, &k)?;
        if r_point.infinity {
            retry = retry.wrapping_add(1);
            continue;
        }
        let r = &r_point.x % &curve.n;
        if r.is_zero() {
            retry = retry.wrapping_add(1);
            continue;
        }
        let k_inv = CryptoBigInt(k)
            .mod_inverse(&CryptoBigInt(curve.n.clone()))
            .ok_or_else(|| CryptoError::BigIntError("ECDSA k inverse missing".to_string()))?
            .0;
        let s = (k_inv * (&e + &r * &d)) % &curve.n;
        if s.is_zero() {
            retry = retry.wrapping_add(1);
            continue;
        }
        return Ok((to_fixed_bytes(&r, order_len), to_fixed_bytes(&s, order_len)));
    }
}

/// ECDSA verify. Returns `Ok(())` on valid, `Err(SignatureInvalid)` otherwise.
pub fn verify(
    message: &[u8],
    r: &[u8],
    s: &[u8],
    px: &[u8],
    py: &[u8],
    curve_name: &str,
) -> CryptoResult<()> {
    let curve = curve(curve_name)?;
    let r = BigUint::from_bytes_be(r);
    let s = BigUint::from_bytes_be(s);
    if r.is_zero() || r >= curve.n || s.is_zero() || s >= curve.n {
        return Err(CryptoError::SignatureInvalid);
    }
    let q = AffinePoint {
        x: BigUint::from_bytes_be(px),
        y: BigUint::from_bytes_be(py),
        infinity: false,
    };
    if !is_on_curve(&curve, &q) {
        return Err(CryptoError::InvalidKey("ECDSA public key is off-curve".to_string()));
    }

    let e = hash_to_scalar(message, &curve.n);
    let s_inv = CryptoBigInt(s.clone())
        .mod_inverse(&CryptoBigInt(curve.n.clone()))
        .ok_or_else(|| CryptoError::SignatureInvalid)?
        .0;
    let u1 = (&e * &s_inv) % &curve.n;
    let u2 = (&r * &s_inv) % &curve.n;
    let p1 = scalar_mul_point(&curve, &curve.g, &u1)?;
    let p2 = scalar_mul_point(&curve, &q, &u2)?;
    let x = point_add(&curve, &p1, &p2)?;
    if x.infinity {
        return Err(CryptoError::SignatureInvalid);
    }
    let v = x.x % &curve.n;
    let len = order_len(&curve.n);
    if bool::from(to_fixed_bytes(&v, len).ct_eq(&to_fixed_bytes(&r, len))) {
        Ok(())
    } else {
        Err(CryptoError::SignatureInvalid)
    }
}

fn validate_private_scalar(d: &BigUint, n: &BigUint) -> CryptoResult<()> {
    if d.is_zero() || d >= n {
        return Err(CryptoError::InvalidKey(
            "ECDSA private scalar out of range".to_string(),
        ));
    }
    Ok(())
}

fn rfc6979_generate_k(d: &BigUint, message: &[u8], n: &BigUint, retry: u32) -> BigUint {
    let qlen = n.bits() as usize;
    let rlen = order_len(n);
    let bx = int2octets(d, rlen);
    let bh = bits2octets(&sha256(message), n);

    let mut v = vec![0x01u8; 32];
    let mut k = vec![0x00u8; 32];

    let mut input = Vec::with_capacity(v.len() + 1 + bx.len() + bh.len());
    input.extend_from_slice(&v);
    input.push(0x00);
    input.extend_from_slice(&bx);
    input.extend_from_slice(&bh);
    k = hmac_sha256(&k, &input).to_vec();
    v = hmac_sha256(&k, &v).to_vec();

    input.clear();
    input.extend_from_slice(&v);
    input.push(0x01);
    input.extend_from_slice(&bx);
    input.extend_from_slice(&bh);
    k = hmac_sha256(&k, &input).to_vec();
    v = hmac_sha256(&k, &v).to_vec();

    for _ in 0..=retry {
        loop {
            let mut t = Vec::with_capacity(rlen);
            while t.len() < rlen {
                v = hmac_sha256(&k, &v).to_vec();
                t.extend_from_slice(&v);
            }
            let secret = bits2int(&t, qlen);
            if secret >= BigUint::one() && secret < *n {
                if retry == 0 {
                    return secret;
                }
                break;
            }
            let mut retry_input = Vec::with_capacity(v.len() + 1);
            retry_input.extend_from_slice(&v);
            retry_input.push(0x00);
            k = hmac_sha256(&k, &retry_input).to_vec();
            v = hmac_sha256(&k, &v).to_vec();
        }
        let mut retry_input = Vec::with_capacity(v.len() + 1);
        retry_input.extend_from_slice(&v);
        retry_input.push(0x00);
        k = hmac_sha256(&k, &retry_input).to_vec();
        v = hmac_sha256(&k, &v).to_vec();
    }

    BigUint::one()
}

fn hash_to_scalar(message: &[u8], n: &BigUint) -> BigUint {
    bits2int(&sha256(message), n.bits() as usize)
}

fn bits2int(bytes: &[u8], qlen: usize) -> BigUint {
    let mut v = BigUint::from_bytes_be(bytes);
    let blen = bytes.len() * 8;
    if blen > qlen {
        v >>= blen - qlen;
    }
    v
}

fn bits2octets(hash: &[u8], n: &BigUint) -> Vec<u8> {
    let z1 = bits2int(hash, n.bits() as usize);
    let z2 = z1 % n;
    int2octets(&z2, order_len(n))
}

fn int2octets(value: &BigUint, len: usize) -> Vec<u8> {
    to_fixed_bytes(value, len)
}

fn order_len(n: &BigUint) -> usize {
    ((n.bits() + 7) / 8) as usize
}

#[cfg(test)]
mod tests {
    use super::*;

    fn hx(s: &str) -> Vec<u8> {
        hex::decode(s).expect("valid hex")
    }

    #[test]
    fn sign_verify_roundtrip() {
        let d = hx("9717619397619fc8e6c73ca2d0c2ba2a2c4e2a45");
        let curve = curve("secp160r1").expect("curve");
        let q = scalar_mul_point(&curve, &curve.g, &BigUint::from_bytes_be(&d)).expect("q");
        let msg = b"sample";
        let (r, s) = sign(msg, &d, "secp160r1").expect("sign");
        assert_eq!(hex::encode(&r), "00b28dc7224bae71617117ae60160360e0ff801830");
        assert_eq!(hex::encode(&s), "006767d5ffbfae5b56aa6c0381107e06a4a5413027");
        verify(
            msg,
            &r,
            &s,
            &to_fixed_bytes(&q.x, curve.field_len),
            &to_fixed_bytes(&q.y, curve.field_len),
            "secp160r1",
        )
        .expect("verify");
    }

    #[test]
    fn tampering_fails() {
        let d = hx("9717619397619fc8e6c73ca2d0c2ba2a2c4e2a45");
        let curve = curve("secp160r1").expect("curve");
        let q = scalar_mul_point(&curve, &curve.g, &BigUint::from_bytes_be(&d)).expect("q");
        let (mut r, s) = sign(b"sample", &d, "secp160r1").expect("sign");
        assert!(verify(
            b"test",
            &r,
            &s,
            &to_fixed_bytes(&q.x, curve.field_len),
            &to_fixed_bytes(&q.y, curve.field_len),
            "secp160r1",
        )
        .is_err());
        r[0] ^= 1;
        assert!(verify(
            b"sample",
            &r,
            &s,
            &to_fixed_bytes(&q.x, curve.field_len),
            &to_fixed_bytes(&q.y, curve.field_len),
            "secp160r1",
        )
        .is_err());
    }
}
