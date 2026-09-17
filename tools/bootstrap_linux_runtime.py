#!/usr/bin/env python3
"""Resolve pinned official Linux runtime files for CI/runtime validation.

This is deliberately separate from the player-facing Windows bootstrap. It reads the
same runtime-lock.json and downloads only official upstream GitHub release assets.
Freedoom is checksum-verified against the project's official release checksum file.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "runtime-lock.json"
EXTERNAL = ROOT / "external" / "linux"
CACHE = ROOT / ".cache" / "runtime-linux"
GZ_DEB = EXTERNAL / "gzdoom-pinned-amd64.deb"
FREEDOOM_WAD = EXTERNAL / "freedoom2.wad"
MANIFEST = EXTERNAL / "runtime-manifest.json"

HEADERS = {
    "User-Agent": "checkout-of-hell-linux-runtime-bootstrap",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if os.environ.get("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"


def request(url: str, *, binary: bool = False) -> bytes | str:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
            return data if binary else data.decode("utf-8")
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2**attempt)
    raise RuntimeError(f"Download failed after 3 attempts: {url}\n{last_error}")


def release(repo: str, tag: str) -> dict:
    safe_tag = urllib.parse.quote(tag, safe="")
    return json.loads(request(f"https://api.github.com/repos/{repo}/releases/tags/{safe_tag}"))


def asset_for(rel: dict, pattern: str, description: str) -> dict:
    regex = re.compile(pattern)
    for asset in rel.get("assets", []):
        if regex.search(asset.get("name", "")):
            return asset
    raise RuntimeError(f"Could not find {description} in release {rel.get('tag_name')!r}.")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = request(url, binary=True)
    assert isinstance(payload, bytes)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)
    tmp_path.replace(destination)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_freedoom(zip_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        candidates = [name for name in archive.namelist() if name.lower().endswith("/freedoom2.wad") or name.lower() == "freedoom2.wad"]
        if not candidates:
            raise RuntimeError("Official Freedoom archive does not contain freedoom2.wad.")
        member = candidates[0]
        with archive.open(member) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)
    if destination.stat().st_size < 1024 * 1024:
        raise RuntimeError("Extracted freedoom2.wad looks unexpectedly small.")


def main() -> int:
    if not LOCK_PATH.is_file():
        raise RuntimeError("runtime-lock.json is missing.")
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    gz_lock = lock["gzdoom"]
    fd_lock = lock["freedoom"]
    if "linux_asset_regex" not in gz_lock:
        raise RuntimeError("runtime-lock.json is missing gzdoom.linux_asset_regex.")

    gz_release = release(gz_lock["repo"], gz_lock["tag"])
    gz_asset = asset_for(gz_release, gz_lock["linux_asset_regex"], "GZDoom Linux amd64 package")
    fd_release = release(fd_lock["repo"], fd_lock["tag"])
    fd_asset = asset_for(fd_release, fd_lock["asset_regex"], "Freedoom ZIP")
    checksum_asset = asset_for(fd_release, fd_lock["checksum_regex"], "Freedoom checksum file")

    if "--dry-run" in sys.argv:
        print(f"GZDoom : {gz_release['tag_name']} / {gz_asset['name']}")
        print(f"Freedoom: {fd_release['tag_name']} / {fd_asset['name']}")
        print(f"Checksum: {checksum_asset['name']}")
        return 0

    EXTERNAL.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    print(f"Downloading pinned official GZDoom Linux package: {gz_asset['browser_download_url']}")
    download(gz_asset["browser_download_url"], GZ_DEB)
    if GZ_DEB.stat().st_size < 5 * 1024 * 1024:
        raise RuntimeError("Downloaded GZDoom package is unexpectedly small.")

    fd_zip = CACHE / fd_asset["name"]
    checksum_file = CACHE / checksum_asset["name"]
    print(f"Downloading pinned official Freedoom archive: {fd_asset['browser_download_url']}")
    download(fd_asset["browser_download_url"], fd_zip)
    download(checksum_asset["browser_download_url"], checksum_file)

    checksum_text = checksum_file.read_text(encoding="utf-8", errors="replace")
    matching = next((line for line in checksum_text.splitlines() if fd_asset["name"] in line), None)
    if not matching:
        raise RuntimeError(f"Official checksum file has no entry for {fd_asset['name']}.")
    match = re.search(r"\b([A-Fa-f0-9]{64})\b", matching)
    if not match:
        raise RuntimeError(f"Could not parse SHA-256 for {fd_asset['name']} from official checksum file.")
    expected = match.group(1).lower()
    actual = sha256(fd_zip)
    if actual != expected:
        raise RuntimeError(f"Freedoom SHA-256 mismatch: expected {expected}, got {actual}.")
    print("Freedoom SHA-256 verified against official release checksum.")

    extract_freedoom(fd_zip, FREEDOOM_WAD)

    manifest = {
        "schema": 1,
        "gzdoom": {
            "repo": gz_lock["repo"],
            "tag": gz_release["tag_name"],
            "asset": gz_asset["name"],
            "source": gz_asset["browser_download_url"],
            "local_sha256": sha256(GZ_DEB),
        },
        "freedoom": {
            "repo": fd_lock["repo"],
            "tag": fd_release["tag_name"],
            "asset": fd_asset["name"],
            "source": fd_asset["browser_download_url"],
            "local_sha256": sha256(FREEDOOM_WAD),
            "archive_sha256": actual,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"GZDoom package: {GZ_DEB}")
    print(f"Freedoom IWAD : {FREEDOOM_WAD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
