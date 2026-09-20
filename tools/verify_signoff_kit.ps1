[CmdletBinding()]
param([string]$EvidenceDir)

$ErrorActionPreference = "Stop"
$KitRoot = Split-Path -Parent $PSScriptRoot
$CandidatePath = Join-Path $KitRoot "SIGNOFF-CANDIDATE.json"
$Candidate = Get-Content -LiteralPath $CandidatePath -Raw | ConvertFrom-Json
$ExpectedCommit = [string]$Candidate.source.commit

if ([string]::IsNullOrWhiteSpace($EvidenceDir)) {
    $EvidenceRoot = Join-Path $KitRoot "evidence"
    if (-not (Test-Path -LiteralPath $EvidenceRoot -PathType Container)) {
        throw "No evidence directory exists yet. Run RUN-SIGNOFF.bat first."
    }
    $latest = Get-ChildItem -LiteralPath $EvidenceRoot -Directory |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if (-not $latest) {
        throw "No sign-off evidence directory was found. Run RUN-SIGNOFF.bat first."
    }
    $EvidenceDir = $latest.FullName
}
else {
    $EvidenceDir = (Resolve-Path -LiteralPath $EvidenceDir).Path
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $PythonExe = $python.Source
}
else {
    & (Join-Path $PSScriptRoot "bootstrap_python.ps1")
    $PythonExe = Join-Path $PSScriptRoot "runtime\python\python.exe"
}
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Python could not be prepared from the pinned official python.org source."
}

& $PythonExe (Join-Path $PSScriptRoot "verify_windows_signoff_evidence.py") $EvidenceDir --expected-commit $ExpectedCommit
exit $LASTEXITCODE
