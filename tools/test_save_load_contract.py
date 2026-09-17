from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runner = (ROOT / "tools" / "gzdoom_save_load_roundtrip.ps1").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")

required_runner_markers = (
    '"-savedir", $SaveDir',
    '"-noautoload"',
    'give CheckoutFuse 2',
    'give CorporateMemo 1',
    'save coh_ci_roundtrip',
    'load coh_ci_roundtrip',
    'printinv',
    "CheckoutFuse #[0-9]+ \\(2/3\\)",
    "CorporateMemo #[0-9]+ \\(1/3\\)",
    'GZDoom save/load roundtrip: PASS',
)
for marker in required_runner_markers:
    assert marker in runner, f"save/load runner missing contract marker: {marker}"

for failure_marker in (
    "Cannot find savegame",
    "Savegame is from a different version",
    "Savegame is incompatible",
    "Unknown command",
):
    assert failure_marker in runner, f"save/load runner does not guard against: {failure_marker}"

assert "Validate save/load roundtrip with pinned GZDoom" in workflow
assert ".\\tools\\gzdoom_save_load_roundtrip.ps1" in workflow
assert "timeout-minutes: 4" in workflow
assert "save-load-roundtrip" in workflow
assert "test_save_load_contract.py" in workflow

assert "real GZDoom save/load roundtrip" in readme
assert "[x] Save/load validation" in roadmap

print("Save/load contract: PASS")
