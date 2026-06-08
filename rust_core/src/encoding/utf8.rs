//! UTF-8 — RFC 3629 transformation of Unicode codepoints.
//!
//! Rust's `str` is already UTF-8, but the assignment asks us to demonstrate
//! the codec end-to-end (including overlong-encoding rejection).

use crate::error::{CryptoError, CryptoResult};

/// Encode a Rust string into raw UTF-8 bytes.
pub fn encode(text: &str) -> Vec<u8> {
    let mut out = Vec::with_capacity(text.len());

    for ch in text.chars() {
        let codepoint = ch as u32;
        if codepoint <= 0x7f {
            out.push(codepoint as u8);
        } else if codepoint <= 0x07ff {
            out.push(0b1100_0000 | ((codepoint >> 6) as u8));
            out.push(0b1000_0000 | ((codepoint & 0x3f) as u8));
        } else if codepoint <= 0xffff {
            out.push(0b1110_0000 | ((codepoint >> 12) as u8));
            out.push(0b1000_0000 | (((codepoint >> 6) & 0x3f) as u8));
            out.push(0b1000_0000 | ((codepoint & 0x3f) as u8));
        } else {
            out.push(0b1111_0000 | ((codepoint >> 18) as u8));
            out.push(0b1000_0000 | (((codepoint >> 12) & 0x3f) as u8));
            out.push(0b1000_0000 | (((codepoint >> 6) & 0x3f) as u8));
            out.push(0b1000_0000 | ((codepoint & 0x3f) as u8));
        }
    }

    out
}

/// Decode raw bytes into a Rust `String`, rejecting overlong forms /
/// surrogate halves / invalid continuation bytes.
pub fn decode(data: &[u8]) -> CryptoResult<String> {
    let mut out = String::new();
    let mut index = 0;

    while index < data.len() {
        let first = data[index];
        let (codepoint, width) = match first {
            0x00..=0x7f => (first as u32, 1),
            0xc2..=0xdf => {
                let second = tail(data, index + 1)?;
                let codepoint = (((first & 0x1f) as u32) << 6) | ((second & 0x3f) as u32);
                (codepoint, 2)
            }
            0xe0 => {
                let second = ranged_byte(data, index + 1, 0xa0, 0xbf)?;
                let third = tail(data, index + 2)?;
                let codepoint = (((first & 0x0f) as u32) << 12)
                    | (((second & 0x3f) as u32) << 6)
                    | ((third & 0x3f) as u32);
                (codepoint, 3)
            }
            0xe1..=0xec => {
                let second = tail(data, index + 1)?;
                let third = tail(data, index + 2)?;
                let codepoint = (((first & 0x0f) as u32) << 12)
                    | (((second & 0x3f) as u32) << 6)
                    | ((third & 0x3f) as u32);
                (codepoint, 3)
            }
            0xed => {
                let second = ranged_byte(data, index + 1, 0x80, 0x9f)?;
                let third = tail(data, index + 2)?;
                let codepoint = (((first & 0x0f) as u32) << 12)
                    | (((second & 0x3f) as u32) << 6)
                    | ((third & 0x3f) as u32);
                (codepoint, 3)
            }
            0xee..=0xef => {
                let second = tail(data, index + 1)?;
                let third = tail(data, index + 2)?;
                let codepoint = (((first & 0x0f) as u32) << 12)
                    | (((second & 0x3f) as u32) << 6)
                    | ((third & 0x3f) as u32);
                (codepoint, 3)
            }
            0xf0 => {
                let second = ranged_byte(data, index + 1, 0x90, 0xbf)?;
                let third = tail(data, index + 2)?;
                let fourth = tail(data, index + 3)?;
                let codepoint = (((first & 0x07) as u32) << 18)
                    | (((second & 0x3f) as u32) << 12)
                    | (((third & 0x3f) as u32) << 6)
                    | ((fourth & 0x3f) as u32);
                (codepoint, 4)
            }
            0xf1..=0xf3 => {
                let second = tail(data, index + 1)?;
                let third = tail(data, index + 2)?;
                let fourth = tail(data, index + 3)?;
                let codepoint = (((first & 0x07) as u32) << 18)
                    | (((second & 0x3f) as u32) << 12)
                    | (((third & 0x3f) as u32) << 6)
                    | ((fourth & 0x3f) as u32);
                (codepoint, 4)
            }
            0xf4 => {
                let second = ranged_byte(data, index + 1, 0x80, 0x8f)?;
                let third = tail(data, index + 2)?;
                let fourth = tail(data, index + 3)?;
                let codepoint = (((first & 0x07) as u32) << 18)
                    | (((second & 0x3f) as u32) << 12)
                    | (((third & 0x3f) as u32) << 6)
                    | ((fourth & 0x3f) as u32);
                (codepoint, 4)
            }
            _ => return Err(encoding_error("invalid UTF-8 leading byte")),
        };

        let ch = char::from_u32(codepoint)
            .ok_or_else(|| encoding_error("UTF-8 decoded to an invalid Unicode scalar value"))?;
        out.push(ch);
        index += width;
    }

    Ok(out)
}

fn tail(data: &[u8], index: usize) -> CryptoResult<u8> {
    ranged_byte(data, index, 0x80, 0xbf)
}

fn ranged_byte(data: &[u8], index: usize, min: u8, max: u8) -> CryptoResult<u8> {
    let byte = data
        .get(index)
        .copied()
        .ok_or_else(|| encoding_error("truncated UTF-8 byte sequence"))?;
    if (min..=max).contains(&byte) {
        Ok(byte)
    } else {
        Err(encoding_error("invalid UTF-8 continuation byte"))
    }
}

fn encoding_error(message: &str) -> CryptoError {
    CryptoError::EncodingError(message.to_string())
}

#[cfg(test)]
mod tests {
    use super::{decode, encode};

    #[test]
    fn encode_matches_rfc3629_widths() {
        let cases: [(&str, &[u8]); 6] = [
            ("Hello", b"Hello"),
            ("héllo", b"h\xc3\xa9llo"),
            ("你好", &[0xe4, 0xbd, 0xa0, 0xe5, 0xa5, 0xbd]),
            ("𝄞", &[0xf0, 0x9d, 0x84, 0x9e]),
            ("a你𝄞", &[0x61, 0xe4, 0xbd, 0xa0, 0xf0, 0x9d, 0x84, 0x9e]),
            ("", b""),
        ];

        for (text, bytes) in cases {
            assert_eq!(encode(text), bytes);
            assert_eq!(decode(bytes).expect("well-formed UTF-8"), text);
        }
    }

    #[test]
    fn decode_rejects_ill_formed_rfc3629_sequences() {
        let cases: [&[u8]; 8] = [
            &[0xc0, 0x80],
            &[0xc0, 0xaf],
            &[0xed, 0xa0, 0x80],
            &[0xed, 0xbf, 0xbf],
            &[0xe4, 0xbd],
            &[0xfe],
            &[0xff],
            &[0xf8, 0x80, 0x80, 0x80, 0x80],
        ];

        for data in cases {
            assert!(decode(data).is_err(), "{data:02x?} should be rejected");
        }
    }
}
