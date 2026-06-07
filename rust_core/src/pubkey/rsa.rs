//! RSA-1024 implementation (RFC 8017 / PKCS #1 v2.2).
//!
//! OAEP and PSS use MGF1-SHA256 from this crate's SHA-256 implementation.
//! PKCS#1 v1.5 is included only for teaching and compatibility demos; do not
//! use it in production protocols.

use num_bigint::BigUint;
use num_integer::Integer;
use num_traits::{One, Zero};
use rand::rngs::OsRng;
use rand::RngCore;
use subtle::ConstantTimeEq;

use crate::bigint::CryptoBigInt;
use crate::error::{CryptoError, CryptoResult};
use crate::hash::sha2::sha256;

const H_LEN: usize = 32;
const PSS_SALT_LEN: usize = 32;
const SHA256_DIGESTINFO_PREFIX: [u8; 19] = [
    0x30, 0x31, 0x30, 0x0d, 0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01,
    0x05, 0x00, 0x04, 0x20,
];

/// CRT-friendly RSA private key pair.
#[derive(Debug, Clone)]
pub struct RsaKeyPair {
    /// Public modulus.
    pub n: BigUint,
    /// Public exponent.
    pub e: BigUint,
    /// Private exponent.
    pub d: BigUint,
    /// First prime factor.
    pub p: BigUint,
    /// Second prime factor.
    pub q: BigUint,
    /// CRT exponent d mod (p - 1).
    pub dp: BigUint,
    /// CRT exponent d mod (q - 1).
    pub dq: BigUint,
    /// CRT coefficient q^-1 mod p.
    pub qinv: BigUint,
}

impl RsaKeyPair {
    /// Generate a fresh RSA keypair of `bits` bits with public exponent `e`.
    pub fn generate(bits: usize, e: u64) -> CryptoResult<Self> {
        if bits < 1024 || bits % 2 != 0 {
            return Err(CryptoError::InvalidParameter(format!(
                "RSA key size must be an even value >= 1024 bits, got {bits}"
            )));
        }
        if e < 65537 || e % 2 == 0 {
            return Err(CryptoError::InvalidParameter(format!(
                "RSA exponent {e} is unsafe (< 65537 or even)"
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
            return Ok(Self {
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

    fn private_op_crt(&self, c: &BigUint) -> BigUint {
        let m1 = c.modpow(&self.dp, &self.p);
        let m2 = c.modpow(&self.dq, &self.q);
        let diff = if m1 >= m2 {
            &m1 - &m2
        } else {
            &m1 + &self.p - &m2
        };
        let h = (&self.qinv * diff) % &self.p;
        &m2 + &self.q * h
    }
}

/// Generate a fresh RSA keypair of `bits` bits with public exponent `e`.
///
/// Returns big-endian byte representations of `(n, e, d, p, q)`.
pub fn keygen(
    bits: usize,
    e: u64,
) -> CryptoResult<(Vec<u8>, Vec<u8>, Vec<u8>, Vec<u8>, Vec<u8>)> {
    let key = RsaKeyPair::generate(bits, e)?;
    Ok((
        key.n.to_bytes_be(),
        key.e.to_bytes_be(),
        key.d.to_bytes_be(),
        key.p.to_bytes_be(),
        key.q.to_bytes_be(),
    ))
}

/// RSA encrypt under the chosen padding ("oaep" or "pkcs1v15").
pub fn encrypt(plaintext: &[u8], n: &[u8], e: &[u8], padding: &str) -> CryptoResult<Vec<u8>> {
    let n = BigUint::from_bytes_be(n);
    let e = BigUint::from_bytes_be(e);
    let k = modulus_len(&n)?;
    let em = match padding.to_ascii_lowercase().as_str() {
        "oaep" => oaep_encode(plaintext, k)?,
        "pkcs1v15" | "pkcs1-v1_5" => pkcs1v15_encrypt_encode(plaintext, k)?,
        other => {
            return Err(CryptoError::InvalidParameter(format!(
                "unsupported RSA encryption padding: {other}"
            )))
        }
    };
    let m = os2ip(&em);
    if m >= n {
        return Err(CryptoError::InvalidParameter(
            "encoded message representative >= modulus".to_string(),
        ));
    }
    let c = m.modpow(&e, &n);
    i2osp(&c, k)
}

/// RSA decrypt under the chosen padding.
pub fn decrypt(ciphertext: &[u8], n: &[u8], d: &[u8], padding: &str) -> CryptoResult<Vec<u8>> {
    let n = BigUint::from_bytes_be(n);
    let d = BigUint::from_bytes_be(d);
    let k = modulus_len(&n)?;
    if ciphertext.len() != k {
        return Err(CryptoError::InvalidInputLength(format!(
            "RSA ciphertext must be {k} bytes"
        )));
    }
    let c = os2ip(ciphertext);
    if c >= n {
        return Err(CryptoError::InvalidPadding);
    }
    let m = c.modpow(&d, &n);
    let em = i2osp(&m, k)?;
    match padding.to_ascii_lowercase().as_str() {
        "oaep" => oaep_decode(&em),
        "pkcs1v15" | "pkcs1-v1_5" => pkcs1v15_encrypt_decode(&em),
        other => Err(CryptoError::InvalidParameter(format!(
            "unsupported RSA encryption padding: {other}"
        ))),
    }
}

/// RSA OAEP decrypt using CRT private parameters.
pub fn decrypt_oaep_crt(
    ciphertext: &[u8],
    n: &[u8],
    d: &[u8],
    p: &[u8],
    q: &[u8],
) -> CryptoResult<Vec<u8>> {
    let key = private_from_parts(n, d, p, q)?;
    let k = modulus_len(&key.n)?;
    if ciphertext.len() != k {
        return Err(CryptoError::InvalidInputLength(format!(
            "RSA ciphertext must be {k} bytes"
        )));
    }
    let c = os2ip(ciphertext);
    if c >= key.n {
        return Err(CryptoError::InvalidPadding);
    }
    let em = i2osp(&key.private_op_crt(&c), k)?;
    oaep_decode(&em)
}

/// RSA sign under PSS (recommended) or PKCS#1 v1.5 (legacy).
pub fn sign(message: &[u8], n: &[u8], d: &[u8], scheme: &str) -> CryptoResult<Vec<u8>> {
    let n = BigUint::from_bytes_be(n);
    let d = BigUint::from_bytes_be(d);
    let k = modulus_len(&n)?;
    let em_bits = n.bits().saturating_sub(1) as usize;
    let em = match scheme.to_ascii_lowercase().as_str() {
        "pss" => pss_encode(message, em_bits)?,
        "pkcs1v15" | "pkcs1-v1_5" => pkcs1v15_sign_encode(message, k)?,
        other => {
            return Err(CryptoError::InvalidParameter(format!(
                "unsupported RSA signature scheme: {other}"
            )))
        }
    };
    let m = os2ip(&em);
    let s = m.modpow(&d, &n);
    i2osp(&s, k)
}

/// RSA-PSS sign using CRT private parameters.
pub fn sign_pss_crt(message: &[u8], n: &[u8], d: &[u8], p: &[u8], q: &[u8]) -> CryptoResult<Vec<u8>> {
    let key = private_from_parts(n, d, p, q)?;
    let k = modulus_len(&key.n)?;
    let em = pss_encode(message, key.n.bits().saturating_sub(1) as usize)?;
    let s = key.private_op_crt(&os2ip(&em));
    i2osp(&s, k)
}

/// RSA verify. Returns `Ok(())` on match, `Err(SignatureInvalid)` otherwise.
pub fn verify(
    message: &[u8],
    signature: &[u8],
    n: &[u8],
    e: &[u8],
    scheme: &str,
) -> CryptoResult<()> {
    let n = BigUint::from_bytes_be(n);
    let e = BigUint::from_bytes_be(e);
    let k = modulus_len(&n)?;
    if signature.len() != k {
        return Err(CryptoError::SignatureInvalid);
    }
    let s = os2ip(signature);
    if s >= n {
        return Err(CryptoError::SignatureInvalid);
    }
    let m = s.modpow(&e, &n);
    let em = i2osp(&m, k)?;
    match scheme.to_ascii_lowercase().as_str() {
        "pss" => pss_verify(message, &em, n.bits().saturating_sub(1) as usize),
        "pkcs1v15" | "pkcs1-v1_5" => {
            let expected = pkcs1v15_sign_encode(message, k)?;
            if bool::from(expected.ct_eq(&em)) {
                Ok(())
            } else {
                Err(CryptoError::SignatureInvalid)
            }
        }
        other => Err(CryptoError::InvalidParameter(format!(
            "unsupported RSA signature scheme: {other}"
        ))),
    }
}

fn private_from_parts(n: &[u8], d: &[u8], p: &[u8], q: &[u8]) -> CryptoResult<RsaKeyPair> {
    let n = BigUint::from_bytes_be(n);
    let d = BigUint::from_bytes_be(d);
    let p = BigUint::from_bytes_be(p);
    let q = BigUint::from_bytes_be(q);
    let one = BigUint::one();
    if p.is_zero() || q.is_zero() || &p * &q != n {
        return Err(CryptoError::InvalidKey("RSA p*q != n".to_string()));
    }
    let dp = &d % (&p - &one);
    let dq = &d % (&q - &one);
    let qinv = CryptoBigInt(q.clone())
        .mod_inverse(&CryptoBigInt(p.clone()))
        .ok_or_else(|| CryptoError::InvalidKey("RSA q inverse missing".to_string()))?
        .0;
    Ok(RsaKeyPair {
        n,
        e: BigUint::from(65537u32),
        d,
        p,
        q,
        dp,
        dq,
        qinv,
    })
}

fn oaep_encode(message: &[u8], k: usize) -> CryptoResult<Vec<u8>> {
    if message.len() > k.saturating_sub(2 * H_LEN + 2) {
        return Err(CryptoError::InvalidInputLength(
            "message too long for RSA-OAEP-SHA256".to_string(),
        ));
    }
    let l_hash = sha256(b"");
    let ps_len = k - message.len() - 2 * H_LEN - 2;
    let mut db = Vec::with_capacity(k - H_LEN - 1);
    db.extend_from_slice(&l_hash);
    db.extend(std::iter::repeat(0u8).take(ps_len));
    db.push(1);
    db.extend_from_slice(message);

    let mut seed = [0u8; H_LEN];
    OsRng.fill_bytes(&mut seed);
    let db_mask = mgf1_sha256(&seed, k - H_LEN - 1);
    xor_in_place(&mut db, &db_mask);
    let seed_mask = mgf1_sha256(&db, H_LEN);
    let mut masked_seed = seed.to_vec();
    xor_in_place(&mut masked_seed, &seed_mask);

    let mut em = Vec::with_capacity(k);
    em.push(0);
    em.extend_from_slice(&masked_seed);
    em.extend_from_slice(&db);
    Ok(em)
}

fn oaep_decode(em: &[u8]) -> CryptoResult<Vec<u8>> {
    if em.len() < 2 * H_LEN + 2 {
        return Err(CryptoError::InvalidPadding);
    }
    let (y, rest) = em.split_at(1);
    let (masked_seed, masked_db) = rest.split_at(H_LEN);
    let seed_mask = mgf1_sha256(masked_db, H_LEN);
    let mut seed = masked_seed.to_vec();
    xor_in_place(&mut seed, &seed_mask);
    let db_mask = mgf1_sha256(&seed, em.len() - H_LEN - 1);
    let mut db = masked_db.to_vec();
    xor_in_place(&mut db, &db_mask);

    let l_hash = sha256(b"");
    let mut valid = y[0].ct_eq(&0u8) & db[..H_LEN].ct_eq(&l_hash);
    let mut seen_one = 0u8;
    let mut msg_index = 0usize;
    for (offset, b) in db[H_LEN..].iter().enumerate() {
        let is_zero = b.ct_eq(&0u8);
        let is_one = b.ct_eq(&1u8);
        let before_one = seen_one.ct_eq(&0u8);
        valid &= (!before_one) | is_zero | is_one;
        if bool::from(before_one & is_one) {
            msg_index = H_LEN + offset + 1;
            seen_one = 1;
        }
    }
    valid &= seen_one.ct_eq(&1u8);
    if !bool::from(valid) {
        return Err(CryptoError::InvalidPadding);
    }
    Ok(db[msg_index..].to_vec())
}

fn pkcs1v15_encrypt_encode(message: &[u8], k: usize) -> CryptoResult<Vec<u8>> {
    if message.len() > k.saturating_sub(11) {
        return Err(CryptoError::InvalidInputLength(
            "message too long for RSAES-PKCS1-v1_5".to_string(),
        ));
    }
    let ps_len = k - message.len() - 3;
    let mut ps = vec![0u8; ps_len];
    for b in &mut ps {
        while *b == 0 {
            let mut one = [0u8; 1];
            OsRng.fill_bytes(&mut one);
            *b = one[0];
        }
    }
    let mut em = Vec::with_capacity(k);
    em.extend_from_slice(&[0, 2]);
    em.extend_from_slice(&ps);
    em.push(0);
    em.extend_from_slice(message);
    Ok(em)
}

fn pkcs1v15_encrypt_decode(em: &[u8]) -> CryptoResult<Vec<u8>> {
    if em.len() < 11 || em[0] != 0 || em[1] != 2 {
        return Err(CryptoError::InvalidPadding);
    }
    let mut sep = None;
    for (i, b) in em.iter().enumerate().skip(2) {
        if *b == 0 {
            sep = Some(i);
            break;
        }
    }
    let sep = sep.ok_or(CryptoError::InvalidPadding)?;
    if sep < 10 {
        return Err(CryptoError::InvalidPadding);
    }
    Ok(em[sep + 1..].to_vec())
}

fn pss_encode(message: &[u8], em_bits: usize) -> CryptoResult<Vec<u8>> {
    let em_len = (em_bits + 7) / 8;
    if em_len < H_LEN + PSS_SALT_LEN + 2 {
        return Err(CryptoError::InvalidParameter(
            "RSA modulus too short for PSS-SHA256".to_string(),
        ));
    }
    let m_hash = sha256(message);
    let mut salt = [0u8; PSS_SALT_LEN];
    OsRng.fill_bytes(&mut salt);
    let mut m_prime = vec![0u8; 8];
    m_prime.extend_from_slice(&m_hash);
    m_prime.extend_from_slice(&salt);
    let h = sha256(&m_prime);

    let ps_len = em_len - PSS_SALT_LEN - H_LEN - 2;
    let mut db = Vec::with_capacity(em_len - H_LEN - 1);
    db.extend(std::iter::repeat(0u8).take(ps_len));
    db.push(1);
    db.extend_from_slice(&salt);

    let db_mask = mgf1_sha256(&h, em_len - H_LEN - 1);
    xor_in_place(&mut db, &db_mask);
    clear_leftmost_unused_bits(&mut db, em_bits);

    let mut em = db;
    em.extend_from_slice(&h);
    em.push(0xbc);
    Ok(em)
}

fn pss_verify(message: &[u8], em: &[u8], em_bits: usize) -> CryptoResult<()> {
    let em_len = (em_bits + 7) / 8;
    if em.len() != em_len || em_len < H_LEN + PSS_SALT_LEN + 2 || em[em.len() - 1] != 0xbc {
        return Err(CryptoError::SignatureInvalid);
    }
    let db_len = em_len - H_LEN - 1;
    let (masked_db, rest) = em.split_at(db_len);
    let h = &rest[..H_LEN];
    if has_nonzero_unused_bits(masked_db, em_bits) {
        return Err(CryptoError::SignatureInvalid);
    }

    let db_mask = mgf1_sha256(h, db_len);
    let mut db = masked_db.to_vec();
    xor_in_place(&mut db, &db_mask);
    clear_leftmost_unused_bits(&mut db, em_bits);

    let ps_len = em_len - H_LEN - PSS_SALT_LEN - 2;
    let mut valid = 1u8;
    for b in &db[..ps_len] {
        valid &= bool_to_u8(*b == 0);
    }
    valid &= bool_to_u8(db[ps_len] == 1);
    if valid == 0 {
        return Err(CryptoError::SignatureInvalid);
    }
    let salt = &db[db_len - PSS_SALT_LEN..];
    let m_hash = sha256(message);
    let mut m_prime = vec![0u8; 8];
    m_prime.extend_from_slice(&m_hash);
    m_prime.extend_from_slice(salt);
    let expected_h = sha256(&m_prime);
    if bool::from(expected_h.ct_eq(h)) {
        Ok(())
    } else {
        Err(CryptoError::SignatureInvalid)
    }
}

fn pkcs1v15_sign_encode(message: &[u8], k: usize) -> CryptoResult<Vec<u8>> {
    // DigestInfo prefix for SHA-256 from RFC 8017 Section 9.2 notes.
    let hash = sha256(message);
    let mut t = Vec::with_capacity(SHA256_DIGESTINFO_PREFIX.len() + H_LEN);
    t.extend_from_slice(&SHA256_DIGESTINFO_PREFIX);
    t.extend_from_slice(&hash);
    if k < t.len() + 11 {
        return Err(CryptoError::InvalidParameter(
            "RSA modulus too short for PKCS1-v1_5 SHA-256 signature".to_string(),
        ));
    }
    let ps_len = k - t.len() - 3;
    let mut em = Vec::with_capacity(k);
    em.extend_from_slice(&[0, 1]);
    em.extend(std::iter::repeat(0xff).take(ps_len));
    em.push(0);
    em.extend_from_slice(&t);
    Ok(em)
}

fn mgf1_sha256(seed: &[u8], len: usize) -> Vec<u8> {
    let mut out = Vec::with_capacity(len);
    let mut counter = 0u32;
    while out.len() < len {
        let mut input = Vec::with_capacity(seed.len() + 4);
        input.extend_from_slice(seed);
        input.extend_from_slice(&counter.to_be_bytes());
        out.extend_from_slice(&sha256(&input));
        counter = counter.wrapping_add(1);
    }
    out.truncate(len);
    out
}

fn xor_in_place(left: &mut [u8], right: &[u8]) {
    for (a, b) in left.iter_mut().zip(right.iter()) {
        *a ^= b;
    }
}

fn clear_leftmost_unused_bits(bytes: &mut [u8], em_bits: usize) {
    let unused = 8 * bytes.len() + H_LEN * 8 + 8 - em_bits;
    if unused > 0 && unused < 8 {
        bytes[0] &= 0xffu8 >> unused;
    }
}

fn has_nonzero_unused_bits(bytes: &[u8], em_bits: usize) -> bool {
    let unused = 8 * bytes.len() + H_LEN * 8 + 8 - em_bits;
    unused > 0 && unused < 8 && (bytes[0] & !(0xffu8 >> unused)) != 0
}

fn modulus_len(n: &BigUint) -> CryptoResult<usize> {
    if n.is_zero() {
        return Err(CryptoError::InvalidKey("RSA modulus is zero".to_string()));
    }
    Ok(((n.bits() + 7) / 8) as usize)
}

fn os2ip(bytes: &[u8]) -> BigUint {
    BigUint::from_bytes_be(bytes)
}

fn i2osp(value: &BigUint, len: usize) -> CryptoResult<Vec<u8>> {
    let bytes = value.to_bytes_be();
    if bytes.len() > len {
        return Err(CryptoError::InvalidInputLength(
            "integer too large for requested output length".to_string(),
        ));
    }
    let mut out = vec![0u8; len - bytes.len()];
    out.extend_from_slice(&bytes);
    Ok(out)
}

fn bool_to_u8(value: bool) -> u8 {
    if value {
        1
    } else {
        0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_low_public_exponent() {
        assert!(RsaKeyPair::generate(1024, 3).is_err());
    }

    #[test]
    fn mgf1_is_deterministic() {
        assert_eq!(mgf1_sha256(b"seed", 40), mgf1_sha256(b"seed", 40));
    }

    #[ignore = "RSA-1024 key generation is intentionally slow"]
    #[test]
    fn rsa_keygen_oaep_pss_roundtrip() {
        let (n, e, d, p, q) = keygen(1024, 65537).expect("keygen");
        let message = b"hello";
        let ct = encrypt(message, &n, &e, "oaep").expect("encrypt");
        let pt = decrypt_oaep_crt(&ct, &n, &d, &p, &q).expect("decrypt");
        assert_eq!(pt, message);

        let sig = sign_pss_crt(message, &n, &d, &p, &q).expect("sign");
        verify(message, &sig, &n, &e, "pss").expect("verify");
        let mut tampered = sig;
        tampered[0] ^= 1;
        assert!(verify(message, &tampered, &n, &e, "pss").is_err());
    }
}
