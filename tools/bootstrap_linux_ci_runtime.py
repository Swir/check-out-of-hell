#!/usr/bin/env python3
"""Resolve pinned GZDoom/Freedoom Linux CI assets from official upstream releases.

This is CI-only tooling. Player/runtime bootstrap remains PLAY.bat + PowerShell on Windows.
The resolver intentionally uses the pinned tags from runtime-lock.json and official GitHub
Release API/browser_download_url endpoints only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "runtime-lock.json"
OUT = ROOT / "external" / "linux-ci"
USER_AGENT = "checkout-of-hell-ci-runtime/1.0"


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=60) as response, destination.open("wb") as output:
            shutil.copyfileobj(response, output)
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def release(repo: str, tag: str) -> dict:
    return request_json(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")


def select_asset(payload: dict, pattern: str, label: str) -> dict:
    rx = re.compile(pattern, re.IGNORECASE)
    matches = [asset for asset in payload.get("assets", []) if rx.match(asset.get("name", ""))]
    if len(matches) != 1:
        names = ", ".join(asset.get("name", "?") for asset in payload.get("assets", []))
        raise RuntimeError(f"Expected one {label} asset matching {pattern!r}; found {len(matches)}. Assets: {names}")
    asset = matches[0]
    url = asset.get("browser_download_url", "")
    if not url.startswith("https://github.com/"):
        raise RuntimeError(f"Refusing non-official {label} URL: {url}")
    return asset


def verify_freedoom_checksum(archive: Path, checksum: Path) -> None:
    expected = None
    archive_name = archive.name
    for line in checksum.read_text(encoding="utf-8", errors="replace").splitlines():
        if archive_name not in line:
            continue
        match = re.search(r"\b([0-9a-fA-F]{64})\b", line)
        if match:
            expected = match.group(1).lower()
            break
    if not expected:
        raise RuntimeError(f"Official checksum file does not contain SHA-256 for {archive_name}")
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(f"Freedoom SHA-256 mismatch: expected {expected}, got {actual}")


def main() -> int:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    gz = lock["gzdoom"]
    fd = lock["freedoom"]

    OUT.mkdir(parents=True, exist_ok=True)

    gz_release = release(gz["repo"], gz["tag"])
    # Official GZDoom releases publish the Linux amd64 package as gzdoom_4.14.2_amd64.deb.
    version = gz["tag"].lstrip("g")
    gz_asset = select_asset(gz_release, rf"^gzdoom_{re.escape(version)}_amd64\.deb$", "GZDoom Linux")
    gz_deb = OUT / gz_asset["name"]
    if not gz_deb.exists() or gz_deb.stat().st_size != int(gz_asset.get("size", -1)):
        print(f"Downloading official GZDoom Linux package: {gz_asset['browser_download_url']}")
        download(gz_asset["browser_download_url"], gz_deb)

    fd_release = release(fd["repo"], fd["tag"])
    fd_asset = select_asset(fd_release, fd["asset_regex"], "Freedoom")
    checksum_asset = select_asset(fd_release, fd["checksum_regex"], "Freedoom checksum")
    fd_zip = OUT / fd_asset["name"]
    checksum = OUT / checksum_asset["name"]
    if not fd_zip.exists() or fd_zip.stat().st_size != int(fd_asset.get("size", -1)):
        print(f"Downloading official Freedoom archive: {fd_asset['browser_download_url']}")
        download(fd_asset["browser_download_url"], fd_zip)
    if not checksum.exists() or checksum.stat().st_size != int(checksum_asset.get("size", -1)):
        print(f"Downloading official Freedoom checksum: {checksum_asset['browser_download_url']}")
        download(checksum_asset["browser_download_url"], checksum)
    verify_freedoom_checksum(fd_zip, checksum)
    print("Freedoom SHA-256 verified against official checksum.")

    fd_extract = OUT / "freedoom"
    if fd_extract.exists():
        shutil.rmtree(fd_extract)
    with zipfile.ZipFile(fd_zip) as archive:
        archive.extractall(fd_extract)
    wads = list(fd_extract.rglob("freedoom2.wad"))
    if len(wads) != 1:
        raise RuntimeError(f"Expected exactly one freedoom2.wad, found {len(wads)}")

    manifest = {
        "gzdoom_deb": str(gz_deb),
        "freedoom_wad": str(wads[0]),
        "gzdoom_tag": gz["tag"],
        "freedoom_tag": fd["tag"],
    }
    manifest_path = OUT / "runtime.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Linux CI runtime manifest: {manifest_path}")
    print(f"GZDoom package: {gz_deb}")
    print(f"Freedoom IWAD: {wads[0]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
