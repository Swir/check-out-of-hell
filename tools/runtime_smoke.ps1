[CmdletBinding()]
param(
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoom = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$Freedoom = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$LogPath = Join-Path $ProjectRoot "dist\gzdoom-runtime-validation.log"
$StdoutPath = Join-Path $ProjectRoot "dist\gzdoom-runtime-stdout.log"
$StderrPath = Join-Path $ProjectRoot "dist\gzdoom-runtime-stderr.log"

foreach ($required in @($GZDoom, $Freedoom, $Pk3)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Runtime validation prerequisite is missing: $required"
    }
}

foreach ($oldLog in @($LogPath, $StdoutPath, $StderrPath)) {
    if (Test-Path -LiteralPath $oldLog) {
        Remove-Item -LiteralPath $oldLog -Force
    }
}

# GZDoom implements -norun specifically for startup/batch validation. It loads
# the IWAD/mod resources and parses game definitions, then exits before entering
# the interactive game loop. This exercises the real pinned GZDoom executable
# without pretending that a hosted CI runner is an interactive playtest machine.
$arguments = @(
    "-iwad", $Freedoom,
    "-file", $Pk3,
    "-noautoload",
    "-nosound",
    "-nomusic",
    "-stdout",
    "+logfile", $LogPath,
    "-norun"
)

function Show-Diagnostics {
    foreach ($path in @($LogPath, $StdoutPath, $StderrPath)) {
        if (Test-Path -LiteralPath $path) {
            Write-Host "----- $([System.IO.Path]::GetFileName($path)) -----"
            Get-Content -LiteralPath $path -ErrorAction SilentlyContinue | Select-Object -Last 200 | Write-Host
        }
    }
}

Write-Host "Starting pinned GZDoom startup/parser validation..."
$process = Start-Process `
    -FilePath $GZDoom `
    -ArgumentList $arguments `
    -RedirectStandardOutput $StdoutPath `
    -RedirectStandardError $StderrPath `
    -PassThru

if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
    try { $process.Kill() } catch { }
    Show-Diagnostics
    throw "GZDoom did not finish -norun validation within $TimeoutSeconds seconds."
}

Show-Diagnostics
if ($process.ExitCode -ne 0) {
    throw "GZDoom startup/parser validation failed with exit code $($process.ExitCode)."
}

Write-Host "GZDoom startup/parser validation: PASS"
