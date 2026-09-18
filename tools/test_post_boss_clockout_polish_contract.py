from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAP_WAD = ROOT / "dist" / "MAP01.wad"


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

build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
for marker in (
    "from generate_clockout_assets import generate_clockout_assets",
    "generate_clockout_assets(GAME)",
    'GAME / "ZSCRIPT_CLOCKOUT"',
):
    if marker not in build:
        raise SystemExit(f"Clock-out polish is not wired into the build: {marker}")

sprite = GAME / "sprites" / "COUTA0.png"
if not sprite.exists():
    raise SystemExit("Generated CLOCK OUT guide sprite is missing")
data = sprite.read_bytes()
if not data.startswith(b"\x89PNG\r\n\x1a\n"):
    raise SystemExit("CLOCK OUT guide is not a PNG")
offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
if len(offsets) != 1 or len(offsets[0]) != 8:
    raise SystemExit("CLOCK OUT guide sprite must contain exactly one valid grAb chunk")

actor_text = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
for marker in (
    "actor CheckoutClockOutGuide",
    "+NOBLOCKMAP",
    "+NOGRAVITY",
    "COUT A 24 Bright",
    "COUT A 12",
):
    if marker not in actor_text:
        raise SystemExit(f"CLOCK OUT guide presentation contract missing: {marker}")

logic = (GAME / "ZSCRIPT_CLOCKOUT").read_text(encoding="utf-8")
try:
    guide_block = logic.split("class CheckoutClockOutGuideSpawner : Actor", 1)[1]
except IndexError as exc:
    raise SystemExit("CheckoutClockOutGuideSpawner class missing") from exc
for marker in (
    'p.CountInv("SupervisorClearanceToken") == 0',
    'Actor.Spawn("CheckoutClockOutGuide", Pos)',
    "Destroy();",
    "nextCheck = Level.maptime + 7",
):
    if marker not in guide_block:
        raise SystemExit(f"Post-boss guide lifecycle contract missing: {marker}")

mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
if '17132 = "CheckoutClockOutGuideSpawner"' not in mapinfo:
    raise SystemExit("Clock-out guide DoomEdNum 17132 is not registered")

map_layer = (GAME / "MAP01_ENVIRONMENT.udmf").read_text(encoding="utf-8")
if map_layer.count("type = 17132") != 1:
    raise SystemExit("Closing Time must contain exactly one post-boss clock-out guide anchor")
if "x = 0.0; y = -315.0" not in map_layer:
    raise SystemExit("Clock-out guide anchor moved away from the authored front-lane approach")
if "type = 17132" in (GAME / "MAP01_OVERTIME.udmf").read_text(encoding="utf-8"):
    raise SystemExit("Clock-out guide must stay in the environment layer, not the hazard layer")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    if "sprites/COUTA0.png" not in names:
        raise SystemExit("Packaged PK3 missing generated CLOCK OUT guide sprite")
    decorate = archive.read("DECORATE").decode("utf-8")
    zscript = archive.read("ZSCRIPT").decode("utf-8")
    if "actor CheckoutClockOutGuide" not in decorate:
        raise SystemExit("Packaged DECORATE missing clock-out guide actor")
    if "class CheckoutClockOutGuideSpawner : Actor" not in zscript:
        raise SystemExit("Packaged ZSCRIPT missing clock-out guide spawner")

wad_text = MAP_WAD.read_bytes()
if b"type = 17132" not in wad_text:
    raise SystemExit("Built MAP01 does not contain the post-boss clock-out guide anchor")

print("Closing Time post-boss clock-out polish contract: PASS")
print("Supervisor clearance reveals one original front-lane CLOCK OUT guide while the physical completion trigger remains unchanged.")
