from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
LINUX_BOOTSTRAP = ROOT / "tools" / "bootstrap_linux_runtime.py"
LINUX_SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke_linux.py"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
LOCK = ROOT / "runtime-lock.json"

windows_script = WINDOWS_SCRIPT.read_text(encoding="utf-8")
linux_bootstrap = LINUX_BOOTSTRAP.read_text(encoding="utf-8")
linux_script = LINUX_SCRIPT.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
lock = json.loads(LOCK.read_text(encoding="utf-8"))

required_windows_markers = (
    '"bootstrap_runtime.ps1"',
    '"-iwad", $FreedoomWad',
    '"-file", $Pk3',
    '"-savedir", $SaveDir',
    'Start-Process -FilePath $GZDoomExe',
    'Stop-Process -Id $Process.Id -Force',
    'give CheckoutFuse 2',
    'give CorporateMemo 2',
    'save $SaveStem',
    '"-loadgame", $saveFile.FullName',
    'COH_RUNTIME_SAVE_WRITTEN',
    'COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE',
)
for marker in required_windows_markers:
    if marker not in windows_script:
        raise SystemExit(f"Native Windows save/load harness is missing required marker: {marker}")
if "quit\"" in windows_script or "; quit" in windows_script:
    raise SystemExit("Windows harness must not depend on an unfocused GZDoom GUI processing quit")

required_linux_bootstrap_markers = (
    "runtime-lock.json",
    "api.github.com/repos/{repo}/releases/tags/",
    "linux_asset_regex",
    "checksum_regex",
    "Freedoom SHA-256 verified against official release checksum.",
    "gzdoom-pinned-amd64.deb",
)
for marker in required_linux_bootstrap_markers:
    if marker not in linux_bootstrap:
        raise SystemExit(f"Linux runtime bootstrap is missing required marker: {marker}")

required_linux_markers = (
    'shutil.which("gzdoom")',
    '"LIBGL_ALWAYS_SOFTWARE"',
    '"MESA_LOADER_DRIVER_OVERRIDE"',
    '"llvmpipe"',
    "give CheckoutFuse 2",
    "give CorporateMemo 2",
    "coh-ci-roundtrip-linux",
    '"-loadgame"',
    "COH_LINUX_RUNTIME_SAVE_WRITTEN",
    "COH_LINUX_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
    r"CheckoutFuse\s+#\d+\s+\(2/3\)",
    r"CorporateMemo\s+#\d+\s+\(2/3\)",
    "save_file.stat().st_size < 4096",
)
for marker in required_linux_markers:
    if marker not in linux_script:
        raise SystemExit(f"Linux runtime save/load smoke is missing required marker: {marker}")
if "; quit" in linux_script:
    raise SystemExit("Linux harness must own the process boundary instead of depending on GUI quit")

if lock.get("gzdoom", {}).get("linux_asset_regex") != r"^gzdoom_.*_amd64\.deb$":
    raise SystemExit("runtime-lock.json must pin the official amd64 GZDoom Linux package pattern")

required_workflow_markers = (
    "python tools/test_gzdoom_save_load_smoke_contract.py",
    "runtime-state-linux:",
    "python tools/bootstrap_linux_runtime.py",
    "external/linux/gzdoom-pinned-amd64.deb",
    "xvfb-run -a",
    "python tools/gzdoom_save_load_smoke_linux.py",
    "gzdoom-linux-save-load-smoke-log",
    "dist/gzdoom-save-load-linux-smoke.log",
    ".\\tools\\gzdoom_runtime_smoke.ps1",
)
for marker in required_workflow_markers:
    if marker not in workflow:
        raise SystemExit(f"CI is not wiring the save/load validation correctly: {marker}")

if ".\\tools\\gzdoom_save_load_smoke.ps1" in workflow:
    raise SystemExit(
        "Hosted Windows CI must not claim a gameplay round-trip while its runner exposes neither "
        "a compatible Vulkan device nor a modern OpenGL context"
    )

print("GZDoom save/load runtime validation contract: PASS")
