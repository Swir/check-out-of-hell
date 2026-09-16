from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAP01 = (ROOT / "game" / "MAP01.udmf").read_text(encoding="utf-8")
MAPINFO = (ROOT / "game" / "MAPINFO").read_text(encoding="utf-8")
ZSCRIPT = (ROOT / "game" / "ZSCRIPT").read_text(encoding="utf-8")


def read_number(block: str, field: str) -> float:
    match = re.search(rf"\b{field}\s*=\s*(-?\d+(?:\.\d+)?)\s*;", block)
    if not match:
        raise SystemExit(f"Missing {field} in thing block: {block}")
    return float(match.group(1))


thing_blocks = re.findall(r"thing\s*\{(.*?)\}", MAP01, flags=re.DOTALL)
things = []
for block in thing_blocks:
    things.append(
        {
            "type": int(read_number(block, "type")),
            "x": read_number(block, "x"),
            "y": read_number(block, "y"),
        }
    )

vertices = [
    (float(x), float(y))
    for x, y in re.findall(
        r"vertex\s*\{\s*x\s*=\s*(-?\d+(?:\.\d+)?)\s*;\s*y\s*=\s*(-?\d+(?:\.\d+)?)\s*;\s*\}",
        MAP01,
    )
]
if not vertices:
    raise SystemExit("MAP01 has no vertices")

xs = [x for x, _ in vertices]
ys = [y for _, y in vertices]
if max(xs) - min(xs) < 1400 or max(ys) - min(ys) < 900:
    raise SystemExit("Closing Time floor is too small for the structured prototype layout")

if MAP01.count("sideback =") < 5:
    raise SystemExit("Closing Time needs at least five internal aisle/counter barriers")

players = [thing for thing in things if thing["type"] == 1]
if len(players) != 1 or players[0]["y"] > -350:
    raise SystemExit("Closing Time player start must remain in the front entrance zone")

fuses = [thing for thing in things if thing["type"] == 17111]
if len(fuses) != 3:
    raise SystemExit(f"Closing Time must contain exactly three breaker fuses, found {len(fuses)}")
if min(thing["x"] for thing in fuses) > -500:
    raise SystemExit("A breaker fuse must pull the player into the left department lane")
if max(thing["x"] for thing in fuses) < 500:
    raise SystemExit("A breaker fuse must pull the player into the right department lane")
if max(thing["y"] for thing in fuses) < 400:
    raise SystemExit("A breaker fuse must pull the player into the rear staff zone")

manager_spawners = [thing for thing in things if thing["type"] == 17101]
if len(manager_spawners) != 1:
    raise SystemExit("Closing Time must contain one gated Night Manager spawner")
if any(thing["type"] == 17003 for thing in things):
    raise SystemExit("Night Manager must not exist in MAP01 before power restoration")

if len([thing for thing in things if thing["type"] == 17100]) < 3:
    raise SystemExit("Closing Time must keep Overtime pressure active across the larger floor")

if '17101 = "CheckoutManagerSpawner"' not in MAPINFO:
    raise SystemExit("CheckoutManagerSpawner DoomEdNum is not registered")
if "class CheckoutManagerSpawner : Actor" not in ZSCRIPT:
    raise SystemExit("CheckoutManagerSpawner ZScript implementation is missing")
if 'CountInv("CheckoutFuse") < 3' not in ZSCRIPT:
    raise SystemExit("Night Manager spawner must remain gated behind all three breakers")

print("Closing Time layout contract: PASS")
print("MAP01 has separated breaker routes, internal retail barriers and a power-gated supervisor.")
