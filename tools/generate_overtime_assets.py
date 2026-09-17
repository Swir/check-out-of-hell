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


def _warning_sprite(path: Path) -> None:
    width, height = 48, 48
    transparent = (0, 0, 0, 0)
    yellow = (244, 194, 54, 255)
    amber = (255, 132, 28, 255)
    red = (211, 43, 50, 255)
    dark = (35, 31, 28, 255)
    white = (255, 245, 210, 255)
    pixels = [transparent] * (width * height)

    _rect(pixels, width, height, 13, 7, 34, 38, dark)
    _rect(pixels, width, height, 15, 9, 32, 36, yellow)
    _rect(pixels, width, height, 18, 12, 29, 29, amber)
    _rect(pixels, width, height, 20, 14, 27, 27, red)
    _rect(pixels, width, height, 23, 16, 24, 23, white)
    _rect(pixels, width, height, 23, 26, 24, 27, white)
    _rect(pixels, width, height, 10, 39, 37, 42, dark)
    _write_png(path, width, height, pixels, (width // 2, height - 3))


def _arc_sprite(path: Path, frame: int) -> None:
    width, height = 64, 34
    transparent = (0, 0, 0, 0)
    blue = (62, 173, 255, 255)
    pale = (202, 240, 255, 255)
    white = (255, 255, 255, 255)
    warning = (244, 194, 54, 210)
    pixels = [transparent] * (width * height)

    # Floor warning stripe keeps the damage area readable before the arc detonates.
    stripe_y = 29
    for x in range(8, 56):
        color = warning if ((x // 5) + frame) % 2 == 0 else (60, 50, 36, 180)
        _rect(pixels, width, height, x, stripe_y, x, stripe_y + 2, color)

    points = [
        (8, 27),
        (16, 18 + (frame % 2) * 3),
        (23, 24 - (frame % 3) * 2),
        (31, 10 + frame * 2),
        (39, 22 - (frame % 2) * 4),
        (47, 14 + (frame % 3) * 2),
        (56, 27),
    ]
    for index in range(len(points) - 1):
        x1, y1 = points[index]
        x2, y2 = points[index + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1))
        for step in range(steps + 1):
            t = step / max(1, steps)
            x = round(x1 + (x2 - x1) * t)
            y = round(y1 + (y2 - y1) * t)
            _rect(pixels, width, height, x - 1, y - 1, x + 1, y + 1, blue)
            _rect(pixels, width, height, x, y, x, y, pale if frame < 2 else white)

    _write_png(path, width, height, pixels, (width // 2, height - 2))


def _write_sound(path: Path, samples: list[float], rate: int = 22050) -> None:
    frames = bytearray()
    for value in samples:
        sample = int(max(-1.0, min(1.0, value)) * 32767)
        frames.extend(struct.pack("<h", sample))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(frames)


def _alarm_sound(path: Path) -> None:
    rate = 22050
    duration = 0.72
    total = int(rate * duration)
    samples: list[float] = []
    for index in range(total):
        t = index / rate
        pulse = 1.0 if int(t * 7.0) % 2 == 0 else 0.35
        attack = min(1.0, t / 0.02)
        release = min(1.0, max(0.0, (duration - t) / 0.08))
        value = (
            math.sin(2.0 * math.pi * 620.0 * t) * 0.24
            + math.sin(2.0 * math.pi * 930.0 * t) * 0.10
        ) * pulse * attack * release
        samples.append(value)
    _write_sound(path, samples, rate)


def _arc_sound(path: Path) -> None:
    rate = 22050
    duration = 0.42
    total = int(rate * duration)
    samples: list[float] = []
    seed = 0xC0FFEE
    for index in range(total):
        t = index / rate
        seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
        noise = ((seed >> 8) / 0xFFFFFF) * 2.0 - 1.0
        envelope = min(1.0, t / 0.01) * min(1.0, max(0.0, (duration - t) / 0.07))
        tone = math.sin(2.0 * math.pi * (185.0 + 420.0 * t) * t)
        samples.append((noise * 0.24 + tone * 0.16) * envelope)
    _write_sound(path, samples, rate)


def generate_overtime_assets(game_dir: Path) -> None:
    _warning_sprite(game_dir / "sprites" / "OWRNA0.png")
    for frame, letter in enumerate("ABCD"):
        _arc_sprite(game_dir / "sprites" / f"OARC{letter}0.png", frame)
    _alarm_sound(game_dir / "sounds" / "overtime_alarm.wav")
    _arc_sound(game_dir / "sounds" / "overtime_arc.wav")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_overtime_assets(root / "game")
    print("Generated CHECKOUT OF HELL Overtime hazard assets.")
