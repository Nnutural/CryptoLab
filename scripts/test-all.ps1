# Run the full CryptoLab test suite: Rust + Python. Mirror of test-all.sh.
#
# Usage:
#   . .\scripts\env.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1

$ErrorActionPreference = "Stop"

if (-not $env:CRYPTOLAB_ROOT) {
    Write-Error "CRYPTOLAB_ROOT is not set. Dot-source scripts/env.ps1 first."
    exit 1
}

Set-Location $env:CRYPTOLAB_ROOT

Write-Host "==> Rust unit tests"
cargo test --manifest-path rust_core/Cargo.toml --all-features
if ($LASTEXITCODE -ne 0) { Write-Error "cargo test failed."; exit 1 }

Write-Host "==> Rust clippy"
cargo clippy --manifest-path rust_core/Cargo.toml --all-targets -- -D warnings
if ($LASTEXITCODE -ne 0) { Write-Error "cargo clippy failed."; exit 1 }

Write-Host "==> Rebuilding Python extension"
& (Join-Path $PSScriptRoot "build-rust.ps1")
if ($LASTEXITCODE -ne 0) { Write-Error "build-rust.ps1 failed."; exit 1 }

Write-Host "==> Python tests"
pytest api_server/tests -v
if ($LASTEXITCODE -ne 0) { Write-Error "pytest failed."; exit 1 }

Write-Host "==> Python lint"
ruff check api_server
if ($LASTEXITCODE -ne 0) { Write-Error "ruff check failed."; exit 1 }
mypy api_server/app
if ($LASTEXITCODE -ne 0) { Write-Error "mypy failed."; exit 1 }

Write-Host "[CryptoLab] all tests passed."
