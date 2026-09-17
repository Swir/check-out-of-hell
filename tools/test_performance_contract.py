from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
docs = (ROOT / "docs" / "PERFORMANCE.md").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")


def class_block(text: str, class_name: str) -> str:
    marker = f"class {class_name} :"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"Missing ZScript class: {class_name}")

    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"Malformed ZScript class: {class_name}")

    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise AssertionError(f"Unterminated ZScript class: {class_name}")


poll_intervals = {
    "CheckoutOvertimeSpawner": 7,
    "CheckoutManagerSpawner": 7,
    "CheckoutBossWaveSpawner": 4,
    "CheckoutStaffShutter": 7,
    "CheckoutFullPowerCacheSpawner": 7,
    "CheckoutRegionalManagerSpawner": 7,
}

for class_name, interval in poll_intervals.items():
    block = class_block(zscript, class_name)
    # The time guard can share an `if` condition with a one-shot lifecycle flag; protect the
    # actual bounded polling predicate rather than one exact formatting shape.
    for marker in (
        "int nextCheck;",
        "Level.maptime < nextCheck",
        f"nextCheck = Level.maptime + {interval};",
    ):
        if marker not in block:
            raise SystemExit(f"{class_name}: sparse-poll marker missing: {marker}")

# One-shot/finished watchers must remove their thinker instead of idling forever.
for class_name in (
    "CheckoutManagerSpawner",
    "CheckoutBossWaveSpawner",
    "CheckoutStaffShutter",
    "CheckoutFullPowerCacheSpawner",
    "CheckoutRegionalManagerSpawner",
):
    if "Destroy();" not in class_block(zscript, class_name):
        raise SystemExit(f"{class_name}: completed watcher does not self-destroy")

overtime = class_block(zscript, "CheckoutOvertimeSpawner")
if 'p.CountInv("SupervisorClearanceToken") > 0' not in overtime or "Destroy();" not in overtime:
    raise SystemExit("Overtime watcher must retire after supervisor clearance")

boss_waves = class_block(zscript, "CheckoutBossWaveSpawner")
if 'p.CountInv("SupervisorClearanceToken") > 0' not in boss_waves:
    raise SystemExit("Boss-wave watcher must stop immediately after supervisor clearance")

# Performance work may not silently retime the authored encounter.
for marker in (
    "nextSpawn = Level.maptime + 35 * 55;",
    "nextSpawn = Level.maptime + 35 * 38;",
    "nextSpawn = Level.maptime + 35 * 25;",
    "elapsed >= 15",
    "elapsed >= 34",
    "elapsed >= 54",
    "elapsed >= 76",
):
    if marker not in zscript:
        raise SystemExit(f"Authored combat cadence changed or disappeared: {marker}")

for marker in (
    "worst-case trigger latency stays below **0.2 seconds**",
    "does **not** claim a specific FPS uplift",
    "interactive target-Windows playtest",
    "Overtime/Hell Rush",
):
    if marker not in docs:
        raise SystemExit(f"Performance documentation marker missing: {marker}")

if "python tools/test_performance_contract.py" not in workflow:
    raise SystemExit("Performance contract is not wired into GitHub Actions")

# A simple deterministic budget model: one instance of each watcher used to evaluate its
# gate every 35-Hz tic. Sparse polling must reduce that gate-check rate by at least 80%.
baseline_checks_per_second = 35.0 * len(poll_intervals)
hardened_checks_per_second = sum(35.0 / interval for interval in poll_intervals.values())
reduction = 1.0 - (hardened_checks_per_second / baseline_checks_per_second)
if reduction < 0.80:
    raise SystemExit(
        f"Sparse polling budget regressed: only {reduction * 100:.1f}% modeled reduction"
    )

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    if "ZSCRIPT" not in names:
        raise SystemExit("Built PK3 missing ZSCRIPT")
    packed = archive.read("ZSCRIPT").decode("utf-8")

    for class_name, interval in poll_intervals.items():
        block = class_block(packed, class_name)
        if f"nextCheck = Level.maptime + {interval};" not in block:
            raise SystemExit(f"Packaged {class_name} missing sparse polling interval")

    if "Destroy();" not in class_block(packed, "CheckoutManagerSpawner"):
        raise SystemExit("Packaged one-shot watcher cleanup missing")

print("Performance hardening contract: PASS")
print(
    "Modeled gate-check budget for one instance of each watcher: "
    f"{baseline_checks_per_second:.0f}/s -> {hardened_checks_per_second:.2f}/s "
    f"({reduction * 100:.1f}% reduction), with authored combat cadence preserved."
)
