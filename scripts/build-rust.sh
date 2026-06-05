#!/usr/bin/env bash
# Compile the Rust core and install the resulting Python extension into ./.venv.
set -euo pipefail

if [ -z "${CRYPTOLAB_ROOT:-}" ]; then
    echo "ERROR: source scripts/env.sh first."
    exit 1
fi

cd "${CRYPTOLAB_ROOT}/rust_core"

# Use the project-local venv as the maturin target interpreter.
if [ -n "${VIRTUAL_ENV:-}" ]; then
    PYTHON="${VIRTUAL_ENV}/bin/python"
    [ -x "${PYTHON}" ] || PYTHON="${VIRTUAL_ENV}/Scripts/python.exe"
else
    PYTHON="$(command -v python3 || command -v python)"
fi

echo "==> maturin develop --release (interpreter: ${PYTHON})"
maturin develop --release -i "${PYTHON}"

echo "==> smoke test"
"${PYTHON}" -c "import cryptolab_core; print('cryptolab_core imported OK:', dir(cryptolab_core)[:5])"
