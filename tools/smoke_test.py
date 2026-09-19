from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
DECORATE = ROOT / "game" / "DECORATE"
MAPINFO = ROOT / "game" / "MAPINFO"
ZSCRIPT = ROOT / "game" / "ZSCRIPT"

PLAYABLE_MAPS = ("MAP01", "MAP02", "MAP03", "MAP04")
EXPECTED_CHAIN = {
    "MAP01": "MAP02",
    "MAP02": "MAP03",
    "MAP03": "MAP04",
    "MAP04": "MAP01",
}
MAP_LAYER_SUFFIXES = ("OVERTIME", "ENVIRONMENT")

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")


def expected_map_source(map_name: str) -> bytes:
    """Mirror the build's deterministic UDMF layer composition for parity checks."""
    chunks = [(ROOT / "game" / f"{map_name}.udmf").read_text(encoding="utf-8").rstrip()]
    for suffix in MAP_LAYER_SUFFIXES:
        extension = ROOT / "game" / f"{map_name}_{suffix}.udmf"
        if extension.exists():
            chunks.append(extension.read_text(encoding="utf-8").rstrip())
    return ("\n\n".join(chunks) + "\n").encode("utf-8")


def read_udmf_textmap(wad: bytes, map_name: str) -> bytes:
    """Validate canonical UDMF markers and return the packaged TEXTMAP payload."""
    if len(wad) < 12:
        raise SystemExit(f"{map_name} WAD is too small")

    ident, numlumps, dir_offset = struct.unpack("<4sII", wad[:12])
    if ident != b"PWAD":
        raise SystemExit(f"{map_name} has invalid WAD identifier: {ident!r}")
    if numlumps != 3:
        raise SystemExit(f"{map_name} must contain exactly MAPxx/TEXTMAP/ENDMAP lumps")
    if not (12 <= dir_offset <= len(wad) - numlumps * 16):
        raise SystemExit(f"{map_name} has invalid WAD directory offset {dir_offset}")

    entries = []
    for index in range(numlumps):
        offset, size, raw_name = struct.unpack_from("<II8s", wad, dir_offset + index * 16)
        name = raw_name.rstrip(b"\0").decode("ascii")
        if offset < 12 or offset + size > dir_offset:
            raise SystemExit(f"{map_name} lump {name} points outside the WAD data region")
        entries.append((name, offset, size))

    names = [name for name, _, _ in entries]
    expected_names = [map_name, "TEXTMAP", "ENDMAP"]
    if names != expected_names:
        raise SystemExit(f"{map_name} UDMF marker order mismatch: {names} != {expected_names}")

    _, text_offset, text_size = entries[1]
    return wad[text_offset : text_offset + text_size]


required_entries = {"DECORATE", "MAPINFO", "LANGUAGE", "ZSCRIPT"}
required_entries.update(f"maps/{map_name}.wad" for map_name in PLAYABLE_MAPS)

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    missing = required_entries - names
    if missing:
        raise SystemExit(f"Missing PK3 entries: {sorted(missing)}")

    for map_name in PLAYABLE_MAPS:
        wad = archive.read(f"maps/{map_name}.wad")
        packaged_textmap = read_udmf_textmap(wad, map_name)
        expected_textmap = expected_map_source(map_name)
        if packaged_textmap != expected_textmap:
            raise SystemExit(
                f"{map_name} packaged TEXTMAP differs from the deterministic source/layer composition"
            )

    packaged_mapinfo = archive.read("MAPINFO").decode("utf-8")
    if packaged_mapinfo != MAPINFO.read_text(encoding="utf-8"):
        raise SystemExit("Packaged MAPINFO differs from game/MAPINFO")

    packaged_decorate = archive.read("DECORATE").decode("utf-8")
    for marker in (
        "actor EmergencyMop",
        "actor OvertimeWarningFlash",
        "actor FrozenCompressorReset",
        "actor ElectronicsNetworkReboot",
    ):
        if marker not in packaged_decorate:
            raise SystemExit(f"Packaged DECORATE lost subsystem marker: {marker}")

    packaged_zscript = archive.read("ZSCRIPT").decode("utf-8")
    for marker in (
        "class CheckoutShiftDirector : EventHandler",
        "class CheckoutClockOutGuideSpawner : Actor",
        "class FrozenCompressorResetSpawner : Actor",
        "class ElectronicsNetworkRebootSequence : Actor",
        "class CheckoutAccessibilityHandler : EventHandler",
    ):
        if marker not in packaged_zscript:
            raise SystemExit(f"Packaged ZSCRIPT lost subsystem marker: {marker}")

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
for map_name in PLAYABLE_MAPS:
    if f"map {map_name} " not in mapinfo:
        raise SystemExit(f"MAPINFO entry missing: {map_name}")

    next_map = EXPECTED_CHAIN[map_name]
    block_match = re.search(
        rf'map\s+{map_name}\s+"[^"]+"\s*\{{(?P<body>.*?)\n\}}',
        mapinfo,
        flags=re.DOTALL,
    )
    if not block_match:
        raise SystemExit(f"Could not parse MAPINFO block for {map_name}")
    block = block_match.group("body")
    if f'next = "{next_map}"' not in block:
        raise SystemExit(f"{map_name} must advance to {next_map}")
    if not re.search(r'music\s*=\s*"D_COH\d{2}"', block):
        raise SystemExit(f"{map_name} must use a project-owned department soundtrack")

if 'AddEventHandlers = "CheckoutShiftDirector"' not in mapinfo:
    raise SystemExit("CheckoutShiftDirector is not registered in MAPINFO")
if '17100 = "CheckoutOvertimeSpawner"' not in mapinfo:
    raise SystemExit("Overtime spawner DoomEdNum is missing")
if '17101 = "CheckoutManagerSpawner"' not in mapinfo:
    raise SystemExit("Gated supervisor spawner DoomEdNum is missing")
if '17139 = "FrozenDepartmentInitSpawner"' not in mapinfo:
    raise SystemExit("Frozen Foods department initializer DoomEdNum is missing")
if '17141 = "FrozenCompressorResetSpawner"' not in mapinfo:
    raise SystemExit("Frozen Foods compressor reset DoomEdNum is missing")
if '17144 = "ElectronicsDepartmentInitSpawner"' not in mapinfo:
    raise SystemExit("Electronics department initializer DoomEdNum is missing")
if '17146 = "ElectronicsNetworkRebootSpawner"' not in mapinfo:
    raise SystemExit("Electronics network reboot DoomEdNum is missing")

zscript = ZSCRIPT.read_text(encoding="utf-8")
for required in (
    "class CheckoutShiftDirector : EventHandler",
    "class CheckoutOvertimeSpawner : Actor",
    "class CheckoutManagerSpawner : Actor",
    "Level.ExitLevel(0, false)",
    'CountInv("CheckoutFuse")',
):
    if required not in zscript:
        raise SystemExit(f"ZScript gameplay contract missing: {required}")

for map_name in PLAYABLE_MAPS:
    source_map = expected_map_source(map_name).decode("utf-8")
    if len(re.findall(r"\btype\s*=\s*1\s*;", source_map)) != 1:
        raise SystemExit(f"{map_name} must contain exactly one player start")
    if "type = 17100" not in source_map:
        raise SystemExit(f"{map_name} must contain at least one Overtime spawner")

for map_name in ("MAP01", "MAP02"):
    source_map = (ROOT / "game" / f"{map_name}.udmf").read_text(encoding="utf-8")
    if source_map.count("type = 17111") < 3:
        raise SystemExit(f"{map_name} must contain at least three breaker fuses")

map01 = (ROOT / "game" / "MAP01.udmf").read_text(encoding="utf-8")
if map01.count("type = 17101") != 1:
    raise SystemExit("MAP01 must contain exactly one gated Night Manager spawner")
if "type = 17003" in map01:
    raise SystemExit("MAP01 must not pre-place Night Manager before power restoration")

map02 = (ROOT / "game" / "MAP02.udmf").read_text(encoding="utf-8")
if map02.count("type = 17133") != 1 or map02.count("type = 17104") != 1:
    raise SystemExit("MAP02 must contain one freight-lift control and one Regional Manager spawner")
if "type = 17006" in map02:
    raise SystemExit("MAP02 must not pre-place Regional Manager before the lift objective")

map03 = (ROOT / "game" / "MAP03.udmf").read_text(encoding="utf-8")
if map03.count("type = 17111") != 2 or map03.count("type = 17141") != 1:
    raise SystemExit("MAP03 must use two breaker fuses plus one rear compressor reset power step")
if map03.count("type = 17101") != 1 or map03.count("type = 17139") != 1:
    raise SystemExit("MAP03 must contain one gated supervisor and one fresh-entry initializer")
if "type = 17003" in map03:
    raise SystemExit("MAP03 must not pre-place Night Manager before freezer power restoration")

map04 = (ROOT / "game" / "MAP04.udmf").read_text(encoding="utf-8")
if map04.count("type = 17111") != 2 or map04.count("type = 17146") != 1:
    raise SystemExit("MAP04 must use two breaker fuses plus one rear Store Network Reboot power step")
if map04.count("type = 17101") != 1 or map04.count("type = 17144") != 1:
    raise SystemExit("MAP04 must contain one gated supervisor and one fresh-entry initializer")
if map04.count("type = 17149") != 1 or map04.count("type = 17150") != 1:
    raise SystemExit("MAP04 must contain one reboot defence anchor and one Overtime lockdown anchor")
if "type = 17003" in map04:
    raise SystemExit("MAP04 must not pre-place Night Manager before electronics power restoration")

print("Smoke test: PASS")
print(
    "PK3 structure, exact packaged UDMF parity, campaign topology and staged objective loops "
    "for MAP01/MAP02/MAP03/MAP04 look valid."
)
