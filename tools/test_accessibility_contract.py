from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

menu = (GAME / "MENUDEF").read_text(encoding="utf-8")
overtime = (GAME / "DECORATE_OVERTIME").read_text(encoding="utf-8")
docs = (ROOT / "docs" / "ACCESSIBILITY.md").read_text(encoding="utf-8")
build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")

required_menu_tokens = [
    'OptionMenu "COHAccessibilityMenu"',
    'ScaleSlider "UI scale", "uiscale"',
    'ScaleSlider "Notification text scale", "con_scaletext"',
    'Slider "Crosshair scale", "crosshairscale"',
    'Option "Center notifications", "con_centernotify", "OnOff"',
    'Option "Reduce pulsing notifications", "con_pulsetext", "OffOn"',
    'Option "Intermission subtitles", "inter_subtitles", "OnOff"',
    'AddOptionMenu "OptionsMenu"',
    'AddOptionMenu "OptionsMenuSimple"',
]
for token in required_menu_tokens:
    assert token in menu, f"Accessibility menu contract missing: {token}"

# The Overtime danger timing remains unchanged; only the rendering cadence is softened.
for token in (
    "TNT1 A 3150",
    "TNT1 A 1575",
    "TNT1 A 1120",
    "TNT1 A 910",
    "TNT1 A 700",
    'A_Explode(10, 72)',
    'A_PlaySound("coh/overtimealarm", CHAN_BODY)',
    'A_PlaySound("coh/overtimearc", CHAN_BODY)',
):
    assert token in overtime, f"Overtime accessibility pass changed gameplay contract: {token}"

bright_lines = [line for line in overtime.splitlines() if " Bright" in line]
assert len(bright_lines) == 2, f"Expected exactly two short Bright telegraph pulses, got {len(bright_lines)}"
assert all(" 3 Bright" in line for line in bright_lines), "Bright Overtime pulses must remain capped at 3 tics"

assert '"MENUDEF"' in build, "Build must package the accessibility MENUDEF lump"
assert "first accessibility pass" in docs.lower(), "Accessibility scope must be documented honestly"
assert "not a claim that every accessibility need is solved" in docs.lower(), "Documentation must retain scope limitation"

assert PK3.exists(), "Build the PK3 before running the accessibility contract"
with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    assert "MENUDEF" in names, "Built PK3 is missing MENUDEF"
    packaged_menu = archive.read("MENUDEF").decode("utf-8")
    assert 'OptionMenu "COHAccessibilityMenu"' in packaged_menu

print("Accessibility contract: OK")
