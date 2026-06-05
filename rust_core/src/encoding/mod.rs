//! Text encodings: Base64 (RFC 4648) and UTF-8 (RFC 3629).
//!
//! These do not provide confidentiality — they are reversible mappings. Only
//! kept here so the system has every primitive that the assignment requires.

pub mod base64;
pub mod utf8;
