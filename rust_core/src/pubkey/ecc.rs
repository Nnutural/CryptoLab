//! Elliptic-curve primitives over short Weierstrass curves.
//!
//! Current production target is SEC 2 secp160r1. Scalar multiplication uses a
//! Montgomery ladder shape: each scalar bit performs one point addition and
//! one point doubling before selecting the next pair of accumulators.

use num_bigint::BigUint;
use num_traits::{One, Zero};

use crate::bigint::CryptoBigInt;
use crate::error::{CryptoError, CryptoResult};

/// Short-Weierstrass parameters: y^2 = x^3 + a*x + b over GF(p), with base
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

/// Internal affine point representation.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AffinePoint {
    /// x-coordinate modulo p.
    pub x: BigUint,
    /// y-coordinate modulo p.
    pub y: BigUint,
    /// Whether this point is the point at infinity.
    pub infinity: bool,
}

/// Internal curve representation with parsed integers.
#[derive(Debug, Clone)]
pub struct Curve {
    /// Field prime.
    pub p: BigUint,
    /// Curve coefficient a.
    pub a: BigUint,
    /// Curve coefficient b.
    pub b: BigUint,
    /// Base point.
    pub g: AffinePoint,
    /// Group order.
    pub n: BigUint,
    /// Coordinate size in bytes.
    pub field_len: usize,
}

/// Resolve named curve to its parameter set.
pub fn curve_params(name: &str) -> CryptoResult<CurveParams> {
    let curve = curve(name)?;
    Ok(CurveParams {
        p: curve.p.to_bytes_be(),
        a: curve.a.to_bytes_be(),
        b: curve.b.to_bytes_be(),
        gx: to_fixed_bytes(&curve.g.x, curve.field_len),
        gy: to_fixed_bytes(&curve.g.y, curve.field_len),
        n: curve.n.to_bytes_be(),
        h: 1,
    })
}

/// Resolve a named curve to parsed integer parameters.
pub fn curve(name: &str) -> CryptoResult<Curve> {
    match name {
        "secp160r1" => {
            let p = parse_hex("ffffffffffffffffffffffffffffffff7fffffff")?;
            let a = parse_hex("ffffffffffffffffffffffffffffffff7ffffffc")?;
            let b = parse_hex("1c97befc54bd7a8b65acf89f81d4d4adc565fa45")?;
            let gx = parse_hex("4a96b5688ef573284664698968c38bb913cbfc82")?;
            let gy = parse_hex("23a628553168947d59dcc912042351377ac5fb32")?;
            let n = parse_hex("0100000000000000000001f4c8f927aed3ca752257")?;
            Ok(Curve {
                p,
                a,
                b,
                g: AffinePoint {
                    x: gx,
                    y: gy,
                    infinity: false,
                },
                n,
                field_len: 20,
            })
        }
        other => Err(CryptoError::InvalidParameter(format!(
            "unknown curve: {other}"
        ))),
    }
}

/// Generate a fresh ECC keypair on `curve`. Returns `(d, px, py)` as big-
/// endian bytes; `d in [1, n-1]`, `(px, py) = d * G`.
pub fn keygen(curve_name: &str) -> CryptoResult<(Vec<u8>, Vec<u8>, Vec<u8>)> {
    let curve = curve(curve_name)?;
    let one = BigUint::one();
    let upper = CryptoBigInt(&curve.n - &one);
    let d = CryptoBigInt::random_below(&upper)?.0 + &one;
    let q = scalar_mul_point(&curve, &curve.g, &d)?;
    if q.infinity {
        return Err(CryptoError::Internal(
            "generated ECC public key at infinity".to_string(),
        ));
    }
    Ok((
        d.to_bytes_be(),
        to_fixed_bytes(&q.x, curve.field_len),
        to_fixed_bytes(&q.y, curve.field_len),
    ))
}

/// Scalar multiplication `k * P` using a Montgomery-ladder algorithm.
pub fn scalar_mul(
    params: &CurveParams,
    k: &[u8],
    px: &[u8],
    py: &[u8],
) -> CryptoResult<(Vec<u8>, Vec<u8>)> {
    let curve = Curve {
        p: BigUint::from_bytes_be(&params.p),
        a: BigUint::from_bytes_be(&params.a),
        b: BigUint::from_bytes_be(&params.b),
        g: AffinePoint {
            x: BigUint::from_bytes_be(&params.gx),
            y: BigUint::from_bytes_be(&params.gy),
            infinity: false,
        },
        n: BigUint::from_bytes_be(&params.n),
        field_len: params.p.len(),
    };
    let point = AffinePoint {
        x: BigUint::from_bytes_be(px),
        y: BigUint::from_bytes_be(py),
        infinity: false,
    };
    if !is_on_curve(&curve, &point) {
        return Err(CryptoError::InvalidKey("ECC point is off-curve".to_string()));
    }
    let out = scalar_mul_point(&curve, &point, &BigUint::from_bytes_be(k))?;
    if out.infinity {
        return Err(CryptoError::InvalidKey(
            "scalar multiplication returned infinity".to_string(),
        ));
    }
    Ok((
        to_fixed_bytes(&out.x, curve.field_len),
        to_fixed_bytes(&out.y, curve.field_len),
    ))
}

/// Multiply an affine point by an integer scalar.
pub fn scalar_mul_point(curve: &Curve, point: &AffinePoint, k: &BigUint) -> CryptoResult<AffinePoint> {
    let mut r0 = AffinePoint::infinity();
    let mut r1 = point.clone();
    for i in (0..k.bits()).rev() {
        let add = point_add(curve, &r0, &r1)?;
        let dbl0 = point_double(curve, &r0)?;
        let dbl1 = point_double(curve, &r1)?;
        if k.bit(i) {
            r0 = add;
            r1 = dbl1;
        } else {
            r0 = dbl0;
            r1 = add;
        }
    }
    Ok(r0)
}

impl AffinePoint {
    /// The point at infinity.
    pub fn infinity() -> Self {
        Self {
            x: BigUint::zero(),
            y: BigUint::zero(),
            infinity: true,
        }
    }
}

/// Add two affine points.
pub fn point_add(curve: &Curve, p1: &AffinePoint, p2: &AffinePoint) -> CryptoResult<AffinePoint> {
    if p1.infinity {
        return Ok(p2.clone());
    }
    if p2.infinity {
        return Ok(p1.clone());
    }
    if p1.x == p2.x {
        if mod_add(&p1.y, &p2.y, &curve.p).is_zero() {
            return Ok(AffinePoint::infinity());
        }
        return point_double(curve, p1);
    }

    let numerator = mod_sub(&p2.y, &p1.y, &curve.p);
    let denominator = mod_sub(&p2.x, &p1.x, &curve.p);
    let inv = mod_inv(&denominator, &curve.p)?;
    let lambda = (&numerator * inv) % &curve.p;
    let x3 = mod_sub(
        &mod_sub(&(&lambda * &lambda % &curve.p), &p1.x, &curve.p),
        &p2.x,
        &curve.p,
    );
    let y3 = mod_sub(&(&lambda * mod_sub(&p1.x, &x3, &curve.p) % &curve.p), &p1.y, &curve.p);
    Ok(AffinePoint {
        x: x3,
        y: y3,
        infinity: false,
    })
}

/// Double an affine point.
pub fn point_double(curve: &Curve, point: &AffinePoint) -> CryptoResult<AffinePoint> {
    if point.infinity || point.y.is_zero() {
        return Ok(AffinePoint::infinity());
    }
    let three = BigUint::from(3u32);
    let two = BigUint::from(2u32);
    let numerator = (&three * &point.x * &point.x + &curve.a) % &curve.p;
    let denominator = (&two * &point.y) % &curve.p;
    let inv = mod_inv(&denominator, &curve.p)?;
    let lambda = (numerator * inv) % &curve.p;
    let x3 = mod_sub(
        &mod_sub(&(&lambda * &lambda % &curve.p), &point.x, &curve.p),
        &point.x,
        &curve.p,
    );
    let y3 = mod_sub(
        &(&lambda * mod_sub(&point.x, &x3, &curve.p) % &curve.p),
        &point.y,
        &curve.p,
    );
    Ok(AffinePoint {
        x: x3,
        y: y3,
        infinity: false,
    })
}

/// Check whether a point satisfies the curve equation.
pub fn is_on_curve(curve: &Curve, point: &AffinePoint) -> bool {
    if point.infinity {
        return true;
    }
    let lhs = (&point.y * &point.y) % &curve.p;
    let rhs = ((&point.x * &point.x * &point.x) + (&curve.a * &point.x) + &curve.b) % &curve.p;
    lhs == rhs
}

fn mod_inv(value: &BigUint, modulus: &BigUint) -> CryptoResult<BigUint> {
    CryptoBigInt(value.clone())
        .mod_inverse(&CryptoBigInt(modulus.clone()))
        .map(|v| v.0)
        .ok_or_else(|| CryptoError::BigIntError("modular inverse does not exist".to_string()))
}

fn mod_add(a: &BigUint, b: &BigUint, modulus: &BigUint) -> BigUint {
    (a + b) % modulus
}

fn mod_sub(a: &BigUint, b: &BigUint, modulus: &BigUint) -> BigUint {
    if a >= b {
        (a - b) % modulus
    } else {
        (a + modulus - b) % modulus
    }
}

fn parse_hex(s: &str) -> CryptoResult<BigUint> {
    let bytes = hex::decode(s).map_err(|err| CryptoError::EncodingError(err.to_string()))?;
    Ok(BigUint::from_bytes_be(&bytes))
}

/// Fixed-width big-endian coordinate encoding.
pub fn to_fixed_bytes(value: &BigUint, len: usize) -> Vec<u8> {
    let bytes = value.to_bytes_be();
    if bytes.len() >= len {
        return bytes;
    }
    let mut out = vec![0u8; len - bytes.len()];
    out.extend_from_slice(&bytes);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn secp160r1_base_point_is_on_curve() {
        let curve = curve("secp160r1").expect("curve");
        assert!(is_on_curve(&curve, &curve.g));
    }

    #[test]
    fn double_matches_add() {
        let curve = curve("secp160r1").expect("curve");
        let doubled = point_double(&curve, &curve.g).expect("double");
        let added = point_add(&curve, &curve.g, &curve.g).expect("add");
        assert_eq!(doubled, added);
    }

    #[test]
    fn order_times_base_point_is_infinity() {
        let curve = curve("secp160r1").expect("curve");
        let out = scalar_mul_point(&curve, &curve.g, &curve.n).expect("scalar");
        assert!(out.infinity);
    }

    #[test]
    fn group_law_for_small_scalars() {
        let curve = curve("secp160r1").expect("curve");
        let k = BigUint::from(123u32);
        let kp = BigUint::from(456u32);
        let left = scalar_mul_point(&curve, &curve.g, &(&k + &kp)).expect("left");
        let kg = scalar_mul_point(&curve, &curve.g, &k).expect("kg");
        let kpg = scalar_mul_point(&curve, &curve.g, &kp).expect("kpg");
        let right = point_add(&curve, &kg, &kpg).expect("add");
        assert_eq!(left, right);
    }
}
