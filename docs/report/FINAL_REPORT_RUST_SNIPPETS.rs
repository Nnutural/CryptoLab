// CryptoLab final report Rust snippets.
//
// Purpose:
// Open this file in VSCode, copy highlighted Rust code, and paste it into Word.
// This file is for display/highlighting only; it is not intended to compile.

// =============================================================================
// rust_core/src/ffi.rs:19-80
// =============================================================================

pub fn register(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(aes_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(aes_encrypt_with_trace, m)?)?;
    m.add_function(wrap_pyfunction!(aes_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sm4_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sm4_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rc6_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rc6_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sha1, m)?)?;
    m.add_function(wrap_pyfunction!(sha256_digest, m)?)?;
    m.add_function(wrap_pyfunction!(sha3_256_digest, m)?)?;
    m.add_function(wrap_pyfunction!(ripemd160_digest, m)?)?;
    m.add_function(wrap_pyfunction!(hmac_sha1, m)?)?;
    m.add_function(wrap_pyfunction!(hmac_sha256, m)?)?;
    m.add_function(wrap_pyfunction!(pbkdf2_hmac_sha256, m)?)?;
    m.add_function(wrap_pyfunction!(base64_encode, m)?)?;
    m.add_function(wrap_pyfunction!(base64_decode, m)?)?;
    m.add_function(wrap_pyfunction!(utf8_encode, m)?)?;
    m.add_function(wrap_pyfunction!(utf8_decode, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_generate_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_encrypt_oaep, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_decrypt_oaep, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_sign_pss, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_verify_pss, m)?)?;
    m.add_function(wrap_pyfunction!(ecc_generate_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_sign, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_verify, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_demo_unsafe_keygen, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_demo_unsafe_encrypt_raw, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_demo_cube_root, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_demo_sign_with_k, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_demo_recover_d_from_k_reuse, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

// =============================================================================
// rust_core/src/hash/hmac.rs:10-60
// =============================================================================

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

pub fn hmac_sha1(key: &[u8], message: &[u8]) -> [u8; 20] {
    let tag = hmac::<Sha1>(key, message);
    let mut out = [0u8; 20];
    out.copy_from_slice(&tag);
    out
}

pub fn hmac_sha256(key: &[u8], message: &[u8]) -> [u8; 32] {
    let tag = hmac::<Sha256>(key, message);
    let mut out = [0u8; 32];
    out.copy_from_slice(&tag);
    out
}

pub fn verify_hmac_sha256(key: &[u8], message: &[u8], tag: &[u8]) -> bool {
    hmac_sha256(key, message).ct_eq(tag).into()
}

// =============================================================================
// rust_core/src/hash/pbkdf2.rs:16-62
// =============================================================================

pub fn pbkdf2_hmac_sha256(
    password: &[u8],
    salt: &[u8],
    iterations: u32,
    key_len: usize,
) -> CryptoResult<Vec<u8>> {
    if iterations == 0 {
        return Err(CryptoError::InvalidParameter(
            "PBKDF2 iterations must be at least 1".to_string(),
        ));
    }
    if key_len == 0 {
        return Err(CryptoError::InvalidParameter(
            "PBKDF2 key_len must be greater than 0".to_string(),
        ));
    }
    let max_len = (u32::MAX as u64) * (H_LEN as u64);
    if (key_len as u64) > max_len {
        return Err(CryptoError::InvalidParameter(format!(
            "PBKDF2 key_len must be <= {max_len}"
        )));
    }
    let blocks = key_len.div_ceil(H_LEN);
    let mut derived = Vec::with_capacity(blocks * H_LEN);
    let mut salt_block = Vec::with_capacity(salt.len() + 4);
    for block_index in 1..=blocks {
        salt_block.clear();
        salt_block.extend_from_slice(salt);
        salt_block.extend_from_slice(&(block_index as u32).to_be_bytes());
        let mut u = hmac_sha256(password, &salt_block);
        let mut t = u;
        for _ in 1..iterations {
            u = hmac_sha256(password, &u);
            for i in 0..H_LEN {
                t[i] ^= u[i];
            }
        }
        derived.extend_from_slice(&t);
    }
    derived.truncate(key_len);
    Ok(derived)
}

// =============================================================================
// rust_core/src/symmetric/aes.rs:355-428
// =============================================================================

fn expand_key(key: &[u8], nk: usize, rounds: usize) -> Vec<u8> {
    let total_words = 4 * (rounds + 1);
    let mut words = vec![[0u8; 4]; total_words];
    for i in 0..nk {
        words[i].copy_from_slice(&key[i * 4..i * 4 + 4]);
    }
    for i in nk..total_words {
        let mut temp = words[i - 1];
        if i % nk == 0 {
            temp = sub_word(rot_word(temp));
            temp[0] ^= RCON[i / nk];
        } else if nk > 6 && i % nk == 4 {
            temp = sub_word(temp);
        }
        for (j, value) in temp.iter().enumerate() {
            words[i][j] = words[i - nk][j] ^ value;
        }
    }
    let mut out = Vec::with_capacity(total_words * 4);
    for word in words {
        out.extend_from_slice(&word);
    }
    out
}

fn rot_word(word: [u8; 4]) -> [u8; 4] { [word[1], word[2], word[3], word[0]] }

fn sub_word(mut word: [u8; 4]) -> [u8; 4] {
    for b in &mut word { *b = S_BOX[*b as usize]; }
    word
}

fn add_round_key(state: &mut [u8; BLOCK_SIZE], key: &[u8]) {
    for i in 0..BLOCK_SIZE { state[i] ^= key[i]; }
}

fn sub_bytes(state: &mut [u8; BLOCK_SIZE]) {
    for b in state { *b = S_BOX[*b as usize]; }
}

fn shift_rows(state: &mut [u8; BLOCK_SIZE]) {
    let tmp = *state;
    for r in 0..4 {
        for c in 0..4 {
            state[r + 4 * c] = tmp[r + 4 * ((c + r) % 4)];
        }
    }
}

fn mix_columns(state: &mut [u8; BLOCK_SIZE]) {
    for c in 0..4 {
        let i = 4 * c;
        let a0 = state[i];
        let a1 = state[i + 1];
        let a2 = state[i + 2];
        let a3 = state[i + 3];

// =============================================================================
// rust_core/src/pubkey/rsa.rs:100-140
// =============================================================================

fn private_op_crt(&self, c: &BigUint) -> BigUint {
    let m1 = c.modpow(&self.dp, &self.p);
    let m2 = c.modpow(&self.dq, &self.q);
    let m2_mod_p = &m2 % &self.p;
    let diff = if m1 >= m2_mod_p {
        &m1 - &m2_mod_p
    } else {
        &m1 + &self.p - &m2_mod_p
    };
    let h = (&self.qinv * diff) % &self.p;
    &m2 + &self.q * h
}

fn private_op_crt_blinded(&self, c: &BigUint) -> CryptoResult<BigUint> {
    let two = BigUint::from(2u32);
    let one = BigUint::one();
    if self.n <= two {
        return Err(CryptoError::InvalidKey(
            "RSA modulus too small for blinding".to_string(),
        ));
    }
    let upper = CryptoBigInt(&self.n - &two);
    for _ in 0..128 {
        let r = CryptoBigInt::random_below(&upper)?.0 + &two;
        if r.gcd(&self.n) != one { continue; }
        let r_inv = CryptoBigInt(r.clone())
            .mod_inverse(&CryptoBigInt(self.n.clone()))
            .ok_or_else(|| CryptoError::BigIntError(
                "RSA blinding inverse missing".to_string()
            ))?.0;
        let blinded_c = (c * r.modpow(&self.e, &self.n)) % &self.n;
        let blinded_m = self.private_op_crt(&blinded_c);
        return Ok((blinded_m * r_inv) % &self.n);
    }
    Err(CryptoError::RandomError(
        "failed to sample invertible RSA blinding factor".to_string(),
    ))
}

// =============================================================================
// rust_core/src/pubkey/ecc.rs:162-246
// =============================================================================

pub fn scalar_mul_point(curve: &Curve, point: &AffinePoint, k: &BigUint) -> CryptoResult<AffinePoint> {
    let mut r0 = AffinePoint::infinity();
    let mut r1 = point.clone();
    for i in (0..k.bits()).rev() {
        let add = point_add(curve, &r0, &r1)?;
        let dbl0 = point_double(curve, &r0)?;
        let dbl1 = point_double(curve, &r1)?;
        if k.bit(i) { r0 = add; r1 = dbl1; }
        else { r0 = dbl0; r1 = add; }
    }
    Ok(r0)
}

pub fn point_add(curve: &Curve, p1: &AffinePoint, p2: &AffinePoint) -> CryptoResult<AffinePoint> {
    if p1.infinity { return Ok(p2.clone()); }
    if p2.infinity { return Ok(p1.clone()); }
    if p1.x == p2.x {
        if mod_add(&p1.y, &p2.y, &curve.p).is_zero() { return Ok(AffinePoint::infinity()); }
        return point_double(curve, p1);
    }
    let numerator = mod_sub(&p2.y, &p1.y, &curve.p);
    let denominator = mod_sub(&p2.x, &p1.x, &curve.p);
    let lambda = (&numerator * mod_inv(&denominator, &curve.p)?) % &curve.p;
    let x3 = mod_sub(&mod_sub(&(&lambda * &lambda % &curve.p), &p1.x, &curve.p), &p2.x, &curve.p);
    let y3 = mod_sub(&(&lambda * mod_sub(&p1.x, &x3, &curve.p) % &curve.p), &p1.y, &curve.p);
    Ok(AffinePoint { x: x3, y: y3, infinity: false })
}

pub fn point_double(curve: &Curve, point: &AffinePoint) -> CryptoResult<AffinePoint> {
    if point.infinity || point.y.is_zero() { return Ok(AffinePoint::infinity()); }
    let numerator = (BigUint::from(3u32) * &point.x * &point.x + &curve.a) % &curve.p;
    let denominator = (BigUint::from(2u32) * &point.y) % &curve.p;
    let lambda = (numerator * mod_inv(&denominator, &curve.p)?) % &curve.p;
    let x3 = mod_sub(&mod_sub(&(&lambda * &lambda % &curve.p), &point.x, &curve.p), &point.x, &curve.p);
    let y3 = mod_sub(&(&lambda * mod_sub(&point.x, &x3, &curve.p) % &curve.p), &point.y, &curve.p);
    Ok(AffinePoint { x: x3, y: y3, infinity: false })
}

// =============================================================================
// rust_core/src/pubkey/ecdsa.rs:107-160
// =============================================================================

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
                if retry == 0 { return secret; }
                break;
            }
            let mut retry_input = Vec::with_capacity(v.len() + 1);
            retry_input.extend_from_slice(&v);
            retry_input.push(0x00);
            k = hmac_sha256(&k, &retry_input).to_vec();
            v = hmac_sha256(&k, &v).to_vec();
        }
    }
    BigUint::one()
}
