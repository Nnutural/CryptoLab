#!/usr/bin/env bash
# Run the full CryptoLab test suite: Rust + Python.
set -euo pipefail

if [ -z "${CRYPTOLAB_ROOT:-}" ]; then
    echo "ERROR: source scripts/env.sh first."
    exit 1
fi

cd "${CRYPTOLAB_ROOT}"

echo "==> Rust unit tests"
cargo test --manifest-path rust_core/Cargo.toml --all-features

echo "==> Rust clippy"
cargo clippy --manifest-path rust_core/Cargo.toml --all-targets -- -D warnings

echo "==> Rebuilding Python extension"
bash scripts/build-rust.sh

echo "==> Python tests"
pytest api_server/tests -v

echo "==> Python lint"
ruff check api_server
mypy api_server/app

echo "[CryptoLab] all tests passed."
