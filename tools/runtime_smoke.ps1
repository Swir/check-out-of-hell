[CmdletBinding()]
param(
    [int]$TimeoutSeconds = 45,
    [string]$Map = "MAP01"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoom = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$Freedoom = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"

foreach ($required in @($GZDoom, $Freedoom, $Pk3)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Runtime smoke test prerequisite is missing: $required"
    }
}

# +quit is processed only after GZDoom has initialized its game definitions,
# which makes this a useful parser/startup smoke test without requiring a human
# to interact with the game window in CI.
$arguments = @(
    "-iwad", $Freedoom,
    "-file", $Pk3,
    "-nosound",
    "-nomusic",
    "+map", $Map,
    "+quit"
)

Write-Host "Starting GZDoom runtime smoke test for $Map..."
$process = Start-Process -FilePath $GZDoom -ArgumentList $arguments -PassThru
if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
    try { $process.Kill() } catch { }
    throw "GZDoom did not finish the smoke test within $TimeoutSeconds seconds."
}

if ($process.ExitCode -ne 0) {
    throw "GZDoom startup smoke test failed with exit code $($process.ExitCode)."
}

Write-Host "GZDoom runtime smoke test: PASS ($Map)"
