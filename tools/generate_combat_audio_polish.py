from __future__ import annotations

from pathlib import Path
import math
import struct
import wave

# freq set, duration, volume, sweep, noise amount, variant count
COMBAT_AUDIO_FAMILIES: dict[str, tuple[tuple[float, ...], float, float, float, float, int]] = {
    "mopswing": ((140.0, 220.0), 0.24, 0.30, 0.95, 0.10, 3),
    "managerattack": ((310.0, 155.0), 0.42, 0.27, -0.35, 0.06, 3),
    "managerdown": ((180.0, 90.0, 60.0), 0.85, 0.31, -0.45, 0.08, 2),
    "ripperfire": ((125.0, 240.0, 510.0), 0.30, 0.34, -0.55, 0.12, 3),
    "rippercycle": ((92.0, 145.0), 0.26, 0.25, 0.35, 0.08, 3),
    "checkoutidle": ((380.0, 760.0), 0.30, 0.15, 0.02, 0.025, 2),
    "checkoutattack": ((820.0, 410.0), 0.34, 0.27, -0.38, 0.08, 3),
    "checkouthit": ((250.0, 180.0), 0.24, 0.22, -0.20, 0.13, 3),
    "checkoutdown": ((210.0, 105.0, 70.0), 0.66, 0.30, -0.48, 0.10, 2),
    "pricefire": ((660.0, 930.0), 0.22, 0.25, -0.32, 0.10, 4),
    "pricelabel": ((1180.0, 590.0), 0.22, 0.17, -0.12, 0.04, 3),
    "canlaunch": ((90.0, 170.0, 360.0), 0.34, 0.33, -0.44, 0.09, 3),
    "canexplode": ((76.0, 52.0, 132.0), 0.56, 0.38, -0.55, 0.18, 4),
    "scanneridle": ((440.0, 880.0), 0.28, 0.14, 0.02, 0.025, 2),
    "scannerattack": ((980.0, 490.0), 0.27, 0.26, -0.38, 0.06, 3),
    "scannerhit": ((330.0, 220.0), 0.24, 0.20, -0.18, 0.10, 3),
    "scannerdown": ((180.0, 92.0, 55.0), 0.64, 0.31, -0.50, 0.10, 2),
    "cartidle": ((105.0, 210.0), 0.34, 0.15, 0.08, 0.06, 2),
    "cartcharge": ((125.0, 255.0, 510.0), 0.40, 0.30, 0.52, 0.10, 3),
    "carthit": ((160.0, 94.0), 0.25, 0.24, -0.22, 0.15, 3),
    "cartdown": ((118.0, 72.0, 43.0), 0.72, 0.32, -0.52, 0.14, 2),
    "palletidle": ((84.0, 168.0), 0.36, 0.16, 0.04, 0.06, 2),
    "palletattack": ((112.0, 224.0, 448.0), 0.38, 0.30, 0.42, 0.11, 3),
    "pallethit": ((148.0, 91.0), 0.25, 0.24, -0.20, 0.14, 3),
    "palletdown": ((108.0, 66.0, 39.0), 0.76, 0.32, -0.55, 0.13, 2),
    "regionalidle": ((74.0, 111.0, 148.0), 0.46, 0.19, -0.10, 0.035, 2),
    "regionalattack": ((190.0, 390.0, 760.0), 0.48, 0.32, -0.28, 0.08, 3),
    "regionalphase": ((96.0, 192.0, 384.0, 768.0), 0.78, 0.35, 0.40, 0.06, 2),
    "regionalstamp": ((76.0, 240.0, 520.0), 0.55, 0.39, -0.42, 0.12, 3),
    "regionalhit": ((180.0, 108.0), 0.28, 0.27, -0.25, 0.13, 3),
    "regionaldown": ((120.0, 72.0, 42.0), 0.92, 0.37, -0.60, 0.14, 2),
}

PITCH_VARIANTS = (0.955, 0.985, 1.015, 1.055)


def _seed_for(name: str, variant: int) -> int:
    seed = 0x51F15EED ^ (variant * 0x9E3779B1)
    for index, char in enumerate(name):
        seed ^= (index + 1) * ord(char) * 0x45D9F3B
        seed &= 0xFFFFFFFF
    return seed or 1


def _write_variant(
    path: Path,
    name: str,
    variant: int,
    freqs: tuple[float, ...],
    duration: float,
    volume: float,
    sweep: float,
    noise_amount: float,
) -> None:
    rate = 22050
    total = max(4000, int(duration * rate))
    pitch = PITCH_VARIANTS[(variant - 1) % len(PITCH_VARIANTS)]
    seed = _seed_for(name, variant)
    frames = bytearray()
    norm = sum(1.0 / (index + 1) for index in range(len(freqs)))

    for sample_index in range(total):
        t = sample_index / rate
        progress = min(1.0, t / max(duration, 0.001))
        attack = min(1.0, t / 0.012)
        release = min(1.0, max(0.0, (duration - t) / 0.075))
        envelope = attack * release

        tone = 0.0
        for tone_index, freq in enumerate(freqs):
            current = freq * pitch * (1.0 + sweep * progress)
            tone += math.sin(2.0 * math.pi * current * t) / (tone_index + 1)
        tone /= max(norm, 1.0)

        seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
        noise = (((seed >> 8) & 0xFFFFFF) / 0x7FFFFF) - 1.0

        # A short deterministic transient gives impacts and mechanisms definition without
        # increasing gameplay loudness or changing actor timing.
        transient = 0.0
        if t < 0.035:
            transient = math.sin(2.0 * math.pi * (1700.0 + variant * 83.0) * t) * (1.0 - t / 0.035)

        value = (tone * volume + noise * noise_amount + transient * noise_amount * 0.55) * envelope
        value = max(-0.88, min(0.88, value))
        frames.extend(struct.pack("<h", int(value * 32767)))

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(frames)


def generate_combat_audio_polish(game_dir: Path) -> None:
    sound_dir = game_dir / "sounds"
    for cue_name, (freqs, duration, volume, sweep, noise_amount, variants) in COMBAT_AUDIO_FAMILIES.items():
        for variant in range(1, variants + 1):
            _write_variant(
                sound_dir / f"{cue_name}_v{variant}.wav",
                cue_name,
                variant,
                freqs,
                duration,
                volume,
                sweep,
                noise_amount,
            )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_combat_audio_polish(root / "game")
    print(
        f"Generated {sum(spec[-1] for spec in COMBAT_AUDIO_FAMILIES.values())} "
        "deterministic CHECKOUT OF HELL combat-audio variants."
    )
