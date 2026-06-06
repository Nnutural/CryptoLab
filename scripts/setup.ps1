# CryptoLab one-shot bootstrap (PowerShell variant of setup.sh).
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
#
# Steps:
#   1) Load project-local env (CARGO_HOME, etc.) via env.ps1.
#   2) Verify the Rust toolchain is installed; if not, instruct the user to
#      install it manually (Windows can't `curl | sh`).
#   3) Create api_server/.venv, activate it, install api_server[dev].
#   4) Install maturin and run `maturin develop --release` (best-effort).
#   5) Install frontend dependencies via npm.
# Any step that fails terminates the script (Stop on Error).

$ErrorActionPreference = "Stop"

# ----- 1) Load the project-local environment -----
. (Join-Path $PSScriptRoot "env.ps1")

if (-not $env:CRYPTOLAB_ROOT) {
    Write-Error "CRYPTOLAB_ROOT is not set after sourcing env.ps1; aborting."
    exit 1
}
if ($env:CARGO_HOME -eq (Join-Path $env:USERPROFILE ".cargo")) {
    Write-Error "CARGO_HOME points at user-global %USERPROFILE%\.cargo; env.ps1 did not take effect."
    exit 1
}

Set-Location $env:CRYPTOLAB_ROOT

# ----- 2) Rust toolchain check -----
Write-Host "==> [1/4] Verifying Rust toolchain under $env:RUSTUP_HOME"
$rustupExe = Join-Path $env:CARGO_HOME "bin\rustup.exe"
if (-not (Test-Path $rustupExe)) {
    Write-Host ""
    Write-Host "rustup not found at $rustupExe."
    Write-Host ""
    Write-Host "Windows does not support 'curl | sh', so this script will NOT auto-install."
    Write-Host "Please install rustup manually:"
    Write-Host ""
    Write-Host "  1. Download rustup-init.exe from https://rustup.rs/"
    Write-Host "  2. Open a NEW PowerShell, run:"
    Write-Host "       . .\scripts\env.ps1"
    Write-Host "       .\rustup-init.exe -y --no-modify-path --default-toolchain stable --profile minimal"
    Write-Host "  3. Re-run this script."
    Write-Host ""
    Write-Error "Aborting until rustup is installed."
    exit 1
}

& $rustupExe toolchain install stable --profile minimal
if ($LASTEXITCODE -ne 0) { Write-Error "rustup toolchain install failed."; exit 1 }
& $rustupExe component add rustfmt clippy
if ($LASTEXITCODE -ne 0) { Write-Error "rustup component add failed."; exit 1 }

# ----- 3) Python venv + editable install of api_server -----
$ApiServerDir = Join-Path $env:CRYPTOLAB_ROOT "api_server"
$VenvDir      = Join-Path $ApiServerDir ".venv"
Write-Host "==> [2/4] Creating Python venv at $VenvDir"

Push-Location $ApiServerDir
try {
    if (-not (Test-Path $VenvDir)) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { Write-Error "python -m venv .venv failed."; exit 1 }
    }
    $Activate = Join-Path $VenvDir "Scripts\Activate.ps1"
    & $Activate

    python -m pip install --upgrade pip wheel
    if ($LASTEXITCODE -ne 0) { Write-Error "pip upgrade failed."; exit 1 }
    pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) { Write-Error "pip install -e .[dev] failed."; exit 1 }
    pip install maturin
    if ($LASTEXITCODE -ne 0) { Write-Error "pip install maturin failed."; exit 1 }
} finally {
    Pop-Location
}

# ----- 4) Build Rust -> Python extension (best-effort at init stage) -----
Write-Host "==> [3/4] Building Rust core (maturin develop --release)"
Push-Location (Join-Path $env:CRYPTOLAB_ROOT "rust_core")
try {
    maturin develop --release
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "maturin develop failed -- expected at init stage while algorithm bodies are todo!()."
    }
} catch {
    Write-Warning "maturin develop threw: $($_.Exception.Message). Skipping (expected at init stage)."
} finally {
    Pop-Location
}

# ----- 5) Frontend deps -----
Write-Host "==> [4/4] Installing frontend dependencies"
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm not found on PATH. Install Node.js 20 LTS from https://nodejs.org/ and re-run."
    exit 1
}
Push-Location (Join-Path $env:CRYPTOLAB_ROOT "frontend")
try {
    npm install --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { Write-Error "npm install failed."; exit 1 }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "[CryptoLab] setup complete."
Write-Host ""
Write-Host "Next steps -- run from the project root after dot-sourcing env.ps1:"
Write-Host "  . .\scripts\env.ps1"
Write-Host "  cargo check --manifest-path rust_core/Cargo.toml"
Write-Host "  pytest api_server/tests --collect-only"
Write-Host "  docker compose -f deploy/docker-compose.yml config | Out-Null"
Write-Host ""
Write-Host "Reminder: dot-source scripts/env.ps1 in every new PowerShell session."
