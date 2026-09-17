#!/usr/bin/env python3
"""Real two-process GZDoom save/load smoke test for headless Linux CI.

Runs under Xvfb with Mesa software rendering. The test authors unmistakable MAP01
objective state, creates a real GZDoom save, ends that engine process, launches a
second engine process with -loadgame, then proves the serialized state survived.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GZDOOM = shutil.which("gzdoom")
FREEDOOM = ROOT / "external" / "linux" / "freedoom2.wad"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
WORK = ROOT / "dist" / "save-load-runtime-linux"
SAVES = WORK / "saves"
CONFIG = WORK / "gzdoom-ci.ini"
SAVE_CFG = WORK / "save-roundtrip.cfg"
LOAD_CFG = WORK / "load-roundtrip.cfg"
SAVE_ENGINE = WORK / "save.engine.log"
LOAD_ENGINE = WORK / "load.engine.log"
SAVE_STDOUT = WORK / "save.stdout.log"
SAVE_STDERR = WORK / "save.stderr.log"
LOAD_STDOUT = WORK / "load.stdout.log"
LOAD_STDERR = WORK / "load.stderr.log"
COMBINED = ROOT / "dist" / "gzdoom-save-load-linux-smoke.log"
SAVE_STEM = "coh-ci-roundtrip-linux"
TIMEOUT = 55.0

ERROR_PATTERNS = (
    "Script error",
    "Execution could not continue",
    "Unknown class",
    "Unknown identifier",
    "Invalid parameter",
    "Parse error",
    "Unknown command",
    "Cannot load savegame",
    "Savegame is from a different",
    "Could not open savegame",
    "Cannot find savegame",
    "No map MAP01",
    "Not in a saveable game",
    "Player is dead in a single-player game",
    "DIED WITH FATAL ERROR",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError):
        return ""


def assert_no_runtime_errors(text: str, label: str) -> None:
    for pattern in ERROR_PATTERNS:
        if pattern.lower() in text.lower():
            raise RuntimeError(f"{label} reported {pattern!r}.")


def combined_phase_text(engine: Path, stdout: Path, stderr: Path) -> str:
    return "\n".join((read_text(engine), read_text(stdout), read_text(stderr)))


def stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def run_phase(
    label: str,
    arguments: list[str],
    engine_log: Path,
    stdout_log: Path,
    stderr_log: Path,
    sentinel: str,
) -> str:
    for path in (engine_log, stdout_log, stderr_log):
        path.unlink(missing_ok=True)

    env = os.environ.copy()
    env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    env.setdefault("MESA_LOADER_DRIVER_OVERRIDE", "llvmpipe")

    with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        process = subprocess.Popen(
            [GZDOOM, *arguments, "+logfile", str(engine_log)],
            cwd=ROOT,
            env=env,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
        )
        deadline = time.monotonic() + TIMEOUT
        try:
            while time.monotonic() < deadline:
                text = combined_phase_text(engine_log, stdout_log, stderr_log)
                assert_no_runtime_errors(text, label)
                if sentinel in text:
                    return text
                return_code = process.poll()
                if return_code is not None:
                    raise RuntimeError(
                        f"{label} exited before sentinel {sentinel!r} "
                        f"(exit code {return_code})."
                    )
                time.sleep(0.25)
            raise RuntimeError(f"{label} timed out after {TIMEOUT:.0f}s before {sentinel!r}.")
        finally:
            stop_process(process)


def write_combined(save_text: str, load_text: str, result: str) -> None:
    COMBINED.write_text(
        "\n".join(
            (
                "CHECKOUT OF HELL - pinned GZDoom Linux save/load runtime smoke",
                "",
                "=== SAVE PASS ===",
                save_text,
                "",
                "=== LOAD PASS ===",
                load_text,
                "",
                result,
                "",
            )
        ),
        encoding="utf-8",
    )


def assert_objective_state(text: str, label: str) -> None:
    checks = (
        (r"CheckoutFuse\s+#\d+\s+\(2/3\)", "CheckoutFuse 2/3"),
        (r"CorporateMemo\s+#\d+\s+\(2/3\)", "CorporateMemo 2/3"),
    )
    for pattern, description in checks:
        if not re.search(pattern, text):
            raise RuntimeError(f"{label} did not expose {description}.")


def main() -> int:
    if not GZDOOM:
        raise RuntimeError("gzdoom is not installed or not on PATH.")
    for required in (FREEDOOM, PK3):
        if not required.is_file():
            raise RuntimeError(f"Runtime save/load prerequisite is missing: {required}")

    if WORK.exists():
        shutil.rmtree(WORK)
    SAVES.mkdir(parents=True)

    CONFIG.write_text(
        "\n".join(
            (
                "[GlobalSettings]",
                "vid_preferbackend=0",
                "vid_fullscreen=false",
                "vid_lowerinbackground=false",
                "vid_activeinbackground=true",
                "i_pauseinbackground=false",
                "i_soundinbackground=false",
                "",
            )
        ),
        encoding="ascii",
    )

    # MAP01 now has a canonical embedded UDMF marker, so start directly into the
    # level with +map. This guarantees that queued give/god cheats are authored in
    # the live playsim rather than being discarded by a deferred map transition.
    SAVE_CFG.write_text(
        'wait 10; god; give CheckoutFuse; give CheckoutFuse; give CorporateMemo; '
        'give CorporateMemo; wait 10; printinv; '
        'save coh-ci-roundtrip-linux "CHECKOUT OF HELL CI ROUNDTRIP"; '
        'wait 20; echo COH_LINUX_RUNTIME_SAVE_WRITTEN\n',
        encoding="ascii",
    )
    LOAD_CFG.write_text(
        "wait 10; printinv; echo COH_LINUX_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE\n",
        encoding="ascii",
    )

    common = [
        "-stdout",
        "-nosound",
        "-config",
        str(CONFIG),
        "-iwad",
        str(FREEDOOM),
        "-file",
        str(PK3),
        "-savedir",
        str(SAVES),
    ]

    save_text = ""
    load_text = ""
    try:
        print("Runtime pass 1/2: write a real GZDoom save with objective state...")
        save_text = run_phase(
            "GZDoom Linux save pass",
            [*common, "+map", "MAP01", "+exec", str(SAVE_CFG)],
            SAVE_ENGINE,
            SAVE_STDOUT,
            SAVE_STDERR,
            "COH_LINUX_RUNTIME_SAVE_WRITTEN",
        )
        assert_objective_state(save_text, "Pre-save inventory")

        saves = sorted(SAVES.glob(f"{SAVE_STEM}*.zds"))
        if not saves:
            raise RuntimeError(f"GZDoom did not create a {SAVE_STEM} savegame in {SAVES}.")
        save_file = saves[0]
        if save_file.stat().st_size < 4096:
            raise RuntimeError(
                f"GZDoom savegame is unexpectedly small ({save_file.stat().st_size} bytes)."
            )
        first_size = save_file.stat().st_size
        time.sleep(0.5)
        if save_file.stat().st_size != first_size:
            time.sleep(0.5)
        if save_file.stat().st_size < 4096:
            raise RuntimeError("GZDoom savegame became invalid after the first process exited.")

        print("Runtime pass 2/2: launch a new process and restore the save...")
        load_text = run_phase(
            "GZDoom Linux load pass",
            [*common, "-loadgame", str(save_file.resolve()), "+exec", str(LOAD_CFG)],
            LOAD_ENGINE,
            LOAD_STDOUT,
            LOAD_STDERR,
            "COH_LINUX_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
        )
        assert_objective_state(load_text, "Post-load inventory")

        result = (
            "PASS: CheckoutFuse 2/3 and CorporateMemo 2/3 survived a real "
            "GZDoom save -> process exit -> load round-trip."
        )
        write_combined(save_text, load_text, result)
        print("GZDoom Linux runtime save/load round-trip: PASS")
        return 0
    except Exception as exc:
        save_text = save_text or combined_phase_text(SAVE_ENGINE, SAVE_STDOUT, SAVE_STDERR)
        load_text = load_text or combined_phase_text(LOAD_ENGINE, LOAD_STDOUT, LOAD_STDERR)
        write_combined(save_text, load_text, f"FAIL: {exc}")
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
