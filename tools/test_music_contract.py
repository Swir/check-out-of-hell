from pathlib import Path
import re
import struct
import tempfile
import zipfile

from generate_music_assets import PPQN, generate_music_assets

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"
MAPINFO = GAME / "MAPINFO"
BUILD = ROOT / "tools" / "build.py"

TRACKS = {
    "D_COH01.mid": b"Closing Time - Empty Aisles",
    "D_COH02.mid": b"Warehouse 13.5 - Forklift Graveyard",
    "D_COH03.mid": b"Frozen Foods - Compressor Choir",
    "D_COH04.mid": b"Electronics - Dead Pixel Choir",
    "D_COH05.mid": b"Customer Service - Please Hold Forever",
}
MAP_TRACKS = {
    "MAP01": "D_COH01",
    "MAP02": "D_COH02",
    "MAP03": "D_COH03",
    "MAP04": "D_COH04",
    "MAP05": "D_COH05",
}
LUMPS = tuple(filename.removesuffix(".mid") for filename in TRACKS)

if not PK3.exists():
    raise SystemExit("Build output missing. Run: python tools/build.py")

mapinfo = MAPINFO.read_text(encoding="utf-8")
for lump_name in LUMPS:
    if f'music = "{lump_name}"' not in mapinfo:
        raise SystemExit(f"MAPINFO is not wired to original soundtrack lump {lump_name}")

if len(set(MAP_TRACKS.values())) != len(MAP_TRACKS):
    raise SystemExit("Playable departments must not share soundtrack mappings")

for map_name, lump_name in MAP_TRACKS.items():
    block = re.search(
        rf'map\s+{re.escape(map_name)}\s+"[^"]+"\s*\{{(.*?)\}}',
        mapinfo,
        flags=re.DOTALL,
    )
    if not block:
        raise SystemExit(f"MAPINFO is missing playable department block {map_name}")
    if f'music = "{lump_name}"' not in block.group(1):
        raise SystemExit(f"{map_name} must use its authored soundtrack lump {lump_name}")

for inherited in ("$MUSIC_RUNNIN", "$MUSIC_STALKS"):
    if inherited in mapinfo:
        raise SystemExit(f"Playable departments must not use inherited base-game music: {inherited}")

build_source = BUILD.read_text(encoding="utf-8")
for marker in (
    "from generate_music_assets import generate_music_assets",
    'ASSET_DIRS = ["textures", "flats", "sprites", "sounds", "music"]',
    "generate_music_assets(GAME)",
):
    if marker not in build_source:
        raise SystemExit(f"Build pipeline is missing soundtrack integration: {marker}")


def validate_midi(name: str, data: bytes, track_name: bytes) -> None:
    if len(data) < 64:
        raise SystemExit(f"{name} is unexpectedly small")
    if data[:4] != b"MThd":
        raise SystemExit(f"{name} does not start with an SMF header")

    header_length, midi_format, track_count, division = struct.unpack(">IHHH", data[4:14])
    if header_length != 6 or midi_format != 0 or track_count != 1:
        raise SystemExit(f"{name} must be deterministic single-track Standard MIDI format 0")
    if division != PPQN:
        raise SystemExit(f"{name} uses unexpected PPQN {division}; expected {PPQN}")
    if data[14:18] != b"MTrk":
        raise SystemExit(f"{name} is missing its MTrk chunk")

    track_length = struct.unpack(">I", data[18:22])[0]
    if track_length != len(data) - 22:
        raise SystemExit(f"{name} has an invalid MTrk length")
    if track_name not in data:
        raise SystemExit(f"{name} is missing its authored track-name marker")
    if b"\xFF\x51\x03" not in data:
        raise SystemExit(f"{name} is missing a tempo meta event")
    if not data.endswith(b"\xFF\x2F\x00"):
        raise SystemExit(f"{name} is missing a clean end-of-track event")

    # The generator deliberately emits explicit note-on statuses rather than running status.
    audible_note_ons = sum(data.count(bytes([0x90 | channel])) for channel in (0, 1, 2, 9))
    if audible_note_ons < 30:
        raise SystemExit(f"{name} has too little authored musical content ({audible_note_ons} note-ons)")


with tempfile.TemporaryDirectory() as temp_dir:
    temp_game = Path(temp_dir) / "game"
    generate_music_assets(temp_game)

    generated = {}
    for filename, track_name in TRACKS.items():
        data = (temp_game / "music" / filename).read_bytes()
        validate_midi(filename, data, track_name)
        generated[filename] = data

        built_asset = GAME / "music" / filename
        if not built_asset.exists():
            raise SystemExit(f"Build did not generate {built_asset.relative_to(ROOT)}")
        if built_asset.read_bytes() != data:
            raise SystemExit(f"{filename} is not deterministic across generation passes")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    packaged_mapinfo = archive.read("MAPINFO").decode("utf-8")

    for filename, expected in generated.items():
        archive_name = f"music/{filename}"
        if archive_name not in names:
            raise SystemExit(f"Packaged PK3 is missing {archive_name}")
        packaged = archive.read(archive_name)
        if packaged != expected:
            raise SystemExit(f"Packaged {archive_name} differs from deterministic generated source")

    for map_name, lump_name in MAP_TRACKS.items():
        block = re.search(
            rf'map\s+{re.escape(map_name)}\s+"[^"]+"\s*\{{(.*?)\}}',
            packaged_mapinfo,
            flags=re.DOTALL,
        )
        if not block or f'music = "{lump_name}"' not in block.group(1):
            raise SystemExit(f"Packaged MAPINFO lost soundtrack mapping {map_name} -> {lump_name}")

print("Original soundtrack contract: PASS")
