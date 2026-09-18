from pathlib import Path
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

memo_png = GAME / "sprites" / "CMEMA0.png"
memo_wav = GAME / "sounds" / "memo.wav"


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

if not memo_png.exists():
    raise SystemExit("Generated Corporate Memo sprite missing")
image = memo_png.read_bytes()
if not image.startswith(b"\x89PNG\r\n\x1a\n"):
    raise SystemExit("Corporate Memo sprite is not a PNG")
offsets = [payload for kind, payload in png_chunks(image) if kind == b"grAb"]
if len(offsets) != 1 or len(offsets[0]) != 8:
    raise SystemExit("Corporate Memo sprite is missing one valid ZDoom grAb chunk")

if not memo_wav.exists():
    raise SystemExit("Generated Corporate Memo pickup cue missing")
with wave.open(str(memo_wav), "rb") as stream:
    if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
        raise SystemExit("Corporate Memo WAV format is invalid")
    if stream.getframerate() != 22050 or stream.getnframes() < 4000:
        raise SystemExit("Corporate Memo WAV duration/rate is invalid")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for rel in ("sprites/CMEMA0.png", "sounds/memo.wav"):
        if rel not in names:
            raise SystemExit(f"Closing Time presentation asset missing from PK3: {rel}")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
for marker in (
    "class CorporateMemo : Inventory",
    'Inventory.MaxAmount 3;',
    'CMEM A -1 Bright;',
    'p.CountInv("CorporateMemo")',
    'MEMO 1/3: BREAKS MAY OCCUR AFTER CLOCK-OUT',
    'MEMO 2/3: PALLET JACKS ARE NOT EMOTIONAL SUPPORT VEHICLES',
    'MEMO 3/3: REGIONAL MANAGEMENT DENIES THE EXISTENCE OF HELL',
    'CHECKOUT OF HELL // NIGHT SHIFT',
    'String.Format("POWER  %d/3", fuses)',
    'String.Format("MEMOS  %d/3", memos)',
    'GetDepartmentObjectiveText(fuses, bossCleared, exitPending, warehouse, liftEngaged)',
    'GetDepartmentObjectiveHint(fuses, bossCleared, warehouse, liftEngaged)',
    'ROUTE: STAFF ONLY ACCESS IS NOW POWERED',
):
    if marker not in zscript:
        raise SystemExit(f"Closing Time HUD/memo presentation contract missing: {marker}")

for threshold in ("return 90;", "return 180;", "return 270;"):
    if threshold not in zscript:
        raise SystemExit(f"HUD no longer exposes the intended Overtime deadline: {threshold}")

mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
if '17105 = "CorporateMemo"' not in mapinfo:
    raise SystemExit("Corporate Memo DoomEdNum is missing")

map01 = (GAME / "MAP01.udmf").read_text(encoding="utf-8")
if map01.count("type = 17105") != 3:
    raise SystemExit("Closing Time must contain exactly three optional Corporate Memo pickups")
if "x = -620.0; y =  455.0" not in map01:
    raise SystemExit("Closing Time Staff Only room must contain one Corporate Memo")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
if "coh/memo            sounds/memo" not in sndinfo:
    raise SystemExit("Corporate Memo pickup cue is not registered in SNDINFO")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_presentation_assets import generate_presentation_assets",
    "generate_presentation_assets(GAME)",
):
    if marker not in build:
        raise SystemExit(f"Presentation generator is not wired into the build: {marker}")

print("Closing Time presentation contract: PASS")
print("Memo exploration route and Closing Time HUD fallbacks remain packaged while department-aware objective routing is enabled.")
