from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
DECORATE = ROOT / "game" / "DECORATE"
MAPINFO = ROOT / "game" / "MAPINFO"
ZSCRIPT = ROOT / "game" / "ZSCRIPT"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

required_entries = {
    "DECORATE",
    "MAPINFO",
    "LANGUAGE",
    "ZSCRIPT",
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
        assert numlumps == 3, (map_name, numlumps)
        assert 12 <= dir_offset < len(wad), (map_name, dir_offset)

        directory = wad[dir_offset : dir_offset + numlumps * 16]
        lump_names = []
        for offset in range(0, len(directory), 16):
            _filepos, _size, raw_name = struct.unpack("<II8s", directory[offset : offset + 16])
            lump_names.append(raw_name.rstrip(b"\0").decode("ascii"))
        expected = [map_name, "TEXTMAP", "ENDMAP"]
        assert lump_names == expected, (map_name, lump_names)

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
    "CheckoutFuse",
]
for actor in required_actors:
    if not re.search(rf"\bactor\s+{re.escape(actor)}\b", source):
        raise SystemExit(f"Actor missing from DECORATE: {actor}")

mapinfo = MAPINFO.read_text(encoding="utf-8")
for map_name in ("MAP01", "MAP02"):
    if f"map {map_name} " not in mapinfo:
        raise SystemExit(f"MAPINFO entry missing: {map_name}")

if 'AddEventHandlers = "CheckoutShiftDirector"' not in mapinfo:
    raise SystemExit("CheckoutShiftDirector is not registered in MAPINFO")
if '17100 = "CheckoutOvertimeSpawner"' not in mapinfo:
    raise SystemExit("Overtime spawner DoomEdNum is missing")
if '17101 = "CheckoutManagerSpawner"' not in mapinfo:
    raise SystemExit("Gated supervisor spawner DoomEdNum is missing")

zscript = ZSCRIPT.read_text(encoding="utf-8")
for required in (
    "class CheckoutShiftDirector : EventHandler",
    "class CheckoutOvertimeSpawner : Actor",
    "class CheckoutManagerSpawner : Actor",
    "Level.ExecuteSpecial(243, p, null, false, 0)",
    'CountInv("CheckoutFuse")',
):
    if required not in zscript:
        raise SystemExit(f"ZScript gameplay contract missing: {required}")

for map_name in ("MAP01", "MAP02"):
    source_map = (ROOT / "game" / f"{map_name}.udmf").read_text(encoding="utf-8")
    if source_map.count("type = 17111") < 3:
        raise SystemExit(f"{map_name} must contain at least three breaker fuses")
    if "type = 17100" not in source_map:
        raise SystemExit(f"{map_name} must contain at least one Overtime spawner")

map01 = (ROOT / "game" / "MAP01.udmf").read_text(encoding="utf-8")
if map01.count("type = 17101") != 1:
    raise SystemExit("MAP01 must contain exactly one gated Night Manager spawner")
if "type = 17003" in map01:
    raise SystemExit("MAP01 must not pre-place Night Manager before power restoration")

print("Smoke test: PASS")
print("PK3 structure, loadable UDMF map markers, staged MAP01 objective loop, Overtime contract and generated maps look valid.")
