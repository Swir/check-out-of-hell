from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
CORE_MAP = GAME / "MAP01.udmf"
ENV_MAP = GAME / "MAP01_ENVIRONMENT.udmf"
DECORATE_ENV = GAME / "DECORATE_ENVIRONMENT"
ZSCRIPT = GAME / "ZSCRIPT"
MAP_WAD = ROOT / "dist" / "MAP01.wad"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not MAP_WAD.exists() or not PK3.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")


def read_number(block: str, field: str) -> float:
    match = re.search(rf"\b{field}\s*=\s*(-?\d+(?:\.\d+)?)\s*;", block)
    if not match:
        raise SystemExit(f"Missing {field} in thing block: {block}")
    return float(match.group(1))


def parse_things(text: str):
    parsed = []
    for block in re.findall(r"thing\s*\{(.*?)\}", text, flags=re.DOTALL):
        parsed.append(
            {
                "type": int(read_number(block, "type")),
                "x": read_number(block, "x"),
                "y": read_number(block, "y"),
            }
        )
    return parsed


def positions(things, thing_type: int):
    return {(thing["x"], thing["y"]) for thing in things if thing["type"] == thing_type}


def read_textmap(path: Path) -> str:
    data = path.read_bytes()
    if data[:4] != b"PWAD":
        raise SystemExit("MAP01 build output is not a PWAD")
    lump_count, directory_offset = struct.unpack_from("<II", data, 4)
    for index in range(lump_count):
        entry = directory_offset + index * 16
        offset, size, raw_name = struct.unpack_from("<II8s", data, entry)
        name = raw_name.rstrip(b"\0").decode("ascii")
        if name == "TEXTMAP":
            return data[offset : offset + size].decode("utf-8")
    raise SystemExit("MAP01 build output has no TEXTMAP lump")


core_text = CORE_MAP.read_text(encoding="utf-8")
env_text = ENV_MAP.read_text(encoding="utf-8")
decorate_env = DECORATE_ENV.read_text(encoding="utf-8")
zscript = ZSCRIPT.read_text(encoding="utf-8")
core = parse_things(core_text)
environment = parse_things(env_text)

# The center strip is the player's strongest navigation line between the front registers and
# the rear objective. Initial combat must pressure its edges without standing directly on it.
initial_checkout_positions = positions(core, 17001)
expected_inner_checkouts = {(-220.0, 90.0), (220.0, 90.0)}
if not expected_inner_checkouts.issubset(initial_checkout_positions):
    raise SystemExit(
        "Closing Time inner Self-Checkout pair must remain flanked at x=+/-220, y=90"
    )

hostile_types = {17001, 17002, 17004, 17005}
centerline_hostiles = [
    thing
    for thing in core
    if thing["type"] in hostile_types
    and abs(thing["x"]) < 180.0
    and -300.0 < thing["y"] < 260.0
]
if centerline_hostiles:
    raise SystemExit(f"Initial hostile placement blocks the authored center strip: {centerline_hostiles}")

# Ambient Overtime pressure stays distributed around the floor rather than materializing in the
# front-to-rear centerline/clock-out approach.
expected_overtime = {(-330.0, 430.0), (700.0, 440.0), (500.0, -120.0)}
actual_overtime = positions(core, 17100)
if actual_overtime != expected_overtime:
    raise SystemExit(f"Unexpected Closing Time Overtime anchor layout: {actual_overtime}")
if any(abs(x) < 180.0 for x, _ in actual_overtime):
    raise SystemExit("An Overtime reinforcement anchor returned to the center navigation strip")

# The Night Manager response should flank the rear approach. Timing remains protected by the
# pacing contract; this contract protects only the authored spatial presentation.
expected_boss_waves = {(-430.0, 300.0), (430.0, 300.0)}
actual_boss_waves = positions(core, 17103)
if actual_boss_waves != expected_boss_waves:
    raise SystemExit(f"Unexpected Night Manager response anchor layout: {actual_boss_waves}")

# Twin Lane 06 signs frame the front approach without becoming cover or blocking the exit zone.
expected_lane_signs = {(-185.0, -430.0), (185.0, -430.0)}
actual_lane_signs = positions(environment, 17123)
if actual_lane_signs != expected_lane_signs:
    raise SystemExit(f"Closing Time front-lane wayfinding is not mirrored: {actual_lane_signs}")

try:
    lane_sign_block = decorate_env.split("actor CheckoutLaneSign 17123", 1)[1].split(
        "actor WetFloorCone 17124", 1
    )[0]
except IndexError as exc:
    raise SystemExit("CheckoutLaneSign actor boundaries missing") from exc
for marker in ("+NOBLOCKMAP", "+NOGRAVITY", "LSGN A -1 Bright"):
    if marker not in lane_sign_block:
        raise SystemExit(f"CheckoutLaneSign readability/safety marker missing: {marker}")

# Do not silently widen, move or automate the physical clock-out trigger while polishing sightlines.
for marker in (
    "p.Pos.X >= -140 && p.Pos.X <= 140 && p.Pos.Y <= -350",
    'powerPulseText = "TIMECARD ACCEPTED - SHIFT COMPLETE"',
):
    if marker not in zscript:
        raise SystemExit(f"Physical clock-out contract changed during readability pass: {marker}")

# Verify the built map contains exactly the same layout, not merely the source files.
built_things = parse_things(read_textmap(MAP_WAD))
if positions(built_things, 17100) != expected_overtime:
    raise SystemExit("Built MAP01 lost the flanked Overtime layout")
if positions(built_things, 17103) != expected_boss_waves:
    raise SystemExit("Built MAP01 lost the flanked management-response layout")
if positions(built_things, 17123) != expected_lane_signs:
    raise SystemExit("Built MAP01 lost the mirrored front-lane signs")

with zipfile.ZipFile(PK3, "r") as archive:
    if "maps/MAP01.wad" not in archive.namelist():
        raise SystemExit("Built PK3 missing MAP01")
    packaged_decorate = archive.read("DECORATE").decode("utf-8")
    for marker in ("actor CheckoutLaneSign 17123", "+NOBLOCKMAP", "LSGN A -1 Bright"):
        if marker not in packaged_decorate:
            raise SystemExit(f"Packaged DECORATE missing lane-sign marker: {marker}")

print("Closing Time combat readability contract: PASS")
print(
    "Center navigation strip stays clear of initial hostiles/reinforcement anchors; "
    "management waves flank the rear approach and mirrored non-blocking Lane 06 signs frame the exit lane."
)
