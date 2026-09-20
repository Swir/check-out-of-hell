from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RC_ZIP = DIST / "CHECKOUT-OF-HELL-Windows-Portable-rc.zip"
RC_CHECKSUM = RC_ZIP.with_suffix(RC_ZIP.suffix + ".sha256")
OUTPUT = DIST / "CHECKOUT-OF-HELL-Windows-Signoff-Kit.zip"
OUTPUT_CHECKSUM = OUTPUT.with_suffix(OUTPUT.suffix + ".sha256")
PACKAGE_MANIFEST = "package-manifest.json"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

RUNNER = r'''@echo off
setlocal
cd /d "%~dp0"
echo CHECKOUT OF HELL - Closing Time target-Windows sign-off kit
echo This kit never publishes a release. It records local evidence only.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\tools\windows_signoff_kit.ps1" -CandidateManifest ".\SIGNOFF-CANDIDATE.json" -RcZip ".\candidate\CHECKOUT-OF-HELL-Windows-Portable-rc.zip" -EvidenceRoot ".\evidence"
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" goto :done
echo.
echo Base gameplay/hardware sign-off passed. Running explicit Closing Time polish review...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\tools\closing_time_polish_review.ps1" -CandidateManifest ".\SIGNOFF-CANDIDATE.json" -EvidenceRoot ".\evidence"
set "EXITCODE=%ERRORLEVEL%"
:done
echo.
if "%EXITCODE%"=="0" (
  echo Sign-off harness and explicit polish review reported PASS. Run VERIFY-EVIDENCE.bat before accepting the evidence.
) else (
  echo Sign-off did not produce a fully verified polish PASS. No release is authorized.
)
pause
exit /b %EXITCODE%
'''

VERIFY = r'''@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\tools\verify_signoff_kit.ps1" %*
set "EXITCODE=%ERRORLEVEL%"
echo.
pause
exit /b %EXITCODE%
'''

README = """CHECKOUT OF HELL — Closing Time Target-Windows Sign-off Kit

THIS IS A HUMAN QA KIT, NOT A PUBLIC DEMO OR GITHUB RELEASE.

Purpose
=======
This artifact binds the exact CI-built Windows release candidate to the exact Git
commit that produced it and removes the need for a tester to clone the repository,
install Python, search for GZDoom/Freedoom, or rebuild the candidate manually.

How to use
==========
1. Extract this whole ZIP to a normal writable Windows folder.
2. Connect the physical controller you intend to test.
3. Double-click RUN-SIGNOFF.bat.
4. Follow the three real Closing Time playthroughs and answer only from what
   actually happened on the tested machine.
5. After the gameplay/hardware pass, complete the explicit final-polish review for
   environment/art consistency, objective/route readability, lighting/atmosphere,
   and clutter/visual hierarchy.
6. After a full PASS, double-click VERIFY-EVIDENCE.bat. The independent verifier
   checks the newest evidence directory against this kit's exact candidate commit.

The sign-off harness automatically verifies the embedded RC hash and source
provenance, extracts the player package, verifies its manifest, obtains missing
GZDoom only from the pinned official upstream source, reuses the bundled verified
Freedoom content, and performs the automated save -> exit -> load round-trip before
human play begins.

No file in this kit publishes a release. PASS evidence is necessary for the
Closing Time polish gate, but ROADMAP release gates still apply.

Project: https://github.com/Swir/check-out-of-hell
by Swir
"""


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def deterministic_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o644 & 0xFFFF) << 16
    return info


def read_required(path: Path) -> bytes:
    if not path.is_file():
        raise SystemExit(f"Sign-off kit input is missing: {path}")
    return path.read_bytes()


def parse_checksum(path: Path) -> str:
    text = read_required(path).decode("utf-8", errors="strict")
    match = re.search(r"\b([0-9a-fA-F]{64})\b", text)
    if not match:
        raise SystemExit(f"No SHA-256 found in {path}")
    return match.group(1).lower()


def load_rc_manifest(rc_bytes: bytes) -> dict:
    try:
        from io import BytesIO
        with zipfile.ZipFile(BytesIO(rc_bytes), "r") as archive:
            raw = archive.read(PACKAGE_MANIFEST)
    except (zipfile.BadZipFile, KeyError) as exc:
        raise SystemExit(f"RC ZIP is invalid or missing {PACKAGE_MANIFEST}: {exc}") from exc
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"RC package manifest is invalid JSON: {exc}") from exc
    if manifest.get("schema") != 1 or manifest.get("package_kind") != "windows-portable-release-candidate":
        raise SystemExit("RC package manifest is not the expected Windows release candidate")
    if manifest.get("public_release") is not False:
        raise SystemExit("RC unexpectedly claims to be a public release")
    return manifest


def main() -> int:
    rc_bytes = read_required(RC_ZIP)
    actual_rc_sha = digest(rc_bytes)
    checksum_sha = parse_checksum(RC_CHECKSUM)
    if actual_rc_sha != checksum_sha:
        raise SystemExit(
            f"RC checksum mismatch: checksum file says {checksum_sha}, actual ZIP is {actual_rc_sha}"
        )

    manifest = load_rc_manifest(rc_bytes)
    source = manifest.get("source")
    if not isinstance(source, dict):
        raise SystemExit("RC package manifest is missing source provenance")
    commit = str(source.get("commit", "")).lower()
    branch = str(source.get("branch", ""))
    clean = source.get("clean")
    if not COMMIT_RE.fullmatch(commit):
        raise SystemExit(f"RC source commit is not a full Git SHA: {commit!r}")
    if not branch or branch == "UNAVAILABLE":
        raise SystemExit("RC source branch/ref is unavailable")
    if clean is not True:
        raise SystemExit("Sign-off kit requires an RC built from a clean source snapshot")

    candidate = {
        "schema": 1,
        "project": "CHECKOUT OF HELL",
        "scope": "Closing Time target-Windows final-polish sign-off",
        "public_release": False,
        "package_name": RC_ZIP.name,
        "rc_sha256": actual_rc_sha,
        "source": {"commit": commit, "branch": branch, "clean": True},
    }
    candidate_bytes = (json.dumps(candidate, indent=2, sort_keys=True) + "\n").encode("utf-8")

    entries: dict[str, bytes] = {
        "RUN-SIGNOFF.bat": RUNNER.replace("\n", "\r\n").encode("utf-8"),
        "VERIFY-EVIDENCE.bat": VERIFY.replace("\n", "\r\n").encode("utf-8"),
        "README-SIGNOFF.txt": README.replace("\n", "\r\n").encode("utf-8"),
        "SIGNOFF-CANDIDATE.json": candidate_bytes,
        f"candidate/{RC_ZIP.name}": rc_bytes,
        f"candidate/{RC_CHECKSUM.name}": read_required(RC_CHECKSUM),
        "runtime-lock.json": read_required(ROOT / "runtime-lock.json"),
        "tools/windows_signoff_kit.ps1": read_required(ROOT / "tools" / "windows_signoff_kit.ps1"),
        "tools/closing_time_polish_review.ps1": read_required(ROOT / "tools" / "closing_time_polish_review.ps1"),
        "tools/gzdoom_save_load_smoke.ps1": read_required(ROOT / "tools" / "gzdoom_save_load_smoke.ps1"),
        "tools/bootstrap_python.ps1": read_required(ROOT / "tools" / "bootstrap_python.ps1"),
        "tools/verify_windows_signoff_evidence.py": read_required(ROOT / "tools" / "verify_windows_signoff_evidence.py"),
        "tools/verify_signoff_kit.ps1": read_required(ROOT / "tools" / "verify_signoff_kit.ps1"),
    }

    kit_manifest = {
        "schema": 1,
        "package_kind": "windows-closing-time-signoff-kit",
        "public_release": False,
        "candidate": candidate,
        "entries": {
            name: {"bytes": len(data), "sha256": digest(data)}
            for name, data in sorted(entries.items())
        },
    }
    entries["signoff-kit-manifest.json"] = (
        json.dumps(kit_manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    DIST.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w") as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(deterministic_info(name), data)

    output_sha = digest(OUTPUT.read_bytes())
    OUTPUT_CHECKSUM.write_text(f"{output_sha}  {OUTPUT.name}\n", encoding="utf-8")
    print(f"Windows sign-off kit: {OUTPUT}")
    print(f"Candidate source: {branch} @ {commit}")
    print(f"Embedded RC SHA-256: {actual_rc_sha}")
    print(f"Kit SHA-256: {output_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
