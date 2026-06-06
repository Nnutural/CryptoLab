//! Base64 — RFC 4648 §4. Standard alphabet, with `=` padding.

use crate::error::{CryptoError, CryptoResult};

const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/// Encode arbitrary bytes as RFC 4648 §4 standard Base64 with `=` padding.
pub fn encode(input: &[u8]) -> String {
    let mut out = String::with_capacity(input.len().div_ceil(3) * 4);

    for chunk in input.chunks(3) {
        let b0 = chunk[0];
        let b1 = if chunk.len() > 1 { chunk[1] } else { 0 };
        let b2 = if chunk.len() > 2 { chunk[2] } else { 0 };

        out.push(ALPHABET[(b0 >> 2) as usize] as char);
        out.push(ALPHABET[(((b0 & 0x03) << 4) | (b1 >> 4)) as usize] as char);

        if chunk.len() > 1 {
            out.push(ALPHABET[(((b1 & 0x0f) << 2) | (b2 >> 6)) as usize] as char);
        } else {
            out.push('=');
        }

        if chunk.len() > 2 {
            out.push(ALPHABET[(b2 & 0x3f) as usize] as char);
        } else {
            out.push('=');
        }
    }

    out
}

/// Decode RFC 4648 §4 standard Base64 with strict alphabet, length, and
/// terminal-padding validation.
pub fn decode(input: &str) -> CryptoResult<Vec<u8>> {
    let bytes = input.as_bytes();
    if bytes.is_empty() {
        return Ok(Vec::new());
    }
    if bytes.len() % 4 != 0 {
        return Err(encoding_error("Base64 length must be a multiple of 4"));
    }

    let first_padding = bytes.iter().position(|&b| b == b'=');
    if let Some(pos) = first_padding {
        let padding_len = bytes.len() - pos;
        if padding_len > 2 || !bytes[pos..].iter().all(|&b| b == b'=') {
            return Err(encoding_error(
                "Base64 padding must be the final 1 or 2 bytes",
            ));
        }
    }

    let mut out = Vec::with_capacity((bytes.len() / 4) * 3);
    for quartet in bytes.chunks_exact(4) {
        let pad = quartet.iter().filter(|&&b| b == b'=').count();
        let v0 = decode_byte(quartet[0])?;
        let v1 = decode_byte(quartet[1])?;
        let v2 = if quartet[2] == b'=' {
            0
        } else {
            decode_byte(quartet[2])?
        };
        let v3 = if quartet[3] == b'=' {
            0
        } else {
            decode_byte(quartet[3])?
        };

        out.push((v0 << 2) | (v1 >> 4));
        if pad < 2 {
            out.push(((v1 & 0x0f) << 4) | (v2 >> 2));
        }
        if pad == 0 {
            out.push(((v2 & 0x03) << 6) | v3);
        }
    }

    Ok(out)
}

fn decode_byte(byte: u8) -> CryptoResult<u8> {
    match byte {
        b'A'..=b'Z' => Ok(byte - b'A'),
        b'a'..=b'z' => Ok(byte - b'a' + 26),
        b'0'..=b'9' => Ok(byte - b'0' + 52),
        b'+' => Ok(62),
        b'/' => Ok(63),
        b'=' => Err(encoding_error("Base64 padding is not a data byte")),
        _ => Err(encoding_error("Base64 contains a non-alphabet byte")),
    }
}

fn encoding_error(message: &str) -> CryptoError {
    CryptoError::EncodingError(message.to_string())
}

#[cfg(test)]
mod tests {
    use super::{decode, encode};
    use rand::rngs::StdRng;
    use rand::{RngCore, SeedableRng};

    #[test]
    fn rfc4648_section_10_vectors() {
        let vectors = [
            ("", ""),
            ("f", "Zg=="),
            ("fo", "Zm8="),
            ("foo", "Zm9v"),
            ("foob", "Zm9vYg=="),
            ("fooba", "Zm9vYmE="),
            ("foobar", "Zm9vYmFy"),
        ];

        for (plain, encoded) in vectors {
            assert_eq!(encode(plain.as_bytes()), encoded);
            assert_eq!(
                decode(encoded).expect("valid RFC 4648 vector"),
                plain.as_bytes()
            );
        }
    }

    #[test]
    fn roundtrip_null_bytes_and_utf8() {
        let with_nulls = b"\x00abc\x00\xff";
        assert_eq!(decode(&encode(with_nulls)).expect("roundtrip"), with_nulls);

        let chinese = "密码实验平台".as_bytes();
        assert_eq!(decode(&encode(chinese)).expect("roundtrip"), chinese);
    }

    #[test]
    fn roundtrip_seeded_random_1kb() {
        let mut rng = StdRng::seed_from_u64(0x4648);
        let mut input = [0u8; 1024];
        rng.fill_bytes(&mut input);

        let encoded = encode(&input);
        assert_eq!(decode(&encoded).expect("random roundtrip"), input);
    }

    #[test]
    fn invalid_decode_inputs_are_rejected() {
        assert!(decode("Zm9v*").is_err());
        assert!(decode("Zg=").is_err());
        assert!(decode("Z=g=").is_err());
        assert!(decode("Z===").is_err());
    }
}
