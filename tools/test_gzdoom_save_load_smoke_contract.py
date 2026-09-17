from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke_linux.sh"
WINDOWS_HELPER = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"

script = SCRIPT.read_text(encoding="utf-8")
windows_helper = WINDOWS_HELPER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")

required_script_markers = (
    'runtime-lock.json',
    'api.github.com/repos/$GZ_REPO/releases/tags/$GZ_TAG',
    'gzdoom_.*_amd64\\.deb',
    'api.github.com/repos/$FD_REPO/releases/tags/$FD_TAG',
    'Freedoom SHA-256 verified.',
    'Xvfb "$DISPLAY" -screen 0 800x600x24',
    'xdotool search --pid "$ENGINE_PID"',
    'LIBGL_ALWAYS_SOFTWARE=1',
    'GALLIUM_DRIVER=llvmpipe',
    '+logfile "$log"',
    'launch_engine "$SAVE_LOG" +map MAP01',
    'send_console_command "$SAVE_WINDOW" "give CheckoutFuse 2"',
    'send_console_command "$SAVE_WINDOW" "printinv"',
    'send_console_command "$SAVE_WINDOW" "save $SAVE_STEM',
    'stop_engine',
    'launch_engine "$LOAD_LOG" -loadgame "$SAVE_STEM"',
    'COH_RUNTIME_SAVE_WRITTEN',
    'COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE',
    'CheckoutFuse[[:space:]]+#[0-9]+[[:space:]]+\\(2/3\\)',
    'stat -c %s "$SAVE_FILE"',
    'RESULT="PASS - CheckoutFuse 2/3 survived real save -> process exit -> load"',
    'gzdoom-save-load-smoke.log',
)
for marker in required_script_markers:
    if marker not in script:
        raise SystemExit(f"Linux runtime save/load smoke script is missing required marker: {marker}")

if script.index('send_console_command "$SAVE_WINDOW" "give CheckoutFuse 2"') > script.index(
    'send_console_command "$SAVE_WINDOW" "save $SAVE_STEM'
):
    raise SystemExit("Runtime objective state must be authored before the real save command")
if script.index('launch_engine "$LOAD_LOG" -loadgame "$SAVE_STEM"') > script.index(
    "CheckoutFuse 2/3 did not survive"
):
    raise SystemExit("Loaded inventory must be verified after the real load phase")
if script.count("stop_engine") < 3:
    raise SystemExit("Runtime harness must cross a real process boundary between save and load")

windows_markers = (
    'bootstrap_runtime.ps1',
    'wait 175; give CheckoutFuse 2',
    'save $SaveStem',
    '-loadgame", $SaveStem',
    'Hosted Windows CI has no renderer suitable for an interactive GZDoom',
)
for marker in windows_markers:
    if marker not in windows_helper:
        raise SystemExit(f"Windows desktop round-trip helper is missing required marker: {marker}")

workflow_markers = (
    "GZDoom save/load smoke contract test",
    "python tools/test_gzdoom_save_load_smoke_contract.py",
    "runtime-save-load",
    "bash tools/gzdoom_save_load_smoke_linux.sh",
    "gzdoom-save-load-smoke-log",
    "dist/gzdoom-save-load-smoke.log",
)
for marker in workflow_markers:
    if marker not in workflow:
        raise SystemExit(f"GitHub Actions is missing runtime save/load coverage: {marker}")

if '.\\tools\\gzdoom_save_load_smoke.ps1' in workflow:
    raise SystemExit("Hosted Windows CI must not run the live GZDoom loop without a usable graphics adapter")

print("GZDoom save/load runtime smoke contract: PASS")
