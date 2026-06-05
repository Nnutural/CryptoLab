#!/usr/bin/env bash
# CryptoLab project-local environment.
# Source this in EVERY new shell before running cargo / rustup / pip / npm:
#   source scripts/env.sh
#
# It pins all toolchain caches under the project directory so user-global
# locations (~/.cargo, ~/.rustup, site-packages, ~/.npm) stay untouched.

# Resolve project root regardless of where the script is sourced from.
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    _CL_SCRIPT="${BASH_SOURCE[0]}"
else
    _CL_SCRIPT="$0"
fi
CRYPTOLAB_ROOT="$(cd "$(dirname "${_CL_SCRIPT}")/.." && pwd)"
export CRYPTOLAB_ROOT

# ----- Rust -----
export CARGO_HOME="${CRYPTOLAB_ROOT}/.cargo-home"
export RUSTUP_HOME="${CRYPTOLAB_ROOT}/.rustup-home"
mkdir -p "${CARGO_HOME}" "${RUSTUP_HOME}"

# Prepend project-local cargo bin so rustup-installed binaries win over system.
case ":${PATH}:" in
    *":${CARGO_HOME}/bin:"*) ;;
    *) export PATH="${CARGO_HOME}/bin:${PATH}" ;;
esac

# ----- Python -----
export PYTHONDONTWRITEBYTECODE=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
# Activate local venv if it exists. setup.sh creates it on first run.
if [ -f "${CRYPTOLAB_ROOT}/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "${CRYPTOLAB_ROOT}/.venv/bin/activate"
elif [ -f "${CRYPTOLAB_ROOT}/.venv/Scripts/activate" ]; then
    # Windows Git Bash layout
    # shellcheck disable=SC1091
    . "${CRYPTOLAB_ROOT}/.venv/Scripts/activate"
fi

# ----- npm -----
export NPM_CONFIG_CACHE="${CRYPTOLAB_ROOT}/.npm-cache"
export NPM_CONFIG_PREFIX="${CRYPTOLAB_ROOT}/.npm-global"
mkdir -p "${NPM_CONFIG_CACHE}" "${NPM_CONFIG_PREFIX}"
case ":${PATH}:" in
    *":${NPM_CONFIG_PREFIX}/bin:"*) ;;
    *) export PATH="${NPM_CONFIG_PREFIX}/bin:${PATH}" ;;
esac

# ----- Summary -----
echo "[CryptoLab] env loaded:"
echo "  CRYPTOLAB_ROOT = ${CRYPTOLAB_ROOT}"
echo "  CARGO_HOME     = ${CARGO_HOME}"
echo "  RUSTUP_HOME    = ${RUSTUP_HOME}"
echo "  npm cache      = ${NPM_CONFIG_CACHE}"
echo "  npm prefix     = ${NPM_CONFIG_PREFIX}"
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "  python venv    = ${VIRTUAL_ENV}"
else
    echo "  python venv    = (not yet created — run scripts/setup.sh)"
fi
