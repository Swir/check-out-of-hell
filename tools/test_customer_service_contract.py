from __future__ import annotations

from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"


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
        raise AssertionError(f"MAP05 is missing DoomEdNum {doomednum}")
    body = match.group("body")
    x = re.search(r"\bx\s*=\s*(-?\d+(?:\.\d+)?)\s*;", body)
    y = re.search(r"\by\s*=\s*(-?\d+(?:\.\d+)?)\s*;", body)
    if not x or not y:
        raise AssertionError(f"MAP05 DoomEdNum {doomednum} is missing coordinates")
    return float(x.group(1)), float(y.group(1))


def textmap_from_wad(blob: bytes) -> str:
    if len(blob) < 12:
        raise AssertionError("MAP05.wad is too small")
    magic, lump_count, directory_offset = struct.unpack_from("<4sII", blob, 0)
    if magic not in {b"PWAD", b"IWAD"}:
        raise AssertionError(f"MAP05.wad has invalid magic {magic!r}")

    for index in range(lump_count):
        entry = directory_offset + index * 16
        if entry + 16 > len(blob):
            raise AssertionError("MAP05.wad directory is truncated")
        offset, size, raw_name = struct.unpack_from("<II8s", blob, entry)
        name = raw_name.rstrip(b"\0").decode("ascii")
        if name == "TEXTMAP":
            payload = blob[offset : offset + size]
            if len(payload) != size:
                raise AssertionError("MAP05 TEXTMAP payload is truncated")
            return payload.decode("utf-8")
    raise AssertionError("MAP05.wad does not contain TEXTMAP")


def main() -> None:
    map_text = (GAME / "MAP05.udmf").read_text(encoding="utf-8")
    mapinfo = (GAME / "MAPINFO").read_text(encoding="utf-8")
    decorate = (GAME / "DECORATE_CUSTOMER_SERVICE").read_text(encoding="utf-8")
    zscript = (GAME / "ZSCRIPT_CUSTOMER_SERVICE").read_text(encoding="utf-8")
    build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")

    # MAP05 must keep two real circuit repairs and replace the former third loose fuse with one
    # physical refund terminal plus exactly one save-safe timed audit sequence.
    if count_type(map_text, 17111) != 2:
        raise AssertionError("MAP05 must contain exactly two physical CheckoutFuse repairs")
    if count_type(map_text, 17151) != 1:
        raise AssertionError("MAP05 must contain exactly one refund authorization spawner")
    if count_type(map_text, 17152) != 1:
        raise AssertionError("MAP05 must contain exactly one refund audit sequence")
    require(map_text, "twelve-second hold objective", "MAP05 objective explanation")

    # Department-specific Overtime must be deterministic, optional to mitigate and kept off the
    # central service lane: one fresh-entry cleanup, one reset station and one complaint anchor.
    for doomednum, label in (
        (17153, "fresh-entry initializer"),
        (17154, "queue reset station"),
        (17155, "complaint queue anchor"),
    ):
        if count_type(map_text, doomednum) != 1:
            raise AssertionError(f"MAP05 must contain exactly one {label}")

    reset_x, reset_y = thing_xy(map_text, 17154)
    queue_x, queue_y = thing_xy(map_text, 17155)
    if reset_x < 600 or queue_x > -600:
        raise AssertionError("queue reset and complaint pressure must remain on opposite outer lanes")
    if abs(reset_x) < 500 or abs(queue_x) < 500:
        raise AssertionError("Customer Service queue-pressure anchors must stay out of the center lane")
    if abs(reset_y - queue_y) < 120:
        raise AssertionError("queue reset must cost meaningful movement away from the complaint anchor")

    require(
        mapinfo,
        '17151 = "CustomerServiceRefundAuthorizationSpawner"',
        "MAPINFO refund terminal DoomEdNum",
    )
    require(
        mapinfo,
        '17152 = "CustomerServiceRefundAuditSequence"',
        "MAPINFO refund audit DoomEdNum",
    )
    require(
        mapinfo,
        '17153 = "CustomerServiceDepartmentInitSpawner"',
        "MAPINFO Customer Service initializer DoomEdNum",
    )
    require(
        mapinfo,
        '17154 = "CustomerServiceQueueResetSpawner"',
        "MAPINFO queue reset DoomEdNum",
    )
    require(
        mapinfo,
        '17155 = "CustomerServiceComplaintQueueSpawner"',
        "MAPINFO complaint queue DoomEdNum",
    )
    require(mapinfo, 'map MAP05 "Customer Service"', "MAP05 registration")
    require(mapinfo, 'next = "MAP01"', "campaign loop")

    require(decorate, "actor CustomerServiceRefundPending : Inventory", "pending token")
    require(
        decorate,
        "actor CustomerServiceRefundAuthorization : CustomInventory",
        "physical refund terminal",
    )
    require(decorate, 'A_GiveInventory("CustomerServiceRefundPending", 1)', "terminal hand-off")
    require(decorate, "Hold the service desk", "readable pickup instruction")
    require(
        decorate,
        "actor CustomerServiceQueueResetToken : Inventory",
        "queue reset state token",
    )
    require(
        decorate,
        "actor CustomerServiceQueueReset : CustomInventory",
        "physical queue reset control",
    )
    require(
        decorate,
        'A_GiveInventory("CustomerServiceQueueResetToken", 1)',
        "queue reset hand-off",
    )
    require(decorate, "Overtime is still active", "non-combat-off pickup wording")

    require(
        zscript,
        "class CustomerServiceRefundAuthorizationSpawner : Actor",
        "terminal spawner",
    )
    require(
        zscript,
        "class CustomerServiceRefundAuditSequence : Actor",
        "audit sequence",
    )
    require(zscript, 'p.CountInv("CheckoutFuse")', "shared authoritative progress")
    require(zscript, "elapsed >= 35 * 2", "first response timing")
    require(zscript, "elapsed >= 35 * 7", "second response timing")
    require(zscript, "elapsed >= 35 * 10", "third response timing")
    require(zscript, "elapsed >= 35 * 12", "audit completion timing")
    require(zscript, 'Actor.Spawn("AngrySelfCheckout", Pos)', "first queue response")
    require(zscript, 'Actor.Spawn("ScannerTurret", Pos)', "second queue response")
    require(zscript, 'Actor.Spawn("CartOfDoom", Pos)', "third queue response")
    require(zscript, 'p.A_GiveInventory("CheckoutFuse", 1)', "authoritative final repair")
    require(zscript, 'p.A_TakeInventory("CustomerServiceRefundPending", 1)', "pending cleanup")

    require(
        zscript,
        "class CustomerServiceDepartmentInitSpawner : Actor",
        "fresh-entry queue-state cleanup",
    )
    require(
        zscript,
        'p.A_TakeInventory("CustomerServiceQueueResetToken", 1)',
        "department-local reset cleanup",
    )
    require(
        zscript,
        "class CustomerServiceQueueResetSpawner : Actor",
        "optional queue reset spawner",
    )
    require(
        zscript,
        'p.CountInv("CheckoutFuse") < 1',
        "first-repair queue reset gate",
    )
    require(
        zscript,
        "class CustomerServiceComplaintQueueSpawner : Actor",
        "department complaint pressure",
    )
    require(zscript, "CheckoutShiftDirector.GetOvertimeStage()", "shared Overtime stage gate")
    require(zscript, "Level.maptime + 35 * 20", "first complaint grace period")
    require(zscript, "Level.maptime + 35 * 2", "complaint warning time")
    require(zscript, "delaySeconds = 38", "stage-one complaint cadence")
    require(zscript, "delaySeconds = 30", "stage-two complaint cadence")
    require(zscript, "delaySeconds = 22", "Hell Rush complaint cadence")
    require(zscript, 'p.CountInv("CustomerServiceRefundPending") > 0', "refund-audit pressure pause")
    require(zscript, "Level.maptime + 35 * 8", "post-audit complaint recovery window")
    require(zscript, 'p.CountInv("CustomerServiceQueueResetToken") > 0', "queue-only safety gate")
    if 'A_TakeInventory("CheckoutOvertime' in zscript or 'A_TakeInventory("SupervisorClearanceToken"' in zscript:
        raise AssertionError("Customer Service queue reset must not disable global Overtime or management")

    require(
        build,
        '(GAME / "DECORATE_CUSTOMER_SERVICE").read_text',
        "DECORATE packaging",
    )
    require(
        build,
        '(GAME / "ZSCRIPT_CUSTOMER_SERVICE").read_text',
        "ZScript packaging",
    )

    if not PK3.is_file():
        raise AssertionError("built PK3 is missing; run python tools/build.py first")

    with zipfile.ZipFile(PK3) as archive:
        names = set(archive.namelist())
        if "maps/MAP05.wad" not in names:
            raise AssertionError("built PK3 is missing maps/MAP05.wad")
        packed_decorate = archive.read("DECORATE").decode("utf-8")
        packed_zscript = archive.read("ZSCRIPT").decode("utf-8")
        packed_mapinfo = archive.read("MAPINFO").decode("utf-8")
        packed_map05 = textmap_from_wad(archive.read("maps/MAP05.wad"))

    require(
        packed_decorate,
        "actor CustomerServiceRefundAuthorization : CustomInventory",
        "PK3 DECORATE objective actor",
    )
    require(
        packed_decorate,
        "actor CustomerServiceQueueReset : CustomInventory",
        "PK3 DECORATE queue reset",
    )
    require(
        packed_zscript,
        "class CustomerServiceRefundAuditSequence : Actor",
        "PK3 ZScript objective sequence",
    )
    require(
        packed_zscript,
        "class CustomerServiceComplaintQueueSpawner : Actor",
        "PK3 ZScript complaint pressure",
    )
    require(
        packed_mapinfo,
        '17152 = "CustomerServiceRefundAuditSequence"',
        "PK3 MAPINFO refund registration",
    )
    require(
        packed_mapinfo,
        '17155 = "CustomerServiceComplaintQueueSpawner"',
        "PK3 MAPINFO complaint registration",
    )

    expected_textmap = map_text.rstrip() + "\n"
    if packed_map05 != expected_textmap:
        raise AssertionError("built MAP05 TEXTMAP is not byte-exact with game/MAP05.udmf")

    print("PASS: Customer Service refund audit + complaint queue contract")


if __name__ == "__main__":
    main()
