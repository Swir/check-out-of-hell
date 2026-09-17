#!/usr/bin/env python3
"""Exercise a real process-to-process GZDoom save/load roundtrip under X11."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
ROUNDTRIP = ROOT / "dist" / "save-load-roundtrip"
SAVE_DIR = ROUNDTRIP / "saves"
INI_PATH = ROUNDTRIP / "gzdoom-ci.ini"
PHASE_TIMEOUT_SECONDS = 45
WINDOW_TIMEOUT_SECONDS = 15

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


def _run_xdotool(xdotool: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(xdotool), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
        env=os.environ.copy(),
    )


def wait_for_window(xdotool: Path, process: subprocess.Popen[object]) -> str:
    deadline = time.monotonic() + WINDOW_TIMEOUT_SECONDS
    last_output = ""
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"GZDoom exited before its X11 window appeared (exit {process.returncode}).")
        found = _run_xdotool(xdotool, "search", "--pid", str(process.pid), check=False)
        last_output = found.stdout or ""
        windows = [line.strip() for line in last_output.splitlines() if line.strip().isdigit()]
        if windows:
            return windows[-1]
        time.sleep(0.20)
    raise RuntimeError(f"Timed out waiting for the GZDoom X11 window; xdotool output: {last_output!r}")


def send_console_command(xdotool: Path, window_id: str, command: str) -> None:
    # The live engine must already own a window before we inject anything. This avoids
    # the startup-order ambiguity of +exec and verifies the same console path a player uses.
    _run_xdotool(xdotool, "windowfocus", "--sync", window_id)
    _run_xdotool(xdotool, "key", "--window", window_id, "--clearmodifiers", "grave")
    time.sleep(0.25)
    _run_xdotool(xdotool, "type", "--window", window_id, "--clearmodifiers", "--delay", "1", command)
    _run_xdotool(xdotool, "key", "--window", window_id, "--clearmodifiers", "Return")


def run_phase(executable: Path, iwad: Path, xdotool: Path, command: str, phase: str) -> str:
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
        "+set",
        "i_pauseinbackground",
        "0",
        # This isolated CI process needs cheats only to seed deterministic inventory.
        "+set",
        "sv_cheats",
        "1",
    ]

    print(f"Running GZDoom {phase} phase...")
    with phase_log.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            argv,
            cwd=ROOT,
            text=True,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
        try:
            window_id = wait_for_window(xdotool, process)
            time.sleep(0.75)
            send_console_command(xdotool, window_id, command)
            return_code = process.wait(timeout=PHASE_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait(timeout=5)
            raise RuntimeError(
                f"GZDoom {phase} phase timed out after {PHASE_TIMEOUT_SECONDS}s; see {phase_log}"
            ) from exc
        except Exception:
            process.kill()
            process.wait(timeout=5)
            raise

    text = phase_log.read_text(encoding="utf-8", errors="replace")
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
    parser.add_argument("--xdotool", type=Path, required=True)
    args = parser.parse_args()

    executable = args.gzdoom.resolve()
    iwad = args.iwad.resolve()
    xdotool = args.xdotool.resolve()
    for required in (executable, iwad, xdotool):
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

    # This command is injected only after a real GZDoom window exists. `map` therefore
    # runs in a fully initialized engine; waits keep subsequent commands behind player spawn.
    save_command = (
        'map MAP01; wait 105; god; notarget; give CheckoutFuse 2; '
        'give CorporateMemo 1; wait 8; printinv; '
        'save coh_ci_roundtrip "COH CI roundtrip"; wait 20; quit'
    )
    save_text = run_phase(executable, iwad, xdotool, save_command, "save")
    require_inventory(save_text, "Pre-save")

    save_files = list(SAVE_DIR.rglob("coh_ci_roundtrip.zds"))
    if len(save_files) != 1:
        raise RuntimeError(f"Expected exactly one coh_ci_roundtrip.zds save, found {len(save_files)}.")
    if save_files[0].stat().st_size < 4096:
        raise RuntimeError(f"Roundtrip save looks unexpectedly small: {save_files[0].stat().st_size} bytes.")

    load_command = "load coh_ci_roundtrip; wait 105; printinv; wait 8; quit"
    load_text = run_phase(executable, iwad, xdotool, load_command, "load")
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
