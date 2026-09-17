[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$WorkDir = Join-Path $ProjectRoot "dist\save-load-runtime"
$SaveDir = Join-Path $WorkDir "saves"
$EngineConfig = Join-Path $WorkDir "gzdoom-ci.ini"
$SaveStdout = Join-Path $WorkDir "save.stdout.log"
$SaveStderr = Join-Path $WorkDir "save.stderr.log"
$LoadStdout = Join-Path $WorkDir "load.stdout.log"
$LoadStderr = Join-Path $WorkDir "load.stderr.log"
$CombinedLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"
$SaveStem = "coh-ci-roundtrip"
$SaveFile = Join-Path $SaveDir "$SaveStem.zds"
$TimeoutSeconds = 25

function Invoke-GZDoomRoundTripProcess {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][string]$Label
    )

    foreach ($path in @($StdoutPath, $StderrPath)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }

    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $Arguments `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -PassThru

    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        try { $process.Kill() } catch { }
        try { $process.WaitForExit(5000) | Out-Null } catch { }
        throw "$Label timed out after $TimeoutSeconds seconds."
    }

    if ($process.ExitCode -ne 0) {
        throw "$Label failed with exit code $($process.ExitCode)."
    }
}

function Read-CombinedProcessLog {
    param(
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath
    )

    $parts = @()
    if (Test-Path -LiteralPath $StdoutPath) {
        $parts += Get-Content -LiteralPath $StdoutPath -Raw
    }
    if (Test-Path -LiteralPath $StderrPath) {
        $parts += Get-Content -LiteralPath $StderrPath -Raw
    }
    return ($parts -join "`n")
}

function Assert-NoRuntimeErrors {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $errorPatterns = @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Invalid parameter",
        "Parse error",
        "Unknown command",
        "Cannot load savegame",
        "Savegame is from a different",
        "Could not open savegame",
        "Cannot find savegame"
    )

    foreach ($pattern in $errorPatterns) {
        if ($Text -match [regex]::Escape($pattern)) {
            throw "$Label reported '$pattern'."
        }
    }
}

function Write-CombinedLog {
    param(
        [string]$SaveText = "",
        [string]$LoadText = "",
        [string]$Result = "INCOMPLETE"
    )

    @(
        "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke",
        "",
        "=== SAVE PASS ===",
        $SaveText,
        "",
        "=== LOAD PASS ===",
        $LoadText,
        "",
        "RESULT: $Result"
    ) -join "`n" | Set-Content -LiteralPath $CombinedLog -Encoding UTF8
}

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

# Hosted Windows runners do not provide a focused game window. Force the mature
# OpenGL path and keep background ticking enabled. The actual round-trip commands
# are passed as startup console commands instead of a delayed exec/wait script:
# `map` completes level setup synchronously before the following give/save commands,
# avoiding the old CI deadlock where a queued wait never reached quit.
@(
    "[GlobalSettings]",
    "vid_preferbackend=0",
    "vid_fullscreen=false",
    "i_pauseinbackground=false",
    "i_soundinbackground=false",
    "storesavepic=false"
) | Set-Content -LiteralPath $EngineConfig -Encoding ASCII

$commonArguments = @(
    "-stdout",
    "-nosound",
    "-noautoload",
    "-config", $EngineConfig,
    "-iwad", $FreedoomWad,
    "-file", $Pk3,
    "-savedir", $SaveDir
)

Write-Host "Runtime pass 1/2: start MAP01, author unmistakable objective state, save, then quit..."
$saveArguments = $commonArguments + @(
    "+map", "MAP01",
    "+give", "CheckoutFuse", "2",
    "+printinv",
    "+save", $SaveStem,
    "+echo", "COH_RUNTIME_SAVE_WRITTEN",
    "+quit"
)

$saveText = ""
$loadText = ""
try {
    Invoke-GZDoomRoundTripProcess -Arguments $saveArguments -StdoutPath $SaveStdout -StderrPath $SaveStderr -Label "GZDoom save pass"
    $saveText = Read-CombinedProcessLog -StdoutPath $SaveStdout -StderrPath $SaveStderr
    Assert-NoRuntimeErrors -Text $saveText -Label "GZDoom save pass"
    Write-CombinedLog -SaveText $saveText -Result "SAVE PASS COMPLETE"

    if ($saveText -notmatch "COH_RUNTIME_SAVE_WRITTEN") {
        throw "Save pass did not reach its completion sentinel."
    }
    if ($saveText -notmatch "CheckoutFuse\s+#\d+\s+\(2/3\)") {
        throw "Save pass did not expose the expected CheckoutFuse 2/3 state before saving."
    }
    if (-not (Test-Path -LiteralPath $SaveFile)) {
        throw "GZDoom did not create the expected savegame: $SaveFile"
    }
    if ((Get-Item -LiteralPath $SaveFile).Length -lt 4096) {
        throw "GZDoom savegame is unexpectedly small; refusing to accept an invalid round-trip fixture."
    }

    Write-Host "Runtime pass 2/2: cross the process boundary, reload the savegame, verify state, then quit..."
    $loadArguments = $commonArguments + @(
        "-loadgame", $SaveFile,
        "+printinv",
        "+echo", "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
        "+quit"
    )

    Invoke-GZDoomRoundTripProcess -Arguments $loadArguments -StdoutPath $LoadStdout -StderrPath $LoadStderr -Label "GZDoom load pass"
    $loadText = Read-CombinedProcessLog -StdoutPath $LoadStdout -StderrPath $LoadStderr
    Assert-NoRuntimeErrors -Text $loadText -Label "GZDoom load pass"

    if ($loadText -notmatch "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE") {
        throw "Load pass did not reach its completion sentinel."
    }
    if ($loadText -notmatch "CheckoutFuse\s+#\d+\s+\(2/3\)") {
        throw "CheckoutFuse 2/3 did not survive the real save -> process exit -> load round-trip."
    }

    Write-CombinedLog -SaveText $saveText -LoadText $loadText -Result "PASS - CheckoutFuse 2/3 survived save -> process exit -> load"
    Write-Host "GZDoom runtime save/load round-trip: PASS"
}
catch {
    if (-not $saveText) {
        $saveText = Read-CombinedProcessLog -StdoutPath $SaveStdout -StderrPath $SaveStderr
    }
    if (-not $loadText) {
        $loadText = Read-CombinedProcessLog -StdoutPath $LoadStdout -StderrPath $LoadStderr
    }
    Write-CombinedLog -SaveText $saveText -LoadText $loadText -Result "FAIL - $($_.Exception.Message)"
    throw
}
