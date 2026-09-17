[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GZDoomExe = Join-Path $ProjectRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $ProjectRoot "external\freedoom2.wad"
$Pk3 = Join-Path $ProjectRoot "dist\checkout-of-hell-prototype.pk3"
$WorkDir = Join-Path $ProjectRoot "dist\save-load-smoke"
$SaveDir = Join-Path $WorkDir "saves"
$RuntimeLog = Join-Path $ProjectRoot "dist\gzdoom-save-load-smoke.log"
$CreateCfg = Join-Path $WorkDir "create-save.cfg"
$LoadCfg = Join-Path $WorkDir "load-save.cfg"
$SaveInspector = Join-Path $PSScriptRoot "inspect_gzdoom_save.py"

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

foreach ($required in @($GZDoomExe, $FreedoomWad, $Pk3, $SaveInspector)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Save/load smoke prerequisite is missing: $required"
    }
}

if (Test-Path -LiteralPath $WorkDir) {
    Remove-Item -LiteralPath $WorkDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $SaveDir | Out-Null
if (Test-Path -LiteralPath $RuntimeLog) {
    Remove-Item -LiteralPath $RuntimeLog -Force
}

# +map is converted by GZDoom into an autostart map before the main loop. The
# startup exec therefore only needs to defer state mutation/save commands until
# the level has ticked. The load pass uses GZDoom's native -loadgame path.
'wait 70; god; give CheckoutFuse 2; give CorporateMemo 1; wait 4; save coh-save-load-ci "CHECKOUT OF HELL CI SAVE"; wait 35; quit' |
    Set-Content -LiteralPath $CreateCfg -Encoding ASCII
'wait 70; save coh-save-load-ci-roundtrip "CHECKOUT OF HELL CI ROUNDTRIP"; wait 35; quit' |
    Set-Content -LiteralPath $LoadCfg -Encoding ASCII

function Invoke-GZDoomScenario {
    param(
        [string]$Label,
        [string]$ConfigPath,
        [string[]]$ExtraArguments = @()
    )

    Write-Host "Running GZDoom $Label scenario..."
    $stdoutPath = Join-Path $WorkDir "$Label.stdout.log"
    $stderrPath = Join-Path $WorkDir "$Label.stderr.log"
    foreach ($path in @($stdoutPath, $stderrPath)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }

    $arguments = @(
        "-stdout",
        "-nosound",
        "-window",
        "-width", "320",
        "-height", "200",
        "+vid_activeinbackground", "true",
        "-savedir", $SaveDir,
        "-iwad", $FreedoomWad,
        "-file", $Pk3
    ) + $ExtraArguments + @(
        "+exec", $ConfigPath
    )

    # GZDoom is a Windows GUI executable. Track it explicitly, and force active
    # background ticking because hosted CI never gives the render window focus.
    $process = Start-Process -FilePath $GZDoomExe `
        -ArgumentList $arguments `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru

    if (-not $process.WaitForExit(20000)) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $diagnostic = @()
        foreach ($path in @($stdoutPath, $stderrPath)) {
            if (Test-Path -LiteralPath $path) {
                $diagnostic += @(Get-Content -LiteralPath $path -ErrorAction SilentlyContinue | ForEach-Object { "$_" })
            }
        }
        Add-Content -LiteralPath $RuntimeLog -Value "=== $Label TIMEOUT ===" -Encoding UTF8
        if ($diagnostic.Count -gt 0) {
            $diagnostic | Add-Content -LiteralPath $RuntimeLog -Encoding UTF8
        }
        Write-SaveDirectory -Label "$Label timeout"
        throw "GZDoom $Label scenario timed out after 20 seconds. See $RuntimeLog"
    }
    $exitCode = $process.ExitCode

    $outputLines = @()
    foreach ($path in @($stdoutPath, $stderrPath)) {
        if (Test-Path -LiteralPath $path) {
            $outputLines += @(Get-Content -LiteralPath $path -ErrorAction SilentlyContinue | ForEach-Object { "$_" })
        }
    }

    Add-Content -LiteralPath $RuntimeLog -Value "=== $Label (exit $exitCode) ===" -Encoding UTF8
    if ($outputLines.Count -gt 0) {
        $outputLines | Add-Content -LiteralPath $RuntimeLog -Encoding UTF8
        $outputLines | ForEach-Object { Write-Host $_ }
    }

    if ($exitCode -ne 0) {
        throw "GZDoom $Label scenario failed with exit code $exitCode. See $RuntimeLog"
    }

    $text = $outputLines -join "`n"
    foreach ($pattern in @(
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Invalid parameter",
        "Parse error",
        "Cannot execute unsafe command",
        "Save failed"
    )) {
        if ($text -match [regex]::Escape($pattern)) {
            throw "GZDoom $Label scenario reported '$pattern'. See $RuntimeLog"
        }
    }
}

function Write-SaveDirectory {
    param([string]$Label)

    Add-Content -LiteralPath $RuntimeLog -Value "--- $Label save directory ---" -Encoding UTF8
    $files = @(Get-ChildItem -LiteralPath $SaveDir -File -ErrorAction SilentlyContinue)
    if ($files.Count -eq 0) {
        Add-Content -LiteralPath $RuntimeLog -Value "(empty)" -Encoding UTF8
        return
    }
    foreach ($file in $files) {
        Add-Content -LiteralPath $RuntimeLog -Value "$($file.Name) - $($file.Length) bytes" -Encoding UTF8
    }
}

function Get-SingleSave {
    param(
        [string]$Pattern,
        [string]$Label
    )

    $matches = @(Get-ChildItem -LiteralPath $SaveDir -Filter $Pattern -File -ErrorAction SilentlyContinue)
    if ($matches.Count -ne 1) {
        Write-SaveDirectory -Label "$Label lookup failure"
        throw "Expected exactly one $Label savegame matching '$Pattern' in $SaveDir, found $($matches.Count). See $RuntimeLog"
    }
    if ($matches[0].Length -lt 1024) {
        throw "$Label savegame is unexpectedly small: $($matches[0].Length) bytes."
    }
    return $matches[0]
}

function Test-SaveState {
    param(
        [System.IO.FileInfo]$SaveFile,
        [string]$Label
    )

    Write-Host "Inspecting $Label save archive: $($SaveFile.FullName)"
    $inspection = @(python $SaveInspector $SaveFile.FullName CheckoutFuse CorporateMemo 2>&1 | ForEach-Object { "$_" })
    $inspectionExit = $LASTEXITCODE
    Add-Content -LiteralPath $RuntimeLog -Value "--- $Label archive inspection (exit $inspectionExit) ---" -Encoding UTF8
    if ($inspection.Count -gt 0) {
        $inspection | Add-Content -LiteralPath $RuntimeLog -Encoding UTF8
        $inspection | ForEach-Object { Write-Host $_ }
    }
    if ($inspectionExit -ne 0) {
        throw "$Label save archive did not preserve required serialized game state. See $RuntimeLog"
    }
}

Invoke-GZDoomScenario -Label "create-save" -ConfigPath $CreateCfg -ExtraArguments @("+map", "MAP01")
Write-SaveDirectory -Label "after create-save"
$initialSave = Get-SingleSave -Pattern "*coh-save-load-ci*.zds" -Label "initial"
Test-SaveState -SaveFile $initialSave -Label "initial"

Invoke-GZDoomScenario -Label "load-save" -ConfigPath $LoadCfg -ExtraArguments @("-loadgame", "coh-save-load-ci")
Write-SaveDirectory -Label "after load-save"
$roundTripSave = Get-SingleSave -Pattern "*coh-save-load-ci-roundtrip*.zds" -Label "round-trip"
Test-SaveState -SaveFile $roundTripSave -Label "round-trip"

Add-Content -LiteralPath $RuntimeLog -Value "Initial save: $($initialSave.Length) bytes" -Encoding UTF8
Add-Content -LiteralPath $RuntimeLog -Value "Round-trip save: $($roundTripSave.Length) bytes" -Encoding UTF8
Add-Content -LiteralPath $RuntimeLog -Value "Required serialized objective state: CheckoutFuse, CorporateMemo" -Encoding UTF8

Write-Host "Pinned GZDoom save/load smoke test: PASS"
