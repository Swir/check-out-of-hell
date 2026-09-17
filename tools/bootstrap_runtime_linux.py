#!/usr/bin/env python3
"""Resolve the pinned official Linux GZDoom + Freedoom CI runtime.

This helper is intentionally CI/developer tooling. Player-facing Windows bootstrap
remains tools/bootstrap_runtime.ps1 and continues to use the Windows release asset.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "runtime-lock.json"
RUNTIME_DIR = ROOT / "external" / "linux-runtime"
CACHE_DIR = ROOT / ".cache" / "linux-runtime"
GZ_DEB = RUNTIME_DIR / "gzdoom.deb"
FREEDOOM_WAD = RUNTIME_DIR / "freedoom2.wad"
MANIFEST = RUNTIME_DIR / "runtime-manifest.json"


def request(url: str) -> urllib.request.Request:
    headers = {
        "User-Agent": "checkout-of-hell-linux-runtime-bootstrap",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def fetch_bytes(url: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request(url), timeout=45) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2**attempt)
    raise RuntimeError(f"Download failed after 3 attempts: {url}\n{last_error}")


def fetch_json(url: str) -> dict:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def pinned_release(repo: str, tag: str) -> dict:
    safe_tag = urllib.parse.quote(tag, safe="")
    return fetch_json(f"https://api.github.com/repos/{repo}/releases/tags/{safe_tag}")


def select_asset(release: dict, pattern: str, description: str) -> dict:
    matcher = re.compile(pattern)
    matches = [asset for asset in release.get("assets", []) if matcher.search(asset.get("name", ""))]
    if len(matches) != 1:
        names = ", ".join(asset.get("name", "") for asset in release.get("assets", []))
        raise RuntimeError(
            f"Expected exactly one {description} matching {pattern!r} in "
            f"{release.get('tag_name')}; found {len(matches)}. Assets: {names}"
        )
    return matches[0]


def write_download(asset: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading official release asset: {asset['browser_download_url']}")
    destination.write_bytes(fetch_bytes(asset["browser_download_url"]))
    if destination.stat().st_size < 1024:
        raise RuntimeError(f"Downloaded asset looks unexpectedly small: {destination}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if not LOCK_PATH.exists():
        raise RuntimeError("runtime-lock.json is missing; refusing unpinned runtime resolution.")

    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    gz_lock = lock["gzdoom"]
    fd_lock = lock["freedoom"]
    linux_pattern = gz_lock.get("linux_asset_regex")
    if not linux_pattern:
        raise RuntimeError("runtime-lock.json is missing gzdoom.linux_asset_regex.")

    gz_release = pinned_release(gz_lock["repo"], gz_lock["tag"])
    fd_release = pinned_release(fd_lock["repo"], fd_lock["tag"])
    gz_asset = select_asset(gz_release, linux_pattern, "official GZDoom amd64 Debian package")
    fd_asset = select_asset(fd_release, fd_lock["asset_regex"], "official Freedoom ZIP")
    checksum_asset = select_asset(fd_release, fd_lock["checksum_regex"], "official Freedoom checksum")

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    gz_cache = CACHE_DIR / gz_asset["name"]
    fd_cache = CACHE_DIR / fd_asset["name"]
    checksum_cache = CACHE_DIR / checksum_asset["name"]
    if not gz_cache.exists():
        write_download(gz_asset, gz_cache)
    if not fd_cache.exists():
        write_download(fd_asset, fd_cache)
    write_download(checksum_asset, checksum_cache)

    checksum_text = checksum_cache.read_text(encoding="utf-8", errors="replace")
    expected = None
    for line in checksum_text.splitlines():
        if fd_asset["name"] in line:
            match = re.search(r"\b([A-Fa-f0-9]{64})\b", line)
            if match:
                expected = match.group(1).lower()
                break
    if not expected:
        raise RuntimeError("Official Freedoom checksum file did not contain a SHA-256 entry for the pinned ZIP.")
    actual = sha256(fd_cache)
    if actual != expected:
        raise RuntimeError(f"Freedoom SHA-256 mismatch: expected {expected}, got {actual}.")
    print("Freedoom SHA-256 verified against the official checksum asset.")

    shutil.copy2(gz_cache, GZ_DEB)
    stage = CACHE_DIR / "freedoom-stage"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    with zipfile.ZipFile(fd_cache) as archive:
        archive.extractall(stage)
    candidates = list(stage.rglob("freedoom2.wad"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one freedoom2.wad in the official archive; found {len(candidates)}.")
    shutil.copy2(candidates[0], FREEDOOM_WAD)
    if FREEDOOM_WAD.stat().st_size < 1024 * 1024:
        raise RuntimeError("freedoom2.wad looks unexpectedly small; refusing to continue.")
    shutil.rmtree(stage)

    manifest = {
        "schema": 1,
        "gzdoom": {
            "repo": gz_lock["repo"],
            "tag": gz_release["tag_name"],
            "asset": gz_asset["name"],
            "source": gz_asset["browser_download_url"],
            "sha256": sha256(GZ_DEB),
        },
        "freedoom": {
            "repo": fd_lock["repo"],
            "tag": fd_release["tag_name"],
            "asset": fd_asset["name"],
            "source": fd_asset["browser_download_url"],
            "sha256": sha256(FREEDOOM_WAD),
            "archive_sha256": actual,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Pinned Linux runtime staged: {GZ_DEB}")
    print(f"Pinned legal IWAD staged: {FREEDOOM_WAD}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Linux runtime bootstrap failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
