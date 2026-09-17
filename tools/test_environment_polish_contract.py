from pathlib import Path
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAP_WAD = ROOT / "dist" / "MAP01.wad"

SPRITES = [
    "CSIGA0.png",
    "FSGNA0.png",
    "ESGNA0.png",
    "LSGNA0.png",
    "CONEA0.png",
    "BOXEA0.png",
    "BRKSA0.png",
    "FLITA0.png",
    "FLITB0.png",
    "FLITC0.png",
    "FLITD0.png",
]


def png_chunks(data: bytes):
    cursor = 8
    while cursor + 12 <= len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        payload = data[cursor + 8 : cursor + 8 + length]
        yield kind, payload
        cursor += 12 + length


if not PK3.exists() or not MAP_WAD.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

for name in SPRITES:
    path = GAME / "sprites" / name
    if not path.exists():
        raise SystemExit(f"Generated environment sprite missing: {name}")
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Environment sprite is not PNG: {name}")
    offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
    if len(offsets) != 1 or len(offsets[0]) != 8:
        raise SystemExit(f"Environment sprite needs exactly one valid ZDoom grAb chunk: {name}")

snack_wav = GAME / "sounds" / "breaksnack.wav"
if not snack_wav.exists():
    raise SystemExit("Emergency Break Snack cue missing")
with wave.open(str(snack_wav), "rb") as stream:
    if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
        raise SystemExit("Emergency Break Snack WAV format is invalid")
    if stream.getframerate() != 22050 or stream.getnframes() < 4000:
        raise SystemExit("Emergency Break Snack WAV rate/duration is invalid")

decorate_env = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
actor_markers = (
    "actor CustomerServiceSign 17120",
    "actor FrozenFoodsSign 17121",
    "actor ElectronicsSign 17122",
    "actor CheckoutLaneSign 17123",
    "actor WetFloorCone 17124",
    "actor RestockBoxes 17125",
    "actor EmployeeBreakSnack : Stimpack 17126",
    "actor FailingFluorescent 17127",
    'Inventory.PickupSound "coh/breaksnack"',
    "FLIT A 70 Bright",
    "FLIT B 12",
    "FLIT C 18 Bright",
    "FLIT D 12",
)
for marker in actor_markers:
    if marker not in decorate_env:
        raise SystemExit(f"Environment actor contract missing: {marker}")

layer = (GAME / "MAP01_ENVIRONMENT.udmf").read_text(encoding="utf-8")
expected_counts = {
    17120: 1,
    17121: 1,
    17122: 1,
    17123: 1,
    17124: 2,
    17125: 2,
    17126: 2,
    17127: 6,
}
for doomednum, expected in expected_counts.items():
    actual = layer.count(f"type = {doomednum}")
    if actual != expected:
        raise SystemExit(
            f"Closing Time environment layer expected {expected} placements of {doomednum}, found {actual}"
        )

if "height = 154.0" not in layer:
    raise SystemExit("Closing Time fluorescent fixtures must stay ceiling-mounted")
if "x = -710.0; y = -455.0" not in layer or "x = -700.0; y =  470.0" not in layer:
    raise SystemExit("Closing Time exploration snack rewards moved from their deliberate side-route positions")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
if "coh/breaksnack      sounds/breaksnack" not in sndinfo:
    raise SystemExit("Emergency Break Snack cue is not registered in SNDINFO")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_environment_assets import generate_environment_assets",
    'MAP_LAYER_SUFFIXES = ["OVERTIME", "ENVIRONMENT"]',
    '(GAME / "DECORATE_ENVIRONMENT").read_text',
    "generate_environment_assets(GAME)",
):
    if marker not in build:
        raise SystemExit(f"Environment polish is not fully wired into the build: {marker}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    for name in SPRITES:
        rel = f"sprites/{name}"
        if rel not in names:
            raise SystemExit(f"Environment sprite missing from PK3: {rel}")
    if "sounds/breaksnack.wav" not in names:
        raise SystemExit("Emergency Break Snack cue missing from PK3")
    decorate = archive.read("DECORATE").decode("utf-8")
    for marker in ("CustomerServiceSign", "EmployeeBreakSnack", "FailingFluorescent"):
        if marker not in decorate:
            raise SystemExit(f"Packaged DECORATE is missing environment actor: {marker}")

wad_text = MAP_WAD.read_bytes()
for doomednum in expected_counts:
    if f"type = {doomednum}".encode("ascii") not in wad_text:
        raise SystemExit(f"Built MAP01 does not contain environment DoomEdNum {doomednum}")

print("Closing Time environment polish contract: PASS")
print("Department signs, safe clutter, reduced-flash failing fixtures and optional joke-reward snacks are packaged and placed.")
