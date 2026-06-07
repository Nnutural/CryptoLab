"""Bridge for RSA / ECC / ECDSA — key_id based flow."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.security import AuthenticatedUser
from app.core.status_codes import StatusCode
from app.schemas.pubkey import (
    EccKeygenRequest,
    EccKeygenResponse,
    EcdsaSignRequest,
    EcdsaSignResponse,
    EcdsaVerifyRequest,
    EcdsaVerifyResponse,
    RsaDecryptRequest,
    RsaDecryptResponse,
    RsaEncryptRequest,
    RsaEncryptResponse,
    RsaKeygenRequest,
    RsaKeygenResponse,
    RsaSignRequest,
    RsaSignResponse,
    RsaVerifyRequest,
    RsaVerifyResponse,
)
from app.services import key_service


async def rsa_keygen(
    db: Session, user: AuthenticatedUser, req: RsaKeygenRequest
) -> RsaKeygenResponse:
    try:
        import cryptolab_core

        n, e, d, p, q = cryptolab_core.rsa_generate_keypair(req.bits, req.e)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.PARAM_MISSING, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    private_material = {
        "n_hex": n.hex(),
        "e_hex": e.hex(),
        "d_hex": d.hex(),
        "p_hex": p.hex(),
        "q_hex": q.hex(),
    }
    public_material = {"n_hex": n.hex(), "e_hex": e.hex()}

    priv_id, pub_id = key_service.store_key_pair(
        db, user, "rsa", private_material, public_material, req.label
    )
    return RsaKeygenResponse(
        private_key_id=priv_id, public_key_id=pub_id, bits=req.bits
    )


async def rsa_encrypt(
    db: Session, user: AuthenticatedUser, req: RsaEncryptRequest
) -> RsaEncryptResponse:
    mat = key_service.fetch_and_decrypt_json(db, user, req.key_id, "public")
    try:
        import cryptolab_core

        ciphertext = cryptolab_core.rsa_encrypt_oaep(
            req.plaintext.encode("utf-8"),
            _hex(mat, "n_hex"),
            _hex(mat, "e_hex"),
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCRYPT_FAILED, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaEncryptResponse(ciphertext_hex=ciphertext.hex())


async def rsa_decrypt(
    db: Session, user: AuthenticatedUser, req: RsaDecryptRequest
) -> RsaDecryptResponse:
    mat = key_service.fetch_and_decrypt_json(db, user, req.key_id, "private")
    try:
        import cryptolab_core

        plaintext = cryptolab_core.rsa_decrypt_oaep(
            bytes.fromhex(req.ciphertext_hex),
            _hex(mat, "n_hex"),
            _hex(mat, "d_hex"),
            _hex(mat, "p_hex"),
            _hex(mat, "q_hex"),
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.DECRYPT_FAILED, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaDecryptResponse(plaintext=plaintext.decode("utf-8"))


async def rsa_sign(
    db: Session, user: AuthenticatedUser, req: RsaSignRequest
) -> RsaSignResponse:
    mat = key_service.fetch_and_decrypt_json(db, user, req.key_id, "private")
    try:
        import cryptolab_core

        signature = cryptolab_core.rsa_sign_pss(
            req.message.encode("utf-8"),
            _hex(mat, "n_hex"),
            _hex(mat, "d_hex"),
            _hex(mat, "p_hex"),
            _hex(mat, "q_hex"),
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaSignResponse(signature_hex=signature.hex())


async def rsa_verify(
    db: Session, user: AuthenticatedUser, req: RsaVerifyRequest
) -> RsaVerifyResponse:
    mat = key_service.fetch_and_decrypt_json(db, user, req.key_id, "public")
    try:
        import cryptolab_core

        valid = cryptolab_core.rsa_verify_pss(
            req.message.encode("utf-8"),
            bytes.fromhex(req.signature_hex),
            _hex(mat, "n_hex"),
            _hex(mat, "e_hex"),
        )
    except ValueError:
        return RsaVerifyResponse(valid=False)
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaVerifyResponse(valid=bool(valid))


async def ecc_keygen(
    db: Session, user: AuthenticatedUser, req: EccKeygenRequest
) -> EccKeygenResponse:
    try:
        import cryptolab_core

        d, qx, qy = cryptolab_core.ecc_generate_keypair(req.curve)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.PARAM_MISSING, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    private_material = {"d_hex": d.hex(), "curve": req.curve}
    public_material = {"qx_hex": qx.hex(), "qy_hex": qy.hex(), "curve": req.curve}

    priv_id, pub_id = key_service.store_key_pair(
        db, user, "ecc", private_material, public_material, req.label
    )
    return EccKeygenResponse(
        private_key_id=priv_id, public_key_id=pub_id, curve=req.curve
    )


async def ecdsa_sign(
    db: Session, user: AuthenticatedUser, req: EcdsaSignRequest
) -> EcdsaSignResponse:
    mat = key_service.fetch_and_decrypt_json(db, user, req.key_id, "private")
    try:
        import cryptolab_core

        r, s = cryptolab_core.ecdsa_sign(
            req.message.encode("utf-8"),
            _hex(mat, "d_hex"),
            req.curve,
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EcdsaSignResponse(r_hex=r.hex(), s_hex=s.hex(), curve=req.curve)


async def ecdsa_verify(
    db: Session, user: AuthenticatedUser, req: EcdsaVerifyRequest
) -> EcdsaVerifyResponse:
    mat = key_service.fetch_and_decrypt_json(db, user, req.key_id, "public")
    try:
        import cryptolab_core

        valid = cryptolab_core.ecdsa_verify(
            req.message.encode("utf-8"),
            bytes.fromhex(req.r_hex),
            bytes.fromhex(req.s_hex),
            _hex(mat, "qx_hex"),
            _hex(mat, "qy_hex"),
            req.curve,
        )
    except ValueError:
        return EcdsaVerifyResponse(valid=False, curve=req.curve)
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EcdsaVerifyResponse(valid=bool(valid), curve=req.curve)


def _hex(mat: dict[str, str], key: str) -> bytes:
    try:
        return bytes.fromhex(mat[key])
    except (KeyError, ValueError) as exc:
        raise CryptoAPIException(StatusCode.INTERNAL, f"corrupt key material: {key}") from exc
