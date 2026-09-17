#!/usr/bin/env python3
"""Resolve pinned official Linux GZDoom + Freedoom assets for CI.

This helper intentionally uses only Python's standard library and downloads only
assets published by the upstream GitHub releases named in runtime-lock.json.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "runtime-lock.json"
EXTERNAL = ROOT / "external"
CACHE = ROOT / ".cache" / "runtime-linux"
GZ_DEB = EXTERNAL / "gzdoom-linux.deb"
FREEDOOM_WAD = EXTERNAL / "freedoom2.wad"


def headers() -> dict[str, str]:
    result = {
        "User-Agent": "checkout-of-hell-linux-ci-bootstrap",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        result["Authorization"] = f"Bearer {token}"
    return result


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=headers())
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            print(f"Downloading {url}")
            req = urllib.request.Request(url, headers=headers())
            with urllib.request.urlopen(req, timeout=60) as response, destination.open("wb") as out:
                shutil.copyfileobj(response, out)
            if destination.stat().st_size == 0:
                raise RuntimeError(f"Downloaded file is empty: {destination}")
            return
        except (OSError, urllib.error.URLError, RuntimeError) as exc:
            last_error = exc
            if attempt < 3:
                delay = 2**attempt
                print(f"Download attempt {attempt} failed; retrying in {delay}s: {exc}")
                time.sleep(delay)
    raise RuntimeError(f"Download failed after 3 attempts: {url}\n{last_error}")


def release(repo: str, tag: str) -> dict:
    encoded_tag = urllib.parse.quote(tag, safe="")
    return request_json(f"https://api.github.com/repos/{repo}/releases/tags/{encoded_tag}")


def select_asset(data: dict, pattern: str, description: str) -> dict:
    regex = re.compile(pattern)
    for asset in data.get("assets", []):
        if regex.search(asset.get("name", "")):
            return asset
    raise RuntimeError(f"Could not find {description} in release {data.get('tag_name')!r}")


def parse_official_sha256(checksum_text: str, asset_name: str) -> str | None:
    escaped = re.escape(asset_name)
    # Freedoom publishes a clear-signed BSD-style checksum file, while some
    # upstream releases use the traditional sha256sum format. Accept both.
    bsd = re.search(
        rf"(?im)^\s*SHA256\s*\(\s*{escaped}\s*\)\s*=\s*([0-9a-f]{{64}})\s*$",
        checksum_text,
    )
    if bsd:
        return bsd.group(1).lower()
    coreutils = re.search(
        rf"(?im)^\s*([0-9a-f]{{64}})\s+[* ]?{escaped}\s*$",
        checksum_text,
    )
    return coreutils.group(1).lower() if coreutils else None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    gz = release(lock["gzdoom"]["repo"], lock["gzdoom"]["tag"])
    gz_asset = select_asset(gz, lock["gzdoom"]["linux_asset_regex"], "GZDoom Linux amd64 DEB")
    gz_cache = CACHE / gz_asset["name"]
    if not gz_cache.exists():
        download(gz_asset["browser_download_url"], gz_cache)
    shutil.copy2(gz_cache, GZ_DEB)
    if GZ_DEB.stat().st_size < 5 * 1024 * 1024:
        raise RuntimeError("Downloaded GZDoom DEB is unexpectedly small; refusing to continue")

    fd = release(lock["freedoom"]["repo"], lock["freedoom"]["tag"])
    fd_asset = select_asset(fd, lock["freedoom"]["asset_regex"], "Freedoom ZIP")
    fd_checksum = select_asset(fd, lock["freedoom"]["checksum_regex"], "Freedoom checksum")
    fd_zip = CACHE / fd_asset["name"]
    checksum_path = CACHE / fd_checksum["name"]
    if not fd_zip.exists():
        download(fd_asset["browser_download_url"], fd_zip)
    download(fd_checksum["browser_download_url"], checksum_path)

    expected = parse_official_sha256(checksum_path.read_text(encoding="utf-8", errors="replace"), fd_asset["name"])
    if expected is None:
        raise RuntimeError("Official Freedoom checksum file does not contain a SHA-256 entry for the pinned ZIP")
    actual = sha256(fd_zip)
    if actual != expected:
        raise RuntimeError(f"Freedoom SHA-256 mismatch. Expected {expected}, got {actual}")
    print("Freedoom SHA-256 verified.")

    with zipfile.ZipFile(fd_zip) as archive:
        candidates = [name for name in archive.namelist() if name.lower().endswith("/freedoom2.wad") or name.lower() == "freedoom2.wad"]
        if not candidates:
            raise RuntimeError("Pinned Freedoom ZIP does not contain freedoom2.wad")
        with archive.open(candidates[0]) as source, FREEDOOM_WAD.open("wb") as destination:
            shutil.copyfileobj(source, destination)
    if FREEDOOM_WAD.stat().st_size < 1024 * 1024:
        raise RuntimeError("Extracted freedoom2.wad is unexpectedly small")

    print(f"Pinned GZDoom Linux package: {gz.get('tag_name')} / {gz_asset['name']}")
    print(f"Pinned Freedoom: {fd.get('tag_name')} / {fd_asset['name']}")
    print(f"GZDoom DEB: {GZ_DEB}")
    print(f"Freedoom WAD: {FREEDOOM_WAD}")


if __name__ == "__main__":
    main()
