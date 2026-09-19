from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAP_WAD = ROOT / "dist" / "MAP01.wad"

if not PK3.exists() or not MAP_WAD.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
zscript_clockout = (GAME / "ZSCRIPT_CLOCKOUT").read_text(encoding="utf-8")
decorate_env = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
map01 = (GAME / "MAP01.udmf").read_text(encoding="utf-8")
environment = (GAME / "MAP01_ENVIRONMENT.udmf").read_text(encoding="utf-8")

# A cleared supervisor must stop both ambient Overtime reinforcements and the staged
# management-response waves, so the return-to-checkout leg remains tense but readable.
for marker in (
    'p.A_GiveInventory("SupervisorClearanceToken", 1)',
    'p.CountInv("SupervisorClearanceToken") > 0',
):
    if marker not in zscript:
        raise SystemExit(f"Closing Time post-boss pacing guard missing: {marker}")

# Keep the boss-wave check scoped to its own class. The implementation may split the fuse
# and clearance guards so a cleared watcher can self-destroy instead of idling forever.
try:
    boss_wave_block = zscript.split("class CheckoutBossWaveSpawner : Actor", 1)[1].split(
        "class CheckoutStaffShutter : Actor", 1
    )[0]
except IndexError as exc:
    raise SystemExit("CheckoutBossWaveSpawner class boundaries missing") from exc

for marker in (
    'p.CountInv("CheckoutFuse") < 3',
    'p.CountInv("SupervisorClearanceToken") > 0',
):
    if marker not in boss_wave_block:
        raise SystemExit(f"Closing Time boss-wave guard missing: {marker}")

# Boss additions are deliberately spaced farther apart than the previous prototype cadence.
for marker in (
    "elapsed >= 15",
    "elapsed >= 34",
    "elapsed >= 54",
    "elapsed >= 76",
):
    if marker not in zscript:
        raise SystemExit(f"Closing Time boss-wave pacing marker missing: {marker}")

# Full power must provide exactly one guaranteed recovery point before the supervisor arena.
for marker in (
    "class CheckoutFullPowerCacheSpawner : Actor",
    'p.CountInv("CheckoutFuse") < 3',
    'Actor.Spawn("CheckoutPowerCache", Pos)',
):
    if marker not in zscript:
        raise SystemExit(f"Full-power cache ZScript contract missing: {marker}")
if '17128 = "CheckoutFullPowerCacheSpawner"' not in mapinfo:
    raise SystemExit("Full-power cache DoomEdNum 17128 is not registered")

if environment.count("type = 17128") != 1:
    raise SystemExit("Closing Time must contain exactly one full-power cache spawner")
if "x = 0.0; y = 250.0" not in environment:
    raise SystemExit("Full-power cache moved away from the deliberate pre-boss approach position")

for marker in (
    "actor SupervisorClearanceToken : Inventory",
    "Inventory.MaxAmount 1",
    "actor CheckoutPowerCache : Backpack",
    'Tag "Full-Power Emergency Cache"',
    'Inventory.PickupSound "coh/breaksnack"',
    "BOXE A -1 Bright",
):
    if marker not in decorate_env:
        raise SystemExit(f"Closing Time pacing inventory actor contract missing: {marker}")

# Deep Overtime now changes Closing Time navigation as well as enemy/hazard pressure. One
# explicitly off-center lane can close for five seconds, but only after two restored breakers,
# Overtime stage 2, and a two-second warning. Supervisor clearance must cancel an armed lock.
if '17156 = "ClosingTimeLockdownSpawner"' not in mapinfo:
    raise SystemExit("Closing Time lockdown DoomEdNum 17156 is not registered")
if map01.count("type = 17156") != 1:
    raise SystemExit("Closing Time must contain exactly one Overtime lockdown anchor")

lock_match = re.search(
    r"thing\s*\{\s*x\s*=\s*(-?\d+(?:\.\d+)?);\s*y\s*=\s*(-?\d+(?:\.\d+)?);[^}]*type\s*=\s*17156;",
    map01,
    re.DOTALL,
)
if not lock_match:
    raise SystemExit("Closing Time lockdown anchor coordinates could not be parsed")
lock_x = float(lock_match.group(1))
lock_y = float(lock_match.group(2))
if abs(lock_x) < 400:
    raise SystemExit("Closing Time lockdown anchor must stay outside the central navigation corridor")
if lock_y <= -350:
    raise SystemExit("Closing Time lockdown anchor must stay away from the physical clock-out trigger")

try:
    lockdown_block = zscript_clockout.split("class ClosingTimeLockdownSpawner : Actor", 1)[1]
except IndexError as exc:
    raise SystemExit("ClosingTimeLockdownSpawner class missing") from exc
for marker in (
    'p.CountInv("SupervisorClearanceToken") > 0',
    'p.CountInv("CheckoutFuse") < 2',
    "overtimeStage < 2",
    'Actor.Spawn("OvertimeWarningFlash", Pos)',
    "closeTic = Level.maptime + 35 * 2",
    'Actor.Spawn("ClosingTimeOvertimeShutter", Pos)',
    "delaySeconds = 28",
    "delaySeconds = 20",
    "nextLockTic = Level.maptime + 35 * 14",
):
    if marker not in lockdown_block:
        raise SystemExit(f"Closing Time lockdown contract missing: {marker}")

try:
    shutter_block = decorate_env.split("actor ClosingTimeOvertimeShutter", 1)[1]
except IndexError as exc:
    raise SystemExit("ClosingTimeOvertimeShutter actor missing") from exc
for marker in (
    'Tag "Closing Time Overtime Shutter"',
    "Radius 96",
    "Height 72",
    "+SOLID",
    'A_PlaySound("coh/shutter", CHAN_BODY)',
    "COSH A 175 Bright",
):
    if marker not in shutter_block:
        raise SystemExit(f"Closing Time lockdown shutter contract missing: {marker}")

with zipfile.ZipFile(PK3, "r") as archive:
    zscript_pk3 = archive.read("ZSCRIPT").decode("utf-8")
    decorate_pk3 = archive.read("DECORATE").decode("utf-8")
    mapinfo_pk3 = archive.read("MAPINFO").decode("utf-8")
    for marker in ("SupervisorClearanceToken", "CheckoutFullPowerCacheSpawner", "ClosingTimeLockdownSpawner"):
        if marker not in zscript_pk3:
            raise SystemExit(f"Packaged ZSCRIPT missing pacing system marker: {marker}")
    for marker in ("SupervisorClearanceToken", "CheckoutPowerCache", "ClosingTimeOvertimeShutter"):
        if marker not in decorate_pk3:
            raise SystemExit(f"Packaged DECORATE missing pacing actor marker: {marker}")
    if '17156 = "ClosingTimeLockdownSpawner"' not in mapinfo_pk3:
        raise SystemExit("Packaged MAPINFO missing Closing Time lockdown registration")

wad_text = MAP_WAD.read_bytes()
if b"type = 17128" not in wad_text:
    raise SystemExit("Built MAP01 does not contain the full-power cache spawner")
if b"type = 17156" not in wad_text:
    raise SystemExit("Built MAP01 does not contain the Overtime lockdown anchor")

print("Closing Time pacing contract: PASS")
print("Full power grants one pre-boss cache; boss waves stay spaced; deep Overtime can briefly lock one side lane while the central clock-out route remains open.")
