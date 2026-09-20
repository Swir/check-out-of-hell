from __future__ import annotations

from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAP_WAD = ROOT / "dist" / "MAP01.wad"

ROUTE_SIGNS = {
    17161: ((-420.0, -215.0), "ClosingTimeLeftFuseSign", "LFSN", "LFSNA0.png"),
    17162: ((420.0, -215.0), "ClosingTimeRightFuseSign", "RFSN", "RFSNA0.png"),
    17163: ((-210.0, 285.0), "ClosingTimeStaffFuseSign", "SFSN", "SFSNA0.png"),
    17164: ((-650.0, -75.0), "ClosingTimeOvertimeLaneSign", "OTSN", "OTSNA0.png"),
}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_number(block: str, field: str) -> float:
    match = re.search(rf"\b{field}\s*=\s*(-?\d+(?:\.\d+)?)\s*;", block)
    if not match:
        fail(f"Missing {field} in thing block: {block}")
    return float(match.group(1))


def parse_things(text: str) -> list[dict[str, float | int]]:
    parsed: list[dict[str, float | int]] = []
    for block in re.findall(r"thing\s*\{(.*?)\}", text, flags=re.DOTALL):
        parsed.append(
            {
                "type": int(read_number(block, "type")),
                "x": read_number(block, "x"),
                "y": read_number(block, "y"),
            }
        )
    return parsed


def png_has_grab(path: Path) -> bool:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    cursor = 8
    grabs = 0
    while cursor + 12 <= len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        payload = data[cursor + 8 : cursor + 8 + length]
        if kind == b"grAb" and len(payload) == 8:
            grabs += 1
        cursor += 12 + length
    return grabs == 1


def read_textmap(path: Path) -> str:
    data = path.read_bytes()
    if data[:4] != b"PWAD":
        fail("MAP01 build output is not a PWAD")
    lump_count, directory_offset = struct.unpack_from("<II", data, 4)
    for index in range(lump_count):
        entry = directory_offset + index * 16
        offset, size, raw_name = struct.unpack_from("<II8s", data, entry)
        name = raw_name.rstrip(b"\0").decode("ascii")
        if name == "TEXTMAP":
            return data[offset : offset + size].decode("utf-8")
    fail("MAP01 build output has no TEXTMAP lump")
    return ""


def main() -> int:
    if not PK3.exists() or not MAP_WAD.exists():
        fail("Build output missing. Run: python tools/build.py")

    core_text = (GAME / "MAP01.udmf").read_text(encoding="utf-8")
    env_text = (GAME / "MAP01_ENVIRONMENT.udmf").read_text(encoding="utf-8")
    polish_text = (GAME / "MAP01_POLISH.udmf").read_text(encoding="utf-8")
    decorate_polish = (GAME / "DECORATE_CLOSING_POLISH").read_text(encoding="utf-8")
    decorate_env = (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8")
    zscript = (GAME / "ZSCRIPT").read_text(encoding="utf-8")
    build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    windows_doc = (ROOT / "docs" / "WINDOWS_PLAYTEST.md").read_text(encoding="utf-8")
    polish_doc = (ROOT / "docs" / "CLOSING_TIME_POLISH.md").read_text(encoding="utf-8")
    signoff = (ROOT / "tools" / "windows_demo_signoff.ps1").read_text(encoding="utf-8")
    verifier = (ROOT / "tools" / "verify_windows_signoff_evidence.py").read_text(encoding="utf-8")

    # The canonical roadmap items deliberately stay open until real target-Windows human evidence exists.
    for marker in (
        "- [ ] First fully decorated/polished level",
        "- [ ] Level 01: Closing Time — polished",
    ):
        if marker not in roadmap:
            fail(f"Closing Time polish gate must remain pending before manual evidence: {marker}")

    # Deterministic project-owned route signs must be exact, unique and outside the permanent center strip.
    polish_things = parse_things(polish_text)
    for doomednum, (expected_pos, actor_name, sprite, png_name) in ROUTE_SIGNS.items():
        matches = [thing for thing in polish_things if thing["type"] == doomednum]
        if len(matches) != 1:
            fail(f"Closing Time polish layer expected exactly one type {doomednum}, found {len(matches)}")
        actual_pos = (matches[0]["x"], matches[0]["y"])
        if actual_pos != expected_pos:
            fail(f"Closing Time polish sign {doomednum} moved: expected {expected_pos}, got {actual_pos}")
        if abs(float(matches[0]["x"])) < 160.0:
            fail(f"Closing Time polish sign {doomednum} entered the permanent center corridor")

        actor_match = re.search(
            rf"actor\s+{re.escape(actor_name)}\s+{doomednum}\s*\{{(.*?)\n\}}",
            decorate_polish,
            flags=re.DOTALL,
        )
        if not actor_match:
            fail(f"Closing Time polish actor missing: {actor_name}")
        actor_block = actor_match.group(1)
        for marker in ("+NOBLOCKMAP", "+NOGRAVITY", f"{sprite} A -1 Bright"):
            if marker not in actor_block:
                fail(f"Closing Time polish actor {actor_name} missing safety/presentation marker: {marker}")

        sprite_path = GAME / "sprites" / png_name
        if not sprite_path.is_file() or not png_has_grab(sprite_path):
            fail(f"Closing Time polish sprite missing/invalid ZDoom PNG: {png_name}")

    # Do not silently reuse these editor numbers elsewhere as the campaign continues.
    for source in sorted(GAME.glob("MAP*.udmf")):
        if source.name == "MAP01_POLISH.udmf":
            continue
        text = source.read_text(encoding="utf-8")
        for doomednum in ROUTE_SIGNS:
            if re.search(rf"\btype\s*=\s*{doomednum}\s*;", text):
                fail(f"Closing Time polish DoomEdNum {doomednum} also appears in {source.name}")
    for source in sorted(GAME.glob("DECORATE*")):
        if source.name == "DECORATE_CLOSING_POLISH":
            continue
        text = source.read_text(encoding="utf-8")
        for doomednum in ROUTE_SIGNS:
            if re.search(rf"\bactor\s+\w+(?:\s*:\s*\w+)?\s+{doomednum}\b", text):
                fail(f"Closing Time polish DoomEdNum {doomednum} also belongs to {source.name}")

    # Clutter remains intentionally restrained while the atmosphere layer keeps slow readable light changes.
    for doomednum, expected in ((17124, 2), (17125, 2), (17127, 6)):
        actual = env_text.count(f"type = {doomednum}")
        if actual != expected:
            fail(f"Closing Time clutter/lighting budget changed for type {doomednum}: expected {expected}, got {actual}")
    for marker in ("FLIT A 70 Bright", "FLIT B 12", "FLIT C 18 Bright", "FLIT D 12"):
        if marker not in decorate_env:
            fail(f"Closing Time slow-flicker lighting contract missing: {marker}")

    # Initial combat, recurring Overtime and boss response must still leave the strongest navigation line readable.
    core_things = parse_things(core_text)
    hostile_types = {17001, 17002, 17004, 17005}
    blocked_center = [
        thing
        for thing in core_things
        if thing["type"] in hostile_types
        and abs(float(thing["x"])) < 180.0
        and -300.0 < float(thing["y"]) < 260.0
    ]
    if blocked_center:
        fail(f"Closing Time polish candidate blocks the center combat route: {blocked_center}")
    if {(thing["x"], thing["y"]) for thing in core_things if thing["type"] == 17103} != {
        (-430.0, 300.0),
        (430.0, 300.0),
    }:
        fail("Closing Time Night Manager response no longer flanks the rear approach")

    # Preserve the authored recovery/pacing evidence that keeps all three difficulties readable.
    for marker in (
        "elapsed >= 15",
        "elapsed >= 34",
        "elapsed >= 54",
        "elapsed >= 76",
        'Actor.Spawn("CheckoutPowerCache", Pos)',
        'p.CountInv("SupervisorClearanceToken") > 0',
    ):
        if marker not in zscript:
            fail(f"Closing Time pacing prerequisite missing: {marker}")

    # Build wiring must regenerate/package the polish layer deterministically on every candidate build.
    for marker in (
        "from generate_closing_time_polish_assets import generate_closing_time_polish_assets",
        'MAP_LAYER_SUFFIXES = ["OVERTIME", "ENVIRONMENT", "POLISH"]',
        '(GAME / "DECORATE_CLOSING_POLISH").read_text',
        "generate_closing_time_polish_assets(GAME)",
        "validate_closing_time_polish_gate()",
    ):
        if marker not in build:
            fail(f"Closing Time polish candidate is not fully wired into build.py: {marker}")

    # Automated evidence can prepare a candidate, but the canonical polished-level checkbox remains human-gated.
    for marker in (
        "three real `MAP01 — Closing Time` runs",
        "explicit confirmation that Closing Time is polished enough",
    ):
        if marker not in windows_doc:
            fail(f"Windows polish sign-off documentation missing: {marker}")
    for marker in (
        "final_polish_signoff",
        "Is Closing Time visually/readably polished and balanced enough",
        "combat_readable",
        "balance_acceptable",
        "performance_sanity",
    ):
        if marker not in signoff:
            fail(f"Windows sign-off harness missing Closing Time polish evidence field/prompt: {marker}")
    for marker in ("final_polish_signoff", "combat_readable", "balance_acceptable", "--expected-commit"):
        if marker not in verifier:
            fail(f"Independent Windows evidence verifier missing Closing Time polish requirement: {marker}")
    for marker in (
        "Status: SIGN-OFF CANDIDATE",
        "Environment / art consistency",
        "Objective / route readability",
        "Lighting / atmosphere",
        "Clutter / visual hierarchy",
        "Gameplay pacing / balance",
        "Target-Windows human evidence",
    ):
        if marker not in polish_doc:
            fail(f"Closing Time polish acceptance note missing: {marker}")

    # Verify actual built source-to-package parity rather than trusting only source files.
    built_text = read_textmap(MAP_WAD)
    for doomednum in ROUTE_SIGNS:
        if built_text.count(f"type = {doomednum}") != 1:
            fail(f"Built MAP01 lost Closing Time polish sign {doomednum}")

    with zipfile.ZipFile(PK3, "r") as archive:
        names = set(archive.namelist())
        packaged_decorate = archive.read("DECORATE").decode("utf-8")
        for _, (_, actor_name, _, png_name) in ROUTE_SIGNS.items():
            if f"sprites/{png_name}" not in names:
                fail(f"Packaged PK3 missing Closing Time polish sprite: {png_name}")
            if actor_name not in packaged_decorate:
                fail(f"Packaged DECORATE missing Closing Time polish actor: {actor_name}")

    print("Closing Time polish candidate contract: PASS")
    print(
        "Automated art/readability/lighting/clutter/pacing/package prerequisites are protected; "
        "the canonical polished-level items intentionally remain open until exact-commit target-Windows human PASS evidence."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
