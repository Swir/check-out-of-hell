from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

cvarinfo = (GAME / "CVARINFO").read_text(encoding="utf-8")
menudef = (GAME / "MENUDEF").read_text(encoding="utf-8")
mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
access = (GAME / "ZSCRIPT_ACCESSIBILITY").read_text(encoding="utf-8")
environment = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")

for marker in (
    "user bool coh_access_focus_hud = false;",
    "user bool coh_access_large_warnings = false;",
):
    if marker not in cvarinfo:
        raise SystemExit(f"Accessibility CVar missing: {marker}")

for marker in (
    "OptionMenu COHAccessibilityOptions",
    'Option "Focus HUD", "coh_access_focus_hud", "OnOff"',
    'Option "Large warnings", "coh_access_large_warnings", "OnOff"',
    "AddOptionMenu OptionsMenu",
    "AddOptionMenu OptionsMenuSimple",
):
    if marker not in menudef:
        raise SystemExit(f"Accessibility menu marker missing: {marker}")

handler_line = 'AddEventHandlers = "CheckoutShiftDirector", "CheckoutAccessibilityHandler"'
if handler_line not in mapinfo:
    raise SystemExit("Accessibility handler must be registered without replacing CheckoutShiftDirector")

for marker in (
    "class CheckoutAccessibilityHandler : EventHandler",
    "static ui bool GetPlayerOption(Name optionName)",
    "CVar.GetCVar(optionName, players[consoleplayer])",
    "ACCESSIBILITY FOCUS",
    "CRITICAL HEALTH",
    "HELL RUSH // MAXIMUM OVERTIME",
    "OVERTIME ACTIVE",
    "CheckoutShiftDirector.GetDepartmentObjectiveText",
    "CheckoutShiftDirector.GetPressureMeter",
    'CountInv("WarehouseDepartmentToken")',
    'CountInv("WarehouseLiftOverride")',
    '"POWER %d/3  //  LIFT %s"',
    'CountInv("ElectronicsDepartmentToken")',
    'CountInv("ElectronicsRebootPending")',
    '"ELECTRONICS %d/3  //  MEMOS %d/3"',
    '"OBJECTIVE  RESTORE SHOWROOM CIRCUITS  %d/2"',
    '"OBJECTIVE  START STORE NETWORK REBOOT"',
    '"OBJECTIVE  HOLD STORE NETWORK REBOOT"',
    '"OBJECTIVE  RETURN TO ELECTRONICS ENTRY"',
):
    if marker not in access:
        raise SystemExit(f"Accessibility overlay marker missing: {marker}")

# Sensory-safety baseline: keep the haunted fluorescent effect but reject the previous
# two-tic flash cuts. The slow cycle is long enough to read as a failing fixture rather
# than a rapid strobe.
for marker in ("FLIT A 70 Bright", "FLIT B 12", "FLIT C 18 Bright", "FLIT D 12"):
    if marker not in environment:
        raise SystemExit(f"Reduced-flash fluorescent cadence missing: {marker}")
for forbidden in ("FLIT B 2", "FLIT D 2"):
    if forbidden in environment:
        raise SystemExit(f"Rapid fluorescent flash returned: {forbidden}")

for marker in (
    '"CVARINFO"',
    '"MENUDEF"',
    'GAME / "ZSCRIPT_ACCESSIBILITY"',
    'archive.writestr("ZSCRIPT", zscript_payload())',
):
    if marker not in build:
        raise SystemExit(f"Build pipeline does not package accessibility layer: {marker}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for required in ("CVARINFO", "MENUDEF", "MAPINFO", "ZSCRIPT", "DECORATE"):
        if required not in names:
            raise SystemExit(f"Built PK3 missing accessibility dependency: {required}")

    packed_cvars = archive.read("CVARINFO").decode("utf-8")
    packed_menu = archive.read("MENUDEF").decode("utf-8")
    packed_mapinfo = archive.read("MAPINFO").decode("utf-8")
    packed_zscript = archive.read("ZSCRIPT").decode("utf-8")
    packed_decorate = archive.read("DECORATE").decode("utf-8")

    for marker in ("coh_access_focus_hud", "coh_access_large_warnings"):
        if marker not in packed_cvars or marker not in packed_menu or marker not in packed_zscript:
            raise SystemExit(f"Packaged accessibility setting is incomplete: {marker}")
    if "CheckoutAccessibilityHandler" not in packed_mapinfo or "CheckoutAccessibilityHandler" not in packed_zscript:
        raise SystemExit("Packaged accessibility handler is not wired")
    for marker in (
        "CheckoutShiftDirector.GetDepartmentObjectiveText",
        'CountInv("WarehouseDepartmentToken")',
        'CountInv("WarehouseLiftOverride")',
        'CountInv("ElectronicsDepartmentToken")',
        'CountInv("ElectronicsRebootPending")',
        '"OBJECTIVE  HOLD STORE NETWORK REBOOT"',
    ):
        if marker not in packed_zscript:
            raise SystemExit(f"Packaged accessibility HUD lost department-aware objective support: {marker}")
    if "FLIT B 2" in packed_decorate or "FLIT D 2" in packed_decorate:
        raise SystemExit("Built PK3 still contains rapid fluorescent flash cadence")

print("Accessibility contract: PASS")
print("Optional focus HUD and large textual warnings are packaged, Warehouse/Electronics department-aware objectives are preserved, and the fluorescent effect uses a slower default cadence.")
