from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "runtime-lock.json").read_text(encoding="utf-8"))
runtime = (ROOT / "tools" / "bootstrap_runtime.ps1").read_text(encoding="utf-8")
python_bootstrap = (ROOT / "tools" / "bootstrap_python.ps1").read_text(encoding="utf-8")
play = (ROOT / "PLAY.bat").read_text(encoding="utf-8")

assert lock["gzdoom"]["repo"] == "ZDoom/gzdoom"
assert lock["gzdoom"]["tag"] == "g4.14.2"
assert lock["gzdoom"]["asset_name"] == "gzdoom-4-14-2-windows.zip"
assert lock["gzdoom"]["asset_id"] == 251530238
assert lock["gzdoom"]["asset_bytes"] == 21879627
assert lock["freedoom"]["repo"] == "freedoom/freedoom"
assert lock["python"]["url"].startswith("https://www.python.org/")

assert "api.github.com/repos/$Repo/releases/tags/$escapedTag" in runtime
assert "browser_download_url" in runtime
assert "Get-FileHash" in runtime
assert "freedoom2.wad" in runtime
assert "gzdoom.exe" in runtime
assert "Assert-PinnedReleaseAsset" in runtime
assert "$Lock.gzdoom.asset_name" in runtime
assert "$Lock.gzdoom.asset_id" in runtime
assert "$Lock.gzdoom.asset_bytes" in runtime
assert "Refusing a silent re-upload/replacement" in runtime
assert "GZDoom archive byte count mismatch after download" in runtime
assert "asset_id = $gzManifestAssetId" in runtime
assert "archive_bytes = $gzManifestArchiveBytes" in runtime
assert "$Lock.python.url" in python_bootstrap
assert "bootstrap_runtime.ps1" in play
assert "bootstrap_python.ps1" in play

for forbidden in ("mediafire.com", "mega.nz", "dropbox.com", "drive.google.com"):
    assert forbidden not in runtime.lower()
    assert forbidden not in python_bootstrap.lower()

print("Bootstrap contract: PASS")
print("Pinned GZDoom Windows release identity is locked by official asset name, GitHub asset ID and byte size; Freedoom retains upstream SHA-256 verification.")
