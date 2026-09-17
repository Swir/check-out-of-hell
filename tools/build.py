from pathlib import Path
import struct
import wave
import zipfile

from generate_assets import generate_assets
from generate_combat_assets import generate_combat_assets
from generate_vehicle_enemy_assets import generate_vehicle_enemy_assets
from generate_regional_manager_assets import generate_regional_manager_assets
from generate_presentation_assets import generate_presentation_assets
from generate_overtime_assets import generate_overtime_assets
from generate_environment_assets import generate_environment_assets
from generate_combat_audio_polish import generate_combat_audio_polish

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

MAPS = ["MAP01", "MAP02"]
ROOT_LUMPS = ["DECORATE", "MAPINFO", "LANGUAGE", "ZSCRIPT", "SNDINFO"]
ASSET_DIRS = ["textures", "flats", "sprites", "sounds"]
MAP_LAYER_SUFFIXES = ["OVERTIME", "ENVIRONMENT"]


def map_source(map_name: str) -> bytes:
    chunks = [(GAME / f"{map_name}.udmf").read_text(encoding="utf-8").rstrip()]
    for suffix in MAP_LAYER_SUFFIXES:
        extension = GAME / f"{map_name}_{suffix}.udmf"
        if extension.exists():
            chunks.append(extension.read_text(encoding="utf-8").rstrip())
    return ("\n\n".join(chunks) + "\n").encode("utf-8")


def make_udmf_wad(map_name: str, path: Path) -> None:
    textmap = map_source(map_name)
    lumps = [("TEXTMAP", textmap), ("ENDMAP", b"")]
    data_offset = 12
    blob = bytearray()
    directory = bytearray()
    offsets = []

    current = data_offset
    for name, data in lumps:
        offsets.append((current, len(data), name))
        blob.extend(data)
        current += len(data)

    dir_offset = data_offset + len(blob)
    for offset, size, name in offsets:
        directory.extend(
            struct.pack("<II8s", offset, size, name.encode("ascii")[:8].ljust(8, b"\0"))
        )

    header = struct.pack("<4sII", b"PWAD", len(lumps), dir_offset)
    path.write_bytes(header + blob + directory)


def pad_short_wavs(sound_dir: Path, min_frames: int = 4000) -> None:
    """Pad intentionally staccato generated cues with silence for stable decoder tails."""
    for path in sorted(sound_dir.glob("*.wav")):
        with wave.open(str(path), "rb") as source:
            params = source.getparams()
            frames = source.readframes(params.nframes)
        if params.nframes >= min_frames:
            continue
        missing = min_frames - params.nframes
        silence = b"\0" * missing * params.nchannels * params.sampwidth
        with wave.open(str(path), "wb") as target:
            target.setparams(params)
            target.writeframes(frames + silence)


def decorate_payload() -> bytes:
    """Compose the core actors and optional subsystem actors into one DECORATE lump."""
    chunks = [
        (GAME / "DECORATE").read_text(encoding="utf-8").rstrip(),
        (GAME / "DECORATE_OVERTIME").read_text(encoding="utf-8").rstrip(),
        (GAME / "DECORATE_ENVIRONMENT").read_text(encoding="utf-8").rstrip(),
    ]
    return ("\n\n".join(chunks) + "\n").encode("utf-8")


def zscript_payload() -> bytes:
    """Compose gameplay ZScript and small compatibility/persistence extensions."""
    chunks = [
        (GAME / "ZSCRIPT").read_text(encoding="utf-8").rstrip(),
        (GAME / "ZSCRIPT_SAVELOAD").read_text(encoding="utf-8").rstrip(),
    ]
    return ("\n\n".join(chunks) + "\n").encode("utf-8")


generate_assets(GAME)
generate_combat_assets(GAME)
generate_vehicle_enemy_assets(GAME)
generate_regional_manager_assets(GAME)
generate_presentation_assets(GAME)
generate_overtime_assets(GAME)
generate_environment_assets(GAME)
generate_combat_audio_polish(GAME)
pad_short_wavs(GAME / "sounds")

built_maps = []
for map_name in MAPS:
    map_wad = DIST / f"{map_name}.wad"
    make_udmf_wad(map_name, map_wad)
    built_maps.append(map_wad)

pk3 = DIST / "checkout-of-hell-prototype.pk3"
with zipfile.ZipFile(pk3, "w", zipfile.ZIP_DEFLATED) as archive:
    for lump in ROOT_LUMPS:
        if lump == "DECORATE":
            archive.writestr("DECORATE", decorate_payload())
        elif lump == "ZSCRIPT":
            archive.writestr("ZSCRIPT", zscript_payload())
        else:
            archive.write(GAME / lump, lump)

    for asset_dir in ASSET_DIRS:
        directory = GAME / asset_dir
        if not directory.exists():
            continue
        for asset in sorted(p for p in directory.rglob("*") if p.is_file()):
            archive.write(asset, asset.relative_to(GAME).as_posix())

    for map_wad in built_maps:
        archive.write(map_wad, f"maps/{map_wad.name}")

print(f"Built: {pk3}")
for map_wad in built_maps:
    print(f"Map:   {map_wad}")
