from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ZSCRIPT = ROOT / "game" / "ZSCRIPT"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

source = ZSCRIPT.read_text(encoding="utf-8")

world_loaded = re.search(
    r"override\s+void\s+WorldLoaded\(WorldEvent\s+e\)\s*\{(.*?)\n\s*\}\n\n\s*override\s+void\s+WorldThingDied",
    source,
    re.DOTALL,
)
if not world_loaded:
    raise SystemExit("Could not locate CheckoutShiftDirector.WorldLoaded")

loaded_body = world_loaded.group(1)
save_guard = loaded_body.find("if (e.IsSaveGame)")
reset_marker = loaded_body.find("bossCleared = false;")
if save_guard < 0:
    raise SystemExit("WorldLoaded must explicitly preserve serialized state when e.IsSaveGame is true")
if reset_marker < 0 or save_guard > reset_marker:
    raise SystemExit("The save-game guard must run before fresh-map state is reset")
if "freshWorldInitPending = true;" not in loaded_body:
    raise SystemExit("Fresh maps must schedule a department-local inventory reset")

for marker in (
    'p.A_TakeInventory("CheckoutFuse", 3);',
    'p.A_TakeInventory("SupervisorClearanceToken", 1);',
    "freshWorldInitPending = false;",
):
    if marker not in source:
        raise SystemExit(f"Fresh-map carry-over protection missing: {marker}")

if 'p.CountInv("SupervisorClearanceToken") > 0' not in source or "bossCleared = true;" not in source:
    raise SystemExit("Supervisor-clear state must be recoverable from serialized player inventory")

thing_died = re.search(
    r"override\s+void\s+WorldThingDied\(WorldEvent\s+e\)\s*\{(.*?)\n\s*\}\n\n\s*override\s+void\s+WorldTick",
    source,
    re.DOTALL,
)
if not thing_died:
    raise SystemExit("Could not locate CheckoutShiftDirector.WorldThingDied")
if 'p.A_GiveInventory("SupervisorClearanceToken", 1);' not in thing_died.group(1):
    raise SystemExit("Boss death must persist supervisor clearance immediately for save/load safety")

with zipfile.ZipFile(PK3, "r") as archive:
    packaged = archive.read("ZSCRIPT").decode("utf-8")
    for marker in (
        "if (e.IsSaveGame)",
        "freshWorldInitPending",
        'A_TakeInventory("CheckoutFuse", 3)',
        'A_TakeInventory("SupervisorClearanceToken", 1)',
    ):
        if marker not in packaged:
            raise SystemExit(f"Packaged ZSCRIPT missing save/load marker: {marker}")

print("Save/load state contract: PASS")
print("Save restores preserve serialized shift state, while fresh departments reset breaker/supervisor carry-over before objective logic runs.")
