[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$RuntimeLog = Join-Path $ProjectRoot "dist\gzdoom-runtime-smoke.log"

Write-Host "Building current prototype..."
python (Join-Path $PSScriptRoot "build.py")
if ($LASTEXITCODE -ne 0) {
    throw "Prototype build failed with exit code $LASTEXITCODE."
}

Write-Host "Resolving pinned official runtime..."
& (Join-Path $PSScriptRoot "bootstrap_runtime.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Runtime bootstrap failed with exit code $LASTEXITCODE."
}

foreach ($required in @($GZDoomExe, $FreedoomWad, $Pk3)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Runtime smoke prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $RuntimeLog) {
    Remove-Item -LiteralPath $RuntimeLog -Force
}

Write-Host "Running GZDoom startup/parser smoke test with -norun..."
$arguments = @(
    "-stdout",
    "-norun",
    "-iwad", $FreedoomWad,
    "-file", $Pk3
)

$output = & $GZDoomExe @arguments 2>&1
$exitCode = $LASTEXITCODE
$output | Tee-Object -FilePath $RuntimeLog | ForEach-Object { Write-Host $_ }

if ($exitCode -ne 0) {
    throw "GZDoom runtime smoke test failed with exit code $exitCode. See $RuntimeLog"
}

$logText = Get-Content -LiteralPath $RuntimeLog -Raw
$errorPatterns = @(
    "Script error",
    "Execution could not continue",
    "Unknown class",
    "Unknown identifier",
    "Invalid parameter",
    "Parse error"
)
foreach ($pattern in $errorPatterns) {
    if ($logText -match [regex]::Escape($pattern)) {
        throw "GZDoom reported '$pattern' during runtime smoke validation."
    }
}

Write-Host "GZDoom runtime smoke test: PASS"
