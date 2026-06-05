//! PyO3 bindings.
//!
//! This is the ONLY module that depends on Python types. Every other
//! algorithm module returns plain Rust values; here we convert those into
//! `PyBytes` / `PyDict` / etc.
//!
//! New algorithms wired up to Python must:
//!   1. live as pure-Rust fn somewhere in `symmetric/`, `hash/`, ...
//!   2. add a `#[pyfunction]` wrapper here that forwards to the pure fn
//!   3. register the wrapper in [`register`] below

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};

use crate::error::CryptoResult;

/// Register every exported binding on `m`.
pub fn register(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    // ----- symmetric -----
    m.add_function(wrap_pyfunction!(aes_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(aes_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sm4_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sm4_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rc6_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rc6_decrypt, m)?)?;

    // ----- hash -----
    m.add_function(wrap_pyfunction!(sha1, m)?)?;
    m.add_function(wrap_pyfunction!(sha224, m)?)?;
    m.add_function(wrap_pyfunction!(sha256, m)?)?;
    m.add_function(wrap_pyfunction!(sha384, m)?)?;
    m.add_function(wrap_pyfunction!(sha512, m)?)?;
    m.add_function(wrap_pyfunction!(sha3_256, m)?)?;
    m.add_function(wrap_pyfunction!(sha3_512, m)?)?;
    m.add_function(wrap_pyfunction!(ripemd160, m)?)?;
    m.add_function(wrap_pyfunction!(hmac_sha256, m)?)?;
    m.add_function(wrap_pyfunction!(pbkdf2_hmac_sha256, m)?)?;

    // ----- encoding -----
    m.add_function(wrap_pyfunction!(base64_encode, m)?)?;
    m.add_function(wrap_pyfunction!(base64_decode, m)?)?;
    m.add_function(wrap_pyfunction!(utf8_encode, m)?)?;
    m.add_function(wrap_pyfunction!(utf8_decode, m)?)?;

    // ----- public-key -----
    m.add_function(wrap_pyfunction!(rsa_keygen, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_sign, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_verify, m)?)?;
    m.add_function(wrap_pyfunction!(ecc_keygen, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_sign, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_verify, m)?)?;

    // Version constant.
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

// =========================================================================
// Helpers
// =========================================================================

#[inline]
fn to_pybytes<'py>(py: Python<'py>, data: CryptoResult<Vec<u8>>) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &data?))
}

// =========================================================================
// Symmetric
// =========================================================================

/// AES encrypt — dispatches to ECB / CBC / CTR / GCM by `mode`.
#[pyfunction]
#[pyo3(signature = (plaintext, key, mode, iv=None, aad=None, padding="pkcs7"))]
fn aes_encrypt<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    aad: Option<&[u8]>,
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::symmetric::aes::encrypt_dispatch(plaintext, key, mode, iv, aad, padding),
    )
}

/// AES decrypt — dispatches to ECB / CBC / CTR / GCM by `mode`.
#[pyfunction]
#[pyo3(signature = (ciphertext, key, mode, iv=None, aad=None, padding="pkcs7"))]
fn aes_decrypt<'py>(
    py: Python<'py>,
    ciphertext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    aad: Option<&[u8]>,
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::symmetric::aes::decrypt_dispatch(ciphertext, key, mode, iv, aad, padding),
    )
}

/// SM4 encrypt — modes: ECB / CBC / CTR.
#[pyfunction]
#[pyo3(signature = (plaintext, key, mode, iv=None, padding="pkcs7"))]
fn sm4_encrypt<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::symmetric::sm4::encrypt_dispatch(plaintext, key, mode, iv, padding),
    )
}

/// SM4 decrypt.
#[pyfunction]
#[pyo3(signature = (ciphertext, key, mode, iv=None, padding="pkcs7"))]
fn sm4_decrypt<'py>(
    py: Python<'py>,
    ciphertext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::symmetric::sm4::decrypt_dispatch(ciphertext, key, mode, iv, padding),
    )
}

/// RC6 encrypt — modes: ECB / CBC.
#[pyfunction]
#[pyo3(signature = (plaintext, key, mode, iv=None, padding="pkcs7"))]
fn rc6_encrypt<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::symmetric::rc6::encrypt_dispatch(plaintext, key, mode, iv, padding),
    )
}

/// RC6 decrypt.
#[pyfunction]
#[pyo3(signature = (ciphertext, key, mode, iv=None, padding="pkcs7"))]
fn rc6_decrypt<'py>(
    py: Python<'py>,
    ciphertext: &[u8],
    key: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::symmetric::rc6::decrypt_dispatch(ciphertext, key, mode, iv, padding),
    )
}

// =========================================================================
// Hash
// =========================================================================

#[pyfunction]
fn sha1<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha1::digest(data)))
}

#[pyfunction]
fn sha224<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha2::sha224(data)))
}

#[pyfunction]
fn sha256<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha2::sha256(data)))
}

#[pyfunction]
fn sha384<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha2::sha384(data)))
}

#[pyfunction]
fn sha512<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha2::sha512(data)))
}

#[pyfunction]
fn sha3_256<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha3::sha3_256(data)))
}

#[pyfunction]
fn sha3_512<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::sha3::sha3_512(data)))
}

#[pyfunction]
fn ripemd160<'py>(py: Python<'py>, data: &[u8]) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::hash::ripemd::ripemd160(data)))
}

#[pyfunction]
fn hmac_sha256<'py>(py: Python<'py>, key: &[u8], message: &[u8]) -> PyResult<&'py PyBytes> {
    to_pybytes(py, crate::hash::hmac::hmac_sha256(key, message))
}

#[pyfunction]
#[pyo3(signature = (password, salt, iterations, dk_len))]
fn pbkdf2_hmac_sha256<'py>(
    py: Python<'py>,
    password: &[u8],
    salt: &[u8],
    iterations: u32,
    dk_len: usize,
) -> PyResult<&'py PyBytes> {
    to_pybytes(
        py,
        crate::hash::pbkdf2::pbkdf2_hmac_sha256(password, salt, iterations, dk_len),
    )
}

// =========================================================================
// Encoding
// =========================================================================

#[pyfunction]
fn base64_encode(data: &[u8]) -> PyResult<String> {
    Ok(crate::encoding::base64::encode(data))
}

#[pyfunction]
fn base64_decode<'py>(py: Python<'py>, encoded: &str) -> PyResult<&'py PyBytes> {
    to_pybytes(py, crate::encoding::base64::decode(encoded))
}

#[pyfunction]
fn utf8_encode<'py>(py: Python<'py>, text: &str) -> PyResult<&'py PyBytes> {
    Ok(PyBytes::new(py, &crate::encoding::utf8::encode(text)))
}

#[pyfunction]
fn utf8_decode(data: &[u8]) -> PyResult<String> {
    crate::encoding::utf8::decode(data).map_err(Into::into)
}

// =========================================================================
// Public-key
// =========================================================================

/// RSA key generation. Returns `(n_bytes, e_bytes, d_bytes, p_bytes, q_bytes)`
/// — the upper Python layer wraps these into structured DTOs.
#[pyfunction]
#[pyo3(signature = (bits=1024, e=65537))]
fn rsa_keygen(py: Python<'_>, bits: usize, e: u64) -> PyResult<PyObject> {
    let (n, e, d, p, q) = crate::pubkey::rsa::keygen(bits, e)?;
    let tup = (
        PyBytes::new(py, &n),
        PyBytes::new(py, &e),
        PyBytes::new(py, &d),
        PyBytes::new(py, &p),
        PyBytes::new(py, &q),
    );
    Ok(tup.into_py(py))
}

#[pyfunction]
#[pyo3(signature = (plaintext, n, e, padding="oaep"))]
fn rsa_encrypt<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    n: &[u8],
    e: &[u8],
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(py, crate::pubkey::rsa::encrypt(plaintext, n, e, padding))
}

#[pyfunction]
#[pyo3(signature = (ciphertext, n, d, padding="oaep"))]
fn rsa_decrypt<'py>(
    py: Python<'py>,
    ciphertext: &[u8],
    n: &[u8],
    d: &[u8],
    padding: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(py, crate::pubkey::rsa::decrypt(ciphertext, n, d, padding))
}

#[pyfunction]
#[pyo3(signature = (message, n, d, scheme="pss"))]
fn rsa_sign<'py>(
    py: Python<'py>,
    message: &[u8],
    n: &[u8],
    d: &[u8],
    scheme: &str,
) -> PyResult<&'py PyBytes> {
    to_pybytes(py, crate::pubkey::rsa::sign(message, n, d, scheme))
}

#[pyfunction]
#[pyo3(signature = (message, signature, n, e, scheme="pss"))]
fn rsa_verify(message: &[u8], signature: &[u8], n: &[u8], e: &[u8], scheme: &str) -> PyResult<bool> {
    Ok(crate::pubkey::rsa::verify(message, signature, n, e, scheme).is_ok())
}

/// ECC key generation on `curve` (e.g. "secp160r1"). Returns `(d, px, py)`.
#[pyfunction]
#[pyo3(signature = (curve="secp160r1"))]
fn ecc_keygen(py: Python<'_>, curve: &str) -> PyResult<PyObject> {
    let (d, px, pyc) = crate::pubkey::ecc::keygen(curve)?;
    let tup = (
        PyBytes::new(py, &d),
        PyBytes::new(py, &px),
        PyBytes::new(py, &pyc),
    );
    Ok(tup.into_py(py))
}

/// ECDSA sign. `k` is derived deterministically per RFC 6979 — the binding
/// does NOT accept a caller-provided k.
#[pyfunction]
#[pyo3(signature = (message, d, curve="secp160r1"))]
fn ecdsa_sign(py: Python<'_>, message: &[u8], d: &[u8], curve: &str) -> PyResult<PyObject> {
    let (r, s) = crate::pubkey::ecdsa::sign(message, d, curve)?;
    let tup = (PyBytes::new(py, &r), PyBytes::new(py, &s));
    Ok(tup.into_py(py))
}

#[pyfunction]
#[pyo3(signature = (message, r, s, px, py, curve="secp160r1"))]
fn ecdsa_verify(
    message: &[u8],
    r: &[u8],
    s: &[u8],
    px: &[u8],
    py: &[u8],
    curve: &str,
) -> PyResult<bool> {
    Ok(crate::pubkey::ecdsa::verify(message, r, s, px, py, curve).is_ok())
}
