from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAP04 = GAME / "MAP04.udmf"
MAP04_OVERTIME = GAME / "MAP04_OVERTIME.udmf"
MAPINFO = GAME / "MAPINFO"
BUILD = ROOT / "tools" / "build.py"
CORE_ZSCRIPT = GAME / "ZSCRIPT"
ZSCRIPT = GAME / "ZSCRIPT_ELECTRONICS"
DECORATE = GAME / "DECORATE_ELECTRONICS"
PRESENTATION = ROOT / "tools" / "generate_presentation_assets.py"

if not PK3.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

source_map = MAP04.read_text(encoding="utf-8")
overtime_map = MAP04_OVERTIME.read_text(encoding="utf-8")
mapinfo = MAPINFO.read_text(encoding="utf-8")
build_source = BUILD.read_text(encoding="utf-8")
core_zscript = CORE_ZSCRIPT.read_text(encoding="utf-8")
zscript = ZSCRIPT.read_text(encoding="utf-8")
decorate = DECORATE.read_text(encoding="utf-8")
presentation = PRESENTATION.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"Electronics contract missing {label}: {needle}")


def positions(text: str, type_id: int) -> list[tuple[float, float]]:
    pattern = re.compile(
        rf"thing\s*\{{[^}}]*?x\s*=\s*(-?\d+(?:\.\d+)?)\s*;\s*"
        rf"y\s*=\s*(-?\d+(?:\.\d+)?)\s*;[^}}]*?type\s*=\s*{type_id}\s*;",
        re.DOTALL,
    )
    return [(float(x), float(y)) for x, y in pattern.findall(text)]


# MAP04 is a real objective department: two repairs, a physical network reboot, a timed reboot
# defence, management, escalating Overtime navigation pressure, optional exploration and a return
# guide. Only the timed sequence owns the final authoritative 3/3 token after physical reboot use.
if source_map.count("type = 17111") != 2:
    raise SystemExit("MAP04 must contain exactly two physical electronics breaker pickups")
for type_id, expected, label in (
    (17144, 1, "fresh-entry initializer"),
    (17145, 1, "breaker-response anchor"),
    (17146, 1, "network-reboot pickup anchor"),
    (17149, 1, "network-reboot defence anchor"),
    (17147, 1, "demo-wall surge anchor"),
    (17148, 1, "demo-wall kill-switch anchor"),
    (17150, 1, "Overtime security-lockdown anchor"),
    (17101, 1, "gated Night Manager"),
    (17103, 1, "management-response anchor"),
    (17128, 1, "full-power recovery cache"),
    (17132, 1, "post-clear clock-out guide"),
):
    actual = source_map.count(f"type = {type_id}")
    if actual != expected:
        raise SystemExit(f"MAP04 expected {expected} {label}, found {actual}")

if source_map.count("type = 17105") != 3:
    raise SystemExit("MAP04 must keep exactly three optional Corporate Compliance Memos")
if source_map.count("type = 17100") < 3:
    raise SystemExit("MAP04 must keep authored hostile Overtime pressure anchors")
if overtime_map.count("type = 17106") != 3:
    raise SystemExit("MAP04 must keep exactly three standard side-lane electrical hazard anchors")
if "type = 17003" in source_map:
    raise SystemExit("MAP04 must not pre-place Night Manager before electronics power restoration")

reboot_positions = positions(source_map, 17146)
defence_positions = positions(source_map, 17149)
surge_positions = positions(source_map, 17147)
kill_positions = positions(source_map, 17148)
lock_positions = positions(source_map, 17150)
if len(reboot_positions) != 1 or reboot_positions[0][1] < 400:
    raise SystemExit(f"Store Network Reboot must live at the rear service position: {reboot_positions}")
if len(defence_positions) != 1 or abs(defence_positions[0][0]) < 500:
    raise SystemExit(f"Network reboot defence must stay on an outer side lane: {defence_positions}")
if len(surge_positions) != 1 or abs(surge_positions[0][0]) < 500:
    raise SystemExit(f"Demo-wall surge must stay on an outer side lane: {surge_positions}")
if len(kill_positions) != 1 or abs(kill_positions[0][0]) < 500:
    raise SystemExit(f"Demo-wall kill switch must stay on an outer side lane: {kill_positions}")
if surge_positions[0][0] * kill_positions[0][0] >= 0:
    raise SystemExit("Demo-wall surge and optional kill switch must occupy opposite side lanes")
if len(lock_positions) != 1:
    raise SystemExit(f"Electronics must keep exactly one authored security-lockdown anchor: {lock_positions}")
lock_x, lock_y = lock_positions[0]
if not (200 <= abs(lock_x) <= 350) or abs(lock_y) > 80:
    raise SystemExit(
        "Electronics lockdown must seal one inner display aisle without occupying the x=0 service lane: "
        f"{lock_positions}"
    )
for x, _ in positions(overtime_map, 17106):
    if abs(x) < 500:
        raise SystemExit("Electronics standard Overtime hazards must stay off the central service lane")

for marker in (
    '17144 = "ElectronicsDepartmentInitSpawner"',
    '17145 = "ElectronicsBreakerResponseSpawner"',
    '17146 = "ElectronicsNetworkRebootSpawner"',
    '17147 = "ElectronicsDemoSurgeSpawner"',
    '17148 = "ElectronicsKillSwitchSpawner"',
    '17149 = "ElectronicsNetworkRebootSequence"',
    '17150 = "ElectronicsLockdownSpawner"',
    'map MAP04 "Electronics"',
    'music = "D_COH04"',
):
    require(mapinfo, marker, "MAPINFO wiring")

for marker in (
    'MAPS = ["MAP01", "MAP02", "MAP03", "MAP04"]',
    '(GAME / "DECORATE_ELECTRONICS").read_text',
    '(GAME / "ZSCRIPT_ELECTRONICS").read_text',
):
    require(build_source, marker, "build integration")

for marker in (
    "class ElectronicsDepartmentInitSpawner : Actor",
    "class ElectronicsBreakerResponseSpawner : Actor",
    "class ElectronicsNetworkRebootSpawner : Actor",
    "class ElectronicsNetworkRebootSequence : Actor",
    "class ElectronicsKillSwitchSpawner : Actor",
    "class ElectronicsDemoSurgeSpawner : Actor",
    "class ElectronicsLockdownSpawner : Actor",
    'p.A_TakeInventory("CorporateMemo", 3);',
    'p.A_TakeInventory("ElectronicsDisplayKillSwitch", 1);',
    'p.A_TakeInventory("ElectronicsRebootPending", 1);',
    'p.A_GiveInventory("ElectronicsDepartmentToken", 1);',
    "nextCheck = Level.maptime + 7;",
    "responseTic = Level.maptime + 35 * 3;",
    'Actor.Spawn("ScannerTurret", Pos);',
    'Actor.Spawn("AngrySelfCheckout", Pos);',
    'Actor.Spawn("ElectronicsNetworkReboot", Pos);',
    'p.CountInv("ElectronicsRebootPending") <= 0',
    "elapsed >= 35 * 2",
    "elapsed >= 35 * 5",
    "elapsed >= 35 * 7",
    "elapsed >= 35 * 10",
    'Actor.Spawn("CartOfDoom", Pos);',
    'p.A_GiveInventory("CheckoutFuse", 1);',
    'p.CountInv("CheckoutFuse") < 3',
    'p.CountInv("ElectronicsDisplayKillSwitch") > 0',
    "nextSurgeTic = Level.maptime + 35 * 16;",
    "burstTic = Level.maptime + 35 * 2;",
    "int delaySeconds = 32;",
    "delaySeconds = 24;",
    "delaySeconds = 18;",
    'Actor.Spawn("ElectronicsDisplayBurst", Pos);',
    "overtimeStage < 2",
    "nextLockTic = Level.maptime + 35 * 12;",
    "closeTic = Level.maptime + 35 * 2;",
    "int delaySeconds = 24;",
    'Actor.Spawn("ElectronicsLockdownShutter", Pos);',
):
    require(zscript, marker, "Electronics ZScript behavior")

for marker in (
    'p.A_TakeInventory("ElectronicsDepartmentToken", 1);',
    'bool electronics = p.CountInv("ElectronicsDepartmentToken") > 0;',
    'bool rebootPending = p.CountInv("ElectronicsRebootPending") > 0;',
    'powerPulseText = "ELECTRONICS POWER 1/3 - SHOWROOM CIRCUIT ONLINE";',
    'powerPulseText = "ELECTRONICS POWER 2/3 - NETWORK REBOOT AVAILABLE";',
    'powerPulseText = "NETWORK ONLINE - SUPERVISOR ACCESS RESTORED";',
    'taskText = "OBJECTIVE  START STORE NETWORK REBOOT";',
    'taskText = "OBJECTIVE  HOLD STORE NETWORK REBOOT";',
    'taskText = "OBJECTIVE  CLEAR THE NIGHT MANAGER";',
    'taskText = "OBJECTIVE  RETURN TO ELECTRONICS ENTRY";',
    'powerText = String.Format("ELECTRONICS POWER  %d/3", fuses);',
):
    require(core_zscript, marker, "department-specific Electronics HUD/state")

lockdown_section = zscript.split("class ElectronicsLockdownSpawner : Actor", 1)[1]
if 'CountInv("ElectronicsDisplayKillSwitch")' in lockdown_section:
    raise SystemExit("Demo Wall Kill Switch must not disable the independent Overtime security lockdown")
if 'CountInv("SupervisorClearanceToken") > 0' not in lockdown_section:
    raise SystemExit("Electronics lockdown must retire on supervisor clearance")
if "delaySeconds = 18;" not in lockdown_section:
    raise SystemExit("HELL RUSH must tighten the Electronics lockdown recurrence")

for marker in (
    "actor ElectronicsDepartmentToken : Inventory",
    "actor ElectronicsRebootPending : Inventory",
    "actor ElectronicsNetworkReboot : CustomInventory",
    'A_GiveInventory("ElectronicsRebootPending", 1)',
    "actor ElectronicsDisplayKillSwitch : Inventory",
    "actor ElectronicsDisplayBurst",
    "actor ElectronicsLockdownShutter",
    "ENRB A -1 Bright",
    "EKIL A -1 Bright",
    "ESUR A 7 Bright",
    "Radius 116",
    "Scale 2.0",
    "COSH A 175 Bright",
    'A_PlaySound("coh/shutter", CHAN_BODY)',
):
    require(decorate, marker, "Electronics actor behavior")
if 'A_GiveInventory("CheckoutFuse", 1)' in decorate:
    raise SystemExit("Electronics reboot pickup must not grant the final power token directly")

for marker in (
    "def _electronics_reboot_sprite",
    "def _electronics_kill_switch_sprite",
    "def _electronics_surge_sprite",
    '"ENRBA0.png"',
    '"EKILA0.png"',
    'f"ESUR{frame}0.png"',
):
    require(presentation, marker, "deterministic Electronics presentation")

# Validate the composed player payload, not just source files.
with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    if "maps/MAP04.wad" not in names:
        raise SystemExit("Packaged PK3 is missing maps/MAP04.wad")
    for asset in (
        "sprites/ENRBA0.png",
        "sprites/EKILA0.png",
        "sprites/ESURA0.png",
        "sprites/ESURB0.png",
        "sprites/ESURC0.png",
        "music/D_COH04.mid",
    ):
        if asset not in names:
            raise SystemExit(f"Packaged PK3 is missing Electronics asset {asset}")

    packaged_zscript = archive.read("ZSCRIPT").decode("utf-8")
    packaged_decorate = archive.read("DECORATE").decode("utf-8")
    packaged_mapinfo = archive.read("MAPINFO").decode("utf-8")
    for marker in (
        "class ElectronicsNetworkRebootSpawner : Actor",
        "class ElectronicsNetworkRebootSequence : Actor",
        "class ElectronicsDemoSurgeSpawner : Actor",
        "class ElectronicsLockdownSpawner : Actor",
        'bool electronics = p.CountInv("ElectronicsDepartmentToken") > 0;',
        'taskText = "OBJECTIVE  HOLD STORE NETWORK REBOOT";',
    ):
        require(packaged_zscript, marker, "packaged Electronics ZScript")
    for marker in (
        "actor ElectronicsDepartmentToken",
        "actor ElectronicsRebootPending",
        "actor ElectronicsNetworkReboot",
        "actor ElectronicsDisplayBurst",
        "actor ElectronicsLockdownShutter",
    ):
        require(packaged_decorate, marker, "packaged Electronics DECORATE")
    require(packaged_mapinfo, 'map MAP04 "Electronics"', "packaged MAPINFO")
    require(packaged_mapinfo, '17149 = "ElectronicsNetworkRebootSequence"', "packaged MAPINFO")
    require(packaged_mapinfo, '17150 = "ElectronicsLockdownSpawner"', "packaged MAPINFO")

    wad = archive.read("maps/MAP04.wad")
    ident, numlumps, dir_offset = struct.unpack("<4sII", wad[:12])
    if ident != b"PWAD" or numlumps != 3:
        raise SystemExit("Packaged MAP04 must be a canonical three-lump UDMF PWAD")
    directory = wad[dir_offset : dir_offset + numlumps * 16]
    entries = []
    for index in range(numlumps):
        offset, size, raw_name = struct.unpack_from("<II8s", directory, index * 16)
        entries.append((offset, size, raw_name.rstrip(b"\0").decode("ascii")))
    if [entry[2] for entry in entries] != ["MAP04", "TEXTMAP", "ENDMAP"]:
        raise SystemExit(f"Packaged MAP04 has invalid UDMF markers: {entries}")
    text_offset, text_size, _ = entries[1]
    textmap = wad[text_offset : text_offset + text_size].decode("utf-8")
    for marker in (
        "type = 17146",
        "type = 17149",
        "type = 17147",
        "type = 17148",
        "type = 17150",
        "type = 17106",
    ):
        require(textmap, marker, "packaged MAP04 objective/hazard payload")

print("Electronics playable department contract: PASS")
