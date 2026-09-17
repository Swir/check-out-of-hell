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
$SaveConfig = Join-Path $WorkDir "save-roundtrip.cfg"
$LoadConfig = Join-Path $WorkDir "load-roundtrip.cfg"
$SaveEngineLog = Join-Path $WorkDir "save.engine.log"
$LoadEngineLog = Join-Path $WorkDir "load.engine.log"
$SaveStdout = Join-Path $WorkDir "save.stdout.log"
$SaveStderr = Join-Path $WorkDir "save.stderr.log"
$LoadStdout = Join-Path $WorkDir "load.stdout.log"
$LoadStderr = Join-Path $WorkDir "load.stderr.log"
$CombinedLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"
$SaveStem = "coh-ci-roundtrip"
$TimeoutSeconds = 55

function Read-TextIfPresent {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return ""
    }
    try {
        return Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
    }
    catch {
        return ""
    }
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
        "Cannot find savegame",
        "No map MAP01",
        "Not in a saveable game",
        "Player is dead in a single-player game"
    )

    foreach ($pattern in $errorPatterns) {
        if ($Text -match [regex]::Escape($pattern)) {
            throw "$Label reported '$pattern'."
        }
    }
}

function Stop-RuntimeProcess {
    param([Parameter(Mandatory = $true)]$Process)
    if ($Process.HasExited) {
        return
    }

    try {
        Stop-Process -Id $Process.Id -Force -ErrorAction Stop
    }
    catch {
        try { $Process.Kill() } catch { }
    }
    try { $Process.WaitForExit(5000) | Out-Null } catch { }
}

function Invoke-RuntimePhase {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$EngineLog,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][string]$Sentinel
    )

    foreach ($path in @($EngineLog, $StdoutPath, $StderrPath)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }

    $phaseArguments = $Arguments + @("+logfile", $EngineLog)
    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $phaseArguments `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -PassThru

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $sentinelSeen = $false
    try {
        while ([DateTime]::UtcNow -lt $deadline) {
            $engineText = Read-TextIfPresent -Path $EngineLog
            $stdoutText = Read-TextIfPresent -Path $StdoutPath
            $stderrText = Read-TextIfPresent -Path $StderrPath
            $combinedText = "$engineText`n$stdoutText`n$stderrText"
            Assert-NoRuntimeErrors -Text $combinedText -Label $Label

            if ($combinedText -match [regex]::Escape($Sentinel)) {
                $sentinelSeen = $true
                break
            }

            if ($process.HasExited) {
                throw "$Label exited before reaching sentinel '$Sentinel' (exit code $($process.ExitCode))."
            }
            Start-Sleep -Milliseconds 250
        }

        if (-not $sentinelSeen) {
            throw "$Label timed out after $TimeoutSeconds seconds before sentinel '$Sentinel'."
        }
    }
    finally {
        Stop-RuntimeProcess -Process $process
    }

    $engineText = Read-TextIfPresent -Path $EngineLog
    $stdoutText = Read-TextIfPresent -Path $StdoutPath
    $stderrText = Read-TextIfPresent -Path $StderrPath
    $combinedText = "$engineText`n$stdoutText`n$stderrText"
    Assert-NoRuntimeErrors -Text $combinedText -Label $Label
    return $combinedText
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
        $Result
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

@(
    "[GlobalSettings]",
    "vid_preferbackend=1",
    "vid_fullscreen=false",
    "vid_lowerinbackground=false",
    "vid_activeinbackground=true",
    "i_pauseinbackground=false",
    "i_soundinbackground=false"
) | Set-Content -LiteralPath $EngineConfig -Encoding ASCII

# Start directly in MAP01 so the authored 2/3 objective state is applied in the
# live playsim rather than being discarded by a deferred map transition. God mode
# prevents an unattended target-machine validation run from dying before the save.
$saveCommands = "wait 10; god; give CheckoutFuse; give CheckoutFuse; give CorporateMemo; give CorporateMemo; wait 10; printinv; save $SaveStem `"CHECKOUT OF HELL CI ROUNDTRIP`"; wait 20; echo COH_RUNTIME_SAVE_WRITTEN"
$loadCommands = "wait 10; printinv; echo COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE"
Set-Content -LiteralPath $SaveConfig -Value $saveCommands -Encoding ASCII
Set-Content -LiteralPath $LoadConfig -Value $loadCommands -Encoding ASCII

$commonArguments = @(
    "-stdout",
    "-nosound",
    "-config", $EngineConfig,
    "-iwad", $FreedoomWad,
    "-file", $Pk3,
    "-savedir", $SaveDir
)

$saveText = ""
$loadText = ""
try {
    Write-Host "Runtime pass 1/2: start MAP01, author objective state and write a real savegame..."
    $saveArguments = $commonArguments + @(
        "+map", "MAP01",
        "+exec", $SaveConfig
    )
    $saveText = Invoke-RuntimePhase `
        -Label "GZDoom save pass" `
        -Arguments $saveArguments `
        -EngineLog $SaveEngineLog `
        -StdoutPath $SaveStdout `
        -StderrPath $SaveStderr `
        -Sentinel "COH_RUNTIME_SAVE_WRITTEN"

    if ($saveText -notmatch "CheckoutFuse\s+#\d+\s+\(2/3\)") {
        throw "Save pass did not expose CheckoutFuse 2/3 before saving."
    }
    if ($saveText -notmatch "CorporateMemo\s+#\d+\s+\(2/3\)") {
        throw "Save pass did not expose CorporateMemo 2/3 before saving."
    }

    $saveFile = Get-ChildItem -LiteralPath $SaveDir -Filter "$SaveStem*.zds" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $saveFile) {
        throw "GZDoom did not create a $SaveStem savegame in $SaveDir."
    }
    if ($saveFile.Length -lt 4096) {
        throw "GZDoom savegame is unexpectedly small ($($saveFile.Length) bytes)."
    }

    $sizeBefore = $saveFile.Length
    Start-Sleep -Milliseconds 500
    $saveFile.Refresh()
    if ($saveFile.Length -ne $sizeBefore) {
        Start-Sleep -Milliseconds 500
        $saveFile.Refresh()
    }
    if ($saveFile.Length -lt 4096) {
        throw "GZDoom savegame became invalid after the save process exited."
    }

    Write-Host "Runtime pass 2/2: launch a new GZDoom process, restore the save and verify objective state..."
    $loadArguments = $commonArguments + @(
        "-loadgame", $saveFile.Name,
        "+exec", $LoadConfig
    )
    $loadText = Invoke-RuntimePhase `
        -Label "GZDoom load pass" `
        -Arguments $loadArguments `
        -EngineLog $LoadEngineLog `
        -StdoutPath $LoadStdout `
        -StderrPath $LoadStderr `
        -Sentinel "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE"

    if ($loadText -notmatch "CheckoutFuse\s+#\d+\s+\(2/3\)") {
        throw "CheckoutFuse 2/3 did not survive the real save -> process exit -> load round-trip."
    }
    if ($loadText -notmatch "CorporateMemo\s+#\d+\s+\(2/3\)") {
        throw "CorporateMemo 2/3 did not survive the real save -> process exit -> load round-trip."
    }

    Write-CombinedLog -SaveText $saveText -LoadText $loadText -Result "PASS: CheckoutFuse 2/3 and CorporateMemo 2/3 survived a real GZDoom save -> process exit -> load round-trip."
    Write-Host "GZDoom runtime save/load round-trip: PASS"
}
catch {
    Write-CombinedLog -SaveText $saveText -LoadText $loadText -Result "FAIL: $($_.Exception.Message)"
    throw
}
