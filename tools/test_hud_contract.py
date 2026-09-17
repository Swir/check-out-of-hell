from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")

required = (
    "static String GetPressureMeter(int stage)",
    "static String GetObjectiveText(int fuses, bool cleared, bool clockingOut)",
    "static String GetObjectiveHint(int fuses, bool cleared)",
    'OBJECTIVE  RESTORE BREAKERS  %d/3',
    'OBJECTIVE  CLEAR THE SUPERVISOR',
    'OBJECTIVE  RETURN TO FRONT CHECKOUT',
    'OBJECTIVE  TIMECARD ACCEPTED',
    'CLOCK-OUT TARGET 06:00',
    'PRESSURE [----]',
    'PRESSURE [#---]',
    'PRESSURE [###-]',
    'PRESSURE [####]',
    'ROUTE: STAFF ONLY ACCESS IS NOW POWERED',
    'WORKER HP  %03d',
    'RESERVES  LABELS %03d  RECEIPTS %02d  CANS %02d',
    'WORKER CONDITION: CRITICAL',
    'p.CountInv("Clip")',
    'p.CountInv("Shell")',
    'p.CountInv("RocketAmmo")',
)

for marker in required:
    if marker not in zscript:
        raise SystemExit(f"Final HUD contract missing: {marker}")

# The final layout must communicate Overtime through words/patterns as well as color.
for label in ("SHIFT ACTIVE", "STORE UNSTABLE", "OVERTIME", "HELL RUSH"):
    if label not in zscript:
        raise SystemExit(f"Overtime text label missing from HUD: {label}")

# Ensure the old tall status stack is no longer the primary objective presentation.
for obsolete in (
    'taskText = "TASK: RESTORE ALL BREAKERS"',
    'taskText = "TASK: CLEAR THE SUPERVISOR"',
    'bossText = "SUPERVISOR ACTIVE"',
):
    if obsolete in zscript:
        raise SystemExit(f"Legacy HUD stack leaked into final layout: {obsolete}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    if "ZSCRIPT" not in names:
        raise SystemExit("Final HUD ZSCRIPT is missing from the built PK3")
    packed = archive.read("ZSCRIPT").decode("utf-8")
    for marker in ("CLOCK-OUT TARGET 06:00", "WORKER CONDITION: CRITICAL", "PRESSURE [####]"):
        if marker not in packed:
            raise SystemExit(f"Built PK3 is missing final HUD marker: {marker}")

print("Final HUD contract: PASS")
print("Objective hierarchy, Overtime pressure, worker health and signature weapon reserves are packaged and readable without color-only cues.")
