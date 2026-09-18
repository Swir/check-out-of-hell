from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = (ROOT / "tools" / "test_windows_offline_runtime_cache.ps1").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
packaging = (ROOT / "docs" / "PACKAGING.md").read_text(encoding="utf-8")

for marker in (
    "verify_player_package.ps1",
    "bootstrap_runtime.ps1",
    "runtime-lock.json",
    "runtime-manifest.json",
    ".cache\\runtime",
    "Get-FileHash",
    "[System.Net.WebRequest]::DefaultWebProxy",
    "http://127.0.0.1:9",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "GITHUB_TOKEN",
    "asset_id",
    "archive_bytes",
    '"bundled-verified-content"',
    "CacheFiles.Count -ne 0",
    "Offline verified-runtime reuse: PASS",
):
    assert marker in script, f"Windows offline-runtime gate missing: {marker}"

assert script.index("& $Verifier") < script.index("& $Bootstrap"), "package must be verified before runtime priming"
assert script.index("Remove-Item -LiteralPath $ArchiveCache") < script.index("Re-running the packaged bootstrap"), (
    "archive cache must be removed before the offline reuse pass"
)
assert script.count("& $Bootstrap") == 2, "gate must perform exactly one online prime and one blocked-network reuse pass"

for marker in (
    "python tools/test_windows_offline_runtime_cache_contract.py",
    "test_windows_offline_runtime_cache.ps1",
    "Prove extracted RC verified-runtime reuse without network",
):
    assert marker in workflow, f"GitHub Actions missing offline-runtime gate wiring: {marker}"

for marker in (
    "offline reuse",
    "archive cache",
    "outbound networking",
    "unchanged hashes",
):
    assert marker.lower() in packaging.lower(), f"PACKAGING docs missing offline-runtime evidence: {marker}"

print("Windows offline verified-runtime reuse contract: PASS")
print("The extracted RC is integrity-checked, primed once, stripped of download archives, then revalidated with outbound HTTP(S) blocked and unchanged runtime hashes required.")
