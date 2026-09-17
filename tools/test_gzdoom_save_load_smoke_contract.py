from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"

script = SCRIPT.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")

required_script_markers = (
    '"bootstrap_runtime.ps1"',
    '"-noautoload"',
    '"-iwad", $FreedoomWad',
    '"-file", $Pk3',
    '"-savedir", $SaveDir',
    '"+map", "MAP01"',
    '"+give", "CheckoutFuse", "2"',
    '"+printinv"',
    '"+save", $SaveStem',
    '"+quit"',
    '"-loadgame", $SaveFile',
    'COH_RUNTIME_SAVE_WRITTEN',
    'COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE',
    'CheckoutFuse\\s+#\\d+\\s+\\(2/3\\)',
    'Test-Path -LiteralPath $SaveFile',
    'Length -lt 4096',
    'WaitForExit($TimeoutSeconds * 1000)',
    'Write-CombinedLog',
)

for marker in required_script_markers:
    if marker not in script:
        raise SystemExit(f"Runtime save/load smoke script is missing required marker: {marker}")

if script.index('"+give", "CheckoutFuse", "2"') > script.index('"+save", $SaveStem'):
    raise SystemExit("Runtime objective state must be authored before the real save command")

if script.index('"-loadgame", $SaveFile') > script.index('CheckoutFuse 2/3 did not survive'):
    raise SystemExit("The loaded inventory must be verified after the real load phase")

for forbidden in (
    'wait 175',
    'wait 70',
    'save-roundtrip.cfg',
    'load-roundtrip.cfg',
):
    if forbidden in script:
        raise SystemExit(f"Runtime smoke still contains the old delayed-command deadlock path: {forbidden}")

workflow_markers = (
    "GZDoom save/load smoke contract test",
    "python tools/test_gzdoom_save_load_smoke_contract.py",
    "Save/load current prototype with pinned GZDoom",
    ".\\tools\\gzdoom_save_load_smoke.ps1",
    "gzdoom-save-load-smoke-log",
    "dist/gzdoom-save-load-smoke.log",
)
for marker in workflow_markers:
    if marker not in workflow:
        raise SystemExit(f"GitHub Actions is missing runtime save/load coverage: {marker}")

print("GZDoom save/load runtime smoke contract: PASS")
