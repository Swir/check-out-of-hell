#!/usr/bin/env python3
"""Run a real pinned-GZDoom save -> process exit -> load round-trip under Xvfb."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
FREEDOOM = ROOT / "external" / "linux-ci" / "freedoom2.wad"
WORK = ROOT / "dist" / "save-load-runtime"
SAVES = WORK / "saves"
ENGINE_INI = WORK / "gzdoom-ci.ini"
SAVE_CFG = WORK / "save-roundtrip.cfg"
LOAD_CFG = WORK / "load-roundtrip.cfg"
SAVE_LOG = WORK / "save.stdout.log"
LOAD_LOG = WORK / "load.stdout.log"
COMBINED_LOG = ROOT / "dist" / "gzdoom-save-load-smoke.log"
SAVE_STEM = "coh-ci-roundtrip"
FUSE_RE = re.compile(r"CheckoutFuse\s+#\d+\s+\(2/3\)")


def run_checked(command: list[str], *, timeout: int = 45) -> str:
    env = os.environ.copy()
    env["LIBGL_ALWAYS_SOFTWARE"] = "1"
    env.setdefault("MESA_LOADER_DRIVER_OVERRIDE", "llvmpipe")
    process = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {process.returncode}: {' '.join(command)}\n{process.stdout}")
    return process.stdout


def assert_clean_runtime(log: str, label: str) -> None:
    for marker in (
        "Script error",
        "Execution could not continue",
        "Unknown class",
        "Unknown identifier",
        "Invalid parameter",
        "Parse error",
        "Cannot load savegame",
        "Savegame is from a different",
        "Could not open savegame",
    ):
        if marker in log:
            raise AssertionError(f"{label} reported {marker!r}\n{log}")


def engine_command(gzdoom: str, cfg: Path) -> list[str]:
    return [
        "xvfb-run",
        "-a",
        "-s",
        "-screen 0 640x480x24",
        gzdoom,
        "-stdout",
        "-nosound",
        "-config",
        str(ENGINE_INI),
        "-iwad",
        str(FREEDOOM),
        "-file",
        str(PK3),
        "-savedir",
        str(SAVES),
        "+exec",
        str(cfg),
    ]


def main() -> None:
    gzdoom = shutil.which("gzdoom")
    if not gzdoom:
        raise RuntimeError("gzdoom is not installed; run tools/bootstrap_linux_ci_runtime.py and install its .deb first")
    if not shutil.which("xvfb-run"):
        raise RuntimeError("xvfb-run is not installed")

    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=ROOT, check=True)
    for required in (PK3, FREEDOOM):
        if not required.is_file():
            raise RuntimeError(f"Runtime prerequisite is missing: {required}")

    if WORK.exists():
        shutil.rmtree(WORK)
    SAVES.mkdir(parents=True)

    ENGINE_INI.write_text(
        "[GlobalSettings]\n"
        "vid_preferbackend=0\n"
        "vid_fullscreen=false\n"
        "i_pauseinbackground=false\n"
        "i_soundinbackground=false\n",
        encoding="ascii",
    )
    SAVE_CFG.write_text(
        'wait 175; give CheckoutFuse 2; wait 10; printinv; '
        f'save {SAVE_STEM} "CHECKOUT OF HELL CI ROUNDTRIP"; '
        'wait 70; echo COH_RUNTIME_SAVE_WRITTEN; quit\n',
        encoding="ascii",
    )
    LOAD_CFG.write_text(
        "wait 175; printinv; echo COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE; wait 10; quit\n",
        encoding="ascii",
    )

    print("Runtime pass 1/2: start MAP01, mutate objective state, save, then exit GZDoom...")
    save_command = engine_command(gzdoom, SAVE_CFG)
    # Put MAP01 before +exec so the deferred command chain starts from the real level.
    insert_at = save_command.index("+exec")
    save_command[insert_at:insert_at] = ["+map", "MAP01"]
    save_log = run_checked(save_command)
    SAVE_LOG.write_text(save_log, encoding="utf-8")
    assert_clean_runtime(save_log, "save pass")
    if "COH_RUNTIME_SAVE_WRITTEN" not in save_log:
        raise AssertionError(f"Save pass did not reach its completion sentinel.\n{save_log}")
    if not FUSE_RE.search(save_log):
        raise AssertionError(f"Save pass did not expose CheckoutFuse 2/3 before saving.\n{save_log}")

    save_files = [path for path in SAVES.glob(f"{SAVE_STEM}*.zds") if path.stat().st_size > 0]
    if len(save_files) != 1:
        raise AssertionError(f"Expected exactly one non-empty {SAVE_STEM} savegame; found {len(save_files)}")

    print("Runtime pass 2/2: new GZDoom process, load savegame, verify serialized objective state...")
    load_command = engine_command(gzdoom, LOAD_CFG)
    insert_at = load_command.index("+exec")
    load_command[insert_at:insert_at] = ["-loadgame", SAVE_STEM]
    load_log = run_checked(load_command)
    LOAD_LOG.write_text(load_log, encoding="utf-8")
    assert_clean_runtime(load_log, "load pass")
    if "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE" not in load_log:
        raise AssertionError(f"Load pass did not reach its completion sentinel.\n{load_log}")
    if not FUSE_RE.search(load_log):
        raise AssertionError(f"CheckoutFuse 2/3 did not survive save -> exit -> load.\n{load_log}")

    COMBINED_LOG.write_text(
        "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke\n\n"
        "=== SAVE PASS ===\n"
        + save_log
        + "\n=== LOAD PASS ===\n"
        + load_log
        + "\nPASS: CheckoutFuse 2/3 survived a real GZDoom save -> process exit -> load round-trip.\n",
        encoding="utf-8",
    )
    print("GZDoom runtime save/load round-trip: PASS")


if __name__ == "__main__":
    main()
