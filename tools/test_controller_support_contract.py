from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

menudef = (GAME / "MENUDEF").read_text(encoding="utf-8")
sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
decorate = (GAME / "DECORATE").read_text(encoding="utf-8")
docs = (ROOT / "docs" / "CONTROLLER.md").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")

menu_markers = (
    "OptionMenu COHControllerOptions",
    'Title "CHECKOUT OF HELL Controller"',
    'Control "Primary fire", "+attack"',
    'Control "Alternate fire", "+altattack"',
    'Control "Use / interact", "+use"',
    'Control "Jump", "+jump"',
    'Control "Crouch", "+crouch"',
    'Control "Run / sprint", "+speed"',
    'Control "Previous weapon", "weapprev"',
    'Control "Next weapon", "weapnext"',
    'Control "Automap", "togglemap"',
    'Submenu "Device / stick setup", "JoystickOptions"',
    'Submenu "Full control bindings", "CustomizeControls"',
)
for marker in menu_markers:
    if marker not in menudef:
        raise SystemExit(f"Controller menu marker missing: {marker}")

submenu_line = 'Submenu "CHECKOUT OF HELL Controller", "COHControllerOptions"'
if menudef.count(submenu_line) != 2:
    raise SystemExit("Controller submenu must be reachable from both full and simple GZDoom options menus")

# The controller pass must remain binding-friendly: expose standard GZDoom actions instead of
# hard-coding physical pad buttons or overwriting a player's existing configuration.
for forbidden in ("defaultbind", "pad_a ", "rtrigger ", "ltrigger "):
    if forbidden.lower() in menudef.lower():
        raise SystemExit(f"Controller menu must not force physical-button bindings: {forbidden}")

weapon_cues = {
    "Emergency Mop": ("coh/mopswing", "MEDIUM"),
    "Receipt Ripper": ("coh/ripperfire", "LIGHT"),
    "Price-Gun SMG": ("coh/pricefire", "SUBTLE"),
    "Turbo Can Launcher": ("coh/canlaunch", "HEAVY"),
}
for weapon, (cue, profile) in weapon_cues.items():
    rumble = f"$rumble {cue} {profile}"
    if rumble not in sndinfo:
        raise SystemExit(f"Signature weapon haptic mapping missing for {weapon}: {rumble}")
    if cue not in decorate:
        raise SystemExit(f"Signature weapon haptic cue is not used by gameplay: {cue}")

# Keep haptics restrained: enemies, alarms and ambient Overtime should never create constant pad rumble.
for forbidden_prefix in (
    "$rumble coh/checkout",
    "$rumble coh/scanner",
    "$rumble coh/cart",
    "$rumble coh/pallet",
    "$rumble coh/regional",
    "$rumble coh/manager",
    "$rumble coh/overtime",
    "$rumble coh/bossalarm",
):
    if forbidden_prefix in sndinfo:
        raise SystemExit(f"Noisy enemy/ambient rumble mapping detected: {forbidden_prefix}")

for marker in (
    "Existing player bindings are never overwritten",
    "Right trigger / R2",
    "Left stick",
    "real-controller playtest",
    "GZDoom `g4.14.2`",
):
    if marker not in docs:
        raise SystemExit(f"Controller documentation marker missing: {marker}")

if "python tools/test_controller_support_contract.py" not in workflow:
    raise SystemExit("Controller support contract is not wired into GitHub Actions")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for required in ("MENUDEF", "SNDINFO", "DECORATE"):
        if required not in names:
            raise SystemExit(f"Built PK3 missing controller-support dependency: {required}")

    packed_menu = archive.read("MENUDEF").decode("utf-8")
    packed_sndinfo = archive.read("SNDINFO").decode("utf-8")
    packed_decorate = archive.read("DECORATE").decode("utf-8")

    for marker in menu_markers:
        if marker not in packed_menu:
            raise SystemExit(f"Packaged controller menu marker missing: {marker}")
    for weapon, (cue, profile) in weapon_cues.items():
        if f"$rumble {cue} {profile}" not in packed_sndinfo or cue not in packed_decorate:
            raise SystemExit(f"Packaged controller haptics incomplete for {weapon}")

print("Controller support contract: PASS")
print("Core GZDoom actions are remappable without forced pad bindings, signature weapons use restrained haptics, and the packaged PK3 carries the controller layer.")
