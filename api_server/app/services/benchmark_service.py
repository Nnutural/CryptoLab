"""HTTP-side benchmark probes for Rust primitives."""

from __future__ import annotations

import secrets
import time
from collections.abc import Callable
from functools import lru_cache

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import StatusCode
from app.schemas.benchmark import BenchmarkResult
from app.services import metrics_service

ONE_MIB = 1024 * 1024
THROUGHPUT_PAYLOAD = bytes(i % 251 for i in range(ONE_MIB))
HMAC_MESSAGE = bytes(i % 197 for i in range(1024))
PBKDF2_PASSWORD = b"benchmark-password"
PBKDF2_SALT = b"benchmark-salt"
PBKDF2_INNER_ITERATIONS = 10_000
PUBKEY_MESSAGE = bytes(range(32))

THROUGHPUT_WARMUP = 5
THROUGHPUT_MIN_ITERATIONS = 100
THROUGHPUT_TARGET_NS = 1_000_000_000
HMAC_WARMUP = 5
HMAC_MIN_ITERATIONS = 1_000
HMAC_TARGET_NS = 1_000_000_000

Operation = Callable[[], object]


def measure(algo: str) -> BenchmarkResult:
    """Run an in-process benchmark for a supported algorithm branch."""
    normalized = _normalize(algo)
    try:
        import cryptolab_core

        if normalized in {"aes", "aes_ecb"}:
            return _bench_symmetric(cryptolab_core, "aes", "ECB", "encrypt")
        if normalized == "aes_gcm":
            return _bench_symmetric(cryptolab_core, "aes", "GCM", "gcm_encrypt")
        if normalized in {"sm4", "sm4_ecb"}:
            return _bench_symmetric(cryptolab_core, "sm4", "ECB", "encrypt")
        if normalized in {"rc6", "rc6_ecb"}:
            return _bench_symmetric(cryptolab_core, "rc6", "ECB", "encrypt")

        if normalized in {"sha1", "sha256", "sha512", "sha3_256", "ripemd160"}:
            return _bench_hash(cryptolab_core, normalized)

        if normalized in {"hmac", "hmac_sha256"}:
            return _bench_hmac(cryptolab_core)
        if normalized == "pbkdf2":
            return _bench_pbkdf2(cryptolab_core)

        if normalized == "rsa_keygen":
            return _bench_rsa_keygen(cryptolab_core)
        if normalized in {"rsa_encrypt", "rsa_enc"}:
            return _bench_rsa_encrypt(cryptolab_core)
        if normalized in {"rsa_decrypt", "rsa_dec"}:
            return _bench_rsa_decrypt(cryptolab_core)
        if normalized == "rsa_sign":
            return _bench_rsa_sign(cryptolab_core)
        if normalized == "rsa_verify":
            return _bench_rsa_verify(cryptolab_core)

        if normalized in {"ecc_keygen", "ecdsa_keygen"}:
            return _bench_ecc_keygen(cryptolab_core)
        if normalized == "ecdsa_sign":
            return _bench_ecdsa_sign(cryptolab_core)
        if normalized == "ecdsa_verify":
            return _bench_ecdsa_verify(cryptolab_core)

        raise CryptoAPIException(StatusCode.ALGORITHM_UNSUPPORTED)
    except CryptoAPIException:
        raise
    except Exception as exc:
        raise CryptoAPIException(StatusCode.CRYPTO_LIB_ERROR, "benchmark_failed") from exc


def _normalize(algo: str) -> str:
    return algo.strip().lower().replace("-", "_")


def _bench_symmetric(
    cryptolab_core: object,
    algorithm: str,
    mode: str,
    operation: str,
) -> BenchmarkResult:
    key = secrets.token_bytes(16)
    iv = secrets.token_bytes(12 if mode == "GCM" else 16)
    aad = b"cryptolab-benchmark"
    encrypt = getattr(cryptolab_core, f"{algorithm}_encrypt")

    def run() -> bytes:
        if mode == "GCM":
            return bytes(encrypt(THROUGHPUT_PAYLOAD, key, mode, iv, aad, "none"))
        return bytes(encrypt(THROUGHPUT_PAYLOAD, key, mode, None, None, "none"))

    return _measure_adaptive(
        algorithm=algorithm,
        operation=operation,
        data_size_bytes=len(THROUGHPUT_PAYLOAD),
        warmup_iterations=THROUGHPUT_WARMUP,
        min_iterations=THROUGHPUT_MIN_ITERATIONS,
        target_ns=THROUGHPUT_TARGET_NS,
        fn=run,
        report_throughput=True,
    )


def _bench_hash(cryptolab_core: object, algorithm: str) -> BenchmarkResult:
    functions: dict[str, Operation] = {
        "sha1": lambda: cryptolab_core.sha1_digest(THROUGHPUT_PAYLOAD),
        "sha256": lambda: cryptolab_core.sha256_digest(THROUGHPUT_PAYLOAD),
        "sha512": lambda: cryptolab_core.sha512_digest(THROUGHPUT_PAYLOAD),
        "sha3_256": lambda: cryptolab_core.sha3_256_digest(THROUGHPUT_PAYLOAD),
        "ripemd160": lambda: cryptolab_core.ripemd160_digest(THROUGHPUT_PAYLOAD),
    }
    return _measure_adaptive(
        algorithm=algorithm,
        operation="digest",
        data_size_bytes=len(THROUGHPUT_PAYLOAD),
        warmup_iterations=THROUGHPUT_WARMUP,
        min_iterations=THROUGHPUT_MIN_ITERATIONS,
        target_ns=THROUGHPUT_TARGET_NS,
        fn=functions[algorithm],
        report_throughput=True,
    )


def _bench_hmac(cryptolab_core: object) -> BenchmarkResult:
    key = secrets.token_bytes(32)
    return _measure_adaptive(
        algorithm="hmac",
        operation="hmac_sha256",
        data_size_bytes=len(HMAC_MESSAGE),
        warmup_iterations=HMAC_WARMUP,
        min_iterations=HMAC_MIN_ITERATIONS,
        target_ns=HMAC_TARGET_NS,
        fn=lambda: cryptolab_core.hmac_sha256(key, HMAC_MESSAGE),
        report_throughput=False,
    )


def _bench_pbkdf2(cryptolab_core: object) -> BenchmarkResult:
    return _measure_fixed(
        algorithm="pbkdf2",
        operation=f"derive_{PBKDF2_INNER_ITERATIONS}",
        data_size_bytes=len(PBKDF2_PASSWORD) + len(PBKDF2_SALT),
        warmup_iterations=1,
        iterations=10,
        fn=lambda: cryptolab_core.pbkdf2_hmac_sha256(
            PBKDF2_PASSWORD,
            PBKDF2_SALT,
            PBKDF2_INNER_ITERATIONS,
            32,
        ),
        report_ops=False,
    )


def _bench_rsa_keygen(cryptolab_core: object) -> BenchmarkResult:
    return _measure_fixed(
        algorithm="rsa",
        operation="keygen",
        data_size_bytes=0,
        warmup_iterations=0,
        iterations=10,
        fn=lambda: cryptolab_core.rsa_generate_keypair(1024, 65537),
        report_ops=True,
    )


def _bench_rsa_encrypt(cryptolab_core: object) -> BenchmarkResult:
    n, e, _d, _p, _q, _ciphertext, _signature = _rsa_fixture()
    return _measure_fixed(
        algorithm="rsa",
        operation="encrypt",
        data_size_bytes=len(PUBKEY_MESSAGE),
        warmup_iterations=1,
        iterations=100,
        fn=lambda: cryptolab_core.rsa_encrypt_oaep(PUBKEY_MESSAGE, n, e),
        report_ops=True,
    )


def _bench_rsa_decrypt(cryptolab_core: object) -> BenchmarkResult:
    n, e, d, p, q, ciphertext, _signature = _rsa_fixture()
    return _measure_fixed(
        algorithm="rsa",
        operation="decrypt",
        data_size_bytes=len(PUBKEY_MESSAGE),
        warmup_iterations=1,
        iterations=100,
        fn=lambda: cryptolab_core.rsa_decrypt_oaep(ciphertext, n, d, p, q, e),
        report_ops=True,
    )


def _bench_rsa_sign(cryptolab_core: object) -> BenchmarkResult:
    n, e, d, p, q, _ciphertext, _signature = _rsa_fixture()
    return _measure_fixed(
        algorithm="rsa",
        operation="sign",
        data_size_bytes=len(PUBKEY_MESSAGE),
        warmup_iterations=1,
        iterations=100,
        fn=lambda: cryptolab_core.rsa_sign_pss(PUBKEY_MESSAGE, n, d, p, q, e),
        report_ops=True,
    )


def _bench_rsa_verify(cryptolab_core: object) -> BenchmarkResult:
    n, e, _d, _p, _q, _ciphertext, signature = _rsa_fixture()
    return _measure_fixed(
        algorithm="rsa",
        operation="verify",
        data_size_bytes=len(PUBKEY_MESSAGE),
        warmup_iterations=1,
        iterations=100,
        fn=lambda: cryptolab_core.rsa_verify_pss(PUBKEY_MESSAGE, signature, n, e),
        report_ops=True,
    )


def _bench_ecc_keygen(cryptolab_core: object) -> BenchmarkResult:
    return _measure_fixed(
        algorithm="ecc",
        operation="keygen",
        data_size_bytes=0,
        warmup_iterations=1,
        iterations=10,
        fn=lambda: cryptolab_core.ecc_generate_keypair("secp160r1"),
        report_ops=True,
    )


def _bench_ecdsa_sign(cryptolab_core: object) -> BenchmarkResult:
    d, _qx, _qy, _r, _s = _ecdsa_fixture()
    return _measure_fixed(
        algorithm="ecdsa",
        operation="sign",
        data_size_bytes=len(PUBKEY_MESSAGE),
        warmup_iterations=1,
        iterations=50,
        fn=lambda: cryptolab_core.ecdsa_sign(PUBKEY_MESSAGE, d, "secp160r1"),
        report_ops=True,
    )


def _bench_ecdsa_verify(cryptolab_core: object) -> BenchmarkResult:
    _d, qx, qy, r, s = _ecdsa_fixture()
    return _measure_fixed(
        algorithm="ecdsa",
        operation="verify",
        data_size_bytes=len(PUBKEY_MESSAGE),
        warmup_iterations=1,
        iterations=100,
        fn=lambda: cryptolab_core.ecdsa_verify(PUBKEY_MESSAGE, r, s, qx, qy, "secp160r1"),
        report_ops=True,
    )


def _measure_adaptive(
    *,
    algorithm: str,
    operation: str,
    data_size_bytes: int,
    warmup_iterations: int,
    min_iterations: int,
    target_ns: int,
    fn: Operation,
    report_throughput: bool,
) -> BenchmarkResult:
    for _ in range(warmup_iterations):
        fn()

    iterations = 0
    duration_ns = 0
    batch_size = 1
    while iterations < min_iterations or duration_ns < target_ns:
        start_ns = time.perf_counter_ns()
        for _ in range(batch_size):
            fn()
        duration_ns += time.perf_counter_ns() - start_ns
        iterations += batch_size
        if duration_ns < target_ns:
            batch_size = min(batch_size * 2, 256)

    return _result(
        algorithm=algorithm,
        operation=operation,
        data_size_bytes=data_size_bytes,
        iterations=iterations,
        warmup_iterations=warmup_iterations,
        duration_ns=duration_ns,
        report_throughput=report_throughput,
        report_ops=not report_throughput,
    )


def _measure_fixed(
    *,
    algorithm: str,
    operation: str,
    data_size_bytes: int,
    warmup_iterations: int,
    iterations: int,
    fn: Operation,
    report_ops: bool,
) -> BenchmarkResult:
    for _ in range(warmup_iterations):
        fn()

    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    duration_ns = time.perf_counter_ns() - start_ns

    return _result(
        algorithm=algorithm,
        operation=operation,
        data_size_bytes=data_size_bytes,
        iterations=iterations,
        warmup_iterations=warmup_iterations,
        duration_ns=duration_ns,
        report_throughput=False,
        report_ops=report_ops,
    )


def _result(
    *,
    algorithm: str,
    operation: str,
    data_size_bytes: int,
    iterations: int,
    warmup_iterations: int,
    duration_ns: int,
    report_throughput: bool,
    report_ops: bool,
) -> BenchmarkResult:
    ns_per_op = duration_ns / max(iterations, 1)
    total_ms = duration_ns / 1_000_000
    seconds = max(duration_ns / 1_000_000_000, 1e-12)
    throughput = None
    if report_throughput:
        throughput = (data_size_bytes * iterations / ONE_MIB) / seconds
    ops = (1_000_000_000 / ns_per_op) if report_ops and ns_per_op > 0 else None

    metrics_service.record_nowait(
        algorithm,
        operation,
        data_size_bytes,
        int(ns_per_op),
        sampling_rate=1.0,
    )

    return BenchmarkResult(
        algorithm=algorithm,
        operation=operation,
        data_size_bytes=data_size_bytes,
        iterations=iterations,
        warmup_iterations=warmup_iterations,
        total_ms=total_ms,
        throughput_mb_per_s=throughput,
        ns_per_op=ns_per_op,
        ops_per_sec=ops,
        ms_per_op=ns_per_op / 1_000_000,
    )


@lru_cache(maxsize=1)
def _rsa_fixture() -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
    import cryptolab_core

    n, e, d, p, q = cryptolab_core.rsa_generate_keypair(1024, 65537)
    ciphertext = cryptolab_core.rsa_encrypt_oaep(PUBKEY_MESSAGE, n, e)
    signature = cryptolab_core.rsa_sign_pss(PUBKEY_MESSAGE, n, d, p, q, e)
    return bytes(n), bytes(e), bytes(d), bytes(p), bytes(q), bytes(ciphertext), bytes(signature)


@lru_cache(maxsize=1)
def _ecdsa_fixture() -> tuple[bytes, bytes, bytes, bytes, bytes]:
    import cryptolab_core

    d, qx, qy = cryptolab_core.ecc_generate_keypair("secp160r1")
    r, s = cryptolab_core.ecdsa_sign(PUBKEY_MESSAGE, d, "secp160r1")
    return bytes(d), bytes(qx), bytes(qy), bytes(r), bytes(s)
