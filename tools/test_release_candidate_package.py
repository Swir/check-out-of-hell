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

BUNDLED_FREEDOOM = "external/freedoom2.wad"
FREEDOOM_LICENSE = "licenses/FREEDOOM-COPYING.adoc"
FREEDOOM_PROVENANCE = "third_party/FREEDOOM-PROVENANCE.json"

if not PACKAGE.is_file():
    raise SystemExit("Release-candidate package is missing. Run: python tools/package_release_candidate.py")
if not CHECKSUM.is_file():
    raise SystemExit("Release-candidate package checksum is missing")

required = {
    "PLAY.bat",
    "PLAYTEST-WINDOWS.bat",
    "README-FIRST.txt",
    "package-manifest.json",
    "runtime-lock.json",
    "tools/bootstrap_runtime.ps1",
    "tools/verify_player_package.ps1",
    "tools/windows_playtest_assistant.ps1",
    "docs/THIRD_PARTY.md",
    "docs/WINDOWS_PLAYTEST.md",
    "branding/icon.svg",
    "LICENSE",
    "game/CHECKOUT-OF-HELL.pk3",
    BUNDLED_FREEDOOM,
    FREEDOOM_LICENSE,
    FREEDOOM_PROVENANCE,
}

with zipfile.ZipFile(PACKAGE, "r") as archive:
    names = set(archive.namelist())
    missing = required - names
    if missing:
        raise SystemExit(f"Release-candidate package entries missing: {sorted(missing)}")

    forbidden_executables = [name for name in names if name.lower().endswith(".exe")]
    if forbidden_executables:
        raise SystemExit(
            "Release-candidate artifact must keep the GZDoom engine in the official-source bootstrap: "
            f"{forbidden_executables}"
        )

    unexpected_wads = [name for name in names if name.lower().endswith(".wad") and name != BUNDLED_FREEDOOM]
    if unexpected_wads:
        raise SystemExit(f"Release-candidate artifact contains unexpected WAD data: {unexpected_wads}")

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
        r"game\checkout-of-hell.pk3",
    ]
    positions = [launcher.find(marker) for marker in ordered_markers]
    if any(position < 0 for position in positions):
        raise SystemExit("Release-candidate PLAY.bat is missing integrity/bootstrap/game launch wiring")
    if positions != sorted(positions):
        raise SystemExit("Release-candidate PLAY.bat must verify before bootstrapping and launching")
    if "python" in launcher or "build.py" in launcher or "bootstrap_python" in launcher:
        raise SystemExit("Release-candidate PLAY.bat must not require Python or a source build toolchain")
    if "official upstream" not in launcher:
        raise SystemExit("Release-candidate launcher must explain the official-upstream GZDoom policy")
    if "freedoom base content is bundled" not in launcher:
        raise SystemExit("Release-candidate launcher must explain that verified Freedoom content is bundled")

    playtest_launcher = archive.read("PLAYTEST-WINDOWS.bat").decode("utf-8", errors="strict").lower()
    if "windows_playtest_assistant.ps1" not in playtest_launcher:
        raise SystemExit("Release-candidate playtest launcher is not wired to the evidence assistant")
    if "auto-approve" not in playtest_launcher or "publish" not in playtest_launcher:
        raise SystemExit("Release-candidate playtest launcher must state that it cannot authorize/publish a demo")

    playtest_script = archive.read("tools/windows_playtest_assistant.ps1").decode("utf-8", errors="strict")
    for marker in (
        'public_release_authorized = $false',
        '"manual_save_quit_load"',
        '"physical_controller"',
        '"real_hardware_performance"',
        "Get-FileHash",
        "bootstrap_runtime.ps1",
        "Start-Process -FilePath $GZDoomExe",
    ):
        if marker not in playtest_script:
            raise SystemExit(f"Release-candidate playtest assistant is missing required evidence behavior: {marker}")

    readme = archive.read("README-FIRST.txt").decode("utf-8", errors="strict")
    for phrase in (
        "NOT A PUBLIC DEMO RELEASE",
        "You do NOT need to search",
        "SHA-256",
        "Freedoom v0.13.0 base content is already bundled",
        "GZDoom engine",
        "official upstream",
        "PLAYTEST-WINDOWS.bat",
        "never publishes a release or auto-approves the demo",
    ):
        if phrase not in readme:
            raise SystemExit(f"Release-candidate README is missing required player/legal wording: {phrase}")

    manifest = json.loads(archive.read("package-manifest.json").decode("utf-8"))
    if manifest.get("schema") != 1:
        raise SystemExit("Unexpected release-candidate package manifest schema")
    if manifest.get("package_kind") != "windows-portable-release-candidate":
        raise SystemExit("Unexpected release-candidate package kind")
    if manifest.get("public_release") is not False:
        raise SystemExit("Release-candidate package must explicitly remain non-public-release metadata")
    if manifest.get("game_entry") != "game/CHECKOUT-OF-HELL.pk3":
        raise SystemExit("Release-candidate manifest names the wrong game payload")

    source = manifest.get("source")
    if not isinstance(source, dict):
        raise SystemExit("Release-candidate manifest must record source identity")
    commit = source.get("commit")
    branch = source.get("branch")
    if not isinstance(commit, str) or not commit or not (commit == "unknown" or re.fullmatch(r"[0-9a-fA-F]{40}", commit)):
        raise SystemExit("Release-candidate manifest source commit is invalid")
    if not isinstance(branch, str) or not branch:
        raise SystemExit("Release-candidate manifest source branch is invalid")

    entries = manifest.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise SystemExit("Release-candidate manifest has no integrity entries")
    if set(entries) != required - {"package-manifest.json"}:
        raise SystemExit("Release-candidate manifest entries do not exactly cover packaged files")

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
        "gzdoom_delivery": "official-source-bootstrap",
        "freedoom_tag": lock["freedoom"]["tag"],
        "freedoom_delivery": "bundled-verified-content",
    }
    if manifest.get("runtime") != expected_runtime:
        raise SystemExit("Release-candidate manifest runtime delivery/pins do not match the package policy")

    game_info = archive.getinfo("game/CHECKOUT-OF-HELL.pk3")
    if game_info.file_size < 1024:
        raise SystemExit("Release-candidate game PK3 looks unexpectedly small")

    wad = archive.read(BUNDLED_FREEDOOM)
    if len(wad) < 1024 * 1024:
        raise SystemExit("Bundled Freedoom WAD looks unexpectedly small")

    license_text = archive.read(FREEDOOM_LICENSE).decode("utf-8", errors="strict")
    for phrase in (
        "Contributors to the Freedoom project",
        "Redistribution and use in source and binary forms",
        "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS",
    ):
        if phrase not in license_text:
            raise SystemExit(f"Bundled Freedoom license notice is incomplete: {phrase}")

    provenance = json.loads(archive.read(FREEDOOM_PROVENANCE).decode("utf-8"))
    if provenance.get("schema") != 1 or provenance.get("component") != "Freedoom":
        raise SystemExit("Bundled Freedoom provenance has an unexpected schema/component")
    if provenance.get("repo") != lock["freedoom"]["repo"] or provenance.get("tag") != lock["freedoom"]["tag"]:
        raise SystemExit("Bundled Freedoom provenance does not match runtime-lock.json")
    if provenance.get("license") != "BSD-3-Clause":
        raise SystemExit("Bundled Freedoom provenance must identify BSD-3-Clause")
    if provenance.get("wad_path") != BUNDLED_FREEDOOM or provenance.get("license_path") != FREEDOOM_LICENSE:
        raise SystemExit("Bundled Freedoom provenance points at unexpected package paths")

    for key in ("archive_sha256", "wad_sha256", "license_sha256"):
        value = provenance.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise SystemExit(f"Bundled Freedoom provenance has invalid {key}")
    if provenance["wad_sha256"] != sha256(wad).hexdigest():
        raise SystemExit("Bundled Freedoom provenance WAD SHA-256 does not match package content")
    if provenance["license_sha256"] != sha256(archive.read(FREEDOOM_LICENSE)).hexdigest():
        raise SystemExit("Bundled Freedoom provenance license SHA-256 does not match package content")

    expected_download_prefix = (
        f"https://github.com/{lock['freedoom']['repo']}/releases/download/{lock['freedoom']['tag']}/"
    )
    if not str(provenance.get("archive_url", "")).startswith(expected_download_prefix):
        raise SystemExit("Bundled Freedoom archive provenance is not an official pinned release URL")
    if not str(provenance.get("checksum_url", "")).startswith(expected_download_prefix):
        raise SystemExit("Bundled Freedoom checksum provenance is not an official pinned release URL")
    if not re.fullmatch(lock["freedoom"]["asset_regex"], str(provenance.get("archive_asset", ""))):
        raise SystemExit("Bundled Freedoom archive asset does not match runtime-lock.json")
    if not re.fullmatch(lock["freedoom"]["checksum_regex"], str(provenance.get("checksum_asset", ""))):
        raise SystemExit("Bundled Freedoom checksum asset does not match runtime-lock.json")

checksum_text = CHECKSUM.read_text(encoding="ascii").strip()
match = re.fullmatch(r"([0-9a-f]{64})\s{2}(.+)", checksum_text)
if not match:
    raise SystemExit("Release-candidate checksum sidecar has an unexpected format")
if match.group(2) != PACKAGE.name:
    raise SystemExit("Release-candidate checksum sidecar names the wrong artifact")
if sha256(PACKAGE.read_bytes()).hexdigest() != match.group(1):
    raise SystemExit("Release-candidate package SHA-256 sidecar does not match the ZIP")

print("Windows portable release-candidate package contract: PASS")
print("Artifact is Python-free, locally integrity-checked, bundles verified BSD-licensed Freedoom content, includes non-authorizing Windows sign-off evidence tooling, uses official-source GZDoom bootstrap, and is not public-released.")
