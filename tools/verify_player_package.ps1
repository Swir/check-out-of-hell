[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $ProjectRoot "package-manifest.json"
$FreedoomWadPath = Join-Path $ProjectRoot "external\freedoom2.wad"
$FreedoomLicensePath = Join-Path $ProjectRoot "licenses\FREEDOOM-COPYING.adoc"
$FreedoomProvenancePath = Join-Path $ProjectRoot "third_party\FREEDOOM-PROVENANCE.json"

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    throw "package-manifest.json is missing. Re-extract the official CHECKOUT OF HELL package."
}

$Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if ($Manifest.schema -ne 1) {
    throw "Unsupported package manifest schema: $($Manifest.schema)"
}
if ($Manifest.package_kind -ne "windows-portable-release-candidate") {
    throw "Unexpected package kind: $($Manifest.package_kind)"
}
if ($Manifest.public_release -ne $false) {
    throw "This verifier expected a non-public release-candidate package."
}
if (-not $Manifest.entries) {
    throw "Package manifest has no integrity entries."
}
if ($Manifest.runtime.gzdoom_delivery -ne "official-source-bootstrap") {
    throw "Package manifest must keep GZDoom on the official-source bootstrap path."
}
if ($Manifest.runtime.freedoom_delivery -ne "bundled-verified-content") {
    throw "Package manifest must identify Freedoom as bundled verified content."
}

$Separator = [IO.Path]::DirectorySeparatorChar.ToString()
$RootFull = [IO.Path]::GetFullPath($ProjectRoot)
if (-not $RootFull.EndsWith($Separator)) {
    $RootFull += $Separator
}

$checked = 0
foreach ($property in $Manifest.entries.PSObject.Properties) {
    $relative = [string]$property.Name
    $record = $property.Value

    if ([string]::IsNullOrWhiteSpace($relative) -or [IO.Path]::IsPathRooted($relative)) {
        throw "Unsafe package manifest path: $relative"
    }

    $normalizedRelative = $relative.Replace('/', [IO.Path]::DirectorySeparatorChar)
    $fullPath = [IO.Path]::GetFullPath((Join-Path $ProjectRoot $normalizedRelative))
    if (-not $fullPath.StartsWith($RootFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Package manifest path escapes the extracted package: $relative"
    }
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Required packaged file is missing: $relative"
    }

    $expectedHash = ([string]$record.sha256).ToLowerInvariant()
    if ($expectedHash -notmatch '^[0-9a-f]{64}$') {
        throw "Invalid SHA-256 in package manifest for: $relative"
    }

    $actualLength = (Get-Item -LiteralPath $fullPath).Length
    $expectedLength = [int64]$record.bytes
    if ($actualLength -ne $expectedLength) {
        throw "Package size mismatch for $relative. Expected $expectedLength bytes but found $actualLength."
    }

    $actualHash = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $expectedHash) {
        throw "Package SHA-256 mismatch for $relative. Re-extract or re-download the official artifact."
    }

    $checked++
}

$gameEntry = [string]$Manifest.game_entry
if ([string]::IsNullOrWhiteSpace($gameEntry)) {
    throw "Package manifest does not name the game payload."
}

foreach ($requiredPath in @($FreedoomWadPath, $FreedoomLicensePath, $FreedoomProvenancePath)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Bundled legal content is incomplete: $requiredPath"
    }
}

if ((Get-Item -LiteralPath $FreedoomWadPath).Length -lt 1048576) {
    throw "Bundled freedoom2.wad looks unexpectedly small."
}

$FreedoomProvenance = Get-Content -LiteralPath $FreedoomProvenancePath -Raw | ConvertFrom-Json
if ($FreedoomProvenance.schema -ne 1 -or $FreedoomProvenance.component -ne "Freedoom") {
    throw "Bundled Freedoom provenance has an unsupported schema/component."
}
if ($FreedoomProvenance.tag -ne $Manifest.runtime.freedoom_tag) {
    throw "Bundled Freedoom provenance tag does not match the package runtime pin."
}
if ($FreedoomProvenance.license -ne "BSD-3-Clause") {
    throw "Bundled Freedoom provenance does not identify the BSD-3-Clause license."
}
if ($FreedoomProvenance.wad_path -ne "external/freedoom2.wad") {
    throw "Bundled Freedoom provenance points at an unexpected WAD path."
}
if ($FreedoomProvenance.license_path -ne "licenses/FREEDOOM-COPYING.adoc") {
    throw "Bundled Freedoom provenance points at an unexpected license path."
}

$wadHash = (Get-FileHash -LiteralPath $FreedoomWadPath -Algorithm SHA256).Hash.ToLowerInvariant()
$licenseHash = (Get-FileHash -LiteralPath $FreedoomLicensePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($wadHash -ne ([string]$FreedoomProvenance.wad_sha256).ToLowerInvariant()) {
    throw "Bundled Freedoom WAD does not match its provenance record."
}
if ($licenseHash -ne ([string]$FreedoomProvenance.license_sha256).ToLowerInvariant()) {
    throw "Bundled Freedoom license notice does not match its provenance record."
}
if ([string]$FreedoomProvenance.archive_url -notmatch '^https://github\.com/freedoom/freedoom/releases/download/') {
    throw "Bundled Freedoom provenance does not name an official GitHub release archive URL."
}
if ([string]$FreedoomProvenance.checksum_url -notmatch '^https://github\.com/freedoom/freedoom/releases/download/') {
    throw "Bundled Freedoom provenance does not name an official GitHub release checksum URL."
}

$licenseText = Get-Content -LiteralPath $FreedoomLicensePath -Raw
foreach ($requiredText in @(
    "Contributors to the Freedoom project",
    "Redistribution and use in source and binary forms",
    "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS"
)) {
    if (-not $licenseText.Contains($requiredText)) {
        throw "Bundled Freedoom BSD notice is incomplete: $requiredText"
    }
}

Write-Host "Package integrity verified: $checked files."
Write-Host "Game payload: $gameEntry"
Write-Host "Bundled legal base content: Freedoom $($Manifest.runtime.freedoom_tag) / BSD-3-Clause / provenance verified"
Write-Host "Engine delivery: GZDoom $($Manifest.runtime.gzdoom_tag) / official-source bootstrap"
