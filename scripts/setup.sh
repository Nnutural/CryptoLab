#!/usr/bin/env bash
# CryptoLab one-shot bootstrap: installs Rust toolchain (project-local),
# creates Python venv, and installs frontend deps. Idempotent.
#
# Usage:
#   source scripts/env.sh
#   bash scripts/setup.sh

set -euo pipefail

if [ -z "${CRYPTOLAB_ROOT:-}" ]; then
    echo "ERROR: CRYPTOLAB_ROOT is not set. Did you forget 'source scripts/env.sh'?"
    exit 1
fi

cd "${CRYPTOLAB_ROOT}"

# ---- Sanity: refuse to run if HOME-global tooling is leaking in ----
if [ "${CARGO_HOME}" = "${HOME}/.cargo" ]; then
    echo "ERROR: CARGO_HOME points at user-global path; env.sh was not sourced."
    exit 1
fi

# ---------- 1) Rust toolchain (project-local) ----------
echo "==> [1/4] Installing Rust toolchain into ${RUSTUP_HOME}"
if ! command -v rustup >/dev/null 2>&1; then
    # rustup-init respects CARGO_HOME / RUSTUP_HOME envs already.
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --no-modify-path --default-toolchain stable --profile minimal
fi

# Make sure we have the stable toolchain + required components.
"${CARGO_HOME}/bin/rustup" toolchain install stable --profile minimal
"${CARGO_HOME}/bin/rustup" component add rustfmt clippy

# ---------- 2) Python venv + deps ----------
echo "==> [2/4] Creating Python venv at ${CRYPTOLAB_ROOT}/.venv"
if [ ! -d "${CRYPTOLAB_ROOT}/.venv" ]; then
    python3 -m venv "${CRYPTOLAB_ROOT}/.venv"
fi

# shellcheck disable=SC1091
. "${CRYPTOLAB_ROOT}/.venv/bin/activate" 2>/dev/null \
    || . "${CRYPTOLAB_ROOT}/.venv/Scripts/activate"

pip install --upgrade pip wheel
pip install -e "${CRYPTOLAB_ROOT}/api_server"
pip install maturin
# Test-time deps.
pip install pytest pytest-asyncio httpx ruff mypy

# ---------- 3) Build Rust → Python extension into the venv ----------
echo "==> [3/4] Building Rust core (maturin develop)"
( cd "${CRYPTOLAB_ROOT}/rust_core" && maturin develop --release ) \
    || echo "WARN: maturin develop failed (this is OK at init stage if algorithms are todo!())."

# ---------- 4) Frontend deps ----------
echo "==> [4/4] Installing frontend dependencies"
if command -v npm >/dev/null 2>&1; then
    ( cd "${CRYPTOLAB_ROOT}/frontend" && npm install --no-audit --no-fund )
else
    echo "WARN: npm not found; skip frontend install."
fi

echo
echo "[CryptoLab] setup complete."
echo "Reminder: source scripts/env.sh in every new shell."
