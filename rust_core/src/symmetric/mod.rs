//! Block ciphers: AES (128/192/256), SM4, RC6.
//!
//! Each sub-module exposes:
//!   - a struct implementing [`crate::traits::SymmetricCipher`]
//!   - module-level `encrypt_dispatch` / `decrypt_dispatch` fns used by the
//!     FFI layer to pick a mode (ECB / CBC / CTR / GCM) at runtime.

pub mod aes;
pub mod rc6;
pub mod sm4;
