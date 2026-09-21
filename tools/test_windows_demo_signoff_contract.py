from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tools" / "windows_demo_signoff.ps1"
POLISH_REVIEW = ROOT / "tools" / "closing_time_polish_review.ps1"
VERIFY_LATEST = ROOT / "tools" / "verify_latest_windows_signoff.ps1"
SAVE_LOAD = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
EVIDENCE_VERIFIER = ROOT / "tools" / "verify_windows_signoff_evidence.py"
DOC = ROOT / "docs" / "WINDOWS_PLAYTEST.md"
WRAPPER = ROOT / "WINDOWS-DEMO-SIGNOFF.bat"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
ROADMAP = ROOT / "ROADMAP.md"
README = ROOT / "README.md"

for required in (HARNESS, POLISH_REVIEW, VERIFY_LATEST, SAVE_LOAD, EVIDENCE_VERIFIER, DOC, WRAPPER, WORKFLOW, ROADMAP, README):
    if not required.is_file():
        raise SystemExit(f"Windows demo sign-off contract is missing required file: {required.relative_to(ROOT)}")

harness = HARNESS.read_text(encoding="utf-8")
polish_review = POLISH_REVIEW.read_text(encoding="utf-8")
verify_latest = VERIFY_LATEST.read_text(encoding="utf-8")
save_load = SAVE_LOAD.read_text(encoding="utf-8")
evidence_verifier = EVIDENCE_VERIFIER.read_text(encoding="utf-8")
doc = DOC.read_text(encoding="utf-8")
wrapper = WRAPPER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
roadmap = ROADMAP.read_text(encoding="utf-8")
readme = README.read_text(encoding="utf-8")

# The save/load helper must retain its normal standalone path while also accepting
# an already verified release-candidate payload. This prevents the sign-off from
# validating one build and silently exercising another.
for marker in (
    "[string]$GZDoomExe",
    "[string]$FreedoomWad",
    "[string]$Pk3",
    "[string]$WorkDir",
    "[string]$CombinedLog",
    "[switch]$PreparedRuntime",
    "if (-not $PreparedRuntime)",
    "Using caller-prepared GZDoom/Freedoom/game payload without rebuilding or replacing it.",
    "COH_RUNTIME_SAVE_WRITTEN",
    "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
    "CheckoutFuse",
    "CorporateMemo",
    "-loadgame",
):
    if marker not in save_load:
        raise SystemExit(f"Parameterized save/load helper lost required behavior: {marker}")

# The Windows harness must build and verify the real RC, resolve the pinned legal
# runtime in that extracted package, run the automated round-trip, then require
# explicit human evidence before base PASS.
for marker in (
    "package_release_candidate.py",
    "CHECKOUT-OF-HELL-Windows-Portable-rc.zip",
    "Expand-Archive",
    "verify_player_package.ps1",
    "bootstrap_runtime.ps1",
    "gzdoom.exe",
    "freedoom2.wad",
    "CHECKOUT-OF-HELL.pk3",
    "gzdoom_save_load_smoke.ps1",
    "-PreparedRuntime",
    "Closing Crew",
    "Graveyard Shift",
    "Corporate Hell",
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
    "Get-FileHash",
    "Get-GitSnapshot",
    "Get-HardwareSummary",
    "No release should be published from this result.",
):
    if marker not in harness:
        raise SystemExit(f"Windows demo sign-off harness lost required behavior: {marker}")

verify_pos = harness.index("verify_player_package.ps1")
bootstrap_pos = harness.index("bootstrap_runtime.ps1")
roundtrip_pos = harness.index("& $SaveLoadHelper")
if not (verify_pos < bootstrap_pos < roundtrip_pos):
    raise SystemExit("Required execution order is RC integrity -> pinned runtime bootstrap -> exact-RC save/load")

# A base PASS must remain impossible without a clean commit-addressable source snapshot.
if "^[0-9a-f]{40}$" not in harness or "$Evidence.source.clean -eq $true" not in harness:
    raise SystemExit("Windows base PASS must remain bound to a clean commit-addressable source snapshot")

# Explicit polish review is mandatory after the base harness and before evidence
# can be treated as canonical Closing Time polish proof.
for marker in (
    "environment_art_consistent",
    "objective_route_readable",
    "lighting_atmosphere_acceptable",
    "clutter_visual_hierarchy_clean",
    "final_polish_signoff",
    "Base target-Windows sign-off must report PASS",
    'Evidence.status = if ($AllPolish) { "PASS" } else { "FAILED_POLISH_REVIEW" }',
):
    if marker not in polish_review:
        raise SystemExit(f"Closing Time explicit polish review lost required behavior: {marker}")

# Developer-checkout verification must bind the newest reviewed evidence to the
# exact clean local HEAD and run the same independent Python verifier used by the kit.
# It also locks a plausible human-created Graveyard Shift save to a SHA-256 witness
# so an autosave, tiny placeholder, deletion or later replacement cannot satisfy the
# manual save artifact prerequisite by file presence alone.
for marker in (
    "dist\\windows-demo-signoff",
    "git",
    "status --porcelain",
    "verify_windows_signoff_evidence.py",
    "--expected-commit",
    "bootstrap_python.ps1",
    "VERIFIED PASS",
    "No release should be published from this result.",
    "Assert-ManualSaveWitness",
    "manual-save-witness.sha256",
    "manual-saves",
    ".zds",
    "(?i)^auto",
    "1024",
    "Get-FileHash",
):
    if marker not in verify_latest:
        raise SystemExit(f"Developer evidence verification helper lost required behavior: {marker}")
for forbidden_publish in ("gh release create", "New-GitHubRelease", "Invoke-RestMethod -Method Post"):
    if forbidden_publish.lower() in verify_latest.lower():
        raise SystemExit(f"Developer evidence verifier must not publish releases: {forbidden_publish}")

# The independent verifier must re-check the completed evidence package instead of
# trusting PASS text alone. It remains evidence validation, never a publisher or a
# substitute for the human play/controller/performance judgments.
for marker in (
    "--expected-commit",
    "runtime-lock.json",
    "package-manifest.json",
    "runtime-manifest.json",
    "FREEDOOM-PROVENANCE.json",
    "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
    "manual-saves",
    "environment_art_consistent",
    "objective_route_readable",
    "lighting_atmosphere_acceptable",
    "clutter_visual_hierarchy_clean",
    "controller_haptics",
    "final_polish_signoff",
    "No release should be published from this result.",
):
    if marker not in evidence_verifier:
        raise SystemExit(f"Windows sign-off evidence verifier lost required behavior: {marker}")
for forbidden_publish in ("gh release create", "New-GitHubRelease", "Invoke-RestMethod -Method Post"):
    if forbidden_publish.lower() in evidence_verifier.lower():
        raise SystemExit(f"Evidence verifier must not publish releases: {forbidden_publish}")

# The harness itself is evidence tooling, never a publisher.
for forbidden_publish in ("gh release create", "New-GitHubRelease", "Invoke-RestMethod -Method Post"):
    if forbidden_publish.lower() in harness.lower():
        raise SystemExit(f"Interactive sign-off harness must not publish releases: {forbidden_publish}")

# Privacy: friendly hardware names are useful evidence, stable identifiers are not.
for forbidden in ("SerialNumber", "PNPDeviceID", "DeviceID", "$env:USERNAME", "$env:COMPUTERNAME"):
    if forbidden in harness:
        raise SystemExit(f"Windows sign-off evidence must not collect sensitive/stable machine identifiers: {forbidden}")
for required_privacy_text in ("controller_names", "cpu_names", "gpu_names", "memory_gb"):
    if required_privacy_text not in harness:
        raise SystemExit(f"Windows sign-off evidence is missing bounded hardware context: {required_privacy_text}")

# The top-level developer wrapper must own the full chain in strict order. A raw
# lower-level harness PASS is not sufficient for canonical polish closure.
for marker in (
    "windows_demo_signoff.ps1",
    "closing_time_polish_review.ps1",
    "verify_latest_windows_signoff.ps1",
    "fully verified PASS",
    "does NOT publish",
):
    if marker.lower() not in wrapper.lower():
        raise SystemExit(f"One-click developer sign-off wrapper lost required chain marker: {marker}")
if not (
    wrapper.lower().index("windows_demo_signoff.ps1")
    < wrapper.lower().index("closing_time_polish_review.ps1")
    < wrapper.lower().index("verify_latest_windows_signoff.ps1")
):
    raise SystemExit("Developer wrapper order must be base harness -> explicit polish review -> independent verifier")

# Documentation must preserve the distinction between automated preparation,
# lower-level base PASS and final verified target-Windows evidence.
for marker in (
    "WINDOWS-DEMO-SIGNOFF.bat",
    "windows_demo_signoff.ps1",
    "closing_time_polish_review.ps1",
    "verify_latest_windows_signoff.ps1",
    "verify_windows_signoff_evidence.py",
    "manual-save-witness.sha256",
    "non-autosave",
    "--expected-commit",
    "-PrepareOnly",
    "INCOMPLETE",
    "physical controller",
    "real-hardware",
):
    if marker.lower() not in doc.lower():
        raise SystemExit(f"Windows playtest documentation lost required guidance: {marker}")
if "does not publish" not in doc.lower():
    raise SystemExit("Windows playtest documentation must state that the harness does not publish")

# Release-gate checks are intentionally milestone-aware instead of freezing an old
# percentage. Progress math belongs to the SWIR Progress SVG generator/check. This
# contract protects the important semantic distinction: automated packaging may
# complete independently, while the real human target-Windows sign-off, release
# notes and GitHub Release must remain open until their own evidence exists.
if "- [x] Standalone legal content package" not in roadmap:
    raise SystemExit("ROADMAP must reflect the implemented/testable standalone legal-content package")
for open_gate in (
    "- [ ] Release notes",
    "- [ ] GitHub Release",
):
    if open_gate not in roadmap:
        raise SystemExit(f"Windows sign-off tooling must not close release gate: {open_gate}")
if "docs/WINDOWS_PLAYTEST.md" not in roadmap or "verify_windows_signoff_evidence.py" not in roadmap:
    raise SystemExit("ROADMAP must link both target-Windows sign-off and independent evidence verification")
if "interactive target-Windows sign-off" not in roadmap:
    raise SystemExit("ROADMAP must keep the human target-Windows sign-off as an explicit release gate")

# README and ROADMAP must agree on ordinary numeric fallback while the dedicated
# progress generator remains authoritative for weighted math and SVG geometry.
readme_progress = re.search(r"Implemented/testable progress \| \*\*(\d+(?:\.\d+)?)%\*\*", readme)
roadmap_progress = re.search(r"Overall progress:\*\*\s*`\s*(\d+(?:\.\d+)?)%`", roadmap)
if not readme_progress or not roadmap_progress or readme_progress.group(1) != roadmap_progress.group(1):
    raise SystemExit("README/ROADMAP project progress must remain synchronized")
if "Public demo | **Not published yet**" not in readme:
    raise SystemExit("README must not claim a public demo before human release gates pass")

# SVG-only presentation remains enforced: numeric fallback is allowed, text-art
# progress bars are not.
legacy_progress_meter = re.compile(r"(?:[█▓▒░]{2,})|(?:\[(?:[#=\-]{4,})\])")
for path, text in ((README, readme), (ROADMAP, roadmap)):
    if legacy_progress_meter.search(text):
        raise SystemExit(f"Legacy character progress meter returned in {path.name}")

# CI may parse/static-test the harness, but it must never execute the interactive
# sign-off and pretend hosted runners are physical target-machine evidence.
for marker in (
    "python tools/test_windows_demo_signoff_contract.py",
    "python tools/test_windows_signoff_evidence_verifier.py",
    "Parse Windows demo sign-off scripts",
    "System.Management.Automation.Language.Parser",
    "powershell-signoff-parse-report",
):
    if marker not in workflow:
        raise SystemExit(f"CI is not protecting the Windows sign-off chain: {marker}")
if re.search(r"(?m)^\s*run:\s*\.\\tools\\windows_demo_signoff\.ps1\s*$", workflow):
    raise SystemExit("Hosted CI must not execute the interactive Windows sign-off harness")

print("Target Windows demo sign-off contract: PASS")
print("Top-level developer flow now requires gameplay/hardware, explicit Closing Time polish, a hashed non-autosave Graveyard save witness and independent exact-commit evidence verification before final PASS.")