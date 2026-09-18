from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    'MAPS = ["MAP01", "MAP02", "MAP03"]',
    '(GAME / "ZSCRIPT_FROZEN").read_text(encoding="utf-8").rstrip()',
):
    if marker not in build:
        raise SystemExit(f"Frozen Foods is not wired into the build: {marker}")

mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
for marker in (
    '17139 = "FrozenDepartmentInitSpawner"',
    '17140 = "FrozenBreakerResponseSpawner"',
    'map MAP03 "Frozen Foods"',
    'music = "D_COH03"',
):
    if marker not in mapinfo:
        raise SystemExit(f"Frozen Foods MAPINFO registration is incomplete: {marker}")

map01_block = mapinfo.split('map MAP01 "Closing Time"', 1)[1].split('map MAP02 "Warehouse 13.5"', 1)[0]
map02_block = mapinfo.split('map MAP02 "Warehouse 13.5"', 1)[1].split('map MAP03 "Frozen Foods"', 1)[0]
map03_block = mapinfo.split('map MAP03 "Frozen Foods"', 1)[1]
if 'next = "MAP02"' not in map01_block or 'next = "MAP03"' not in map02_block or 'next = "MAP01"' not in map03_block:
    raise SystemExit("Playable department progression must remain Closing Time -> Warehouse 13.5 -> Frozen Foods -> Closing Time")

frozen_logic = (GAME / "ZSCRIPT_FROZEN").read_text(encoding="utf-8")
for marker in (
    "class FrozenDepartmentInitSpawner : Actor",
    "nextCheck = Level.maptime + 7;",
    'p.A_TakeInventory("CorporateMemo", 3);',
    "Destroy();",
):
    if marker not in frozen_logic:
        raise SystemExit(f"Frozen Foods department initializer is incomplete: {marker}")

# The initializer is map-local rather than a global EventHandler. That keeps normal save restores
# inside MAP03 from repeatedly erasing optional memo progress.
if "EventHandler" in frozen_logic:
    raise SystemExit("Frozen Foods memo initialization must stay map-local, not become a global save-state handler")

if "class FrozenBreakerResponseSpawner : Actor" not in frozen_logic:
    raise SystemExit("Frozen Foods is missing its breaker-linked cold-chain response spawner")
response_logic = frozen_logic.split("class FrozenBreakerResponseSpawner : Actor", 1)[1]
for marker in (
    "nextCheck = Level.maptime + 7;",
    'p.CountInv("SupervisorClearanceToken") > 0',
    "pendingFuse = observedFuseCount + 1;",
    "responseTic = Level.maptime + 35 * 3;",
    'Actor.Spawn("OvertimeWarningFlash", Pos);',
    "if (pendingFuse == 1)",
    'Actor.Spawn("ScannerTurret", Pos);',
    "else if (pendingFuse == 2)",
    'Actor.Spawn("CartOfDoom", Pos);',
    "observedFuseCount < 2",
):
    if marker not in response_logic:
        raise SystemExit(f"Frozen Foods breaker response lost a readability/gating contract: {marker}")
if 'Actor.Spawn("PalletJack", Pos);' in response_logic:
    raise SystemExit("Frozen Foods breaker response must hand full-power pressure to the boss systems, not add a third instant enemy")

map03 = (GAME / "MAP03.udmf").read_text(encoding="utf-8")
required_counts = {
    17139: 1,  # fresh-entry optional-state initializer
    17140: 1,  # breaker-linked cold-chain flank response
    17111: 3,  # breaker fuses
    17101: 1,  # power-gated Night Manager spawner
    17103: 1,  # deterministic management response
    17128: 1,  # full-power recovery cache
    17132: 1,  # post-clear clock-out guide
    17105: 3,  # optional compliance memos
}
for thing_type, expected in required_counts.items():
    actual = map03.count(f"type = {thing_type}")
    if actual != expected:
        raise SystemExit(f"Frozen Foods type {thing_type} count changed: expected {expected}, found {actual}")

if map03.count("type = 17100") < 3:
    raise SystemExit("Frozen Foods needs at least three ambient Overtime reinforcement anchors")
if "type = 17003" in map03:
    raise SystemExit("Frozen Foods must not pre-place Night Manager before power restoration")

start = re.search(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 90; type = 1", map03)
manager = re.search(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 270; type = 17101", map03)
guide = re.search(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 90; type = 17132", map03)
response_anchor = re.search(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 180; type = 17140", map03)
if not start or abs(float(start.group(1))) > 80.0 or float(start.group(2)) > -350.0:
    raise SystemExit("Frozen Foods player start must stay on the front clock-out approach")
if not manager or abs(float(manager.group(1))) > 100.0 or float(manager.group(2)) < 300.0:
    raise SystemExit("Frozen Foods supervisor must remain at the rear of the department")
if not guide or abs(float(guide.group(1))) > 100.0 or float(guide.group(2)) > -300.0:
    raise SystemExit("Frozen Foods post-clear guide must remain near the entry/clock-out route")
if not response_anchor or float(response_anchor.group(1)) < 500.0 or not -80.0 <= float(response_anchor.group(2)) <= 220.0:
    raise SystemExit("Frozen Foods breaker response must remain on the right-side freezer flank")

# Four authored shelf lines are the minimum department geometry: MAP03 must not regress into a flat
# box arena while still leaving a central service lane between the inner shelving runs.
if map03.count("texturemiddle = \"CHKSHELF\"") < 8:
    raise SystemExit("Frozen Foods is missing its authored freezer-aisle shelving")
for required_vertex in (
    'vertex { x = -360.0; y = -250.0; }',
    'vertex { x = -120.0; y =  -40.0; }',
    'vertex { x =  120.0; y = -300.0; }',
    'vertex { x =  360.0; y = -230.0; }',
):
    if required_vertex not in map03:
        raise SystemExit(f"Frozen Foods aisle geometry drifted: {required_vertex}")

environment = (GAME / "MAP03_ENVIRONMENT.udmf").read_text(encoding="utf-8")
if environment.count("type = 17121") != 2:
    raise SystemExit("Frozen Foods needs exactly two project-owned department signs at the entry")
for prop_type in (17125, 17124, 17126, 17127):
    if f"type = {prop_type}" not in environment:
        raise SystemExit(f"Frozen Foods environment layer is missing project-owned/safe prop type {prop_type}")

overtime = (GAME / "MAP03_OVERTIME.udmf").read_text(encoding="utf-8")
if overtime.count("type = 17106") != 4:
    raise SystemExit("Frozen Foods needs exactly four authored environmental Overtime hazard anchors")
for x_text, y_text in re.findall(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 0; type = 17106", overtime):
    x = float(x_text)
    y = float(y_text)
    if abs(x) < 180.0 and y < -260.0:
        raise SystemExit("Frozen Foods Overtime hazard moved into the player entry/clock-out lane")

sign = GAME / "sprites" / "FSGNA0.png"
track = GAME / "music" / "D_COH03.mid"
for path in (sign, track):
    if not path.exists():
        raise SystemExit(f"Frozen Foods generated presentation asset is missing: {path.relative_to(ROOT)}")
if not sign.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
    raise SystemExit("Frozen Foods department sign is not a valid generated PNG")
if b"Frozen Foods - Compressor Choir" not in track.read_bytes():
    raise SystemExit("Frozen Foods soundtrack lost its authored track-name marker")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for entry in (
        "maps/MAP03.wad",
        "sprites/FSGNA0.png",
        "music/D_COH03.mid",
        "MAPINFO",
        "ZSCRIPT",
    ):
        if entry not in names:
            raise SystemExit(f"Packaged PK3 is missing Frozen Foods payload: {entry}")

    packaged_mapinfo = archive.read("MAPINFO").decode("utf-8")
    packaged_zscript = archive.read("ZSCRIPT").decode("utf-8")
    if 'map MAP03 "Frozen Foods"' not in packaged_mapinfo or 'music = "D_COH03"' not in packaged_mapinfo:
        raise SystemExit("Packaged MAPINFO lost Frozen Foods registration")
    if '17140 = "FrozenBreakerResponseSpawner"' not in packaged_mapinfo:
        raise SystemExit("Packaged MAPINFO lost the Frozen Foods breaker-response registration")
    if "class FrozenDepartmentInitSpawner : Actor" not in packaged_zscript:
        raise SystemExit("Packaged ZSCRIPT lost the Frozen Foods initializer")
    if "class FrozenBreakerResponseSpawner : Actor" not in packaged_zscript:
        raise SystemExit("Packaged ZSCRIPT lost the Frozen Foods breaker-response logic")

    wad = archive.read("maps/MAP03.wad")
    ident, numlumps, dir_offset = struct.unpack("<4sII", wad[:12])
    if ident != b"PWAD" or numlumps != 3:
        raise SystemExit("Packaged MAP03 is not the expected canonical three-lump PWAD")
    directory = wad[dir_offset : dir_offset + numlumps * 16]
    entries = []
    for index in range(numlumps):
        offset, size, raw_name = struct.unpack_from("<II8s", directory, index * 16)
        entries.append((offset, size, raw_name.rstrip(b"\0").decode("ascii")))
    if [name for _, _, name in entries] != ["MAP03", "TEXTMAP", "ENDMAP"]:
        raise SystemExit("Packaged MAP03 lost canonical MAP03 -> TEXTMAP -> ENDMAP ordering")
    text_offset, text_size, _ = entries[1]
    textmap = wad[text_offset : text_offset + text_size].decode("utf-8")
    for marker in ("type = 17139", "type = 17140", "type = 17101", "type = 17106", "type = 17121"):
        if marker not in textmap:
            raise SystemExit(f"Packaged MAP03 TEXTMAP is missing playable Frozen Foods marker {marker}")

print("Frozen Foods playable department contract: PASS")
