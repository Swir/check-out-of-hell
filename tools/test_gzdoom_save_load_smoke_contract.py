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
    '"vid_preferbackend=0"',
    '"i_pauseinbackground=false"',
    'Start-Process -FilePath $GZDoomExe',
    'Stop-Process -Id $Process.Id -Force',
    'give CheckoutFuse 2',
    'give CorporateMemo 2',
    'save $SaveStem',
    '"-loadgame", $saveFile.FullName',
    'printinv',
    'COH_RUNTIME_SAVE_WRITTEN',
    'COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE',
    'CheckoutFuse\\s+#\\d+\\s+\\(2/3\\)',
    'CorporateMemo\\s+#\\d+\\s+\\(2/3\\)',
    '$saveFile.Length -lt 4096',
)
for marker in required_script_markers:
    if marker not in script:
        raise SystemExit(f"Runtime save/load harness is missing required marker: {marker}")

if script.index("give CheckoutFuse 2") > script.index("save $SaveStem"):
    raise SystemExit("Runtime objective state must be authored before the save command")
if script.index('"-loadgame", $saveFile.FullName') > script.index("CheckoutFuse 2/3 did not survive"):
    raise SystemExit("Loaded objective state must be verified after starting the load process")
if "quit\"" in script or "; quit" in script:
    raise SystemExit("Runtime harness must not depend on an unfocused GZDoom GUI processing quit")

required_workflow_markers = (
    "python tools/test_gzdoom_save_load_smoke_contract.py",
    ".\\tools\\gzdoom_save_load_smoke.ps1",
    "gzdoom-save-load-smoke-log",
    "dist/gzdoom-save-load-smoke.log",
)
for marker in required_workflow_markers:
    if marker not in workflow:
        raise SystemExit(f"CI is not wiring the runtime save/load gate correctly: {marker}")

print("GZDoom Windows save/load runtime gate contract: PASS")
