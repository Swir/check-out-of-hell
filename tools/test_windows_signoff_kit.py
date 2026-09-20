from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
KIT = DIST / "CHECKOUT-OF-HELL-Windows-Signoff-Kit.zip"
KIT_SHA = KIT.with_suffix(KIT.suffix + ".sha256")
RC = DIST / "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"
SOURCE_FILES = {
    "tools/windows_signoff_kit.ps1": ROOT / "tools" / "windows_signoff_kit.ps1",
    "tools/gzdoom_save_load_smoke.ps1": ROOT / "tools" / "gzdoom_save_load_smoke.ps1",
    "tools/bootstrap_python.ps1": ROOT / "tools" / "bootstrap_python.ps1",
    "tools/verify_windows_signoff_evidence.py": ROOT / "tools" / "verify_windows_signoff_evidence.py",
    "tools/verify_signoff_kit.ps1": ROOT / "tools" / "verify_signoff_kit.ps1",
    "runtime-lock.json": ROOT / "runtime-lock.json",
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

HARNESS = ROOT / "tools" / "windows_signoff_kit.ps1"
VERIFY_HELPER = ROOT / "tools" / "verify_signoff_kit.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "closing-time-signoff-kit.yml"
DOC = ROOT / "docs" / "WINDOWS_SIGNOFF_KIT.md"
for required in (HARNESS, VERIFY_HELPER, WORKFLOW, DOC):
    if not required.is_file():
        raise SystemExit(f"Windows sign-off kit source contract is missing: {required.relative_to(ROOT)}")

harness_text = HARNESS.read_text(encoding="utf-8")
verify_helper_text = VERIFY_HELPER.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")
doc_text = DOC.read_text(encoding="utf-8")
for marker in (
    "SIGNOFF-CANDIDATE.json", "Get-FileHash", "ExpectedRcSha", "package-manifest.json",
    "verify_player_package.ps1", "bootstrap_runtime.ps1", "-PreparedRuntime",
    "Closing Crew", "Graveyard Shift", "Corporate Hell", "controller_core_actions",
    "controller_haptics", "performance_sanity", "final_polish_signoff",
    'if ($allAutomated -and $allManual -and $sourceIsVerifiable)',
    '$Evidence.status = "PASS"', "No release should be published from this result.",
):
    if marker not in harness_text:
        raise SystemExit(f"Windows sign-off kit harness lost required behavior: {marker}")
for forbidden in ("SerialNumber", "PNPDeviceID", "DeviceID", "$env:USERNAME", "$env:COMPUTERNAME", "gh release create", "New-GitHubRelease"):
    if forbidden.lower() in harness_text.lower():
        raise SystemExit(f"Windows sign-off kit harness contains forbidden behavior/data: {forbidden}")
for marker in ("bootstrap_python.ps1", "verify_windows_signoff_evidence.py", "--expected-commit"):
    if marker not in verify_helper_text:
        raise SystemExit(f"Kit evidence helper lost required behavior: {marker}")
for marker in ("package_windows_signoff_kit.py", "test_windows_signoff_kit.py", "actions/upload-artifact@v4", "windows-script-parse"):
    if marker not in workflow_text:
        raise SystemExit(f"Sign-off-kit workflow lost required gate: {marker}")
if "windows_signoff_kit.ps1" in workflow_text and r"-File .\tools\windows_signoff_kit.ps1" in workflow_text:
    raise SystemExit("Hosted CI must not execute the interactive Windows sign-off kit harness")
for marker in ("physical controller", "not a public demo", "exact candidate", "RUN-SIGNOFF.bat", "VERIFY-EVIDENCE.bat"):
    if marker.lower() not in doc_text.lower():
        raise SystemExit(f"Sign-off kit documentation lost required guidance: {marker}")

for required in (KIT, KIT_SHA, RC, *SOURCE_FILES.values()):
    if not required.is_file():
        raise SystemExit(f"Windows sign-off kit contract is missing required file: {required}")


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


kit_bytes = KIT.read_bytes()
actual_kit_sha = digest(kit_bytes)
checksum_match = re.search(r"\b([0-9a-fA-F]{64})\b", KIT_SHA.read_text(encoding="utf-8"))
if not checksum_match or checksum_match.group(1).lower() != actual_kit_sha:
    raise SystemExit("Windows sign-off kit outer SHA-256 file does not match the ZIP")

with zipfile.ZipFile(KIT, "r") as archive:
    names = set(archive.namelist())
    required_names = {
        "RUN-SIGNOFF.bat", "VERIFY-EVIDENCE.bat", "README-SIGNOFF.txt", "SIGNOFF-CANDIDATE.json",
        "signoff-kit-manifest.json", "candidate/CHECKOUT-OF-HELL-Windows-Portable-rc.zip",
        "candidate/CHECKOUT-OF-HELL-Windows-Portable-rc.zip.sha256", *SOURCE_FILES.keys(),
    }
    missing = required_names - names
    if missing:
        raise SystemExit(f"Windows sign-off kit is missing entries: {sorted(missing)}")

    candidate = json.loads(archive.read("SIGNOFF-CANDIDATE.json").decode("utf-8"))
    kit_manifest = json.loads(archive.read("signoff-kit-manifest.json").decode("utf-8"))
    if candidate.get("schema") != 1 or candidate.get("project") != "CHECKOUT OF HELL" or candidate.get("public_release") is not False:
        raise SystemExit("SIGNOFF-CANDIDATE.json identity/public-release contract failed")
    commit = str(candidate.get("source", {}).get("commit", "")).lower()
    branch = str(candidate.get("source", {}).get("branch", ""))
    if not COMMIT_RE.fullmatch(commit) or not branch or branch == "UNAVAILABLE" or candidate.get("source", {}).get("clean") is not True:
        raise SystemExit("Sign-off kit candidate is not bound to a clean commit-addressable source snapshot")
    rc_sha = str(candidate.get("rc_sha256", "")).lower()
    if not SHA_RE.fullmatch(rc_sha):
        raise SystemExit("Sign-off kit candidate RC SHA-256 is invalid")
    embedded_rc = archive.read("candidate/CHECKOUT-OF-HELL-Windows-Portable-rc.zip")
    if digest(embedded_rc) != rc_sha or digest(RC.read_bytes()) != rc_sha:
        raise SystemExit("Sign-off kit embedded RC does not match the exact CI-built RC")

    with zipfile.ZipFile(RC, "r") as rc_archive:
        rc_manifest = json.loads(rc_archive.read("package-manifest.json").decode("utf-8"))
    if str(rc_manifest.get("source", {}).get("commit", "")).lower() != commit:
        raise SystemExit("Kit candidate commit does not match RC package-manifest provenance")
    if str(rc_manifest.get("source", {}).get("branch", "")) != branch or rc_manifest.get("source", {}).get("clean") is not True:
        raise SystemExit("Kit candidate branch/clean provenance does not match RC package manifest")

    if kit_manifest.get("package_kind") != "windows-closing-time-signoff-kit" or kit_manifest.get("public_release") is not False:
        raise SystemExit("Sign-off kit manifest kind/public-release contract failed")
    for entry_name, record in kit_manifest.get("entries", {}).items():
        payload = archive.read(entry_name)
        if record.get("bytes") != len(payload) or record.get("sha256") != digest(payload):
            raise SystemExit(f"Sign-off kit manifest mismatch for {entry_name}")

    for entry_name, source_path in SOURCE_FILES.items():
        if archive.read(entry_name) != source_path.read_bytes():
            raise SystemExit(f"Sign-off kit carries a stale source tool: {entry_name}")

    runner = archive.read("RUN-SIGNOFF.bat").decode("utf-8")
    verify = archive.read("VERIFY-EVIDENCE.bat").decode("utf-8")
    readme = archive.read("README-SIGNOFF.txt").decode("utf-8")
    for marker in ("windows_signoff_kit.ps1", "SIGNOFF-CANDIDATE.json", "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"):
        if marker not in runner:
            raise SystemExit(f"One-click sign-off runner lost required binding: {marker}")
    if "verify_signoff_kit.ps1" not in verify:
        raise SystemExit("One-click evidence verifier wrapper is not wired")
    for marker in ("not a public demo", "physical controller", "official upstream", "VERIFY-EVIDENCE.bat"):
        if marker.lower() not in readme.lower():
            raise SystemExit(f"Sign-off kit README lost required guidance: {marker}")
    if "gh release create" in runner.lower() or "gh release create" in verify.lower():
        raise SystemExit("Sign-off kit must never publish a release")

print("Windows Closing Time sign-off kit contract: PASS")
print(f"Candidate: {branch} @ {commit}")
print(f"RC SHA-256: {rc_sha}")
