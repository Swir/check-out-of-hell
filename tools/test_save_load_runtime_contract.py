from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gzdoom_save_load_roundtrip.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
README = ROOT / "README.md"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def main() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    for needle, label in (
        ('bootstrap_runtime.ps1', "official runtime bootstrap"),
        ('-savedir', "isolated save directory"),
        ('-loadgame', "real load-game invocation"),
        ('save coh-ci-roundtrip', "real save command"),
        ('map MAP01', "Closing Time runtime target"),
        ('-skill", "2"', "default Graveyard Shift runtime skill"),
        ('CheckoutFuse', "custom objective inventory state"),
        ('CorporateMemo', "custom optional-route inventory state"),
        ('COH_SAVE_ROUNDTRIP_CREATE_DONE', "create completion sentinel"),
        ('COH_SAVE_ROUNDTRIP_LOAD_DONE', "load completion sentinel"),
        ('WaitForExit', "bounded runtime wait"),
        ('*.zds', "save-file discovery"),
        ('0x50', "ZIP save-header validation"),
        ('0x4B', "ZIP save-header validation"),
    ):
        require(script, needle, label)

    require(workflow, "gzdoom_save_load_roundtrip.ps1", "Windows save/load CI execution")
    require(workflow, "save-load-roundtrip", "save/load CI artifact/log path")
    require(readme, "gzdoom_save_load_roundtrip.ps1", "documented developer command")

    forbidden = (
        "mediafire.com",
        "mega.nz",
        "drive.google.com",
        "dropbox.com",
    )
    lowered = script.lower()
    for host in forbidden:
        if host in lowered:
            raise AssertionError(f"Save/load harness must not depend on unofficial mirror: {host}")

    print("Save/load runtime contract: PASS")


if __name__ == "__main__":
    main()
