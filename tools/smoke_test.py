from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
DECORATE = ROOT / "game" / "DECORATE"
MAPINFO = ROOT / "game" / "MAPINFO"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

required_entries = {
    "DECORATE",
    "MAPINFO",
    "LANGUAGE",
    "maps/MAP01.wad",
    "maps/MAP02.wad",
}

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    missing = required_entries - names
    if missing:
        raise SystemExit(f"Missing PK3 entries: {sorted(missing)}")

    for map_name in ("MAP01", "MAP02"):
        wad = archive.read(f"maps/{map_name}.wad")
        ident, numlumps, dir_offset = struct.unpack("<4sII", wad[:12])
        assert ident == b"PWAD", (map_name, ident)
        assert numlumps == 2, (map_name, numlumps)
        assert 12 <= dir_offset < len(wad), (map_name, dir_offset)

source = DECORATE.read_text(encoding="utf-8")
required_actors = [
    "EmergencyMop",
    "ReceiptRipper",
    "PriceGunSMG",
    "TurboCanLauncher",
    "AngrySelfCheckout",
    "CartOfDoom",
    "NightManager",
    "ScannerTurret",
    "PalletJack",
    "RegionalManager",
    "OvertimeDirector",
    "WarehouseOvertimeDirector",
]
for actor in required_actors:
    if not re.search(rf"\bactor\s+{re.escape(actor)}\b", source):
        raise SystemExit(f"Actor missing from DECORATE: {actor}")

# Guard the design contract: both directors must contain staged waits followed by
# dynamic enemy spawns, rather than being empty map placeholders.
for director in ("OvertimeDirector", "WarehouseOvertimeDirector"):
    match = re.search(
        rf"actor\s+{director}\b(?P<body>.*?)(?=\nactor\s+|\Z)",
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise SystemExit(f"Overtime director body missing: {director}")
    body = match.group("body")
    if body.count("A_SpawnItemEx") < 4:
        raise SystemExit(f"Overtime director has too few pressure spawns: {director}")
    if "TNT1 A 700" not in body and "TNT1 A 1050" not in body:
        raise SystemExit(f"Overtime director has no timed escalation: {director}")

mapinfo = MAPINFO.read_text(encoding="utf-8")
for map_name in ("MAP01", "MAP02"):
    if f"map {map_name} " not in mapinfo:
        raise SystemExit(f"MAPINFO entry missing: {map_name}")

map01 = (ROOT / "game" / "MAP01.udmf").read_text(encoding="utf-8")
map02 = (ROOT / "game" / "MAP02.udmf").read_text(encoding="utf-8")
if not re.search(r"\btype\s*=\s*17100\s*;", map01):
    raise SystemExit("MAP01 is missing the OvertimeDirector map thing (17100)")
if not re.search(r"\btype\s*=\s*17101\s*;", map02):
    raise SystemExit("MAP02 is missing the WarehouseOvertimeDirector map thing (17101)")

print("Smoke test: PASS")
print("PK3 structure, maps, actor registry and staged Overtime pressure contract look valid.")
