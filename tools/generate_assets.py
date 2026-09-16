from __future__ import annotations

from pathlib import Path
import math
import struct
import wave
import zlib

RGBA = tuple[int, int, int, int]


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_png(
    path: Path,
    width: int,
    height: int,
    pixels: list[RGBA],
    offset: tuple[int, int] | None = None,
) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    if offset is not None:
        payload += _png_chunk(b"grAb", struct.pack(">ii", offset[0], offset[1]))
    payload += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    payload += _png_chunk(b"IEND", b"")
    path.write_bytes(payload)


def _canvas(width: int, height: int, color: RGBA) -> list[RGBA]:
    return [color] * (width * height)


def _rect(pixels, width, height, x1, y1, x2, y2, color):
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(width - 1, x2), min(height - 1, y2)
    for y in range(y1, y2 + 1):
        base = y * width
        for x in range(x1, x2 + 1):
            pixels[base + x] = color


def _line_h(pixels, width, height, y, color, thickness=1):
    _rect(pixels, width, height, 0, y, width - 1, y + thickness - 1, color)


def _line_v(pixels, width, height, x, color, thickness=1):
    _rect(pixels, width, height, x, 0, x + thickness - 1, height - 1, color)


def _disc(pixels, width, height, cx, cy, radius, color):
    radius_sq = radius * radius
    for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= radius_sq:
                pixels[y * width + x] = color


def _line(pixels, width, height, x1, y1, x2, y2, color, thickness=1):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy), 1)
    for step in range(steps + 1):
        x = round(x1 + dx * step / steps)
        y = round(y1 + dy * step / steps)
        _rect(
            pixels,
            width,
            height,
            x - thickness // 2,
            y - thickness // 2,
            x + thickness // 2,
            y + thickness // 2,
            color,
        )


def _write_tone(path: Path, freqs: tuple[float, ...], duration: float, volume: float, sweep: float = 0.0) -> None:
    rate = 22050
    total = int(duration * rate)
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = bytearray()
    norm = sum(1.0 / (i + 1) for i in range(len(freqs)))
    for i in range(total):
        t = i / rate
        attack = min(1.0, t / 0.02)
        release = min(1.0, max(0.0, (duration - t) / 0.08))
        env = attack * release
        value = 0.0
        for index, freq in enumerate(freqs):
            current = freq * (1.0 + sweep * (t / duration))
            value += math.sin(2.0 * math.pi * current * t) / (index + 1)
        value = (value / norm) * volume * env
        sample = int(max(-1.0, min(1.0, value)) * 32767)
        frames.extend(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(frames)


def _wall(path: Path) -> None:
    w = h = 128
    p = _canvas(w, h, (52, 59, 64, 255))
    for y in range(0, h, 16):
        _line_h(p, w, h, y, (73, 81, 85, 255))
    for x in range(0, w, 32):
        _line_v(p, w, h, x, (65, 72, 77, 255))
    _rect(p, w, h, 0, 44, 127, 63, (24, 122, 137, 255))
    _rect(p, w, h, 0, 64, 127, 69, (238, 191, 54, 255))
    _write_png(path, w, h, p)


def _shelf(path: Path) -> None:
    w = h = 128
    p = _canvas(w, h, (27, 30, 33, 255))
    colors = [(194, 70, 63, 255), (44, 128, 164, 255), (209, 162, 57, 255), (91, 149, 84, 255), (151, 83, 155, 255)]
    for shelf_y in (20, 58, 96):
        _rect(p, w, h, 4, shelf_y, 123, shelf_y + 5, (117, 125, 128, 255))
        _rect(p, w, h, 7, shelf_y - 16, 120, shelf_y - 1, (45, 49, 53, 255))
        for i in range(10):
            x = 10 + i * 11
            _rect(p, w, h, x, shelf_y - 13, x + 7, shelf_y - 3, colors[i % len(colors)])
    _rect(p, w, h, 0, 116, 127, 127, (18, 20, 22, 255))
    _write_png(path, w, h, p)


def _staff(path: Path) -> None:
    w = h = 128
    p = _canvas(w, h, (38, 64, 74, 255))
    for x in range(0, w, 8):
        _line_v(p, w, h, x, (49, 79, 90, 255))
    _rect(p, w, h, 24, 40, 103, 76, (18, 25, 28, 255))
    _rect(p, w, h, 28, 44, 99, 72, (237, 190, 55, 255))
    _rect(p, w, h, 34, 50, 93, 66, (28, 35, 37, 255))
    for x in range(-24, 128, 24):
        for y in range(104, 128):
            start = x + (y - 104)
            for xx in range(start, start + 10):
                if 0 <= xx < w:
                    p[y * w + xx] = (220, 170, 40, 255)
    _write_png(path, w, h, p)


def _floor(path: Path) -> None:
    w = h = 64
    p = _canvas(w, h, (42, 45, 47, 255))
    tile = 16
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            c = (55, 59, 61, 255) if ((x // tile + y // tile) % 2 == 0) else (39, 42, 44, 255)
            _rect(p, w, h, x, y, x + tile - 1, y + tile - 1, c)
            _line_h(p, w, h, y, (75, 80, 82, 255))
            _line_v(p, w, h, x, (75, 80, 82, 255))
    _write_png(path, w, h, p)


def _ceiling(path: Path) -> None:
    w = h = 64
    p = _canvas(w, h, (169, 174, 170, 255))
    for x in (0, 32, 63):
        _line_v(p, w, h, x, (110, 115, 113, 255))
    for y in (0, 32, 63):
        _line_h(p, w, h, y, (110, 115, 113, 255))
    _rect(p, w, h, 9, 13, 54, 20, (235, 240, 225, 255))
    _rect(p, w, h, 9, 44, 54, 51, (225, 232, 220, 255))
    _write_png(path, w, h, p)


def _shutter_sprite(path: Path) -> None:
    w, h = 64, 96
    p = _canvas(w, h, (0, 0, 0, 0))
    _rect(p, w, h, 5, 4, 58, 91, (44, 70, 80, 255))
    _rect(p, w, h, 7, 6, 56, 89, (55, 86, 96, 255))
    for y in range(12, 88, 8):
        _line_h(p, w, h, y, (83, 111, 119, 255), 2)
    _rect(p, w, h, 10, 34, 53, 61, (238, 191, 54, 255))
    _rect(p, w, h, 15, 39, 48, 56, (21, 28, 31, 255))
    _write_png(path, w, h, p, (w // 2, h - 2))


def _fuse_sprite(path: Path) -> None:
    w, h = 32, 48
    p = _canvas(w, h, (0, 0, 0, 0))
    _rect(p, w, h, 5, 4, 26, 43, (38, 48, 50, 255))
    _rect(p, w, h, 7, 6, 24, 41, (61, 74, 77, 255))
    _rect(p, w, h, 9, 10, 22, 18, (237, 190, 55, 255))
    _rect(p, w, h, 14, 22, 17, 37, (82, 220, 148, 255))
    _rect(p, w, h, 11, 35, 20, 41, (82, 220, 148, 255))
    _write_png(path, w, h, p, (w // 2, h - 2))


def _stash_sprite(path: Path) -> None:
    w, h = 56, 40
    p = _canvas(w, h, (0, 0, 0, 0))
    _rect(p, w, h, 3, 9, 52, 36, (91, 58, 34, 255))
    _rect(p, w, h, 3, 4, 52, 13, (115, 74, 40, 255))
    _rect(p, w, h, 24, 9, 31, 36, (219, 187, 73, 255))
    _rect(p, w, h, 8, 20, 18, 27, (230, 222, 190, 255))
    _rect(p, w, h, 37, 20, 47, 27, (230, 222, 190, 255))
    _write_png(path, w, h, p, (w // 2, h - 2))


def _mop_sprite(path: Path, frame: str) -> None:
    w, h = 160, 112
    p = _canvas(w, h, (0, 0, 0, 0))
    dark = (35, 43, 48, 255)
    steel = (120, 139, 145, 255)
    cloth = (54, 176, 167, 255)
    cloth_light = (87, 218, 205, 255)
    glove = (228, 184, 82, 255)

    poses = {
        "A": ((100, 109), (68, 38), 16),
        "B": ((116, 109), (82, 31), 9),
        "C": ((116, 106), (47, 24), -10),
        "D": ((103, 109), (60, 35), 8),
    }
    start, end, head_tilt = poses[frame]
    _line(p, w, h, start[0], start[1], end[0], end[1], dark, 9)
    _line(p, w, h, start[0], start[1], end[0], end[1], steel, 5)

    hx, hy = end
    _line(p, w, h, hx - 25 + head_tilt, hy - 4, hx + 25 + head_tilt, hy + 5, dark, 10)
    _line(p, w, h, hx - 24 + head_tilt, hy - 4, hx + 24 + head_tilt, hy + 5, cloth, 7)
    for strand in (-18, -9, 0, 9, 18):
        _line(p, w, h, hx + strand + head_tilt, hy + 1, hx + strand - 3 + head_tilt, hy + 18, cloth_light if strand % 18 == 0 else cloth, 3)

    _rect(p, w, h, 78, 89, 98, 111, glove)
    _rect(p, w, h, 100, 96, 121, 111, glove)
    _write_png(path, w, h, p, (w // 2, h))


def _manager_sprite(path: Path, frame: str) -> None:
    w, h = 80, 104
    p = _canvas(w, h, (0, 0, 0, 0))
    suit = (34, 39, 48, 255)
    suit_light = (52, 58, 68, 255)
    shirt = (213, 218, 210, 255)
    tie = (183, 49, 53, 255)
    skin = (188, 137, 104, 255)
    eye = (245, 210, 68, 255)
    badge = (83, 201, 190, 255)
    shoe = (18, 20, 24, 255)

    if frame in "HIJK":
        y = 76 + (7 if frame in "JK" else 0)
        _rect(p, w, h, 12, y, 67, min(h - 4, y + 15), suit)
        _rect(p, w, h, 52, y - 5, 72, min(h - 5, y + 10), skin)
        _rect(p, w, h, 24, y - 3, 34, min(h - 3, y + 10), tie)
        _write_png(path, w, h, p, (w // 2, h - 3))
        return

    pain = frame == "G"
    attack = frame in "EF"
    walk_phase = "ABCD".index(frame) if frame in "ABCD" else 0
    body_x = 22 + (1 if walk_phase in (1, 2) else 0)
    _rect(p, w, h, body_x, 39, body_x + 36, 82, suit)
    _rect(p, w, h, body_x + 5, 41, body_x + 31, 49, shirt)
    _rect(p, w, h, body_x + 17, 47, body_x + 21, 72, tie)
    _rect(p, w, h, body_x + 25, 53, body_x + 33, 59, badge)
    _rect(p, w, h, 27, 15, 54, 39, skin)
    _rect(p, w, h, 30, 13, 52, 19, suit_light)
    _rect(p, w, h, 32, 25, 36, 28, eye)
    _rect(p, w, h, 45, 25, 49, 28, eye)

    if pain:
        _line(p, w, h, 24, 48, 10, 66, suit_light, 8)
        _line(p, w, h, 57, 48, 69, 65, suit_light, 8)
    elif attack:
        hand_y = 43 if frame == "E" else 35
        _line(p, w, h, 24, 48, 8, hand_y, suit_light, 8)
        _line(p, w, h, 57, 48, 72, hand_y, suit_light, 8)
        _disc(p, w, h, 8, hand_y, 5, skin)
        _disc(p, w, h, 72, hand_y, 5, skin)
    else:
        arm_shift = (-3, 2, 4, -1)[walk_phase]
        _line(p, w, h, 24, 48, 15 + arm_shift, 72, suit_light, 8)
        _line(p, w, h, 57, 48, 65 - arm_shift, 72, suit_light, 8)

    left_foot = 22 + (4 if walk_phase in (1, 2) else 0)
    right_foot = 48 - (4 if walk_phase in (1, 2) else 0)
    _rect(p, w, h, left_foot, 80, left_foot + 10, 99, suit)
    _rect(p, w, h, right_foot, 80, right_foot + 10, 99, suit)
    _rect(p, w, h, left_foot - 2, 96, left_foot + 12, 102, shoe)
    _rect(p, w, h, right_foot - 2, 96, right_foot + 12, 102, shoe)
    _write_png(path, w, h, p, (w // 2, h - 3))


def _memo_projectile(path: Path, frame: str) -> None:
    w = h = 40
    p = _canvas(w, h, (0, 0, 0, 0))
    if frame in "AB":
        angle = 0 if frame == "A" else 4
        _disc(p, w, h, 20, 20, 18, (255, 198, 58, 80))
        _rect(p, w, h, 7 + angle, 5, 31 - angle, 34, (235, 230, 205, 255))
        _rect(p, w, h, 10 + angle, 9, 28 - angle, 13, (187, 48, 52, 255))
        for y in (18, 23, 28):
            _rect(p, w, h, 11 + angle, y, 27 - angle, y + 1, (72, 82, 85, 255))
    else:
        radius = 11 if frame == "C" else 18
        _disc(p, w, h, 20, 20, radius, (244, 172, 44, 190))
        _disc(p, w, h, 20, 20, max(4, radius // 2), (250, 235, 150, 235))
    _write_png(path, w, h, p, (w // 2, h // 2))


def generate_assets(game_dir: Path) -> None:
    for folder in ("textures", "flats", "sprites", "sounds"):
        (game_dir / folder).mkdir(parents=True, exist_ok=True)

    _wall(game_dir / "textures" / "CHKWALL.png")
    _shelf(game_dir / "textures" / "CHKSHELF.png")
    _staff(game_dir / "textures" / "CHKSTAF.png")
    _floor(game_dir / "flats" / "CHKFLR.png")
    _ceiling(game_dir / "flats" / "CHKCEIL.png")
    _shutter_sprite(game_dir / "sprites" / "COSHA0.png")
    _fuse_sprite(game_dir / "sprites" / "COFUA0.png")
    _stash_sprite(game_dir / "sprites" / "COSTA0.png")

    for frame in "ABCD":
        _mop_sprite(game_dir / "sprites" / f"CMOP{frame}0.png", frame)
    for frame in "ABCDEFGHIJK":
        _manager_sprite(game_dir / "sprites" / f"MNGR{frame}0.png", frame)
    for frame in "ABCD":
        _memo_projectile(game_dir / "sprites" / f"MEMO{frame}0.png", frame)

    _write_tone(game_dir / "sounds" / "fuse.wav", (660.0, 990.0), 0.28, 0.25)
    _write_tone(game_dir / "sounds" / "shutter.wav", (95.0, 140.0), 0.70, 0.30, 0.25)
    _write_tone(game_dir / "sounds" / "bossalarm.wav", (165.0, 110.0), 1.00, 0.32)
    _write_tone(game_dir / "sounds" / "clockout.wav", (880.0, 1320.0), 0.50, 0.28)
    _write_tone(game_dir / "sounds" / "overtime.wav", (220.0, 330.0), 0.65, 0.25, 0.20)
    _write_tone(game_dir / "sounds" / "mopswing.wav", (140.0, 220.0), 0.22, 0.27, 1.10)
    _write_tone(game_dir / "sounds" / "managerattack.wav", (310.0, 155.0), 0.42, 0.25, -0.35)
    _write_tone(game_dir / "sounds" / "managerdown.wav", (180.0, 90.0, 60.0), 0.85, 0.30, -0.45)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_assets(root / "game")
    print("Generated original CHECKOUT OF HELL prototype art/audio assets.")
