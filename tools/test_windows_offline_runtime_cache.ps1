[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageRoot
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$PackageRoot = (Resolve-Path -LiteralPath $PackageRoot).Path
$Verifier = Join-Path $PackageRoot "tools\verify_player_package.ps1"
$Bootstrap = Join-Path $PackageRoot "tools\bootstrap_runtime.ps1"
$LockPath = Join-Path $PackageRoot "runtime-lock.json"
$RuntimeManifestPath = Join-Path $PackageRoot "external\runtime-manifest.json"
$GZDoomExe = Join-Path $PackageRoot "external\gzdoom\gzdoom.exe"
$FreedoomWad = Join-Path $PackageRoot "external\freedoom2.wad"
$ArchiveCache = Join-Path $PackageRoot ".cache\runtime"

foreach ($required in @($Verifier, $Bootstrap, $LockPath, $FreedoomWad)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Offline-runtime gate input is missing: $required"
    }
}

Write-Host "Verifying extracted release-candidate payload before runtime preparation..."
& $Verifier

Write-Host "Priming the pinned runtime once from official upstream..."
& $Bootstrap

foreach ($required in @($RuntimeManifestPath, $GZDoomExe, $FreedoomWad)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Runtime preparation did not produce the required file: $required"
    }
}

$Lock = Get-Content -LiteralPath $LockPath -Raw | ConvertFrom-Json
$FirstManifest = Get-Content -LiteralPath $RuntimeManifestPath -Raw | ConvertFrom-Json
$GZDoomHashBefore = (Get-FileHash -LiteralPath $GZDoomExe -Algorithm SHA256).Hash.ToLowerInvariant()
$FreedoomHashBefore = (Get-FileHash -LiteralPath $FreedoomWad -Algorithm SHA256).Hash.ToLowerInvariant()

if ($FirstManifest.gzdoom.tag -ne $Lock.gzdoom.tag -or
    $FirstManifest.gzdoom.asset -ne $Lock.gzdoom.asset_name -or
    [Int64]$FirstManifest.gzdoom.asset_id -ne [Int64]$Lock.gzdoom.asset_id -or
    [Int64]$FirstManifest.gzdoom.archive_bytes -ne [Int64]$Lock.gzdoom.asset_bytes) {
    throw "Primed GZDoom runtime manifest does not match runtime-lock.json."
}
if ($FirstManifest.freedoom.tag -ne $Lock.freedoom.tag -or
    $FirstManifest.freedoom.delivery -ne "bundled-verified-content") {
    throw "Primed Freedoom runtime manifest does not identify the bundled verified content path."
}

# Remove downloaded archive/cache material. The second bootstrap is allowed to
# recreate the cache directory itself, but it must not need to put a file in it.
if (Test-Path -LiteralPath $ArchiveCache) {
    Remove-Item -LiteralPath $ArchiveCache -Recurse -Force
}

$OriginalDefaultProxy = [System.Net.WebRequest]::DefaultWebProxy
$OriginalHttpProxy = $env:HTTP_PROXY
$OriginalHttpsProxy = $env:HTTPS_PROXY
$OriginalAllProxy = $env:ALL_PROXY
$OriginalNoProxy = $env:NO_PROXY
$OriginalGitHubToken = $env:GITHUB_TOKEN

try {
    # Make accidental outbound HTTP(S) access fail immediately. The verified
    # second launch must succeed exclusively from installed files + provenance.
    $BlockedProxy = New-Object System.Net.WebProxy("http://127.0.0.1:9", $false)
    [System.Net.WebRequest]::DefaultWebProxy = $BlockedProxy
    $env:HTTP_PROXY = "http://127.0.0.1:9"
    $env:HTTPS_PROXY = "http://127.0.0.1:9"
    $env:ALL_PROXY = "http://127.0.0.1:9"
    $env:NO_PROXY = ""
    $env:GITHUB_TOKEN = ""

    Write-Host "Re-running the packaged bootstrap with outbound networking blocked..."
    & $Bootstrap
}
finally {
    [System.Net.WebRequest]::DefaultWebProxy = $OriginalDefaultProxy
    $env:HTTP_PROXY = $OriginalHttpProxy
    $env:HTTPS_PROXY = $OriginalHttpsProxy
    $env:ALL_PROXY = $OriginalAllProxy
    $env:NO_PROXY = $OriginalNoProxy
    $env:GITHUB_TOKEN = $OriginalGitHubToken
}

$CacheFiles = @()
if (Test-Path -LiteralPath $ArchiveCache) {
    $CacheFiles = @(Get-ChildItem -LiteralPath $ArchiveCache -Recurse -File -ErrorAction Stop)
}
if ($CacheFiles.Count -ne 0) {
    throw "Offline bootstrap unexpectedly created/downloaded runtime cache files: $($CacheFiles.FullName -join ', ')"
}

$GZDoomHashAfter = (Get-FileHash -LiteralPath $GZDoomExe -Algorithm SHA256).Hash.ToLowerInvariant()
$FreedoomHashAfter = (Get-FileHash -LiteralPath $FreedoomWad -Algorithm SHA256).Hash.ToLowerInvariant()
if ($GZDoomHashAfter -ne $GZDoomHashBefore) {
    throw "Offline runtime reuse changed the verified GZDoom executable."
}
if ($FreedoomHashAfter -ne $FreedoomHashBefore) {
    throw "Offline runtime reuse changed the verified Freedoom WAD."
}

$SecondManifest = Get-Content -LiteralPath $RuntimeManifestPath -Raw | ConvertFrom-Json
if ($SecondManifest.gzdoom.tag -ne $Lock.gzdoom.tag -or
    $SecondManifest.gzdoom.asset -ne $Lock.gzdoom.asset_name -or
    [Int64]$SecondManifest.gzdoom.asset_id -ne [Int64]$Lock.gzdoom.asset_id -or
    [Int64]$SecondManifest.gzdoom.archive_bytes -ne [Int64]$Lock.gzdoom.asset_bytes -or
    ([string]$SecondManifest.gzdoom.local_sha256).ToLowerInvariant() -ne $GZDoomHashAfter) {
    throw "Offline GZDoom reuse lost the pinned runtime identity/hash contract."
}
if ($SecondManifest.freedoom.tag -ne $Lock.freedoom.tag -or
    $SecondManifest.freedoom.delivery -ne "bundled-verified-content" -or
    ([string]$SecondManifest.freedoom.local_sha256).ToLowerInvariant() -ne $FreedoomHashAfter) {
    throw "Offline Freedoom reuse lost the bundled provenance/hash contract."
}

Write-Host "Offline verified-runtime reuse: PASS"
Write-Host "GZDoom $($Lock.gzdoom.tag) and Freedoom $($Lock.freedoom.tag) were reused with unchanged hashes after archive-cache removal while outbound networking was blocked."
