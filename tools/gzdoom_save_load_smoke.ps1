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
$SaveProcessLog = Join-Path $WorkDir "save-process.log"
$LoadProcessLog = Join-Path $WorkDir "load-process.log"
$SaveStateLog = Join-Path $WorkDir "save-state.log"
$LoadStateLog = Join-Path $WorkDir "load-state.log"
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

function Write-CombinedLog {
    $sections = @()
    if (Test-Path -LiteralPath $SaveProcessLog) {
        $sections += "=== SAVE PROCESS ==="
        $sections += (Get-Content -LiteralPath $SaveProcessLog -Raw)
    }
    if (Test-Path -LiteralPath $SaveStateLog) {
        $sections += "=== SAVE ENGINE LOG ==="
        $sections += (Get-Content -LiteralPath $SaveStateLog -Raw)
    }
    if (Test-Path -LiteralPath $LoadProcessLog) {
        $sections += "=== LOAD PROCESS ==="
        $sections += (Get-Content -LiteralPath $LoadProcessLog -Raw)
    }
    if (Test-Path -LiteralPath $LoadStateLog) {
        $sections += "=== LOAD ENGINE LOG ==="
        $sections += (Get-Content -LiteralPath $LoadStateLog -Raw)
    }
    if ($sections.Count -gt 0) {
        $sections | Set-Content -LiteralPath $CombinedLog -Encoding UTF8
    }
}

function ConvertTo-ProcessArgument([string]$Value) {
    if ($Value.Contains('"')) {
        throw "Runtime smoke argument contains an unsupported quote: $Value"
    }
    if ($Value -match "\s") {
        return '"' + $Value + '"'
    }
    return $Value
}

function Invoke-GZDoomPhase(
    [string]$PhaseName,
    [string]$CommandFile,
    [string]$ProcessLog,
    [string]$StateLog
) {
    foreach ($log in @($ProcessLog, $StateLog)) {
        if (Test-Path -LiteralPath $log) {
            Remove-Item -LiteralPath $log -Force
        }
    }

    $stdoutLog = "$ProcessLog.stdout"
    $stderrLog = "$ProcessLog.stderr"
    foreach ($log in @($stdoutLog, $stderrLog)) {
        if (Test-Path -LiteralPath $log) {
            Remove-Item -LiteralPath $log -Force
        }
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
        "+vid_activeinbackground", "true",
        "+i_pauseinbackground", "false",
        "+logfile", $StateLog,
        "+exec", $CommandFile
    )
    $argumentLine = ($arguments | ForEach-Object { ConvertTo-ProcessArgument "$_" }) -join " "

    Write-Host "Running GZDoom $PhaseName phase..."
    # GZDoom is a Windows GUI executable. A direct PowerShell invocation can return
    # before the game process exits, so explicitly wait for the real engine process.
    # Hosted CI has no focused game window: keep rendering/ticks active and disable
    # background pausing so delayed save/load assertions and quickexit can advance.
    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $argumentLine `
        -PassThru `
        -Wait `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog
    $exitCode = $process.ExitCode

    $outputLines = @()
    if (Test-Path -LiteralPath $stdoutLog) {
        $outputLines += Get-Content -LiteralPath $stdoutLog
    }
    if (Test-Path -LiteralPath $stderrLog) {
        $outputLines += Get-Content -LiteralPath $stderrLog
    }
    if ($outputLines.Count -gt 0) {
        $outputLines | Set-Content -LiteralPath $ProcessLog -Encoding UTF8
        $outputLines | ForEach-Object { Write-Host $_ }
    }
    else {
        "GZDoom $PhaseName phase completed with no redirected stdout/stderr. Exit code: $exitCode" |
            Set-Content -LiteralPath $ProcessLog -Encoding UTF8
    }

    Write-CombinedLog

    if ($exitCode -ne 0) {
        throw "GZDoom $PhaseName phase failed with exit code $exitCode. See $CombinedLog"
    }
    if (-not (Test-Path -LiteralPath $StateLog)) {
        throw "GZDoom $PhaseName phase did not create its engine logfile. See $CombinedLog"
    }

    $processText = Get-Content -LiteralPath $ProcessLog -Raw
    $stateText = Get-Content -LiteralPath $StateLog -Raw
    $allText = "$processText`n$stateText"
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
        if ($allText -match [regex]::Escape($pattern)) {
            throw "GZDoom reported '$pattern' during the $PhaseName phase. See $CombinedLog"
        }
    }

    return $stateText
}

function Assert-InventoryState([string]$LogText, [string]$PhaseName) {
    if ($LogText -notmatch "(?m)^\s*CheckoutFuse\s+#\d+\s+\(2/") {
        throw "$PhaseName inventory dump did not contain CheckoutFuse amount 2. See $CombinedLog"
    }
    if ($LogText -notmatch "(?m)^\s*CorporateMemo\s+#\d+\s+\(2/") {
        throw "$PhaseName inventory dump did not contain CorporateMemo amount 2. See $CombinedLog"
    }
}

$saveText = Invoke-GZDoomPhase -PhaseName "save" -CommandFile $SaveCommandPath -ProcessLog $SaveProcessLog -StateLog $SaveStateLog
Assert-InventoryState -LogText $saveText -PhaseName "Pre-save"

if (-not (Test-Path -LiteralPath $SaveFile)) {
    throw "GZDoom did not create the expected savegame: $SaveFile"
}
if ((Get-Item -LiteralPath $SaveFile).Length -lt 4096) {
    throw "GZDoom savegame is unexpectedly small; refusing to treat it as a valid runtime save."
}

$loadText = Invoke-GZDoomPhase -PhaseName "load" -CommandFile $LoadCommandPath -ProcessLog $LoadProcessLog -StateLog $LoadStateLog
Write-CombinedLog
Assert-InventoryState -LogText $loadText -PhaseName "Post-load"

Write-Host "GZDoom runtime save/load smoke test: PASS"
Write-Host "Verified real save -> process exit -> load with CheckoutFuse=2 and CorporateMemo=2 preserved."
Write-Host "Log: $CombinedLog"
