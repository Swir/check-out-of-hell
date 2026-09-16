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

# GZDoom's -errorlog option enables its own batchrun path. Combined with
# -norun, the engine loads the IWAD and our PK3, parses definitions and performs
# startup initialization, but deliberately avoids entering the graphical game
# loop. Upstream returns the special process code 1337 for a successful norun
# batch exit, so CI treats 1337 as success rather than masking it as an error.
$arguments = @(
    "-iwad", $Freedoom,
    "-file", $Pk3,
    "-noautoload",
    "-nosound",
    "-nomusic",
    "-errorlog", $LogPath,
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

Write-Host "Starting pinned GZDoom batch startup/parser validation..."
$process = Start-Process `
    -FilePath $GZDoom `
    -ArgumentList $arguments `
    -RedirectStandardOutput $StdoutPath `
    -RedirectStandardError $StderrPath `
    -PassThru

if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
    try { $process.Kill() } catch { }
    Show-Diagnostics
    throw "GZDoom did not finish batch -norun validation within $TimeoutSeconds seconds."
}

Show-Diagnostics
if ($process.ExitCode -ne 0 -and $process.ExitCode -ne 1337) {
    throw "GZDoom startup/parser validation failed with exit code $($process.ExitCode)."
}

Write-Host "GZDoom startup/parser validation: PASS (exit $($process.ExitCode))"
