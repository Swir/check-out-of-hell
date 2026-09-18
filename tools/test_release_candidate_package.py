from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE = DIST / "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"
CHECKSUM = PACKAGE.with_suffix(PACKAGE.suffix + ".sha256")

if not PACKAGE.is_file():
    raise SystemExit("Release-candidate package is missing. Run: python tools/package_release_candidate.py")
if not CHECKSUM.is_file():
    raise SystemExit("Release-candidate package checksum is missing")

required = {
    "PLAY.bat",
    "README-FIRST.txt",
    "package-manifest.json",
    "runtime-lock.json",
    "tools/bootstrap_runtime.ps1",
    "tools/verify_player_package.ps1",
    "docs/THIRD_PARTY.md",
    "branding/icon.svg",
    "LICENSE",
    "game/CHECKOUT-OF-HELL.pk3",
}

with zipfile.ZipFile(PACKAGE, "r") as archive:
    names = set(archive.namelist())
    missing = required - names
    if missing:
        raise SystemExit(f"Release-candidate package entries missing: {sorted(missing)}")

    forbidden_runtime = [
        name for name in names
        if name.lower().endswith((".exe", ".wad"))
    ]
    if forbidden_runtime:
        raise SystemExit(
            "Release-candidate artifact must keep runtime EXE/WAD acquisition in the official-source bootstrap: "
            f"{forbidden_runtime}"
        )

    source_leaks = [
        name for name in names
        if name.startswith("game/") and name != "game/CHECKOUT-OF-HELL.pk3"
    ]
    if source_leaks:
        raise SystemExit(f"Release-candidate artifact unexpectedly contains game source files: {source_leaks}")

    launcher = archive.read("PLAY.bat").decode("utf-8", errors="strict").lower()
    ordered_markers = [
        "verify_player_package.ps1",
        "bootstrap_runtime.ps1",
        "game\checkout-of-hell.pk3",
    ]
    positions = [launcher.find(marker) for marker in ordered_markers]
    if any(position < 0 for position in positions):
        raise SystemExit("Release-candidate PLAY.bat is missing integrity/bootstrap/game launch wiring")
    if positions != sorted(positions):
        raise SystemExit("Release-candidate PLAY.bat must verify before bootstrapping and launching")
    if "python" in launcher or "build.py" in launcher or "bootstrap_python" in launcher:
        raise SystemExit("Release-candidate PLAY.bat must not require Python or a source build toolchain")
    if "official upstream" not in launcher:
        raise SystemExit("Release-candidate launcher must explain the official-upstream runtime policy")

    readme = archive.read("README-FIRST.txt").decode("utf-8", errors="strict")
    if "NOT A PUBLIC DEMO RELEASE" not in readme:
        raise SystemExit("Release-candidate README must not imply that a public demo exists")
    if "You do NOT need to search" not in readme:
        raise SystemExit("Release-candidate README must preserve the no-manual-dependency-search contract")
    if "SHA-256" not in readme:
        raise SystemExit("Release-candidate README must explain local package integrity verification")

    manifest = json.loads(archive.read("package-manifest.json").decode("utf-8"))
    if manifest.get("schema") != 1:
        raise SystemExit("Unexpected release-candidate package manifest schema")
    if manifest.get("package_kind") != "windows-portable-release-candidate":
        raise SystemExit("Unexpected release-candidate package kind")
    if manifest.get("public_release") is not False:
        raise SystemExit("Release-candidate package must explicitly remain non-public-release metadata")
    if manifest.get("game_entry") != "game/CHECKOUT-OF-HELL.pk3":
        raise SystemExit("Release-candidate manifest names the wrong game payload")

    entries = manifest.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise SystemExit("Release-candidate manifest has no integrity entries")
    if set(entries) != required - {"package-manifest.json"}:
        raise SystemExit("Release-candidate manifest entries do not exactly cover packaged project files")

    for name, record in entries.items():
        data = archive.read(name)
        expected_hash = record.get("sha256")
        expected_size = record.get("bytes")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            raise SystemExit(f"Manifest SHA-256 is invalid for {name}")
        if expected_size != len(data):
            raise SystemExit(f"Manifest byte count mismatch for {name}")
        if sha256(data).hexdigest() != expected_hash:
            raise SystemExit(f"Manifest SHA-256 mismatch for {name}")

    lock = json.loads(archive.read("runtime-lock.json").decode("utf-8"))
    expected_runtime = {
        "gzdoom_tag": lock["gzdoom"]["tag"],
        "freedoom_tag": lock["freedoom"]["tag"],
    }
    if manifest.get("runtime") != expected_runtime:
        raise SystemExit("Release-candidate manifest runtime pins do not match runtime-lock.json")

    game_info = archive.getinfo("game/CHECKOUT-OF-HELL.pk3")
    if game_info.file_size < 1024:
        raise SystemExit("Release-candidate game PK3 looks unexpectedly small")

checksum_text = CHECKSUM.read_text(encoding="ascii").strip()
match = re.fullmatch(r"([0-9a-f]{64})\s{2}(.+)", checksum_text)
if not match:
    raise SystemExit("Release-candidate checksum sidecar has an unexpected format")
if match.group(2) != PACKAGE.name:
    raise SystemExit("Release-candidate checksum sidecar names the wrong artifact")
if sha256(PACKAGE.read_bytes()).hexdigest() != match.group(1):
    raise SystemExit("Release-candidate package SHA-256 sidecar does not match the ZIP")

print("Windows portable release-candidate package contract: PASS")
print("Artifact is prebuilt, Python-free, locally integrity-checked, official-source runtime capable, and not public-released.")
