//! RIPEMD-160 (Dobbertin, Bosselaers & Preneel, 1996).
//!
//! 160-bit output, 80 rounds split across two parallel pipelines.

/// One-shot RIPEMD-160.
pub fn ripemd160(_data: &[u8]) -> Vec<u8> {
    todo!("two parallel lines over 5 rounds × 16 ops, then mix")
}
