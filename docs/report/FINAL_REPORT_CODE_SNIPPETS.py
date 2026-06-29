"""
CryptoLab final report code snippets.

Purpose:
    Open this file in VSCode, copy highlighted code blocks, and paste them into Word.
    The file is intentionally written as Python-style source/pseudocode for display.
    It is not meant to be executed as a complete program.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import math
import os
from dataclasses import dataclass
from typing import Any


# =============================================================================
# Figure 1-1: report structure and evidence chain
# =============================================================================

FIGURE_1_1_MERMAID = r"""
flowchart TD
  A[第1章 引言] --> B[第2章 系统设计]
  B --> C[第3章 算法实现]
  C --> D[第4章 执行结果与系统展示]
  D --> E[第5章 接口设计与调用]
  E --> F[第6章 总结与展望]
  F --> G[第7章 参考文献与附录]
  B -.证据.-> H[源码/CSV/日志/截图]
  C -.验证.-> H
  D -.复现.-> H
"""


# =============================================================================
# Figure 2-1: six-layer architecture
# =============================================================================

FIGURE_2_1_MERMAID = r"""
flowchart TB
  L6[表示层 React/Vite 前端与 Swagger UI] --> L4[接口层 FastAPI Router + Pydantic]
  L4 --> L3[服务层 Key/Audit/Benchmark/Demo/Scenario]
  L3 --> L2[算法层 Rust cryptolab_core via PyO3]
  L3 --> L1[数据层 SQLAlchemy + SQLite/PostgreSQL]
  L4 --> M[中间件 JWT/RateLimit/Trace/Audit]
  M --> C[Redis 或 Memory Cache]
  G[网关层 Nginx/Docker Compose] -.部署路径.-> L6
  G -.反向代理.-> L4
"""


# =============================================================================
# Figure 2-2: database entity relationship model
# =============================================================================

FIGURE_2_2_MERMAID = r"""
erDiagram
  users ||--o{ key_store : owns
  users ||--o{ operation_logs : emits
  key_store ||--o{ key_store : pairs
  algorithm_metrics {
    int id
    string algorithm
    string operation
    bigint data_size_bytes
    bigint duration_ns
  }
  users {
    int id
    string username
    string password_hash
    bytes salt
  }
  key_store {
    string id
    int user_id
    string algorithm
    bytes key_material_encrypted
  }
  operation_logs {
    int id
    string trace_id
    string operation
    string algorithm
    int status_code
  }
"""


# =============================================================================
# Figure 2-3: request trust boundary and data flow
# =============================================================================

FIGURE_2_3_MERMAID = r"""
flowchart LR
  U[Browser or Third-party Client] -->|HTTP + JWT| A[FastAPI Middleware]
  A -->|schema valid| R[Router]
  R --> S[Service Layer]
  S -->|PyO3 bytes| C[Rust Core]
  S -->|ORM| D[(Database)]
  A -->|rate_limit key| Redis[(Redis or Memory Cache)]
  S -->|audit record| D
  C -->|result or error| S
  S -->|APIResponse + trace_id| U
"""


# =============================================================================
# Section 3.1: PyO3 boundary registration
# =============================================================================

REGISTERED_RUST_FUNCTIONS = [
    "aes_encrypt",
    "aes_encrypt_with_trace",
    "aes_decrypt",
    "sm4_encrypt",
    "sm4_decrypt",
    "rc6_encrypt",
    "rc6_decrypt",
    "sha1",
    "sha256_digest",
    "sha3_256_digest",
    "ripemd160_digest",
    "hmac_sha1",
    "hmac_sha256",
    "pbkdf2_hmac_sha256",
    "base64_encode",
    "base64_decode",
    "utf8_encode",
    "utf8_decode",
    "rsa_generate_keypair",
    "rsa_encrypt_oaep",
    "rsa_decrypt_oaep",
    "rsa_sign_pss",
    "rsa_verify_pss",
    "ecc_generate_keypair",
    "ecdsa_sign",
    "ecdsa_verify",
    "rsa_demo_unsafe_keygen",
    "rsa_demo_unsafe_encrypt_raw",
    "rsa_demo_cube_root",
    "ecdsa_demo_sign_with_k",
    "ecdsa_demo_recover_d_from_k_reuse",
]


RUST_FFI_REGISTER_SNIPPET = r"""
// rust_core/src/ffi.rs:19-80
pub fn register(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(aes_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(aes_encrypt_with_trace, m)?)?;
    m.add_function(wrap_pyfunction!(aes_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sm4_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sm4_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rc6_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(rc6_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(sha1, m)?)?;
    m.add_function(wrap_pyfunction!(sha256_digest, m)?)?;
    m.add_function(wrap_pyfunction!(sha3_256_digest, m)?)?;
    m.add_function(wrap_pyfunction!(ripemd160_digest, m)?)?;
    m.add_function(wrap_pyfunction!(hmac_sha1, m)?)?;
    m.add_function(wrap_pyfunction!(hmac_sha256, m)?)?;
    m.add_function(wrap_pyfunction!(pbkdf2_hmac_sha256, m)?)?;
    m.add_function(wrap_pyfunction!(base64_encode, m)?)?;
    m.add_function(wrap_pyfunction!(base64_decode, m)?)?;
    m.add_function(wrap_pyfunction!(utf8_encode, m)?)?;
    m.add_function(wrap_pyfunction!(utf8_decode, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_generate_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_encrypt_oaep, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_decrypt_oaep, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_sign_pss, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_verify_pss, m)?)?;
    m.add_function(wrap_pyfunction!(ecc_generate_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_sign, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_verify, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_demo_unsafe_keygen, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_demo_unsafe_encrypt_raw, m)?)?;
    m.add_function(wrap_pyfunction!(rsa_demo_cube_root, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_demo_sign_with_k, m)?)?;
    m.add_function(wrap_pyfunction!(ecdsa_demo_recover_d_from_k_reuse, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
"""


def register_cryptolab_core(module: dict[str, Any]) -> None:
    """Python-style rendering of rust_core/src/ffi.rs registration."""
    for function_name in REGISTERED_RUST_FUNCTIONS:
        module[function_name] = f"wrap_pyfunction!({function_name})"
    module["__version__"] = "CARGO_PKG_VERSION"


# =============================================================================
# Algorithm 3-1: strict Base64 decode
# =============================================================================

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def strict_base64_decode(text: str) -> bytes:
    """Algorithm 3-1 Strict Base64 Decode."""
    if len(text) % 4 != 0:
        raise ValueError("Base64 length must be a multiple of 4")

    padding_started = False
    for index, ch in enumerate(text):
        if ch == "=":
            padding_started = True
            if index < len(text) - 2:
                raise ValueError("padding appears too early")
        elif padding_started:
            raise ValueError("non-padding character after padding")
        elif ch not in BASE64_ALPHABET:
            raise ValueError("invalid Base64 alphabet")

    return base64.b64decode(text, validate=True)


# =============================================================================
# Algorithm 3-2: SHA-256 compression loop
# =============================================================================

def rotr32(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def sha256_compression_loop(words: list[int], state: list[int], constants: list[int]) -> list[int]:
    """Algorithm 3-2 SHA-256 Compression Loop."""
    w = words[:]
    for t in range(16, 64):
        s0 = rotr32(w[t - 15], 7) ^ rotr32(w[t - 15], 18) ^ (w[t - 15] >> 3)
        s1 = rotr32(w[t - 2], 17) ^ rotr32(w[t - 2], 19) ^ (w[t - 2] >> 10)
        w.append((w[t - 16] + s0 + w[t - 7] + s1) & 0xFFFFFFFF)

    a, b, c, d, e, f, g, h = state
    for t in range(64):
        ch = (e & f) ^ ((~e) & g)
        maj = (a & b) ^ (a & c) ^ (b & c)
        big_sigma0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22)
        big_sigma1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25)
        t1 = (h + big_sigma1 + ch + constants[t] + w[t]) & 0xFFFFFFFF
        t2 = (big_sigma0 + maj) & 0xFFFFFFFF
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF

    return [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]


# =============================================================================
# Algorithm 3-3: HMAC-SHA256
# =============================================================================

def hmac_sha256_manual(key: bytes, message: bytes) -> bytes:
    """Algorithm 3-3 HMAC-SHA256."""
    block_size = 64
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()
    key_block = key.ljust(block_size, b"\x00")

    ipad = bytes(byte ^ 0x36 for byte in key_block)
    opad = bytes(byte ^ 0x5C for byte in key_block)
    inner_digest = hashlib.sha256(ipad + message).digest()
    return hashlib.sha256(opad + inner_digest).digest()


def verify_hmac_sha256(key: bytes, message: bytes, tag: bytes) -> bool:
    """Constant-time HMAC tag comparison."""
    expected = hmac_sha256_manual(key, message)
    return hmac.compare_digest(expected, tag)


# =============================================================================
# Algorithm 3-4: PBKDF2-HMAC-SHA256
# =============================================================================

def pbkdf2_hmac_sha256_manual(password: bytes, salt: bytes, iterations: int, key_len: int) -> bytes:
    """Algorithm 3-4 PBKDF2-HMAC-SHA256."""
    h_len = 32
    if iterations <= 0:
        raise ValueError("PBKDF2 iterations must be at least 1")
    if key_len <= 0:
        raise ValueError("PBKDF2 key_len must be greater than 0")

    blocks = math.ceil(key_len / h_len)
    derived = bytearray()

    for block_index in range(1, blocks + 1):
        salt_block = salt + block_index.to_bytes(4, "big")
        u = hmac_sha256_manual(password, salt_block)
        t = bytearray(u)
        for _ in range(1, iterations):
            u = hmac_sha256_manual(password, u)
            for i in range(h_len):
                t[i] ^= u[i]
        derived.extend(t)

    return bytes(derived[:key_len])


# =============================================================================
# Algorithm 3-5: AES block encryption
# =============================================================================

AES_BLOCK_SIZE = 16
S_BOX = [0] * 256
RCON = [0] * 16


def rot_word(word: list[int]) -> list[int]:
    return [word[1], word[2], word[3], word[0]]


def sub_word(word: list[int]) -> list[int]:
    return [S_BOX[b] for b in word]


def expand_key(key: bytes, nk: int, rounds: int) -> bytes:
    total_words = 4 * (rounds + 1)
    words = [[0, 0, 0, 0] for _ in range(total_words)]

    for i in range(nk):
        words[i] = list(key[i * 4 : i * 4 + 4])

    for i in range(nk, total_words):
        temp = words[i - 1][:]
        if i % nk == 0:
            temp = sub_word(rot_word(temp))
            temp[0] ^= RCON[i // nk]
        elif nk > 6 and i % nk == 4:
            temp = sub_word(temp)
        words[i] = [words[i - nk][j] ^ temp[j] for j in range(4)]

    return bytes(byte for word in words for byte in word)


def add_round_key(state: bytearray, round_key: bytes) -> None:
    for i in range(AES_BLOCK_SIZE):
        state[i] ^= round_key[i]


def sub_bytes(state: bytearray) -> None:
    for i, byte in enumerate(state):
        state[i] = S_BOX[byte]


def shift_rows(state: bytearray) -> None:
    tmp = state[:]
    for r in range(4):
        for c in range(4):
            state[r + 4 * c] = tmp[r + 4 * ((c + r) % 4)]


def gf_mul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        carry = a & 0x80
        a = (a << 1) & 0xFF
        if carry:
            a ^= 0x1B
        b >>= 1
    return result


def mix_columns(state: bytearray) -> None:
    for c in range(4):
        i = 4 * c
        a0, a1, a2, a3 = state[i], state[i + 1], state[i + 2], state[i + 3]
        state[i] = gf_mul(a0, 2) ^ gf_mul(a1, 3) ^ a2 ^ a3
        state[i + 1] = a0 ^ gf_mul(a1, 2) ^ gf_mul(a2, 3) ^ a3
        state[i + 2] = a0 ^ a1 ^ gf_mul(a2, 2) ^ gf_mul(a3, 3)
        state[i + 3] = gf_mul(a0, 3) ^ a1 ^ a2 ^ gf_mul(a3, 2)


def aes_block_encrypt_pseudocode(block: bytes, expanded_key: bytes, rounds: int) -> bytes:
    """Algorithm 3-5 AES Block Encryption."""
    state = bytearray(block)
    add_round_key(state, expanded_key[:AES_BLOCK_SIZE])
    for round_index in range(1, rounds):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        start = round_index * AES_BLOCK_SIZE
        add_round_key(state, expanded_key[start : start + AES_BLOCK_SIZE])
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, expanded_key[rounds * AES_BLOCK_SIZE : (rounds + 1) * AES_BLOCK_SIZE])
    return bytes(state)


# =============================================================================
# Algorithm 3-6: SM4 32-round transform
# =============================================================================

def sm4_t_transform(x: int) -> int:
    """Placeholder for SM4 tau + linear transform."""
    return x


def sm4_round_transform(words: list[int], round_keys: list[int]) -> list[int]:
    """Algorithm 3-6 SM4 32-Round Transform."""
    x = words[:]
    for i in range(32):
        next_word = x[i] ^ sm4_t_transform(x[i + 1] ^ x[i + 2] ^ x[i + 3] ^ round_keys[i])
        x.append(next_word)
    return [x[35], x[34], x[33], x[32]]


# =============================================================================
# Algorithm 3-7: RSA key generation and CRT private operation
# =============================================================================

def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, n: int) -> int:
    g, x, _ = egcd(a % n, n)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % n


@dataclass
class RsaPrivateKey:
    n: int
    e: int
    d: int
    p: int
    q: int
    dp: int
    dq: int
    qinv: int

    def private_op_crt(self, c: int) -> int:
        """CRT private operation."""
        m1 = pow(c, self.dp, self.p)
        m2 = pow(c, self.dq, self.q)
        diff = (m1 - (m2 % self.p)) % self.p
        h_value = (self.qinv * diff) % self.p
        return m2 + self.q * h_value

    def private_op_crt_blinded(self, c: int) -> int:
        """CRT private operation with multiplicative blinding."""
        for _ in range(128):
            r = 2 + int.from_bytes(os.urandom(32), "big") % max(2, self.n - 2)
            if math.gcd(r, self.n) != 1:
                continue
            r_inv = mod_inverse(r, self.n)
            blinded_c = (c * pow(r, self.e, self.n)) % self.n
            blinded_m = self.private_op_crt(blinded_c)
            return (blinded_m * r_inv) % self.n
        raise RuntimeError("failed to sample invertible RSA blinding factor")


# =============================================================================
# Section 3.5.3: ECC-160 point arithmetic
# =============================================================================

@dataclass
class Curve:
    p: int
    a: int
    b: int
    gx: int
    gy: int
    n: int


@dataclass
class AffinePoint:
    x: int = 0
    y: int = 0
    infinity: bool = False

    @staticmethod
    def inf() -> "AffinePoint":
        return AffinePoint(0, 0, True)


def mod_add(a: int, b: int, p: int) -> int:
    return (a + b) % p


def mod_sub(a: int, b: int, p: int) -> int:
    return (a - b) % p


def point_add(curve: Curve, p1: AffinePoint, p2: AffinePoint) -> AffinePoint:
    if p1.infinity:
        return p2
    if p2.infinity:
        return p1
    if p1.x == p2.x:
        if mod_add(p1.y, p2.y, curve.p) == 0:
            return AffinePoint.inf()
        return point_double(curve, p1)

    numerator = mod_sub(p2.y, p1.y, curve.p)
    denominator = mod_sub(p2.x, p1.x, curve.p)
    lam = numerator * mod_inverse(denominator, curve.p) % curve.p
    x3 = mod_sub(mod_sub(lam * lam % curve.p, p1.x, curve.p), p2.x, curve.p)
    y3 = mod_sub(lam * mod_sub(p1.x, x3, curve.p) % curve.p, p1.y, curve.p)
    return AffinePoint(x3, y3, False)


def point_double(curve: Curve, point: AffinePoint) -> AffinePoint:
    if point.infinity or point.y == 0:
        return AffinePoint.inf()
    numerator = (3 * point.x * point.x + curve.a) % curve.p
    denominator = (2 * point.y) % curve.p
    lam = numerator * mod_inverse(denominator, curve.p) % curve.p
    x3 = mod_sub(mod_sub(lam * lam % curve.p, point.x, curve.p), point.x, curve.p)
    y3 = mod_sub(lam * mod_sub(point.x, x3, curve.p) % curve.p, point.y, curve.p)
    return AffinePoint(x3, y3, False)


def scalar_mul_point(curve: Curve, point: AffinePoint, k: int) -> AffinePoint:
    """Montgomery-ladder-shaped scalar multiplication."""
    r0 = AffinePoint.inf()
    r1 = point
    for i in reversed(range(k.bit_length())):
        add = point_add(curve, r0, r1)
        dbl0 = point_double(curve, r0)
        dbl1 = point_double(curve, r1)
        if (k >> i) & 1:
            r0, r1 = add, dbl1
        else:
            r0, r1 = dbl0, add
    return r0


# =============================================================================
# Algorithm 3-8: ECDSA signing with RFC 6979 nonce
# =============================================================================

def bits2int(data: bytes, qlen: int) -> int:
    value = int.from_bytes(data, "big")
    excess = len(data) * 8 - qlen
    return value >> excess if excess > 0 else value


def int2octets(value: int, length: int) -> bytes:
    return value.to_bytes(length, "big")


def bits2octets(data: bytes, n: int) -> bytes:
    z1 = bits2int(data, n.bit_length())
    z2 = z1 % n
    return int2octets(z2, (n.bit_length() + 7) // 8)


def rfc6979_generate_k(d: int, message: bytes, n: int, retry: int = 0) -> int:
    """RFC 6979 HMAC-SHA256 deterministic nonce generation."""
    qlen = n.bit_length()
    rlen = (qlen + 7) // 8
    bx = int2octets(d, rlen)
    bh = bits2octets(hashlib.sha256(message).digest(), n)
    v = b"\x01" * 32
    k = b"\x00" * 32

    k = hmac_sha256_manual(k, v + b"\x00" + bx + bh)
    v = hmac_sha256_manual(k, v)
    k = hmac_sha256_manual(k, v + b"\x01" + bx + bh)
    v = hmac_sha256_manual(k, v)

    for _ in range(retry + 1):
        while True:
            t = b""
            while len(t) < rlen:
                v = hmac_sha256_manual(k, v)
                t += v
            secret = bits2int(t, qlen)
            if 1 <= secret < n:
                if retry == 0:
                    return secret
                break
            k = hmac_sha256_manual(k, v + b"\x00")
            v = hmac_sha256_manual(k, v)
    return 1


def ecdsa_sign_pseudocode(curve: Curve, private_key: int, message: bytes) -> tuple[int, int]:
    """Algorithm 3-8 ECDSA Signing with RFC 6979 Nonce."""
    n = curve.n
    z = bits2int(hashlib.sha256(message).digest(), n.bit_length())
    k = rfc6979_generate_k(private_key, message, n)
    base = AffinePoint(curve.gx, curve.gy, False)
    r_point = scalar_mul_point(curve, base, k)
    r = r_point.x % n
    s = mod_inverse(k, n) * (z + r * private_key) % n
    if r == 0 or s == 0:
        return ecdsa_sign_pseudocode(curve, private_key, message + b"\x00")
    return r, s


def recover_ecdsa_private_key_from_k_reuse(
    z1: int,
    z2: int,
    s1: int,
    s2: int,
    r: int,
    n: int,
) -> int:
    """ECDSA nonce reuse attack from equations (3-18) and (3-19)."""
    k = ((z1 - z2) * mod_inverse(s1 - s2, n)) % n
    d = ((s1 * k - z1) * mod_inverse(r, n)) % n
    return d


# =============================================================================
# Algorithm 4-1: three-layer cross validation
# =============================================================================

def three_layer_cross_validation(
    standard_vectors: list[dict[str, Any]],
    third_party_oracle: Any,
    http_api_client: Any,
) -> list[dict[str, Any]]:
    """Algorithm 4-1 Three-Layer Cross Validation."""
    validation_report = []
    for vector in standard_vectors:
        local_result = vector["cryptolab_function"](*vector["inputs"])
        standard_ok = local_result == vector["expected"]

        if third_party_oracle is None:
            oracle_ok = "limited"
        else:
            oracle_ok = local_result == third_party_oracle(vector)

        api_result = http_api_client.post(vector["endpoint"], json=vector["payload"])
        api_ok = api_result["code"] == 1000 and api_result["data"] == vector["api_expected"]

        validation_report.append(
            {
                "algorithm": vector["algorithm"],
                "standard_vector": standard_ok,
                "third_party": oracle_ok,
                "http_api": api_ok,
            }
        )
    return validation_report


# =============================================================================
# Section 4.7: secure file transfer sequence
# =============================================================================

SECURE_FILE_TRANSFER_SEQUENCE = r"""
sequenceDiagram
  participant S as Sender
  participant API as FastAPI Service
  participant R as Rust Core
  participant T as Receiver
  S->>API: secure_file_transfer/send(file, RSA pub, ECDSA priv)
  API->>R: AES-GCM encrypt + SHA256 + ECDSA sign + RSA-OAEP wrap
  R-->>API: envelope
  API-->>S: APIResponse(code=1000, envelope)
  S->>T: transmit envelope
  T->>API: secure_file_transfer/receive(envelope, RSA priv, ECDSA pub)
  API->>R: unwrap + decrypt + digest check + verify
  R-->>API: plaintext or error
  API-->>T: APIResponse(code, result)
"""


def secure_file_transfer_send(file_bytes: bytes, rsa_public_key: Any, ecdsa_private_key: Any) -> dict[str, Any]:
    session_key = os.urandom(32)
    ciphertext, tag, iv = aes_gcm_encrypt_placeholder(session_key, file_bytes)
    digest = hashlib.sha256(file_bytes).digest()
    signature = ecdsa_sign_placeholder(ecdsa_private_key, digest)
    wrapped_key = rsa_oaep_wrap_placeholder(rsa_public_key, session_key)
    return {
        "wrapped_key": wrapped_key,
        "ciphertext": ciphertext,
        "tag": tag,
        "iv": iv,
        "digest": digest,
        "signature": signature,
    }


def secure_file_transfer_receive(envelope: dict[str, Any], rsa_private_key: Any, ecdsa_public_key: Any) -> bytes:
    session_key = rsa_oaep_unwrap_placeholder(rsa_private_key, envelope["wrapped_key"])
    plaintext = aes_gcm_decrypt_placeholder(session_key, envelope["ciphertext"], envelope["iv"], envelope["tag"])
    digest = hashlib.sha256(plaintext).digest()
    if not hmac.compare_digest(digest, envelope["digest"]):
        raise ValueError("digest check failed")
    if not ecdsa_verify_placeholder(ecdsa_public_key, digest, envelope["signature"]):
        raise ValueError("signature verification failed")
    return plaintext


def aes_gcm_encrypt_placeholder(key: bytes, plaintext: bytes) -> tuple[bytes, bytes, bytes]:
    return plaintext[::-1], b"tag", b"iv"


def aes_gcm_decrypt_placeholder(key: bytes, ciphertext: bytes, iv: bytes, tag: bytes) -> bytes:
    return ciphertext[::-1]


def rsa_oaep_wrap_placeholder(public_key: Any, session_key: bytes) -> bytes:
    return b"wrapped:" + session_key


def rsa_oaep_unwrap_placeholder(private_key: Any, wrapped_key: bytes) -> bytes:
    return wrapped_key.removeprefix(b"wrapped:")


def ecdsa_sign_placeholder(private_key: Any, digest: bytes) -> bytes:
    return b"signature:" + digest[:8]


def ecdsa_verify_placeholder(public_key: Any, digest: bytes, signature: bytes) -> bool:
    return signature == b"signature:" + digest[:8]


# =============================================================================
# Figure 5-1: JWT authentication and blacklist sequence
# =============================================================================

JWT_AUTH_SEQUENCE = r"""
sequenceDiagram
  participant C as Client
  participant A as Auth Router
  participant M as Auth Middleware
  participant Cache as Redis/Memory Cache
  participant R as Protected Router
  C->>A: POST /api/v1/auth/login
  A-->>C: access_token + expires_at
  C->>M: Bearer token request
  M->>Cache: get jwt_blacklist:{jti}
  Cache-->>M: not found
  M->>R: authenticated user context
  R-->>C: APIResponse(code=1000, trace_id)
  C->>A: POST /api/v1/auth/logout
  A->>Cache: setex jwt_blacklist:{jti}
"""


def jwt_authentication_flow(client_request: dict[str, Any], cache: dict[str, Any]) -> dict[str, Any]:
    token = client_request["headers"]["Authorization"].removeprefix("Bearer ")
    jti = parse_jti_placeholder(token)
    if f"jwt_blacklist:{jti}" in cache:
        return api_response(code=4105, message="AUTH_TOKEN_BLACKLISTED", data=None)
    user_context = {"user_id": parse_user_id_placeholder(token)}
    return protected_router_placeholder(user_context)


def logout_flow(token: str, cache: dict[str, Any]) -> None:
    jti = parse_jti_placeholder(token)
    ttl = token_remaining_ttl_placeholder(token)
    cache[f"jwt_blacklist:{jti}"] = {"ttl": ttl}


def parse_jti_placeholder(token: str) -> str:
    return "jti-from-token"


def parse_user_id_placeholder(token: str) -> int:
    return 1


def token_remaining_ttl_placeholder(token: str) -> int:
    return 1800


def protected_router_placeholder(user_context: dict[str, Any]) -> dict[str, Any]:
    return api_response(code=1000, message="OK", data={"user": user_context})


# =============================================================================
# Figure 5-2: request-response data flow
# =============================================================================

FIGURE_5_2_MERMAID = r"""
flowchart LR
  Client[Client] --> Trace[TraceID Middleware]
  Trace --> Rate[Rate Limit Middleware]
  Rate --> Auth[Auth Middleware]
  Auth --> Router[FastAPI Router]
  Router --> Service[Service Layer]
  Service --> Rust[Rust Core via PyO3]
  Service --> DB[(SQLAlchemy DB)]
  Service --> Audit[Audit Record]
  Audit --> DB
  Rust --> Service
  Service --> Response[APIResponse]
  Response --> Client
"""


def request_response_pipeline(request: dict[str, Any]) -> dict[str, Any]:
    trace_id = request.get("headers", {}).get("X-Trace-Id") or generate_trace_id_placeholder()
    request["trace_id"] = trace_id

    if rate_limited_placeholder(request):
        return api_response(code=5001, message="RATE_LIMIT_EXCEEDED", data=None, trace_id=trace_id)
    if not authenticated_placeholder(request):
        return api_response(code=4103, message="AUTH_TOKEN_INVALID", data=None, trace_id=trace_id)

    route_result = fastapi_router_placeholder(request)
    service_result = service_layer_placeholder(route_result)
    audit_record_placeholder(request, service_result)
    return api_response(code=1000, message="OK", data=service_result, trace_id=trace_id)


def generate_trace_id_placeholder() -> str:
    return "trace-id"


def rate_limited_placeholder(request: dict[str, Any]) -> bool:
    return False


def authenticated_placeholder(request: dict[str, Any]) -> bool:
    return True


def fastapi_router_placeholder(request: dict[str, Any]) -> dict[str, Any]:
    return {"operation": "sha256", "payload": request.get("json", {})}


def service_layer_placeholder(route_result: dict[str, Any]) -> dict[str, Any]:
    payload = route_result["payload"].get("data", "").encode()
    digest = hashlib.sha256(payload).hexdigest()
    return {"digest_hex": digest}


def audit_record_placeholder(request: dict[str, Any], result: dict[str, Any]) -> None:
    audit_record = {
        "trace_id": request["trace_id"],
        "status_code": 1000,
        "input_hash": hashlib.sha256(repr(request.get("json", {})).encode()).hexdigest(),
        "output_hash": hashlib.sha256(repr(result).encode()).hexdigest(),
        "duration_ms": 1.0,
    }
    _ = audit_record


def api_response(code: int, message: str, data: Any, trace_id: str | None = None) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
        "trace_id": trace_id or generate_trace_id_placeholder(),
    }


# =============================================================================
# Section 5.5: third-party API call examples
# =============================================================================

CURL_HASH_API_EXAMPLE = r"""
curl -X POST "http://127.0.0.1:8000/api/v1/hash/sha256" \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"BUPT CryptoLab\"}"
"""


def python_hash_api_example() -> None:
    import httpx

    payload = {"data": "BUPT CryptoLab"}
    resp = httpx.post("http://127.0.0.1:8000/api/v1/hash/sha256", json=payload)
    body = resp.json()
    assert body["code"] == 1000
    print(body["data"]["digest_hex"], body["trace_id"])


# =============================================================================
# End of report code snippets
# =============================================================================
