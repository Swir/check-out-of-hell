from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
TOOLS = ROOT / "tools"
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"


def require(text: str, needle: str, context: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {needle!r} in {context}")


def main() -> None:
    extension = (GAME / "ZSCRIPT_SAVELOAD").read_text(encoding="utf-8")
    mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
    build = (TOOLS / "build.py").read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    runtime_script = (TOOLS / "gzdoom_save_load_smoke_linux.sh").read_text(encoding="utf-8")
    windows_runtime_script = (TOOLS / "gzdoom_save_load_smoke.ps1").read_text(encoding="utf-8")
    linux_bootstrap = (TOOLS / "bootstrap_runtime_linux.py").read_text(encoding="utf-8")
    inspector = (TOOLS / "inspect_gzdoom_save.py").read_text(encoding="utf-8")
    runtime_lock = json.loads((ROOT / "runtime-lock.json").read_text(encoding="utf-8"))

    require(extension, "class CheckoutPersistentShiftDirector : CheckoutShiftDirector", "ZSCRIPT_SAVELOAD")
    require(extension, "override void WorldLoaded(WorldEvent e)", "ZSCRIPT_SAVELOAD")
    require(extension, "if (e.IsSaveGame)", "ZSCRIPT_SAVELOAD")
    require(extension, "Super.WorldLoaded(e);", "ZSCRIPT_SAVELOAD")

    require(mapinfo, 'AddEventHandlers = "CheckoutPersistentShiftDirector"', "MAPINFO")
    if 'AddEventHandlers = "CheckoutShiftDirector"' in mapinfo:
        raise AssertionError("MAPINFO still registers the reset-prone base event handler directly")

    require(build, "def zscript_payload()", "tools/build.py")
    require(build, 'GAME / "ZSCRIPT_SAVELOAD"', "tools/build.py")
    require(build, 'archive.writestr("ZSCRIPT", zscript_payload())', "tools/build.py")

    require(runtime_script, "give CheckoutFuse 2", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "give CorporateMemo 1", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "save coh-save-load-ci", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "-loadgame coh-save-load-ci", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "save coh-save-load-ci-roundtrip", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "LIBGL_ALWAYS_SOFTWARE=1", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "xvfb-run", "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, 'run_scenario create-save "$CREATE_CFG" +warp MAP01', "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, '-exec "$cfg"', "gzdoom_save_load_smoke_linux.sh")
    require(runtime_script, "inspect_gzdoom_save.py", "gzdoom_save_load_smoke_linux.sh")
    if 'run_scenario create-save "$CREATE_CFG" +map MAP01' in runtime_script:
        raise AssertionError("Linux save/load smoke regressed to +map; GZDoom needs startup +warp to autostart in hosted CI")

    require(windows_runtime_script, '@("+warp", "MAP01")', "gzdoom_save_load_smoke.ps1")
    require(windows_runtime_script, '"-exec", $ConfigPath', "gzdoom_save_load_smoke.ps1")
    if '@("+map", "MAP01")' in windows_runtime_script:
        raise AssertionError("Windows save/load smoke regressed to startup +map instead of +warp")

    require(linux_bootstrap, 'runtime-lock.json', "bootstrap_runtime_linux.py")
    require(linux_bootstrap, 'browser_download_url', "bootstrap_runtime_linux.py")
    require(linux_bootstrap, 'Freedoom SHA-256 verified.', "bootstrap_runtime_linux.py")
    require(linux_bootstrap, 'linux_asset_regex', "bootstrap_runtime_linux.py")
    if "linux_asset_regex" not in runtime_lock["gzdoom"]:
        raise AssertionError("runtime-lock.json does not pin an official Linux GZDoom asset")

    require(inspector, "zipfile.is_zipfile", "inspect_gzdoom_save.py")
    require(inspector, 'endswith(".json")', "inspect_gzdoom_save.py")
    require(inspector, "json.loads(text)", "inspect_gzdoom_save.py")

    require(workflow, "Save/load persistence contract test", "build.yml")
    require(workflow, "save-load-runtime:", "build.yml")
    require(workflow, "Resolve pinned official Linux runtime assets", "build.yml")
    require(workflow, "Save/load current prototype with pinned GZDoom", "build.yml")
    require(workflow, "bash tools/gzdoom_save_load_smoke_linux.sh", "build.yml")

    if not PK3.exists():
        raise AssertionError("Built PK3 is missing; run tools/build.py before this contract")

    with zipfile.ZipFile(PK3) as archive:
        zscript = archive.read("ZSCRIPT").decode("utf-8")
        packaged_mapinfo = archive.read("MAPINFO").decode("utf-8")

    require(zscript, "class CheckoutPersistentShiftDirector", "packaged ZSCRIPT")
    require(zscript, "if (e.IsSaveGame)", "packaged ZSCRIPT")
    require(packaged_mapinfo, 'AddEventHandlers = "CheckoutPersistentShiftDirector"', "packaged MAPINFO")

    print("Save/load persistence contract: PASS")


if __name__ == "__main__":
    main()
