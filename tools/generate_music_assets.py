from pathlib import Path
import struct

PPQN = 96


def _vlq(value: int) -> bytes:
    """Encode a non-negative MIDI variable-length quantity."""
    if value < 0:
        raise ValueError("MIDI delta time cannot be negative")

    buffer = value & 0x7F
    value >>= 7
    while value:
        buffer = (buffer << 8) | ((value & 0x7F) | 0x80)
        value >>= 7

    encoded = bytearray()
    while True:
        encoded.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break
    return bytes(encoded)


class MidiTrack:
    def __init__(self) -> None:
        self.events: list[tuple[int, int, bytes]] = []

    def add(self, tick: int, order: int, data: bytes) -> None:
        self.events.append((tick, order, data))

    def meta(self, tick: int, meta_type: int, payload: bytes, order: int = -20) -> None:
        self.add(tick, order, bytes([0xFF, meta_type]) + _vlq(len(payload)) + payload)

    def program(self, tick: int, channel: int, program: int) -> None:
        self.add(tick, -10, bytes([0xC0 | channel, program]))

    def control(self, tick: int, channel: int, controller: int, value: int) -> None:
        self.add(tick, -9, bytes([0xB0 | channel, controller, value]))

    def note(self, tick: int, duration: int, channel: int, note: int, velocity: int) -> None:
        self.add(tick, 1, bytes([0x90 | channel, note, velocity]))
        self.add(tick + duration, 0, bytes([0x80 | channel, note, 0]))

    def build(self, end_tick: int) -> bytes:
        self.meta(end_tick, 0x2F, b"", order=99)
        payload = bytearray()
        previous_tick = 0

        for tick, order, data in sorted(self.events, key=lambda event: (event[0], event[1])):
            del order
            payload += _vlq(tick - previous_tick)
            payload += data
            previous_tick = tick

        return b"MTrk" + struct.pack(">I", len(payload)) + bytes(payload)


def _make_track(
    name: str,
    tempo_bpm: int,
    bars: int,
    chords: list[tuple[int, int, int]],
    melody: list[tuple[int, float, int, float, int]],
    chimes: list[tuple[int, float, tuple[int, ...], int]] | None = None,
    drums: list[tuple[float, int, int]] | None = None,
) -> bytes:
    track = MidiTrack()
    beat = PPQN
    bar = beat * 4
    microseconds_per_quarter = round(60_000_000 / tempo_bpm)

    track.meta(0, 0x03, name.encode("ascii"))
    track.meta(0, 0x51, microseconds_per_quarter.to_bytes(3, "big"))
    track.meta(0, 0x58, bytes([4, 2, 24, 8]))

    # General MIDI programs are deliberately conservative so the tracks remain readable
    # on the different synth backends a GZDoom player may use.
    track.program(0, 0, 88)  # New Age Pad
    track.program(0, 1, 48)  # String Ensemble
    track.program(0, 2, 11)  # Vibraphone

    for channel, volume, pan, reverb in (
        (0, 58, 54, 88),
        (1, 48, 74, 78),
        (2, 72, 64, 64),
    ):
        track.control(0, channel, 7, volume)
        track.control(0, channel, 10, pan)
        track.control(0, channel, 91, reverb)

    # Slow two-bar drones create the empty-store bed without masking combat cues.
    for bar_index in range(0, bars, 2):
        chord = chords[(bar_index // 2) % len(chords)]
        duration = bar * 2 - 12
        for voice, note in enumerate(chord):
            track.note(bar_index * bar, duration, 0, note, 30 - voice * 2)
            track.note(bar_index * bar + beat * 2, duration - beat * 2, 1, note + 12, 16)

    # Sparse recurring motifs leave long sections of negative space for creepy ambience.
    for cycle_start in range(0, bars, 8):
        for bar_offset, beat_offset, note, duration_beats, velocity in melody:
            bar_index = cycle_start + bar_offset
            if bar_index >= bars:
                continue
            tick = bar_index * bar + int(beat_offset * beat)
            track.note(tick, int(duration_beats * beat), 2, note, velocity)

    if chimes:
        for cycle_start in range(0, bars, 8):
            for bar_offset, beat_offset, notes, velocity in chimes:
                bar_index = cycle_start + bar_offset
                if bar_index >= bars:
                    continue
                tick = bar_index * bar + int(beat_offset * beat)
                for index, note in enumerate(notes):
                    track.note(tick + index * 12, beat // 2, 2, note, max(1, velocity - index * 2))

    if drums:
        # Channel 10/zero-based 9 is percussion. These very low-velocity hits are used as
        # distant warehouse machinery rather than a conventional action beat.
        for bar_index in range(bars):
            for beat_offset, note, velocity in drums:
                track.note(bar_index * bar + int(beat_offset * beat), 8, 9, note, velocity)

    end_tick = bars * bar
    midi_track = track.build(end_tick)
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQN)
    return header + midi_track


def generate_music_assets(game_dir: Path) -> None:
    music_dir = game_dir / "music"
    music_dir.mkdir(parents=True, exist_ok=True)

    closing_time = _make_track(
        "Closing Time - Empty Aisles",
        tempo_bpm=54,
        bars=24,
        chords=[
            (45, 52, 57),
            (43, 50, 55),
            (41, 48, 53),
            (40, 47, 52),
        ],
        melody=[
            (1, 1.5, 69, 1.0, 32),
            (1, 3.0, 67, 0.5, 25),
            (3, 0.5, 64, 1.5, 28),
            (3, 3.25, 62, 0.5, 20),
            (5, 2.0, 65, 1.0, 29),
            (7, 1.0, 60, 2.0, 24),
        ],
        chimes=[
            (0, 3.5, (76, 83), 42),
            (4, 3.5, (74, 81), 35),
        ],
    )

    warehouse = _make_track(
        "Warehouse 13.5 - Forklift Graveyard",
        tempo_bpm=60,
        bars=24,
        chords=[
            (38, 45, 50),
            (36, 43, 48),
            (35, 42, 47),
            (33, 40, 45),
        ],
        melody=[
            (0, 2.0, 62, 0.75, 27),
            (2, 1.0, 59, 1.0, 23),
            (2, 3.0, 57, 0.5, 20),
            (4, 0.5, 60, 1.25, 28),
            (6, 2.5, 55, 1.0, 22),
        ],
        drums=[
            (0.0, 36, 18),
            (2.0, 41, 14),
        ],
    )

    frozen_foods = _make_track(
        "Frozen Foods - Compressor Choir",
        tempo_bpm=52,
        bars=24,
        chords=[
            (42, 49, 54),
            (40, 47, 52),
            (38, 45, 50),
            (37, 44, 49),
        ],
        melody=[
            (0, 3.0, 73, 0.5, 26),
            (2, 0.5, 70, 1.0, 24),
            (3, 3.0, 68, 0.75, 20),
            (5, 1.5, 75, 0.5, 28),
            (7, 0.5, 66, 1.5, 22),
        ],
        chimes=[
            (1, 3.25, (80, 87), 34),
            (5, 3.25, (78, 85), 30),
        ],
        drums=[
            (0.0, 36, 11),
            (3.0, 41, 9),
        ],
    )

    (music_dir / "D_COH01.mid").write_bytes(closing_time)
    (music_dir / "D_COH02.mid").write_bytes(warehouse)
    (music_dir / "D_COH03.mid").write_bytes(frozen_foods)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_music_assets(root / "game")
    print("Generated original CHECKOUT OF HELL MIDI soundtrack assets.")
