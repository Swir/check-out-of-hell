from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tools" / "windows_demo_signoff.ps1"
SAVE_LOAD = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
DOC = ROOT / "docs" / "WINDOWS_PLAYTEST.md"
WRAPPER = ROOT / "WINDOWS-DEMO-SIGNOFF.bat"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
ROADMAP = ROOT / "ROADMAP.md"
README = ROOT / "README.md"

for required in (HARNESS, SAVE_LOAD, DOC, WRAPPER, WORKFLOW, ROADMAP, README):
    if not required.is_file():
        raise SystemExit(f"Windows demo sign-off contract is missing required file: {required.relative_to(ROOT)}")

harness = HARNESS.read_text(encoding="utf-8")
save_load = SAVE_LOAD.read_text(encoding="utf-8")
doc = DOC.read_text(encoding="utf-8")
wrapper = WRAPPER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
roadmap = ROADMAP.read_text(encoding="utf-8")
readme = README.read_text(encoding="utf-8")

# Normalize Windows separators only for static path matching. The implementation
# still uses native Windows paths; this just keeps the contract from depending on
# Python literal escaping details.
harness_paths = harness.replace("\\", "/")
workflow_paths = workflow.replace("\\", "/")

# The helper must still work in its original standalone mode while accepting an
# already prepared RC payload so the sign-off does not secretly rebuild/swap it.
helper_markers = (
    "[string]$GZDoomExe",
    "[string]$FreedoomWad",
    "[string]$Pk3",
    "[string]$WorkDir",
    "[string]$CombinedLog",
    "[switch]$PreparedRuntime",
    "if (-not $PreparedRuntime)",
    "Using caller-prepared GZDoom/Freedoom/game payload without rebuilding or replacing it.",
    '"-iwad", $FreedoomWad',
    '"-file", $Pk3',
    '"-savedir", $SaveDir',
    '"-loadgame", $saveFile.Name',
    "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
)
for marker in helper_markers:
    if marker not in save_load:
        raise SystemExit(f"Parameterized save/load helper is missing required marker: {marker}")

# The target-Windows harness must validate the exact extracted player package,
# then collect manual evidence rather than claiming hosted CI is a playtest.
harness_markers = (
    "package_release_candidate.py",
    "CHECKOUT-OF-HELL-Windows-Portable-rc.zip",
    "Expand-Archive -LiteralPath $RcZip -DestinationPath $PackageDir -Force",
    '"tools/verify_player_package.ps1"',
    '"tools/bootstrap_runtime.ps1"',
    '"external/gzdoom/gzdoom.exe"',
    '"external/freedoom2.wad"',
    '"game/CHECKOUT-OF-HELL.pk3"',
    "gzdoom_save_load_smoke.ps1",
    "-PreparedRuntime",
    '"Closing Crew"',
    '"Graveyard Shift"',
    '"Corporate Hell"',
    "save_quit_load",
    "controller_core_actions",
    "controller_haptics",
    "performance_sanity",
    "final_polish_signoff",
    "$allAutomated",
    "$allManual",
    "$sourceIsVerifiable",
    'if ($allAutomated -and $allManual -and $sourceIsVerifiable)',
    '$Evidence.status = "PASS"',
    '$Evidence.status = "INCOMPLETE"',
    "No release should be published from this result.",
)
for marker in harness_markers:
    if marker not in harness_paths:
        raise SystemExit(f"Windows demo sign-off harness is missing required marker: {marker}")

verify_call = '& (Join-Path $PackageDir "tools/verify_player_package.ps1")'
bootstrap_call = '& (Join-Path $PackageDir "tools/bootstrap_runtime.ps1")'
save_load_call = "& $SaveLoadHelper `"
if not (
    harness_paths.index(verify_call)
    < harness_paths.index(bootstrap_call)
    < harness_paths.index(save_load_call)
):
    raise SystemExit("Required execution order is RC integrity -> pinned runtime bootstrap -> exact-RC save/load")

if "-PrepareOnly" not in doc or "INCOMPLETE" not in doc:
    raise SystemExit("Windows playtest documentation must make automated-only preparation explicitly incomplete")
if "does not publish" not in doc.lower() or "remaining" not in doc.lower():
    raise SystemExit("Windows playtest documentation must preserve the no-release and remaining-gates policy")
if "WINDOWS-DEMO-SIGNOFF.bat" not in doc or "windows_demo_signoff.ps1" not in wrapper:
    raise SystemExit("The documented one-click Windows sign-off entry point is not wired correctly")

# Privacy: friendly hardware names are useful evidence, stable identifiers are not.
for forbidden in ("SerialNumber", "PNPDeviceID", "DeviceID", "$env:USERNAME", "$env:COMPUTERNAME"):
    if forbidden in harness:
        raise SystemExit(f"Windows sign-off evidence must not collect sensitive/stable machine identifiers: {forbidden}")
for required_privacy_text in ("controller_names", "cpu_names", "gpu_names", "memory_gb"):
    if required_privacy_text not in harness:
        raise SystemExit(f"Windows sign-off evidence is missing bounded hardware context: {required_privacy_text}")

# This iteration creates evidence tooling only. It must not promote roadmap gates.
if "**Overall progress:** ` 84.8%`" not in roadmap:
    raise SystemExit("Windows sign-off tooling must not inflate overall project progress")
if "**Demo Release readiness: 60.0%**" not in roadmap:
    raise SystemExit("Windows sign-off tooling must keep Demo Release readiness at the verified 60.0%")
for open_gate in (
    "- [ ] Standalone legal content package",
    "- [ ] Release notes",
    "- [ ] GitHub Release",
):
    if open_gate not in roadmap:
        raise SystemExit(f"Windows sign-off tooling must not close release gate: {open_gate}")
if "docs/WINDOWS_PLAYTEST.md" not in roadmap:
    raise SystemExit("ROADMAP must link the reproducible target-Windows sign-off procedure")

# SVG-only presentation remains enforced: plain percentages are allowed, text-art
# progress bars are not. Existing README PRO coverage performs the same check too.
legacy_progress_meter = re.compile(r"(?:[█▓▒░]{2,})|(?:\[(?:[#=\-]{4,})\])")
for path, text in ((README, readme), (ROADMAP, roadmap)):
    if legacy_progress_meter.search(text):
        raise SystemExit(f"Legacy character progress meter returned in {path.name}")

workflow_markers = (
    "python tools/test_windows_demo_signoff_contract.py",
    "Parse Windows demo sign-off scripts",
    "./tools/windows_demo_signoff.ps1",
    "./tools/gzdoom_save_load_smoke.ps1",
    "System.Management.Automation.Language.Parser",
    "powershell-signoff-parse-report",
)
for marker in workflow_markers:
    if marker not in workflow_paths:
        raise SystemExit(f"CI is not protecting the Windows sign-off kit: {marker}")

# The interactive harness must never be executed by hosted CI as if it were real
# target-machine evidence; only parser/static contracts belong there.
if re.search(r"run:\s*\./tools/windows_demo_signoff\.ps1(?:\s|$)", workflow_paths):
    raise SystemExit("Hosted CI must not execute the interactive Windows sign-off harness")

print("Target Windows demo sign-off contract: PASS")
print("Exact RC package verification/save-load automation is separated from required human Windows/controller/balance/performance evidence.")
