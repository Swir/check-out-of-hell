[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$WorkDir = Join-Path $ProjectRoot "dist\runtime-save-load"
$SaveDir = Join-Path $WorkDir "saves"
$ConfigPath = Join-Path $WorkDir "gzdoom-ci.ini"
$SaveCommandPath = Join-Path $WorkDir "save-phase.cfg"
$LoadCommandPath = Join-Path $WorkDir "load-phase.cfg"
$SaveLog = Join-Path $WorkDir "save-phase.log"
$LoadLog = Join-Path $WorkDir "load-phase.log"
$CombinedLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"
$SaveStem = "coh-runtime-state"
$SaveFile = Join-Path $SaveDir "$SaveStem.zds"

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
        throw "Runtime save/load prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $WorkDir) {
    Remove-Item -LiteralPath $WorkDir -Recurse -Force
}
New-Item -ItemType Directory -Path $SaveDir -Force | Out-Null

# The first process enters MAP01, waits for fresh-world objective cleanup, then writes
# unmistakable department state into real GZDoom inventory before saving and exiting.
# If WorldLoaded incorrectly treats the later restore as a fresh map, CheckoutFuse will
# be stripped and the second-process assertion below will fail.
$saveCommands = @"
map MAP01; wait 15; god; notarget; wait 20; setinv CheckoutFuse 2; setinv CorporateMemo 2; wait 5; printinv; save $SaveStem "CHECKOUT OF HELL runtime state"; wait 70; quickexit
"@
$loadCommands = @"
load $SaveStem; wait 70; printinv; wait 10; quickexit
"@
$saveCommands.Trim() | Set-Content -LiteralPath $SaveCommandPath -Encoding ASCII
$loadCommands.Trim() | Set-Content -LiteralPath $LoadCommandPath -Encoding ASCII

function Invoke-GZDoomPhase([string]$PhaseName, [string]$CommandFile, [string]$LogPath) {
    if (Test-Path -LiteralPath $LogPath) {
        Remove-Item -LiteralPath $LogPath -Force
    }

    $arguments = @(
        "-stdout",
        "-nosound",
        "-noautoload",
        "-iwad", $FreedoomWad,
        "-file", $Pk3,
        "-savedir", $SaveDir,
        "-config", $ConfigPath,
        "+vid_fullscreen", "false",
        "+vid_preferbackend", "0",
        "+exec", $CommandFile
    )

    Write-Host "Running GZDoom $PhaseName phase..."
    $output = & $GZDoomExe @arguments 2>&1
    $exitCode = $LASTEXITCODE
    $outputLines = @($output | ForEach-Object { "$_" })

    if ($outputLines.Count -gt 0) {
        $outputLines | Set-Content -LiteralPath $LogPath -Encoding UTF8
        $outputLines | ForEach-Object { Write-Host $_ }
    }
    else {
        "GZDoom $PhaseName phase completed with no stdout. Exit code: $exitCode" |
            Set-Content -LiteralPath $LogPath -Encoding UTF8
    }

    if ($exitCode -ne 0) {
        throw "GZDoom $PhaseName phase failed with exit code $exitCode. See $LogPath"
    }

    $logText = Get-Content -LiteralPath $LogPath -Raw
    $errorPatterns = @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Invalid parameter",
        "Parse error",
        "Unknown command",
        "Cannot find savegame"
    )
    foreach ($pattern in $errorPatterns) {
        if ($logText -match [regex]::Escape($pattern)) {
            throw "GZDoom reported '$pattern' during the $PhaseName phase."
        }
    }

    return $logText
}

function Assert-InventoryState([string]$LogText, [string]$PhaseName) {
    if ($LogText -notmatch "(?m)^\s*CheckoutFuse\s+#\d+\s+\(2/") {
        throw "$PhaseName inventory dump did not contain CheckoutFuse amount 2."
    }
    if ($LogText -notmatch "(?m)^\s*CorporateMemo\s+#\d+\s+\(2/") {
        throw "$PhaseName inventory dump did not contain CorporateMemo amount 2."
    }
}

$saveText = Invoke-GZDoomPhase -PhaseName "save" -CommandFile $SaveCommandPath -LogPath $SaveLog
Assert-InventoryState -LogText $saveText -PhaseName "Pre-save"

if (-not (Test-Path -LiteralPath $SaveFile)) {
    throw "GZDoom did not create the expected savegame: $SaveFile"
}
if ((Get-Item -LiteralPath $SaveFile).Length -lt 4096) {
    throw "GZDoom savegame is unexpectedly small; refusing to treat it as a valid runtime save."
}

$loadText = Invoke-GZDoomPhase -PhaseName "load" -CommandFile $LoadCommandPath -LogPath $LoadLog
Assert-InventoryState -LogText $loadText -PhaseName "Post-load"

@(
    "=== SAVE PHASE ===",
    (Get-Content -LiteralPath $SaveLog -Raw),
    "",
    "=== LOAD PHASE ===",
    (Get-Content -LiteralPath $LoadLog -Raw)
) | Set-Content -LiteralPath $CombinedLog -Encoding UTF8

Write-Host "GZDoom runtime save/load smoke test: PASS"
Write-Host "Verified real save -> process exit -> load with CheckoutFuse=2 and CorporateMemo=2 preserved."
Write-Host "Log: $CombinedLog"
