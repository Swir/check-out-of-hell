from __future__ import annotations

from pathlib import Path

from generate_assets import _canvas, _disc, _line, _rect, _write_png, _write_tone


def _district_director_sprite(path: Path, frame: str) -> None:
    """Draw a distinct executive-horror silhouette for The District Director."""
    w, h = 132, 134
    p = _canvas(w, h, (0, 0, 0, 0))

    suit = (19, 29, 45, 255)
    suit_edge = (45, 71, 92, 255)
    shirt = (221, 232, 229, 255)
    cyan = (60, 218, 232, 255)
    magenta = (228, 57, 151, 255)
    amber = (247, 189, 62, 255)
    skin = (194, 146, 111, 255)
    dark = (12, 17, 26, 255)
    paper = (242, 239, 218, 255)
    red = (235, 66, 64, 255)

    if frame in "LMNO":
        sink = {"L": 0, "M": 10, "N": 20, "O": 26}[frame]
        base_y = 88 + sink
        _rect(p, w, h, 17, base_y, 114, min(h - 4, base_y + 20), suit)
        _rect(p, w, h, 31, base_y - 16, 94, base_y + 7, shirt)
        _line(p, w, h, 35, base_y - 5, 96, base_y + 12, cyan, 5)
        _rect(p, w, h, 79, base_y - 13, 101, base_y - 5, amber)
        if frame in "LM":
            _disc(p, w, h, 99, base_y - 10, 10, magenta)
        _write_png(path, w, h, p, (w // 2, h - 3))
        return

    phase = "ABCD".index(frame) if frame in "ABCD" else 0
    bob = (0, -2, 0, 2)[phase]
    attack_push = {"E": 1, "F": 4, "G": 7, "H": 2, "I": 5, "J": 8, "K": -2}.get(frame, 0)
    body_x = 65 + attack_push
    head_y = 25 + bob
    torso_y = 49 + bob

    # Tall, narrow executive silhouette: deliberately different from the broad Regional Manager.
    _rect(p, w, h, body_x - 27, torso_y, body_x + 27, torso_y + 54, suit)
    _rect(p, w, h, body_x - 18, torso_y + 5, body_x + 18, torso_y + 42, shirt)
    _line(p, w, h, body_x - 17, torso_y + 5, body_x, torso_y + 43, cyan, 5)
    _line(p, w, h, body_x + 17, torso_y + 5, body_x, torso_y + 43, magenta, 5)
    _line(p, w, h, body_x - 26, torso_y + 15, body_x - 44, torso_y + 48, suit_edge, 8)
    _line(p, w, h, body_x + 26, torso_y + 15, body_x + 44, torso_y + 48, suit_edge, 8)

    # Hollow boardroom face with a cyan KPI visor and asymmetric warning eye.
    _disc(p, w, h, body_x, head_y, 21, skin)
    _rect(p, w, h, body_x - 18, head_y - 7, body_x + 18, head_y + 5, dark)
    _rect(p, w, h, body_x - 15, head_y - 4, body_x + 10, head_y + 2, cyan)
    _disc(p, w, h, body_x + 12, head_y - 1, 5, magenta)
    _rect(p, w, h, body_x - 10, head_y + 11, body_x + 13, head_y + 14, dark)

    # Executive badge and split-color lapel make the silhouette readable during combat.
    _rect(p, w, h, body_x + 11, torso_y + 10, body_x + 24, torso_y + 24, amber)
    _rect(p, w, h, body_x + 14, torso_y + 13, body_x + 21, torso_y + 21, dark)

    _rect(p, w, h, body_x - 23, torso_y + 51, body_x - 5, 121 + bob, suit)
    _rect(p, w, h, body_x + 5, torso_y + 51, body_x + 23, 121 + bob, suit)
    _rect(p, w, h, body_x - 28, 118 + bob, body_x - 2, 126 + bob, dark)
    _rect(p, w, h, body_x + 2, 118 + bob, body_x + 28, 126 + bob, dark)

    if frame in "EFG":
        # Performance-review clipboard telegraphs the first attack family.
        _rect(p, w, h, body_x + 31, torso_y + 13, min(w - 4, body_x + 54), torso_y + 42, paper)
        _rect(p, w, h, body_x + 36, torso_y + 9, min(w - 6, body_x + 49), torso_y + 15, amber)
        _line(p, w, h, body_x + 35, torso_y + 23, min(w - 5, body_x + 51), torso_y + 23, magenta, 2)
        _line(p, w, h, body_x + 35, torso_y + 30, min(w - 5, body_x + 51), torso_y + 30, cyan, 2)
        if frame == "G":
            _disc(p, w, h, min(w - 8, body_x + 51), torso_y + 33, 11, (228, 57, 151, 90))
    elif frame in "HIJ":
        # Rage tell: an oversized glowing KPI stamp is raised before the radial paperwork burst.
        _rect(p, w, h, max(4, body_x - 56), torso_y + 10, body_x - 34, torso_y + 39, dark)
        _rect(p, w, h, max(7, body_x - 53), torso_y + 14, body_x - 37, torso_y + 34, cyan)
        _line(p, w, h, body_x - 48, torso_y + 18, body_x - 39, torso_y + 31, magenta, 3)
        _line(p, w, h, body_x - 39, torso_y + 18, body_x - 48, torso_y + 31, magenta, 3)
        _disc(p, w, h, max(10, body_x - 46), torso_y + 25, 14 if frame == "J" else 9, (60, 218, 232, 80))
    elif frame == "K":
        _line(p, w, h, body_x - 31, torso_y + 5, body_x + 31, torso_y + 48, red, 4)
        _line(p, w, h, body_x + 31, torso_y + 5, body_x - 31, torso_y + 48, amber, 4)

    _write_png(path, w, h, p, (w // 2, h - 3))


def generate_district_director_assets(game_dir: Path) -> None:
    sprites = game_dir / "sprites"
    sounds = game_dir / "sounds"
    sprites.mkdir(parents=True, exist_ok=True)
    sounds.mkdir(parents=True, exist_ok=True)

    for frame in "ABCDEFGHIJKLMNO":
        _district_director_sprite(sprites / f"DDIR{frame}0.png", frame)

    # Deterministic cue families keep the boss audibly distinct without introducing external assets.
    tone_sets = {
        "directoridle_v1": ((58.0, 91.0, 146.0), 0.46, 0.16, -0.08),
        "directoridle_v2": ((62.0, 104.0, 171.0), 0.44, 0.15, 0.06),
        "directorattack_v1": ((210.0, 420.0, 840.0), 0.46, 0.30, -0.24),
        "directorattack_v2": ((226.0, 452.0, 678.0), 0.43, 0.29, -0.18),
        "directorattack_v3": ((196.0, 392.0, 784.0), 0.49, 0.30, -0.30),
        "directorphase_v1": ((82.0, 164.0, 328.0, 656.0), 0.82, 0.33, 0.44),
        "directorphase_v2": ((92.0, 184.0, 368.0, 736.0), 0.78, 0.32, 0.38),
        "directorstamp_v1": ((88.0, 276.0, 612.0), 0.54, 0.38, -0.38),
        "directorstamp_v2": ((96.0, 304.0, 684.0), 0.52, 0.37, -0.34),
        "directorstamp_v3": ((80.0, 252.0, 566.0), 0.57, 0.38, -0.43),
        "directorhit_v1": ((202.0, 122.0), 0.29, 0.24, -0.24),
        "directorhit_v2": ((218.0, 130.0), 0.27, 0.23, -0.20),
        "directorhit_v3": ((188.0, 112.0), 0.31, 0.24, -0.28),
        "directordown_v1": ((136.0, 78.0, 43.0), 0.96, 0.35, -0.62),
        "directordown_v2": ((148.0, 86.0, 48.0), 0.92, 0.34, -0.56),
    }
    for name, (freqs, duration, volume, sweep) in tone_sets.items():
        _write_tone(sounds / f"{name}.wav", freqs, duration, volume, sweep)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_district_director_assets(root / "game")
    print("Generated original District Director boss presentation.")
