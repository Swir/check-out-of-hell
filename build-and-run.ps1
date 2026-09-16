$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& "$PSScriptRoot\tools\bootstrap_runtime.ps1"

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $pythonExe = $python.Source
}
else {
    & "$PSScriptRoot\tools\bootstrap_python.ps1"
    $pythonExe = "$PSScriptRoot\tools\runtime\python\python.exe"
}

& $pythonExe tools\build.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $pythonExe tools\smoke_test.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$gzdoom = Join-Path $PSScriptRoot "external\gzdoom\gzdoom.exe"
$iwad = Join-Path $PSScriptRoot "external\freedoom2.wad"
$pk3 = Join-Path $PSScriptRoot "dist\checkout-of-hell-prototype.pk3"

Start-Process -FilePath $gzdoom -ArgumentList @("-iwad", $iwad, "-file", $pk3, "+map", "MAP01")
