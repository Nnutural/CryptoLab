# Compile the Rust core and install the resulting Python extension into the
# project-local venv. Mirror of scripts/build-rust.sh.
#
# Usage:
#   . .\scripts\env.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\build-rust.ps1

$ErrorActionPreference = "Stop"

if (-not $env:CRYPTOLAB_ROOT) {
    Write-Error "CRYPTOLAB_ROOT is not set. Dot-source scripts/env.ps1 first."
    exit 1
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Push-Location (Join-Path $env:CRYPTOLAB_ROOT "rust_core")
try {
    # Pick the venv's python.exe as maturin's target interpreter so the wheel
    # lands in api_server/.venv\Lib\site-packages and not the system Python.
    if ($env:VIRTUAL_ENV) {
        $PythonExe = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (-not (Test-Path $PythonExe)) {
            $PythonExe = Join-Path $env:VIRTUAL_ENV "bin\python"
        }
    } else {
        $PythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $PythonCmd) { Write-Error "python not found on PATH."; exit 1 }
        $PythonExe = $PythonCmd.Source
    }

    Write-Host "==> maturin develop --release (active interpreter: $PythonExe)"
    maturin develop --release
    if ($LASTEXITCODE -ne 0) { Write-Error "maturin develop failed."; exit 1 }

    Write-Host "==> smoke test"
    & $PythonExe -c "import cryptolab_core; print('cryptolab_core imported OK:', dir(cryptolab_core)[:5])"
    if ($LASTEXITCODE -ne 0) { Write-Error "smoke import failed."; exit 1 }
} finally {
    Pop-Location
}
