# Run criterion benchmarks for the Rust core. Mirror of bench.sh.
#
# Usage:
#   . .\scripts\env.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\bench.ps1 [-- extra-criterion-args]

$ErrorActionPreference = "Stop"

if (-not $env:CRYPTOLAB_ROOT) {
    Write-Error "CRYPTOLAB_ROOT is not set. Dot-source scripts/env.ps1 first."
    exit 1
}

Push-Location (Join-Path $env:CRYPTOLAB_ROOT "rust_core")
try {
    cargo bench --bench '*' @args
    if ($LASTEXITCODE -ne 0) { Write-Error "cargo bench failed."; exit 1 }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Report: $(Join-Path $env:CRYPTOLAB_ROOT 'rust_core\target\criterion\report\index.html')"
