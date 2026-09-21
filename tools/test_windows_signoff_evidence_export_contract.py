from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools" / "verify_signoff_kit.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "closing-time-signoff-kit.yml"
DOC = ROOT / "docs" / "WINDOWS_SIGNOFF_KIT.md"

for required in (HELPER, WORKFLOW, DOC):
    if not required.is_file():
        raise SystemExit(f"Windows sign-off evidence-export contract is missing: {required.relative_to(ROOT)}")

helper_text = HELPER.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")
doc_text = DOC.read_text(encoding="utf-8")

for marker in (
    "verify_windows_signoff_evidence.py",
    "$VerifierExitCode = $LASTEXITCODE",
    "if ($VerifierExitCode -ne 0)",
    'Join-Path $KitRoot "evidence-export"',
    "CHECKOUT-OF-HELL-Windows-Signoff-Evidence-",
    "Compress-Archive",
    "Get-FileHash -LiteralPath $OutputZip -Algorithm SHA256",
    '$OutputChecksum = "$OutputZip.sha256"',
    "You can upload/send this ZIP",
):
    if marker not in helper_text:
        raise SystemExit(f"Verified-evidence export lost required behavior: {marker}")

if not (
    helper_text.index("verify_windows_signoff_evidence.py")
    < helper_text.index("$VerifierExitCode = $LASTEXITCODE")
    < helper_text.index("Compress-Archive")
):
    raise SystemExit("Evidence must be independently verified before any upload bundle is created")

for forbidden in ("gh release create", "New-GitHubRelease", "Invoke-RestMethod -Method Post"):
    if forbidden.lower() in helper_text.lower():
        raise SystemExit(f"Evidence export must never publish or upload automatically: {forbidden}")

if "test_windows_signoff_evidence_export_contract.py" not in workflow_text:
    raise SystemExit("Closing Time sign-off workflow does not run the evidence-export contract")

for marker in ("evidence-export", "ready-to-upload", "SHA-256"):
    if marker.lower() not in doc_text.lower():
        raise SystemExit(f"Windows sign-off kit documentation lost evidence-export guidance: {marker}")

print("Windows sign-off verified-evidence export contract: PASS")
