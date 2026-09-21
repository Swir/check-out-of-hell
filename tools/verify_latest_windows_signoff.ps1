[CmdletBinding()]
param([string]$EvidenceRoot)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if ($env:OS -ne "Windows_NT") {
    throw "The developer sign-off evidence verifier must run on the target Windows machine."
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
    $EvidenceRoot = Join-Path $ProjectRoot "dist\windows-demo-signoff"
}
if (-not (Test-Path -LiteralPath $EvidenceRoot -PathType Container)) {
    throw "Evidence root does not exist: $EvidenceRoot"
}
$EvidenceRoot = (Resolve-Path -LiteralPath $EvidenceRoot).Path

$EvidenceDir = Get-ChildItem -LiteralPath $EvidenceRoot -Directory |
    Sort-Object Name -Descending |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "evidence.json") -PathType Leaf } |
    Select-Object -First 1
if ($null -eq $EvidenceDir) {
    throw "No target-Windows evidence directory was found under: $EvidenceRoot"
}

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    throw "Git is required only for developer-checkout evidence verification so the exact local HEAD can be bound to the evidence."
}

$Commit = (& $git.Source -C $ProjectRoot rev-parse HEAD 2>$null | Select-Object -First 1).Trim().ToLowerInvariant()
if ($LASTEXITCODE -ne 0 -or $Commit -notmatch '^[0-9a-f]{40}$') {
    throw "Could not resolve the exact developer-checkout Git commit."
}
$Dirty = @(& $git.Source -C $ProjectRoot status --porcelain 2>$null)
if ($LASTEXITCODE -ne 0) {
    throw "Could not verify developer-checkout Git status."
}
if ($Dirty.Count -ne 0) {
    throw "Developer checkout is not clean. Final evidence verification requires the exact clean candidate snapshot."
}

$EvidenceJson = Join-Path $EvidenceDir.FullName "evidence.json"
$Evidence = Get-Content -LiteralPath $EvidenceJson -Raw | ConvertFrom-Json
if ($Evidence.schema -ne 1 -or $Evidence.project -ne "CHECKOUT OF HELL") {
    throw "Newest evidence identity/schema is invalid: $EvidenceJson"
}
if ($Evidence.status -ne "PASS") {
    throw "Newest evidence is not PASS after the explicit Closing Time polish review."
}
$EvidenceCommit = ([string]$Evidence.source.commit).ToLowerInvariant()
if ($EvidenceCommit -ne $Commit) {
    throw "Evidence commit $EvidenceCommit does not match clean checkout HEAD $Commit."
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

Assert-ManualSaveWitness -EvidenceDirectory $EvidenceDir.FullName

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $PythonExe = $python.Source
}
else {
    & (Join-Path $PSScriptRoot "bootstrap_python.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "Portable Python bootstrap failed with exit code $LASTEXITCODE."
    }
    $PythonExe = Join-Path $PSScriptRoot "runtime\python\python.exe"
}
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Python could not be prepared for independent evidence verification."
}

$Verifier = Join-Path $PSScriptRoot "verify_windows_signoff_evidence.py"
& $PythonExe $Verifier $EvidenceDir.FullName --expected-commit $Commit
$VerifierExit = $LASTEXITCODE
if ($VerifierExit -ne 0) {
    Write-Host "Developer target-Windows evidence chain: FAIL"
    Write-Host "No release should be published from this result."
    exit $VerifierExit
}

Write-Host "Developer target-Windows evidence chain: VERIFIED PASS"
Write-Host "Evidence: $($EvidenceDir.FullName)"
Write-Host "This confirms evidence consistency only; it does not publish or authorize a demo."
exit 0