//! Block-cipher modes of operation.
//!
//! Generic adapters over [`crate::traits::SymmetricCipher`]. They never know
//! which underlying cipher they're driving — that lets AES / SM4 / RC6 all
//! share the same mode implementations.

pub mod cbc;
pub mod ctr;
pub mod ecb;
pub mod gcm;

use crate::error::{CryptoError, CryptoResult};

/// Supported PKCS#7 / Zero / ANSI X.923 padding flavors.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Padding {
    /// PKCS#7 — append N bytes of value N (N == bytes-to-block-boundary).
    Pkcs7,
    /// Append zero bytes; cannot disambiguate inputs that already end in 0x00.
    Zero,
    /// ANSI X.923 — append (N-1) zero bytes then one byte of value N.
    AnsiX923,
    /// No padding; input length must already be a block multiple.
    None,
}

impl Padding {
    /// Parse a padding scheme name (case-insensitive).
    pub fn parse(name: &str) -> CryptoResult<Self> {
        match name.to_ascii_lowercase().as_str() {
            "pkcs7" | "pkcs#7" => Ok(Self::Pkcs7),
            "zero" => Ok(Self::Zero),
            "ansi_x923" | "x923" => Ok(Self::AnsiX923),
            "none" => Ok(Self::None),
            other => Err(CryptoError::InvalidParameter(format!(
                "unsupported padding: {other}"
            ))),
        }
    }

    /// Apply padding so that `data.len()` becomes a multiple of `block_size`.
    pub fn pad(&self, _data: &mut Vec<u8>, _block_size: usize) -> CryptoResult<()> {
        todo!("apply self to data; return Err for None when len % block != 0")
    }

    /// Remove padding in-place.
    pub fn unpad(&self, _data: &mut Vec<u8>, _block_size: usize) -> CryptoResult<()> {
        todo!("strip self from data; constant-time when possible")
    }
}
