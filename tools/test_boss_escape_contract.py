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
things = [
    {
        "type": int(read_number(block, "type")),
        "x": read_number(block, "x"),
        "y": read_number(block, "y"),
    }
    for block in thing_blocks
]

boss_waves = [thing for thing in things if thing["type"] == 17103]
if len(boss_waves) != 2:
    raise SystemExit(f"Closing Time needs two boss-wave anchors, found {len(boss_waves)}")
expected_boss_wave_positions = {(-520.0, 240.0), (520.0, 240.0)}
actual_boss_wave_positions = {(thing["x"], thing["y"]) for thing in boss_waves}
if actual_boss_wave_positions != expected_boss_wave_positions:
    raise SystemExit(
        f"Boss-wave anchors must stay on the verified outer rear-handoff lanes: "
        f"{actual_boss_wave_positions} != {expected_boss_wave_positions}"
    )
if any(abs(thing["x"]) < 500.0 for thing in boss_waves):
    raise SystemExit("Boss-wave anchors must stay outside the rear objective breadcrumb corridor")
if any(thing["y"] < 220.0 for thing in boss_waves):
    raise SystemExit("Boss-wave anchors must remain on the rear management approach")

if '17103 = "CheckoutBossWaveSpawner"' not in MAPINFO:
    raise SystemExit("CheckoutBossWaveSpawner DoomEdNum is not registered")
if "class CheckoutBossWaveSpawner : Actor" not in ZSCRIPT:
    raise SystemExit("Boss-wave ZScript implementation is missing")
if 'CountInv("CheckoutFuse") < 3' not in ZSCRIPT:
    raise SystemExit("Boss-wave pressure must stay locked until full power is restored")

for enemy in ("AngrySelfCheckout", "CartOfDoom", "ScannerTurret", "PalletJack"):
    if f'Actor.Spawn("{enemy}", Pos)' not in ZSCRIPT:
        raise SystemExit(f"Boss-wave sequence is missing {enemy}")

# The tuned cadence deliberately leaves more room to read the supervisor and each reinforcement.
for threshold in (15, 34, 54, 76):
    if f"elapsed >= {threshold}" not in ZSCRIPT:
        raise SystemExit(f"Boss-wave sequence is missing the tuned {threshold}s stage")

if 'CountInv("SupervisorClearanceToken") > 0' not in ZSCRIPT:
    raise SystemExit("Boss-wave pressure must stop adding new threats after supervisor clearance")
if 'return "OBJECTIVE  RETURN TO FRONT CHECKOUT";' not in ZSCRIPT:
    raise SystemExit("HUD must send the player back to the front checkout after the boss")
if 'return "ROUTE: CLOCK OUT AT THE FRONT LANES";' not in ZSCRIPT:
    raise SystemExit("HUD route hint must point back to the front clock-out lane")
if "p.Pos.X >= -140" not in ZSCRIPT or "p.Pos.X <= 140" not in ZSCRIPT:
    raise SystemExit("Clock-out zone must stay centered on the front checkout")
if "p.Pos.Y <= -350" not in ZSCRIPT:
    raise SystemExit("Clock-out zone must remain in the front entrance area")
if "TIMECARD ACCEPTED - SHIFT COMPLETE" not in ZSCRIPT:
    raise SystemExit("Clock-out interaction needs explicit completion feedback")

print("Boss + escape contract: PASS")
print("Full power starts tuned staged outer-lane pressure; supervisor clearance requires a readable return to checkout.")
