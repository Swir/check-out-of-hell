from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

map03 = (GAME / "MAP03.udmf").read_text(encoding="utf-8")
decorate = (GAME / "DECORATE_FROZEN").read_text(encoding="utf-8")

for marker in (
    "actor FrozenRecallStockPile 17164",
    'Tag "Recall-Hold Stock Pile"',
    "Health 65",
    "Radius 30",
    "+SOLID",
    "+SHOOTABLE",
    'A_PlaySound("coh/palletdown", CHAN_BODY)',
    "A_NoBlocking",
    "actor FrozenRecallStash : Backpack 17165",
    'Tag "Recall Freezer Emergency Stash"',
    "BOXE A -1 Bright",
):
    if marker not in decorate:
        raise SystemExit(f"Frozen Recall Freezer actor contract is incomplete: {marker}")

# The optional pocket is a real authored room, not a loose pickup. Five two-sided shelf walls form a
# compact rear-left enclosure with a 64-unit south doorway between x=-602 and x=-538.
for vertex in (
    'vertex { x = -640.0; y = 330.0; }',
    'vertex { x = -602.0; y = 330.0; }',
    'vertex { x = -538.0; y = 330.0; }',
    'vertex { x = -500.0; y = 330.0; }',
    'vertex { x = -500.0; y = 455.0; }',
    'vertex { x = -640.0; y = 455.0; }',
):
    if vertex not in map03:
        raise SystemExit(f"Frozen Recall Freezer geometry drifted: {vertex}")

for line in (
    "linedef { v1 = 12; v2 = 13; sidefront = 12; sideback = 13; blocking = true; }",
    "linedef { v1 = 14; v2 = 15; sidefront = 14; sideback = 15; blocking = true; }",
    "linedef { v1 = 15; v2 = 16; sidefront = 16; sideback = 17; blocking = true; }",
    "linedef { v1 = 16; v2 = 17; sidefront = 18; sideback = 19; blocking = true; }",
    "linedef { v1 = 17; v2 = 12; sidefront = 20; sideback = 21; blocking = true; }",
):
    if line not in map03:
        raise SystemExit(f"Frozen Recall Freezer shelf wall is missing: {line}")

if "linedef { v1 = 13; v2 = 14;" in map03 or "linedef { v1 = 14; v2 = 13;" in map03:
    raise SystemExit("Frozen Recall Freezer doorway was accidentally sealed with map geometry")

required_counts = {
    17164: 1,  # shootable recall-hold doorway pile
    17165: 1,  # optional multi-ammo stash
    17105: 3,  # compliance memo route remains three items total
    17001: 2,  # one normal Self-Checkout plus one contained secret encounter
}
for thing_type, expected in required_counts.items():
    actual = map03.count(f"type = {thing_type}")
    if actual != expected:
        raise SystemExit(f"Frozen Recall Freezer type {thing_type} count changed: expected {expected}, found {actual}")

stock = re.search(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 90; type = 17164", map03)
stash = re.search(r"x = (-?[0-9.]+); y = (-?[0-9.]+); angle = 0; type = 17165", map03)
secret_enemy = re.search(r"x = -570\.0; y = 382\.0; angle = 270; type = 17001", map03)
secret_memo = re.search(r"x = -615\.0; y = 420\.0; angle = 0; type = 17105", map03)
if not stock or (float(stock.group(1)), float(stock.group(2))) != (-570.0, 330.0):
    raise SystemExit("Frozen Recall Freezer stock pile must seal the authored 64-unit doorway")
if not stash or not (-640.0 < float(stash.group(1)) < -500.0 and 330.0 < float(stash.group(2)) < 455.0):
    raise SystemExit("Frozen Recall Freezer stash must stay inside the optional pocket")
if not secret_enemy or not secret_memo:
    raise SystemExit("Frozen Recall Freezer must keep its contained Self-Checkout encounter and compliance memo payoff")

# Mandatory work and global pressure anchors must stay outside the optional room. This keeps the
# secret a reward/encounter choice rather than a disguised key hunt or progression shortcut.
thing_pattern = re.compile(r"thing \{ x =\s*(-?[0-9.]+); y =\s*(-?[0-9.]+); angle = [-0-9]+; type = (\d+);")
mandatory_types = {17111, 17141, 17101, 17103, 17128, 17132, 17140, 17100}
for x_text, y_text, type_text in thing_pattern.findall(map03):
    thing_type = int(type_text)
    if thing_type not in mandatory_types:
        continue
    x = float(x_text)
    y = float(y_text)
    if -650.0 <= x <= -490.0 and 320.0 <= y <= 465.0:
        raise SystemExit(f"Mandatory/ambient type {thing_type} moved into the optional Recall Freezer at ({x}, {y})")

with zipfile.ZipFile(PK3, "r") as archive:
    packaged_decorate = archive.read("DECORATE").decode("utf-8")
    for marker in (
        "actor FrozenRecallStockPile 17164",
        "actor FrozenRecallStash : Backpack 17165",
    ):
        if marker not in packaged_decorate:
            raise SystemExit(f"Packaged DECORATE lost Frozen Recall Freezer content: {marker}")

    wad = archive.read("maps/MAP03.wad")
    ident, numlumps, dir_offset = struct.unpack("<4sII", wad[:12])
    if ident != b"PWAD" or numlumps != 3:
        raise SystemExit("Packaged MAP03 is not the expected canonical three-lump PWAD")
    directory = wad[dir_offset : dir_offset + numlumps * 16]
    entries = []
    for index in range(numlumps):
        offset, size, raw_name = struct.unpack_from("<II8s", directory, index * 16)
        entries.append((offset, size, raw_name.rstrip(b"\0").decode("ascii")))
    if [name for _, _, name in entries] != ["MAP03", "TEXTMAP", "ENDMAP"]:
        raise SystemExit("Packaged MAP03 lost canonical MAP03 -> TEXTMAP -> ENDMAP ordering")
    text_offset, text_size, _ = entries[1]
    textmap = wad[text_offset : text_offset + text_size].decode("utf-8")
    for marker in (
        "type = 17164",
        "type = 17165",
        "x = -570.0; y = 382.0; angle = 270; type = 17001",
        "vertex { x = -640.0; y = 330.0; }",
        "vertex { x = -500.0; y = 455.0; }",
    ):
        if marker not in textmap:
            raise SystemExit(f"Packaged MAP03 TEXTMAP lost Frozen Recall Freezer marker: {marker}")

print("Frozen Foods Recall Freezer secret contract: PASS")
print("Breakable optional-room routing, useful reward, contained encounter and mandatory-objective separation stay source/package verified.")
