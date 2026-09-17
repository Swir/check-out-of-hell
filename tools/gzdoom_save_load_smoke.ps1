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
$SaveInspector = Join-Path $PSScriptRoot "inspect_gzdoom_save.py"

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

foreach ($required in @($GZDoomExe, $FreedoomWad, $Pk3, $SaveInspector)) {
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

# The first process creates a real in-level save with authored objective inventory.
# The second process can only create the round-trip save after the first save has loaded.
'map MAP01; wait 70; god; give CheckoutFuse 2; give CorporateMemo 1; wait 4; save coh-save-load-ci "CHECKOUT OF HELL CI SAVE"; wait 35; quit' |
    Set-Content -LiteralPath $CreateCfg -Encoding ASCII
'load coh-save-load-ci; wait 70; save coh-save-load-ci-roundtrip "CHECKOUT OF HELL CI ROUNDTRIP"; wait 35; quit' |
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
}

function Get-SingleSave {
    param(
        [string]$Pattern,
        [string]$Label
    )

    $matches = @(Get-ChildItem -LiteralPath $SaveDir -Filter $Pattern -File -ErrorAction SilentlyContinue)
    if ($matches.Count -ne 1) {
        throw "Expected exactly one $Label savegame matching '$Pattern' in $SaveDir, found $($matches.Count)."
    }
    if ($matches[0].Length -lt 1024) {
        throw "$Label savegame is unexpectedly small: $($matches[0].Length) bytes."
    }
    return $matches[0]
}

function Test-SaveState {
    param(
        [System.IO.FileInfo]$SaveFile,
        [string]$Label
    )

    Write-Host "Inspecting $Label save archive: $($SaveFile.FullName)"
    python $SaveInspector $SaveFile.FullName CheckoutFuse CorporateMemo CheckoutPersistentShiftDirector
    if ($LASTEXITCODE -ne 0) {
        throw "$Label save archive did not preserve required serialized game state."
    }
}

Invoke-GZDoomScenario -Label "create-save" -ConfigPath $CreateCfg
$initialSave = Get-SingleSave -Pattern "coh-save-load-ci.zds" -Label "initial"
Test-SaveState -SaveFile $initialSave -Label "initial"

Invoke-GZDoomScenario -Label "load-save" -ConfigPath $LoadCfg
$roundTripSave = Get-SingleSave -Pattern "coh-save-load-ci-roundtrip.zds" -Label "round-trip"
Test-SaveState -SaveFile $roundTripSave -Label "round-trip"

Add-Content -LiteralPath $RuntimeLog -Value "Initial save: $($initialSave.Length) bytes" -Encoding UTF8
Add-Content -LiteralPath $RuntimeLog -Value "Round-trip save: $($roundTripSave.Length) bytes" -Encoding UTF8
Add-Content -LiteralPath $RuntimeLog -Value "Required serialized state: CheckoutFuse, CorporateMemo, CheckoutPersistentShiftDirector" -Encoding UTF8

Write-Host "Pinned GZDoom save/load smoke test: PASS"
