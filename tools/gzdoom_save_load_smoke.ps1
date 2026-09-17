[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$WorkDir = Join-Path $ProjectRoot "dist\save-load-runtime"
$SaveDir = Join-Path $WorkDir "saves"
$SaveConfig = Join-Path $WorkDir "save-roundtrip.cfg"
$LoadConfig = Join-Path $WorkDir "load-roundtrip.cfg"
$SaveStdout = Join-Path $WorkDir "save.stdout.log"
$SaveStderr = Join-Path $WorkDir "save.stderr.log"
$LoadStdout = Join-Path $WorkDir "load.stdout.log"
$LoadStderr = Join-Path $WorkDir "load.stderr.log"
$CombinedLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"
$SaveStem = "coh-ci-roundtrip"
$TimeoutSeconds = 90

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
        "Cannot load savegame",
        "Savegame is from a different",
        "Could not open savegame"
    )

    foreach ($pattern in $errorPatterns) {
        if ($Text -match [regex]::Escape($pattern)) {
            throw "$Label reported '$pattern'."
        }
    }
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

# Commands after wait remain in one command string so GZDoom's delayed-command
# queue advances only after MAP01 is live. We deliberately save two Breaker Fuses:
# a fresh-world reset would erase them, while a genuine save restore must preserve them.
$saveCommands = "wait 175; give CheckoutFuse 2; wait 10; printinv; save $SaveStem \"CHECKOUT OF HELL CI ROUNDTRIP\"; wait 70; echo COH_RUNTIME_SAVE_WRITTEN; quit"
$loadCommands = "wait 175; printinv; echo COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE; wait 10; quit"
Set-Content -LiteralPath $SaveConfig -Value $saveCommands -Encoding ASCII
Set-Content -LiteralPath $LoadConfig -Value $loadCommands -Encoding ASCII

$commonArguments = @(
    "-stdout",
    "-nosound",
    "-iwad", $FreedoomWad,
    "-file", $Pk3,
    "-savedir", $SaveDir
)

Write-Host "Runtime pass 1/2: start MAP01, mutate state and write a savegame..."
$saveArguments = $commonArguments + @(
    "+map", "MAP01",
    "+exec", $SaveConfig
)
Invoke-GZDoomRoundTripProcess -Arguments $saveArguments -StdoutPath $SaveStdout -StderrPath $SaveStderr -Label "GZDoom save pass"
$saveLog = Read-CombinedProcessLog -StdoutPath $SaveStdout -StderrPath $SaveStderr
Assert-NoRuntimeErrors -Text $saveLog -Label "GZDoom save pass"

if ($saveLog -notmatch "COH_RUNTIME_SAVE_WRITTEN") {
    throw "Save pass did not reach its completion sentinel."
}
if ($saveLog -notmatch "CheckoutFuse\s+#\d+\s+\(2/3\)") {
    throw "Save pass did not expose the expected CheckoutFuse 2/3 state before saving."
}

$saveFile = Get-ChildItem -LiteralPath $SaveDir -Filter "$SaveStem*.zds" -File -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $saveFile -or $saveFile.Length -le 0) {
    throw "GZDoom did not create a non-empty $SaveStem savegame in $SaveDir."
}

Write-Host "Runtime pass 2/2: quit boundary, reload the savegame and verify serialized objective state..."
$loadArguments = $commonArguments + @(
    "-loadgame", $SaveStem,
    "+exec", $LoadConfig
)
Invoke-GZDoomRoundTripProcess -Arguments $loadArguments -StdoutPath $LoadStdout -StderrPath $LoadStderr -Label "GZDoom load pass"
$loadLog = Read-CombinedProcessLog -StdoutPath $LoadStdout -StderrPath $LoadStderr
Assert-NoRuntimeErrors -Text $loadLog -Label "GZDoom load pass"

if ($loadLog -notmatch "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE") {
    throw "Load pass did not reach its completion sentinel."
}
if ($loadLog -notmatch "CheckoutFuse\s+#\d+\s+\(2/3\)") {
    throw "CheckoutFuse 2/3 did not survive the real save -> quit -> load round-trip."
}

$combined = @(
    "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke",
    "",
    "=== SAVE PASS ===",
    $saveLog,
    "",
    "=== LOAD PASS ===",
    $loadLog,
    "",
    "PASS: CheckoutFuse 2/3 survived a real GZDoom save -> process exit -> load round-trip."
) -join "`n"
$combined | Set-Content -LiteralPath $CombinedLog -Encoding UTF8

Write-Host "GZDoom runtime save/load round-trip: PASS"
