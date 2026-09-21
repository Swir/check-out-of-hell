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
    $ManualSaveRoot = (Resolve-Path -LiteralPath $ManualSaveDir).Path

    $WitnessFile = Join-Path $EvidenceDirectory "manual-save-witness.sha256"
    if (Test-Path -LiteralPath $WitnessFile -PathType Leaf) {
        $WitnessLine = (Get-Content -LiteralPath $WitnessFile -Raw).Trim()
        $WitnessMatch = [regex]::Match($WitnessLine, '^([0-9a-fA-F]{64})\s{2}(.+)$')
        if (-not $WitnessMatch.Success) {
            throw "Manual save witness file has an invalid format: $WitnessFile"
        }
        $ExpectedSaveSha = $WitnessMatch.Groups[1].Value.ToLowerInvariant()
        $RelativeSavePath = $WitnessMatch.Groups[2].Value
        $PathParts = @($RelativeSavePath -split '[\\/]')
        if ([System.IO.Path]::IsPathRooted($RelativeSavePath) -or $PathParts -contains "..") {
            throw "Manual save witness path must stay inside the evidence manual-saves directory."
        }
        $SavePath = Join-Path $EvidenceDirectory $RelativeSavePath
        if (-not (Test-Path -LiteralPath $SavePath -PathType Leaf)) {
            throw "Manual save witness points to a missing file: $RelativeSavePath"
        }
        $SavePath = (Resolve-Path -LiteralPath $SavePath).Path
        $ExpectedPrefix = $ManualSaveRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
        if (-not $SavePath.StartsWith($ExpectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Manual save witness points outside the manual-saves evidence directory."
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
$VerifierExitCode = $LASTEXITCODE
if ($VerifierExitCode -ne 0) {
    exit $VerifierExitCode
}

$ExportRoot = Join-Path $KitRoot "evidence-export"
New-Item -ItemType Directory -Path $ExportRoot -Force | Out-Null
$EvidenceName = (Get-Item -LiteralPath $EvidenceDir).Name
$ShortCommit = $ExpectedCommit.Substring(0, 7).ToLowerInvariant()
$OutputZip = Join-Path $ExportRoot "CHECKOUT-OF-HELL-Windows-Signoff-Evidence-$ShortCommit-$EvidenceName.zip"
$OutputChecksum = "$OutputZip.sha256"

if (Test-Path -LiteralPath $OutputZip) {
    Remove-Item -LiteralPath $OutputZip -Force
}
if (Test-Path -LiteralPath $OutputChecksum) {
    Remove-Item -LiteralPath $OutputChecksum -Force
}

$BundlePaths = @(
    Get-ChildItem -LiteralPath $EvidenceDir -Force |
        ForEach-Object { $_.FullName }
)
if ($BundlePaths.Count -lt 1) {
    throw "Verified evidence directory is unexpectedly empty: $EvidenceDir"
}

Compress-Archive -Path $BundlePaths -DestinationPath $OutputZip -CompressionLevel Optimal -Force
$BundleSha = (Get-FileHash -LiteralPath $OutputZip -Algorithm SHA256).Hash.ToLowerInvariant()
"$BundleSha  $([System.IO.Path]::GetFileName($OutputZip))`r`n" |
    Set-Content -LiteralPath $OutputChecksum -Encoding ASCII

Write-Host "Verified PASS evidence bundle: $OutputZip"
Write-Host "Evidence bundle SHA-256: $BundleSha"
Write-Host "You can upload/send this ZIP as the exact target-Windows sign-off evidence package."
exit 0
