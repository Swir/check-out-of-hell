from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"


def png_chunks(data: bytes):
    cursor = 8
    while cursor + 12 <= len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        payload = data[cursor + 8 : cursor + 8 + length]
        yield kind, payload
        cursor += 12 + length


if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

for rel in ("sprites/WCTLA0.png", "sprites/WSGNA0.png"):
    path = GAME / rel
    if not path.exists():
        raise SystemExit(f"Warehouse generated sprite missing: {rel}")
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Warehouse generated PNG is invalid: {rel}")
    width, height = struct.unpack(">II", data[16:24])
    if width < 64 or height < 64:
        raise SystemExit(f"Warehouse generated sign is unexpectedly small: {rel} -> {width}x{height}")
    offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
    if len(offsets) != 1 or len(offsets[0]) != 8:
        raise SystemExit(f"Warehouse sprite is missing one valid ZDoom grAb chunk: {rel}")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_warehouse_assets import generate_warehouse_assets",
    "generate_warehouse_assets(GAME)",
):
    if marker not in build:
        raise SystemExit(f"Warehouse asset generator is not wired into the build: {marker}")

decorate_env = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
for marker in (
    "actor WarehouseDepartmentToken : Inventory",
    "actor WarehouseLiftOverride : Inventory",
    'Tag "Freight Lift Override"',
    "WCTL A -1 Bright",
    "actor WarehouseFreightSign 17134",
    "WSGN A -1",
):
    if marker not in decorate_env:
        raise SystemExit(f"Warehouse objective presentation is incomplete: {marker}")

mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
if '17133 = "WarehouseLiftControlSpawner"' not in mapinfo:
    raise SystemExit("Warehouse lift-control spawner DoomEdNum is missing")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
for marker in (
    'p.A_TakeInventory("WarehouseDepartmentToken", 1)',
    'p.A_TakeInventory("WarehouseLiftOverride", 1)',
    "class WarehouseLiftControlSpawner : Actor",
    'p.A_GiveInventory("WarehouseDepartmentToken", 1)',
    'Actor.Spawn("WarehouseLiftOverride", Pos)',
    'return "OBJECTIVE  ENGAGE FREIGHT LIFT OVERRIDE";',
    'return "OBJECTIVE  SURVIVE REGIONAL MANAGEMENT";',
    'return "ROUTE: POWERED LIFT CONTROL IS AT THE REAR BAY";',
):
    if marker not in zscript:
        raise SystemExit(f"Warehouse objective logic is incomplete: {marker}")

regional_block = zscript.split("class CheckoutRegionalManagerSpawner : Actor", 1)[1].split(
    "class WarehouseLiftControlSpawner : Actor", 1
)[0]
for marker in (
    'p.CountInv("CheckoutFuse") < 3',
    'p.CountInv("WarehouseLiftOverride") < 1',
    'Actor.Spawn("RegionalManager", Pos)',
):
    if marker not in regional_block:
        raise SystemExit(f"Regional Manager must remain behind breakers + freight-lift activation: {marker}")

accessibility = (GAME / "ZSCRIPT_ACCESSIBILITY").read_text(encoding="utf-8")
for marker in (
    'p.CountInv("WarehouseDepartmentToken") > 0',
    'p.CountInv("WarehouseLiftOverride") > 0',
    "CheckoutShiftDirector.GetDepartmentObjectiveText(",
    'String.Format("POWER %d/3  //  LIFT %s"',
):
    if marker not in accessibility:
        raise SystemExit(f"Accessibility focus HUD is not synchronized with the warehouse objective: {marker}")

map02 = (GAME / "MAP02.udmf").read_text(encoding="utf-8")
if map02.count("type = 17111") != 3:
    raise SystemExit("Warehouse 13.5 must retain exactly three breaker fuses")
if map02.count("type = 17133") != 1 or map02.count("type = 17104") != 1:
    raise SystemExit("Warehouse 13.5 needs exactly one lift-control anchor and one Regional Manager anchor")
if "type = 17006" in map02:
    raise SystemExit("Warehouse 13.5 must not pre-place the Regional Manager")

control_match = re.search(r"x = 0\.0; y = ([0-9.]+); angle = 270; type = 17133", map02)
boss_match = re.search(r"x = 0\.0; y = ([0-9.]+); angle = 270; type = 17104", map02)
if not control_match or not boss_match:
    raise SystemExit("Warehouse rear-bay objective anchors are not at the expected readable centerline")
if float(boss_match.group(1)) - float(control_match.group(1)) < 96.0:
    raise SystemExit("Regional Manager anchor is too close to the lift-control interaction")

environment = (GAME / "MAP02_ENVIRONMENT.udmf").read_text(encoding="utf-8")
if environment.count("type = 17134") < 2:
    raise SystemExit("Warehouse 13.5 needs paired project-owned freight signage")
for prop_type in ("17125", "17127", "17124"):
    if f"type = {prop_type}" not in environment:
        raise SystemExit(f"Warehouse 13.5 environment layer is missing safe retail prop type {prop_type}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for rel in ("sprites/WCTLA0.png", "sprites/WSGNA0.png", "maps/MAP02.wad"):
        if rel not in names:
            raise SystemExit(f"Warehouse runtime payload missing from PK3: {rel}")
    runtime_zscript = archive.read("ZSCRIPT").decode("utf-8")
    runtime_decorate = archive.read("DECORATE").decode("utf-8")
    runtime_map = archive.read("maps/MAP02.wad")
    if "class WarehouseLiftControlSpawner : Actor" not in runtime_zscript:
        raise SystemExit("Packaged ZSCRIPT lost the warehouse lift-control spawner")
    if "actor WarehouseLiftOverride : Inventory" not in runtime_decorate:
        raise SystemExit("Packaged DECORATE lost the warehouse lift override")
    for marker in (b"type = 17133", b"type = 17104", b"type = 17134"):
        if marker not in runtime_map:
            raise SystemExit(f"Packaged MAP02 lost warehouse objective/environment marker: {marker!r}")

print("Warehouse 13.5 freight-lift objective contract: PASS")
print("Three breakers now power a deliberate lift override before Regional Management can enter; HUD/accessibility and project-owned loading-bay presentation stay synchronized.")
