from pathlib import Path
import struct
import wave
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


def read_textmap(wad: bytes) -> str:
    ident, numlumps, directory_offset = struct.unpack("<4sII", wad[:12])
    if ident != b"PWAD" or numlumps < 1:
        raise SystemExit("MAP01 WAD header is invalid")
    for index in range(numlumps):
        entry = directory_offset + index * 16
        offset, size, raw_name = struct.unpack("<II8s", wad[entry : entry + 16])
        name = raw_name.rstrip(b"\0").decode("ascii")
        if name == "TEXTMAP":
            return wad[offset : offset + size].decode("utf-8")
    raise SystemExit("MAP01 WAD has no TEXTMAP lump")


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
    "actor CheckoutOvertimeHazardSpawner 17106",
    'A_PlaySound("coh/overtimealarm"',
    'A_PlaySound("coh/overtimearc"',
    "A_Explode(10, 72)",
    "TNT1 A 3150",
    "TNT1 A 1575",
    "TNT1 A 1120",
    "TNT1 A 910",
    "TNT1 A 700",
):
    if marker not in extension:
        raise SystemExit(f"Overtime hazard actor contract missing: {marker}")

map_extension = (GAME / "MAP01_OVERTIME.udmf").read_text(encoding="utf-8")
if map_extension.count("type = 17106") != 4:
    raise SystemExit("Closing Time must contain exactly four Overtime hazard anchors")
if "y = -430.0" in map_extension or "y = -365.0" in map_extension:
    raise SystemExit("Overtime hazards must not occupy the player start/clock-out zone")

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
    'GAME / f"{map_name}_OVERTIME.udmf"',
):
    if marker not in build:
        raise SystemExit(f"Overtime subsystem is not wired into the build: {marker}")

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
    if "actor CheckoutOvertimeHazardSpawner 17106" not in decorate:
        raise SystemExit("Packaged DECORATE does not include the Overtime hazard subsystem")

    textmap = read_textmap(archive.read("maps/MAP01.wad"))
    if textmap.count("type = 17106") != 4:
        raise SystemExit("Packaged MAP01 does not contain all four Overtime hazard anchors")

print("Overtime environmental hazard contract: PASS")
print("Closing Time now escalates from warning alarms to readable floor arcs and faster Hell Rush traps.")
