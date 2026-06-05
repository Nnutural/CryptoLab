//! SHA-2 family (FIPS 180-4): SHA-224, SHA-256, SHA-384, SHA-512.

/// One-shot SHA-224.
pub fn sha224(_data: &[u8]) -> Vec<u8> {
    todo!("SHA-224: SHA-256 with different IV, truncated to 224 bits")
}

/// One-shot SHA-256.
pub fn sha256(_data: &[u8]) -> Vec<u8> {
    todo!("SHA-256 compression function over 64 rounds, IV from FIPS 180-4")
}

/// One-shot SHA-384.
pub fn sha384(_data: &[u8]) -> Vec<u8> {
    todo!("SHA-384: SHA-512 with different IV, truncated to 384 bits")
}

/// One-shot SHA-512.
pub fn sha512(_data: &[u8]) -> Vec<u8> {
    todo!("SHA-512 compression function over 80 rounds, 64-bit words")
}
