from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAPINFO = ROOT / "game" / "MAPINFO"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

if not PK3.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

mapinfo = MAPINFO.read_text(encoding="utf-8")

if "clearskills" not in mapinfo:
    raise SystemExit("Custom difficulty contract requires clearskills")

skill_ids = re.findall(r"(?im)^skill\s+([a-z0-9_]+)\s*$", mapinfo)
expected_ids = ["closingcrew", "graveyardshift", "corporatehell"]
if skill_ids != expected_ids:
    raise SystemExit(f"Expected exactly {expected_ids}; found {skill_ids}")


def skill_block(skill_id: str) -> str:
    match = re.search(
        rf"(?ims)^skill\s+{re.escape(skill_id)}\s*\{{(.*?)^\}}",
        mapinfo,
    )
    if not match:
        raise SystemExit(f"Missing skill block: {skill_id}")
    return match.group(1)


contracts = {
    "closingcrew": (
        'Name = "Closing Crew"',
        "SpawnFilter = Easy",
        "AmmoFactor = 1.25",
        "DamageFactor = 0.75",
        "HealthFactor = 1.20",
        "MonsterHealth = 0.90",
    ),
    "graveyardshift": (
        'Name = "Graveyard Shift"',
        "SpawnFilter = Normal",
        "AmmoFactor = 1.00",
        "DamageFactor = 1.00",
        "HealthFactor = 1.00",
        "MonsterHealth = 1.00",
        "DefaultSkill",
    ),
    "corporatehell": (
        'Name = "Corporate Hell"',
        "SpawnFilter = Hard",
        "AmmoFactor = 0.85",
        "DamageFactor = 1.25",
        "HealthFactor = 0.85",
        "MonsterHealth = 1.15",
        "MustConfirm",
    ),
}

for skill_id, markers in contracts.items():
    block = skill_block(skill_id)
    for marker in markers:
        if marker not in block:
            raise SystemExit(f"Difficulty contract missing in {skill_id}: {marker}")

# Corporate Hell intentionally raises resource/combat pressure without enabling opaque
# speed/respawn chaos that would undermine authored telegraphs and Overtime readability.
corporate = skill_block("corporatehell")
for forbidden in ("FastMonsters", "RespawnTime", "DisableCheats"):
    if forbidden in corporate:
        raise SystemExit(f"Corporate Hell must preserve readable authored pacing; remove {forbidden}")

with zipfile.ZipFile(PK3, "r") as archive:
    packaged = archive.read("MAPINFO").decode("utf-8")
    for marker in (
        'Name = "Closing Crew"',
        'Name = "Graveyard Shift"',
        'Name = "Corporate Hell"',
        "DefaultSkill",
        "MustConfirm",
    ):
        if marker not in packaged:
            raise SystemExit(f"Packaged MAPINFO missing difficulty marker: {marker}")

print("Difficulty modes contract: PASS")
print("Closing Crew, Graveyard Shift and Corporate Hell preserve scripted Overtime timing while tuning forgiveness and resource pressure.")
