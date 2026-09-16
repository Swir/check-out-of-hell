from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ZSCRIPT = (ROOT / "game" / "ZSCRIPT").read_text(encoding="utf-8")
DECORATE = (ROOT / "game" / "DECORATE").read_text(encoding="utf-8")
MAPINFO = (ROOT / "game" / "MAPINFO").read_text(encoding="utf-8")

thresholds = [int(value) for value in re.findall(r"seconds >= (\d+)", ZSCRIPT)]
if thresholds != [270, 180, 90]:
    raise SystemExit(f"Unexpected Overtime thresholds: {thresholds}")

for stage_name in ("SHIFT ACTIVE", "STORE UNSTABLE", "OVERTIME", "HELL RUSH"):
    if stage_name not in ZSCRIPT:
        raise SystemExit(f"Missing Overtime stage label: {stage_name}")

if "Inventory.MaxAmount 3" not in DECORATE:
    raise SystemExit("CheckoutFuse must cap at three breakers")

if "next = \"MAP02\"" not in MAPINFO or "next = \"MAP01\"" not in MAPINFO:
    raise SystemExit("Prototype map loop is not connected")

if "bossCleared && fuses >= 3" not in ZSCRIPT:
    raise SystemExit("Level exit must require both the supervisor and three breakers")

print("Gameplay contract test: PASS")
