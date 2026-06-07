"""Bridge for RSA / ECC / ECDSA to the Rust public-key primitives."""

from __future__ import annotations

from app.core.exceptions import CryptoAPIException
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


async def rsa_keygen(req: RsaKeygenRequest) -> RsaKeygenResponse:
    try:
        import cryptolab_core

        n, e, d, p, q = cryptolab_core.rsa_generate_keypair(req.bits, req.e)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.PARAM_MISSING, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc

    return RsaKeygenResponse(
        n_hex=n.hex(),
        e_hex=e.hex(),
        d_hex=d.hex(),
        p_hex=p.hex(),
        q_hex=q.hex(),
        warning=(
            "Private key is returned for demo only; production should store encrypted "
            "private key and return key_id"
        ),
    )


async def rsa_encrypt(req: RsaEncryptRequest) -> RsaEncryptResponse:
    try:
        import cryptolab_core

        ciphertext = cryptolab_core.rsa_encrypt_oaep(
            req.plaintext.encode("utf-8"),
            _from_hex(req.n_hex, "n_hex"),
            _from_hex(req.e_hex, "e_hex"),
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCRYPT_FAILED, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaEncryptResponse(ciphertext_hex=ciphertext.hex())


async def rsa_decrypt(req: RsaDecryptRequest) -> RsaDecryptResponse:
    try:
        import cryptolab_core

        plaintext = cryptolab_core.rsa_decrypt_oaep(
            _from_hex(req.ciphertext_hex, "ciphertext_hex"),
            _from_hex(req.n_hex, "n_hex"),
            _from_hex(req.d_hex, "d_hex"),
            _from_hex(req.p_hex, "p_hex"),
            _from_hex(req.q_hex, "q_hex"),
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.DECRYPT_FAILED, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaDecryptResponse(plaintext=plaintext.decode("utf-8"))


async def rsa_sign(req: RsaSignRequest) -> RsaSignResponse:
    try:
        import cryptolab_core

        signature = cryptolab_core.rsa_sign_pss(
            req.message.encode("utf-8"),
            _from_hex(req.n_hex, "n_hex"),
            _from_hex(req.d_hex, "d_hex"),
            _from_hex(req.p_hex, "p_hex"),
            _from_hex(req.q_hex, "q_hex"),
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaSignResponse(signature_hex=signature.hex())


async def rsa_verify(req: RsaVerifyRequest) -> RsaVerifyResponse:
    try:
        import cryptolab_core

        valid = cryptolab_core.rsa_verify_pss(
            req.message.encode("utf-8"),
            _from_hex(req.signature_hex, "signature_hex"),
            _from_hex(req.n_hex, "n_hex"),
            _from_hex(req.e_hex, "e_hex"),
        )
    except ValueError:
        return RsaVerifyResponse(valid=False)
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return RsaVerifyResponse(valid=bool(valid))


async def ecc_keygen(req: EccKeygenRequest) -> EccKeygenResponse:
    try:
        import cryptolab_core

        d, qx, qy = cryptolab_core.ecc_generate_keypair(req.curve)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.PARAM_MISSING, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EccKeygenResponse(curve=req.curve, d_hex=d.hex(), qx_hex=qx.hex(), qy_hex=qy.hex())


async def ecdsa_sign(req: EcdsaSignRequest) -> EcdsaSignResponse:
    try:
        import cryptolab_core

        r, s = cryptolab_core.ecdsa_sign(
            req.message.encode("utf-8"),
            _from_hex(req.d_hex, "d_hex"),
            req.curve,
        )
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, str(exc)) from exc
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EcdsaSignResponse(r_hex=r.hex(), s_hex=s.hex(), curve=req.curve)


async def ecdsa_verify(req: EcdsaVerifyRequest) -> EcdsaVerifyResponse:
    try:
        import cryptolab_core

        valid = cryptolab_core.ecdsa_verify(
            req.message.encode("utf-8"),
            _from_hex(req.r_hex, "r_hex"),
            _from_hex(req.s_hex, "s_hex"),
            _from_hex(req.qx_hex, "qx_hex"),
            _from_hex(req.qy_hex, "qy_hex"),
            req.curve,
        )
    except ValueError:
        return EcdsaVerifyResponse(valid=False, curve=req.curve)
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR) from exc
    return EcdsaVerifyResponse(valid=bool(valid), curve=req.curve)


def _from_hex(value: str, field: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, f"{field} must be hex") from exc
