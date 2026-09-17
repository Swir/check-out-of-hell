from pathlib import Path
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
    runtime_script = (TOOLS / "gzdoom_save_load_smoke.ps1").read_text(encoding="utf-8")

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

    require(runtime_script, 'give CheckoutFuse 2', "gzdoom_save_load_smoke.ps1")
    require(runtime_script, 'give CorporateMemo 1', "gzdoom_save_load_smoke.ps1")
    require(runtime_script, 'save coh-save-load-ci', "gzdoom_save_load_smoke.ps1")
    require(runtime_script, 'load coh-save-load-ci', "gzdoom_save_load_smoke.ps1")
    require(runtime_script, 'printinv', "gzdoom_save_load_smoke.ps1")
    require(runtime_script, 'CheckoutFuse', "gzdoom_save_load_smoke.ps1")
    require(runtime_script, 'CorporateMemo', "gzdoom_save_load_smoke.ps1")

    require(workflow, "Save/load persistence contract test", "build.yml")
    require(workflow, "Save/load current prototype with pinned GZDoom", "build.yml")
    require(workflow, ".\\tools\\gzdoom_save_load_smoke.ps1", "build.yml")

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
