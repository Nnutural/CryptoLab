//! Elliptic-curve primitives over short Weierstrass curves.
//!
//! Initial target: secp160r1 (SEC 2). Curve parameters resolved by name so
//! we can swap in secp256r1 / secp256k1 later without API churn.
//!
//! Implementation notes:
//!   - Use Jacobian projective coordinates to avoid modular inverses inside
//!     point doubling / addition.
//!   - Scalar multiplication MUST use Montgomery ladder for SPA resistance.

use crate::error::{CryptoError, CryptoResult};

/// Short-Weierstrass parameters: y^2 = x^3 + a·x + b over GF(p), with base
/// point G of order n and cofactor h.
pub struct CurveParams {
    /// Field prime.
    pub p: Vec<u8>,
    /// Curve coefficient a.
    pub a: Vec<u8>,
    /// Curve coefficient b.
    pub b: Vec<u8>,
    /// Base-point x-coordinate.
    pub gx: Vec<u8>,
    /// Base-point y-coordinate.
    pub gy: Vec<u8>,
    /// Group order.
    pub n: Vec<u8>,
    /// Cofactor (1 for prime-order curves).
    pub h: u32,
}

/// Resolve named curve to its parameter set.
pub fn curve_params(name: &str) -> CryptoResult<CurveParams> {
    match name {
        "secp160r1" => todo!("populate SEC 2 §2.4.2 parameters for secp160r1"),
        other => Err(CryptoError::InvalidParameter(format!(
            "unknown curve: {other}"
        ))),
    }
}

/// Generate a fresh ECC keypair on `curve`. Returns `(d, px, py)` as big-
/// endian bytes; `d ∈ [1, n-1]`, `(px, py) = d · G`.
pub fn keygen(_curve: &str) -> CryptoResult<(Vec<u8>, Vec<u8>, Vec<u8>)> {
    todo!("uniform d ∈ [1, n-1] via random_below; scalar_mul(G, d)")
}

/// Scalar multiplication `k · P` using a Montgomery-ladder constant-time
/// algorithm.
pub fn scalar_mul(
    _params: &CurveParams,
    _k: &[u8],
    _px: &[u8],
    _py: &[u8],
) -> CryptoResult<(Vec<u8>, Vec<u8>)> {
    todo!("Montgomery ladder over Jacobian coords; project back to affine at the end")
}
