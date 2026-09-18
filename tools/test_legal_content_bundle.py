from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CONTENT = DIST / "CHECKOUT-OF-HELL-Legal-Content-rc.zip"
CONTENT_SHA = CONTENT.with_suffix(CONTENT.suffix + ".sha256")
PLAYER = DIST / "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"

GAME_ENTRY = "game/CHECKOUT-OF-HELL.pk3"
FREEDOOM = "external/freedoom2.wad"
FREEDOOM_LICENSE = "licenses/FREEDOOM-COPYING.adoc"
FREEDOOM_PROVENANCE = "third_party/FREEDOOM-PROVENANCE.json"

required = {
    "README-CONTENT.txt",
    "content-manifest.json",
    "runtime-lock.json",
    "docs/THIRD_PARTY.md",
    "LICENSE",
    GAME_ENTRY,
    FREEDOOM,
    FREEDOOM_LICENSE,
    FREEDOOM_PROVENANCE,
}

for path in (CONTENT, CONTENT_SHA, PLAYER):
    if not path.is_file():
        raise SystemExit(f"Required packaging artifact is missing: {path.name}")

with zipfile.ZipFile(CONTENT, "r") as archive, zipfile.ZipFile(PLAYER, "r") as player:
    names = set(archive.namelist())
    if names != required:
        raise SystemExit(
            "Standalone legal content bundle must contain exactly the audited content set; "
            f"missing={sorted(required - names)} extra={sorted(names - required)}"
        )

    forbidden = [
        name for name in names
        if name.lower().endswith((".exe", ".dll", ".bat", ".ps1"))
    ]
    if forbidden:
        raise SystemExit(f"Content-only bundle unexpectedly contains executable/bootstrap files: {forbidden}")

    readme = archive.read("README-CONTENT.txt").decode("utf-8", errors="strict")
    for phrase in (
        "CONTENT-ONLY CI ARTIFACT",
        "NOT A PUBLIC PLAYER PACKAGE OR DEMO RELEASE",
        "does NOT redistribute a GZDoom executable",
        "No player is expected to hunt",
        "by Swir",
    ):
        if phrase not in readme:
            raise SystemExit(f"Content bundle README is missing required wording: {phrase}")

    manifest = json.loads(archive.read("content-manifest.json").decode("utf-8"))
    if manifest.get("schema") != 1:
        raise SystemExit("Unexpected legal-content manifest schema")
    if manifest.get("package_kind") != "legal-content-release-candidate":
        raise SystemExit("Unexpected legal-content package kind")
    if manifest.get("public_release") is not False or manifest.get("content_only") is not True:
        raise SystemExit("Legal-content bundle must be explicit content-only, non-public RC metadata")
    if manifest.get("game_entry") != GAME_ENTRY or manifest.get("base_content_entry") != FREEDOOM:
        raise SystemExit("Legal-content manifest points at unexpected payload entries")
    if manifest.get("licenses") != {"project": "MIT", "freedoom": "BSD-3-Clause"}:
        raise SystemExit("Legal-content manifest license summary is incomplete or unexpected")

    source = manifest.get("source")
    if not isinstance(source, dict):
        raise SystemExit("Legal-content manifest is missing source provenance")
    commit = source.get("commit")
    branch = source.get("branch")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit("Legal-content manifest source commit is not a full Git SHA")
    if not isinstance(branch, str) or not branch.strip() or branch == "UNAVAILABLE":
        raise SystemExit("Legal-content manifest source branch/ref is unavailable")
    if source.get("clean") is not True:
        raise SystemExit("CI legal-content bundle must come from a clean tracked source snapshot")

    try:
        checkout_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().lower()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Could not resolve checkout commit for content provenance verification: {exc}") from exc
    if commit != checkout_commit:
        raise SystemExit(
            "Legal-content bundle source commit does not match the checkout validating it: "
            f"manifest={commit} checkout={checkout_commit}"
        )

    lock = json.loads(archive.read("runtime-lock.json").decode("utf-8"))
    runtime = manifest.get("runtime")
    expected_runtime = {
        "gzdoom_tag": lock["gzdoom"]["tag"],
        "gzdoom_included": False,
        "gzdoom_delivery": "official-source-bootstrap-via-player-package",
        "freedoom_tag": lock["freedoom"]["tag"],
        "freedoom_delivery": "bundled-verified-content",
    }
    if runtime != expected_runtime:
        raise SystemExit("Legal-content manifest runtime/content delivery policy does not match runtime-lock.json")

    entries = manifest.get("entries")
    if not isinstance(entries, dict) or set(entries) != required - {"content-manifest.json"}:
        raise SystemExit("Legal-content manifest does not exactly cover bundled payload files")
    for name, record in entries.items():
        data = archive.read(name)
        if record.get("bytes") != len(data):
            raise SystemExit(f"Legal-content manifest byte count mismatch for {name}")
        expected_hash = record.get("sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            raise SystemExit(f"Legal-content manifest SHA-256 is invalid for {name}")
        if sha256(data).hexdigest() != expected_hash:
            raise SystemExit(f"Legal-content manifest SHA-256 mismatch for {name}")

    # The standalone content artifact is not a second independently assembled payload.
    # Every shared file must be byte-for-byte identical to the verified Windows RC.
    for name in required - {"README-CONTENT.txt", "content-manifest.json"}:
        if name not in player.namelist():
            raise SystemExit(f"Player RC is missing legal-content entry {name}")
        if archive.read(name) != player.read(name):
            raise SystemExit(f"Legal-content bundle drifted from player RC entry {name}")

    provenance = json.loads(archive.read(FREEDOOM_PROVENANCE).decode("utf-8"))
    wad = archive.read(FREEDOOM)
    license_bytes = archive.read(FREEDOOM_LICENSE)
    if provenance.get("license") != "BSD-3-Clause":
        raise SystemExit("Freedoom provenance must identify BSD-3-Clause")
    if provenance.get("wad_sha256") != sha256(wad).hexdigest():
        raise SystemExit("Freedoom WAD provenance hash does not match content bundle")
    if provenance.get("license_sha256") != sha256(license_bytes).hexdigest():
        raise SystemExit("Freedoom license provenance hash does not match content bundle")

    official_prefix = f"https://github.com/{lock['freedoom']['repo']}/releases/download/{lock['freedoom']['tag']}/"
    if not str(provenance.get("archive_url", "")).startswith(official_prefix):
        raise SystemExit("Freedoom archive provenance is not the pinned official release URL")
    if not str(provenance.get("checksum_url", "")).startswith(official_prefix):
        raise SystemExit("Freedoom checksum provenance is not the pinned official release URL")

checksum_text = CONTENT_SHA.read_text(encoding="ascii").strip()
match = re.fullmatch(r"([0-9a-f]{64})\s{2}(.+)", checksum_text)
if not match or match.group(2) != CONTENT.name:
    raise SystemExit("Legal-content SHA-256 sidecar has an unexpected format or filename")
if sha256(CONTENT.read_bytes()).hexdigest() != match.group(1):
    raise SystemExit("Legal-content SHA-256 sidecar does not match the ZIP")

print("Standalone legal content release-candidate contract: PASS")
print("Content bundle is commit-bound, manifest-verified, engine-free, license/provenance-complete and byte-identical to the legal content embedded in the Windows RC.")
