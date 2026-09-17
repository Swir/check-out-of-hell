from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAP_WAD = ROOT / "dist" / "MAP01.wad"

if not PK3.exists() or not MAP_WAD.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

decorate = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
layer = (GAME / "MAP01_ENVIRONMENT.udmf").read_text(encoding="utf-8")
core_map = (GAME / "MAP01.udmf").read_text(encoding="utf-8")

actors = {
    17129: ("ReturnsDeskReceiptStash : ShellBox", "CMEM A -1 Bright", "emotionally non-refundable"),
    17130: ("DamagedGoodsLabelStash : ClipBox", "BOXE A -1 Bright", "damage appears to be managerial"),
    17131: ("EmployeeReliefKit : Medikit", "BRKS A -1 Bright", "recover off the clock"),
}

for doomednum, (actor, sprite, joke) in actors.items():
    marker = f"actor {actor} {doomednum}"
    if marker not in decorate:
        raise SystemExit(f"Closing Time secret actor missing: {marker}")
    if sprite not in decorate:
        raise SystemExit(f"Secret actor does not use project-owned visible sprite: {sprite}")
    if joke not in decorate:
        raise SystemExit(f"Secret pickup interaction text missing: {joke}")
    if layer.count(f"type = {doomednum}") != 1:
        raise SystemExit(f"Secret DoomEdNum {doomednum} must be placed exactly once")

expected_positions = (
    "x =  720.0; y = -455.0",
    "x =  720.0; y =  465.0",
    "x = -730.0; y =  300.0",
)
for marker in expected_positions:
    if marker not in layer:
        raise SystemExit(f"Authored side-route secret moved unexpectedly: {marker}")

# The full exploration pass keeps the existing three Corporate Compliance Memos as optional lore
# and adds useful resource rewards without touching mandatory breaker/supervisor logic.
if core_map.count("type = 17105") != 3:
    raise SystemExit("Closing Time must keep exactly three Corporate Compliance Memos")
for doomednum in actors:
    if f"type = {doomednum}" in core_map:
        raise SystemExit(f"Secret reward {doomednum} leaked into mandatory core MAP01 geometry")

with zipfile.ZipFile(PK3, "r") as archive:
    packaged_decorate = archive.read("DECORATE").decode("utf-8")
    for actor, _, _ in actors.values():
        class_name = actor.split(" : ", 1)[0]
        if class_name not in packaged_decorate:
            raise SystemExit(f"Packaged DECORATE is missing secret reward: {class_name}")

wad_text = MAP_WAD.read_bytes()
for doomednum in actors:
    if f"type = {doomednum}".encode("ascii") not in wad_text:
        raise SystemExit(f"Built MAP01 does not contain secret DoomEdNum {doomednum}")

print("Closing Time secrets/joke-interactions contract: PASS")
print("Three optional resource stashes, three compliance memos and project-owned pickup presentation are packaged.")
