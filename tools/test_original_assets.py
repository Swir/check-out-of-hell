from pathlib import Path
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

surface_pngs = [
    "textures/CHKWALL.png",
    "textures/CHKSHELF.png",
    "textures/CHKSTAF.png",
    "flats/CHKFLR.png",
    "flats/CHKCEIL.png",
]
world_sprite_pngs = [
    "sprites/COSHA0.png",
    "sprites/COFUA0.png",
    "sprites/COSTA0.png",
]
mop_sprite_pngs = [f"sprites/CMOP{frame}0.png" for frame in "ABCD"]
ripper_view_pngs = [f"sprites/RRPV{frame}0.png" for frame in "ABCDE"]
ripper_pickup_pngs = ["sprites/RRPKA0.png"]
manager_sprite_pngs = [f"sprites/MNGR{frame}0.png" for frame in "ABCDEFGHIJK"]
memo_sprite_pngs = [f"sprites/MEMO{frame}0.png" for frame in "ABCD"]
checkout_sprite_pngs = [f"sprites/SCKO{frame}0.png" for frame in "ABCDEFGHIJ"]
receipt_projectile_pngs = [f"sprites/RCPT{frame}0.png" for frame in "ABCD"]
required_pngs = (
    surface_pngs
    + world_sprite_pngs
    + mop_sprite_pngs
    + ripper_view_pngs
    + ripper_pickup_pngs
    + manager_sprite_pngs
    + memo_sprite_pngs
    + checkout_sprite_pngs
    + receipt_projectile_pngs
)

required_wavs = [
    "sounds/fuse.wav",
    "sounds/shutter.wav",
    "sounds/bossalarm.wav",
    "sounds/clockout.wav",
    "sounds/overtime.wav",
    "sounds/mopswing.wav",
    "sounds/managerattack.wav",
    "sounds/managerdown.wav",
    "sounds/ripperfire.wav",
    "sounds/rippercycle.wav",
    "sounds/checkoutidle.wav",
    "sounds/checkoutattack.wav",
    "sounds/checkouthit.wav",
    "sounds/checkoutdown.wav",
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
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Generated PNG is invalid: {rel}")
    width, height = struct.unpack(">II", data[16:24])
    if width < 32 or height < 32:
        raise SystemExit(f"Generated PNG is unexpectedly small: {rel} -> {width}x{height}")

sprite_pngs = (
    world_sprite_pngs
    + mop_sprite_pngs
    + ripper_view_pngs
    + ripper_pickup_pngs
    + manager_sprite_pngs
    + memo_sprite_pngs
    + checkout_sprite_pngs
    + receipt_projectile_pngs
)
for rel in sprite_pngs:
    data = (GAME / rel).read_bytes()
    offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
    if len(offsets) != 1 or len(offsets[0]) != 8:
        raise SystemExit(f"Sprite PNG is missing one valid ZDoom grAb offset chunk: {rel}")

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
for sprite in (
    "COFU A",
    "COST A",
    "CMOP A",
    "CMOP B",
    "CMOP C",
    "CMOP D",
    "RRPK A",
    "RRPV A",
    "RRPV C",
    "RRPV E",
    "MNGR A",
    "MNGR F",
    "MNGR K",
    "MEMO A",
    "MEMO D",
    "SCKO A",
    "SCKO F",
    "SCKO J",
    "RCPT A",
    "RCPT D",
):
    if sprite not in actors:
        raise SystemExit(f"Original sprite state missing: {sprite}")

mop_block = actors.split("actor EmergencyMop", 1)[1].split("actor ReceiptRipper", 1)[0]
if "PUNG" in mop_block:
    raise SystemExit("Emergency Mop still references the placeholder IWAD fist sprite")
if 'A_PlaySound("coh/mopswing"' not in mop_block:
    raise SystemExit("Emergency Mop original swing cue is not wired into its attack")

ripper_block = actors.split("actor ReceiptRipper", 1)[1].split("actor PriceGunSMG", 1)[0]
for marker in (
    "RRPK A -1",
    "RRPV A 1 A_WeaponReady",
    'A_PlaySound("coh/ripperfire"',
    'A_PlaySound("coh/rippercycle"',
    "A_FireBullets(7.0, 5.0, 9, 5",
):
    if marker not in ripper_block:
        raise SystemExit(f"Receipt Ripper signature presentation is incomplete: {marker}")
if "SHTG" in ripper_block:
    raise SystemExit("Receipt Ripper still references placeholder IWAD shotgun sprites")

checkout_block = actors.split("actor AngrySelfCheckout", 1)[1].split("actor CartOfDoom", 1)[0]
for marker in (
    "SCKO A 10 A_Look",
    'A_PlaySound("coh/checkoutattack"',
    'A_CustomMissile("CheckoutReceiptProjectile"',
    'PainSound "coh/checkouthit"',
    'DeathSound "coh/checkoutdown"',
):
    if marker not in checkout_block:
        raise SystemExit(f"Angry Self-Checkout signature presentation is incomplete: {marker}")
if "SPOS" in checkout_block:
    raise SystemExit("Angry Self-Checkout still references placeholder shotgun-guy sprites")

manager_block = actors.split("actor NightManager", 1)[1].split("actor ScannerTurret", 1)[0]
for marker in ("MNGR A 10 A_Look", 'A_CustomMissile("ManagerMemoProjectile"', 'A_PlaySound("coh/managerattack"', 'A_PlaySound("coh/managerdown"'):
    if marker not in manager_block:
        raise SystemExit(f"Night Manager signature presentation is incomplete: {marker}")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
if "COSH A -1" not in zscript:
    raise SystemExit("Original Staff Only shutter sprite state missing")
for cue in ("coh/overtime", "coh/clockout", "coh/bossalarm", "coh/shutter"):
    if cue not in zscript:
        raise SystemExit(f"Runtime cue is not wired into gameplay: {cue}")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
for cue in (
    "coh/fuse",
    "coh/shutter",
    "coh/bossalarm",
    "coh/clockout",
    "coh/overtime",
    "coh/mopswing",
    "coh/managerattack",
    "coh/managerdown",
    "coh/ripperfire",
    "coh/rippercycle",
    "coh/checkoutidle",
    "coh/checkoutattack",
    "coh/checkouthit",
    "coh/checkoutdown",
):
    if cue not in sndinfo:
        raise SystemExit(f"SNDINFO cue missing: {cue}")

print("Original asset contract: PASS")
print("Closing Time packages original retail surfaces plus Emergency Mop, Receipt Ripper, Angry Self-Checkout and Night Manager combat presentation.")