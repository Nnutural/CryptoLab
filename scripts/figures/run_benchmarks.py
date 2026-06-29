from __future__ import annotations

import csv
import os
import statistics
import sys
import time
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "docs" / "report_assets" / "data"
RAW_CSV = DATA_DIR / "fig4_benchmark_raw.csv"
SUMMARY_CSV = DATA_DIR / "fig4_benchmark_summary.csv"

sys.path.insert(0, str(ROOT / "api_server"))

PUBKEY_MESSAGE = bytes(range(32))


ALGOS = [
    ("symmetric", "AES ECB", "aes_ecb", 5),
    ("symmetric", "AES GCM", "aes_gcm", 5),
    ("symmetric", "SM4 ECB", "sm4", 5),
    ("symmetric", "RC6 ECB", "rc6", 5),
    ("hash", "SHA1", "sha1", 5),
    ("hash", "SHA256", "sha256", 5),
    ("hash", "SHA512", "sha512", 5),
    ("hash", "SHA3-256", "sha3_256", 5),
    ("hash", "RIPEMD160", "ripemd160", 5),
    ("kdf_hmac", "HMAC-SHA256", "hmac_sha256", 5),
    ("kdf_hmac", "PBKDF2-HMAC-SHA256", "pbkdf2", 5),
    ("public_key", "RSA encrypt", "rsa_encrypt", 5),
    ("public_key", "RSA decrypt", "rsa_decrypt", 5),
    ("public_key", "RSA sign", "rsa_sign", 5),
    ("public_key", "RSA verify", "rsa_verify", 5),
    ("public_key", "ECDSA sign", "ecdsa_sign", 5),
    ("public_key", "ECDSA verify", "ecdsa_verify", 5),
]


def to_dict(result: object) -> dict[str, object]:
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    raise TypeError(f"Unsupported benchmark result type: {type(result)!r}")


@lru_cache(maxsize=1)
def rsa_fixture() -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
    import cryptolab_core

    n, e, d, p, q = cryptolab_core.rsa_generate_keypair(1024, 65537)
    ciphertext = cryptolab_core.rsa_encrypt_oaep(PUBKEY_MESSAGE, n, e)
    signature = cryptolab_core.rsa_sign_pss(PUBKEY_MESSAGE, n, d, p, q)
    return bytes(n), bytes(e), bytes(d), bytes(p), bytes(q), bytes(ciphertext), bytes(signature)


@lru_cache(maxsize=1)
def ecdsa_fixture() -> tuple[bytes, bytes, bytes, bytes, bytes]:
    import cryptolab_core

    d, qx, qy = cryptolab_core.ecc_generate_keypair("secp160r1")
    r, s = cryptolab_core.ecdsa_sign(PUBKEY_MESSAGE, d, "secp160r1")
    return bytes(d), bytes(qx), bytes(qy), bytes(r), bytes(s)


def measure_fixed(
    *,
    algorithm: str,
    operation: str,
    endpoint_algo: str,
    data_size_bytes: int,
    warmup_iterations: int,
    iterations: int,
    fn: object,
) -> dict[str, object]:
    for _ in range(warmup_iterations):
        fn()
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    duration_ns = time.perf_counter_ns() - start_ns
    ns_per_op = duration_ns / max(iterations, 1)
    return {
        "algorithm": algorithm,
        "operation": operation,
        "data_size_bytes": data_size_bytes,
        "iterations": iterations,
        "warmup_iterations": warmup_iterations,
        "total_ms": duration_ns / 1_000_000,
        "ns_per_op": ns_per_op,
        "ms_per_op": ns_per_op / 1_000_000,
        "throughput_mb_per_s": None,
        "ops_per_sec": 1_000_000_000 / ns_per_op if ns_per_op > 0 else None,
        "note": f"direct cryptolab_core call for {endpoint_algo}",
    }


def measure_public_key(endpoint_algo: str) -> dict[str, object]:
    import cryptolab_core

    if endpoint_algo == "rsa_encrypt":
        n, e, _d, _p, _q, _ciphertext, _signature = rsa_fixture()
        return measure_fixed(
            algorithm="rsa",
            operation="encrypt",
            endpoint_algo=endpoint_algo,
            data_size_bytes=len(PUBKEY_MESSAGE),
            warmup_iterations=1,
            iterations=100,
            fn=lambda: cryptolab_core.rsa_encrypt_oaep(PUBKEY_MESSAGE, n, e),
        )
    if endpoint_algo == "rsa_decrypt":
        n, _e, d, p, q, ciphertext, _signature = rsa_fixture()
        return measure_fixed(
            algorithm="rsa",
            operation="decrypt",
            endpoint_algo=endpoint_algo,
            data_size_bytes=len(PUBKEY_MESSAGE),
            warmup_iterations=1,
            iterations=100,
            fn=lambda: cryptolab_core.rsa_decrypt_oaep(ciphertext, n, d, p, q),
        )
    if endpoint_algo == "rsa_sign":
        n, _e, d, p, q, _ciphertext, _signature = rsa_fixture()
        return measure_fixed(
            algorithm="rsa",
            operation="sign",
            endpoint_algo=endpoint_algo,
            data_size_bytes=len(PUBKEY_MESSAGE),
            warmup_iterations=1,
            iterations=100,
            fn=lambda: cryptolab_core.rsa_sign_pss(PUBKEY_MESSAGE, n, d, p, q),
        )
    if endpoint_algo == "rsa_verify":
        n, e, _d, _p, _q, _ciphertext, signature = rsa_fixture()
        return measure_fixed(
            algorithm="rsa",
            operation="verify",
            endpoint_algo=endpoint_algo,
            data_size_bytes=len(PUBKEY_MESSAGE),
            warmup_iterations=1,
            iterations=100,
            fn=lambda: cryptolab_core.rsa_verify_pss(PUBKEY_MESSAGE, signature, n, e),
        )
    if endpoint_algo == "ecdsa_sign":
        d, _qx, _qy, _r, _s = ecdsa_fixture()
        return measure_fixed(
            algorithm="ecdsa",
            operation="sign",
            endpoint_algo=endpoint_algo,
            data_size_bytes=len(PUBKEY_MESSAGE),
            warmup_iterations=1,
            iterations=50,
            fn=lambda: cryptolab_core.ecdsa_sign(PUBKEY_MESSAGE, d, "secp160r1"),
        )
    if endpoint_algo == "ecdsa_verify":
        _d, qx, qy, r, s = ecdsa_fixture()
        return measure_fixed(
            algorithm="ecdsa",
            operation="verify",
            endpoint_algo=endpoint_algo,
            data_size_bytes=len(PUBKEY_MESSAGE),
            warmup_iterations=1,
            iterations=100,
            fn=lambda: cryptolab_core.ecdsa_verify(PUBKEY_MESSAGE, r, s, qx, qy, "secp160r1"),
        )
    raise ValueError(f"unsupported public-key benchmark: {endpoint_algo}")


def main() -> None:
    os.environ.setdefault("METRICS_SAMPLING_RATE", "0")
    from app.services import benchmark_service

    benchmark_service.metrics_service.record_nowait = lambda *args, **kwargs: None
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_rows: list[dict[str, object]] = []
    for family, label, endpoint_algo, repeats in ALGOS:
        for repeat in range(1, repeats + 1):
            started = datetime.now(timezone.utc).isoformat()
            wall_start_ns = time.perf_counter_ns()
            if family == "public_key":
                result = measure_public_key(endpoint_algo)
            else:
                result = to_dict(benchmark_service.measure(endpoint_algo))
                result["note"] = "real benchmark_service.measure call"
            wall_elapsed_ms = (time.perf_counter_ns() - wall_start_ns) / 1_000_000
            raw_rows.append(
                {
                    "timestamp_utc": started,
                    "family": family,
                    "label": label,
                    "requested_algo": endpoint_algo,
                    "repeat": repeat,
                    "service_algorithm": result["algorithm"],
                    "service_operation": result["operation"],
                    "data_size_bytes": result["data_size_bytes"],
                    "iterations": result["iterations"],
                    "warmup_iterations": result["warmup_iterations"],
                    "total_ms": result["total_ms"],
                    "ns_per_op": result["ns_per_op"],
                    "ms_per_op": result["ms_per_op"],
                    "throughput_mb_per_s": result["throughput_mb_per_s"],
                    "ops_per_sec": result["ops_per_sec"],
                    "wall_elapsed_ms": wall_elapsed_ms,
                    "note": result["note"],
                }
            )
            print(f"{label} repeat {repeat}/{repeats}: {result['ms_per_op']:.4f} ms/op")

    with RAW_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
        writer.writeheader()
        writer.writerows(raw_rows)

    summary_rows: list[dict[str, object]] = []
    for family, label, endpoint_algo, _repeats in ALGOS:
        rows = [r for r in raw_rows if r["label"] == label]
        metric_name = "throughput_mb_per_s" if family in {"symmetric", "hash"} else "ms_per_op"
        values = [float(r[metric_name]) for r in rows if r[metric_name] not in {None, ""}]
        summary_rows.append(
            {
                "family": family,
                "label": label,
                "requested_algo": endpoint_algo,
                "metric": metric_name,
                "n": len(values),
                "mean": statistics.fmean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "data_size_bytes": rows[0]["data_size_bytes"],
                "service_operation": rows[0]["service_operation"],
                "note": "summary from fig4_benchmark_raw.csv",
            }
        )

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Wrote {RAW_CSV}")
    print(f"Wrote {SUMMARY_CSV}")


if __name__ == "__main__":
    main()
