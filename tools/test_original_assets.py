from pathlib import Path
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

required_pngs = [
    "textures/CHKWALL.png",
    "textures/CHKSHELF.png",
    "textures/CHKSTAF.png",
    "flats/CHKFLR.png",
    "flats/CHKCEIL.png",
    "sprites/COSHA0.png",
    "sprites/COFUA0.png",
    "sprites/COSTA0.png",
]
required_wavs = [
    "sounds/fuse.wav",
    "sounds/shutter.wav",
    "sounds/bossalarm.wav",
    "sounds/clockout.wav",
    "sounds/overtime.wav",
]

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

for rel in required_pngs:
    path = GAME / rel
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Generated PNG is invalid: {rel}")
    width, height = struct.unpack(">II", data[16:24])
    if width < 32 or height < 32:
        raise SystemExit(f"Generated PNG is unexpectedly small: {rel} -> {width}x{height}")

for rel in required_wavs:
    path = GAME / rel
    with wave.open(str(path), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise SystemExit(f"Generated WAV format is invalid: {rel}")
        if stream.getframerate() != 22050 or stream.getnframes() < 4000:
            raise SystemExit(f"Generated WAV duration/rate is invalid: {rel}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    expected = {"SNDINFO", *required_pngs, *required_wavs}
    missing = expected - names
    if missing:
        raise SystemExit(f"Original runtime assets missing from PK3: {sorted(missing)}")

map01 = (GAME / "MAP01.udmf").read_text(encoding="utf-8")
for texture in ("CHKFLR", "CHKCEIL", "CHKWALL", "CHKSHELF", "CHKSTAF"):
    if texture not in map01:
        raise SystemExit(f"Closing Time does not reference original surface: {texture}")

actors = (GAME / "DECORATE").read_text(encoding="utf-8")
for sprite in ("COFU A", "COST A"):
    if sprite not in actors:
        raise SystemExit(f"Original objective sprite state missing: {sprite}")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
if "COSH A -1" not in zscript:
    raise SystemExit("Original Staff Only shutter sprite state missing")
for cue in ("coh/overtime", "coh/clockout", "coh/bossalarm", "coh/shutter"):
    if cue not in zscript:
        raise SystemExit(f"Runtime cue is not wired into gameplay: {cue}")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
for cue in ("coh/fuse", "coh/shutter", "coh/bossalarm", "coh/clockout", "coh/overtime"):
    if cue not in sndinfo:
        raise SystemExit(f"SNDINFO cue missing: {cue}")

print("Original asset contract: PASS")
print("Closing Time now packages deterministic original surfaces, objective sprites and interaction audio.")
