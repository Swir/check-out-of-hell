#!/usr/bin/env python3
"""Resolve pinned official GZDoom/Freedoom assets for Linux CI runtime tests."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "runtime-lock.json"
OUT = ROOT / "external" / "linux-ci"
GZDOOM_DEB = OUT / "gzdoom.deb"
FREEDOOM_WAD = OUT / "freedoom2.wad"


def github_json(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "checkout-of-hell-ci-runtime-resolver",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def release_asset(repo: str, tag: str, pattern: str) -> dict:
    release = github_json(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")
    rx = re.compile(pattern)
    matches = [asset for asset in release.get("assets", []) if rx.search(asset.get("name", ""))]
    if len(matches) != 1:
        names = ", ".join(asset.get("name", "?") for asset in release.get("assets", []))
        raise RuntimeError(f"Expected one {repo}@{tag} asset matching {pattern!r}; got {len(matches)}. Assets: {names}")
    return matches[0]


def download(url: str, destination: Path, expected_size: int | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "checkout-of-hell-ci-runtime-resolver"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)
    if expected_size and destination.stat().st_size != expected_size:
        raise RuntimeError(
            f"Downloaded size mismatch for {destination.name}: {destination.stat().st_size} != {expected_size}"
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_for(checksum_text: str, filename: str) -> str:
    for line in checksum_text.splitlines():
        match = re.search(r"\b([0-9a-fA-F]{64})\b\s+\*?(.+?)\s*$", line)
        if match and Path(match.group(2)).name == filename:
            return match.group(1).lower()
    raise RuntimeError(f"Official checksum file does not contain SHA-256 for {filename}")


def main() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    gz = lock["gzdoom"]
    fd = lock["freedoom"]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    gz_asset = release_asset(gz["repo"], gz["tag"], r"^gzdoom_[0-9.]+_amd64\.deb$")
    print(f"Downloading official GZDoom CI package: {gz_asset['name']}")
    download(gz_asset["browser_download_url"], GZDOOM_DEB, gz_asset.get("size"))

    fd_asset = release_asset(fd["repo"], fd["tag"], fd["asset_regex"])
    checksum_asset = release_asset(fd["repo"], fd["tag"], fd["checksum_regex"])
    fd_zip = OUT / fd_asset["name"]
    checksum_path = OUT / checksum_asset["name"]
    print(f"Downloading official Freedoom CI package: {fd_asset['name']}")
    download(fd_asset["browser_download_url"], fd_zip, fd_asset.get("size"))
    download(checksum_asset["browser_download_url"], checksum_path, checksum_asset.get("size"))

    expected = checksum_for(checksum_path.read_text(encoding="utf-8", errors="replace"), fd_asset["name"])
    actual = sha256(fd_zip)
    if actual != expected:
        raise RuntimeError(f"Freedoom SHA-256 mismatch: expected {expected}, got {actual}")
    print("Freedoom SHA-256 verified against official upstream checksum.")

    with zipfile.ZipFile(fd_zip) as archive:
        candidates = [name for name in archive.namelist() if Path(name).name.lower() == "freedoom2.wad"]
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one freedoom2.wad in {fd_asset['name']}; got {len(candidates)}")
        with archive.open(candidates[0]) as source, FREEDOOM_WAD.open("wb") as target:
            shutil.copyfileobj(source, target)

    print(f"GZDoom package ready: {GZDOOM_DEB}")
    print(f"Freedoom IWAD ready:  {FREEDOOM_WAD}")


if __name__ == "__main__":
    main()
