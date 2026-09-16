[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LockPath = Join-Path $ProjectRoot "runtime-lock.json"
$ExternalDir = Join-Path $ProjectRoot "external"
$CacheDir = Join-Path $ProjectRoot ".cache\runtime"
$GZDoomDir = Join-Path $ExternalDir "gzdoom"
$FreedoomWad = Join-Path $ExternalDir "freedoom2.wad"
$ManifestPath = Join-Path $ExternalDir "runtime-manifest.json"

if (-not (Test-Path -LiteralPath $LockPath)) {
    throw "runtime-lock.json is missing. The runtime cannot be resolved safely."
}

$Lock = Get-Content -LiteralPath $LockPath -Raw | ConvertFrom-Json
$Headers = @{
    "User-Agent" = "checkout-of-hell-bootstrap"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}
if ($env:GITHUB_TOKEN) {
    $Headers["Authorization"] = "Bearer $env:GITHUB_TOKEN"
}

function Ensure-Directory([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-PinnedRelease([string]$Repo, [string]$Tag) {
    $escapedTag = [uri]::EscapeDataString($Tag)
    $uri = "https://api.github.com/repos/$Repo/releases/tags/$escapedTag"
    return Invoke-RestMethod -Uri $uri -Headers $Headers -Method Get
}

function Select-ReleaseAsset($Release, [string]$Regex, [string]$Description) {
    $asset = $Release.assets | Where-Object { $_.name -match $Regex } | Select-Object -First 1
    if (-not $asset) {
        throw "Could not find $Description in release $($Release.tag_name)."
    }
    return $asset
}

function Download-WithRetry([string]$Url, [string]$Destination) {
    $lastError = $null
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            Write-Host "Downloading $Url"
            Invoke-WebRequest -Uri $Url -OutFile $Destination -Headers $Headers -UseBasicParsing
            return
        }
        catch {
            $lastError = $_
            if ($attempt -lt 3) {
                $delay = [math]::Pow(2, $attempt)
                Write-Warning "Download attempt $attempt failed. Retrying in $delay seconds..."
                Start-Sleep -Seconds $delay
            }
        }
    }
    throw "Download failed after 3 attempts: $Url`n$lastError"
}

$gzRelease = Get-PinnedRelease -Repo $Lock.gzdoom.repo -Tag $Lock.gzdoom.tag
$gzAsset = Select-ReleaseAsset -Release $gzRelease -Regex $Lock.gzdoom.asset_regex -Description "GZDoom Windows ZIP"
$fdRelease = Get-PinnedRelease -Repo $Lock.freedoom.repo -Tag $Lock.freedoom.tag
$fdAsset = Select-ReleaseAsset -Release $fdRelease -Regex $Lock.freedoom.asset_regex -Description "Freedoom ZIP"
$fdChecksumAsset = $fdRelease.assets | Where-Object { $_.name -match $Lock.freedoom.checksum_regex } | Select-Object -First 1

if ($DryRun) {
    Write-Host "Runtime lock resolved successfully."
    Write-Host "GZDoom : $($gzRelease.tag_name) / $($gzAsset.name)"
    Write-Host "Freedoom: $($fdRelease.tag_name) / $($fdAsset.name)"
    if ($fdChecksumAsset) { Write-Host "Checksum: $($fdChecksumAsset.name)" }
    exit 0
}

Ensure-Directory $ExternalDir
Ensure-Directory $CacheDir

$gzInstalled = Test-Path -LiteralPath (Join-Path $GZDoomDir "gzdoom.exe")
if ($Force -or -not $gzInstalled) {
    $gzZip = Join-Path $CacheDir $gzAsset.name
    $gzStage = Join-Path $CacheDir "gzdoom-stage"
    if (Test-Path -LiteralPath $gzStage) { Remove-Item -LiteralPath $gzStage -Recurse -Force }
    if ($Force -or -not (Test-Path -LiteralPath $gzZip)) {
        Download-WithRetry -Url $gzAsset.browser_download_url -Destination $gzZip
    }
    Ensure-Directory $gzStage
    Expand-Archive -LiteralPath $gzZip -DestinationPath $gzStage -Force
    $gzExe = Get-ChildItem -LiteralPath $gzStage -Recurse -Filter "gzdoom.exe" -File | Select-Object -First 1
    if (-not $gzExe) { throw "Downloaded GZDoom archive does not contain gzdoom.exe." }
    if (Test-Path -LiteralPath $GZDoomDir) { Remove-Item -LiteralPath $GZDoomDir -Recurse -Force }
    Ensure-Directory $GZDoomDir
    Copy-Item -Path (Join-Path $gzExe.Directory.FullName "*") -Destination $GZDoomDir -Recurse -Force
    if (-not (Test-Path -LiteralPath (Join-Path $GZDoomDir "gzdoom.exe"))) {
        throw "GZDoom extraction failed."
    }
    Remove-Item -LiteralPath $gzStage -Recurse -Force
}

$fdInstalled = Test-Path -LiteralPath $FreedoomWad
if ($Force -or -not $fdInstalled) {
    $fdZip = Join-Path $CacheDir $fdAsset.name
    $fdStage = Join-Path $CacheDir "freedoom-stage"
    if (Test-Path -LiteralPath $fdStage) { Remove-Item -LiteralPath $fdStage -Recurse -Force }
    if ($Force -or -not (Test-Path -LiteralPath $fdZip)) {
        Download-WithRetry -Url $fdAsset.browser_download_url -Destination $fdZip
    }

    if ($fdChecksumAsset) {
        $checksumFile = Join-Path $CacheDir $fdChecksumAsset.name
        Download-WithRetry -Url $fdChecksumAsset.browser_download_url -Destination $checksumFile
        $escapedName = [regex]::Escape($fdAsset.name)
        $checksumLine = Get-Content -LiteralPath $checksumFile | Where-Object { $_ -match $escapedName } | Select-Object -First 1
        if ($checksumLine -and $checksumLine -match "([A-Fa-f0-9]{64})") {
            $expected = $Matches[1].ToUpperInvariant()
            $actual = (Get-FileHash -LiteralPath $fdZip -Algorithm SHA256).Hash.ToUpperInvariant()
            if ($actual -ne $expected) {
                throw "Freedoom SHA-256 mismatch. Expected $expected but got $actual."
            }
            Write-Host "Freedoom SHA-256 verified."
        }
        else {
            Write-Warning "Official Freedoom checksum file was downloaded, but its SHA-256 entry could not be parsed."
        }
    }

    Ensure-Directory $fdStage
    Expand-Archive -LiteralPath $fdZip -DestinationPath $fdStage -Force
    $wad = Get-ChildItem -LiteralPath $fdStage -Recurse -Filter "freedoom2.wad" -File | Select-Object -First 1
    if (-not $wad) { throw "Downloaded Freedoom archive does not contain freedoom2.wad." }
    Copy-Item -LiteralPath $wad.FullName -Destination $FreedoomWad -Force
    if ((Get-Item -LiteralPath $FreedoomWad).Length -lt 1048576) {
        throw "freedoom2.wad looks unexpectedly small; refusing to continue."
    }
    Remove-Item -LiteralPath $fdStage -Recurse -Force
}

$manifest = [ordered]@{
    schema = 1
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    gzdoom = [ordered]@{
        repo = $Lock.gzdoom.repo
        tag = $gzRelease.tag_name
        asset = $gzAsset.name
        source = $gzAsset.browser_download_url
        local_sha256 = (Get-FileHash -LiteralPath (Join-Path $GZDoomDir "gzdoom.exe") -Algorithm SHA256).Hash
    }
    freedoom = [ordered]@{
        repo = $Lock.freedoom.repo
        tag = $fdRelease.tag_name
        asset = $fdAsset.name
        source = $fdAsset.browser_download_url
        local_sha256 = (Get-FileHash -LiteralPath $FreedoomWad -Algorithm SHA256).Hash
    }
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

Write-Host "Runtime ready."
Write-Host "GZDoom : $(Join-Path $GZDoomDir 'gzdoom.exe')"
Write-Host "Freedoom: $FreedoomWad"
