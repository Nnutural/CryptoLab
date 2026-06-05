#!/usr/bin/env bash
# Run criterion benchmarks for the Rust core.
set -euo pipefail

if [ -z "${CRYPTOLAB_ROOT:-}" ]; then
    echo "ERROR: source scripts/env.sh first."
    exit 1
fi

cd "${CRYPTOLAB_ROOT}/rust_core"
cargo bench --bench '*' "$@"

echo
echo "Report: ${CRYPTOLAB_ROOT}/rust_core/target/criterion/report/index.html"
