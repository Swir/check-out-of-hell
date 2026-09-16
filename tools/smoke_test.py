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
]
for actor in required_actors:
    if not re.search(rf"\bactor\s+{re.escape(actor)}\b", source):
        raise SystemExit(f"Actor missing from DECORATE: {actor}")

mapinfo = MAPINFO.read_text(encoding="utf-8")
for map_name in ("MAP01", "MAP02"):
    if f"map {map_name} " not in mapinfo:
        raise SystemExit(f"MAPINFO entry missing: {map_name}")

print("Smoke test: PASS")
print("PK3 structure, two generated maps and prototype actor registry look valid.")
