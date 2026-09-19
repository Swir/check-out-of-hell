from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

decorate = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
for marker in (
    "actor WarehouseShelfBridge 17138",
    'Tag "Staff-Only Overstock Catwalk"',
    "Radius 40",
    "Height 16",
    "+SOLID",
    "+NOGRAVITY",
    "+NOLIFTDROP",
    "+ACTLIKEBRIDGE",
    "actor WarehouseOverstockStash : Backpack 17158",
    'Tag "Unlogged Overstock Stash"',
    'Inventory.PickupMessage "Unlogged overstock found. Inventory insists this shelf does not exist."',
    "BOXE A -1 Bright",
):
    if marker not in decorate:
        raise SystemExit(f"Warehouse vertical-route presentation is incomplete: {marker}")

map02 = (GAME / "MAP02.udmf").read_text(encoding="utf-8")
bridge_pattern = re.compile(
    r"x = (-?[0-9.]+); y = (-?[0-9.]+); height = ([0-9.]+);\s+angle = 0; type = 17138"
)
bridges = [(float(x), float(y), float(z)) for x, y, z in bridge_pattern.findall(map02)]
expected = [
    (-590.0, -300.0, 0.0),
    (-590.0, -240.0, 16.0),
    (-590.0, -180.0, 32.0),
    (-590.0, -120.0, 48.0),
    (-590.0, -60.0, 64.0),
    (-590.0, 0.0, 80.0),
    (-590.0, 60.0, 80.0),
    (-590.0, 120.0, 80.0),
    (-590.0, 180.0, 80.0),
    (-590.0, 240.0, 80.0),
]
if bridges != expected:
    raise SystemExit(f"Warehouse overstock catwalk drifted: {bridges!r}")

# The first platform top is a normal Doom-height step, each rising segment adds only 16 units,
# and 60-unit center spacing with Radius 40 leaves overlapping walkable tops instead of jump gaps.
if bridges[0][2] + 16.0 > 24.0:
    raise SystemExit("Warehouse catwalk first step became too tall for normal traversal")
for left, right in zip(bridges, bridges[1:]):
    if right[2] - left[2] > 16.0:
        raise SystemExit("Warehouse catwalk contains an unintended vertical jump")
    if abs(right[1] - left[1]) > 80.0:
        raise SystemExit("Warehouse catwalk contains an unintended horizontal gap")

# Keep the route on the far west shelf wall: it must not overlap the x=+-300 moving-pallet lanes,
# the x=-180..180 permanent center corridor, or the rear lift / Regional Manager centerline.
if any(x > -550.0 for x, _y, _z in bridges):
    raise SystemExit("Warehouse catwalk left the far-west optional route")
if max(z + 16.0 for _x, _y, z in bridges) > 96.0:
    raise SystemExit("Warehouse catwalk exceeds the authored 96-unit top height")

stash = re.findall(
    r"x = (-?[0-9.]+); y = (-?[0-9.]+); height = ([0-9.]+); angle = 0; type = 17158",
    map02,
)
if stash != [("-590.0", "190.0", "96.0")]:
    raise SystemExit(f"Warehouse high-route stash drifted: {stash!r}")

# No mandatory power/lift/boss/safety actor may be moved onto the optional high route.
for mandatory_type in (17111, 17133, 17104, 17137):
    pattern = re.compile(
        rf"x = (-?[0-9.]+); y = (-?[0-9.]+);(?: height = [0-9.]+;)? angle = [0-9]+; type = {mandatory_type}"
    )
    for x_text, _y_text in pattern.findall(map02):
        if float(x_text) <= -550.0:
            raise SystemExit(f"Mandatory Warehouse type {mandatory_type} moved onto the optional catwalk")

# Existing route guarantees remain authoritative while the new route adds optional elevation.
for marker in (
    "x = 0.0; y = 280.0; angle = 270; type = 17133",
    "x = 0.0; y = 390.0; angle = 270; type = 17104",
    "x = -430.0; y = 250.0; angle = 0; type = 17137",
    "x = 0.0; y = -300.0; angle = 90; type = 17132",
):
    if marker not in map02:
        raise SystemExit(f"Warehouse core route moved while adding optional elevation: {marker}")

with zipfile.ZipFile(PK3, "r") as archive:
    runtime_decorate = archive.read("DECORATE").decode("utf-8")
    runtime_map = archive.read("maps/MAP02.wad")
    for marker in (
        "actor WarehouseShelfBridge 17138",
        "+ACTLIKEBRIDGE",
        "actor WarehouseOverstockStash : Backpack 17158",
        'Tag "Unlogged Overstock Stash"',
    ):
        if marker not in runtime_decorate:
            raise SystemExit(f"Packaged DECORATE lost Warehouse high-route marker: {marker}")
    for marker in (b"type = 17138", b"type = 17158"):
        if marker not in runtime_map:
            raise SystemExit(f"Packaged MAP02 lost Warehouse high-route marker: {marker!r}")

print("Warehouse 13.5 vertical overstock route contract: PASS")
print("Ten fixed west-wall bridge stacks create an optional elevated shortcut with a project-owned ammo stash while mandatory lanes remain untouched.")
