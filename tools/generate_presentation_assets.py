from __future__ import annotations

from pathlib import Path
import math
import struct
import wave
import zlib

RGBA = tuple[int, int, int, int]


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


def _rect(pixels: list[RGBA], width: int, height: int, x1: int, y1: int, x2: int, y2: int, color: RGBA) -> None:
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(width - 1, x2), min(height - 1, y2)
    for y in range(y1, y2 + 1):
        row = y * width
        for x in range(x1, x2 + 1):
            pixels[row + x] = color


def _memo_sprite(path: Path) -> None:
    width, height = 40, 52
    transparent = (0, 0, 0, 0)
    paper = (231, 225, 197, 255)
    shadow = (29, 34, 36, 220)
    ink = (58, 65, 66, 255)
    warning = (230, 181, 49, 255)
    stamp = (177, 48, 53, 255)
    pixels = [transparent] * (width * height)

    _rect(pixels, width, height, 7, 6, 35, 48, shadow)
    _rect(pixels, width, height, 4, 3, 32, 45, paper)
    _rect(pixels, width, height, 4, 3, 32, 10, warning)
    _rect(pixels, width, height, 8, 14, 28, 16, ink)
    _rect(pixels, width, height, 8, 20, 26, 21, ink)
    _rect(pixels, width, height, 8, 25, 29, 26, ink)
    _rect(pixels, width, height, 8, 30, 23, 31, ink)
    _rect(pixels, width, height, 16, 35, 30, 41, stamp)
    _rect(pixels, width, height, 18, 37, 28, 39, paper)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _compressor_reset_sprite(path: Path) -> None:
    width, height = 52, 60
    transparent = (0, 0, 0, 0)
    shadow = (2, 5, 10, 220)
    panel = (7, 17, 28, 255)
    steel = (24, 48, 64, 255)
    cyan = (98, 229, 255, 255)
    blue = (0, 136, 255, 255)
    ice = (218, 248, 255, 255)
    amber = (240, 177, 48, 255)
    pixels = [transparent] * (width * height)

    _rect(pixels, width, height, 8, 7, 47, 57, shadow)
    _rect(pixels, width, height, 5, 4, 44, 54, panel)
    _rect(pixels, width, height, 5, 4, 44, 7, cyan)
    _rect(pixels, width, height, 5, 51, 44, 54, blue)
    _rect(pixels, width, height, 5, 4, 8, 54, blue)
    _rect(pixels, width, height, 41, 4, 44, 54, cyan)
    _rect(pixels, width, height, 12, 12, 37, 20, steel)
    _rect(pixels, width, height, 15, 14, 20, 18, ice)
    _rect(pixels, width, height, 23, 14, 28, 18, cyan)
    _rect(pixels, width, height, 31, 14, 34, 18, blue)
    _rect(pixels, width, height, 13, 26, 36, 42, steel)
    _rect(pixels, width, height, 18, 29, 31, 39, amber)
    _rect(pixels, width, height, 21, 26, 28, 31, ice)
    _rect(pixels, width, height, 13, 46, 36, 47, cyan)
    _rect(pixels, width, height, 13, 49, 36, 50, blue)
    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _memo_sound(path: Path) -> None:
    rate = 22050
    duration = 0.34
    total = int(rate * duration)
    frames = bytearray()
    for index in range(total):
        t = index / rate
        attack = min(1.0, t / 0.015)
        release = min(1.0, max(0.0, (duration - t) / 0.08))
        envelope = attack * release
        value = (
            math.sin(2.0 * math.pi * 880.0 * t) * 0.20
            + math.sin(2.0 * math.pi * 1320.0 * t) * 0.10
        ) * envelope
        sample = int(max(-1.0, min(1.0, value)) * 32767)
        frames.extend(struct.pack("<h", sample))

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(frames)


def generate_presentation_assets(game_dir: Path) -> None:
    _memo_sprite(game_dir / "sprites" / "CMEMA0.png")
    _compressor_reset_sprite(game_dir / "sprites" / "FCRSA0.png")
    _memo_sound(game_dir / "sounds" / "memo.wav")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_presentation_assets(root / "game")
    print("Generated CHECKOUT OF HELL presentation assets.")
