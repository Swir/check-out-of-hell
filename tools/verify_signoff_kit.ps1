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

function Assert-ManualSaveWitness([string]$EvidenceDirectory) {
    $ManualSaveDir = Join-Path $EvidenceDirectory "manual-saves"
    if (-not (Test-Path -LiteralPath $ManualSaveDir -PathType Container)) {
        throw "Manual Graveyard Shift save directory is missing: $ManualSaveDir"
    }

    $WitnessFile = Join-Path $EvidenceDirectory "manual-save-witness.sha256"
    if (Test-Path -LiteralPath $WitnessFile -PathType Leaf) {
        $WitnessLine = (Get-Content -LiteralPath $WitnessFile -Raw).Trim()
        $WitnessMatch = [regex]::Match($WitnessLine, '^([0-9a-fA-F]{64})\s{2}(.+)$')
        if (-not $WitnessMatch.Success) {
            throw "Manual save witness file has an invalid format: $WitnessFile"
        }
        $ExpectedSaveSha = $WitnessMatch.Groups[1].Value.ToLowerInvariant()
        $RelativeSavePath = $WitnessMatch.Groups[2].Value
        $SavePath = Join-Path $EvidenceDirectory $RelativeSavePath
        if (-not (Test-Path -LiteralPath $SavePath -PathType Leaf)) {
            throw "Manual save witness points to a missing file: $RelativeSavePath"
        }
        $SaveItem = Get-Item -LiteralPath $SavePath
        if ($SaveItem.Extension -ine ".zds" -or $SaveItem.Name -match '(?i)^auto' -or $SaveItem.Length -lt 1024) {
            throw "Manual save witness is not a plausible non-autosave GZDoom save: $RelativeSavePath"
        }
        $ActualSaveSha = (Get-FileHash -LiteralPath $SavePath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($ActualSaveSha -ne $ExpectedSaveSha) {
            throw "Manual Graveyard Shift save witness hash changed after sign-off: $RelativeSavePath"
        }
        Write-Host "Manual Graveyard Shift save witness: VERIFIED $RelativeSavePath ($ActualSaveSha)"
        return
    }

    $SaveCandidates = @(
        Get-ChildItem -LiteralPath $ManualSaveDir -File -Recurse |
            Where-Object { $_.Extension -ieq ".zds" -and $_.Name -notmatch '(?i)^auto' -and $_.Length -ge 1024 } |
            Sort-Object LastWriteTimeUtc -Descending
    )
    if ($SaveCandidates.Count -lt 1) {
        throw "Manual Graveyard Shift evidence has no plausible non-autosave .zds save of at least 1 KiB. Create a normal save after objective progress, quit GZDoom, then load that save as instructed."
    }

    $SaveItem = $SaveCandidates[0]
    $SaveSha = (Get-FileHash -LiteralPath $SaveItem.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $RelativeSavePath = $SaveItem.FullName.Substring($EvidenceDirectory.Length)
    while ($RelativeSavePath.StartsWith("\") -or $RelativeSavePath.StartsWith("/")) {
        $RelativeSavePath = $RelativeSavePath.Substring(1)
    }
    "$SaveSha  $RelativeSavePath`r`n" | Set-Content -LiteralPath $WitnessFile -Encoding ASCII
    Write-Host "Manual Graveyard Shift save witness: LOCKED $RelativeSavePath ($SaveSha)"
}

Assert-ManualSaveWitness -EvidenceDirectory $EvidenceDir

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