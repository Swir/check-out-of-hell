[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$NoLaunch,
    [string]$EvidenceRoot = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RuntimeLockPath = Join-Path $ProjectRoot "runtime-lock.json"
$BootstrapRuntime = Join-Path $PSScriptRoot "bootstrap_runtime.ps1"
$BootstrapPython = Join-Path $PSScriptRoot "bootstrap_python.ps1"
$BuildScript = Join-Path $PSScriptRoot "build.py"
$SmokeTest = Join-Path $PSScriptRoot "smoke_test.py"
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$RuntimeManifestPath = Join-Path $ProjectRoot "external\runtime-manifest.json"
$PackageManifestPath = Join-Path $ProjectRoot "package-manifest.json"
$PackagedPk3 = Join-Path $ProjectRoot "game\CHECKOUT-OF-HELL.pk3"
$SourcePk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$PackageVerifier = Join-Path $PSScriptRoot "verify_player_package.ps1"

$GateDefinitions = @(
    [ordered]@{ key = "full_playthrough"; label = "Complete Closing Time from shift start through the physical clock-out trigger" },
    [ordered]@{ key = "manual_save_quit_load"; label = "Create a normal in-game save, quit GZDoom fully, relaunch, load it and continue successfully" },
    [ordered]@{ key = "physical_controller"; label = "Play with a real controller and confirm movement, aiming, actions and weapon haptics are usable" },
    [ordered]@{ key = "closing_crew_balance"; label = "Closing Crew difficulty feels readable and finishable without broken pacing or resource starvation" },
    [ordered]@{ key = "graveyard_shift_balance"; label = "Graveyard Shift difficulty feels like the intended baseline and remains readable" },
    [ordered]@{ key = "corporate_hell_balance"; label = "Corporate Hell feels demanding but fair, with no progression blockers or unreadable pressure spikes" },
    [ordered]@{ key = "real_hardware_performance"; label = "Real Windows hardware remains responsive through Overtime, boss waves and the post-boss return leg" },
    [ordered]@{ key = "final_polish"; label = "No presentation/gameplay issue remains that would make Closing Time unrepresentative of the intended demo quality" }
)

function Ensure-File([string]$Path, [string]$Description) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Description is missing: $Path"
    }
}

function Read-JsonFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-ProjectPath([string]$Path) {
    $root = $ProjectRoot.TrimEnd("\") + "\"
    if ($Path.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Substring($root.Length).Replace("\", "/")
    }
    return $Path
}

function Get-FileRecord([string]$Path) {
    Ensure-File -Path $Path -Description "Evidence input"
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = Get-ProjectPath -Path $Path
        bytes = [Int64]$item.Length
        sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

function Get-SourceIdentity {
    $commit = "unknown"
    $branch = "unknown"
    $packageManifest = Read-JsonFile -Path $PackageManifestPath
    if ($packageManifest -and $packageManifest.source) {
        if ($packageManifest.source.commit) { $commit = [string]$packageManifest.source.commit }
        if ($packageManifest.source.branch) { $branch = [string]$packageManifest.source.branch }
    }

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git -and (Test-Path -LiteralPath (Join-Path $ProjectRoot ".git"))) {
        try {
            $gitCommit = (& $git.Source -C $ProjectRoot rev-parse HEAD 2>$null).Trim()
            $gitBranch = (& $git.Source -C $ProjectRoot rev-parse --abbrev-ref HEAD 2>$null).Trim()
            if ($gitCommit) { $commit = $gitCommit }
            if ($gitBranch) { $branch = $gitBranch }
        }
        catch { }
    }
    return [ordered]@{ commit = $commit; branch = $branch }
}

function Get-HardwareSnapshot {
    $snapshot = [ordered]@{
        os = "unknown"
        cpu = "unknown"
        gpu = @()
        memory_gb = $null
        controller_candidates = @()
    }
    try {
        $os = Get-CimInstance Win32_OperatingSystem | Select-Object -First 1
        if ($os) {
            $snapshot.os = "$($os.Caption) $($os.Version) build $($os.BuildNumber)"
            if ($os.TotalVisibleMemorySize) {
                $snapshot.memory_gb = [math]::Round(([double]$os.TotalVisibleMemorySize / 1MB), 1)
            }
        }
    }
    catch { }
    try {
        $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
        if ($cpu -and $cpu.Name) { $snapshot.cpu = ([string]$cpu.Name).Trim() }
    }
    catch { }
    try {
        $snapshot.gpu = @(Get-CimInstance Win32_VideoController | Where-Object { $_.Name } | ForEach-Object { ([string]$_.Name).Trim() } | Sort-Object -Unique)
    }
    catch { }
    try {
        $pattern = "Xbox|XInput|Controller|Gamepad|DualSense|DualShock|8BitDo|Wireless Controller"
        $snapshot.controller_candidates = @(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -and ([string]$_.Name -match $pattern) } | ForEach-Object { ([string]$_.Name).Trim() } | Sort-Object -Unique)
    }
    catch { }
    return $snapshot
}

function Resolve-GamePackage {
    if (Test-Path -LiteralPath $PackagedPk3 -PathType Leaf) { return $PackagedPk3 }
    if (Test-Path -LiteralPath $SourcePk3 -PathType Leaf) { return $SourcePk3 }

    Ensure-File -Path $BuildScript -Description "Build script"
    Ensure-File -Path $SmokeTest -Description "Smoke test"
    $python = Get-Command python -ErrorAction SilentlyContinue
    $pythonExe = $null
    if ($python) {
        $pythonExe = $python.Source
    }
    else {
        Ensure-File -Path $BootstrapPython -Description "Portable Python bootstrap"
        & $BootstrapPython
        if ($LASTEXITCODE -ne 0) { throw "Portable Python bootstrap failed with exit code $LASTEXITCODE." }
        $pythonExe = Join-Path $ProjectRoot "tools\runtime\python\python.exe"
    }
    Ensure-File -Path $pythonExe -Description "Python runtime"
    & $pythonExe $BuildScript
    if ($LASTEXITCODE -ne 0) { throw "Game build failed with exit code $LASTEXITCODE." }
    & $pythonExe $SmokeTest
    if ($LASTEXITCODE -ne 0) { throw "Smoke test failed with exit code $LASTEXITCODE." }
    Ensure-File -Path $SourcePk3 -Description "Built PK3"
    return $SourcePk3
}

function Read-GateResult($Definition) {
    Write-Host ""
    Write-Host $Definition.label -ForegroundColor Cyan
    while ($true) {
        $answer = (Read-Host "Result: [Y] pass  [N] fail  [S] not tested").Trim().ToLowerInvariant()
        if ($answer -in @("y", "yes")) { $status = "PASS"; break }
        if ($answer -in @("n", "no")) { $status = "FAIL"; break }
        if ($answer -in @("s", "skip", "not tested")) { $status = "NOT_TESTED"; break }
        Write-Host "Please enter Y, N or S."
    }
    return [ordered]@{
        label = $Definition.label
        status = $status
        note = (Read-Host "Optional note").Trim()
    }
}

function Write-MarkdownReport($Evidence, [string]$Path) {
    $lines = @(
        "# CHECKOUT OF HELL — Windows playtest evidence",
        "",
        "This records manual target-Windows evidence for the named Closing Time sign-off scope. It does not authorize a public release by itself.",
        "",
        "- Generated UTC: ``$($Evidence.generated_at_utc)``",
        "- Scope: **$($Evidence.scope)**",
        "- Result: **$($Evidence.result)**",
        "- Source branch: ``$($Evidence.source.branch)``",
        "- Source commit: ``$($Evidence.source.commit)``",
        "- GZDoom pin: ``$($Evidence.runtime.gzdoom_tag)``",
        "- Freedoom pin: ``$($Evidence.runtime.freedoom_tag)``",
        "",
        "## Manual gates",
        "",
        "| Gate | Result | Note |",
        "| --- | --- | --- |"
    )
    foreach ($property in $Evidence.gates.PSObject.Properties) {
        $gate = $property.Value
        $safeNote = ([string]$gate.note).Replace("|", "\|")
        $lines += "| $($gate.label) | **$($gate.status)** | $safeNote |"
    }
    $lines += @(
        "",
        "## Hardware snapshot",
        "",
        "- OS: $($Evidence.hardware.os)",
        "- CPU: $($Evidence.hardware.cpu)",
        "- GPU: $([string]::Join('; ', @($Evidence.hardware.gpu)))",
        "- Memory: $($Evidence.hardware.memory_gb) GB",
        "- Controller candidates: $([string]::Join('; ', @($Evidence.hardware.controller_candidates)))",
        "",
        "## Evidence files",
        "",
        "- Game PK3 SHA-256: ``$($Evidence.files.game.sha256)``",
        "- GZDoom executable SHA-256: ``$($Evidence.files.gzdoom.sha256)``",
        "- Freedoom WAD SHA-256: ``$($Evidence.files.freedoom.sha256)``",
        "",
        "Public release authorized by this report: **NO**. Release notes, legal-content packaging policy and repository release gates remain separate."
    )
    $lines -join "`r`n" | Set-Content -LiteralPath $Path -Encoding UTF8
}

Ensure-File -Path $RuntimeLockPath -Description "Runtime lock"
Ensure-File -Path $BootstrapRuntime -Description "Pinned runtime bootstrap"
$lock = Read-JsonFile -Path $RuntimeLockPath
if (-not $lock -or -not $lock.gzdoom -or -not $lock.freedoom) {
    throw "runtime-lock.json is missing the expected GZDoom/Freedoom records."
}

if ($DryRun) {
    if ((-not (Test-Path -LiteralPath $PackagedPk3 -PathType Leaf)) -and (-not (Test-Path -LiteralPath $BuildScript -PathType Leaf))) {
        throw "Dry-run cannot find either the packaged game or the source build path."
    }
    Write-Host "Windows playtest assistant dry-run: PASS"
    Write-Host "GZDoom pin : $($lock.gzdoom.tag)"
    Write-Host "Freedoom pin: $($lock.freedoom.tag)"
    Write-Host "Manual gates : $($GateDefinitions.Count)"
    Write-Host "Dry-run does not download runtime files, launch the game, prompt for results, or mark demo readiness complete."
    exit 0
}

if ((Test-Path -LiteralPath $PackageManifestPath -PathType Leaf) -and (Test-Path -LiteralPath $PackageVerifier -PathType Leaf)) {
    Write-Host "Verifying release-candidate package before playtest..."
    & $PackageVerifier
    if ($LASTEXITCODE -ne 0) { throw "Release-candidate integrity verification failed with exit code $LASTEXITCODE." }
}

Write-Host "Preparing pinned legal runtime..."
& $BootstrapRuntime
if ($LASTEXITCODE -ne 0) { throw "Runtime bootstrap failed with exit code $LASTEXITCODE." }

$gamePk3 = Resolve-GamePackage
foreach ($required in @($GZDoomExe, $FreedoomWad, $gamePk3, $RuntimeManifestPath)) {
    Ensure-File -Path $required -Description "Playtest prerequisite"
}

if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) { $EvidenceRoot = Join-Path $ProjectRoot "playtest-evidence" }
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmssZ")
$sessionDir = Join-Path $EvidenceRoot $stamp
New-Item -ItemType Directory -Path $sessionDir -Force | Out-Null
$engineConfig = Join-Path $sessionDir "gzdoom-playtest.ini"
$engineLog = Join-Path $sessionDir "gzdoom-playtest.log"
$evidenceJson = Join-Path $sessionDir "evidence.json"
$evidenceMarkdown = Join-Path $sessionDir "evidence.md"

@(
    "[GlobalSettings]",
    "vid_fullscreen=false",
    "vid_lowerinbackground=false",
    "vid_activeinbackground=true",
    "i_pauseinbackground=true"
) | Set-Content -LiteralPath $engineConfig -Encoding ASCII

$source = Get-SourceIdentity
$runtimeManifest = Read-JsonFile -Path $RuntimeManifestPath
$hardware = Get-HardwareSnapshot

if (-not $NoLaunch) {
    Write-Host ""
    Write-Host "Manual target-Windows session is ready." -ForegroundColor Green
    Write-Host "Evaluate Closing Time, Overtime, Night Manager, the clock-out route, controller feel and performance."
    Write-Host "Create a normal in-game save before quitting. A second process will then start so you can manually load that save."

    $args1 = @("-config", "`"$engineConfig`"", "-iwad", "`"$FreedoomWad`"", "-file", "`"$gamePk3`"", "+logfile", "`"$engineLog`"", "+map", "MAP01")
    $first = Start-Process -FilePath $GZDoomExe -ArgumentList $args1 -WorkingDirectory $ProjectRoot -Wait -PassThru
    Write-Host "First GZDoom session exited with code $($first.ExitCode)."

    Write-Host "Second session: load the save from the first session, confirm it resumes correctly, then exit GZDoom." -ForegroundColor Cyan
    $args2 = @("-config", "`"$engineConfig`"", "-iwad", "`"$FreedoomWad`"", "-file", "`"$gamePk3`"", "+logfile", "`"$engineLog`"")
    $second = Start-Process -FilePath $GZDoomExe -ArgumentList $args2 -WorkingDirectory $ProjectRoot -Wait -PassThru
    Write-Host "Second GZDoom session exited with code $($second.ExitCode)."
}
else {
    Write-Host "NoLaunch mode: runtime/package evidence was prepared, but no manual gameplay session was started."
}

$gateResults = [ordered]@{}
foreach ($definition in $GateDefinitions) {
    if ($NoLaunch) {
        $gateResults[$definition.key] = [ordered]@{ label = $definition.label; status = "NOT_TESTED"; note = "NoLaunch mode" }
    }
    else {
        $gateResults[$definition.key] = Read-GateResult -Definition $definition
    }
}

$allPassed = $true
foreach ($gate in $gateResults.Values) {
    if ($gate.status -ne "PASS") { $allPassed = $false; break }
}
$result = if ($allPassed) { "PASS" } else { "INCOMPLETE" }

$evidence = [ordered]@{
    schema = 1
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    project = "CHECKOUT OF HELL"
    scope = "Closing Time target-Windows interactive demo sign-off"
    result = $result
    public_release_authorized = $false
    source = $source
    runtime = [ordered]@{
        gzdoom_tag = [string]$lock.gzdoom.tag
        freedoom_tag = [string]$lock.freedoom.tag
        manifest = $runtimeManifest
    }
    hardware = $hardware
    files = [ordered]@{
        game = Get-FileRecord -Path $gamePk3
        gzdoom = Get-FileRecord -Path $GZDoomExe
        freedoom = Get-FileRecord -Path $FreedoomWad
    }
    gates = $gateResults
}

$evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $evidenceJson -Encoding UTF8
Write-MarkdownReport -Evidence $evidence -Path $evidenceMarkdown

$resultColor = if ($allPassed) { "Green" } else { "Yellow" }
Write-Host ""
Write-Host "Windows playtest evidence result: $result" -ForegroundColor $resultColor
Write-Host "JSON: $evidenceJson"
Write-Host "Report: $evidenceMarkdown"
if (-not $allPassed) { Write-Host "The demo sign-off remains open until every named manual gate is PASS." }
Write-Host "This helper never publishes a GitHub Release or changes ROADMAP progress automatically."
