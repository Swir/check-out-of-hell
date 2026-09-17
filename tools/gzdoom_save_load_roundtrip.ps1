[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$RoundtripRoot = Join-Path $ProjectRoot "dist\save-load-roundtrip"
$SaveDir = Join-Path $RoundtripRoot "saves"
$IniPath = Join-Path $RoundtripRoot "gzdoom-ci.ini"
$CommandPath = Join-Path $RoundtripRoot "roundtrip.cfg"
$SaveLog = Join-Path $RoundtripRoot "save-phase.log"
$LoadLog = Join-Path $RoundtripRoot "load-phase.log"

function Assert-RuntimeLog {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Phase
    )

    $errorPatterns = @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Unknown command",
        "Invalid parameter",
        "Parse error",
        "Cannot find savegame",
        "Savegame is from a different version",
        "Savegame is incompatible"
    )

    foreach ($pattern in $errorPatterns) {
        if ($Text -match [regex]::Escape($pattern)) {
            throw "GZDoom $Phase phase reported '$pattern'."
        }
    }
}

function ConvertTo-ProcessArgument {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    # Start-Process joins ArgumentList entries into a command line on Windows.
    # Quote paths/descriptions containing whitespace and escape embedded quotes.
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Invoke-RoundtripPhase {
    param(
        [Parameter(Mandatory = $true)][string]$Commands,
        [Parameter(Mandatory = $true)][string]$LogPath,
        [Parameter(Mandatory = $true)][string]$Phase
    )

    Set-Content -LiteralPath $CommandPath -Value $Commands -Encoding ASCII

    $arguments = @(
        "-stdout",
        "-window",
        "-nosound",
        "-nomusic",
        "-noautoload",
        "-config", $IniPath,
        "-savedir", $SaveDir,
        "-iwad", $FreedoomWad,
        "-file", $Pk3,
        "+i_pauseinbackground", "0",
        "+exec", $CommandPath
    )

    # GZDoom is a Windows GUI-subsystem executable. A direct PowerShell invocation
    # can return as soon as the process is launched, so explicitly wait for it.
    $stdoutPath = "$LogPath.stdout"
    $stderrPath = "$LogPath.stderr"
    foreach ($temporary in @($stdoutPath, $stderrPath, $LogPath)) {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }

    $argumentLine = (($arguments | ForEach-Object { ConvertTo-ProcessArgument "$_" }) -join " ")
    Write-Host "Running GZDoom $Phase phase..."
    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $argumentLine `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru `
        -Wait

    $combined = @()
    if (Test-Path -LiteralPath $stdoutPath) {
        $combined += @(Get-Content -LiteralPath $stdoutPath)
    }
    if (Test-Path -LiteralPath $stderrPath) {
        $combined += @(Get-Content -LiteralPath $stderrPath)
    }

    if ($combined.Count -gt 0) {
        $combined | Set-Content -LiteralPath $LogPath -Encoding UTF8
        $combined | ForEach-Object { Write-Host $_ }
    }
    else {
        "GZDoom $Phase phase completed with no stdout/stderr. Exit code: $($process.ExitCode)" |
            Set-Content -LiteralPath $LogPath -Encoding UTF8
    }

    if ($process.ExitCode -ne 0) {
        throw "GZDoom $Phase phase failed with exit code $($process.ExitCode). See $LogPath"
    }

    $text = Get-Content -LiteralPath $LogPath -Raw
    Assert-RuntimeLog -Text $text -Phase $Phase
    return $text
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
        throw "Save/load prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $RoundtripRoot) {
    Remove-Item -LiteralPath $RoundtripRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $SaveDir -Force | Out-Null

# Put the player into a meaningful mid-objective state before saving. The one-line
# command chain uses GZDoom's built-in `wait` command so map startup and networked
# give commands have time to settle before the save is written.
$saveCommands = 'map MAP01; wait 105; sv_cheats 1; give CheckoutFuse 2; give CorporateMemo 1; wait 8; printinv; save coh_ci_roundtrip "COH CI roundtrip"; wait 70; quit'
$saveText = Invoke-RoundtripPhase -Commands $saveCommands -LogPath $SaveLog -Phase "save"

$saveFiles = @(Get-ChildItem -LiteralPath $SaveDir -Filter "coh_ci_roundtrip.zds" -File -Recurse)
if ($saveFiles.Count -ne 1) {
    throw "Expected exactly one coh_ci_roundtrip.zds save, found $($saveFiles.Count)."
}
if ($saveFiles[0].Length -lt 4096) {
    throw "Roundtrip save looks unexpectedly small: $($saveFiles[0].Length) bytes."
}

# The pre-save inventory snapshot proves that the save was taken after the intended
# objective state was established rather than during startup.
if ($saveText -notmatch 'CheckoutFuse #[0-9]+ \(2/3\)') {
    throw "Pre-save inventory did not contain CheckoutFuse 2/3."
}
if ($saveText -notmatch 'CorporateMemo #[0-9]+ \(1/3\)') {
    throw "Pre-save inventory did not contain CorporateMemo 1/3."
}

# Load the exact slot in a fresh GZDoom process, then ask the engine itself to print
# the restored inventory. This catches package/load incompatibilities and verifies
# that objective progress survives a real process-to-process save/load roundtrip.
$loadCommands = 'load coh_ci_roundtrip; wait 105; printinv; wait 8; quit'
$loadText = Invoke-RoundtripPhase -Commands $loadCommands -LogPath $LoadLog -Phase "load"

if ($loadText -notmatch 'CheckoutFuse #[0-9]+ \(2/3\)') {
    throw "Loaded inventory did not restore CheckoutFuse 2/3."
}
if ($loadText -notmatch 'CorporateMemo #[0-9]+ \(1/3\)') {
    throw "Loaded inventory did not restore CorporateMemo 1/3."
}

Write-Host "GZDoom save/load roundtrip: PASS"
Write-Host "Verified save: $($saveFiles[0].FullName)"
