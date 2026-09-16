[CmdletBinding()]
param(
    [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoom = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$Freedoom = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"

foreach ($required in @($GZDoom, $Freedoom, $Pk3)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Runtime validation prerequisite is missing: $required"
    }
}

# GZDoom implements -norun specifically for startup/batch validation. It loads
# the IWAD/mod resources and parses game definitions, then exits before entering
# the interactive game loop. This avoids false CI hangs caused by trying to run
# a graphical game session on a hosted Windows runner while still exercising the
# real pinned GZDoom executable against our PK3.
$arguments = @(
    "-iwad", $Freedoom,
    "-file", $Pk3,
    "-noautoload",
    "-nosound",
    "-nomusic",
    "-stdout",
    "-norun"
)

Write-Host "Starting pinned GZDoom startup/parser validation..."
$process = Start-Process -FilePath $GZDoom -ArgumentList $arguments -PassThru -Wait

if ($process.ExitCode -ne 0) {
    throw "GZDoom startup/parser validation failed with exit code $($process.ExitCode)."
}

Write-Host "GZDoom startup/parser validation: PASS"
