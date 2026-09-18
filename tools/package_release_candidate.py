from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SOURCE_PK3 = DIST / "checkout-of-hell-prototype.pk3"
OUTPUT = DIST / "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"
CHECKSUM = OUTPUT.with_suffix(OUTPUT.suffix + ".sha256")
PACKAGED_PK3 = "game/CHECKOUT-OF-HELL.pk3"
MANIFEST_NAME = "package-manifest.json"

README_FIRST = """CHECKOUT OF HELL — Windows Portable Release Candidate

THIS IS A CI RELEASE-CANDIDATE PACKAGE, NOT A PUBLIC DEMO RELEASE.

Player path
===========
1. Extract the whole ZIP to a normal writable folder.
2. Double-click PLAY.bat.
3. The launcher first verifies the bundled game/package files with SHA-256.
4. On first launch it automatically obtains the pinned GZDoom and Freedoom
   runtime from their official upstream releases and then starts MAP01.
5. Later launches reuse the verified local runtime cache.

You do NOT need to search for GZDoom, Freedoom, Python, WAD files, or any other
required runtime file manually.

The candidate intentionally does not redistribute third-party runtime EXE/WAD
files inside this ZIP. PLAY.bat obtains the pinned redistributable runtime from
official upstream release endpoints, while preserving explicit provenance and
third-party license boundaries. Network or verification failures stop with a
clear error instead of falling back to unofficial mirrors.

Project: https://github.com/Swir/check-out-of-hell
by Swir
"""


def deterministic_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o644 & 0xFFFF) << 16
    return info


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def read_required(path: Path) -> bytes:
    if not path.is_file():
        raise SystemExit(f"Release-candidate package input is missing: {path}")
    return path.read_bytes()


def build_entry_map() -> dict[str, bytes]:
    return {
        "PLAY.bat": read_required(ROOT / "packaging" / "PLAY-RC.bat"),
        "README-FIRST.txt": README_FIRST.encode("utf-8"),
        "runtime-lock.json": read_required(ROOT / "runtime-lock.json"),
        "tools/bootstrap_runtime.ps1": read_required(ROOT / "tools" / "bootstrap_runtime.ps1"),
        "tools/verify_player_package.ps1": read_required(ROOT / "tools" / "verify_player_package.ps1"),
        "docs/THIRD_PARTY.md": read_required(ROOT / "docs" / "THIRD_PARTY.md"),
        "branding/icon.svg": read_required(ROOT / "branding" / "icon.svg"),
        "LICENSE": read_required(ROOT / "LICENSE"),
        PACKAGED_PK3: read_required(SOURCE_PK3),
    }


def build_manifest(entries: dict[str, bytes]) -> bytes:
    lock = json.loads(entries["runtime-lock.json"].decode("utf-8"))
    manifest = {
        "schema": 1,
        "package_kind": "windows-portable-release-candidate",
        "public_release": False,
        "game_entry": PACKAGED_PK3,
        "runtime": {
            "gzdoom_tag": lock["gzdoom"]["tag"],
            "freedoom_tag": lock["freedoom"]["tag"],
        },
        "entries": {
            name: {
                "bytes": len(data),
                "sha256": digest(data),
            }
            for name, data in sorted(entries.items())
        },
    }
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_zip(entries: dict[str, bytes], manifest: bytes) -> None:
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(deterministic_info(name), data)
        archive.writestr(deterministic_info(MANIFEST_NAME), manifest)


def main() -> None:
    DIST.mkdir(exist_ok=True)

    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=ROOT, check=True)
    if not SOURCE_PK3.is_file():
        raise SystemExit("PK3 build did not produce the expected package")

    entries = build_entry_map()
    manifest = build_manifest(entries)
    write_zip(entries, manifest)

    archive_digest = digest(OUTPUT.read_bytes())
    CHECKSUM.write_text(f"{archive_digest}  {OUTPUT.name}\n", encoding="ascii")

    print(f"Release-candidate package: {OUTPUT}")
    print(f"SHA-256:                  {archive_digest}")
    print("Bundled project files have an internal SHA-256 manifest.")
    print("Pinned runtime EXE/WAD files remain official-source first-run downloads.")
    print("This CI artifact is not a public demo release.")


if __name__ == "__main__":
    main()
