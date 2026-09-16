from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ZSCRIPT = (ROOT / "game" / "ZSCRIPT").read_text(encoding="utf-8")
DECORATE = (ROOT / "game" / "DECORATE").read_text(encoding="utf-8")
MAPINFO = (ROOT / "game" / "MAPINFO").read_text(encoding="utf-8")
MAP01 = (ROOT / "game" / "MAP01.udmf").read_text(encoding="utf-8")

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
    raise SystemExit("Clock-out must require both the supervisor and three breakers")
if 'taskText = "TASK: RETURN TO FRONT CHECKOUT"' not in ZSCRIPT:
    raise SystemExit("Completed combat must send the player back to the front checkout")
if "TIMECARD ACCEPTED - SHIFT COMPLETE" not in ZSCRIPT:
    raise SystemExit("Clock-out zone must acknowledge successful shift completion")

if "class CheckoutManagerSpawner : Actor" not in ZSCRIPT:
    raise SystemExit("Closing Time needs a staged supervisor spawner")
if 'CountInv("CheckoutFuse") < 3' not in ZSCRIPT:
    raise SystemExit("Night Manager must remain locked until all breakers are restored")
if 'Actor.Spawn("NightManager", Pos)' not in ZSCRIPT:
    raise SystemExit("Staged supervisor spawner does not create Night Manager")
if '"SUPERVISOR LOCKED"' not in ZSCRIPT:
    raise SystemExit("HUD must explain the supervisor power gate")
if 'taskText = "TASK: RESTORE ALL BREAKERS"' not in ZSCRIPT:
    raise SystemExit("HUD must expose the current restoration task")

if MAP01.count("type = 17101") != 1 or "type = 17003" in MAP01:
    raise SystemExit("MAP01 must stage Night Manager instead of pre-placing the boss")

print("Gameplay contract test: PASS")
