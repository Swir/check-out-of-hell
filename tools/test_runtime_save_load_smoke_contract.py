from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke.py"
BOOTSTRAP = ROOT / "tools" / "bootstrap_linux_ci_runtime.py"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing required runtime save/load contract marker: {needle!r}")


def main() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    for marker in (
        "xvfb-run",
        "LIBGL_ALWAYS_SOFTWARE",
        "MESA_LOADER_DRIVER_OVERRIDE",
        "i_pauseinbackground",
        "i_soundinbackground",
        "-nomusic",
        "TimeoutExpired",
        "partial GZDoom output",
        "-savedir",
        "give CheckoutFuse 2",
        "printinv",
        "SAVE_STEM",
        '"-loadgame", SAVE_STEM',
        "COH_RUNTIME_SAVE_WRITTEN",
        "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
        r"CheckoutFuse\s+#\d+\s+\(2/3\)",
        "save -> process exit -> load round-trip",
    ):
        require(script, marker, SCRIPT)

    for marker in (
        "api.github.com/repos/{repo}/releases/tags/{tag}",
        'lock["gzdoom"]',
        'lock["freedoom"]',
        "browser_download_url",
        "Freedoom SHA-256 verified",
        "freedoom2.wad",
    ):
        require(bootstrap, marker, BOOTSTRAP)

    for marker in (
        "runtime-save-load:",
        "bootstrap_linux_ci_runtime.py",
        "gzdoom_save_load_smoke.py",
        "gzdoom-save-load-smoke.log",
        "Save/load round-trip with pinned GZDoom",
    ):
        require(workflow, marker, WORKFLOW)

    print("Pinned GZDoom runtime save/load smoke contract: PASS")


if __name__ == "__main__":
    main()
