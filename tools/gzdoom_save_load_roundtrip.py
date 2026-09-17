#!/usr/bin/env python3
"""Exercise a real process-to-process GZDoom save/load roundtrip."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
ROUNDTRIP = ROOT / "dist" / "save-load-roundtrip"
SAVE_DIR = ROUNDTRIP / "saves"
INI_PATH = ROUNDTRIP / "gzdoom-ci.ini"
COMMAND_PATH = ROUNDTRIP / "roundtrip.cfg"
PHASE_TIMEOUT_SECONDS = 45

ERROR_MARKERS = (
    "Script error",
    "Execution could not continue",
    "Unknown class",
    "Unknown identifier",
    "Unknown command",
    "Invalid parameter",
    "Parse error",
    "Cannot find savegame",
    "Savegame is from a different version",
    "Savegame is incompatible",
    "DIED WITH FATAL ERROR",
)
FUSE_RE = re.compile(r"CheckoutFuse #[0-9]+ \(2/3\)")
MEMO_RE = re.compile(r"CorporateMemo #[0-9]+ \(1/3\)")


def run_phase(executable: Path, iwad: Path, commands: str, phase: str) -> str:
    COMMAND_PATH.write_text(commands + "\n", encoding="ascii")
    phase_log = ROUNDTRIP / f"{phase}-phase.log"
    phase_log.unlink(missing_ok=True)

    # Do not pass -errorlog here. In GZDoom it intentionally enables batch mode,
    # which exits after initialization instead of entering the live game loop.
    # Parser-only smoke tests use -errorlog separately; this harness needs real play.
    argv = [
        str(executable),
        "-stdout",
        "-window",
        "-width",
        "640",
        "-height",
        "480",
        "-nosound",
        "-nomusic",
        "-noautoload",
        "-config",
        str(INI_PATH),
        "-savedir",
        str(SAVE_DIR),
        "-iwad",
        str(iwad),
        "-file",
        str(PK3),
        "+i_pauseinbackground",
        "0",
        "+exec",
        str(COMMAND_PATH),
    ]

    print(f"Running GZDoom {phase} phase...")
    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=PHASE_TIMEOUT_SECONDS,
            env=os.environ.copy(),
            check=False,
        )
        text = completed.stdout or ""
        return_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        text = exc.stdout or ""
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        phase_log.write_text(text, encoding="utf-8")
        raise RuntimeError(f"GZDoom {phase} phase timed out after {PHASE_TIMEOUT_SECONDS}s; see {phase_log}") from exc

    phase_log.write_text(text, encoding="utf-8")
    if text:
        print(text)

    if return_code != 0:
        raise RuntimeError(f"GZDoom {phase} phase failed with exit code {return_code}; see {phase_log}")
    for marker in ERROR_MARKERS:
        if marker in text:
            raise RuntimeError(f"GZDoom {phase} phase reported {marker!r}; see {phase_log}")
    return text


def require_inventory(text: str, where: str) -> None:
    if not FUSE_RE.search(text):
        raise RuntimeError(f"{where} inventory did not contain CheckoutFuse 2/3.")
    if not MEMO_RE.search(text):
        raise RuntimeError(f"{where} inventory did not contain CorporateMemo 1/3.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gzdoom", type=Path, required=True)
    parser.add_argument("--iwad", type=Path, required=True)
    args = parser.parse_args()

    executable = args.gzdoom.resolve()
    iwad = args.iwad.resolve()
    for required in (executable, iwad):
        if not required.exists():
            raise RuntimeError(f"Save/load prerequisite is missing: {required}")

    build = subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=ROOT, check=False)
    if build.returncode != 0 or not PK3.exists():
        raise RuntimeError("Prototype build failed before save/load validation.")

    if ROUNDTRIP.exists():
        shutil.rmtree(ROUNDTRIP)
    SAVE_DIR.mkdir(parents=True)
    INI_PATH.write_text(
        "[GlobalSettings]\n"
        "i_pauseinbackground=false\n"
        "vid_fullscreen=false\n"
        "vid_preferbackend=0\n"
        "queryiwad=false\n",
        encoding="ascii",
    )

    save_commands = (
        'map MAP01; wait 105; sv_cheats 1; give CheckoutFuse 2; '
        'give CorporateMemo 1; wait 8; printinv; '
        'save coh_ci_roundtrip "COH CI roundtrip"; wait 70; quit'
    )
    save_text = run_phase(executable, iwad, save_commands, "save")
    require_inventory(save_text, "Pre-save")

    save_files = list(SAVE_DIR.rglob("coh_ci_roundtrip.zds"))
    if len(save_files) != 1:
        raise RuntimeError(f"Expected exactly one coh_ci_roundtrip.zds save, found {len(save_files)}.")
    if save_files[0].stat().st_size < 4096:
        raise RuntimeError(f"Roundtrip save looks unexpectedly small: {save_files[0].stat().st_size} bytes.")

    load_commands = "load coh_ci_roundtrip; wait 105; printinv; wait 8; quit"
    load_text = run_phase(executable, iwad, load_commands, "load")
    require_inventory(load_text, "Loaded")

    print("GZDoom save/load roundtrip: PASS")
    print(f"Verified save: {save_files[0]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"GZDoom save/load roundtrip: FAIL — {exc}", file=sys.stderr)
        raise SystemExit(1)
