//! SHA-3 family (FIPS 202): SHA3-256, SHA3-512. Built on the Keccak-f[1600]
//! permutation. We provide the two sizes required by the assignment;
//! Keccak-f and absorb/squeeze are shared internals.

/// One-shot SHA3-256.
pub fn sha3_256(_data: &[u8]) -> Vec<u8> {
    todo!("Keccak[c=512], rate=1088 bits, output 256 bits")
}

/// One-shot SHA3-512.
pub fn sha3_512(_data: &[u8]) -> Vec<u8> {
    todo!("Keccak[c=1024], rate=576 bits, output 512 bits")
}

/// Keccak-f[1600] permutation — 24 rounds over a 5×5×64 state.
fn _keccak_f1600(_state: &mut [u64; 25]) {
    todo!("θ, ρ, π, χ, ι steps per FIPS 202 §3.2")
}
