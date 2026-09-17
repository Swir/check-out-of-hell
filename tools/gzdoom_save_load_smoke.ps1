[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$WorkDir = Join-Path $ProjectRoot "dist\save-load-smoke"
$SaveDir = Join-Path $WorkDir "saves"
$RuntimeLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"
$CreateCfg = Join-Path $WorkDir "create-save.cfg"
$LoadCfg = Join-Path $WorkDir "load-save.cfg"

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
        throw "Save/load smoke prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $WorkDir) {
    Remove-Item -LiteralPath $WorkDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $SaveDir | Out-Null
if (Test-Path -LiteralPath $RuntimeLog) {
    Remove-Item -LiteralPath $RuntimeLog -Force
}

# Keep each scenario on one command line so GZDoom's built-in `wait` command
# defers the remaining commands by deterministic game tics.
'map MAP01; wait 70; god; give CheckoutFuse 2; give CorporateMemo 1; wait 2; printinv; save coh-save-load-ci "CHECKOUT OF HELL CI SAVE"; wait 35; quit' |
    Set-Content -LiteralPath $CreateCfg -Encoding ASCII
'load coh-save-load-ci; wait 70; printinv; wait 2; quit' |
    Set-Content -LiteralPath $LoadCfg -Encoding ASCII

function Invoke-GZDoomScenario {
    param(
        [string]$Label,
        [string]$ConfigPath
    )

    Write-Host "Running GZDoom $Label scenario..."
    $arguments = @(
        "-stdout",
        "-nosound",
        "-window",
        "-width", "320",
        "-height", "200",
        "-savedir", $SaveDir,
        "-iwad", $FreedoomWad,
        "-file", $Pk3,
        "+exec", $ConfigPath
    )

    $output = & $GZDoomExe @arguments 2>&1
    $exitCode = $LASTEXITCODE
    $outputLines = @($output | ForEach-Object { "$_" })

    Add-Content -LiteralPath $RuntimeLog -Value "=== $Label (exit $exitCode) ===" -Encoding UTF8
    if ($outputLines.Count -gt 0) {
        $outputLines | Add-Content -LiteralPath $RuntimeLog -Encoding UTF8
        $outputLines | ForEach-Object { Write-Host $_ }
    }

    if ($exitCode -ne 0) {
        throw "GZDoom $Label scenario failed with exit code $exitCode. See $RuntimeLog"
    }

    $text = $outputLines -join "`n"
    foreach ($pattern in @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Invalid parameter",
        "Parse error",
        "Cannot execute unsafe command"
    )) {
        if ($text -match [regex]::Escape($pattern)) {
            throw "GZDoom $Label scenario reported '$pattern'. See $RuntimeLog"
        }
    }

    return $text
}

$createOutput = Invoke-GZDoomScenario -Label "create-save" -ConfigPath $CreateCfg

$saveFiles = @(Get-ChildItem -LiteralPath $SaveDir -Filter "coh-save-load-ci*.zds" -File -ErrorAction SilentlyContinue)
if ($saveFiles.Count -ne 1) {
    throw "Expected exactly one CI savegame in $SaveDir, found $($saveFiles.Count). See $RuntimeLog"
}
if ($saveFiles[0].Length -lt 1024) {
    throw "CI savegame is unexpectedly small: $($saveFiles[0].Length) bytes."
}

if ($createOutput -notmatch "CheckoutFuse.*\(2/3\)") {
    throw "Pre-save inventory did not contain CheckoutFuse 2/3. See $RuntimeLog"
}
if ($createOutput -notmatch "CorporateMemo.*\(1/3\)") {
    throw "Pre-save inventory did not contain CorporateMemo 1/3. See $RuntimeLog"
}

$loadOutput = Invoke-GZDoomScenario -Label "load-save" -ConfigPath $LoadCfg
if ($loadOutput -notmatch "CheckoutFuse.*\(2/3\)") {
    throw "Loaded inventory did not preserve CheckoutFuse 2/3. See $RuntimeLog"
}
if ($loadOutput -notmatch "CorporateMemo.*\(1/3\)") {
    throw "Loaded inventory did not preserve CorporateMemo 1/3. See $RuntimeLog"
}

Write-Host "Pinned GZDoom save/load smoke test: PASS"
