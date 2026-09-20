[CmdletBinding()]
param(
    [switch]$PrepareOnly,
    [string]$CandidateManifest,
    [string]$RcZip,
    [string]$EvidenceRoot
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if ($env:OS -ne "Windows_NT") {
    throw "The sign-off kit must run on the target Windows machine."
}

$KitRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($CandidateManifest)) {
    $CandidateManifest = Join-Path $KitRoot "SIGNOFF-CANDIDATE.json"
}
if ([string]::IsNullOrWhiteSpace($RcZip)) {
    $RcZip = Join-Path $KitRoot "candidate\CHECKOUT-OF-HELL-Windows-Portable-rc.zip"
}
if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
    $EvidenceRoot = Join-Path $KitRoot "evidence"
}
$CandidateManifest = (Resolve-Path -LiteralPath $CandidateManifest).Path
$RcZip = (Resolve-Path -LiteralPath $RcZip).Path

$Candidate = Get-Content -LiteralPath $CandidateManifest -Raw | ConvertFrom-Json
if ($Candidate.schema -ne 1 -or $Candidate.project -ne "CHECKOUT OF HELL" -or $Candidate.public_release -ne $false) {
    throw "SIGNOFF-CANDIDATE.json is not a valid non-public CHECKOUT OF HELL candidate manifest."
}
$ExpectedCommit = ([string]$Candidate.source.commit).ToLowerInvariant()
$ExpectedBranch = [string]$Candidate.source.branch
$ExpectedRcSha = ([string]$Candidate.rc_sha256).ToLowerInvariant()
if ($ExpectedCommit -notmatch '^[0-9a-f]{40}$') { throw "Candidate commit is not a full Git SHA." }
if ($ExpectedRcSha -notmatch '^[0-9a-f]{64}$') { throw "Candidate RC SHA-256 is invalid." }
if ($Candidate.source.clean -ne $true) { throw "Candidate source snapshot is not clean." }
if ([string]::IsNullOrWhiteSpace($ExpectedBranch) -or $ExpectedBranch -eq "UNAVAILABLE") { throw "Candidate source branch/ref is unavailable." }

$Timestamp = [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmss")
$EvidenceDir = Join-Path $EvidenceRoot $Timestamp
$PackageDir = Join-Path $EvidenceDir "package"
$ManualSaveDir = Join-Path $EvidenceDir "manual-saves"
$PlaytestConfig = Join-Path $EvidenceDir "playtest.ini"
$EvidenceJson = Join-Path $EvidenceDir "evidence.json"
$EvidenceMarkdown = Join-Path $EvidenceDir "REPORT.md"
$AutomatedSaveLoadLog = Join-Path $EvidenceDir "gzdoom-save-load-smoke.log"
$AutomatedSaveLoadDir = Join-Path $EvidenceDir "save-load-runtime"
$SaveLoadHelper = Join-Path $PSScriptRoot "gzdoom_save_load_smoke.ps1"

New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
New-Item -ItemType Directory -Path $ManualSaveDir -Force | Out-Null

function Get-HardwareSummary {
    $summary = [ordered]@{
        windows_version = [Environment]::OSVersion.VersionString
        os_architecture = [Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
        cpu_names = @()
        gpu_names = @()
        memory_gb = $null
        controller_names = @()
    }
    try { $summary.cpu_names = @(Get-CimInstance Win32_Processor -ErrorAction Stop | ForEach-Object { [string]$_.Name } | Where-Object { $_ } | Sort-Object -Unique) } catch { }
    try { $summary.gpu_names = @(Get-CimInstance Win32_VideoController -ErrorAction Stop | ForEach-Object { [string]$_.Name } | Where-Object { $_ } | Sort-Object -Unique) } catch { }
    try {
        $system = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
        if ($system.TotalPhysicalMemory) { $summary.memory_gb = [Math]::Round(([double]$system.TotalPhysicalMemory / 1GB), 1) }
    } catch { }
    try {
        $summary.controller_names = @(
            Get-CimInstance Win32_PnPEntity -ErrorAction Stop |
                Where-Object { $_.Name -and $_.Name -match '(?i)controller|gamepad|xbox|dualsense|dualshock|joystick' } |
                ForEach-Object { [string]$_.Name } | Sort-Object -Unique
        )
    } catch { }
    return $summary
}

function Format-CheckValue([object]$Value) {
    if ($Value -eq $true) { return "PASS" }
    if ($Value -eq $false) { return "FAIL" }
    return "N/A"
}

$Evidence = [ordered]@{
    schema = 1
    project = "CHECKOUT OF HELL"
    scope = "Target Windows demo-readiness sign-off for Closing Time"
    started_utc = [DateTime]::UtcNow.ToString("o")
    updated_utc = [DateTime]::UtcNow.ToString("o")
    status = "INCOMPLETE"
    source = [ordered]@{ commit = $ExpectedCommit; branch = $ExpectedBranch; clean = $true }
    package = [ordered]@{ name = "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"; sha256 = "PENDING" }
    runtime = [ordered]@{
        gzdoom_tag = "PENDING"; gzdoom_asset = "PENDING"; gzdoom_asset_id = $null; gzdoom_local_sha256 = "PENDING"
        freedoom_tag = "PENDING"; freedoom_wad_sha256 = "PENDING"
    }
    hardware = Get-HardwareSummary
    automated = [ordered]@{ package_built = $false; package_integrity = $false; runtime_bootstrap = $false; save_load_roundtrip = $false }
    manual = [ordered]@{
        closing_crew = [ordered]@{ completed = $false; no_softlock = $false; combat_readable = $false; balance_acceptable = $false; engine_exit_ok = $false }
        graveyard_shift = [ordered]@{ completed = $false; no_softlock = $false; combat_readable = $false; balance_acceptable = $false; engine_exit_ok = $false; save_quit_load = $false }
        corporate_hell = [ordered]@{ completed = $false; no_softlock = $false; combat_readable = $false; balance_acceptable = $false; engine_exit_ok = $false }
        controller_core_actions = $false; controller_haptics = $false; performance_sanity = $false; final_polish_signoff = $false
    }
    failure = $null
}

function Write-EvidenceReport {
    $Evidence.updated_utc = [DateTime]::UtcNow.ToString("o")
    ($Evidence | ConvertTo-Json -Depth 10) + "`n" | Set-Content -LiteralPath $EvidenceJson -Encoding UTF8
    $lines = @(
        "# CHECKOUT OF HELL - Target Windows Demo Sign-off Evidence", "",
        "**Status:** $($Evidence.status)", "**Source branch:** $($Evidence.source.branch)", "**Source commit:** $($Evidence.source.commit)",
        "**Clean source tree:** $(Format-CheckValue $Evidence.source.clean)", "**RC SHA-256:** $($Evidence.package.sha256)",
        "**GZDoom:** $($Evidence.runtime.gzdoom_tag)", "**Freedoom:** $($Evidence.runtime.freedoom_tag)", "",
        "## Automated gates", "", "| Gate | Result |", "| --- | --- |",
        "| Exact RC package built | $(Format-CheckValue $Evidence.automated.package_built) |",
        "| RC manifest/integrity verified | $(Format-CheckValue $Evidence.automated.package_integrity) |",
        "| Pinned official runtime prepared | $(Format-CheckValue $Evidence.automated.runtime_bootstrap) |",
        "| Exact RC save -> process exit -> load | $(Format-CheckValue $Evidence.automated.save_load_roundtrip) |", "",
        "## Manual target-Windows gates", "", "| Gate | Result |", "| --- | --- |",
        "| Closing Crew full clock-out run | $(Format-CheckValue $Evidence.manual.closing_crew.completed) |",
        "| Graveyard Shift manual save/quit/load + clock-out | $(Format-CheckValue ($Evidence.manual.graveyard_shift.completed -and $Evidence.manual.graveyard_shift.save_quit_load)) |",
        "| Corporate Hell full clock-out run | $(Format-CheckValue $Evidence.manual.corporate_hell.completed) |",
        "| Physical controller used for core actions | $(Format-CheckValue $Evidence.manual.controller_core_actions) |",
        "| Controller haptics acceptable | $(Format-CheckValue $Evidence.manual.controller_haptics) |",
        "| Real-hardware Overtime/boss performance sanity | $(Format-CheckValue $Evidence.manual.performance_sanity) |",
        "| Closing Time presentation/balance sign-off | $(Format-CheckValue $Evidence.manual.final_polish_signoff) |", "",
        "## Privacy", "",
        "This evidence records OS/CPU/GPU/RAM and controller friendly names only. It intentionally does not collect account names, serial numbers, hardware IDs or device IDs.", "",
        "A PASS here is necessary evidence for the interactive Windows gate, but it does not publish or authorize a public demo by itself. Remaining ROADMAP release gates still apply."
    )
    ($lines -join "`r`n") + "`r`n" | Set-Content -LiteralPath $EvidenceMarkdown -Encoding UTF8
}

function Read-RequiredYesNo([string]$Question) {
    while ($true) {
        $answer = (Read-Host "$Question [y/n]").Trim().ToLowerInvariant()
        if ($answer -in @("y", "yes")) { return $true }
        if ($answer -in @("n", "no")) { return $false }
        Write-Host "Please answer y or n."
    }
}

function Start-ManualGameSession([string]$Instruction) {
    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host $Instruction
    Write-Host "Use New Game -> The Worst Shift and the requested difficulty."
    Write-Host "The script will continue after GZDoom is fully closed."
    Write-Host "------------------------------------------------------------"
    $args = @("-iwad", ('"' + $FreedoomWad + '"'), "-file", ('"' + $GamePk3 + '"'), "-config", ('"' + $PlaytestConfig + '"'), "-savedir", ('"' + $ManualSaveDir + '"'))
    $process = Start-Process -FilePath $GZDoomExe -ArgumentList $args -WorkingDirectory $PackageDir -Wait -PassThru
    return ($process.ExitCode -eq 0)
}

function Run-StandardDifficultyPass([string]$Difficulty, [string]$Key) {
    $launchedCleanly = Start-ManualGameSession "Play MAP01 - Closing Time from a fresh start on $Difficulty. Restore all breakers, defeat the Night Manager and physically clock out."
    $Evidence.manual[$Key] = [ordered]@{
        engine_exit_ok = $launchedCleanly
        completed = Read-RequiredYesNo "Did you complete Closing Time and clock out on $Difficulty without using console cheats?"
        no_softlock = Read-RequiredYesNo "Was the full objective route free of crashes, progression blockers and softlocks on $Difficulty?"
        combat_readable = Read-RequiredYesNo "Were threats, Overtime warnings and the clock-out route readable during real play on $Difficulty?"
        balance_acceptable = Read-RequiredYesNo "Was the $Difficulty balance appropriate for its intended role?"
    }
    Write-EvidenceReport
}

Write-EvidenceReport
try {
    Write-Host "Verifying the exact CI-built release candidate against SIGNOFF-CANDIDATE.json..."
    $ActualRcSha = (Get-FileHash -LiteralPath $RcZip -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualRcSha -ne $ExpectedRcSha) { throw "Embedded RC SHA-256 does not match SIGNOFF-CANDIDATE.json." }
    $Evidence.package.sha256 = $ActualRcSha
    $Evidence.automated.package_built = $true
    Write-EvidenceReport

    if (Test-Path -LiteralPath $PackageDir) { Remove-Item -LiteralPath $PackageDir -Recurse -Force }
    New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
    Expand-Archive -LiteralPath $RcZip -DestinationPath $PackageDir -Force

    $PackageManifestPath = Join-Path $PackageDir "package-manifest.json"
    $PackageManifest = Get-Content -LiteralPath $PackageManifestPath -Raw | ConvertFrom-Json
    if ($PackageManifest.package_kind -ne "windows-portable-release-candidate" -or $PackageManifest.public_release -ne $false) {
        throw "Extracted package manifest is not the expected non-public Windows RC."
    }
    if (([string]$PackageManifest.source.commit).ToLowerInvariant() -ne $ExpectedCommit -or [string]$PackageManifest.source.branch -ne $ExpectedBranch -or $PackageManifest.source.clean -ne $true) {
        throw "Extracted RC source provenance does not match SIGNOFF-CANDIDATE.json."
    }
    & (Join-Path $PackageDir "tools\verify_player_package.ps1")
    $Evidence.automated.package_integrity = $true
    Write-EvidenceReport

    Write-Host "Preparing the pinned official runtime inside the verified RC..."
    & (Join-Path $PackageDir "tools\bootstrap_runtime.ps1")
    $Evidence.automated.runtime_bootstrap = $true
    $GZDoomExe = Join-Path $PackageDir "external\gzdoom\gzdoom.exe"
    $FreedoomWad = Join-Path $PackageDir "external\freedoom2.wad"
    $GamePk3 = Join-Path $PackageDir "game\CHECKOUT-OF-HELL.pk3"
    foreach ($required in @($GZDoomExe, $FreedoomWad, $GamePk3)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Prepared RC runtime payload is missing: $required" }
    }

    $RuntimeManifest = Get-Content -LiteralPath (Join-Path $PackageDir "external\runtime-manifest.json") -Raw | ConvertFrom-Json
    $FreedoomProvenance = Get-Content -LiteralPath (Join-Path $PackageDir "third_party\FREEDOOM-PROVENANCE.json") -Raw | ConvertFrom-Json
    $Evidence.runtime.gzdoom_tag = [string]$PackageManifest.runtime.gzdoom_tag
    $Evidence.runtime.gzdoom_asset = [string]$RuntimeManifest.gzdoom.asset
    $Evidence.runtime.gzdoom_asset_id = [Int64]$RuntimeManifest.gzdoom.asset_id
    $Evidence.runtime.gzdoom_local_sha256 = [string]$RuntimeManifest.gzdoom.local_sha256
    $Evidence.runtime.freedoom_tag = [string]$PackageManifest.runtime.freedoom_tag
    $Evidence.runtime.freedoom_wad_sha256 = [string]$FreedoomProvenance.wad_sha256
    Write-EvidenceReport

    Write-Host "Running real save -> process exit -> load against the exact extracted candidate..."
    & $SaveLoadHelper -GZDoomExe $GZDoomExe -FreedoomWad $FreedoomWad -Pk3 $GamePk3 -WorkDir $AutomatedSaveLoadDir -CombinedLog $AutomatedSaveLoadLog -PreparedRuntime
    if (-not $?) { throw "Exact-RC save/load helper failed." }
    $Evidence.automated.save_load_roundtrip = $true
    Write-EvidenceReport
}
catch {
    $Evidence.failure = $_.Exception.Message
    $Evidence.status = "FAILED_AUTOMATION"
    Write-EvidenceReport
    Write-Host "Automated sign-off preparation FAILED: $($Evidence.failure)"
    Write-Host "Evidence: $EvidenceMarkdown"
    throw
}

if ($PrepareOnly) {
    $Evidence.status = "INCOMPLETE"
    Write-EvidenceReport
    Write-Host "Automated candidate verification is complete; manual target-Windows gates were intentionally not run."
    Write-Host "Evidence: $EvidenceMarkdown"
    exit 2
}

Run-StandardDifficultyPass -Difficulty "Closing Crew" -Key "closing_crew"

$graveyardFirstExit = Start-ManualGameSession "Start Graveyard Shift. After at least one breaker is restored, create a normal manual save, then quit GZDoom completely BEFORE finishing MAP01."
$graveyardSaved = Read-RequiredYesNo "Did you create a normal Graveyard Shift save after making objective progress and then fully quit GZDoom?"
$graveyardSecondExit = Start-ManualGameSession "Relaunch Graveyard Shift evidence: use Load Game to restore the save you just created, verify the objective state, then finish MAP01 and clock out."
$graveyardLoaded = Read-RequiredYesNo "Did the save restore the expected breaker/objective state after a full process exit?"
$Evidence.manual.graveyard_shift = [ordered]@{
    engine_exit_ok = ($graveyardFirstExit -and $graveyardSecondExit)
    save_quit_load = ($graveyardSaved -and $graveyardLoaded)
    completed = Read-RequiredYesNo "After loading, did you complete Closing Time and clock out on Graveyard Shift without console cheats?"
    no_softlock = Read-RequiredYesNo "Was the full Graveyard Shift route free of crashes, progression blockers and softlocks?"
    combat_readable = Read-RequiredYesNo "Were threats, Overtime warnings and the clock-out route readable on Graveyard Shift?"
    balance_acceptable = Read-RequiredYesNo "Was Graveyard Shift balance appropriate as the intended default difficulty?"
}
Write-EvidenceReport

Run-StandardDifficultyPass -Difficulty "Corporate Hell" -Key "corporate_hell"
$Evidence.manual.controller_core_actions = Read-RequiredYesNo "Using a physical controller, did move/look/fire/alternate-fire/use/jump or crouch/weapon cycling work as expected during the playtest?"
$Evidence.manual.controller_haptics = Read-RequiredYesNo "Were the signature-weapon haptics present when expected and restrained enough for extended play?"
$Evidence.manual.performance_sanity = Read-RequiredYesNo "On this real Windows hardware, did Overtime and the Night Manager fight remain responsive without a sustained performance problem that would block a demo?"
$Evidence.manual.final_polish_signoff = Read-RequiredYesNo "Is Closing Time visually/readably polished and balanced enough to represent the intended final game direction in a public demo?"
Write-EvidenceReport

$manualChecks = @(
    $Evidence.manual.closing_crew.engine_exit_ok, $Evidence.manual.closing_crew.completed, $Evidence.manual.closing_crew.no_softlock, $Evidence.manual.closing_crew.combat_readable, $Evidence.manual.closing_crew.balance_acceptable,
    $Evidence.manual.graveyard_shift.engine_exit_ok, $Evidence.manual.graveyard_shift.save_quit_load, $Evidence.manual.graveyard_shift.completed, $Evidence.manual.graveyard_shift.no_softlock, $Evidence.manual.graveyard_shift.combat_readable, $Evidence.manual.graveyard_shift.balance_acceptable,
    $Evidence.manual.corporate_hell.engine_exit_ok, $Evidence.manual.corporate_hell.completed, $Evidence.manual.corporate_hell.no_softlock, $Evidence.manual.corporate_hell.combat_readable, $Evidence.manual.corporate_hell.balance_acceptable,
    $Evidence.manual.controller_core_actions, $Evidence.manual.controller_haptics, $Evidence.manual.performance_sanity, $Evidence.manual.final_polish_signoff
)
$automatedChecks = @($Evidence.automated.package_built, $Evidence.automated.package_integrity, $Evidence.automated.runtime_bootstrap, $Evidence.automated.save_load_roundtrip)
$allAutomated = -not ($automatedChecks -contains $false)
$allManual = -not ($manualChecks -contains $false)
$sourceIsVerifiable = ($Evidence.source.commit -match '^[0-9a-f]{40}$' -and $Evidence.source.clean -eq $true)

if ($allAutomated -and $allManual -and $sourceIsVerifiable) {
    $Evidence.status = "PASS"
    Write-EvidenceReport
    Write-Host "TARGET WINDOWS SIGN-OFF: PASS"
    Write-Host "Evidence: $EvidenceMarkdown"
    Write-Host "Run VERIFY-EVIDENCE.bat before accepting this as roadmap evidence. This does not publish a demo."
    exit 0
}

$Evidence.status = "FAIL"
Write-EvidenceReport
Write-Host "TARGET WINDOWS SIGN-OFF: FAIL"
Write-Host "Evidence: $EvidenceMarkdown"
Write-Host "No release should be published from this result."
exit 3
