from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_SCRIPT = ROOT / "tools" / "gzdoom_save_load_roundtrip.ps1"
LINUX_SCRIPT = ROOT / "tools" / "gzdoom_save_load_roundtrip.sh"
LINUX_BOOTSTRAP = ROOT / "tools" / "bootstrap_linux_ci_runtime.py"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
README = ROOT / "README.md"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def main() -> None:
    windows_script = WINDOWS_SCRIPT.read_text(encoding="utf-8")
    linux_script = LINUX_SCRIPT.read_text(encoding="utf-8")
    linux_bootstrap = LINUX_BOOTSTRAP.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    for script_name, script in (("Windows", windows_script), ("Linux", linux_script)):
        for needle, label in (
            ("-savedir", "isolated save directory"),
            ("-loadgame", "real load-game invocation"),
            ("save coh-ci-roundtrip", "real save command"),
            ("map MAP01", "Closing Time runtime target"),
            ("CheckoutFuse", "custom objective inventory state"),
            ("CorporateMemo", "custom optional-route inventory state"),
            ("COH_SAVE_ROUNDTRIP_CREATE_DONE", "create completion sentinel"),
            ("COH_SAVE_ROUNDTRIP_LOAD_DONE", "load completion sentinel"),
            ("*.zds", "save-file discovery"),
        ):
            require(script, needle, f"{script_name} {label}")

    require(windows_script, "bootstrap_runtime.ps1", "Windows official runtime bootstrap")
    require(windows_script, '"-skill", "2"', "Windows default Graveyard Shift runtime skill")
    require(windows_script, "WaitForExit", "Windows bounded runtime wait")
    require(windows_script, "0x50", "Windows ZIP save-header validation")
    require(windows_script, "0x4B", "Windows ZIP save-header validation")

    require(linux_script, "bootstrap_linux_ci_runtime.py", "Linux official runtime bootstrap")
    require(linux_script, "-skill 2", "Linux default Graveyard Shift runtime skill")
    require(linux_script, "timeout --signal=KILL", "Linux bounded runtime wait")
    require(linux_script, "+vid_preferbackend 0", "headless OpenGL selection")
    require(linux_script, "xvfb-run", "headless display wrapper")
    require(linux_script, 'b"PK"', "Linux ZIP save-header validation")

    for needle, label in (
        ("api.github.com/repos/", "official GitHub Release API"),
        ("browser_download_url", "official release download URL"),
        ("runtime-lock.json", "pinned version source"),
        ("gzdoom_", "official GZDoom Linux package matcher"),
        ("freedoom2.wad", "Freedoom IWAD extraction"),
        ("SHA-256", "official Freedoom checksum verification"),
    ):
        require(linux_bootstrap, needle, label)

    require(workflow, "runtime-save-load:", "dedicated save/load CI job")
    require(workflow, "bootstrap_linux_ci_runtime.py", "official Linux runtime resolution in CI")
    require(workflow, "gzdoom_save_load_roundtrip.sh", "headless GZDoom save/load CI execution")
    require(workflow, "gzdoom-save-load-logs", "save/load CI log artifact")
    require(readme, "gzdoom_save_load_roundtrip.ps1", "documented Windows developer command")
    require(readme, "save/load", "documented save/load validation")

    forbidden = (
        "mediafire.com",
        "mega.nz",
        "drive.google.com",
        "dropbox.com",
    )
    combined = "\n".join((windows_script, linux_script, linux_bootstrap)).lower()
    for host in forbidden:
        if host in combined:
            raise AssertionError(f"Save/load harness must not depend on unofficial mirror: {host}")

    print("Save/load runtime contract: PASS")


if __name__ == "__main__":
    main()
