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
use subtle::Choice;

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
    pub fn pad(&self, data: &mut Vec<u8>, block_size: usize) -> CryptoResult<()> {
        if block_size == 0 || block_size > u8::MAX as usize {
            return Err(CryptoError::InvalidParameter(format!(
                "invalid block size for padding: {block_size}"
            )));
        }

        let rem = data.len() % block_size;
        let pad_len = if rem == 0 { block_size } else { block_size - rem };
        match self {
            Self::Pkcs7 => data.extend(std::iter::repeat(pad_len as u8).take(pad_len)),
            Self::Zero => {
                if rem != 0 {
                    data.extend(std::iter::repeat(0u8).take(pad_len));
                }
            }
            Self::AnsiX923 => {
                if pad_len > 1 {
                    data.extend(std::iter::repeat(0u8).take(pad_len - 1));
                }
                data.push(pad_len as u8);
            }
            Self::None => {
                if rem != 0 {
                    return Err(CryptoError::InvalidInputLength(format!(
                        "input length {} is not a multiple of block size {block_size}",
                        data.len()
                    )));
                }
            }
        }
        Ok(())
    }

    /// Remove padding in-place.
    pub fn unpad(&self, data: &mut Vec<u8>, block_size: usize) -> CryptoResult<()> {
        if block_size == 0 || data.is_empty() || data.len() % block_size != 0 {
            return Err(CryptoError::InvalidPadding);
        }

        match self {
            Self::Pkcs7 => {
                let pad_len = *data.last().ok_or(CryptoError::InvalidPadding)? as usize;
                if pad_len == 0 || pad_len > block_size || pad_len > data.len() {
                    return Err(CryptoError::InvalidPadding);
                }

                let expected = pad_len as u8;
                let mut valid = Choice::from(1);
                for i in 0..block_size {
                    let b = data[data.len() - 1 - i];
                    let in_padding = Choice::from((i < pad_len) as u8);
                    valid &= (!in_padding) | subtle::ConstantTimeEq::ct_eq(&b, &expected);
                }
                if !bool::from(valid) {
                    return Err(CryptoError::InvalidPadding);
                }
                data.truncate(data.len() - pad_len);
                Ok(())
            }
            Self::Zero => Err(CryptoError::InvalidPadding),
            Self::AnsiX923 => {
                let pad_len = *data.last().ok_or(CryptoError::InvalidPadding)? as usize;
                if pad_len == 0 || pad_len > block_size || pad_len > data.len() {
                    return Err(CryptoError::InvalidPadding);
                }

                let mut valid = Choice::from(1);
                for i in 1..block_size {
                    let b = data[data.len() - 1 - i];
                    let in_padding = Choice::from((i < pad_len) as u8);
                    valid &= (!in_padding) | subtle::ConstantTimeEq::ct_eq(&b, &0u8);
                }
                if !bool::from(valid) {
                    return Err(CryptoError::InvalidPadding);
                }
                data.truncate(data.len() - pad_len);
                Ok(())
            }
            Self::None => Ok(()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::Padding;

    #[test]
    fn pkcs7_adds_full_block_on_boundary() {
        let mut data = b"1234567890abcdef".to_vec();
        Padding::Pkcs7.pad(&mut data, 16).expect("valid padding");
        assert_eq!(data.len(), 32);
        Padding::Pkcs7.unpad(&mut data, 16).expect("valid unpad");
        assert_eq!(data, b"1234567890abcdef");
    }

    #[test]
    fn zero_unpad_is_rejected() {
        let mut data = b"abc".to_vec();
        Padding::Zero.pad(&mut data, 16).expect("valid padding");
        assert!(Padding::Zero.unpad(&mut data, 16).is_err());
    }

    #[test]
    fn ansi_x923_roundtrip_and_rejects_bad_bytes() {
        let mut data = b"abc".to_vec();
        Padding::AnsiX923
            .pad(&mut data, 16)
            .expect("valid padding");
        let mut bad = data.clone();
        bad[14] = 1;
        assert!(Padding::AnsiX923.unpad(&mut bad, 16).is_err());
        Padding::AnsiX923
            .unpad(&mut data, 16)
            .expect("valid unpad");
        assert_eq!(data, b"abc");
    }
}
