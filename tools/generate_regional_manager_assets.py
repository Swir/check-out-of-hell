from __future__ import annotations

from pathlib import Path

from generate_assets import _canvas, _disc, _line, _rect, _write_png, _write_tone


def _regional_manager_sprite(path: Path, frame: str) -> None:
    """Draw the Regional Manager as a readable corporate-horror boss silhouette."""
    w, h = 124, 126
    p = _canvas(w, h, (0, 0, 0, 0))

    suit = (38, 45, 59, 255)
    suit_light = (62, 74, 92, 255)
    shirt = (210, 216, 211, 255)
    tie = (197, 51, 54, 255)
    skin = (201, 157, 119, 255)
    dark = (25, 29, 35, 255)
    red = (241, 64, 61, 255)
    amber = (244, 182, 49, 255)
    teal = (45, 210, 194, 255)
    paper = (238, 233, 211, 255)

    if frame in "LMNO":
        sink = {"L": 0, "M": 9, "N": 18, "O": 23}[frame]
        base_y = 84 + sink
        _rect(p, w, h, 20, base_y, 105, min(h - 4, base_y + 18), suit)
        _rect(p, w, h, 35, base_y - 14, 91, base_y + 5, shirt)
        _line(p, w, h, 40, base_y - 4, 92, base_y + 10, tie, 5)
        if frame in "LM":
            _disc(p, w, h, 88, base_y - 10, 8, red)
        _write_png(path, w, h, p, (w // 2, h - 3))
        return

    phase = "ABCD".index(frame) if frame in "ABCD" else 0
    bob = (0, -2, 0, 2)[phase]
    attack_push = {"E": 2, "F": 6, "G": 9, "H": 4, "I": 7, "J": 10, "K": -2}.get(frame, 0)

    body_x = 61 + attack_push
    head_y = 24 + bob
    torso_y = 48 + bob

    # broad suit silhouette
    _rect(p, w, h, body_x - 31, torso_y, body_x + 31, torso_y + 50, suit)
    _rect(p, w, h, body_x - 23, torso_y + 4, body_x + 23, torso_y + 42, shirt)
    _line(p, w, h, body_x, torso_y + 7, body_x + 2, torso_y + 40, tie, 6)
    _line(p, w, h, body_x - 29, torso_y + 15, body_x - 43, torso_y + 45, suit_light, 10)
    _line(p, w, h, body_x + 29, torso_y + 15, body_x + 43, torso_y + 45, suit_light, 10)

    # unsettling head and management visor
    _disc(p, w, h, body_x, head_y, 22, skin)
    _rect(p, w, h, body_x - 18, head_y - 5, body_x + 18, head_y + 4, dark)
    _disc(p, w, h, body_x - 10, head_y, 4, red)
    _disc(p, w, h, body_x + 10, head_y, 4, red)
    _rect(p, w, h, body_x - 12, head_y + 10, body_x + 12, head_y + 13, dark)

    # badge / KPI panel
    _rect(p, w, h, body_x + 11, torso_y + 10, body_x + 25, torso_y + 23, amber)
    _rect(p, w, h, body_x + 14, torso_y + 13, body_x + 22, torso_y + 20, teal)

    # legs
    _rect(p, w, h, body_x - 25, torso_y + 48, body_x - 6, 114 + bob, suit)
    _rect(p, w, h, body_x + 6, torso_y + 48, body_x + 25, 114 + bob, suit)
    _rect(p, w, h, body_x - 29, 112 + bob, body_x - 3, 120 + bob, dark)
    _rect(p, w, h, body_x + 3, 112 + bob, body_x + 29, 120 + bob, dark)

    if frame in "EFG":
        # red-tape barrage tell
        _rect(p, w, h, body_x + 33, torso_y + 18, min(w - 4, body_x + 51), torso_y + 35, paper)
        _line(p, w, h, body_x + 35, torso_y + 22, min(w - 5, body_x + 50), torso_y + 22, red, 2)
        _line(p, w, h, body_x + 35, torso_y + 28, min(w - 5, body_x + 50), torso_y + 28, red, 2)
        _disc(p, w, h, min(w - 6, body_x + 48), torso_y + 27, 10 if frame == "G" else 7, (241, 64, 61, 85))
    elif frame in "HIJ":
        # phase-two stamp attack tell
        _rect(p, w, h, max(3, body_x - 51), torso_y + 18, body_x - 31, torso_y + 35, dark)
        _rect(p, w, h, max(5, body_x - 48), torso_y + 20, body_x - 34, torso_y + 31, red)
        _disc(p, w, h, max(8, body_x - 43), torso_y + 27, 13 if frame == "J" else 8, (244, 182, 49, 90))
        _line(p, w, h, body_x - 19, head_y - 12, body_x + 20, head_y + 12, red, 3)
    elif frame == "K":
        _line(p, w, h, body_x - 31, torso_y + 7, body_x + 30, torso_y + 45, amber, 4)
        _line(p, w, h, body_x + 31, torso_y + 7, body_x - 30, torso_y + 45, amber, 4)

    _write_png(path, w, h, p, (w // 2, h - 3))


def _red_tape_sprite(path: Path, frame: str) -> None:
    w = h = 48
    p = _canvas(w, h, (0, 0, 0, 0))
    paper = (242, 235, 211, 255)
    red = (232, 54, 57, 255)
    amber = (247, 185, 49, 255)
    dark = (42, 45, 50, 255)

    if frame in "AB":
        slant = 5 if frame == "A" else -5
        _rect(p, w, h, 9, 12, 38, 34, paper)
        _line(p, w, h, 12, 18, 34, 18 + slant // 2, red, 3)
        _line(p, w, h, 12, 25, 34, 25 - slant // 2, dark, 2)
        _line(p, w, h, 12, 30, 30, 30, dark, 2)
    else:
        radius = 10 if frame == "C" else 17
        _disc(p, w, h, 24, 24, radius, (232, 54, 57, 135))
        _line(p, w, h, 8, 24, 40, 24, amber, 4)
        _line(p, w, h, 24, 8, 24, 40, amber, 4)
    _write_png(path, w, h, p, (w // 2, h // 2))


def _stamp_sprite(path: Path, frame: str) -> None:
    w = h = 52
    p = _canvas(w, h, (0, 0, 0, 0))
    dark = (35, 39, 47, 255)
    red = (235, 61, 58, 255)
    amber = (248, 184, 48, 255)

    if frame in "AB":
        _rect(p, w, h, 18, 6, 33, 26, dark)
        _rect(p, w, h, 12, 24, 39, 38, red)
        _rect(p, w, h, 15, 28, 36, 34, amber)
        if frame == "B":
            _disc(p, w, h, 26, 31, 13, (235, 61, 58, 90))
    else:
        radius = 12 if frame == "C" else 20
        _disc(p, w, h, 26, 26, radius, (248, 184, 48, 120))
        _disc(p, w, h, 26, 26, max(4, radius // 2), red)
    _write_png(path, w, h, p, (w // 2, h // 2))


def generate_regional_manager_assets(game_dir: Path) -> None:
    (game_dir / "sprites").mkdir(parents=True, exist_ok=True)
    (game_dir / "sounds").mkdir(parents=True, exist_ok=True)

    for frame in "ABCDEFGHIJKLMNO":
        _regional_manager_sprite(game_dir / "sprites" / f"RMGR{frame}0.png", frame)
    for frame in "ABCD":
        _red_tape_sprite(game_dir / "sprites" / f"RTAP{frame}0.png", frame)
        _stamp_sprite(game_dir / "sprites" / f"STMP{frame}0.png", frame)

    _write_tone(game_dir / "sounds" / "regionalidle.wav", (74.0, 111.0, 148.0), 0.46, 0.18, -0.10)
    _write_tone(game_dir / "sounds" / "regionalattack.wav", (190.0, 390.0, 760.0), 0.48, 0.31, -0.28)
    _write_tone(game_dir / "sounds" / "regionalphase.wav", (96.0, 192.0, 384.0, 768.0), 0.78, 0.34, 0.40)
    _write_tone(game_dir / "sounds" / "regionalstamp.wav", (76.0, 240.0, 520.0), 0.55, 0.38, -0.42)
    _write_tone(game_dir / "sounds" / "regionalhit.wav", (180.0, 108.0), 0.28, 0.25, -0.25)
    _write_tone(game_dir / "sounds" / "regionaldown.wav", (120.0, 72.0, 42.0), 0.92, 0.36, -0.60)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_regional_manager_assets(root / "game")
    print("Generated original Regional Manager boss presentation.")
