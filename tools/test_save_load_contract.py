import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runner = (ROOT / "tools" / "gzdoom_save_load_roundtrip.py").read_text(encoding="utf-8")
linux_bootstrap = (ROOT / "tools" / "bootstrap_runtime_linux.py").read_text(encoding="utf-8")
windows_wrapper = (ROOT / "tools" / "gzdoom_save_load_roundtrip.ps1").read_text(encoding="utf-8")
parser_smoke = (ROOT / "tools" / "gzdoom_runtime_smoke.ps1").read_text(encoding="utf-8")
zscript = (ROOT / "game" / "ZSCRIPT").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
lock = json.loads((ROOT / "runtime-lock.json").read_text(encoding="utf-8"))

required_runner_markers = (
    '"-savedir"',
    '"-noautoload"',
    '"+sv_cheats"',
    'argv.extend(["+map", "MAP01"])',
    "autostart_map01=True",
    '"give CheckoutFuse 2"',
    '"give CorporateMemo 1"',
    "save coh_ci_roundtrip",
    "load coh_ci_roundtrip",
    "printinv",
    "CheckoutFuse #[0-9]+",
    "CorporateMemo #[0-9]+",
    "PHASE_TIMEOUT_SECONDS = 45",
    "GZDoom save/load roundtrip: PASS",
)
for marker in required_runner_markers:
    assert marker in runner, f"save/load runner missing contract marker: {marker}"

for failure_marker in (
    "Cannot find savegame",
    "Savegame is from a different version",
    "Savegame is incompatible",
    "Unknown command",
    "DIED WITH FATAL ERROR",
):
    assert failure_marker in runner, f"save/load runner does not guard against: {failure_marker}"

# The persistence regression must be deterministic and isolated from combat/navigation.
# Pickup placement and route logic are already guarded by dedicated MAP01 contracts.
for old_warp in ("warp -690 -310 0", "warp -640 140 0", "warp 620 340 0"):
    assert old_warp not in runner
assert "checks serialization" in runner
assert 'save_commands = "\\n".join(' in runner
assert 'load_commands = "\\n".join(' in runner

# +map is intentionally queued before +exec so the map/player exists when cfg commands
# execute. +warp is the live coordinate-warp command and is not a map-number launcher.
assert 'argv.extend(["+warp", "1"])' not in runner
assert 'argv.extend(["-warp", "1"])' not in runner
assert "+map is a post-initialization console command" in runner

# GZDoom treats -errorlog as a batch/parser mode switch and exits before the live
# game loop. Keep it in the -norun parser smoke, never in the real save/load process.
assert '"-errorlog"' not in runner, "real save/load runner must not enable GZDoom batch mode"
assert "Do not pass -errorlog here" in runner

# WorldLoaded also runs when restoring a save. Serialized director fields must survive
# that callback instead of being reset as if a fresh map had started.
assert "if (e.IsSaveGame)" in zscript, "shift director does not protect restored savegame state"
assert zscript.index("if (e.IsSaveGame)") < zscript.index("bossCleared = false;"), (
    "savegame guard must run before fresh-level shift state initialization"
)

# Actor state lines must remain legal ZScript. A live Linux GZDoom run exposed bare
# Stop/TNT1/COSH statements that the earlier stdout-only Windows smoke could miss.
assert not re.search(r"(?m)^\s+Stop\s*$", zscript), "bare Stop state statement found in ZSCRIPT"
for state_line in ("TNT1 A -1;", "COSH A -1 Bright;"):
    assert state_line in zscript, f"expected terminated ZScript state line missing: {state_line}"

for parser_marker in (
    '"-errorlog", $EngineErrorLog',
    "===== GZDoom engine error log =====",
    '"Script error"',
    '"DIED WITH FATAL ERROR"',
):
    assert parser_marker in parser_smoke, f"Windows parser smoke missing engine-log guard: {parser_marker}"

assert lock["gzdoom"]["linux_asset_regex"] == r"^gzdoom_.*_amd64\.deb$"
for bootstrap_marker in (
    "api.github.com/repos/{repo}/releases/tags/",
    "browser_download_url",
    "Freedoom SHA-256 verified against the official checksum asset.",
    "Expected exactly one {description}",
):
    assert bootstrap_marker in linux_bootstrap, f"Linux bootstrap missing resilience marker: {bootstrap_marker}"

assert "gzdoom_save_load_roundtrip.py" in windows_wrapper
assert "bootstrap_runtime.ps1" in windows_wrapper
assert "save-load-runtime:" in workflow
assert "Resolve pinned official Linux runtime assets" in workflow
assert "python tools/bootstrap_runtime_linux.py" in workflow
assert "xvfb-run -a python tools/gzdoom_save_load_roundtrip.py" in workflow
assert 'LIBGL_ALWAYS_SOFTWARE: "1"' in workflow
assert "timeout-minutes: 8" in workflow
assert "gzdoom-save-load-validation-logs" in workflow
assert "test_save_load_contract.py" in workflow

assert "real GZDoom save/load roundtrip" in readme
assert "[x] Save/load validation" in roadmap

print("Save/load contract: PASS")
