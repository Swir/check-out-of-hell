[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"

Write-Host "Resolving pinned official Windows runtime..."
& (Join-Path $PSScriptRoot "bootstrap_runtime.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Runtime bootstrap failed with exit code $LASTEXITCODE."
}

foreach ($required in @($GZDoomExe, $FreedoomWad)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Save/load prerequisite is missing: $required"
    }
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python is required for the developer save/load regression. Use PLAY.bat for player-facing one-click setup."
}

& $python.Source (Join-Path $PSScriptRoot "gzdoom_save_load_roundtrip.py") `
    --gzdoom $GZDoomExe `
    --iwad $FreedoomWad
if ($LASTEXITCODE -ne 0) {
    throw "GZDoom save/load roundtrip failed with exit code $LASTEXITCODE."
}
