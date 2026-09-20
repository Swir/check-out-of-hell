from __future__ import annotations

from pathlib import Path
import re
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

DIRECTOR_SPRITES = [f"sprites/DDIR{frame}0.png" for frame in "ABCDEFGHIJKLMNO"]
DIRECTOR_SOUNDS = [
    "sounds/directoridle_v1.wav",
    "sounds/directoridle_v2.wav",
    "sounds/directorattack_v1.wav",
    "sounds/directorattack_v2.wav",
    "sounds/directorattack_v3.wav",
    "sounds/directorphase_v1.wav",
    "sounds/directorphase_v2.wav",
    "sounds/directorstamp_v1.wav",
    "sounds/directorstamp_v2.wav",
    "sounds/directorstamp_v3.wav",
    "sounds/directorhit_v1.wav",
    "sounds/directorhit_v2.wav",
    "sounds/directorhit_v3.wav",
    "sounds/directordown_v1.wav",
    "sounds/directordown_v2.wav",
]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing {needle!r}")


def count_type(map_text: str, doomednum: int) -> int:
    return len(re.findall(rf"\btype\s*=\s*{doomednum}\s*;", map_text))


def thing_xy(map_text: str, doomednum: int) -> tuple[float, float]:
    match = re.search(
        rf"thing\s*\{{(?=[^}}]*\btype\s*=\s*{doomednum}\s*;)(?P<body>[^}}]*)\}}",
        map_text,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError(f"MAP06 is missing DoomEdNum {doomednum}")
    body = match.group("body")
    x = re.search(r"\bx\s*=\s*(-?\d+(?:\.\d+)?)\s*;", body)
    y = re.search(r"\by\s*=\s*(-?\d+(?:\.\d+)?)\s*;", body)
    if not x or not y:
        raise AssertionError(f"MAP06 DoomEdNum {doomednum} is missing coordinates")
    return float(x.group(1)), float(y.group(1))


def textmap_from_wad(blob: bytes) -> str:
    if len(blob) < 12:
        raise AssertionError("MAP06.wad is too small")
    magic, lump_count, directory_offset = struct.unpack_from("<4sII", blob, 0)
    if magic not in {b"PWAD", b"IWAD"}:
        raise AssertionError(f"MAP06.wad has invalid magic {magic!r}")

    for index in range(lump_count):
        entry = directory_offset + index * 16
        if entry + 16 > len(blob):
            raise AssertionError("MAP06.wad directory is truncated")
        offset, size, raw_name = struct.unpack_from("<II8s", blob, entry)
        name = raw_name.rstrip(b"\0").decode("ascii")
        if name == "TEXTMAP":
            payload = blob[offset : offset + size]
            if len(payload) != size:
                raise AssertionError("MAP06 TEXTMAP payload is truncated")
            return payload.decode("utf-8")
    raise AssertionError("MAP06.wad does not contain TEXTMAP")


def png_chunks(data: bytes):
    cursor = 8
    while cursor + 12 <= len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        payload = data[cursor + 8 : cursor + 8 + length]
        yield kind, payload
        cursor += 12 + length


def validate_director_assets() -> None:
    for rel in DIRECTOR_SPRITES:
        data = (GAME / rel).read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise AssertionError(f"District Director sprite is not a PNG: {rel}")
        width, height = struct.unpack(">II", data[16:24])
        if width < 64 or height < 64:
            raise AssertionError(f"District Director sprite is unexpectedly small: {rel} -> {width}x{height}")
        offsets = [payload for kind, payload in png_chunks(data) if kind == b"grAb"]
        if len(offsets) != 1 or len(offsets[0]) != 8:
            raise AssertionError(f"District Director sprite lacks one valid grAb offset: {rel}")

    for rel in DIRECTOR_SOUNDS:
        with wave.open(str(GAME / rel), "rb") as stream:
            if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
                raise AssertionError(f"District Director WAV format is invalid: {rel}")
            if stream.getframerate() != 22050 or stream.getnframes() < 4000:
                raise AssertionError(f"District Director WAV duration/rate is invalid: {rel}")


def main() -> None:
    map_text = (GAME / "MAP06.udmf").read_text(encoding="utf-8")
    mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
    decorate = (GAME / "DECORATE_MANAGEMENT").read_text(encoding="utf-8")
    zscript = (GAME / "ZSCRIPT_MANAGEMENT").read_text(encoding="utf-8")
    sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
    build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
    generator = (ROOT / "tools" / "generate_district_director_assets.py").read_text(encoding="utf-8")
    management_doc = (ROOT / "docs" / "MANAGEMENT_FLOOR.md").read_text(encoding="utf-8")

    auth_block = decorate.split("actor ManagementBoardroomAuthorization : CustomInventory 17020", 1)[1].split(
        "actor DistrictDirector : RegionalManager", 1
    )[0]
    director_block = decorate.split("actor DistrictDirector : RegionalManager", 1)[1]
    review_block = zscript.split("class ManagementBoardroomReviewSequence : Actor", 1)[1].split(
        "class ManagementDirectorArrivalSpawner : Actor", 1
    )[0]
    arrival_block = zscript.split("class ManagementDirectorArrivalSpawner : Actor", 1)[1].split(
        "class ManagementExecutiveAuditSpawner : Actor", 1
    )[0]
    audit_block = zscript.split("class ManagementExecutiveAuditSpawner : Actor", 1)[1]

    # Management Floor must require two opposite Executive Access repairs, then a physical boardroom
    # authorization plus exactly one timed review sequence before full power can be granted.
    if count_type(map_text, 17111) != 2:
        raise AssertionError("MAP06 must contain exactly two Executive Access circuit repairs")
    if count_type(map_text, 17102) != 2:
        raise AssertionError("MAP06 must contain exactly two powered boardroom shutters")
    if count_type(map_text, 17020) != 1:
        raise AssertionError("MAP06 must contain exactly one Boardroom Breaker Authorization")
    if count_type(map_text, 17160) != 1:
        raise AssertionError("MAP06 must contain exactly one Boardroom Review sequence anchor")
    if count_type(map_text, 17158) != 1 or count_type(map_text, 17159) != 1:
        raise AssertionError("MAP06 must contain one District Director arrival and one Executive Audit anchor")

    auth_x, auth_y = thing_xy(map_text, 17020)
    review_x, review_y = thing_xy(map_text, 17160)
    if abs(auth_x) > 100 or auth_y < 350:
        raise AssertionError("Boardroom authorization must remain centered behind the powered shutters")
    if abs(review_x) < 500 or review_y < 330:
        raise AssertionError("Boardroom Review response anchor must stay on an outer boardroom lane")

    require(mapinfo, '17158 = "ManagementDirectorArrivalSpawner"', "MAPINFO director arrival DoomEdNum")
    require(mapinfo, '17159 = "ManagementExecutiveAuditSpawner"', "MAPINFO executive audit DoomEdNum")
    require(mapinfo, '17160 = "ManagementBoardroomReviewSequence"', "MAPINFO boardroom review DoomEdNum")
    require(mapinfo, 'map MAP06 "Management Floor"', "MAP06 registration")
    require(mapinfo, 'next = "MAP01"', "campaign loop")
    require(mapinfo, 'music = "D_COH06"', "Management Floor soundtrack")

    require(decorate, "actor ManagementBoardroomReviewPending : Inventory", "boardroom pending token")
    require(decorate, "actor ManagementBoardroomAuthorization : CustomInventory 17020", "physical boardroom authorization")
    require(auth_block, 'A_GiveInventory("ManagementBoardroomReviewPending", 1)', "authorization hand-off")
    if "CheckoutFuse" in auth_block:
        raise AssertionError("Boardroom authorization must not grant full power directly")

    # The boss must now be visually/audio-distinct from Regional Management while retaining the tested
    # inheritance defaults and leaving all objective state in the shared death handler.
    require(decorate, "actor DistrictDirector : RegionalManager", "District Director actor")
    require(director_block, 'Tag "The District Director"', "District Director identity")
    require(director_block, "Health 1400", "District Director durability")
    for marker in (
        "DDIR A 10 A_Look",
        "DDIR F 4 Bright",
        "DDIR J 5 Bright",
        "DDIR O -1",
        'SeeSound "coh/directoridle"',
        'PainSound "coh/directorhit"',
        'DeathSound "coh/directordown"',
        'A_PlaySound("coh/directorattack"',
        'A_PlaySound("coh/directorstamp"',
        'A_PlaySound("coh/directorphase"',
    ):
        require(director_block, marker, "District Director signature presentation")
    if "RMGR " in director_block:
        raise AssertionError("District Director still references Regional Manager sprite frames")
    if "CheckoutFuse" in director_block or "SupervisorClearanceToken" in director_block:
        raise AssertionError("District Director DECORATE must not own objective progression state")

    require(generator, "def generate_district_director_assets", "District Director deterministic generator")
    require(generator, 'for frame in "ABCDEFGHIJKLMNO"', "District Director complete frame generation")
    require(build, "from generate_district_director_assets import generate_district_director_assets", "director generator import")
    require(build, "generate_district_director_assets(GAME)", "director generator build invocation")

    for cue in ("coh/directoridle", "coh/directorattack", "coh/directorphase", "coh/directorstamp", "coh/directorhit", "coh/directordown"):
        require(sndinfo, cue, "District Director SNDINFO cue")

    require(zscript, "class ManagementBoardroomReviewSequence : Actor", "boardroom review sequence")
    require(review_block, 'p.CountInv("ManagementBoardroomReviewPending")', "pending review gate")
    require(review_block, "elapsed >= 35 * 4", "first boardroom response timing")
    require(review_block, "elapsed >= 35 * 7", "second boardroom warning timing")
    require(review_block, "elapsed >= 35 * 9", "second boardroom response timing")
    require(review_block, "elapsed >= 35 * 10", "boardroom review completion timing")
    require(review_block, 'Actor.Spawn("ScannerTurret", Pos)', "first review response")
    require(review_block, 'Actor.Spawn("AngrySelfCheckout", Pos)', "second review response")
    require(review_block, 'p.A_GiveInventory("CheckoutFuse", 1)', "authoritative final power hand-off")
    require(review_block, 'p.A_TakeInventory("ManagementBoardroomReviewPending", 1)', "review pending cleanup")

    require(zscript, "class ManagementDirectorArrivalSpawner : Actor", "director arrival spawner")
    require(arrival_block, 'p.CountInv("CheckoutFuse") < 3', "full-power director gate")
    require(arrival_block, "arrivalTic = Level.maptime + 35 * 4", "director warning time")
    require(arrival_block, 'p.A_StartSound("coh/directorphase", CHAN_AUTO)', "director-specific arrival warning")
    require(arrival_block, 'director.A_StartSound("coh/directorphase", CHAN_BODY)', "director-specific arrival cue")
    require(arrival_block, 'Actor.Spawn("DistrictDirector", Pos)', "director spawn")

    require(zscript, "class ManagementExecutiveAuditSpawner : Actor", "executive audit pressure")
    require(audit_block, 'p.CountInv("ManagementBoardroomReviewPending") > 0', "review pressure pause")
    require(audit_block, "nextAuditTic = Level.maptime + 35 * 8", "post-review recovery window")
    require(audit_block, "responseTic = Level.maptime + 35 * 2", "audit warning time")
    require(audit_block, "delaySeconds = 32", "stage-two audit cadence")
    require(audit_block, "delaySeconds = 22", "Hell Rush audit cadence")
    require(audit_block, 'Actor.Spawn("ScannerTurret", Pos)', "stage-two audit response")
    require(audit_block, 'Actor.Spawn("CartOfDoom", Pos)', "Hell Rush audit response")

    require(management_doc, "# MAP06 — Management Floor", "Management Floor documentation title")
    require(management_doc, "Executive Access circuits", "Management Floor circuit documentation")
    require(management_doc, "10-second Boardroom Review", "Management Floor review documentation")
    require(management_doc, "`4 / 7 / 9 / 10`", "Management Floor review timing documentation")
    require(management_doc, "Executive Audit", "Management Floor Overtime documentation")
    require(management_doc, "`32 / 22`", "Management Floor audit cadence documentation")
    require(management_doc, "DDIR", "District Director unique sprite documentation")
    require(management_doc, "deterministic project-owned cue families", "District Director audio documentation")
    require(management_doc, "Management Floor — Synergy Funeral", "Management Floor music documentation")
    require(management_doc, "No proprietary Doom, Star Wars", "Management Floor legal asset documentation")

    require(build, '(GAME / "DECORATE_MANAGEMENT").read_text', "DECORATE packaging")
    require(build, '(GAME / "ZSCRIPT_MANAGEMENT").read_text', "ZScript packaging")
    require(build, '"MAP06"', "MAP06 packaging")

    validate_director_assets()

    if not PK3.is_file():
        raise AssertionError("built PK3 is missing; run python tools/build.py first")

    with zipfile.ZipFile(PK3) as archive:
        names = set(archive.namelist())
        if "maps/MAP06.wad" not in names:
            raise AssertionError("built PK3 is missing maps/MAP06.wad")
        packed_decorate = archive.read("DECORATE").decode("utf-8")
        packed_zscript = archive.read("ZSCRIPT").decode("utf-8")
        packed_mapinfo = archive.read("MAPINFO").decode("utf-8")
        packed_map06 = textmap_from_wad(archive.read("maps/MAP06.wad"))
        missing_assets = set(DIRECTOR_SPRITES + DIRECTOR_SOUNDS) - names
        if missing_assets:
            raise AssertionError(f"PK3 is missing District Director assets: {sorted(missing_assets)}")

    require(packed_decorate, "actor ManagementBoardroomReviewPending : Inventory", "PK3 DECORATE boardroom state")
    require(packed_decorate, "actor DistrictDirector : RegionalManager", "PK3 DECORATE District Director")
    require(packed_decorate, "DDIR A 10 A_Look", "PK3 District Director unique sprite states")
    require(packed_zscript, "class ManagementBoardroomReviewSequence : Actor", "PK3 ZScript boardroom review")
    require(packed_zscript, "class ManagementDirectorArrivalSpawner : Actor", "PK3 ZScript director arrival")
    require(packed_zscript, "class ManagementExecutiveAuditSpawner : Actor", "PK3 ZScript executive audit")
    require(packed_mapinfo, '17160 = "ManagementBoardroomReviewSequence"', "PK3 MAPINFO boardroom review registration")

    expected_textmap = map_text.rstrip() + "\n"
    if packed_map06 != expected_textmap:
        raise AssertionError("built MAP06 TEXTMAP is not byte-exact with game/MAP06.udmf")

    print("PASS: Management Floor boardroom review + unique District Director + Executive Audit contract")


if __name__ == "__main__":
    main()
