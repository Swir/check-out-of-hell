Set-Location $PSScriptRoot
python tools/build.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python tools/smoke_test.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$gzdoom = Join-Path $PSScriptRoot "external\gzdoom.exe"
$iwad = Join-Path $PSScriptRoot "external\freedoom2.wad"
$pk3 = Join-Path $PSScriptRoot "dist\checkout-of-hell-prototype.pk3"

if (-not (Test-Path $gzdoom)) { throw "Missing external\gzdoom.exe" }
if (-not (Test-Path $iwad)) { throw "Missing external\freedoom2.wad" }

Start-Process -FilePath $gzdoom -ArgumentList @("-iwad", $iwad, "-file", $pk3, "+map", "MAP01")
