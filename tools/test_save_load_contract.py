import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runner = (ROOT / "tools" / "gzdoom_save_load_roundtrip.py").read_text(encoding="utf-8")
linux_bootstrap = (ROOT / "tools" / "bootstrap_runtime_linux.py").read_text(encoding="utf-8")
windows_wrapper = (ROOT / "tools" / "gzdoom_save_load_roundtrip.ps1").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
lock = json.loads((ROOT / "runtime-lock.json").read_text(encoding="utf-8"))

required_runner_markers = (
    '"-savedir"',
    '"-noautoload"',
    "give CheckoutFuse 2",
    "give CorporateMemo 1",
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
