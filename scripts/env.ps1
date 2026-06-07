# CryptoLab project-local environment (PowerShell variant of env.sh).
# Dot-source in EVERY new PowerShell session:
#   . .\scripts\env.ps1
#
# Pins every toolchain cache under the project so user-global locations
# (~/.cargo, ~/.rustup, %APPDATA%\npm, %APPDATA%\Python, ~\.cache\pip) stay
# untouched.

# Resolve project root from the script's own location (works whether dot-sourced
# from the repo root or any subdirectory).
$ScriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Path
$CryptolabRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$env:CRYPTOLAB_ROOT = $CryptolabRoot

# ----- Rust -----
$env:CARGO_HOME  = Join-Path $CryptolabRoot ".cargo-home"
$env:RUSTUP_HOME = Join-Path $CryptolabRoot ".rustup-home"
if (-not (Test-Path $env:CARGO_HOME))  { New-Item -ItemType Directory -Force -Path $env:CARGO_HOME  | Out-Null }
if (-not (Test-Path $env:RUSTUP_HOME)) { New-Item -ItemType Directory -Force -Path $env:RUSTUP_HOME | Out-Null }

$CargoBin = Join-Path $env:CARGO_HOME "bin"
if (-not ($env:PATH.Split(';') -contains $CargoBin)) {
    $env:PATH = "$CargoBin;$env:PATH"
}

# ----- Python -----
$env:PYTHONDONTWRITEBYTECODE      = "1"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
if (-not $env:CRYPTOLAB_JWT_SECRET) {
    $env:CRYPTOLAB_JWT_SECRET = "dev-jwt-secret-change-me-32-bytes-minimum-for-hs256"
}

# Project-local pip cache (replaces %LOCALAPPDATA%\pip\Cache).
$env:PIP_CACHE_DIR = Join-Path $CryptolabRoot ".pip-cache"
if (-not (Test-Path $env:PIP_CACHE_DIR)) {
    New-Item -ItemType Directory -Force -Path $env:PIP_CACHE_DIR | Out-Null
}

# Activate the venv created by setup.ps1. We look in two locations:
#   1. api_server/.venv  — the layout setup.ps1 creates
#   2. .venv             — repo-root layout used by setup.sh on Unix
# Whichever exists wins; if neither exists, setup.ps1 has not been run yet.
$VenvCandidates = @(
    (Join-Path $CryptolabRoot "api_server\.venv\Scripts\Activate.ps1"),
    (Join-Path $CryptolabRoot ".venv\Scripts\Activate.ps1")
)
$VenvActivated = $false
foreach ($candidate in $VenvCandidates) {
    if (Test-Path $candidate) {
        & $candidate
        $VenvActivated = $true
        break
    }
}

# ----- npm -----
$env:NPM_CONFIG_CACHE  = Join-Path $CryptolabRoot ".npm-cache"
$env:NPM_CONFIG_PREFIX = Join-Path $CryptolabRoot ".npm-global"
if (-not (Test-Path $env:NPM_CONFIG_CACHE))  { New-Item -ItemType Directory -Force -Path $env:NPM_CONFIG_CACHE  | Out-Null }
if (-not (Test-Path $env:NPM_CONFIG_PREFIX)) { New-Item -ItemType Directory -Force -Path $env:NPM_CONFIG_PREFIX | Out-Null }

# On Windows, global npm binaries live directly in $prefix (no `bin/` subdir).
if (-not ($env:PATH.Split(';') -contains $env:NPM_CONFIG_PREFIX)) {
    $env:PATH = "$env:NPM_CONFIG_PREFIX;$env:PATH"
}

# ----- Summary -----
Write-Host "[CryptoLab] env loaded:"
Write-Host "  CRYPTOLAB_ROOT = $env:CRYPTOLAB_ROOT"
Write-Host "  CARGO_HOME     = $env:CARGO_HOME"
Write-Host "  RUSTUP_HOME    = $env:RUSTUP_HOME"
Write-Host "  PIP_CACHE_DIR  = $env:PIP_CACHE_DIR"
Write-Host "  npm cache      = $env:NPM_CONFIG_CACHE"
Write-Host "  npm prefix     = $env:NPM_CONFIG_PREFIX"
if ($VenvActivated -and $env:VIRTUAL_ENV) {
    Write-Host "  python venv    = $env:VIRTUAL_ENV"
} else {
    Write-Host "  python venv    = (not yet created -- run scripts/setup.ps1)"
}
