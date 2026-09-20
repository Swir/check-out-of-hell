from pathlib import Path
import re
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

CLOSING_TIME_CENTER_HALF_WIDTH = 300.0
OVERTIME_ARC_RADIUS = 72.0
CLOSING_TIME_OVERTIME_ANCHORS = {
    (-510.0, -60.0),
    (510.0, -60.0),
    (-390.0, 220.0),
    (390.0, 220.0),
}


def png_chunks(data: bytes):
    cursor = 8
    while cursor + 12 <= len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        payload = data[cursor + 8 : cursor + 8 + length]
        yield kind, payload
        cursor += 12 + length


def read_textmap(wad: bytes) -> str:
    ident, numlumps, directory_offset = struct.unpack("<4sII", wad[:12])
    if ident != b"PWAD" or numlumps < 1:
        raise SystemExit("Map WAD header is invalid")
    for index in range(numlumps):
        entry = directory_offset + index * 16
        offset, size, raw_name = struct.unpack("<II8s", wad[entry : entry + 16])
        name = raw_name.rstrip(b"\0").decode("ascii")
        if name == "TEXTMAP":
            return wad[offset : offset + size].decode("utf-8")
    raise SystemExit("Map WAD has no TEXTMAP lump")


def overtime_anchor_positions(text: str) -> set[tuple[float, float]]:
    positions: set[tuple[float, float]] = set()
    for block in re.findall(r"thing\s*\{(.*?)\}", text, flags=re.DOTALL):
        if not re.search(r"\btype\s*=\s*17106\s*;", block):
            continue
        x_match = re.search(r"\bx\s*=\s*(-?\d+(?:\.\d+)?)\s*;", block)
        y_match = re.search(r"\by\s*=\s*(-?\d+(?:\.\d+)?)\s*;", block)
        if not x_match or not y_match:
            raise SystemExit("Overtime hazard anchor is missing x/y coordinates")
        positions.add((float(x_match.group(1)), float(y_match.group(1))))
    return positions


def verify_closing_time_anchor_geometry(text: str, source: str) -> None:
    positions = overtime_anchor_positions(text)
    if positions != CLOSING_TIME_OVERTIME_ANCHORS:
        raise SystemExit(
            f"{source} Closing Time Overtime anchors changed: "
            f"expected {sorted(CLOSING_TIME_OVERTIME_ANCHORS)}, got {sorted(positions)}"
        )
    for x, y in positions:
        if abs(x) - OVERTIME_ARC_RADIUS <= CLOSING_TIME_CENTER_HALF_WIDTH:
            raise SystemExit(
                f"{source} Overtime arc at ({x}, {y}) reaches the permanent "
                f"x=-{CLOSING_TIME_CENTER_HALF_WIDTH:.0f}..{CLOSING_TIME_CENTER_HALF_WIDTH:.0f} center corridor"
            )


if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

required_pngs = [
    "OWRNA0.png",
    "OARCA0.png",
    "OARCB0.png",
    "OARCC0.png",
    "OARCD0.png",
]
for name in required_pngs:
    path = GAME / "sprites" / name
    if not path.exists():
        raise SystemExit(f"Generated Overtime sprite missing: {name}")
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Overtime sprite is not PNG: {name}")
    offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
    if len(offsets) != 1 or len(offsets[0]) != 8:
        raise SystemExit(f"Overtime sprite missing one valid grAb chunk: {name}")

for name in ("overtime_alarm.wav", "overtime_arc.wav"):
    path = GAME / "sounds" / name
    if not path.exists():
        raise SystemExit(f"Generated Overtime cue missing: {name}")
    with wave.open(str(path), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise SystemExit(f"Overtime cue has invalid PCM format: {name}")
        if stream.getframerate() != 22050 or stream.getnframes() < 4000:
            raise SystemExit(f"Overtime cue has invalid duration/rate: {name}")

extension = (GAME / "DECORATE_OVERTIME").read_text(encoding="utf-8")
for marker in (
    "actor OvertimeWarningFlash",
    "actor OvertimeFloorArc",
    'A_PlaySound("coh/overtimealarm"',
    'A_PlaySound("coh/overtimearc"',
    "A_Explode(10, 72)",
):
    if marker not in extension:
        raise SystemExit(f"Overtime hazard presentation contract missing: {marker}")
if "actor CheckoutOvertimeHazardSpawner" in extension:
    raise SystemExit("Timed Overtime hazard anchor must live in ZSCRIPT_CLOCKOUT for clearance-aware retirement")

zscript_clockout = (GAME / "ZSCRIPT_CLOCKOUT").read_text(encoding="utf-8")
for marker in (
    "class CheckoutOvertimeHazardSpawner : Actor",
    "nextHazardTic = Level.maptime + 35 * 90",
    'p.CountInv("SupervisorClearanceToken") > 0',
    'Actor.Spawn("OvertimeWarningFlash", Pos)',
    'Actor.Spawn("OvertimeFloorArc", Pos)',
    "nextHazardTic += 35 * 45",
    "nextHazardTic += 35 * 32",
    "nextHazardTic += 35 * 26",
    "nextHazardTic += 35 * 20",
    "Destroy();",
):
    if marker not in zscript_clockout:
        raise SystemExit(f"Clearance-aware Overtime hazard contract missing: {marker}")

# The migrated state machine must preserve the authored schedule exactly:
# 90s warning, 135s warning, 180/212/244/270s arcs, then every 20s.
schedule = [90]
for delay in (45, 45, 32, 32, 26, 20, 20):
    schedule.append(schedule[-1] + delay)
if schedule != [90, 135, 180, 212, 244, 270, 290, 310]:
    raise SystemExit(f"Unexpected Overtime hazard schedule model: {schedule}")

mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
if '17106 = "CheckoutOvertimeHazardSpawner"' not in mapinfo:
    raise SystemExit("Overtime hazard DoomEdNum 17106 is not mapped to the ZScript anchor")

map_extension = (GAME / "MAP01_OVERTIME.udmf").read_text(encoding="utf-8")
if map_extension.count("type = 17106") != 4:
    raise SystemExit("Closing Time must contain exactly four Overtime hazard anchors")
if "y = -430.0" in map_extension or "y = -365.0" in map_extension:
    raise SystemExit("Overtime hazards must not occupy the player start/clock-out zone")
verify_closing_time_anchor_geometry(map_extension, "Source")

warehouse_extension = (GAME / "MAP02_OVERTIME.udmf").read_text(encoding="utf-8")
if warehouse_extension.count("type = 17106") != 2:
    raise SystemExit("Warehouse 13.5 must contain exactly two authored Overtime hazard anchors")
for marker in (
    "x = -500.0; y = -40.0; angle = 0; type = 17106",
    "x =  500.0; y = -40.0; angle = 0; type = 17106",
):
    if marker not in warehouse_extension:
        raise SystemExit(f"Warehouse Overtime hazard anchor left its readable side-lane position: {marker}")
if "x = 0.0" in warehouse_extension:
    raise SystemExit("Warehouse Overtime hazards must stay off the lift/clock-out centerline")
if "y = 116.0" in warehouse_extension or "y = 170.0" in warehouse_extension:
    raise SystemExit("Warehouse Overtime hazards must not enter the optional Damaged Goods cage")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
for marker in (
    "coh/overtimealarm   sounds/overtime_alarm",
    "coh/overtimearc     sounds/overtime_arc",
):
    if marker not in sndinfo:
        raise SystemExit(f"Overtime cue is not registered in SNDINFO: {marker}")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_overtime_assets import generate_overtime_assets",
    "generate_overtime_assets(GAME)",
    'GAME / "DECORATE_OVERTIME"',
    'GAME / "ZSCRIPT_CLOCKOUT"',
    'MAP_LAYER_SUFFIXES = ["OVERTIME", "ENVIRONMENT", "POLISH"]',
    'extension = GAME / f"{map_name}_{suffix}.udmf"',
):
    if marker not in build:
        raise SystemExit(f"Overtime subsystem is not wired into the layered build: {marker}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for rel in (
        "sprites/OWRNA0.png",
        "sprites/OARCA0.png",
        "sprites/OARCB0.png",
        "sprites/OARCC0.png",
        "sprites/OARCD0.png",
        "sounds/overtime_alarm.wav",
        "sounds/overtime_arc.wav",
    ):
        if rel not in names:
            raise SystemExit(f"Overtime asset missing from PK3: {rel}")

    decorate = archive.read("DECORATE").decode("utf-8")
    zscript = archive.read("ZSCRIPT").decode("utf-8")
    if "actor OvertimeFloorArc" not in decorate:
        raise SystemExit("Packaged DECORATE does not include Overtime hazard presentation")
    if "class CheckoutOvertimeHazardSpawner : Actor" not in zscript:
        raise SystemExit("Packaged ZSCRIPT does not include the clearance-aware Overtime hazard anchor")

    textmap = read_textmap(archive.read("maps/MAP01.wad"))
    if textmap.count("type = 17106") != 4:
        raise SystemExit("Packaged MAP01 does not contain all four Overtime hazard anchors")
    verify_closing_time_anchor_geometry(textmap, "Packaged MAP01")

    warehouse_textmap = read_textmap(archive.read("maps/MAP02.wad"))
    if warehouse_textmap.count("type = 17106") != 2:
        raise SystemExit("Packaged MAP02 does not contain both Warehouse Overtime hazard anchors")
    for marker in (
        "x = -500.0; y = -40.0; angle = 0; type = 17106",
        "x =  500.0; y = -40.0; angle = 0; type = 17106",
    ):
        if marker not in warehouse_textmap:
            raise SystemExit(f"Packaged MAP02 lost Warehouse Overtime side-lane placement: {marker}")

print("Overtime environmental hazard contract: PASS")
print("Closing Time keeps each 72-unit floor arc outside its permanent center corridor, and Warehouse 13.5 preserves its side-lane pressure.")
