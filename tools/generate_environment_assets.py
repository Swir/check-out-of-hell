from __future__ import annotations

from pathlib import Path
import math
import struct
import wave
import zlib

RGBA = tuple[int, int, int, int]

FONT: dict[str, tuple[str, ...]] = {
    " ": ("00000",) * 7,
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
}


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_png(path: Path, width: int, height: int, pixels: list[RGBA], offset: tuple[int, int]) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    payload += _png_chunk(b"grAb", struct.pack(">ii", offset[0], offset[1]))
    payload += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    payload += _png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _canvas(width: int, height: int) -> list[RGBA]:
    return [(0, 0, 0, 0)] * (width * height)


def _rect(pixels: list[RGBA], width: int, height: int, x1: int, y1: int, x2: int, y2: int, color: RGBA) -> None:
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(width - 1, x2), min(height - 1, y2)
    for y in range(y1, y2 + 1):
        base = y * width
        for x in range(x1, x2 + 1):
            pixels[base + x] = color


def _draw_text(
    pixels: list[RGBA], width: int, height: int, text: str, x: int, y: int, color: RGBA, scale: int = 1
) -> None:
    cursor = x
    for char in text.upper():
        glyph = FONT.get(char, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    _rect(
                        pixels,
                        width,
                        height,
                        cursor + gx * scale,
                        y + gy * scale,
                        cursor + gx * scale + scale - 1,
                        y + gy * scale + scale - 1,
                        color,
                    )
        cursor += 6 * scale


def _standing_sign(path: Path, line1: str, line2: str, accent: RGBA) -> None:
    width, height = 112, 104
    pixels = _canvas(width, height)
    edge = (24, 29, 34, 255)
    board = (52, 60, 66, 255)
    ink = (241, 236, 215, 255)
    pole = (103, 111, 114, 255)
    foot = (64, 70, 73, 255)

    _rect(pixels, width, height, 7, 6, 104, 50, edge)
    _rect(pixels, width, height, 11, 10, 100, 46, board)
    _rect(pixels, width, height, 11, 10, 100, 15, accent)
    _draw_text(pixels, width, height, line1, 15, 21, ink, 1)
    _draw_text(pixels, width, height, line2, 15, 33, accent, 1)
    _rect(pixels, width, height, 53, 51, 58, 92, pole)
    _rect(pixels, width, height, 35, 91, 76, 99, foot)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _lane_sign(path: Path) -> None:
    width, height = 64, 92
    pixels = _canvas(width, height)
    dark = (23, 29, 32, 255)
    yellow = (239, 190, 53, 255)
    cream = (240, 235, 218, 255)
    metal = (102, 111, 114, 255)
    _rect(pixels, width, height, 7, 5, 56, 38, dark)
    _rect(pixels, width, height, 10, 8, 53, 13, yellow)
    _draw_text(pixels, width, height, "LANE", 16, 17, cream)
    _draw_text(pixels, width, height, "06", 25, 28, yellow)
    _rect(pixels, width, height, 29, 39, 34, 82, metal)
    _rect(pixels, width, height, 18, 81, 45, 88, dark)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _cone(path: Path) -> None:
    width, height = 36, 44
    pixels = _canvas(width, height)
    orange = (236, 137, 41, 255)
    pale = (247, 223, 170, 255)
    dark = (70, 55, 41, 255)
    for y in range(5, 35):
        half = max(2, int((y - 2) * 0.34))
        _rect(pixels, width, height, 18 - half, y, 18 + half, y, orange)
    _rect(pixels, width, height, 10, 19, 26, 23, pale)
    _rect(pixels, width, height, 4, 35, 32, 41, dark)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _boxes(path: Path) -> None:
    width, height = 58, 48
    pixels = _canvas(width, height)
    cardboard = (132, 91, 49, 255)
    light = (163, 117, 65, 255)
    tape = (218, 187, 98, 255)
    mark = (48, 52, 48, 255)
    _rect(pixels, width, height, 4, 20, 31, 44, cardboard)
    _rect(pixels, width, height, 26, 10, 54, 44, light)
    _rect(pixels, width, height, 16, 20, 19, 44, tape)
    _rect(pixels, width, height, 38, 10, 42, 44, tape)
    _rect(pixels, width, height, 8, 27, 22, 29, mark)
    _rect(pixels, width, height, 31, 18, 49, 20, mark)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _snack(path: Path) -> None:
    width, height = 34, 28
    pixels = _canvas(width, height)
    wrapper = (49, 158, 153, 255)
    highlight = (89, 217, 204, 255)
    stripe = (237, 190, 53, 255)
    dark = (31, 38, 42, 255)
    _rect(pixels, width, height, 4, 5, 29, 22, dark)
    _rect(pixels, width, height, 6, 7, 27, 20, wrapper)
    _rect(pixels, width, height, 8, 9, 25, 11, stripe)
    _rect(pixels, width, height, 9, 15, 24, 17, highlight)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _fluorescent(path: Path, frame: str) -> None:
    width, height = 72, 20
    pixels = _canvas(width, height)
    casing = (86, 94, 96, 255)
    off = (75, 82, 82, 255)
    glow = {
        "A": (225, 235, 218, 255),
        "B": (135, 153, 145, 255),
        "C": (244, 246, 222, 255),
        "D": off,
    }[frame]
    _rect(pixels, width, height, 2, 2, 69, 17, casing)
    _rect(pixels, width, height, 7, 6, 64, 13, glow)
    _write_png(path, width, height, pixels, (width // 2, height // 2))


def _snack_sound(path: Path) -> None:
    rate = 22050
    duration = 0.42
    total = int(rate * duration)
    frames = bytearray()
    for index in range(total):
        t = index / rate
        attack = min(1.0, t / 0.012)
        release = min(1.0, max(0.0, (duration - t) / 0.09))
        chirp = 620.0 + 520.0 * (t / duration)
        value = (
            math.sin(2.0 * math.pi * chirp * t) * 0.18
            + math.sin(2.0 * math.pi * (chirp * 1.5) * t) * 0.08
        ) * attack * release
        sample = int(max(-1.0, min(1.0, value)) * 32767)
        frames.extend(struct.pack("<h", sample))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(frames)


def generate_environment_assets(game_dir: Path) -> None:
    sprites = game_dir / "sprites"
    _standing_sign(sprites / "CSIGA0.png", "CUSTOMER", "SERVICE", (75, 189, 180, 255))
    _standing_sign(sprites / "FSGNA0.png", "FROZEN", "FOODS", (88, 177, 220, 255))
    _standing_sign(sprites / "ESGNA0.png", "ELECTRONICS", "RETURNS", (213, 84, 90, 255))
    _lane_sign(sprites / "LSGNA0.png")
    _cone(sprites / "CONEA0.png")
    _boxes(sprites / "BOXEA0.png")
    _snack(sprites / "BRKSA0.png")
    for frame in "ABCD":
        _fluorescent(sprites / f"FLIT{frame}0.png", frame)
    _snack_sound(game_dir / "sounds" / "breaksnack.wav")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_environment_assets(root / "game")
    print("Generated CHECKOUT OF HELL Closing Time environment assets.")
