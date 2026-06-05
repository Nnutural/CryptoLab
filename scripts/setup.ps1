# CryptoLab one-shot bootstrap (PowerShell variant of setup.sh).
# Usage:
#   . .\scripts\env.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

if (-not $env:CRYPTOLAB_ROOT) {
    Write-Error "CRYPTOLAB_ROOT is not set. Did you dot-source scripts/env.ps1?"
    exit 1
}

Set-Location $env:CRYPTOLAB_ROOT

# ----- 1) Rust toolchain (project-local) -----
Write-Host "==> [1/4] Installing Rust toolchain into $env:RUSTUP_HOME"
$rustupExe = Join-Path $env:CARGO_HOME "bin\rustup.exe"
if (-not (Test-Path $rustupExe)) {
    $rustupInit = Join-Path $env:TEMP "rustup-init.exe"
    Invoke-WebRequest -Uri "https://win.rustup.rs/x86_64" -OutFile $rustupInit
    & $rustupInit -y --no-modify-path --default-toolchain stable --profile minimal
}
& $rustupExe toolchain install stable --profile minimal
& $rustupExe component add rustfmt clippy

# ----- 2) Python venv + deps -----
Write-Host "==> [2/4] Creating Python venv at $env:CRYPTOLAB_ROOT\.venv"
$venvPath = Join-Path $env:CRYPTOLAB_ROOT ".venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
& $activate

python -m pip install --upgrade pip wheel
pip install -e (Join-Path $env:CRYPTOLAB_ROOT "api_server")
pip install maturin pytest pytest-asyncio httpx ruff mypy

# ----- 3) Build Rust → Python extension -----
Write-Host "==> [3/4] Building Rust core (maturin develop)"
try {
    Push-Location (Join-Path $env:CRYPTOLAB_ROOT "rust_core")
    maturin develop --release
} catch {
    Write-Warning "maturin develop failed (OK at init stage if algorithms are todo!())."
} finally {
    Pop-Location
}

# ----- 4) Frontend deps -----
Write-Host "==> [4/4] Installing frontend dependencies"
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Push-Location (Join-Path $env:CRYPTOLAB_ROOT "frontend")
    npm install --no-audit --no-fund
    Pop-Location
} else {
    Write-Warning "npm not found; skip frontend install."
}

Write-Host ""
Write-Host "[CryptoLab] setup complete."
Write-Host "Reminder: dot-source scripts/env.ps1 in every new PowerShell session."
