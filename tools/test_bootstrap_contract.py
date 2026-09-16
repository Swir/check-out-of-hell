from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "runtime-lock.json").read_text(encoding="utf-8"))
runtime = (ROOT / "tools" / "bootstrap_runtime.ps1").read_text(encoding="utf-8")
python_bootstrap = (ROOT / "tools" / "bootstrap_python.ps1").read_text(encoding="utf-8")
play = (ROOT / "PLAY.bat").read_text(encoding="utf-8")

assert lock["gzdoom"]["repo"] == "ZDoom/gzdoom"
assert lock["freedoom"]["repo"] == "freedoom/freedoom"
assert lock["python"]["url"].startswith("https://www.python.org/")

assert "api.github.com/repos/$Repo/releases/tags/$escapedTag" in runtime
assert "browser_download_url" in runtime
assert "Get-FileHash" in runtime
assert "freedoom2.wad" in runtime
assert "gzdoom.exe" in runtime
assert "www.python.org" in python_bootstrap
assert "bootstrap_runtime.ps1" in play
assert "bootstrap_python.ps1" in play

for forbidden in ("mediafire.com", "mega.nz", "dropbox.com", "drive.google.com"):
    assert forbidden not in runtime.lower()
    assert forbidden not in python_bootstrap.lower()

print("Bootstrap contract: PASS")
