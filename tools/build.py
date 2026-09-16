from pathlib import Path
import zipfile
import struct

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

MAPS = ["MAP01", "MAP02"]
ROOT_LUMPS = ["DECORATE", "MAPINFO", "LANGUAGE", "ZSCRIPT", "SNDINFO"]
ASSET_DIRS = ["textures", "flats", "sprites", "sounds"]


def make_udmf_wad(map_name: str, path: Path) -> None:
    textmap = (GAME / f"{map_name}.udmf").read_bytes()
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


built_maps = []
for map_name in MAPS:
    map_wad = DIST / f"{map_name}.wad"
    make_udmf_wad(map_name, map_wad)
    built_maps.append(map_wad)

pk3 = DIST / "checkout-of-hell-prototype.pk3"
with zipfile.ZipFile(pk3, "w", zipfile.ZIP_DEFLATED) as archive:
    for lump in ROOT_LUMPS:
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
