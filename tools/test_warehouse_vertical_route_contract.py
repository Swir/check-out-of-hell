from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

# The lift-to-boss handoff must remain readable: the authored MAP02 Regional Manager anchor now
# uses the Warehouse-specific arrival spawner, which gives the player a deterministic four-second
# visual/audio warning after the lift override before management materializes.
mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
warehouse_zscript = (GAME / "ZSCRIPT_WAREHOUSE").read_text(encoding="utf-8")
if '17104 = "WarehouseRegionalManagerArrivalSpawner"' not in mapinfo:
    raise SystemExit("Warehouse Regional Manager anchor is not registered to the warned arrival spawner")
if '17104 = "CheckoutRegionalManagerSpawner"' in mapinfo:
    raise SystemExit("Warehouse Regional Manager must not use the instant generic boss spawner")
for marker in (
    "class WarehouseRegionalManagerArrivalSpawner : Actor",
    "bool arrivalArmed;",
    "int arrivalTic;",
    'p.CountInv("WarehouseDepartmentToken") < 1',
    'p.CountInv("CheckoutFuse") < 3',
    'p.CountInv("WarehouseLiftOverride") < 1',
    'p.CountInv("SupervisorClearanceToken") > 0',
    "arrivalTic = Level.maptime + 35 * 4;",
    'Actor.Spawn("OvertimeWarningFlash", Pos);',
    'p.A_StartSound("coh/regionalphase", CHAN_AUTO);',
    'Actor.Spawn("TeleportFog", Pos);',
    'Actor manager = Actor.Spawn("RegionalManager", Pos);',
):
    if marker not in warehouse_zscript:
        raise SystemExit(f"Warehouse Regional Manager arrival pacing is incomplete: {marker}")

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
    r"x\s*=\s*(-?[0-9.]+);\s*y\s*=\s*(-?[0-9.]+);\s*height\s*=\s*([0-9.]+);\s*angle\s*=\s*0;\s*type\s*=\s*17138"
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
    r"x\s*=\s*(-?[0-9.]+);\s*y\s*=\s*(-?[0-9.]+);\s*height\s*=\s*([0-9.]+);\s*angle\s*=\s*0;\s*type\s*=\s*17158",
    map02,
)
if stash != [("-590.0", "190.0", "96.0")]:
    raise SystemExit(f"Warehouse high-route stash drifted: {stash!r}")

# The hidden Staff Room is a real same-sector room with two 80-unit doorway gaps. The catwalk passes
# through both gaps at x=-590, while one shootable stock pile seals only the floor-level south entrance.
vertex_pattern = re.compile(r"vertex\s*\{\s*x\s*=\s*(-?[0-9.]+);\s*y\s*=\s*(-?[0-9.]+);\s*\}")
vertices = {(float(x), float(y)) for x, y in vertex_pattern.findall(map02)}
required_staff_vertices = {
    (-640.0, 80.0), (-620.0, 80.0), (-540.0, 80.0), (-480.0, 80.0),
    (-480.0, 220.0), (-540.0, 220.0), (-620.0, 220.0), (-640.0, 220.0),
}
if not required_staff_vertices.issubset(vertices):
    raise SystemExit("Warehouse hidden Staff Room geometry drifted")

for marker in (
    "linedef { v1 = 7;  v2 = 8;  sidefront = 8;  sideback = 9;  blocking = true; }",
    "linedef { v1 = 9;  v2 = 10; sidefront = 10; sideback = 11; blocking = true; }",
    "linedef { v1 = 10; v2 = 11; sidefront = 12; sideback = 13; blocking = true; }",
    "linedef { v1 = 11; v2 = 12; sidefront = 14; sideback = 15; blocking = true; }",
    "linedef { v1 = 13; v2 = 14; sidefront = 16; sideback = 17; blocking = true; }",
):
    if marker not in map02:
        raise SystemExit(f"Warehouse hidden Staff Room wall/gap layout drifted: {marker}")

thing_pattern = re.compile(
    r"x\s*=\s*(-?[0-9.]+);\s*y\s*=\s*(-?[0-9.]+);(?:\s*height\s*=\s*[0-9.]+;)?\s*angle\s*=\s*[0-9]+;\s*type\s*=\s*([0-9]+)"
)
things = [(float(x), float(y), int(actor_type)) for x, y, actor_type in thing_pattern.findall(map02)]
if (-580.0, 80.0, 17136) not in things:
    raise SystemExit("Warehouse hidden Staff Room lost its shootable ground-level entrance")
if (-520.0, 140.0, 17131) not in things or (-520.0, 180.0, 17130) not in things:
    raise SystemExit("Warehouse hidden Staff Room lost its useful optional rewards")

# No mandatory power/lift/boss/safety actor may be moved onto the optional high route or into the room.
for mandatory_type in (17111, 17133, 17104, 17137):
    pattern = re.compile(
        rf"x\s*=\s*(-?[0-9.]+);\s*y\s*=\s*(-?[0-9.]+);(?:\s*height\s*=\s*[0-9.]+;)?\s*angle\s*=\s*[0-9]+;\s*type\s*=\s*{mandatory_type}"
    )
    for x_text, y_text in pattern.findall(map02):
        x = float(x_text)
        y = float(y_text)
        if x <= -550.0:
            raise SystemExit(f"Mandatory Warehouse type {mandatory_type} moved onto the optional catwalk")
        if -640.0 <= x <= -480.0 and 80.0 <= y <= 220.0:
            raise SystemExit(f"Mandatory Warehouse type {mandatory_type} moved into the hidden Staff Room")

# Existing route guarantees remain authoritative while the new routes add optional elevation/shortcut value.
for marker in (
    "x = 0.0; y = 280.0; angle = 270; type = 17133",
    "x = 0.0; y = 390.0; angle = 270; type = 17104",
    "x = -430.0; y = 250.0; angle = 0; type = 17137",
    "x = 0.0; y = -300.0; angle = 90; type = 17132",
):
    if marker not in map02:
        raise SystemExit(f"Warehouse core route moved while adding optional routes: {marker}")

with zipfile.ZipFile(PK3, "r") as archive:
    runtime_decorate = archive.read("DECORATE").decode("utf-8")
    runtime_zscript = archive.read("ZSCRIPT").decode("utf-8")
    runtime_mapinfo = archive.read("MAPINFO").decode("utf-8")
    runtime_map = archive.read("maps/MAP02.wad")
    for marker in (
        "actor WarehouseShelfBridge 17138",
        "+ACTLIKEBRIDGE",
        "actor WarehouseOverstockStash : Backpack 17158",
        'Tag "Unlogged Overstock Stash"',
    ):
        if marker not in runtime_decorate:
            raise SystemExit(f"Packaged DECORATE lost Warehouse high-route marker: {marker}")
    for marker in (
        "class WarehouseRegionalManagerArrivalSpawner : Actor",
        "arrivalTic = Level.maptime + 35 * 4;",
        'Actor manager = Actor.Spawn("RegionalManager", Pos);',
    ):
        if marker not in runtime_zscript:
            raise SystemExit(f"Packaged ZSCRIPT lost Warehouse boss-arrival marker: {marker}")
    if '17104 = "WarehouseRegionalManagerArrivalSpawner"' not in runtime_mapinfo:
        raise SystemExit("Packaged MAPINFO lost the warned Warehouse Regional Manager registration")
    for marker in (
        b"type = 17138",
        b"type = 17158",
        b"x = -580.0; y =  80.0; angle = 0; type = 17136",
        b"x = -520.0; y = 140.0; angle = 0; type = 17131",
        b"x = -520.0; y = 180.0; angle = 0; type = 17130",
    ):
        if marker not in runtime_map:
            raise SystemExit(f"Packaged MAP02 lost Warehouse optional-route marker: {marker!r}")

print("Warehouse 13.5 vertical overstock + hidden Staff Room + Regional Manager handoff contract: PASS")
print("The optional west route and four-second warned boss arrival improve elevation, shortcuts and management pacing while mandatory lanes remain untouched.")
