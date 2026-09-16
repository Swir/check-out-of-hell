[CmdletBinding()]
param([switch]$Force, [switch]$DryRun)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Lock = Get-Content -LiteralPath (Join-Path $ProjectRoot "runtime-lock.json") -Raw | ConvertFrom-Json
$PythonDir = Join-Path $PSScriptRoot "runtime\python"
$PythonExe = Join-Path $PythonDir "python.exe"
$CacheDir = Join-Path $ProjectRoot ".cache\runtime"
$ZipPath = Join-Path $CacheDir "python-$($Lock.python.version)-embed-amd64.zip"

if ($DryRun) {
    if ($Lock.python.url -notmatch '^https://www\.python\.org/') {
        throw "Portable Python source is not an official python.org URL."
    }
    Write-Host "Portable Python lock resolved: $($Lock.python.version) / $($Lock.python.url)"
    exit 0
}

if (-not $Force -and (Test-Path -LiteralPath $PythonExe)) {
    & $PythonExe --version
    exit 0
}

New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
if ($Force -or -not (Test-Path -LiteralPath $ZipPath)) {
    Write-Host "Downloading portable Python $($Lock.python.version) from python.org..."
    Invoke-WebRequest -Uri $Lock.python.url -OutFile $ZipPath -UseBasicParsing
}

if (Test-Path -LiteralPath $PythonDir) { Remove-Item -LiteralPath $PythonDir -Recurse -Force }
New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null
Expand-Archive -LiteralPath $ZipPath -DestinationPath $PythonDir -Force

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Portable Python extraction failed."
}

& $PythonExe --version
if ($LASTEXITCODE -ne 0) { throw "Portable Python smoke test failed." }
Write-Host "Portable Python is ready at $PythonExe"
