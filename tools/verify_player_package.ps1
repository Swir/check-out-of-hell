[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $ProjectRoot "package-manifest.json"

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

$RootFull = [IO.Path]::GetFullPath($ProjectRoot)
if (-not $RootFull.EndsWith([IO.Path]::DirectorySeparatorChar)) {
    $RootFull += [IO.Path]::DirectorySeparatorChar
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

Write-Host "Package integrity verified: $checked files."
Write-Host "Game payload: $gameEntry"
Write-Host "Runtime pins: GZDoom $($Manifest.runtime.gzdoom_tag), Freedoom $($Manifest.runtime.freedoom_tag)"
