from pathlib import Path
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

manager_pngs = [f"sprites/RMGR{frame}0.png" for frame in "ABCDEFGHIJKLMNO"]
red_tape_pngs = [f"sprites/RTAP{frame}0.png" for frame in "ABCD"]
stamp_pngs = [f"sprites/STMP{frame}0.png" for frame in "ABCD"]
required_pngs = manager_pngs + red_tape_pngs + stamp_pngs
required_wavs = [
    "sounds/regionalidle.wav",
    "sounds/regionalattack.wav",
    "sounds/regionalphase.wav",
    "sounds/regionalstamp.wav",
    "sounds/regionalhit.wav",
    "sounds/regionaldown.wav",
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
        raise SystemExit(f"Generated Regional Manager sprite missing: {rel}")
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Generated Regional Manager PNG is invalid: {rel}")
    width, height = struct.unpack(">II", data[16:24])
    if width < 32 or height < 32:
        raise SystemExit(f"Generated Regional Manager PNG is unexpectedly small: {rel} -> {width}x{height}")
    offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
    if len(offsets) != 1 or len(offsets[0]) != 8:
        raise SystemExit(f"Regional Manager sprite is missing one valid ZDoom grAb chunk: {rel}")

for rel in required_wavs:
    path = GAME / rel
    if not path.exists():
        raise SystemExit(f"Generated Regional Manager cue missing: {rel}")
    with wave.open(str(path), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise SystemExit(f"Generated Regional Manager WAV format is invalid: {rel}")
        if stream.getframerate() != 22050 or stream.getnframes() < 4000:
            raise SystemExit(f"Generated Regional Manager WAV duration/rate is invalid: {rel}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    missing = set(required_pngs + required_wavs) - names
    if missing:
        raise SystemExit(f"Regional Manager runtime assets missing from PK3: {sorted(missing)}")

actors = (GAME / "DECORATE").read_text(encoding="utf-8")
manager_block = actors.split("actor RegionalManager", 1)[1].split("actor PrototypeCanLauncherPickup", 1)[0]
for marker in (
    "RMGR A 10 A_Look",
    "RMGR D 4 A_Chase",
    'A_JumpIfHealthLower(550, "MissileRage")',
    'A_CustomMissile("CorporateRedTapeProjectile"',
    'A_CustomMissile("ExecutiveStampProjectile"',
    'A_PlaySound("coh/regionalphase"',
    'A_PlaySound("coh/regionalstamp"',
    'PainSound "coh/regionalhit"',
    'DeathSound "coh/regionaldown"',
    "RMGR O -1",
):
    if marker not in manager_block:
        raise SystemExit(f"Regional Manager original boss presentation is incomplete: {marker}")
if "CYBR" in manager_block:
    raise SystemExit("Regional Manager still references compatible-IWAD Cyberdemon sprite states")

for actor_name in ("CorporateRedTapeProjectile", "ExecutiveStampProjectile"):
    if f"actor {actor_name}" not in actors:
        raise SystemExit(f"Regional Manager custom projectile missing: {actor_name}")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
for cue in (
    "coh/regionalidle",
    "coh/regionalattack",
    "coh/regionalphase",
    "coh/regionalstamp",
    "coh/regionalhit",
    "coh/regionaldown",
):
    if cue not in sndinfo:
        raise SystemExit(f"Regional Manager SNDINFO cue missing: {cue}")

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_regional_manager_assets import generate_regional_manager_assets",
    "generate_regional_manager_assets(GAME)",
):
    if marker not in build:
        raise SystemExit(f"Regional Manager generator is not wired into the build: {marker}")

mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
if '17104 = "WarehouseRegionalManagerArrivalSpawner"' not in mapinfo:
    raise SystemExit("Warehouse 13.5 Regional Manager arrival spawner DoomEdNum is missing")
if '17104 = "CheckoutRegionalManagerSpawner"' in mapinfo:
    raise SystemExit("Warehouse 13.5 still maps the legacy instant Regional Manager spawner")

warehouse = (GAME / "ZSCRIPT_WAREHOUSE").read_text(encoding="utf-8")
for marker in (
    "class WarehouseRegionalManagerArrivalSpawner : Actor",
    'p.CountInv("WarehouseDepartmentToken") < 1',
    'p.CountInv("CheckoutFuse") < 3',
    'p.CountInv("WarehouseLiftOverride") < 1',
    'p.CountInv("SupervisorClearanceToken") > 0',
    "arrivalTic = Level.maptime + 35 * 4",
    'Actor.Spawn("OvertimeWarningFlash", Pos)',
    'p.A_StartSound("coh/regionalphase", CHAN_AUTO)',
    'Actor.Spawn("TeleportFog", Pos)',
    'Actor manager = Actor.Spawn("RegionalManager", Pos)',
):
    if marker not in warehouse:
        raise SystemExit(f"Regional Manager warned-arrival logic is incomplete: {marker}")

map02 = (GAME / "MAP02.udmf").read_text(encoding="utf-8")
if "type = 17104" not in map02:
    raise SystemExit("Warehouse 13.5 is missing the Regional Manager warned-arrival spawner")
if "type = 17006" in map02:
    raise SystemExit("Warehouse 13.5 still pre-places the Regional Manager before lift activation")
for surface in ('texturefloor = "CHKFLR"', 'textureceiling = "CHKCEIL"', 'texturemiddle = "CHKWALL"'):
    if surface not in map02:
        raise SystemExit(f"Warehouse 13.5 still lacks project-owned retail surface use: {surface}")

print("Regional Manager boss contract: PASS")
print("Regional Manager uses project-owned generated presentation, a two-phase attack kit and a warned four-second Warehouse arrival after the breaker + lift gate.")
