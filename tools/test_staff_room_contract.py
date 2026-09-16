from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAP01 = (ROOT / "game" / "MAP01.udmf").read_text(encoding="utf-8")
MAPINFO = (ROOT / "game" / "MAPINFO").read_text(encoding="utf-8")
ZSCRIPT = (ROOT / "game" / "ZSCRIPT").read_text(encoding="utf-8")
DECORATE = (ROOT / "game" / "DECORATE").read_text(encoding="utf-8")


def read_number(block: str, field: str) -> float:
    match = re.search(rf"\b{field}\s*=\s*(-?\d+(?:\.\d+)?)\s*;", block)
    if not match:
        raise SystemExit(f"Missing {field} in thing block: {block}")
    return float(match.group(1))


thing_blocks = re.findall(r"thing\s*\{(.*?)\}", MAP01, flags=re.DOTALL)
things = [
    {
        "type": int(read_number(block, "type")),
        "x": read_number(block, "x"),
        "y": read_number(block, "y"),
    }
    for block in thing_blocks
]

shutters = [thing for thing in things if thing["type"] == 17102]
if len(shutters) != 3:
    raise SystemExit(f"Staff Only entrance must use three visible shutter blockers, found {len(shutters)}")
if not all(-560 <= thing["x"] <= -464 and 240 <= thing["y"] <= 260 for thing in shutters):
    raise SystemExit("Staff Only shutter blockers are not aligned with the rear-left doorway")

stashes = [thing for thing in things if thing["type"] == 17112]
if len(stashes) != 1:
    raise SystemExit(f"Closing Time must contain exactly one optional staff-room stash, found {len(stashes)}")
stash = stashes[0]
if not (stash["x"] < -560 and stash["y"] > 250):
    raise SystemExit("Staff-room stash must sit inside the gated rear-left side room")

fuses = [thing for thing in things if thing["type"] == 17111]
if any(thing["x"] < -560 and thing["y"] > 250 for thing in fuses):
    raise SystemExit("The optional Staff Only room must not contain a mandatory breaker fuse")

if '17102 = "CheckoutStaffShutter"' not in MAPINFO:
    raise SystemExit("CheckoutStaffShutter DoomEdNum is not registered")
if "class CheckoutStaffShutter : Actor" not in ZSCRIPT:
    raise SystemExit("Powered Staff Only shutter implementation is missing")
if 'CountInv("CheckoutFuse") < 2' not in ZSCRIPT:
    raise SystemExit("Staff Only shutter must remain locked until two breakers are restored")
if "STAFF SECURITY ONLINE" not in ZSCRIPT:
    raise SystemExit("Breaker feedback must announce when staff security receives power")
if "FULL POWER - SUPERVISOR ACCESS RESTORED" not in ZSCRIPT:
    raise SystemExit("Breaker feedback must visibly acknowledge full power restoration")
if "actor StaffRoomStash : Backpack 17112" not in DECORATE:
    raise SystemExit("Optional staff-room reward actor is missing")
if "Payroll does not need to know" not in DECORATE:
    raise SystemExit("Staff-room reward is missing its workplace-comedy pickup message")

print("Staff Only route contract: PASS")
print("Two breakers unlock an optional rear-left reward room without gating the third breaker.")
