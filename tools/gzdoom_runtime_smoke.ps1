[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$RuntimeLog = Join-Path $ProjectRoot "dist\gzdoom-runtime-smoke.log"
$EngineErrorLog = Join-Path $ProjectRoot "dist\gzdoom-runtime-engine.log"

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

foreach ($path in @($RuntimeLog, $EngineErrorLog)) {
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

Write-Host "Running GZDoom startup/parser smoke test with -norun..."
$arguments = @(
    "-stdout",
    "-norun",
    "-noautoload",
    "-errorlog", $EngineErrorLog,
    "-iwad", $FreedoomWad,
    "-file", $Pk3
)

$output = & $GZDoomExe @arguments 2>&1
$exitCode = $LASTEXITCODE
$outputLines = @($output | ForEach-Object { "$_" })
$combined = New-Object System.Collections.Generic.List[string]
if ($outputLines.Count -gt 0) {
    foreach ($line in $outputLines) {
        $combined.Add($line)
        Write-Host $line
    }
}
if (Test-Path -LiteralPath $EngineErrorLog) {
    $engineText = Get-Content -LiteralPath $EngineErrorLog -Raw
    if (-not [string]::IsNullOrWhiteSpace($engineText)) {
        $combined.Add("===== GZDoom engine error log =====")
        $combined.Add($engineText)
    }
}
if ($combined.Count -eq 0) {
    $combined.Add("GZDoom -norun completed with no stdout or engine error log. Exit code: $exitCode")
}
$combined | Set-Content -LiteralPath $RuntimeLog -Encoding UTF8

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
    "Parse error",
    "DIED WITH FATAL ERROR"
)
foreach ($pattern in $errorPatterns) {
    if ($logText -match [regex]::Escape($pattern)) {
        throw "GZDoom reported '$pattern' during runtime smoke validation. See $RuntimeLog"
    }
}

Write-Host "GZDoom runtime smoke test: PASS"
