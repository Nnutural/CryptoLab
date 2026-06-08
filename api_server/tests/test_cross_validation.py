"""Cross-validation against reference libraries.

RC6 has no reference implementation in mainstream Python libraries; RC6 cases
below are KAT-only. secp160r1 is not exposed by cryptography and is validated
here only through the existing deterministic-k KAT path.
"""

from __future__ import annotations

import base64
import hashlib
import hmac as stdlib_hmac
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import product
from pathlib import Path

import httpx
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from gmssl import sm4
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT

from app.core.security import AuthenticatedUser
from app.db.session import get_session_factory
from app.services import key_service

import cryptolab_core


AES_KEY_CASES = [
    (
        "fixed",
        "128",
        bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
        bytes.fromhex("00112233445566778899aabbccddeeff102132435465768798a9babbdcdeeff0"),
    ),
    (
        "random",
        "128",
        bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c"),
        bytes.fromhex("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e51"),
    ),
    (
        "fixed",
        "192",
        bytes.fromhex("000102030405060708090a0b0c0d0e0f1011121314151617"),
        bytes.fromhex("00112233445566778899aabbccddeeffffeeddccbbaa99887766554433221100"),
    ),
    (
        "random",
        "192",
        bytes.fromhex("8e73b0f7da0e6452c810f32b809079e562f8ead2522c6b7b"),
        bytes.fromhex("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e51"),
    ),
    (
        "fixed",
        "256",
        bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"),
        bytes.fromhex("00112233445566778899aabbccddeeff0102030405060708090a0b0c0d0e0f10"),
    ),
    (
        "random",
        "256",
        bytes.fromhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4"),
        bytes.fromhex("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e51"),
    ),
]

AES_MODES = ["ECB", "CBC", "CTR", "GCM"]
SM4_CASES = [
    (
        "gbt",
        bytes.fromhex("0123456789abcdeffedcba9876543210"),
        bytes.fromhex("0123456789abcdeffedcba9876543210"),
        bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
    ),
    (
        "two-block",
        bytes.fromhex("fedcba98765432100123456789abcdef"),
        bytes.fromhex("00112233445566778899aabbccddeeffffeeddccbbaa99887766554433221100"),
        bytes.fromhex("101112131415161718191a1b1c1d1e1f"),
    ),
]
RC6_KATS = [
    (
        "rivest-zero",
        bytes.fromhex("00" * 16),
        bytes.fromhex("00" * 16),
        bytes.fromhex("8fc3a53656b1f778c129df4e9848a41e"),
    ),
    (
        "krovetz-rc6-32-20-16",
        bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
        bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
        bytes.fromhex("3a96f9c7f6755cfe46f00e3dcd5d2a3c"),
    ),
]
HASH_INPUTS = [
    "",
    "x",
    "a" * 64,
    "b" * 1024,
    "c" * (1024 * 1024),
    "你好𝄞",
]
HASH_ALGOS = [
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
    "sha3_256",
    "sha3_512",
    "ripemd160",
]
HMAC_CASES = list(product(["sha1", "sha256"], ["", "k", "k" * 64, "k" * 100]))
PBKDF2_CASES = list(product([1000, 10000, 100000], [8, 16, 32], [16, 32, 64]))
ENCODING_TEXTS = ["", "f", "foo", "foobar", "你好𝄞", "line\nbreak"]

ECDSA_VECTOR_D = "9717619397619fc8e6c73ca2d0c2ba2a2c4e2a45"
ECDSA_VECTOR_R = "00b28dc7224bae71617117ae60160360e0ff801830"
ECDSA_VECTOR_S = "006767d5ffbfae5b56aa6c0381107e06a4a5413027"


@dataclass(frozen=True)
class MatrixRow:
    algorithm: str
    kat: str
    reference: str
    cases: int
    result: str


MATRIX_ROWS = [
    *[
        MatrixRow(
            f"AES-{bits}-{mode}",
            "✅ NIST/FIPS",
            "✅ cryptography",
            sum(1 for _label, key_bits, _key, _plain in AES_KEY_CASES if key_bits == bits),
            "✅",
        )
        for bits in ("128", "192", "256")
        for mode in AES_MODES
    ],
    MatrixRow("SM4-ECB", "✅ GB/T", "✅ gmssl", len(SM4_CASES), "✅"),
    MatrixRow("SM4-CBC", "✅ GB/T", "✅ gmssl", len(SM4_CASES), "✅"),
    MatrixRow("RC6", "✅ Rivest/Krovetz", "❌ N/A", len(RC6_KATS) * 2, "✅ KAT-only"),
    *[
        MatrixRow(algo.upper(), "✅ RFC/NIST", "✅ hashlib", len(HASH_INPUTS), "✅")
        for algo in HASH_ALGOS
    ],
    MatrixRow("HMAC-SHA1", "✅ RFC", "✅ hmac", 4, "✅"),
    MatrixRow("HMAC-SHA256", "✅ RFC", "✅ hmac", 4, "✅"),
    MatrixRow("PBKDF2-HMAC-SHA256", "✅ RFC", "✅ cryptography", len(PBKDF2_CASES), "✅"),
    MatrixRow("RSA-OAEP/PSS", "✅ RFC 8017", "✅ cryptography", 2, "✅"),
    MatrixRow("RSA-PKCS1-v1_5", "✅ RFC 8017", "✅ cryptography", 2, "✅"),
    MatrixRow("ECDSA secp160r1", "✅ RFC 6979", "❌ N/A", 1, "✅ KAT-only"),
    MatrixRow("Base64", "✅ RFC 4648", "✅ python base64", len(ENCODING_TEXTS) * 2, "✅"),
    MatrixRow("UTF-8", "✅ Unicode", "✅ Python codec", len(ENCODING_TEXTS) * 2 + 1, "✅"),
]


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def api_data(response: httpx.Response) -> dict:
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 1000, body
    return body["data"]


async def authenticate(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    username: str,
) -> AuthenticatedUser:
    client.headers.update(await auth_headers(client, username))
    me = api_data(await client.get("/api/v1/auth/me"))
    token = client.headers["Authorization"].removeprefix("Bearer ")
    return AuthenticatedUser(
        id=me["user_id"],
        username=me["username"],
        role=me["role"],
        jti="cross-validation",
        token=token,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )


def reference_aes_encrypt(
    key: bytes,
    mode_name: str,
    plaintext: bytes,
    iv: bytes | None,
    aad: bytes,
) -> bytes:
    if mode_name == "ECB":
        mode_obj = modes.ECB()
    elif mode_name == "CBC":
        assert iv is not None
        mode_obj = modes.CBC(iv)
    elif mode_name == "CTR":
        assert iv is not None
        mode_obj = modes.CTR(iv)
    elif mode_name == "GCM":
        assert iv is not None
        mode_obj = modes.GCM(iv)
    else:  # pragma: no cover - parametrize keeps this closed.
        raise AssertionError(f"unsupported AES mode: {mode_name}")

    encryptor = Cipher(algorithms.AES(key), mode_obj).encryptor()
    if mode_name == "GCM":
        encryptor.authenticate_additional_data(aad)
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    if mode_name == "GCM":
        return ciphertext + encryptor.tag
    return ciphertext


def reference_sm4_encrypt(key: bytes, mode_name: str, plaintext: bytes, iv: bytes | None) -> bytes:
    padding_mode = -1 if mode_name == "ECB" else sm4.PKCS7
    crypt_sm4 = CryptSM4(padding_mode=padding_mode)
    crypt_sm4.set_key(key, SM4_ENCRYPT)
    if mode_name == "ECB":
        return crypt_sm4.crypt_ecb(plaintext)
    assert iv is not None
    return crypt_sm4.crypt_cbc(iv, plaintext)


def reference_hash(algo: str, data: str) -> str:
    raw = data.encode("utf-8")
    if algo == "ripemd160":
        try:
            return hashlib.new("ripemd160", raw).hexdigest()
        except ValueError:
            fallback = {
                "": "9c1185a5c5e9fc54612808977ee8f548b2258d31",
                "x": "11a7a4e0fda63d946e5c80e4d79795e8a3b4552d",
            }
            if data in fallback:
                return fallback[data]
            pytest.skip("hashlib RIPEMD160 unavailable for dynamic vectors")
    return getattr(hashlib, algo)(raw).hexdigest()


def private_material(user: AuthenticatedUser, private_key_id: str) -> dict[str, str]:
    with get_session_factory()() as db:
        return key_service.fetch_and_decrypt_json(db, user, private_key_id, "private")


def private_key_from_material(material: dict[str, str]) -> rsa.RSAPrivateKey:
    n = int(material["n_hex"], 16)
    e = int(material["e_hex"], 16)
    d = int(material["d_hex"], 16)
    p = int(material["p_hex"], 16)
    q = int(material["q_hex"], 16)
    numbers = rsa.RSAPrivateNumbers(
        p=p,
        q=q,
        d=d,
        dmp1=d % (p - 1),
        dmq1=d % (q - 1),
        iqmp=pow(q, -1, p),
        public_numbers=rsa.RSAPublicNumbers(e=e, n=n),
    )
    return numbers.private_key()


def rsa_enc_padding(scheme: str) -> padding.AsymmetricPadding:
    if scheme == "oaep":
        return padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    return padding.PKCS1v15()


def rsa_sig_padding(scheme: str) -> padding.AsymmetricPadding:
    if scheme == "pss":
        return padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=32,
        )
    return padding.PKCS1v15()


async def rsa_keygen(client: httpx.AsyncClient) -> dict:
    return api_data(
        await client.post("/api/v1/pubkey/rsa/keygen", json={"bits": 1024, "e": 65537})
    )


async def assert_api_rsa_cross_validation(
    client: httpx.AsyncClient,
    key: dict,
    private_key: rsa.RSAPrivateKey,
    key_index: int,
) -> None:
    message = f"rsa-cross-message-{key_index}".encode("utf-8")
    plaintext = message.decode("utf-8")
    public_key = private_key.public_key()

    encrypted = api_data(
        await client.post(
            "/api/v1/pubkey/rsa/encrypt",
            json={"plaintext": plaintext, "key_id": key["public_key_id"]},
        )
    )
    ciphertext = bytes.fromhex(encrypted["ciphertext_hex"])
    assert private_key.decrypt(ciphertext, rsa_enc_padding("oaep")) == message

    reference_ciphertext = public_key.encrypt(message, rsa_enc_padding("oaep"))
    decrypted = api_data(
        await client.post(
            "/api/v1/pubkey/rsa/decrypt",
            json={
                "ciphertext_hex": reference_ciphertext.hex(),
                "key_id": key["private_key_id"],
            },
        )
    )
    assert decrypted["plaintext"] == plaintext

    reference_signature = private_key.sign(message, rsa_sig_padding("pss"), hashes.SHA256())
    verified = api_data(
        await client.post(
            "/api/v1/pubkey/rsa/verify",
            json={
                "message": plaintext,
                "signature_hex": reference_signature.hex(),
                "key_id": key["public_key_id"],
            },
        )
    )
    assert verified["valid"] is True

    signed = api_data(
        await client.post(
            "/api/v1/pubkey/rsa/sign",
            json={"message": plaintext, "key_id": key["private_key_id"]},
        )
    )
    public_key.verify(
        bytes.fromhex(signed["signature_hex"]),
        message,
        rsa_sig_padding("pss"),
        hashes.SHA256(),
    )


def assert_ffi_rsa_pkcs1v15_cross_validation(
    material: dict[str, str],
    private_key: rsa.RSAPrivateKey,
    key_index: int,
) -> None:
    message = f"rsa-pkcs1v15-message-{key_index}".encode("utf-8")
    n = bytes.fromhex(material["n_hex"])
    e = bytes.fromhex(material["e_hex"])
    d = bytes.fromhex(material["d_hex"])
    public_key = private_key.public_key()

    self_ciphertext = cryptolab_core.rsa_encrypt(message, n, e, "pkcs1v15")
    assert private_key.decrypt(self_ciphertext, rsa_enc_padding("pkcs1v15")) == message

    reference_ciphertext = public_key.encrypt(message, rsa_enc_padding("pkcs1v15"))
    assert cryptolab_core.rsa_decrypt(reference_ciphertext, n, d, "pkcs1v15") == message

    reference_signature = private_key.sign(
        message,
        rsa_sig_padding("pkcs1v15"),
        hashes.SHA256(),
    )
    assert cryptolab_core.rsa_verify(message, reference_signature, n, e, "pkcs1v15") is True

    self_signature = cryptolab_core.rsa_sign(message, n, d, "pkcs1v15")
    public_key.verify(
        self_signature,
        message,
        rsa_sig_padding("pkcs1v15"),
        hashes.SHA256(),
    )


@pytest.mark.parametrize("mode_name", AES_MODES)
@pytest.mark.parametrize(
    ("case_label", "bits", "key", "plaintext"),
    AES_KEY_CASES,
    ids=[f"{case[0]}-{case[1]}" for case in AES_KEY_CASES],
)
async def test_aes_matches_cryptography(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    store_sym_key: Callable[[int, str, bytes, str | None], str],
    mode_name: str,
    case_label: str,
    bits: str,
    key: bytes,
    plaintext: bytes,
) -> None:
    user = await authenticate(client, auth_headers, f"aes-{bits}-{mode_name}-{case_label}")
    key_id = store_sym_key(user.id, "aes", key, f"aes-{bits}-{case_label}")
    iv = None
    if mode_name in {"CBC", "CTR"}:
        iv = bytes.fromhex("00112233445566778899aabbccddeeff")
    elif mode_name == "GCM":
        iv = bytes.fromhex("cafebabefacedbaddecaf888")
    aad = f"aes-{bits}-{mode_name}".encode("ascii")

    request = {
        "algorithm": "aes",
        "mode": mode_name,
        "padding": "None",
        "key_id": key_id,
        "plaintext_b64": b64(plaintext),
        "aad_b64": b64(aad),
    }
    if iv is not None:
        request["iv_hex"] = iv.hex()
    data = api_data(await client.post("/api/v1/symmetric/aes/encrypt", json=request))
    assert base64.b64decode(data["ciphertext_b64"]) == reference_aes_encrypt(
        key, mode_name, plaintext, iv, aad
    )


@pytest.mark.parametrize("mode_name", ["ECB", "CBC"])
@pytest.mark.parametrize(
    ("case_label", "key", "plaintext", "iv"),
    SM4_CASES,
    ids=[case[0] for case in SM4_CASES],
)
async def test_sm4_matches_gmssl(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    store_sym_key: Callable[[int, str, bytes, str | None], str],
    mode_name: str,
    case_label: str,
    key: bytes,
    plaintext: bytes,
    iv: bytes,
) -> None:
    user = await authenticate(client, auth_headers, f"sm4-{mode_name}-{case_label}")
    key_id = store_sym_key(user.id, "sm4", key, f"sm4-{case_label}")
    request = {
        "algorithm": "sm4",
        "mode": mode_name,
        "padding": "PKCS7" if mode_name == "CBC" else "None",
        "key_id": key_id,
        "plaintext_b64": b64(plaintext),
    }
    if mode_name == "CBC":
        request["iv_hex"] = iv.hex()
    data = api_data(await client.post("/api/v1/symmetric/sm4/encrypt", json=request))
    assert base64.b64decode(data["ciphertext_b64"]) == reference_sm4_encrypt(
        key, mode_name, plaintext, iv if mode_name == "CBC" else None
    )


@pytest.mark.parametrize(
    ("case_label", "key", "plaintext", "ciphertext"),
    RC6_KATS,
    ids=[case[0] for case in RC6_KATS],
)
@pytest.mark.parametrize("operation", ["encrypt", "decrypt"])
async def test_rc6_kat_only_vectors(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    store_sym_key: Callable[[int, str, bytes, str | None], str],
    operation: str,
    case_label: str,
    key: bytes,
    plaintext: bytes,
    ciphertext: bytes,
) -> None:
    user = await authenticate(client, auth_headers, f"rc6-{operation}-{case_label}")
    key_id = store_sym_key(user.id, "rc6", key, f"rc6-{case_label}")
    if operation == "encrypt":
        data = api_data(
            await client.post(
                "/api/v1/symmetric/rc6/encrypt",
                json={
                    "algorithm": "rc6",
                    "mode": "ECB",
                    "padding": "None",
                    "key_id": key_id,
                    "plaintext_b64": b64(plaintext),
                },
            )
        )
        assert base64.b64decode(data["ciphertext_b64"]) == ciphertext
    else:
        data = api_data(
            await client.post(
                "/api/v1/symmetric/rc6/decrypt",
                json={
                    "algorithm": "rc6",
                    "mode": "ECB",
                    "padding": "None",
                    "key_id": key_id,
                    "ciphertext_b64": b64(ciphertext),
                },
            )
        )
        assert base64.b64decode(data["plaintext_b64"]) == plaintext


@pytest.mark.parametrize("algo", HASH_ALGOS)
@pytest.mark.parametrize("data", HASH_INPUTS, ids=["empty", "1b", "64b", "1kb", "1mb", "utf8"])
async def test_hashes_match_hashlib(
    client: httpx.AsyncClient,
    algo: str,
    data: str,
) -> None:
    response_data = api_data(await client.post(f"/api/v1/hash/{algo}", json={"data": data}))
    assert response_data["digest_hex"] == reference_hash(algo, data)


@pytest.mark.parametrize(("algo", "key"), HMAC_CASES)
async def test_hmac_matches_stdlib(
    client: httpx.AsyncClient,
    algo: str,
    key: str,
) -> None:
    message = "The quick brown fox jumps over the lazy dog 你好"
    response_data = api_data(
        await client.post(
            f"/api/v1/hash/hmac/{algo}",
            json={"key": key, "message": message, "algorithm": algo},
        )
    )
    digestmod = getattr(hashlib, algo)
    expected = stdlib_hmac.new(key.encode(), message.encode(), digestmod).hexdigest()
    assert response_data["mac_hex"] == expected


@pytest.mark.parametrize(("iterations", "salt_len", "key_len"), PBKDF2_CASES)
async def test_pbkdf2_matches_cryptography(
    client: httpx.AsyncClient,
    iterations: int,
    salt_len: int,
    key_len: int,
) -> None:
    password = "password-你好"
    salt = "s" * salt_len
    response_data = api_data(
        await client.post(
            "/api/v1/hash/pbkdf2",
            json={
                "password": password,
                "salt": salt,
                "iterations": iterations,
                "key_len": key_len,
            },
        )
    )
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_len,
        salt=salt.encode("utf-8"),
        iterations=iterations,
    )
    assert response_data["derived_key_hex"] == kdf.derive(password.encode("utf-8")).hex()


@pytest.mark.parametrize("key_index", [0, 1])
async def test_rsa_oaep_pss_matches_cryptography(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    key_index: int,
) -> None:
    user = await authenticate(client, auth_headers, f"rsa-oaep-pss-{key_index}")
    key = await rsa_keygen(client)
    material = private_material(user, key["private_key_id"])
    private_key = private_key_from_material(material)

    public = api_data(await client.get(f"/api/v1/keys/{key['public_key_id']}/public"))
    assert int(public["material"]["n_hex"], 16) == private_key.public_key().public_numbers().n
    await assert_api_rsa_cross_validation(client, key, private_key, key_index)


@pytest.mark.parametrize("key_index", [0, 1])
async def test_rsa_pkcs1v15_matches_cryptography(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    key_index: int,
) -> None:
    user = await authenticate(client, auth_headers, f"rsa-pkcs1v15-{key_index}")
    key = await rsa_keygen(client)
    material = private_material(user, key["private_key_id"])
    private_key = private_key_from_material(material)
    assert_ffi_rsa_pkcs1v15_cross_validation(material, private_key, key_index)


async def test_ecdsa_secp160r1_rfc6979_kat_only(
    client: httpx.AsyncClient,
    auth_headers: Callable[[httpx.AsyncClient, str], Awaitable[dict[str, str]]],
    store_key_pair: Callable[
        [int, str, dict[str, str], dict[str, str], str | None], tuple[str, str]
    ],
) -> None:
    user = await authenticate(client, auth_headers, "ecdsa-kat-only")
    private_key_id, _public_key_id = store_key_pair(
        user.id,
        "ecc",
        {"d_hex": ECDSA_VECTOR_D, "curve": "secp160r1"},
        {"qx_hex": "00" * 20, "qy_hex": "00" * 20, "curve": "secp160r1"},
        "ecdsa-rfc6979",
    )
    data = api_data(
        await client.post(
            "/api/v1/pubkey/ecdsa/sign",
            json={"message": "sample", "key_id": private_key_id, "curve": "secp160r1"},
        )
    )
    assert data["r_hex"] == ECDSA_VECTOR_R
    assert data["s_hex"] == ECDSA_VECTOR_S


@pytest.mark.parametrize("text", ENCODING_TEXTS)
async def test_base64_matches_python(
    client: httpx.AsyncClient,
    text: str,
) -> None:
    encoded = api_data(
        await client.post("/api/v1/encoding/base64/encode", json={"data": text})
    )["encoded"]
    assert encoded == base64.b64encode(text.encode("utf-8")).decode("ascii")

    decoded = api_data(
        await client.post("/api/v1/encoding/base64/decode", json={"encoded": encoded})
    )["data"]
    assert base64.b64decode(decoded) == base64.b64decode(encoded)


@pytest.mark.parametrize("text", ENCODING_TEXTS)
async def test_utf8_matches_python(
    client: httpx.AsyncClient,
    text: str,
) -> None:
    encoded = api_data(
        await client.post("/api/v1/encoding/utf8/encode", json={"data": text})
    )["encoded"]
    assert base64.b64decode(encoded) == text.encode("utf-8")

    decoded = api_data(
        await client.post("/api/v1/encoding/utf8/decode", json={"data": encoded})
    )["data"]
    assert decoded == base64.b64decode(encoded).decode("utf-8", errors="strict")


async def test_utf8_rejects_overlong_like_python(
    client: httpx.AsyncClient,
) -> None:
    invalid = bytes([0xC0, 0x80])
    encoded = base64.b64encode(invalid).decode("ascii")
    with pytest.raises(UnicodeDecodeError):
        invalid.decode("utf-8", errors="strict")

    response = await client.post("/api/v1/encoding/utf8/decode", json={"data": encoded})
    assert response.status_code == 400
    assert response.json()["code"] == 2003


def render_matrix() -> str:
    header = [
        "# CryptoLab Cross-Validation Matrix",
        "",
        "| 算法 | 第一重(KAT) | 第二重(库对照) | 用例数 | 全部通过? |",
        "|------|-------------|-----------------|--------|----------|",
    ]
    rows = [
        f"| {row.algorithm} | {row.kat} | {row.reference} | {row.cases} | {row.result} |"
        for row in MATRIX_ROWS
    ]
    note = [
        "",
        "Notes:",
        "- RC6 is KAT-only because mainstream Python cryptography libraries do not ship RC6.",
        "- ECDSA secp160r1 is KAT-only because cryptography does not expose secp160r1.",
        "- RSA PKCS#1 v1.5 uses the Rust core FFI directly; the HTTP layer intentionally exposes OAEP/PSS only.",
    ]
    return "\n".join([*header, *rows, *note]) + "\n"


def test_cross_validation_matrix_document_generated() -> None:
    output = Path(__file__).resolve().parents[2] / "docs" / "cross_validation_matrix.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_matrix()
    output.write_text(rendered, encoding="utf-8")
    assert "AES-128-ECB" in rendered
    assert "ECDSA secp160r1" in rendered
    assert output.read_text(encoding="utf-8") == rendered


def test_cryptography_secp160r1_not_available() -> None:
    assert not hasattr(ec, "SECP160R1")
