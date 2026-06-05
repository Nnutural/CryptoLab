//! Shared traits that every algorithm family implements.
//!
//! These exist so the upper layers can dispatch generically (`fn encrypt<C:
//! SymmetricCipher>(...)`) and so the criterion benches can sweep across
//! algorithm impls without bespoke wiring.

use crate::error::CryptoResult;

/// A fixed-block-size symmetric cipher (AES, SM4, RC6).
///
/// Implementors expose **block** primitives only; chaining (ECB / CBC / CTR /
/// GCM) is composed via the [`crate::modes`] adapters.
pub trait SymmetricCipher: Sized {
    /// Block size in bytes.
    const BLOCK_SIZE: usize;
    /// Key size in bytes that this construction accepts.
    /// Algorithms that support multiple key sizes (AES) expose this via a
    /// `&[usize]` slice in a dedicated `KEY_SIZES` const.
    const KEY_SIZE: usize;

    /// Initialize a cipher instance from key material.
    fn new(key: &[u8]) -> CryptoResult<Self>;

    /// Encrypt a single block in place.
    fn encrypt_block(&self, block: &mut [u8]) -> CryptoResult<()>;

    /// Decrypt a single block in place.
    fn decrypt_block(&self, block: &mut [u8]) -> CryptoResult<()>;

    /// Encrypt a block while capturing every-round intermediate state.
    ///
    /// Used by the "可视化中间过程导出" feature exposed through
    /// `?verbose=true` on the HTTP layer. Default impl: not supported.
    fn encrypt_with_trace(&self, _block: &mut [u8]) -> CryptoResult<EncryptionTrace> {
        Err(crate::error::CryptoError::Internal(
            "encrypt_with_trace not implemented for this cipher".to_string(),
        ))
    }
}

/// Per-round state snapshot for educational tracing.
#[derive(Debug, Clone, Default)]
pub struct EncryptionTrace {
    /// The state-matrix bytes captured at the end of each round.
    pub rounds: Vec<RoundState>,
    /// Round keys derived from the master key, one per round.
    pub round_keys: Vec<Vec<u8>>,
    /// Per-round timings in nanoseconds (best-effort, not constant-time).
    pub timings_ns: Vec<u64>,
}

/// One round's working state.
#[derive(Debug, Clone)]
pub struct RoundState {
    /// 1-based round index.
    pub round: usize,
    /// Snapshot of the block state at the end of this round.
    pub state: Vec<u8>,
    /// Free-form note (e.g. "after SubBytes", "after MixColumns") for the
    /// front-end visualization layer to label the snapshot.
    pub note: &'static str,
}

/// A keyless cryptographic hash (SHA-1, SHA-2, SHA-3 family, RIPEMD).
pub trait HashAlgorithm: Sized + Default {
    /// Digest length in bytes.
    const DIGEST_SIZE: usize;
    /// Internal block size in bytes (used by HMAC for ipad/opad sizing).
    const BLOCK_SIZE: usize;

    /// Reset the hasher to its initial state.
    fn reset(&mut self);

    /// Absorb `data` into the running state.
    fn update(&mut self, data: &[u8]);

    /// Finalize and write the digest into `out`.
    /// `out` must be exactly `DIGEST_SIZE` bytes.
    fn finalize_into(self, out: &mut [u8]) -> CryptoResult<()>;

    /// Convenience: one-shot hash of `data`.
    fn digest(data: &[u8]) -> Vec<u8> {
        let mut h = Self::default();
        h.update(data);
        let mut out = vec![0u8; Self::DIGEST_SIZE];
        // Safe: digest_size matches our allocation above.
        let _ = h.finalize_into(&mut out);
        out
    }
}

/// An asymmetric primitive supporting any subset of {encrypt, decrypt, sign,
/// verify}. Concrete impls (RSA, ECC, ECDSA) document which operations apply.
pub trait PublicKeyAlgorithm {
    /// The opaque public-key type.
    type PublicKey;
    /// The opaque private-key type.
    type PrivateKey;
    /// Signature type (Vec<u8> for RSA, (r, s) pair for ECDSA, ...).
    type Signature;

    /// Generate a fresh keypair.
    fn generate_keypair() -> CryptoResult<(Self::PublicKey, Self::PrivateKey)>;

    /// Encrypt `plaintext` with `pk`. Returns `Err` for sign-only schemes.
    fn encrypt(_pk: &Self::PublicKey, _plaintext: &[u8]) -> CryptoResult<Vec<u8>> {
        Err(crate::error::CryptoError::Internal(
            "encrypt not supported by this primitive".to_string(),
        ))
    }

    /// Decrypt `ciphertext` with `sk`. Returns `Err` for sign-only schemes.
    fn decrypt(_sk: &Self::PrivateKey, _ciphertext: &[u8]) -> CryptoResult<Vec<u8>> {
        Err(crate::error::CryptoError::Internal(
            "decrypt not supported by this primitive".to_string(),
        ))
    }

    /// Sign `message` with `sk`. Returns `Err` for encrypt-only schemes.
    fn sign(_sk: &Self::PrivateKey, _message: &[u8]) -> CryptoResult<Self::Signature> {
        Err(crate::error::CryptoError::Internal(
            "sign not supported by this primitive".to_string(),
        ))
    }

    /// Verify `signature` over `message` against `pk`.
    fn verify(
        _pk: &Self::PublicKey,
        _message: &[u8],
        _signature: &Self::Signature,
    ) -> CryptoResult<()> {
        Err(crate::error::CryptoError::Internal(
            "verify not supported by this primitive".to_string(),
        ))
    }
}
