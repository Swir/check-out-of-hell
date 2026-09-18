from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

PROJECT = "CHECKOUT OF HELL"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class EvidenceError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise EvidenceError(message)


def load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        fail(f"Missing {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"Invalid {label}: {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"{label} must be a JSON object: {path}")
    return data


def file_sha256(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing file required by evidence: {path}")
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_true(value: object, label: str) -> None:
    if value is not True:
        fail(f"Required gate is not PASS: {label}")


def require_sha(value: object, label: str, pattern: re.Pattern[str]) -> str:
    text = str(value or "").lower()
    if not pattern.fullmatch(text):
        fail(f"Invalid {label}: {value!r}")
    return text


def get(mapping: dict, *keys: str) -> object:
    current: object = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            fail("Missing evidence field: " + ".".join(keys))
        current = current[key]
    return current


def verify_entry(package_root: Path, entry_name: str, record: dict) -> None:
    path = package_root / Path(entry_name)
    if not path.is_file():
        fail(f"Package manifest entry is missing from extracted evidence package: {entry_name}")
    expected_bytes = record.get("bytes")
    expected_sha = str(record.get("sha256", "")).lower()
    if not isinstance(expected_bytes, int) or expected_bytes < 0:
        fail(f"Invalid package manifest byte count for {entry_name}")
    if not SHA256_RE.fullmatch(expected_sha):
        fail(f"Invalid package manifest SHA-256 for {entry_name}")
    if path.stat().st_size != expected_bytes:
        fail(
            f"Package manifest byte-count mismatch for {entry_name}: "
            f"expected {expected_bytes}, got {path.stat().st_size}"
        )
    actual_sha = file_sha256(path)
    if actual_sha != expected_sha:
        fail(
            f"Package manifest SHA-256 mismatch for {entry_name}: "
            f"expected {expected_sha}, got {actual_sha}"
        )


def verify_evidence(evidence_dir: Path, *, expected_commit: str | None = None) -> dict[str, str]:
    evidence_dir = evidence_dir.resolve()
    evidence = load_json(evidence_dir / "evidence.json", "evidence.json")
    if evidence.get("schema") != 1:
        fail(f"Unsupported evidence schema: {evidence.get('schema')!r}")
    if evidence.get("project") != PROJECT:
        fail(f"Unexpected project in evidence: {evidence.get('project')!r}")
    if evidence.get("status") != "PASS":
        fail(f"Windows sign-off evidence status is not PASS: {evidence.get('status')!r}")

    source_commit = require_sha(get(evidence, "source", "commit"), "source commit", COMMIT_RE)
    if expected_commit is not None:
        expected_commit = expected_commit.lower()
        if not COMMIT_RE.fullmatch(expected_commit):
            fail(f"--expected-commit must be a full 40-character SHA: {expected_commit!r}")
        if source_commit != expected_commit:
            fail(f"Evidence commit {source_commit} does not match expected commit {expected_commit}")
    require_true(get(evidence, "source", "clean"), "clean source tree")
    source_branch = str(get(evidence, "source", "branch"))
    if not source_branch or source_branch == "UNAVAILABLE":
        fail("Evidence source branch/ref is unavailable")

    outer_rc_sha = require_sha(get(evidence, "package", "sha256"), "RC SHA-256", SHA256_RE)
    if get(evidence, "package", "name") != "CHECKOUT-OF-HELL-Windows-Portable-rc.zip":
        fail("Evidence package name is not the expected Windows release-candidate ZIP")

    for field in ("package_built", "package_integrity", "runtime_bootstrap", "save_load_roundtrip"):
        require_true(get(evidence, "automated", field), f"automated.{field}")

    for difficulty in ("closing_crew", "graveyard_shift", "corporate_hell"):
        for field in ("engine_exit_ok", "completed", "no_softlock", "combat_readable", "balance_acceptable"):
            require_true(get(evidence, "manual", difficulty, field), f"manual.{difficulty}.{field}")
    require_true(get(evidence, "manual", "graveyard_shift", "save_quit_load"), "manual.graveyard_shift.save_quit_load")
    for field in ("controller_core_actions", "controller_haptics", "performance_sanity", "final_polish_signoff"):
        require_true(get(evidence, "manual", field), f"manual.{field}")

    package_root = evidence_dir / "package"
    lock = load_json(package_root / "runtime-lock.json", "runtime-lock.json")
    package_manifest = load_json(package_root / "package-manifest.json", "package-manifest.json")
    runtime_manifest = load_json(package_root / "external" / "runtime-manifest.json", "runtime-manifest.json")
    freedoom_provenance = load_json(
        package_root / "third_party" / "FREEDOOM-PROVENANCE.json",
        "FREEDOOM-PROVENANCE.json",
    )

    if package_manifest.get("schema") != 1 or package_manifest.get("package_kind") != "windows-portable-release-candidate":
        fail("Extracted package manifest is not the expected Windows release candidate")
    if package_manifest.get("public_release") is not False:
        fail("Evidence package unexpectedly claims to be a public release")
    package_source = package_manifest.get("source")
    if not isinstance(package_source, dict):
        fail("Package manifest is missing source provenance")
    if str(package_source.get("commit", "")).lower() != source_commit:
        fail("Package manifest source commit does not match sign-off evidence")
    if package_source.get("clean") is not True:
        fail("Package manifest source snapshot is not clean")
    if str(package_source.get("branch", "")) != source_branch:
        fail("Package manifest source branch/ref does not match sign-off evidence")

    lock_gzdoom = get(lock, "gzdoom")
    lock_freedoom = get(lock, "freedoom")
    if not isinstance(lock_gzdoom, dict) or not isinstance(lock_freedoom, dict):
        fail("runtime-lock.json has invalid runtime sections")

    expected_gzdoom_tag = str(lock_gzdoom.get("tag"))
    expected_gzdoom_asset = str(lock_gzdoom.get("asset_name"))
    expected_gzdoom_asset_id = int(lock_gzdoom.get("asset_id"))
    expected_gzdoom_bytes = int(lock_gzdoom.get("asset_bytes"))
    expected_freedoom_tag = str(lock_freedoom.get("tag"))

    manifest_runtime = package_manifest.get("runtime")
    if not isinstance(manifest_runtime, dict):
        fail("Package manifest is missing runtime provenance")
    if manifest_runtime.get("gzdoom_tag") != expected_gzdoom_tag:
        fail("Package manifest GZDoom tag does not match runtime lock")
    if manifest_runtime.get("gzdoom_delivery") != "official-source-bootstrap":
        fail("Package manifest GZDoom delivery mode changed")
    if manifest_runtime.get("freedoom_tag") != expected_freedoom_tag:
        fail("Package manifest Freedoom tag does not match runtime lock")
    if manifest_runtime.get("freedoom_delivery") != "bundled-verified-content":
        fail("Package manifest Freedoom delivery mode changed")

    entries = package_manifest.get("entries")
    if not isinstance(entries, dict) or not entries:
        fail("Package manifest has no integrity entries")
    for entry_name, record in sorted(entries.items()):
        if not isinstance(entry_name, str) or not isinstance(record, dict):
            fail("Package manifest contains an invalid entry record")
        verify_entry(package_root, entry_name, record)

    runtime_gzdoom = runtime_manifest.get("gzdoom")
    runtime_freedoom = runtime_manifest.get("freedoom")
    if not isinstance(runtime_gzdoom, dict) or not isinstance(runtime_freedoom, dict):
        fail("Runtime manifest is missing GZDoom/Freedoom sections")

    gzdoom_hash = require_sha(runtime_gzdoom.get("local_sha256"), "runtime GZDoom SHA-256", SHA256_RE)
    freedoom_hash = require_sha(runtime_freedoom.get("local_sha256"), "runtime Freedoom SHA-256", SHA256_RE)
    if (
        runtime_gzdoom.get("tag") != expected_gzdoom_tag
        or runtime_gzdoom.get("asset") != expected_gzdoom_asset
        or int(runtime_gzdoom.get("asset_id")) != expected_gzdoom_asset_id
        or int(runtime_gzdoom.get("archive_bytes")) != expected_gzdoom_bytes
    ):
        fail("Runtime GZDoom identity does not match runtime-lock.json")
    if runtime_freedoom.get("tag") != expected_freedoom_tag:
        fail("Runtime Freedoom tag does not match runtime-lock.json")
    if runtime_freedoom.get("delivery") != "bundled-verified-content":
        fail("Runtime Freedoom delivery is not bundled-verified-content")

    evidence_gzdoom_hash = require_sha(
        get(evidence, "runtime", "gzdoom_local_sha256"),
        "evidence GZDoom SHA-256",
        SHA256_RE,
    )
    evidence_freedoom_hash = require_sha(
        get(evidence, "runtime", "freedoom_wad_sha256"),
        "evidence Freedoom SHA-256",
        SHA256_RE,
    )
    if get(evidence, "runtime", "gzdoom_tag") != expected_gzdoom_tag:
        fail("Evidence GZDoom tag does not match runtime lock")
    if get(evidence, "runtime", "gzdoom_asset") != expected_gzdoom_asset:
        fail("Evidence GZDoom asset does not match runtime lock")
    if int(get(evidence, "runtime", "gzdoom_asset_id")) != expected_gzdoom_asset_id:
        fail("Evidence GZDoom asset ID does not match runtime lock")
    if get(evidence, "runtime", "freedoom_tag") != expected_freedoom_tag:
        fail("Evidence Freedoom tag does not match runtime lock")
    if evidence_gzdoom_hash != gzdoom_hash:
        fail("Evidence GZDoom hash does not match the runtime manifest")
    if evidence_freedoom_hash != freedoom_hash:
        fail("Evidence Freedoom hash does not match the runtime manifest")

    gzdoom_exe = package_root / "external" / "gzdoom" / "gzdoom.exe"
    freedoom_wad = package_root / "external" / "freedoom2.wad"
    if file_sha256(gzdoom_exe) != gzdoom_hash:
        fail("Installed GZDoom executable hash no longer matches evidence")
    if file_sha256(freedoom_wad) != freedoom_hash:
        fail("Bundled Freedoom WAD hash no longer matches evidence")

    if freedoom_provenance.get("tag") != expected_freedoom_tag:
        fail("Freedoom provenance tag does not match runtime lock")
    if freedoom_provenance.get("wad_path") != "external/freedoom2.wad":
        fail("Freedoom provenance WAD path changed")
    provenance_wad_hash = require_sha(
        freedoom_provenance.get("wad_sha256"),
        "Freedoom provenance WAD SHA-256",
        SHA256_RE,
    )
    if provenance_wad_hash != freedoom_hash:
        fail("Freedoom provenance hash does not match the bundled WAD")

    save_load_log = evidence_dir / "gzdoom-save-load-smoke.log"
    if not save_load_log.is_file():
        fail(f"Missing save/load log: {save_load_log}")
    log_text = save_load_log.read_text(encoding="utf-8", errors="replace")
    for marker in ("COH_RUNTIME_SAVE_WRITTEN", "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE"):
        if marker not in log_text:
            fail(f"Save/load evidence log is missing marker: {marker}")

    manual_save_dir = evidence_dir / "manual-saves"
    if not manual_save_dir.is_dir() or not any(path.is_file() for path in manual_save_dir.rglob("*")):
        fail("Manual Graveyard Shift evidence contains no saved-game file")

    report = evidence_dir / "REPORT.md"
    if not report.is_file():
        fail(f"Missing human-readable evidence report: {report}")
    report_text = report.read_text(encoding="utf-8-sig", errors="replace")
    if "**Status:** PASS" not in report_text:
        fail("REPORT.md does not record PASS")
    if source_commit not in report_text.lower():
        fail("REPORT.md does not contain the source commit")

    return {
        "commit": source_commit,
        "branch": source_branch,
        "rc_sha256": outer_rc_sha,
        "gzdoom_tag": expected_gzdoom_tag,
        "freedoom_tag": expected_freedoom_tag,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Independently verify a completed CHECKOUT OF HELL target-Windows "
            "sign-off evidence directory without replaying human judgments."
        )
    )
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument(
        "--expected-commit",
        help="Require the PASS evidence to belong to this exact 40-character Git commit.",
    )
    args = parser.parse_args(argv)

    try:
        result = verify_evidence(args.evidence_dir, expected_commit=args.expected_commit)
    except EvidenceError as exc:
        print(f"Windows sign-off evidence verification: FAIL: {exc}", file=sys.stderr)
        print("No release should be published from this result.", file=sys.stderr)
        return 2

    print("Windows sign-off evidence verification: PASS")
    print(f"Source: {result['branch']} @ {result['commit']}")
    print(f"RC SHA-256: {result['rc_sha256']}")
    print(f"Runtime: GZDoom {result['gzdoom_tag']} / Freedoom {result['freedoom_tag']}")
    print("This verifier confirms evidence consistency only; it does not publish or authorize a demo by itself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
