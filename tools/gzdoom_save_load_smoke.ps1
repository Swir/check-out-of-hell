[CmdletBinding()]
param(
    [int]$RunSeconds = 10
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$ProbeRoot = Join-Path $ProjectRoot "dist\runtime-save-load"
$SaveDir = Join-Path $ProbeRoot "saves"
$ConfigFile = Join-Path $ProbeRoot "gzdoom-runtime-probe.ini"
$SaveLog = Join-Path $ProbeRoot "save-pass.log"
$LoadLog = Join-Path $ProbeRoot "load-pass.log"
$CombinedLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"

function Assert-NoRuntimeErrors {
    param(
        [string]$Text,
        [string]$Phase
    )

    $errorPatterns = @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Invalid parameter",
        "Parse error",
        "VM execution aborted",
        "Could not load savegame",
        "Savegame is from a different version",
        "Savegame uses a different set of files"
    )

    foreach ($pattern in $errorPatterns) {
        if ($Text -match [regex]::Escape($pattern)) {
            throw "GZDoom reported '$pattern' during the $Phase phase."
        }
    }
}

function Invoke-GZDoomProbe {
    param(
        [string[]]$Arguments,
        [string]$LogPath,
        [string]$Phase
    )

    if (Test-Path -LiteralPath $LogPath) {
        Remove-Item -LiteralPath $LogPath -Force
    }

    $stdoutPath = "$LogPath.stdout"
    $stderrPath = "$LogPath.stderr"
    foreach ($path in @($stdoutPath, $stderrPath)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }

    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $Arguments `
        -WorkingDirectory $ProjectRoot `
        -PassThru `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath

    $exitedNaturally = $process.WaitForExit($RunSeconds * 1000)
    $naturalExitCode = $null
    if ($exitedNaturally) {
        $naturalExitCode = $process.ExitCode
    }
    else {
        # A successful interactive engine run is expected to remain alive. Stop it after the
        # probe window instead of relying on a startup +quit command that can fire before the
        # first map/save cycle on some GZDoom builds.
        try {
            $process.Kill()
            $process.WaitForExit()
        }
        catch {
            throw "Could not stop GZDoom after the $Phase probe window: $($_.Exception.Message)"
        }
    }

    $stdout = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw } else { "" }
    $stderr = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { "" }
    $lifecycle = if ($exitedNaturally) { "natural exit $naturalExitCode" } else { "alive after $RunSeconds s; stopped by harness" }
    $text = "=== STDOUT ===`r`n$stdout`r`n=== STDERR ===`r`n$stderr`r`nLifecycle: $lifecycle`r`n"
    Set-Content -LiteralPath $LogPath -Value $text -Encoding UTF8

    if ($exitedNaturally -and $naturalExitCode -ne 0) {
        throw "GZDoom $Phase phase exited early with code $naturalExitCode. See $LogPath"
    }

    Assert-NoRuntimeErrors -Text $text -Phase $Phase
    return $text
}

Write-Host "Building current prototype..."
python (Join-Path $PSScriptRoot "build.py")
if ($LASTEXITCODE -ne 0) {
    throw "Prototype build failed with exit code $LASTEXITCODE."
}

Write-Host "Resolving pinned official runtime..."
& (Join-Path $PSScriptRoot "bootstrap_runtime.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Runtime bootstrap failed with exit code $LASTEXITCODE."
}

foreach ($required in @($GZDoomExe, $FreedoomWad, $Pk3)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Runtime save/load prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $ProbeRoot) {
    Remove-Item -LiteralPath $ProbeRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $SaveDir -Force | Out-Null

$common = @(
    "-stdout",
    "-nosound",
    "-nomusic",
    "-noautoload",
    "-config", $ConfigFile,
    "-savedir", $SaveDir,
    "-iwad", $FreedoomWad,
    "-file", $Pk3,
    "+vid_fullscreen", "0"
)

Write-Host "Creating an actual MAP01 savegame with the pinned GZDoom runtime..."
$saveArguments = $common + @(
    "+map", "MAP01",
    "+give", "CheckoutFuse", "2",
    "+give", "CorporateMemo", "1",
    "+save", "coh-runtime-probe"
)
$saveText = Invoke-GZDoomProbe -Arguments $saveArguments -LogPath $SaveLog -Phase "save"

$saveFiles = @(Get-ChildItem -LiteralPath $SaveDir -Filter "*.zds" -File -Recurse | Sort-Object LastWriteTimeUtc -Descending)
if ($saveFiles.Count -lt 1) {
    throw "GZDoom stayed healthy for the save probe but did not create a .zds savegame under $SaveDir."
}
$saveFile = $saveFiles[0]
if ($saveFile.Length -lt 1024) {
    throw "Created savegame is unexpectedly small ($($saveFile.Length) bytes): $($saveFile.FullName)"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($saveFile.FullName)
try {
    if ($archive.Entries.Count -lt 3) {
        throw "Created savegame archive contains too few entries: $($archive.Entries.Count)"
    }

    $entryNames = @($archive.Entries | ForEach-Object { $_.FullName })
    if (-not ($entryNames -contains "globals.json")) {
        throw "Created savegame is missing globals.json and does not look like a valid modern GZDoom save."
    }
}
finally {
    $archive.Dispose()
}

Write-Host "Reloading the generated savegame in a fresh GZDoom process..."
$loadArguments = $common + @(
    "-loadgame", $saveFile.FullName
)
$loadText = Invoke-GZDoomProbe -Arguments $loadArguments -LogPath $LoadLog -Phase "load"

$combined = @(
    "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke",
    "Savegame: $($saveFile.FullName)",
    "Save bytes: $($saveFile.Length)",
    "",
    "===== SAVE PASS =====",
    $saveText,
    "===== LOAD PASS =====",
    $loadText,
    "Runtime save/load smoke: PASS"
) -join "`r`n"
Set-Content -LiteralPath $CombinedLog -Value $combined -Encoding UTF8

Write-Host "Runtime save/load smoke: PASS"
Write-Host "Created and reloaded $($saveFile.Name) with pinned GZDoom."
