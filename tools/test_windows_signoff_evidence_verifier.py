from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile

from verify_windows_signoff_evidence import EvidenceError, verify_evidence


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_valid_fixture(root: Path) -> tuple[Path, str]:
    evidence_dir = root / "evidence"
    package = evidence_dir / "package"
    commit = "1234567890abcdef1234567890abcdef12345678"
    branch = "automation/windows-signoff-evidence-verifier"

    lock = {
        "schema": 1,
        "gzdoom": {
            "repo": "ZDoom/gzdoom",
            "tag": "g4.14.2",
            "asset_regex": "^gzdoom-.*-windows\\.zip$",
            "asset_name": "gzdoom-4-14-2-windows.zip",
            "asset_id": 251530238,
            "asset_bytes": 21879627,
        },
        "freedoom": {
            "repo": "freedoom/freedoom",
            "tag": "v0.13.0",
            "asset_regex": "^freedoom-[0-9].*\\.zip$",
            "checksum_regex": "^freedoom-.*-CHECKSUM$",
        },
    }
    write_json(package / "runtime-lock.json", lock)

    gzdoom = b"synthetic-gzdoom-exe"
    freedoom = b"synthetic-freedoom-wad"
    game_pk3 = b"synthetic-checkout-of-hell-pk3"
    license_text = b"synthetic BSD notice fixture"
    provenance = {
        "schema": 1,
        "component": "Freedoom",
        "tag": "v0.13.0",
        "wad_path": "external/freedoom2.wad",
        "wad_sha256": digest(freedoom),
        "license_path": "licenses/FREEDOOM-COPYING.adoc",
        "license_sha256": digest(license_text),
        "license": "BSD-3-Clause",
    }

    files = {
        "game/CHECKOUT-OF-HELL.pk3": game_pk3,
        "external/freedoom2.wad": freedoom,
        "licenses/FREEDOOM-COPYING.adoc": license_text,
        "third_party/FREEDOOM-PROVENANCE.json": (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8"),
    }
    for name, data in files.items():
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    gzdoom_path = package / "external/gzdoom/gzdoom.exe"
    gzdoom_path.parent.mkdir(parents=True, exist_ok=True)
    gzdoom_path.write_bytes(gzdoom)

    package_manifest = {
        "schema": 1,
        "package_kind": "windows-portable-release-candidate",
        "public_release": False,
        "source": {"commit": commit, "branch": branch, "clean": True},
        "runtime": {
            "gzdoom_tag": "g4.14.2",
            "gzdoom_delivery": "official-source-bootstrap",
            "freedoom_tag": "v0.13.0",
            "freedoom_delivery": "bundled-verified-content",
        },
        "entries": {
            name: {"bytes": len(data), "sha256": digest(data)}
            for name, data in sorted(files.items())
        },
    }
    write_json(package / "package-manifest.json", package_manifest)
    runtime_manifest = {
        "gzdoom": {
            "tag": "g4.14.2",
            "asset": "gzdoom-4-14-2-windows.zip",
            "asset_id": 251530238,
            "archive_bytes": 21879627,
            "local_sha256": digest(gzdoom),
        },
        "freedoom": {
            "tag": "v0.13.0",
            "delivery": "bundled-verified-content",
            "local_sha256": digest(freedoom),
        },
    }
    write_json(package / "external/runtime-manifest.json", runtime_manifest)

    difficulty = {
        "engine_exit_ok": True,
        "completed": True,
        "no_softlock": True,
        "combat_readable": True,
        "balance_acceptable": True,
    }
    graveyard = dict(difficulty)
    graveyard["save_quit_load"] = True
    evidence = {
        "schema": 1,
        "project": "CHECKOUT OF HELL",
        "scope": "Target Windows demo-readiness sign-off for Closing Time",
        "status": "PASS",
        "source": {"commit": commit, "branch": branch, "clean": True},
        "package": {
            "name": "CHECKOUT-OF-HELL-Windows-Portable-rc.zip",
            "sha256": "a" * 64,
        },
        "runtime": {
            "gzdoom_tag": "g4.14.2",
            "gzdoom_asset": "gzdoom-4-14-2-windows.zip",
            "gzdoom_asset_id": 251530238,
            "gzdoom_local_sha256": digest(gzdoom),
            "freedoom_tag": "v0.13.0",
            "freedoom_wad_sha256": digest(freedoom),
        },
        "automated": {
            "package_built": True,
            "package_integrity": True,
            "runtime_bootstrap": True,
            "save_load_roundtrip": True,
        },
        "manual": {
            "closing_crew": dict(difficulty),
            "graveyard_shift": graveyard,
            "corporate_hell": dict(difficulty),
            "environment_art_consistent": True,
            "objective_route_readable": True,
            "lighting_atmosphere_acceptable": True,
            "clutter_visual_hierarchy_clean": True,
            "controller_core_actions": True,
            "controller_haptics": True,
            "performance_sanity": True,
            "final_polish_signoff": True,
        },
    }
    write_json(evidence_dir / "evidence.json", evidence)
    (evidence_dir / "gzdoom-save-load-smoke.log").write_text(
        "COH_RUNTIME_SAVE_WRITTEN\nCOH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE\n",
        encoding="utf-8",
    )
    manual_save = evidence_dir / "manual-saves/checkout-hell-test.zds"
    manual_save.parent.mkdir(parents=True, exist_ok=True)
    manual_save.write_bytes(b"synthetic manual save")
    (evidence_dir / "REPORT.md").write_text(
        f"# Evidence\n\n**Status:** PASS\n**Source commit:** {commit}\n\n"
        "## Closing Time explicit polish review\n\n"
        "| Gate | Result |\n| --- | --- |\n"
        "| Environment / art consistency | PASS |\n"
        "| Objective / route readability | PASS |\n"
        "| Lighting / atmosphere | PASS |\n"
        "| Clutter / visual hierarchy | PASS |\n",
        encoding="utf-8",
    )
    return evidence_dir, commit


def expect_failure(evidence_dir: Path, label: str) -> None:
    try:
        verify_evidence(evidence_dir)
    except EvidenceError:
        return
    raise SystemExit(f"Verifier accepted invalid evidence: {label}")


with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    evidence_dir, commit = build_valid_fixture(root)
    result = verify_evidence(evidence_dir, expected_commit=commit)
    if result["commit"] != commit:
        raise SystemExit("Verifier returned the wrong source commit")

    game_pk3 = evidence_dir / "package/game/CHECKOUT-OF-HELL.pk3"
    original_game = game_pk3.read_bytes()
    game_pk3.write_bytes(original_game + b"-tampered")
    expect_failure(evidence_dir, "tampered package entry")
    game_pk3.write_bytes(original_game)

    evidence_path = evidence_dir / "evidence.json"
    valid_evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    failed_manual = deepcopy(valid_evidence)
    failed_manual["manual"]["controller_haptics"] = False
    write_json(evidence_path, failed_manual)
    expect_failure(evidence_dir, "failed manual controller haptics gate")
    write_json(evidence_path, valid_evidence)

    failed_polish = deepcopy(valid_evidence)
    failed_polish["manual"]["lighting_atmosphere_acceptable"] = False
    write_json(evidence_path, failed_polish)
    expect_failure(evidence_dir, "failed explicit lighting/atmosphere polish gate")
    write_json(evidence_path, valid_evidence)

    try:
        verify_evidence(evidence_dir, expected_commit="f" * 40)
    except EvidenceError:
        pass
    else:
        raise SystemExit("Verifier accepted evidence for the wrong expected commit")

print("Windows sign-off evidence verifier contract: PASS")
print("Valid evidence passes; tampered package data, failed human/polish gates and stale commits are rejected.")
