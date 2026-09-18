from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "runtime-lock.json").read_text(encoding="utf-8"))
package = (ROOT / "tools" / "package_release_candidate.py").read_text(encoding="utf-8")
bootstrap = (ROOT / "tools" / "bootstrap_runtime.ps1").read_text(encoding="utf-8")
verifier = (ROOT / "tools" / "verify_player_package.ps1").read_text(encoding="utf-8")
third_party = (ROOT / "docs" / "THIRD_PARTY.md").read_text(encoding="utf-8")
packaging = (ROOT / "docs" / "PACKAGING.md").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")

assert lock["freedoom"]["repo"] == "freedoom/freedoom"
assert lock["freedoom"]["tag"] == "v0.13.0"
assert lock["gzdoom"]["repo"] == "ZDoom/gzdoom"

for marker in (
    "https://api.github.com/repos/{repo}/releases/tags/{tag}",
    "browser_download_url",
    "checksum_asset",
    "parse_official_checksum",
    "freedoom2.wad",
    "COPYING.adoc",
    "FREEDOOM-PROVENANCE.json",
    '"license": "BSD-3-Clause"',
    '"freedoom_delivery": "bundled-verified-content"',
    '"gzdoom_delivery": "official-source-bootstrap"',
):
    assert marker in package, f"release-candidate builder missing legal-content marker: {marker}"

for forbidden in ("mediafire.com", "mega.nz", "dropbox.com", "drive.google.com"):
    assert forbidden not in package.lower()
    assert forbidden not in bootstrap.lower()

for marker in (
    "FREEDOOM-PROVENANCE.json",
    "Test-HashMatch",
    "if (-not $fdInstalled)",
    "if (-not $gzInstalled)",
    "bundled-verified-content",
    "api.github.com/repos/$Repo/releases/tags/$escapedTag",
):
    assert marker in bootstrap, f"runtime bootstrap missing bundled/cache-safe marker: {marker}"

for marker in (
    "external\\freedoom2.wad",
    "licenses\\FREEDOOM-COPYING.adoc",
    "third_party\\FREEDOOM-PROVENANCE.json",
    "BSD-3-Clause",
    "bundled-verified-content",
    "official-source-bootstrap",
):
    assert marker in verifier, f"player package verifier missing legal-content gate: {marker}"

for text, source in ((third_party, "THIRD_PARTY"), (packaging, "PACKAGING")):
    for marker in ("BSD 3-Clause", "official", "checksum", "GZDoom"):
        assert marker in text, f"{source} docs missing: {marker}"

assert "python tools/test_legal_content_package_contract.py" in workflow
assert "Build portable Windows release-candidate package" in workflow
assert "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in workflow

print("Standalone legal base-content packaging contract: PASS")
print("Freedoom bundling is pinned, official-source checksum verified, notice/provenance protected, and GZDoom remains official-source bootstrap.")
