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
$GZDoomExe = Join-Path $GZDoomDir "gzdoom.exe"
$FreedoomWad = Join-Path $ExternalDir "freedoom2.wad"
$ManifestPath = Join-Path $ExternalDir "runtime-manifest.json"
$BundledFreedoomProvenancePath = Join-Path $ProjectRoot "third_party\FREEDOOM-PROVENANCE.json"

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
    $asset = $Release.assets | Where-Object { $_.name -match $Regex } | Sort-Object name | Select-Object -First 1
    if (-not $asset) {
        throw "Could not find $Description in release $($Release.tag_name)."
    }
    return $asset
}

function Assert-PinnedReleaseAsset($Asset, $Config, [string]$Description) {
    $expectedName = [string]$Config.asset_name
    $expectedId = [Int64]$Config.asset_id
    $expectedBytes = [Int64]$Config.asset_bytes

    if ([string]::IsNullOrWhiteSpace($expectedName) -or $expectedId -le 0 -or $expectedBytes -le 0) {
        throw "$Description identity is incomplete in runtime-lock.json. Expected asset_name, asset_id and asset_bytes."
    }
    if ([string]$Asset.name -ne $expectedName) {
        throw "$Description name drifted from runtime-lock.json. Expected '$expectedName' but official release metadata returned '$($Asset.name)'."
    }
    if ([Int64]$Asset.id -ne $expectedId) {
        throw "$Description GitHub asset ID drifted from runtime-lock.json. Expected $expectedId but official release metadata returned $($Asset.id). Refusing a silent re-upload/replacement."
    }
    if ([Int64]$Asset.size -ne $expectedBytes) {
        throw "$Description byte size drifted from runtime-lock.json. Expected $expectedBytes but official release metadata returned $($Asset.size)."
    }
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

function Read-JsonFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        Write-Warning "Ignoring unreadable JSON metadata: $Path"
        return $null
    }
}

function Test-HashMatch([string]$Path, [string]$ExpectedHash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }
    if ([string]::IsNullOrWhiteSpace($ExpectedHash) -or $ExpectedHash -notmatch '^[A-Fa-f0-9]{64}$') {
        return $false
    }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    return $actual.Equals($ExpectedHash, [StringComparison]::OrdinalIgnoreCase)
}

$ExistingManifest = Read-JsonFile $ManifestPath
$BundledFreedoomProvenance = Read-JsonFile $BundledFreedoomProvenancePath

if ($DryRun) {
    $gzRelease = Get-PinnedRelease -Repo $Lock.gzdoom.repo -Tag $Lock.gzdoom.tag
    $gzAsset = Select-ReleaseAsset -Release $gzRelease -Regex $Lock.gzdoom.asset_regex -Description "GZDoom Windows ZIP"
    Assert-PinnedReleaseAsset -Asset $gzAsset -Config $Lock.gzdoom -Description "GZDoom Windows release asset"
    $fdRelease = Get-PinnedRelease -Repo $Lock.freedoom.repo -Tag $Lock.freedoom.tag
    $fdAsset = Select-ReleaseAsset -Release $fdRelease -Regex $Lock.freedoom.asset_regex -Description "Freedoom ZIP"
    $fdChecksumAsset = Select-ReleaseAsset -Release $fdRelease -Regex $Lock.freedoom.checksum_regex -Description "Freedoom checksum"

    Write-Host "Runtime lock resolved successfully."
    Write-Host "GZDoom : $($gzRelease.tag_name) / $($gzAsset.name) / asset $($gzAsset.id) / $($gzAsset.size) bytes"
    Write-Host "Freedoom: $($fdRelease.tag_name) / $($fdAsset.name)"
    Write-Host "Checksum: $($fdChecksumAsset.name)"
    exit 0
}

Ensure-Directory $ExternalDir
Ensure-Directory $CacheDir

$gzInstalled = $false
$gzManifestAsset = $null
$gzManifestAssetId = $null
$gzManifestArchiveBytes = $null
$gzManifestSource = $null
if (-not $Force -and (Test-Path -LiteralPath $GZDoomExe -PathType Leaf) -and $ExistingManifest -and $ExistingManifest.gzdoom) {
    $identityMatches = (
        [string]$ExistingManifest.gzdoom.asset -eq [string]$Lock.gzdoom.asset_name -and
        [Int64]$ExistingManifest.gzdoom.asset_id -eq [Int64]$Lock.gzdoom.asset_id -and
        [Int64]$ExistingManifest.gzdoom.archive_bytes -eq [Int64]$Lock.gzdoom.asset_bytes
    )
    if ($ExistingManifest.gzdoom.tag -eq $Lock.gzdoom.tag -and $identityMatches -and (Test-HashMatch -Path $GZDoomExe -ExpectedHash ([string]$ExistingManifest.gzdoom.local_sha256))) {
        $gzInstalled = $true
        $gzManifestAsset = [string]$ExistingManifest.gzdoom.asset
        $gzManifestAssetId = [Int64]$ExistingManifest.gzdoom.asset_id
        $gzManifestArchiveBytes = [Int64]$ExistingManifest.gzdoom.archive_bytes
        $gzManifestSource = [string]$ExistingManifest.gzdoom.source
        Write-Host "Using verified cached GZDoom $($Lock.gzdoom.tag) with pinned release-asset identity."
    }
    else {
        Write-Warning "Cached GZDoom does not match the pinned verified runtime/asset identity record; it will be refreshed."
    }
}

$fdInstalled = $false
$fdManifestAsset = $null
$fdManifestSource = $null
if (-not $Force -and (Test-Path -LiteralPath $FreedoomWad -PathType Leaf)) {
    if ($BundledFreedoomProvenance -and
        $BundledFreedoomProvenance.tag -eq $Lock.freedoom.tag -and
        (Test-HashMatch -Path $FreedoomWad -ExpectedHash ([string]$BundledFreedoomProvenance.wad_sha256))) {
        $fdInstalled = $true
        $fdManifestAsset = [string]$BundledFreedoomProvenance.archive_asset
        $fdManifestSource = [string]$BundledFreedoomProvenance.archive_url
        Write-Host "Using bundled, provenance-verified Freedoom $($Lock.freedoom.tag)."
    }
    elseif ($ExistingManifest -and $ExistingManifest.freedoom -and
        $ExistingManifest.freedoom.tag -eq $Lock.freedoom.tag -and
        (Test-HashMatch -Path $FreedoomWad -ExpectedHash ([string]$ExistingManifest.freedoom.local_sha256))) {
        $fdInstalled = $true
        $fdManifestAsset = [string]$ExistingManifest.freedoom.asset
        $fdManifestSource = [string]$ExistingManifest.freedoom.source
        Write-Host "Using verified cached Freedoom $($Lock.freedoom.tag)."
    }
    else {
        Write-Warning "Existing Freedoom data has no matching verified provenance; it will be refreshed from official upstream."
    }
}

if (-not $gzInstalled) {
    $gzRelease = Get-PinnedRelease -Repo $Lock.gzdoom.repo -Tag $Lock.gzdoom.tag
    $gzAsset = Select-ReleaseAsset -Release $gzRelease -Regex $Lock.gzdoom.asset_regex -Description "GZDoom Windows ZIP"
    Assert-PinnedReleaseAsset -Asset $gzAsset -Config $Lock.gzdoom -Description "GZDoom Windows release asset"
    $gzZip = Join-Path $CacheDir $gzAsset.name
    $gzStage = Join-Path $CacheDir "gzdoom-stage"

    if (Test-Path -LiteralPath $gzStage) { Remove-Item -LiteralPath $gzStage -Recurse -Force }

    $downloadGZDoom = $Force -or -not (Test-Path -LiteralPath $gzZip -PathType Leaf)
    if (-not $downloadGZDoom) {
        $cachedBytes = (Get-Item -LiteralPath $gzZip).Length
        if ([Int64]$cachedBytes -ne [Int64]$Lock.gzdoom.asset_bytes) {
            Write-Warning "Cached GZDoom archive has the wrong byte count; discarding it before an official-source refresh."
            Remove-Item -LiteralPath $gzZip -Force
            $downloadGZDoom = $true
        }
    }
    if ($downloadGZDoom) {
        Download-WithRetry -Url $gzAsset.browser_download_url -Destination $gzZip
    }

    $gzArchiveBytes = (Get-Item -LiteralPath $gzZip).Length
    if ([Int64]$gzArchiveBytes -ne [Int64]$Lock.gzdoom.asset_bytes) {
        Remove-Item -LiteralPath $gzZip -Force -ErrorAction SilentlyContinue
        throw "GZDoom archive byte count mismatch after download. Expected $($Lock.gzdoom.asset_bytes) but got $gzArchiveBytes. Refusing to extract unpinned content."
    }

    Ensure-Directory $gzStage
    Expand-Archive -LiteralPath $gzZip -DestinationPath $gzStage -Force
    $gzExe = Get-ChildItem -LiteralPath $gzStage -Recurse -Filter "gzdoom.exe" -File | Select-Object -First 1
    if (-not $gzExe) { throw "Downloaded GZDoom archive does not contain gzdoom.exe." }

    if (Test-Path -LiteralPath $GZDoomDir) { Remove-Item -LiteralPath $GZDoomDir -Recurse -Force }
    Ensure-Directory $GZDoomDir
    Copy-Item -Path (Join-Path $gzExe.Directory.FullName "*") -Destination $GZDoomDir -Recurse -Force
    if (-not (Test-Path -LiteralPath $GZDoomExe)) {
        throw "GZDoom extraction failed."
    }
    Remove-Item -LiteralPath $gzStage -Recurse -Force

    $gzManifestAsset = [string]$gzAsset.name
    $gzManifestAssetId = [Int64]$gzAsset.id
    $gzManifestArchiveBytes = [Int64]$gzArchiveBytes
    $gzManifestSource = [string]$gzAsset.browser_download_url
}

if (-not $fdInstalled) {
    $fdRelease = Get-PinnedRelease -Repo $Lock.freedoom.repo -Tag $Lock.freedoom.tag
    $fdAsset = Select-ReleaseAsset -Release $fdRelease -Regex $Lock.freedoom.asset_regex -Description "Freedoom ZIP"
    $fdChecksumAsset = Select-ReleaseAsset -Release $fdRelease -Regex $Lock.freedoom.checksum_regex -Description "Freedoom checksum"
    $fdZip = Join-Path $CacheDir $fdAsset.name
    $fdStage = Join-Path $CacheDir "freedoom-stage"
    if (Test-Path -LiteralPath $fdStage) { Remove-Item -LiteralPath $fdStage -Recurse -Force }
    if ($Force -or -not (Test-Path -LiteralPath $fdZip)) {
        Download-WithRetry -Url $fdAsset.browser_download_url -Destination $fdZip
    }

    $checksumFile = Join-Path $CacheDir $fdChecksumAsset.name
    Download-WithRetry -Url $fdChecksumAsset.browser_download_url -Destination $checksumFile
    $escapedName = [regex]::Escape($fdAsset.name)
    $checksumLine = Get-Content -LiteralPath $checksumFile | Where-Object { $_ -match $escapedName } | Select-Object -First 1
    if (-not $checksumLine -or $checksumLine -notmatch "([A-Fa-f0-9]{64})") {
        throw "Official Freedoom checksum file does not contain a parsable SHA-256 entry for $($fdAsset.name)."
    }
    $expected = $Matches[1].ToUpperInvariant()
    $actual = (Get-FileHash -LiteralPath $fdZip -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actual -ne $expected) {
        throw "Freedoom SHA-256 mismatch. Expected $expected but got $actual."
    }
    Write-Host "Freedoom archive SHA-256 verified."

    Ensure-Directory $fdStage
    Expand-Archive -LiteralPath $fdZip -DestinationPath $fdStage -Force
    $wad = Get-ChildItem -LiteralPath $fdStage -Recurse -Filter "freedoom2.wad" -File | Select-Object -First 1
    if (-not $wad) { throw "Downloaded Freedoom archive does not contain freedoom2.wad." }
    Copy-Item -LiteralPath $wad.FullName -Destination $FreedoomWad -Force
    if ((Get-Item -LiteralPath $FreedoomWad).Length -lt 1048576) {
        throw "freedoom2.wad looks unexpectedly small; refusing to continue."
    }
    Remove-Item -LiteralPath $fdStage -Recurse -Force

    $fdManifestAsset = [string]$fdAsset.name
    $fdManifestSource = [string]$fdAsset.browser_download_url
}

if (-not (Test-Path -LiteralPath $GZDoomExe -PathType Leaf)) {
    throw "Pinned GZDoom runtime is not available after bootstrap."
}
if (-not (Test-Path -LiteralPath $FreedoomWad -PathType Leaf)) {
    throw "Pinned Freedoom content is not available after bootstrap."
}

$manifest = [ordered]@{
    schema = 1
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    gzdoom = [ordered]@{
        repo = $Lock.gzdoom.repo
        tag = $Lock.gzdoom.tag
        asset = $gzManifestAsset
        asset_id = $gzManifestAssetId
        archive_bytes = $gzManifestArchiveBytes
        source = $gzManifestSource
        local_sha256 = (Get-FileHash -LiteralPath $GZDoomExe -Algorithm SHA256).Hash
    }
    freedoom = [ordered]@{
        repo = $Lock.freedoom.repo
        tag = $Lock.freedoom.tag
        asset = $fdManifestAsset
        source = $fdManifestSource
        local_sha256 = (Get-FileHash -LiteralPath $FreedoomWad -Algorithm SHA256).Hash
        delivery = $(if ($BundledFreedoomProvenance -and $BundledFreedoomProvenance.tag -eq $Lock.freedoom.tag -and (Test-HashMatch -Path $FreedoomWad -ExpectedHash ([string]$BundledFreedoomProvenance.wad_sha256))) { "bundled-verified-content" } else { "official-source-bootstrap" })
    }
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

Write-Host "Runtime ready."
Write-Host "GZDoom : $GZDoomExe"
Write-Host "Freedoom: $FreedoomWad"
