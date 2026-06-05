# CryptoLab project-local environment (PowerShell variant of env.sh).
# Dot-source in every new PowerShell session:
#   . .\scripts\env.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
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
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

$VenvActivate = Join-Path $CryptolabRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    & $VenvActivate
}

# ----- npm -----
$env:NPM_CONFIG_CACHE  = Join-Path $CryptolabRoot ".npm-cache"
$env:NPM_CONFIG_PREFIX = Join-Path $CryptolabRoot ".npm-global"
if (-not (Test-Path $env:NPM_CONFIG_CACHE))  { New-Item -ItemType Directory -Force -Path $env:NPM_CONFIG_CACHE  | Out-Null }
if (-not (Test-Path $env:NPM_CONFIG_PREFIX)) { New-Item -ItemType Directory -Force -Path $env:NPM_CONFIG_PREFIX | Out-Null }

$NpmBin = $env:NPM_CONFIG_PREFIX
if (-not ($env:PATH.Split(';') -contains $NpmBin)) {
    $env:PATH = "$NpmBin;$env:PATH"
}

Write-Host "[CryptoLab] env loaded:"
Write-Host "  CRYPTOLAB_ROOT = $env:CRYPTOLAB_ROOT"
Write-Host "  CARGO_HOME     = $env:CARGO_HOME"
Write-Host "  RUSTUP_HOME    = $env:RUSTUP_HOME"
Write-Host "  npm cache      = $env:NPM_CONFIG_CACHE"
Write-Host "  npm prefix     = $env:NPM_CONFIG_PREFIX"
if ($env:VIRTUAL_ENV) {
    Write-Host "  python venv    = $env:VIRTUAL_ENV"
} else {
    Write-Host "  python venv    = (not yet created — run scripts/setup.ps1)"
}
