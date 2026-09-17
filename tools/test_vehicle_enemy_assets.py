from pathlib import Path
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

cart_pngs = [f"sprites/CART{frame}0.png" for frame in "ABCDEFGHIJK"]
pallet_pngs = [f"sprites/PJCK{frame}0.png" for frame in "ABCDEFGHIJK"]
required_pngs = cart_pngs + pallet_pngs
required_wavs = [
    "sounds/cartidle.wav",
    "sounds/cartcharge.wav",
    "sounds/carthit.wav",
    "sounds/cartdown.wav",
    "sounds/palletidle.wav",
    "sounds/palletattack.wav",
    "sounds/pallethit.wav",
    "sounds/palletdown.wav",
]


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

for rel in required_pngs:
    path = GAME / rel
    if not path.exists():
        raise SystemExit(f"Generated vehicle-enemy sprite missing: {rel}")
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Generated vehicle-enemy PNG is invalid: {rel}")
    width, height = struct.unpack(">II", data[16:24])
    if width < 32 or height < 32:
        raise SystemExit(f"Generated vehicle-enemy PNG is unexpectedly small: {rel} -> {width}x{height}")
    offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
    if len(offsets) != 1 or len(offsets[0]) != 8:
        raise SystemExit(f"Vehicle-enemy sprite is missing one valid ZDoom grAb chunk: {rel}")

for rel in required_wavs:
    path = GAME / rel
    if not path.exists():
        raise SystemExit(f"Generated vehicle-enemy cue missing: {rel}")
    with wave.open(str(path), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise SystemExit(f"Generated vehicle-enemy WAV format is invalid: {rel}")
        if stream.getframerate() != 22050 or stream.getnframes() < 4000:
            raise SystemExit(f"Generated vehicle-enemy WAV duration/rate is invalid: {rel}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    missing = set(required_pngs + required_wavs) - names
    if missing:
        raise SystemExit(f"Vehicle-enemy runtime assets missing from PK3: {sorted(missing)}")

actors = (GAME / "DECORATE").read_text(encoding="utf-8")
cart_block = actors.split("actor CartOfDoom", 1)[1].split("actor NightManager", 1)[0]
pallet_block = actors.split("actor PalletJack", 1)[1].split("actor RegionalManager", 1)[0]

for marker in (
    "CART A 10 A_Look",
    "CART D 3 A_Chase",
    'A_PlaySound("coh/cartcharge"',
    "A_SkullAttack",
    'PainSound "coh/carthit"',
    'DeathSound "coh/cartdown"',
    "CART K -1",
):
    if marker not in cart_block:
        raise SystemExit(f"Cart of Doom original presentation is incomplete: {marker}")
if "SKUL" in cart_block:
    raise SystemExit("Cart of Doom still references compatible-IWAD Lost Soul sprite states")

for marker in (
    "PJCK A 10 A_Look",
    "PJCK D 3 A_Chase",
    'A_PlaySound("coh/palletattack"',
    "A_SargAttack",
    'PainSound "coh/pallethit"',
    'DeathSound "coh/palletdown"',
    "PJCK K -1",
):
    if marker not in pallet_block:
        raise SystemExit(f"Possessed Pallet Jack original presentation is incomplete: {marker}")
if "SARG" in pallet_block:
    raise SystemExit("Possessed Pallet Jack still references compatible-IWAD Demon sprite states")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
for cue in (
    "coh/cartidle",
    "coh/cartcharge",
    "coh/carthit",
    "coh/cartdown",
    "coh/palletidle",
    "coh/palletattack",
    "coh/pallethit",
    "coh/palletdown",
):
    if cue not in sndinfo:
        raise SystemExit(f"Vehicle-enemy SNDINFO cue missing: {cue}")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_vehicle_enemy_assets import generate_vehicle_enemy_assets",
    "generate_vehicle_enemy_assets(GAME)",
):
    if marker not in build:
        raise SystemExit(f"Vehicle-enemy generator is not wired into the build: {marker}")

print("Vehicle enemy asset contract: PASS")
print("Cart of Doom and Possessed Pallet Jack use project-owned generated sprites, attack tells and combat cues.")
