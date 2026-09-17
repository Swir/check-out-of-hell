from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gzdoom_save_load_smoke.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing required runtime save/load contract marker: {needle!r}")


def main() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    for marker in (
        "bootstrap_runtime.ps1",
        "-savedir",
        "give CheckoutFuse 2",
        "printinv",
        "save $SaveStem",
        '"-loadgame", $SaveStem',
        "COH_RUNTIME_SAVE_WRITTEN",
        "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE",
        r"CheckoutFuse\s+#\d+\s+\(2/3\)",
        "save -> quit -> load round-trip",
    ):
        require(script, marker, SCRIPT)

    require(workflow, "gzdoom_save_load_smoke.ps1", WORKFLOW)
    require(workflow, "gzdoom-save-load-smoke.log", WORKFLOW)

    print("Pinned GZDoom runtime save/load smoke contract: PASS")


if __name__ == "__main__":
    main()
