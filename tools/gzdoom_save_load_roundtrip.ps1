[CmdletBinding()]
param(
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$WorkDir = Join-Path $ProjectRoot "dist\save-load-roundtrip"
$SaveDir = Join-Path $WorkDir "saves"
$ConfigPath = Join-Path $WorkDir "gzdoom-ci.ini"
$CreateCfg = Join-Path $WorkDir "create-save.cfg"
$LoadCfg = Join-Path $WorkDir "load-save.cfg"
$CreateLog = Join-Path $WorkDir "create-save.log"
$LoadLog = Join-Path $WorkDir "load-save.log"

function Quote-ProcessArgument([string]$Value)
{
    if ($Value -notmatch '[\s"]')
    {
        return $Value
    }

    return '"' + $Value.Replace('"', '\"') + '"'
}

function Write-CombinedLog
{
    param(
        [string]$StdoutPath,
        [string]$StderrPath,
        [string]$LogPath,
        [string]$Fallback
    )

    $output = @()
    if (Test-Path -LiteralPath $StdoutPath)
    {
        $output += Get-Content -LiteralPath $StdoutPath
    }
    if (Test-Path -LiteralPath $StderrPath)
    {
        $output += Get-Content -LiteralPath $StderrPath
    }
    if ($output.Count -eq 0)
    {
        $output = @($Fallback)
    }

    $output | Set-Content -LiteralPath $LogPath -Encoding UTF8
    return $output
}

function Invoke-GZDoomChecked
{
    param(
        [string]$Phase,
        [string[]]$Arguments,
        [string]$LogPath
    )

    $stdoutPath = "$LogPath.stdout"
    $stderrPath = "$LogPath.stderr"
    foreach ($path in @($stdoutPath, $stderrPath, $LogPath))
    {
        if (Test-Path -LiteralPath $path)
        {
            Remove-Item -LiteralPath $path -Force
        }
    }

    $argumentLine = ($Arguments | ForEach-Object { Quote-ProcessArgument $_ }) -join ' '
    Write-Host "Running GZDoom $Phase phase..."
    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $argumentLine `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath

    if (-not $process.WaitForExit($TimeoutSeconds * 1000))
    {
        try { $process.Kill() } catch { }
        try { $process.WaitForExit(5000) | Out-Null } catch { }
        $timeoutOutput = Write-CombinedLog `
            -StdoutPath $stdoutPath `
            -StderrPath $stderrPath `
            -LogPath $LogPath `
            -Fallback "GZDoom $Phase phase timed out without redirected output."
        $timeoutOutput | ForEach-Object { Write-Host $_ }
        throw "GZDoom $Phase phase exceeded the ${TimeoutSeconds}s timeout. See $LogPath"
    }

    $output = Write-CombinedLog `
        -StdoutPath $stdoutPath `
        -StderrPath $stderrPath `
        -LogPath $LogPath `
        -Fallback "GZDoom $Phase phase completed with no redirected output."
    $output | ForEach-Object { Write-Host $_ }

    if ($process.ExitCode -ne 0)
    {
        throw "GZDoom $Phase phase failed with exit code $($process.ExitCode). See $LogPath"
    }

    $logText = Get-Content -LiteralPath $LogPath -Raw
    $errorPatterns = @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Unknown command",
        "Invalid parameter",
        "Parse error",
        "Could not save",
        "Could not load",
        "Savegame is from a different",
        "No such savegame",
        "File not found"
    )
    foreach ($pattern in $errorPatterns)
    {
        if ($logText -match [regex]::Escape($pattern))
        {
            throw "GZDoom reported '$pattern' during the $Phase phase."
        }
    }

    return $logText
}

Write-Host "Building current prototype..."
python (Join-Path $PSScriptRoot "build.py")
if ($LASTEXITCODE -ne 0)
{
    throw "Prototype build failed with exit code $LASTEXITCODE."
}

Write-Host "Resolving pinned official runtime..."
& (Join-Path $PSScriptRoot "bootstrap_runtime.ps1")
if ($LASTEXITCODE -ne 0)
{
    throw "Runtime bootstrap failed with exit code $LASTEXITCODE."
}

foreach ($required in @($GZDoomExe, $FreedoomWad, $Pk3))
{
    if (-not (Test-Path -LiteralPath $required))
    {
        throw "Save/load prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $WorkDir)
{
    Remove-Item -LiteralPath $WorkDir -Recurse -Force
}
New-Item -ItemType Directory -Path $SaveDir -Force | Out-Null

# GZDoom's `wait` defers only the remainder of the same command string.
# Keep each phase on one semicolon-delimited line so map startup, inventory
# injection, save I/O and quit happen on deterministic later tics instead of
# racing each other during initial console command dispatch.
'echo COH_SAVE_ROUNDTRIP_CREATE_BEGIN; map MAP01; wait 70; give CheckoutFuse; give CheckoutFuse; give CorporateMemo; wait 2; save coh-ci-roundtrip; wait 20; echo COH_SAVE_ROUNDTRIP_CREATE_DONE; quit' |
    Set-Content -LiteralPath $CreateCfg -Encoding ASCII

'echo COH_SAVE_ROUNDTRIP_LOAD_BEGIN; wait 70; echo COH_SAVE_ROUNDTRIP_LOAD_DONE; quit' |
    Set-Content -LiteralPath $LoadCfg -Encoding ASCII

$commonArgs = @(
    "-stdout",
    "-nosound",
    "-noautoload",
    "-iwad", $FreedoomWad,
    "-file", $Pk3,
    "-config", $ConfigPath,
    "-savedir", $SaveDir
)

$createArgs = $commonArgs + @(
    "-skill", "2",
    "+exec", $CreateCfg
)
$createText = Invoke-GZDoomChecked -Phase "save-create" -Arguments $createArgs -LogPath $CreateLog
if ($createText -notmatch "COH_SAVE_ROUNDTRIP_CREATE_DONE")
{
    throw "The save-create command sequence did not reach its completion sentinel."
}

$saveFiles = @(Get-ChildItem -LiteralPath $SaveDir -Recurse -File -Filter "*.zds")
if ($saveFiles.Count -ne 1)
{
    throw "Expected exactly one .zds save after create phase, found $($saveFiles.Count)."
}
$saveFile = $saveFiles[0]
if ($saveFile.Length -lt 4096)
{
    throw "Generated save is unexpectedly small: $($saveFile.Length) bytes."
}

$header = New-Object byte[] 2
$stream = [System.IO.File]::OpenRead($saveFile.FullName)
try
{
    if ($stream.Read($header, 0, 2) -ne 2 -or $header[0] -ne 0x50 -or $header[1] -ne 0x4B)
    {
        throw "Generated save does not have the expected ZIP-based ZDoom save header."
    }
}
finally
{
    $stream.Dispose()
}

Write-Host "Created save: $($saveFile.FullName) ($($saveFile.Length) bytes)"

$loadArgs = $commonArgs + @(
    "-loadgame", $saveFile.FullName,
    "+exec", $LoadCfg
)
$loadText = Invoke-GZDoomChecked -Phase "save-load" -Arguments $loadArgs -LogPath $LoadLog
if ($loadText -notmatch "COH_SAVE_ROUNDTRIP_LOAD_DONE")
{
    throw "The save-load command sequence did not reach its completion sentinel."
}

Write-Host "Pinned GZDoom save/load roundtrip: PASS"
