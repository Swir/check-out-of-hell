from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"

script = SCRIPT.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")

required_script_markers = (
    '"bootstrap_runtime.ps1"',
    '"-iwad", $FreedoomWad',
    '"-file", $Pk3',
    '"-savedir", $SaveDir',
    '"-noautoload"',
    '"+vid_activeinbackground", "true"',
    '"+i_pauseinbackground", "false"',
    'Start-Process -FilePath $GZDoomExe',
    '-Wait `',
    'setinv CheckoutFuse 2',
    'setinv CorporateMemo 2',
    'save $SaveStem',
    'load $SaveStem',
    'printinv',
    'wait 70; quit',
    'wait 10; quit',
    'CheckoutFuse\\s+#\\d+\\s+\\(2/',
    'CorporateMemo\\s+#\\d+\\s+\\(2/',
    'Test-Path -LiteralPath $SaveFile',
)
for marker in required_script_markers:
    if marker not in script:
        raise SystemExit(f"Runtime save/load smoke script is missing required marker: {marker}")

if script.index("setinv CheckoutFuse 2") > script.index("save $SaveStem"):
    raise SystemExit("Runtime state must be authored before the save command")
if script.index("load $SaveStem") > script.index("Assert-InventoryState -LogText $loadText"):
    raise SystemExit("Loaded inventory must be verified after the real load phase")

workflow_markers = (
    "Save/load current prototype with pinned GZDoom",
    ".\\tools\\gzdoom_save_load_smoke.ps1",
    "gzdoom-save-load-smoke-log",
    "dist/gzdoom-save-load-smoke.log",
)
for marker in workflow_markers:
    if marker not in workflow:
        raise SystemExit(f"GitHub Actions is not wired for runtime save/load validation: {marker}")

print("GZDoom save/load smoke contract: PASS")
print("Windows CI must wait for the real GZDoom process, keep background rendering/ticks active, and verify serialized department state after a second-process load.")
