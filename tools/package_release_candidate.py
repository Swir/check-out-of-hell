from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SOURCE_PK3 = DIST / "checkout-of-hell-prototype.pk3"
OUTPUT = DIST / "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"
CHECKSUM = OUTPUT.with_suffix(OUTPUT.suffix + ".sha256")
PACKAGED_PK3 = "game/CHECKOUT-OF-HELL.pk3"
MANIFEST_NAME = "package-manifest.json"
BUNDLED_FREEDOOM = "external/freedoom2.wad"
FREEDOOM_LICENSE = "licenses/FREEDOOM-COPYING.adoc"
FREEDOOM_PROVENANCE = "third_party/FREEDOOM-PROVENANCE.json"

README_FIRST = """CHECKOUT OF HELL — Windows Portable Release Candidate

THIS IS A CI RELEASE-CANDIDATE PACKAGE, NOT A PUBLIC DEMO RELEASE.

Player path
===========
1. Extract the whole ZIP to a normal writable folder.
2. Double-click PLAY.bat.
3. The launcher first verifies every bundled project/content file with SHA-256.
4. Freedoom v0.13.0 base content is already bundled from the official upstream
   release, verified against the official release checksum, and accompanied by
   its BSD 3-Clause notice and provenance record.
5. On first launch the launcher automatically obtains the pinned GZDoom engine
   from its official upstream release, then starts MAP01.
6. Later launches reuse the verified local GZDoom cache and can start offline.

You do NOT need to search for GZDoom, Freedoom, Python, WAD files, or any other
required runtime file manually.

The candidate deliberately redistributes only third-party content whose bundled
license obligations are handled here. GZDoom remains an official-source first-
run download instead of being copied into this package. Network or verification
failures stop with a clear error and never fall back to unofficial mirrors.

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


def get_source_snapshot() -> dict[str, str | bool | None]:
    """Return commit/branch/clean metadata without making Git a player dependency.

    Release-candidate builds run from a Git checkout in CI and in the target-Windows
    sign-off harness. Recording the source snapshot in the package manifest lets an
    extracted ZIP be tied back to the exact repository commit that produced it.
    The package still remains buildable from a source archive: unavailable Git
    metadata is recorded explicitly instead of being fabricated.
    """

    snapshot: dict[str, str | bool | None] = {
        "commit": "UNAVAILABLE",
        "branch": "UNAVAILABLE",
        "clean": None,
    }

    try:
        commit_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        commit = commit_result.stdout.strip().lower()
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError(f"Unexpected Git commit id: {commit!r}")
        snapshot["commit"] = commit

        branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or ""
        branch = branch.strip()
        if not branch:
            branch_result = subprocess.run(
                ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            branch = branch_result.stdout.strip()
        snapshot["branch"] = branch or "DETACHED"

        status_result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        snapshot["clean"] = not bool(status_result.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        # Source archives may not carry .git metadata. Keep the explicit
        # UNAVAILABLE/None markers instead of inventing provenance.
        pass

    return snapshot


def github_headers(url: str) -> dict[str, str]:
    headers = {
        "User-Agent": "checkout-of-hell-release-packager",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    return headers


def download_bytes(url: str, *, accept: str | None = None) -> bytes:
    headers = github_headers(url)
    if accept:
        headers["Accept"] = accept
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urlopen(Request(url, headers=headers), timeout=60) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2**attempt)
    raise SystemExit(f"Official upstream download failed after 3 attempts: {url}\n{last_error}")


def download_json(url: str) -> dict:
    try:
        return json.loads(download_bytes(url).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Official upstream response was not valid JSON: {url}\n{exc}") from exc


def select_release_asset(release: dict, pattern: str, description: str) -> dict:
    matcher = re.compile(pattern)
    matches = [asset for asset in release.get("assets", []) if matcher.search(asset.get("name", ""))]
    if not matches:
        raise SystemExit(f"Could not resolve {description} from official release {release.get('tag_name')!r}")
    return sorted(matches, key=lambda item: item["name"])[0]


def parse_official_checksum(checksum_bytes: bytes, asset_name: str) -> str:
    try:
        text = checksum_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit("Official Freedoom checksum asset is not UTF-8 text") from exc

    for line in text.splitlines():
        if asset_name not in line:
            continue
        match = re.search(r"\b([A-Fa-f0-9]{64})\b", line)
        if match:
            return match.group(1).lower()
    raise SystemExit(f"Official Freedoom checksum file has no SHA-256 entry for {asset_name}")


def find_zip_member(archive: zipfile.ZipFile, basename: str) -> str:
    matches = [name for name in archive.namelist() if Path(name).name.lower() == basename.lower()]
    if not matches:
        raise SystemExit(f"Official Freedoom archive is missing {basename}")
    return sorted(matches, key=lambda name: (name.count("/"), len(name), name))[0]


def build_freedoom_bundle(lock: dict) -> dict[str, bytes]:
    config = lock["freedoom"]
    repo = config["repo"]
    tag = config["tag"]
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    license_url = f"https://raw.githubusercontent.com/{repo}/{tag}/COPYING.adoc"
    release = download_json(release_url)
    if release.get("tag_name") != tag:
        raise SystemExit(f"Freedoom release tag mismatch: expected {tag}, got {release.get('tag_name')}")

    archive_asset = select_release_asset(release, config["asset_regex"], "Freedoom ZIP")
    checksum_asset = select_release_asset(release, config["checksum_regex"], "Freedoom checksum")

    archive_url = archive_asset["browser_download_url"]
    checksum_url = checksum_asset["browser_download_url"]
    checksum_bytes = download_bytes(checksum_url, accept="application/octet-stream")
    archive_bytes = download_bytes(archive_url, accept="application/octet-stream")

    expected_archive_hash = parse_official_checksum(checksum_bytes, archive_asset["name"])
    actual_archive_hash = digest(archive_bytes)
    if actual_archive_hash != expected_archive_hash:
        raise SystemExit(
            "Freedoom archive SHA-256 mismatch. "
            f"Expected {expected_archive_hash} but downloaded {actual_archive_hash}."
        )

    try:
        with zipfile.ZipFile(BytesIO(archive_bytes), "r") as archive:
            wad_member = find_zip_member(archive, "freedoom2.wad")
            wad = archive.read(wad_member)
    except zipfile.BadZipFile as exc:
        raise SystemExit("Official Freedoom release asset is not a valid ZIP archive") from exc

    # The v0.13.0 binary release ZIP does not carry COPYING.adoc, so obtain the
    # exact notice from the same pinned upstream repository tag. This remains an
    # official, immutable-source path and is recorded in the provenance file.
    license_text = download_bytes(license_url, accept="text/plain")

    if len(wad) < 1024 * 1024:
        raise SystemExit("Bundled Freedoom WAD looks unexpectedly small")
    try:
        decoded_license = license_text.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit("Freedoom COPYING.adoc is not UTF-8 text") from exc
    for required_text in (
        "Contributors to the Freedoom project",
        "Redistribution and use in source and binary forms",
        "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS",
    ):
        if required_text not in decoded_license:
            raise SystemExit(f"Freedoom COPYING.adoc is missing required notice text: {required_text}")

    provenance = {
        "schema": 1,
        "component": "Freedoom",
        "repo": repo,
        "tag": tag,
        "archive_asset": archive_asset["name"],
        "archive_url": archive_url,
        "checksum_asset": checksum_asset["name"],
        "checksum_url": checksum_url,
        "archive_sha256": actual_archive_hash,
        "wad_path": BUNDLED_FREEDOOM,
        "wad_sha256": digest(wad),
        "license_path": FREEDOOM_LICENSE,
        "license_url": license_url,
        "license_sha256": digest(license_text),
        "license": "BSD-3-Clause",
    }
    provenance_bytes = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")

    return {
        BUNDLED_FREEDOOM: wad,
        FREEDOOM_LICENSE: license_text,
        FREEDOOM_PROVENANCE: provenance_bytes,
    }


def build_entry_map() -> dict[str, bytes]:
    lock_bytes = read_required(ROOT / "runtime-lock.json")
    lock = json.loads(lock_bytes.decode("utf-8"))
    entries = {
        "PLAY.bat": read_required(ROOT / "packaging" / "PLAY-RC.bat"),
        "README-FIRST.txt": README_FIRST.encode("utf-8"),
        "runtime-lock.json": lock_bytes,
        "tools/bootstrap_runtime.ps1": read_required(ROOT / "tools" / "bootstrap_runtime.ps1"),
        "tools/verify_player_package.ps1": read_required(ROOT / "tools" / "verify_player_package.ps1"),
        "docs/THIRD_PARTY.md": read_required(ROOT / "docs" / "THIRD_PARTY.md"),
        "branding/icon.svg": read_required(ROOT / "branding" / "icon.svg"),
        "LICENSE": read_required(ROOT / "LICENSE"),
        PACKAGED_PK3: read_required(SOURCE_PK3),
    }
    entries.update(build_freedoom_bundle(lock))
    return entries


def build_manifest(entries: dict[str, bytes], source_snapshot: dict[str, str | bool | None]) -> bytes:
    lock = json.loads(entries["runtime-lock.json"].decode("utf-8"))
    manifest = {
        "schema": 1,
        "package_kind": "windows-portable-release-candidate",
        "public_release": False,
        "game_entry": PACKAGED_PK3,
        "source": source_snapshot,
        "runtime": {
            "gzdoom_tag": lock["gzdoom"]["tag"],
            "gzdoom_delivery": "official-source-bootstrap",
            "freedoom_tag": lock["freedoom"]["tag"],
            "freedoom_delivery": "bundled-verified-content",
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

    # Capture source identity before build outputs are generated. Tracked changes
    # are recorded, while untracked dist/cache files do not make a clean checkout
    # look dirty after repeated local packaging attempts.
    source_snapshot = get_source_snapshot()

    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=ROOT, check=True)
    if not SOURCE_PK3.is_file():
        raise SystemExit("PK3 build did not produce the expected package")

    entries = build_entry_map()
    manifest = build_manifest(entries, source_snapshot)
    write_zip(entries, manifest)

    archive_digest = digest(OUTPUT.read_bytes())
    CHECKSUM.write_text(f"{archive_digest}  {OUTPUT.name}\n", encoding="ascii")

    print(f"Release-candidate package: {OUTPUT}")
    print(f"SHA-256:                  {archive_digest}")
    print(
        "Source snapshot:           "
        f"{source_snapshot['commit']} / {source_snapshot['branch']} / clean={source_snapshot['clean']}"
    )
    print("Bundled project + Freedoom content files have an internal SHA-256 manifest.")
    print("Freedoom came from the pinned official release and passed its official checksum.")
    print("The exact BSD notice came from the same pinned upstream repository tag and is provenance-recorded.")
    print("GZDoom remains an official-source first-run download; no manual dependency hunting is required.")
    print("This CI artifact is not a public demo release.")


if __name__ == "__main__":
    main()
