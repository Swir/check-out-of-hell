[CmdletBinding()]
param(
    [string]$EvidenceRoot,
    [string]$CandidateManifest
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if ($env:OS -ne "Windows_NT") {
    throw "The Closing Time polish review must run on the target Windows machine."
}

$KitRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
    $EvidenceRoot = Join-Path $KitRoot "evidence"
}
if (-not (Test-Path -LiteralPath $EvidenceRoot -PathType Container)) {
    throw "Evidence root does not exist: $EvidenceRoot"
}
$EvidenceRoot = (Resolve-Path -LiteralPath $EvidenceRoot).Path

$ExpectedCommit = $null
if (-not [string]::IsNullOrWhiteSpace($CandidateManifest)) {
    $CandidateManifest = (Resolve-Path -LiteralPath $CandidateManifest).Path
    $Candidate = Get-Content -LiteralPath $CandidateManifest -Raw | ConvertFrom-Json
    if ($Candidate.schema -ne 1 -or $Candidate.project -ne "CHECKOUT OF HELL" -or $Candidate.public_release -ne $false) {
        throw "Candidate manifest is not a valid non-public CHECKOUT OF HELL sign-off manifest."
    }
    $ExpectedCommit = ([string]$Candidate.source.commit).ToLowerInvariant()
    if ($ExpectedCommit -notmatch '^[0-9a-f]{40}$') {
        throw "Candidate manifest commit is not a full Git SHA."
    }
}

$EvidenceDir = Get-ChildItem -LiteralPath $EvidenceRoot -Directory |
    Sort-Object Name -Descending |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "evidence.json") -PathType Leaf } |
    Select-Object -First 1
if ($null -eq $EvidenceDir) {
    throw "No target-Windows sign-off evidence directory was found under: $EvidenceRoot"
}

$EvidenceJson = Join-Path $EvidenceDir.FullName "evidence.json"
$EvidenceMarkdown = Join-Path $EvidenceDir.FullName "REPORT.md"
$Evidence = Get-Content -LiteralPath $EvidenceJson -Raw | ConvertFrom-Json
if ($Evidence.schema -ne 1 -or $Evidence.project -ne "CHECKOUT OF HELL") {
    throw "Evidence identity/schema is invalid: $EvidenceJson"
}
if ($Evidence.status -ne "PASS") {
    throw "Base target-Windows sign-off must report PASS before final Closing Time polish review."
}
$EvidenceCommit = ([string]$Evidence.source.commit).ToLowerInvariant()
if ($EvidenceCommit -notmatch '^[0-9a-f]{40}$') {
    throw "Evidence source commit is not a full Git SHA."
}
if ($null -ne $ExpectedCommit -and $EvidenceCommit -ne $ExpectedCommit) {
    throw "Evidence commit $EvidenceCommit does not match candidate commit $ExpectedCommit."
}
if ($Evidence.manual.final_polish_signoff -ne $true) {
    throw "Base evidence does not contain final_polish_signoff = true."
}

function Read-RequiredYesNo([string]$Question) {
    while ($true) {
        $answer = (Read-Host "$Question [y/n]").Trim().ToLowerInvariant()
        if ($answer -in @("y", "yes")) { return $true }
        if ($answer -in @("n", "no")) { return $false }
        Write-Host "Please answer y or n."
    }
}

function Set-ManualField([string]$Name, [bool]$Value) {
    $Evidence.manual | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
}

Write-Host ""
Write-Host "Closing Time final polish review"
Write-Host "Judge the exact candidate you just played; do not answer from expectation or documentation."
Write-Host ""

$EnvironmentArt = Read-RequiredYesNo "Did Closing Time read as one coherent supermarket night-shift environment with consistent project-owned art and dressing?"
$CombatReadability = Read-RequiredYesNo "Across the full Closing Time run, were enemies, projectiles, hit reactions, Overtime warnings and combat lanes readable enough for clear combat decisions?"
$ObjectiveRoute = Read-RequiredYesNo "Were the breaker routes, Night Manager transition and physical CLOCK OUT route clear without route confusion?"
$LightingAtmosphere = Read-RequiredYesNo "Did lighting and flicker preserve the creepy atmosphere without hiding objective, hazard or combat information?"
$ClutterHierarchy = Read-RequiredYesNo "Was clutter and visual hierarchy clean enough that movement, objectives and combat lanes stayed readable?"
$PacingBalance = Read-RequiredYesNo "Across all three difficulties, did encounter pacing, recovery windows, resource pressure and Night Manager escalation feel intentional and fair for each mode?"

Set-ManualField "environment_art_consistent" $EnvironmentArt
Set-ManualField "combat_readability_polished" $CombatReadability
Set-ManualField "objective_route_readable" $ObjectiveRoute
Set-ManualField "lighting_atmosphere_acceptable" $LightingAtmosphere
Set-ManualField "clutter_visual_hierarchy_clean" $ClutterHierarchy
Set-ManualField "gameplay_pacing_balance_polished" $PacingBalance

$AllPolish = $EnvironmentArt -and $CombatReadability -and $ObjectiveRoute -and $LightingAtmosphere -and $ClutterHierarchy -and $PacingBalance
$Evidence.status = if ($AllPolish) { "PASS" } else { "FAILED_POLISH_REVIEW" }
$Evidence.updated_utc = [DateTime]::UtcNow.ToString("o")
($Evidence | ConvertTo-Json -Depth 10) + "`n" | Set-Content -LiteralPath $EvidenceJson -Encoding UTF8

function Format-Result([bool]$Value) {
    if ($Value) { return "PASS" }
    return "FAIL"
}

$StartMarker = "<!-- CLOSING-TIME-POLISH-REVIEW:START -->"
$EndMarker = "<!-- CLOSING-TIME-POLISH-REVIEW:END -->"
$Section = @(
    $StartMarker,
    "## Closing Time explicit polish review",
    "",
    "| Gate | Result |",
    "| --- | --- |",
    "| Environment / art consistency | $(Format-Result $EnvironmentArt) |",
    "| Combat readability | $(Format-Result $CombatReadability) |",
    "| Objective / route readability | $(Format-Result $ObjectiveRoute) |",
    "| Lighting / atmosphere | $(Format-Result $LightingAtmosphere) |",
    "| Clutter / visual hierarchy | $(Format-Result $ClutterHierarchy) |",
    "| Gameplay pacing / balance | $(Format-Result $PacingBalance) |",
    "",
    "These whole-level polish judgments complement the three difficulty-specific combat/balance passes, controller/haptics checks, real-hardware performance sanity and final_polish_signoff.",
    $EndMarker
) -join "`r`n"

if (Test-Path -LiteralPath $EvidenceMarkdown -PathType Leaf) {
    $ReportText = Get-Content -LiteralPath $EvidenceMarkdown -Raw
} else {
    $ReportText = "# CHECKOUT OF HELL - Target Windows Demo Sign-off Evidence`r`n`r`n"
}
$ReportText = [regex]::Replace($ReportText, '(?m)^\*\*Status:\*\* .+$', "**Status:** $($Evidence.status)")
$Pattern = '(?s)<!-- CLOSING-TIME-POLISH-REVIEW:START -->.*?<!-- CLOSING-TIME-POLISH-REVIEW:END -->'
if ([regex]::IsMatch($ReportText, $Pattern)) {
    $ReportText = [regex]::Replace($ReportText, $Pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $Section })
} else {
    $ReportText = $ReportText.TrimEnd() + "`r`n`r`n" + $Section + "`r`n"
}
Set-Content -LiteralPath $EvidenceMarkdown -Value $ReportText -Encoding UTF8

if (-not $AllPolish) {
    Write-Host "Closing Time explicit polish review: FAIL"
    Write-Host "Evidence remains non-releaseable: $EvidenceMarkdown"
    exit 2
}

Write-Host "Closing Time explicit polish review: PASS"
Write-Host "Evidence: $EvidenceMarkdown"
Write-Host "Run VERIFY-EVIDENCE.bat before accepting the evidence."
exit 0
