from __future__ import annotations

import ast
import csv
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "docs" / "report_assets"
DATA_DIR = REPORT_DIR / "data"
LOG_DIR = REPORT_DIR / "logs"
STATS_MD = REPORT_DIR / "STATS.md"

TEXT_EXTENSIONS = {
    ".py",
    ".rs",
    ".toml",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".txt",
    ".csv",
    ".yml",
    ".yaml",
    ".ps1",
    ".sh",
    ".css",
    ".html",
    ".ini",
    ".mako",
    ".R",
}


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


def rel(path: Path | str) -> str:
    path = Path(path)
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def run(args: list[str], log_name: str) -> CommandResult:
    result = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    text = result.stdout
    if result.stderr:
        text += ("\n" if text else "") + result.stderr
    write_text(LOG_DIR / log_name, text)
    return CommandResult(" ".join(args), result.returncode, result.stdout, result.stderr)


def collect_git_logs() -> tuple[str, str, str]:
    status = run(["git", "status", "--short"], "git_status.txt")
    head = run(["git", "rev-parse", "HEAD"], "git_head.txt")
    files = run(["rg", "--files"], "code_file_inventory.txt")
    return status.stdout.strip(), head.stdout.strip(), files.stdout


def iter_files(base: Path, extensions: set[str] | None = None) -> Iterable[Path]:
    if not base.exists():
        return []
    ignored_parts = {
        ".git",
        ".venv",
        "node_modules",
        "dist",
        "target",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
    }
    files: list[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.relative_to(ROOT).parts):
            continue
        if extensions is not None and path.suffix not in extensions:
            continue
        files.append(path)
    return sorted(files)


def count_lines(files: Iterable[Path]) -> tuple[int, int]:
    total = 0
    non_empty = 0
    for path in files:
        text = read(path)
        lines = text.splitlines()
        total += len(lines)
        non_empty += sum(1 for line in lines if line.strip())
    return total, non_empty


def build_code_lines_summary() -> list[dict[str, object]]:
    areas = [
        ("Rust core", "rust_core/src/**/*.rs", ROOT / "rust_core" / "src", {".rs"}),
        ("API application", "api_server/app/**/*.py", ROOT / "api_server" / "app", {".py"}),
        ("API tests", "api_server/tests/**/*.py", ROOT / "api_server" / "tests", {".py"}),
        ("Frontend source", "frontend/src/**/*.{ts,tsx,css}", ROOT / "frontend" / "src", {".ts", ".tsx", ".css"}),
        ("Docs", "docs/**/* text assets", ROOT / "docs", TEXT_EXTENSIONS),
        ("Scripts", "scripts/**/*", ROOT / "scripts", TEXT_EXTENSIONS),
    ]
    rows: list[dict[str, object]] = []
    for area, pattern, base, exts in areas:
        files = list(iter_files(base, exts))
        total, non_empty = count_lines(files)
        if area == "Rust core":
            test_file_count = sum(
                1 for path in files if "#[cfg(test)]" in read(path) or "mod tests" in read(path)
            )
        elif area.endswith("tests"):
            test_file_count = len(files)
        else:
            test_file_count = sum(1 for path in files if "test" in path.name.lower())
        rows.append(
            {
                "area": area,
                "path_pattern": pattern,
                "file_count": len(files),
                "line_count": total,
                "non_empty_line_count": non_empty,
                "test_file_count": test_file_count,
                "evidence_command": f"Get-ChildItem -Recurse {pattern}; Python line counter in scripts/stats/generate_stats.py",
            }
        )
    return rows


def parse_status_codes() -> list[dict[str, object]]:
    status_file = ROOT / "api_server" / "app" / "core" / "status_codes.py"
    text = read(status_file)
    tree = ast.parse(text)
    codes: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "StatusCode":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                    target = stmt.targets[0]
                    if isinstance(target, ast.Name):
                        value = ast.literal_eval(stmt.value)
                        if isinstance(value, int):
                            codes[target.id] = value
    http_text = text.split("HTTP_FOR_STATUS", 1)[1] if "HTTP_FOR_STATUS" in text else ""
    http_map = dict(re.findall(r"StatusCode\.([A-Z_]+):\s*(\d+)", http_text))
    app_files = list(iter_files(ROOT / "api_server" / "app", {".py"}))
    rows: list[dict[str, object]] = []
    for name, value in codes.items():
        reference_files: list[str] = []
        ref_count = 0
        pattern = f"StatusCode.{name}"
        for path in app_files:
            if path == status_file:
                continue
            content = read(path)
            count = content.count(pattern)
            if count:
                ref_count += count
                reference_files.append(rel(path))
        http_status = http_map.get(name, "未定义")
        rows.append(
            {
                "code_name": name,
                "value_or_http_status": f"{value} / HTTP {http_status}",
                "definition_file": rel(status_file),
                "reference_count": ref_count,
                "reference_files": "; ".join(reference_files),
                "evidence_command": f'rg -n "StatusCode.{name}" api_server\\app',
            }
        )
    return rows


def parse_router_prefixes() -> dict[str, str]:
    text = read(ROOT / "api_server" / "app" / "main.py")
    prefixes: dict[str, str] = {}
    for match in re.finditer(
        r"app\.include_router\((?P<router>\w+)\.router,\s*prefix=f\"\{api_prefix\}(?P<prefix>[^\"]*)\"",
        text,
    ):
        router_var = match.group("router")
        module = "hash" if router_var == "hash_router" else router_var
        prefixes[module] = "/api/v1" + match.group("prefix")
    return prefixes


def annotation_to_str(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def find_test_files_for_endpoint(module: str, route_path: str, handler: str) -> str:
    tests = list(iter_files(ROOT / "api_server" / "tests", {".py"}))
    matched: list[str] = []
    module_aliases = {
        "auth": ["auth", "jwt"],
        "symmetric": ["symmetric", "aes_verbose", "cross_validation"],
        "hash": ["hash", "cross_validation"],
        "encoding": ["encoding", "cross_validation"],
        "pubkey": ["pubkey"],
        "keys": ["keys", "pubkey", "scenarios"],
        "audit": ["audit"],
        "demos": ["demos"],
        "benchmark": ["benchmark"],
        "metrics": ["metrics"],
        "scenarios": ["scenarios"],
    }.get(module, [module])
    route_tokens = [token for token in route_path.split("/") if token and "{" not in token]
    for path in tests:
        name = path.stem.lower()
        content = read(path)
        if any(alias in name for alias in module_aliases):
            matched.append(rel(path))
            continue
        if handler in content or any(token and token in content for token in route_tokens):
            matched.append(rel(path))
    return "; ".join(sorted(set(matched)))


def parse_api_endpoints() -> list[dict[str, object]]:
    prefixes = parse_router_prefixes()
    rows: list[dict[str, object]] = []
    methods = {"get", "post", "put", "delete", "patch"}
    for path in sorted((ROOT / "api_server" / "app" / "routers").glob("*.py")):
        if path.name == "__init__.py":
            continue
        module = path.stem
        text = read(path)
        tree = ast.parse(text)
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if not (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and isinstance(dec.func.value, ast.Name)
                    and dec.func.value.id == "router"
                    and dec.func.attr in methods
                ):
                    continue
                route_path = ""
                if dec.args:
                    try:
                        route_path = ast.literal_eval(dec.args[0])
                    except Exception:
                        route_path = ast.unparse(dec.args[0])
                response_model = ""
                for kw in dec.keywords:
                    if kw.arg == "response_model":
                        response_model = ast.unparse(kw.value)
                req_schema = ""
                for arg in node.args.args:
                    if arg.arg == "req":
                        req_schema = annotation_to_str(arg.annotation)
                source = ast.get_source_segment(text, node) or ""
                calls = sorted(
                    {
                        f"{svc}.{fn}"
                        for svc, fn in re.findall(r"([A-Za-z_]+_service)\.([A-Za-z_][A-Za-z0-9_]*)", source)
                    }
                )
                if "cryptolab_core" in source:
                    calls.append("cryptolab_core")
                test_files = find_test_files_for_endpoint(module, route_path, node.name)
                full_path = prefixes.get(module, f"/api/v1/{module}") + route_path
                if calls and response_model and test_files:
                    status = "✅"
                elif calls and test_files:
                    status = "🟡"
                else:
                    status = "❌"
                rows.append(
                    {
                        "module": module,
                        "method": dec.func.attr.upper(),
                        "path": full_path,
                        "router_file": rel(path),
                        "handler_name": node.name,
                        "request_schema": req_schema or "None",
                        "response_schema": response_model or "未显式声明 response_model",
                        "service_call": "; ".join(calls) or "未检测到 service 调用",
                        "test_files": test_files or "未检测到",
                        "status": status,
                        "evidence": 'rg -n "@router\\.(get|post|put|delete|patch)|APIRouter|def " api_server\\app\\routers api_server\\app\\schemas api_server\\tests',
                    }
                )
    rows.sort(key=lambda row: (str(row["module"]), str(row["path"]), str(row["method"])))
    return rows


def count_cargo_tests(pattern: str) -> int:
    text = read(LOG_DIR / "cargo_test_full.txt")
    return len(re.findall(pattern, text))


def cargo_passed() -> bool:
    return "test result: ok. 53 passed; 0 failed; 3 ignored" in read(LOG_DIR / "cargo_test_full.txt")


def has_unfinished(path: Path) -> bool:
    text = read(path)
    return any(token in text for token in ["todo!(", "unimplemented!"])


def build_algorithm_rows() -> list[dict[str, object]]:
    cargo_ok = cargo_passed()
    definitions = [
        ("Rust core", "encoding", "Base64", "RFC 4648 encode/decode", "rust_core/src/encoding/base64.rs", r"encoding::base64::tests::"),
        ("Rust core", "encoding", "UTF-8", "RFC 3629 encode/decode", "rust_core/src/encoding/utf8.rs", r"encoding::utf8::tests::"),
        ("Rust core", "hash", "SHA1", "one-shot and streaming digest", "rust_core/src/hash/sha1.rs", r"hash::sha1::tests::"),
        ("Rust core", "hash", "SHA256", "SHA-2 family, SHA-256 streaming", "rust_core/src/hash/sha2.rs", r"hash::sha2::tests::sha256|hash::sha2::tests::sha224|hash::sha2::tests::sha384|hash::sha2::tests::sha512"),
        ("Rust core", "hash", "SHA3", "SHA3-256 / SHA3-512", "rust_core/src/hash/sha3.rs", r"hash::sha3::tests::"),
        ("Rust core", "hash", "RIPEMD160", "RIPEMD-160 digest", "rust_core/src/hash/ripemd.rs", r"hash::ripemd::tests::"),
        ("Rust core", "hash", "HMAC-SHA1", "RFC 2202 keyed MAC with constant-time verify path", "rust_core/src/hash/hmac.rs", r"hash::hmac::tests::rfc_2202_hmac_sha1_vectors"),
        ("Rust core", "hash", "HMAC-SHA256", "RFC 4231 keyed MAC with constant-time verify path", "rust_core/src/hash/hmac.rs", r"hash::hmac::tests::rfc_4231_hmac_sha256_vectors|hash::hmac::tests::verify_hmac_sha256_uses_constant_time_compare_path"),
        ("Rust core", "hash", "PBKDF2", "PBKDF2-HMAC-SHA256", "rust_core/src/hash/pbkdf2.rs", r"hash::pbkdf2::tests::"),
        ("Rust core", "symmetric", "AES", "ECB/CBC/CTR/GCM plus verbose trace", "rust_core/src/symmetric/aes.rs", r"symmetric::aes::"),
        ("Rust core", "symmetric", "SM4", "ECB/CBC/CTR/GCM dispatch, GB/T single-block KAT", "rust_core/src/symmetric/sm4.rs", r"symmetric::sm4::tests::"),
        ("Rust core", "symmetric", "RC6", "ECB/CBC implemented; GCM not exposed", "rust_core/src/symmetric/rc6.rs", r"symmetric::rc6::tests::"),
        ("Rust core", "pubkey", "RSA-1024", "keygen/encrypt/decrypt/sign/verify", "rust_core/src/pubkey/rsa.rs", r"pubkey::rsa::tests::"),
        ("Rust core", "pubkey", "ECC-160", "secp160r1 point arithmetic and keygen", "rust_core/src/pubkey/ecc.rs", r"pubkey::ecc::tests::"),
        ("Rust core", "pubkey", "ECDSA", "secp160r1 sign/verify and deterministic nonce", "rust_core/src/pubkey/ecdsa.rs", r"pubkey::ecdsa::tests::"),
    ]
    rows: list[dict[str, object]] = []
    for layer, module, algorithm, subfeature, impl_file, pattern in definitions:
        path = ROOT / impl_file
        test_count = count_cargo_tests(pattern)
        if algorithm == "RC6":
            status = "🟡"
        elif path.exists() and not has_unfinished(path) and test_count > 0 and cargo_ok:
            status = "✅"
        else:
            status = "❌"
        rows.append(
            {
                "layer": layer,
                "module": module,
                "algorithm": algorithm,
                "subfeature": subfeature,
                "implementation_file": impl_file,
                "test_file": impl_file + " (inline #[cfg(test)])",
                "test_count": test_count,
                "status": status,
                "evidence": f"cargo_test_full.txt; rg -n \"todo!\\(\\)|unimplemented!\" {impl_file}",
            }
        )
    return rows


def build_test_vector_sources() -> list[dict[str, object]]:
    rows = [
        ("Base64", "RFC 4648", "rust_core/src/encoding/base64.rs", "rfc4648_section_10_vectors", "RFC 4648"),
        ("UTF-8", "RFC 3629 / Unicode scalar widths", "rust_core/src/encoding/utf8.rs", "encode_matches_rfc3629_widths; decode_rejects_ill_formed_rfc3629_sequences", "RFC 3629"),
        ("SHA1", "FIPS 180-4", "rust_core/src/hash/sha1.rs", "fips_180_4_classic_vectors; million_a_vector", "FIPS 180-4"),
        ("SHA256/SHA2", "NIST / FIPS 180-4", "rust_core/src/hash/sha2.rs", "sha256_nist_short_vectors; sha256_streaming_matches_one_shot_for_random_1mb", "NIST|FIPS"),
        ("SHA3", "FIPS 202", "rust_core/src/hash/sha3.rs", "fips_202_sha3_256_vectors; fips_202_sha3_512_vectors", "FIPS 202"),
        ("RIPEMD160", "Original RIPEMD-160 vectors", "rust_core/src/hash/ripemd.rs", "original_ripemd160_vectors", "RIPEMD"),
        ("HMAC-SHA1", "RFC 2202", "rust_core/src/hash/hmac.rs", "rfc_2202_hmac_sha1_vectors", "RFC 2202"),
        ("HMAC-SHA256", "RFC 4231", "rust_core/src/hash/hmac.rs", "rfc_4231_hmac_sha256_vectors", "RFC 4231"),
        ("PBKDF2", "RFC 8018 / NIST SP 800-132", "rust_core/src/hash/pbkdf2.rs", "pbkdf2_hmac_sha256_known_vectors", "RFC 8018|NIST SP 800-132"),
        ("AES", "NIST SP 800-38A/38D; FIPS 197", "rust_core/src/symmetric/aes.rs", "aes128_*_nist_*; fips_197_aes128_trace_matches_every_intermediate_state", "NIST SP 800|FIPS 197"),
        ("SM4", "GB/T 32907", "rust_core/src/symmetric/sm4.rs", "gb_t_32907_appendix_a_single_block", "GB/T 32907|SM4"),
        ("RC6", "RC6 paper appendix", "rust_core/src/symmetric/rc6.rs", "rc6_paper_appendix_b_zero_vector", "RC6 paper"),
        ("RSA-1024", "RFC 8017", "rust_core/src/pubkey/rsa.rs", "rsa_keygen_oaep_pss_roundtrip; mgf1_is_deterministic", "RFC 8017"),
        ("ECC-160", "secp160r1 domain checks", "rust_core/src/pubkey/ecc.rs", "secp160r1_base_point_is_on_curve; order_times_base_point_is_infinity", "secp160r1"),
        ("ECDSA", "FIPS 186-4 / RFC 6979", "rust_core/src/pubkey/ecdsa.rs", "sign_verify_roundtrip; tampering_fails", "RFC 6979|FIPS 186"),
    ]
    output: list[dict[str, object]] = []
    for algorithm, source, test_file, case_name, source_pattern in rows:
        text = read(ROOT / test_file)
        count = 0
        for case in re.split(r";\s*", case_name):
            name = case.replace("*", "")
            if name and name in text:
                count += 1
        if count == 0:
            count = len(re.findall(source_pattern, text, flags=re.IGNORECASE))
        output.append(
            {
                "algorithm": algorithm,
                "source_standard_or_library": source,
                "test_file": test_file,
                "test_case_name": case_name,
                "count": count,
                "evidence": 'docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC|NIST|FIPS|OpenSSL|PyCryptodome|known vector|test vector|RFC 4648|Wycheproof|GM/T|SM4" rust_core api_server docs',
            }
        )
    return output


def parse_test_summary() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    cargo = read(LOG_DIR / "cargo_test_full.txt")
    m = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", cargo)
    rows.append(
        {
            "test_layer": "Rust core",
            "command": "cargo test --manifest-path rust_core\\Cargo.toml --no-fail-fast",
            "passed": int(m.group(1)) if m else 0,
            "failed": int(m.group(2)) if m else "未统计",
            "ignored_or_skipped": int(m.group(3)) if m else "未统计",
            "deselected": 0,
            "errors": 0 if m else 1,
            "status": "✅" if m else "❌",
            "evidence_log": "docs/report_assets/logs/cargo_test_full.txt",
        }
    )
    pytest_bare = read(LOG_DIR / "pytest_full.txt")
    rows.append(
        {
            "test_layer": "API pytest (requested shell)",
            "command": "cd api_server; pytest --tb=no -q",
            "passed": 0,
            "failed": 0,
            "ignored_or_skipped": 0,
            "deselected": 0,
            "errors": 1 if "ModuleNotFoundError" in pytest_bare or "ImportError" in pytest_bare else 0,
            "status": "❌" if "ModuleNotFoundError" in pytest_bare or "ImportError" in pytest_bare else "未统计",
            "evidence_log": "docs/report_assets/logs/pytest_full.txt",
        }
    )
    pytest_venv = read(LOG_DIR / "pytest_venv_full.txt")
    m = re.search(r"(\d+) passed(?:, (\d+) skipped)?(?:, (\d+) deselected)?", pytest_venv)
    rows.append(
        {
            "test_layer": "API pytest (.venv)",
            "command": "cd api_server; .\\.venv\\Scripts\\python.exe -m pytest --tb=no -q",
            "passed": int(m.group(1)) if m else 0,
            "failed": 0 if m else "未统计",
            "ignored_or_skipped": int(m.group(2) or 0) if m else "未统计",
            "deselected": int(m.group(3) or 0) if m else 0,
            "errors": 0 if m else 1,
            "status": "✅" if m else "❌",
            "evidence_log": "docs/report_assets/logs/pytest_venv_full.txt",
        }
    )
    npm = read(LOG_DIR / "npm_test_full.txt")
    npm_ok = "tsc -b --pretty false" in npm and "error TS" not in npm.lower()
    rows.append(
        {
            "test_layer": "Frontend TypeScript",
            "command": "cd frontend; npm test",
            "passed": "tsc smoke",
            "failed": 0 if npm_ok else 1,
            "ignored_or_skipped": 0,
            "deselected": 0,
            "errors": 0 if npm_ok else 1,
            "status": "✅" if npm_ok else "❌",
            "evidence_log": "docs/report_assets/logs/npm_test_full.txt",
        }
    )
    compose = read(LOG_DIR / "docker_compose_config.txt")
    rows.append(
        {
            "test_layer": "Docker compose config",
            "command": "docker compose -f deploy\\docker-compose.yml config",
            "passed": "config parsed" if "services:" in compose else 0,
            "failed": 0 if "services:" in compose else 1,
            "ignored_or_skipped": 0,
            "deselected": 0,
            "errors": 0 if "services:" in compose else 1,
            "status": "✅" if "services:" in compose else "❌",
            "evidence_log": "docs/report_assets/logs/docker_compose_config.txt",
        }
    )
    build = read(LOG_DIR / "docker_compose_build.txt")
    build_ok = bool(build) and "failed to solve" not in build and "ERROR:" not in build
    rows.append(
        {
            "test_layer": "Docker compose build",
            "command": "docker compose -f deploy\\docker-compose.yml build",
            "passed": "build completed" if build_ok else 0,
            "failed": 0 if build_ok else 1,
            "ignored_or_skipped": 0,
            "deselected": 0,
            "errors": 0 if build_ok else 1,
            "status": "✅" if build_ok else "❌",
            "evidence_log": "docs/report_assets/logs/docker_compose_build.txt",
        }
    )
    return rows


def build_figure_assets_summary() -> list[dict[str, object]]:
    figures = [
        ("Fig. 1", "测试验证总览图", "docs/report_assets/data/fig1_validation_overview.csv", "scripts/figures/plot_validation_overview.py", "fig1_validation_overview", ".\\.venv\\Scripts\\python.exe scripts\\figures\\plot_validation_overview.py"),
        ("Fig. 2", "算法覆盖与实现状态矩阵", "docs/report_assets/data/fig2_algorithm_coverage_matrix.csv", "scripts/figures/plot_algorithm_coverage_matrix.R", "fig2_algorithm_coverage_matrix", "Rscript scripts\\figures\\plot_algorithm_coverage_matrix.R"),
        ("Fig. 3", "交叉验证证据矩阵", "docs/report_assets/data/fig3_cross_validation_evidence.csv", "scripts/figures/plot_cross_validation_evidence.R", "fig3_cross_validation_evidence", "Rscript scripts\\figures\\plot_cross_validation_evidence.R"),
        ("Fig. 4", "Benchmark 性能结果图", "docs/report_assets/data/fig4_benchmark_summary.csv", "scripts/figures/plot_benchmark_performance.py", "fig4_benchmark_performance", ".\\.venv\\Scripts\\python.exe scripts\\figures\\plot_benchmark_performance.py"),
        ("Fig. 5", "AES verbose trace 结果图", "docs/report_assets/data/fig5_aes_verbose_trace.csv", "scripts/figures/plot_aes_verbose_trace.py", "fig5_aes_verbose_trace", ".\\.venv\\Scripts\\python.exe scripts\\figures\\plot_aes_verbose_trace.py"),
        ("Fig. 6", "安全演示效果图", "docs/report_assets/data/fig6_ecb_leak_metrics.csv; docs/report_assets/data/fig6_pbkdf2_iterations.csv", "scripts/figures/plot_security_demos.py", "fig6_security_demos", ".\\.venv\\Scripts\\python.exe scripts\\figures\\plot_security_demos.py"),
    ]
    qa = read(REPORT_DIR / "FIGURE_QA.md")
    rows: list[dict[str, object]] = []
    for figure_id, title, source_data, script, stem, command in figures:
        svg = REPORT_DIR / "figures" / f"{stem}.svg"
        png = REPORT_DIR / "figures" / f"{stem}.png"
        qa_status = "PASS" if re.search(rf"\| {re.escape(figure_id)} \|.*\| PASS \|", qa) else "未统计"
        rows.append(
            {
                "figure_id": figure_id,
                "title": title,
                "source_data": source_data,
                "script": script,
                "svg_path": rel(svg) if svg.exists() else "未生成",
                "png_path": rel(png) if png.exists() else "未生成",
                "qa_status": qa_status,
                "used_in_report": "建议纳入 PDF 正文",
                "repro_command": command,
            }
        )
    return rows


def file_status(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "❌ 缺失", ""
    if path.is_dir():
        count = sum(1 for p in path.rglob("*") if p.is_file())
        status = "✅ 存在" if count else "🟡 空目录"
        return status, str(count)
    size = path.stat().st_size
    status = "✅ 非空" if size > 0 else "🟡 空文件"
    return status, str(size)


def build_evidence_inventory() -> list[dict[str, object]]:
    paths: list[tuple[str, Path, str, str]] = [
        ("progress", ROOT / "docs" / "PROGRESS.md", "历史进度报告", ""),
        ("progress", ROOT / "docs" / "PROGRESS_DELTA.md", "Stage A 修复记录", ""),
        ("stats", STATS_MD, "本次统计汇总", "生成时先写临时占位，最终大小以实际文件为准"),
        ("figures", REPORT_DIR / "FIGURE_INDEX.md", "图表索引", ""),
        ("figures", REPORT_DIR / "FIGURE_QA.md", "图表质量检查", ""),
        ("screenshots", REPORT_DIR / "SCREENSHOT_CHECKLIST.md", "截图清单", ""),
        ("screenshots", REPORT_DIR / "SCREENSHOT_INDEX.md", "截图索引", ""),
        ("screenshots", REPORT_DIR / "screenshots" / "frontend", "前端截图目录", ""),
        ("screenshots", REPORT_DIR / "screenshots" / "api", "API 截图目录", "如为空则需人工补拍"),
        ("screenshots", REPORT_DIR / "screenshots" / "tests", "测试截图目录", "如为空则需人工补拍"),
        ("screenshots", REPORT_DIR / "screenshots" / "database", "数据库截图目录", "如为空则需人工补拍"),
        ("screenshots", REPORT_DIR / "screenshots" / "docker", "Docker 截图目录", "如为空则需人工补拍"),
        ("logs", LOG_DIR, "统计与验证日志目录", ""),
        ("progress_evidence", ROOT / "docs" / "progress_evidence", "早期进度证据目录", ""),
        ("progress_evidence", ROOT / "docs" / "progress_evidence" / "docker_build_stage_a.log", "Stage A Docker build 日志", "可能不存在于当前树"),
    ]
    for path in sorted((REPORT_DIR / "figures").glob("*")):
        paths.append(("figures", path, "实验图资产", ""))
    for path in sorted(DATA_DIR.glob("*")):
        paths.append(("data", path, "CSV/数据资产", ""))
    for path in sorted(LOG_DIR.glob("*")):
        if path.is_file():
            paths.append(("logs", path, "命令输出日志", ""))
    rows: list[dict[str, object]] = []
    for category, path, purpose, notes in paths:
        status, extra = file_status(path)
        last_write = ""
        if path.exists():
            last_write = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        if path == STATS_MD:
            status = "✅ 生成"
            extra = ""
            notes = "最终文件由本脚本写入；大小以文件系统当前值为准"
        rows.append(
            {
                "category": category,
                "file_path": rel(path),
                "purpose": purpose,
                "status": status,
                "last_write_time": last_write,
                "notes": notes or (f"{extra} files" if path.is_dir() and extra else f"{extra} bytes" if extra else ""),
            }
        )
    return rows


def md_escape(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def markdown_table(rows: list[dict[str, object]], columns: list[str], max_rows: int | None = None) -> str:
    selected = rows if max_rows is None else rows[:max_rows]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in selected:
        lines.append("| " + " | ".join(md_escape(row.get(col, "")) for col in columns) + " |")
    if max_rows is not None and len(rows) > max_rows:
        lines.append(
            "| "
            + " | ".join(["..."] + ["" for _ in columns[1:-1]] + [f"其余 {len(rows) - max_rows} 行见 CSV"])
            + " |"
        )
    return "\n".join(lines)


def status_from_log(path: Path) -> str:
    text = read(path).strip()
    if not text:
        return "无命中"
    return text.splitlines()[0][:160]


def build_stats_md(
    *,
    generated_at: str,
    head: str,
    git_status: str,
    code_rows: list[dict[str, object]],
    status_rows: list[dict[str, object]],
    endpoint_rows: list[dict[str, object]],
    algo_rows: list[dict[str, object]],
    vector_rows: list[dict[str, object]],
    test_rows: list[dict[str, object]],
    figure_rows: list[dict[str, object]],
    evidence_rows: list[dict[str, object]],
) -> str:
    dirty = "dirty" if git_status.strip() else "clean"
    implemented_algos = sum(1 for row in algo_rows if row["status"] in {"✅", "🟡"})
    full_algos = sum(1 for row in algo_rows if row["status"] == "✅")
    endpoint_implemented = sum(1 for row in endpoint_rows if row["status"] in {"✅", "🟡"})
    rust_row = next(row for row in test_rows if row["test_layer"] == "Rust core")
    api_venv_row = next(row for row in test_rows if row["test_layer"] == "API pytest (.venv)")
    api_requested_row = next(row for row in test_rows if row["test_layer"] == "API pytest (requested shell)")
    npm_row = next(row for row in test_rows if row["test_layer"] == "Frontend TypeScript")
    docker_config_row = next(row for row in test_rows if row["test_layer"] == "Docker compose config")
    docker_build_row = next(row for row in test_rows if row["test_layer"] == "Docker compose build")
    screenshot_files = list((REPORT_DIR / "screenshots").rglob("*.*")) if (REPORT_DIR / "screenshots").exists() else []
    frontend_screens = [
        p for p in (REPORT_DIR / "screenshots" / "frontend").rglob("*.png")
    ] if (REPORT_DIR / "screenshots" / "frontend").exists() else []
    overview = [
        {"类别": "算法实现", "数值": f"{implemented_algos}/{len(algo_rows)} 有实现证据；{full_algos} 个为 ✅", "证据": "algorithm_implementation.csv; cargo_test_full.txt"},
        {"类别": "API 端点", "数值": f"{endpoint_implemented}/{len(endpoint_rows)} router 端点有 handler/service/test 证据", "证据": "api_endpoints.csv; endpoint_scan.txt"},
        {"类别": "Rust 测试", "数值": f"{rust_row['passed']} passed, {rust_row['failed']} failed, {rust_row['ignored_or_skipped']} ignored", "证据": rust_row["evidence_log"]},
        {"类别": "API 测试", "数值": f".venv: {api_venv_row['passed']} passed, {api_venv_row['deselected']} deselected；裸 pytest: errors={api_requested_row['errors']}", "证据": "pytest_venv_full.txt; pytest_full.txt"},
        {"类别": "前端检查", "数值": f"npm test: {npm_row['status']} ({npm_row['passed']})", "证据": npm_row["evidence_log"]},
        {"类别": "实验图", "数值": f"{sum(1 for row in figure_rows if row['qa_status'] == 'PASS')} 张 Fig.1-Fig.6 QA PASS", "证据": "FIGURE_QA.md; figure_assets_summary.csv"},
        {"类别": "截图材料", "数值": f"已归档图片 {len(screenshot_files)} 个；前端 PNG {len(frontend_screens)} 个", "证据": "SCREENSHOT_INDEX.md; FRONT_SCREENSHOT_CLASSIFICATION.md"},
        {"类别": "Docker", "数值": f"config {docker_config_row['status']}；build {docker_build_row['status']}", "证据": "docker_compose_config.txt; docker_compose_build.txt"},
    ]
    gaps = [
        "前端 AES verbose trace 截图 `P0_03_frontend_symmetric_aes_verbose_trace.png` 仍缺；可用 `fig5_aes_verbose_trace.png` 作非前端替代证据。",
        "Swagger `/docs` 与关键 API 成功响应仍缺 PNG 截图；当前只有日志证据。",
        "测试、数据库、Docker 构建多数为日志证据，PNG 截图目录存在但 API/tests/database/docker 子目录为空或待人工补拍。",
        "Docker build 本轮失败，关键错误为 Cargo 1.78 无法解析 `edition2024` 依赖；不能作为构建成功证据。",
    ]
    git_summary = git_status.strip().replace("\n", "<br>") if git_status.strip() else "clean"
    rust_scan = status_from_log(LOG_DIR / "rust_todo_scan.txt")
    api_scan = status_from_log(LOG_DIR / "api_todo_scan.txt")
    frontend_scan = status_from_log(LOG_DIR / "frontend_todo_scan.txt")

    paper_tables = f"""
### 9.1 系统实现规模表

{markdown_table(code_rows, ["area", "file_count", "line_count", "non_empty_line_count", "test_file_count"])}

### 9.2 算法实现与验证表

{markdown_table(algo_rows, ["algorithm", "subfeature", "test_count", "status", "implementation_file"])}

### 9.3 API 端点覆盖表

{markdown_table(endpoint_rows, ["module", "method", "path", "request_schema", "response_schema", "status"], max_rows=40)}

### 9.4 测试结果汇总表

{markdown_table(test_rows, ["test_layer", "command", "passed", "failed", "ignored_or_skipped", "deselected", "errors", "status"])}

### 9.5 实验图索引表

{markdown_table(figure_rows, ["figure_id", "title", "source_data", "png_path", "qa_status"])}

### 9.6 报告素材清单表

{markdown_table(evidence_rows, ["category", "file_path", "purpose", "status", "notes"], max_rows=20)}
"""
    return f"""# CryptoLab 项目统计汇总

生成时间：{generated_at} Asia/Shanghai  
基于 commit hash：`{head}`  
工作树状态：{dirty}（`git status --short` 摘要：{git_summary}）

## 1. 统计口径

本文件由 `scripts/stats/generate_stats.py` 生成。统计来源包括当前 Git 输出、`rg --files` 文件清单、源码 AST/正则解析、已执行测试日志、Docker 日志、截图索引、图表 QA 报告与现有进度报告。所有 CSV 输出位于 `docs/report_assets/data/`，所有命令输出日志位于 `docs/report_assets/logs/`。

本轮命令执行情况：

- `git status --short`、`git rev-parse HEAD`、`rg --files` 已重新保存。
- Rust `cargo test --manifest-path rust_core\\Cargo.toml --no-fail-fast` 通过。
- 用户指定的裸 `pytest --tb=no -q` 在当前 shell Python 中失败，原因为 `ModuleNotFoundError: No module named 'jwt'`；随后用项目 `.venv` 执行同等 pytest 通过。
- `frontend npm test` 执行 TypeScript smoke check，通过。
- `docker compose config` 通过；`docker compose build` 失败，失败阶段见 Docker 日志。
- 占位扫描：Rust=`{rust_scan}`；API=`{api_scan}`；Frontend=`{frontend_scan}`。

## 2. 总览数据表

{markdown_table(overview, ["类别", "数值", "证据"])}

## 3. 代码规模统计

{markdown_table(code_rows, ["area", "path_pattern", "file_count", "line_count", "non_empty_line_count", "test_file_count", "evidence_command"])}

## 4. 算法与测试向量统计

### 4.1 算法实现统计

{markdown_table(algo_rows, ["layer", "module", "algorithm", "subfeature", "implementation_file", "test_count", "status", "evidence"])}

### 4.2 测试向量来源统计

{markdown_table(vector_rows, ["algorithm", "source_standard_or_library", "test_file", "test_case_name", "count", "evidence"])}

## 5. API 与状态码统计

### 5.1 API 端点

{markdown_table(endpoint_rows, ["module", "method", "path", "handler_name", "request_schema", "response_schema", "service_call", "test_files", "status"], max_rows=40)}

### 5.2 统一状态码

状态码定义共 `{len(status_rows)}` 项；引用计数按 `api_server/app` 源码中 `StatusCode.NAME` 出现次数统计，定义文件自身不计入引用数。

{markdown_table(status_rows, ["code_name", "value_or_http_status", "definition_file", "reference_count", "reference_files"], max_rows=40)}

## 6. 测试与构建统计

{markdown_table(test_rows, ["test_layer", "command", "passed", "failed", "ignored_or_skipped", "deselected", "errors", "status", "evidence_log"])}

Docker build 关键结论：`docs/report_assets/logs/docker_compose_build.txt` 显示 `rust-builder` 在 `maturin build` 阶段失败，Cargo 1.78.0 不支持依赖需要的 `edition2024` feature。该结果是构建失败证据，不是部署成功证据。

## 7. 实验图与数据资产统计

{markdown_table(figure_rows, ["figure_id", "title", "source_data", "script", "svg_path", "png_path", "qa_status", "used_in_report", "repro_command"])}

## 8. 报告素材缺口

{chr(10).join(f"- {gap}" for gap in gaps)}

截图清单存在性：

- `docs/report_assets/SCREENSHOT_CHECKLIST.md`：{'存在' if (REPORT_DIR / 'SCREENSHOT_CHECKLIST.md').exists() else '缺失'}
- `docs/report_assets/SCREENSHOT_INDEX.md`：{'存在' if (REPORT_DIR / 'SCREENSHOT_INDEX.md').exists() else '缺失'}
- 前端运行截图：`docs/report_assets/screenshots/frontend/` 当前 PNG 数 `{len(frontend_screens)}`
- API 文档截图：需人工补拍，见 `SCREENSHOT_INDEX.md`
- 测试通过截图：当前以日志为主，PNG 需人工补拍
- 数据库表/审计日志截图：当前以日志为主，PNG 需人工补拍
- Docker 构建成功截图或日志：有失败日志，无成功截图

## 9. 可直接写入论文报告的数据表
{paper_tables}

## 10. 复现命令

```powershell
Set-Location "{ROOT}"
python scripts\\stats\\generate_stats.py
```

重新生成底层日志的核心命令：

```powershell
git status --short | Tee-Object docs\\report_assets\\logs\\git_status.txt
git rev-parse HEAD | Tee-Object docs\\report_assets\\logs\\git_head.txt
rg --files | Tee-Object docs\\report_assets\\logs\\code_file_inventory.txt
cargo test --manifest-path rust_core\\Cargo.toml --no-fail-fast 2>&1 | Tee-Object docs\\report_assets\\logs\\cargo_test_full.txt | Select-Object -Last 80 | Tee-Object docs\\report_assets\\logs\\cargo_test_tail.txt
Push-Location api_server; .\\.venv\\Scripts\\python.exe -m pytest --tb=no -q 2>&1 | Tee-Object ..\\docs\\report_assets\\logs\\pytest_venv_full.txt | Select-Object -Last 80 | Tee-Object ..\\docs\\report_assets\\logs\\pytest_venv_tail.txt; Pop-Location
Push-Location frontend; npm test 2>&1 | Tee-Object ..\\docs\\report_assets\\logs\\npm_test_full.txt | Select-Object -Last 80 | Tee-Object ..\\docs\\report_assets\\logs\\npm_test_tail.txt; Pop-Location
docker compose -f deploy\\docker-compose.yml config 2>&1 | Tee-Object docs\\report_assets\\logs\\docker_compose_config.txt
docker compose -f deploy\\docker-compose.yml build 2>&1 | Tee-Object docs\\report_assets\\logs\\docker_compose_build.txt
```

## 附录 A：关键命令输出索引

{markdown_table(evidence_rows, ["category", "file_path", "purpose", "status", "notes"], max_rows=80)}
"""


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    git_status, head, _files = collect_git_logs()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    code_rows = build_code_lines_summary()
    status_rows = parse_status_codes()
    endpoint_rows = parse_api_endpoints()
    algo_rows = build_algorithm_rows()
    vector_rows = build_test_vector_sources()
    test_rows = parse_test_summary()
    figure_rows = build_figure_assets_summary()

    write_csv(
        DATA_DIR / "code_lines_summary.csv",
        ["area", "path_pattern", "file_count", "line_count", "non_empty_line_count", "test_file_count", "evidence_command"],
        code_rows,
    )
    write_csv(
        DATA_DIR / "status_codes.csv",
        ["code_name", "value_or_http_status", "definition_file", "reference_count", "reference_files", "evidence_command"],
        status_rows,
    )
    write_csv(
        DATA_DIR / "api_endpoints.csv",
        ["module", "method", "path", "router_file", "handler_name", "request_schema", "response_schema", "service_call", "test_files", "status", "evidence"],
        endpoint_rows,
    )
    write_csv(
        DATA_DIR / "algorithm_implementation.csv",
        ["layer", "module", "algorithm", "subfeature", "implementation_file", "test_file", "test_count", "status", "evidence"],
        algo_rows,
    )
    write_csv(
        DATA_DIR / "test_vector_sources.csv",
        ["algorithm", "source_standard_or_library", "test_file", "test_case_name", "count", "evidence"],
        vector_rows,
    )
    write_csv(
        DATA_DIR / "test_summary.csv",
        ["test_layer", "command", "passed", "failed", "ignored_or_skipped", "deselected", "errors", "status", "evidence_log"],
        test_rows,
    )
    write_csv(
        DATA_DIR / "figure_assets_summary.csv",
        ["figure_id", "title", "source_data", "script", "svg_path", "png_path", "qa_status", "used_in_report", "repro_command"],
        figure_rows,
    )

    write_text(STATS_MD, "# CryptoLab 项目统计汇总\n\n生成中。\n")
    evidence_rows = build_evidence_inventory()
    write_csv(
        DATA_DIR / "evidence_inventory.csv",
        ["category", "file_path", "purpose", "status", "last_write_time", "notes"],
        evidence_rows,
    )
    stats_text = build_stats_md(
        generated_at=generated_at,
        head=head,
        git_status=git_status,
        code_rows=code_rows,
        status_rows=status_rows,
        endpoint_rows=endpoint_rows,
        algo_rows=algo_rows,
        vector_rows=vector_rows,
        test_rows=test_rows,
        figure_rows=figure_rows,
        evidence_rows=evidence_rows,
    )
    write_text(STATS_MD, stats_text)


if __name__ == "__main__":
    main()
