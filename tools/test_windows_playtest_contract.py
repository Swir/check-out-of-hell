from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_playtest_assistant.ps1"
LAUNCHER = ROOT / "PLAYTEST-WINDOWS.bat"
DOC = ROOT / "docs" / "WINDOWS_PLAYTEST.md"

for path in (SCRIPT, LAUNCHER, DOC):
    if not path.is_file():
        raise SystemExit(f"Windows playtest evidence file is missing: {path.relative_to(ROOT)}")

script = SCRIPT.read_text(encoding="utf-8")
launcher = LAUNCHER.read_text(encoding="utf-8")
doc = DOC.read_text(encoding="utf-8")

required_script_markers = (
    "[switch]$DryRun",
    "[switch]$NoLaunch",
    '"Closing Time target-Windows interactive demo sign-off"',
    'public_release_authorized = $false',
    '"full_playthrough"',
    '"manual_save_quit_load"',
    '"physical_controller"',
    '"closing_crew_balance"',
    '"graveyard_shift_balance"',
    '"corporate_hell_balance"',
    '"real_hardware_performance"',
    '"final_polish"',
    "Get-FileHash",
    "Get-HardwareSnapshot",
    "Get-SourceIdentity",
    "bootstrap_runtime.ps1",
    "runtime-manifest.json",
    "Start-Process -FilePath $GZDoomExe",
    '"+map", "MAP01"',
    "evidence.json",
    "evidence.md",
    "This helper never publishes a GitHub Release or changes ROADMAP progress automatically.",
)
for marker in required_script_markers:
    if marker not in script:
        raise SystemExit(f"Windows playtest assistant is missing required behavior: {marker}")

if script.count("Start-Process -FilePath $GZDoomExe") != 2:
    raise SystemExit("Windows playtest assistant must use two separate GZDoom processes for manual save/quit/load confirmation")

if "Read-Host" in script.split("if ($DryRun)", 1)[1].split("if ((Test-Path", 1)[0]:
    raise SystemExit("DryRun path must exit before any interactive manual gate prompts")

for forbidden in (
    "Invoke-WebRequest",
    "Invoke-RestMethod",
    "curl ",
    "wget ",
    "github.com/releases/latest",
):
    if forbidden.lower() in script.lower():
        raise SystemExit(f"Playtest assistant must delegate downloads to the pinned bootstrap, not fetch directly: {forbidden}")

if "windows_playtest_assistant.ps1" not in launcher.lower():
    raise SystemExit("PLAYTEST-WINDOWS.bat is not wired to the playtest assistant")
if "publish" not in launcher.lower() or "auto-approve" not in launcher.lower():
    raise SystemExit("PLAYTEST-WINDOWS.bat must clearly state that it cannot publish or auto-approve a demo")

for phrase in (
    "One-click helper",
    "Required manual gates",
    "Evidence output",
    "Automation / CI validation",
    "does **not** authorize a public release",
    "Closing Crew",
    "Graveyard Shift",
    "Corporate Hell",
    "physical controller",
    "real Windows hardware",
):
    if phrase not in doc:
        raise SystemExit(f"Windows playtest documentation is missing required sign-off guidance: {phrase}")

if re.search(r"[█▓▒░]{2,}|\[[#=\-]{4,}\]", doc):
    raise SystemExit("Windows playtest documentation must not reintroduce a legacy progress meter")

print("Windows target-playtest evidence contract: PASS")
print("Manual sign-off remains explicit, two-process save/load evidence is assisted, and the helper cannot authorize a release.")
