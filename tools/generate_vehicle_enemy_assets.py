from __future__ import annotations

from pathlib import Path

from generate_assets import _canvas, _disc, _line, _rect, _write_png, _write_tone


def _cart_sprite(path: Path, frame: str) -> None:
    """Draw a possessed supermarket cart with readable charge/death poses."""
    w, h = 104, 82
    p = _canvas(w, h, (0, 0, 0, 0))

    metal = (132, 145, 151, 255)
    metal_light = (195, 205, 209, 255)
    dark = (38, 43, 47, 255)
    red = (239, 73, 61, 255)
    amber = (242, 186, 47, 255)
    teal = (49, 209, 192, 255)

    if frame in "HIJK":
        fall = {"H": 0, "I": 5, "J": 10, "K": 13}[frame]
        top = 48 + fall
        _rect(p, w, h, 14, top, 90, min(h - 5, top + 16), dark)
        _rect(p, w, h, 23, top - 8, 78, min(h - 7, top + 7), metal)
        if frame in "HI":
            _line(p, w, h, 25, top - 3, 77, top + 9, red, 3)
        if frame == "H":
            _disc(p, w, h, 23, top + 15, 7, amber)
            _disc(p, w, h, 80, top + 15, 7, amber)
        _write_png(path, w, h, p, (w // 2, h - 2))
        return

    phase = "ABCD".index(frame) if frame in "ABCD" else 0
    bounce = (0, -2, 0, 2)[phase]
    shove = 0
    if frame == "E":
        shove = 4
    elif frame == "F":
        shove = 9
    elif frame == "G":
        shove = -3

    body_y = 25 + bounce
    left = 16 + shove
    right = 88 + shove

    # basket and handle
    _rect(p, w, h, left + 8, body_y + 8, right - 4, body_y + 40, metal)
    _rect(p, w, h, left + 12, body_y + 12, right - 8, body_y + 34, dark)
    for x in range(left + 18, right - 10, 10):
        _line(p, w, h, x, body_y + 13, x - 4, body_y + 33, metal_light, 2)
    _line(p, w, h, left + 10, body_y + 18, right - 8, body_y + 18, metal_light, 2)
    _line(p, w, h, left + 9, body_y + 28, right - 7, body_y + 28, metal_light, 2)
    _line(p, w, h, left + 3, body_y + 3, left + 14, body_y + 12, metal_light, 4)
    _line(p, w, h, left - 2, body_y + 1, left + 6, body_y + 2, dark, 5)

    # possessed face / scanner bar
    _rect(p, w, h, left + 24, body_y + 17, left + 52, body_y + 25, (22, 31, 34, 255))
    _disc(p, w, h, left + 31, body_y + 21, 3, red)
    _disc(p, w, h, left + 45, body_y + 21, 3, red)
    _rect(p, w, h, left + 27, body_y + 29, left + 50, body_y + 32, teal)

    # chassis and wheels
    _line(p, w, h, left + 12, body_y + 39, right - 2, body_y + 46, metal_light, 4)
    wheel_y = body_y + 50
    _disc(p, w, h, left + 18, wheel_y, 8, dark)
    _disc(p, w, h, right - 12, wheel_y, 8, dark)
    _disc(p, w, h, left + 18, wheel_y, 3, amber)
    _disc(p, w, h, right - 12, wheel_y, 3, amber)

    if frame in "EF":
        # charge tell: hot wheels + forward warning glow
        glow_radius = 9 if frame == "E" else 14
        _disc(p, w, h, min(w - 8, right + 2), body_y + 26, glow_radius, (239, 73, 61, 105))
        _line(p, w, h, right - 4, body_y + 26, min(w - 3, right + 11), body_y + 26, red, 4)
        _disc(p, w, h, left + 18, wheel_y, 11, (242, 186, 47, 70))
        _disc(p, w, h, right - 12, wheel_y, 11, (242, 186, 47, 70))
    elif frame == "G":
        _line(p, w, h, left + 14, body_y + 10, right - 8, body_y + 38, amber, 4)
        _line(p, w, h, right - 10, body_y + 10, left + 16, body_y + 38, amber, 4)

    _write_png(path, w, h, p, (w // 2, h - 2))


def _pallet_jack_sprite(path: Path, frame: str) -> None:
    """Draw a low possessed pallet jack with fork-lunge silhouettes."""
    w, h = 116, 88
    p = _canvas(w, h, (0, 0, 0, 0))

    yellow = (232, 169, 36, 255)
    yellow_dark = (131, 87, 18, 255)
    steel = (133, 145, 150, 255)
    dark = (35, 39, 42, 255)
    red = (237, 68, 58, 255)
    teal = (51, 211, 193, 255)

    if frame in "HIJK":
        sink = {"H": 0, "I": 5, "J": 10, "K": 13}[frame]
        y = 53 + sink
        _rect(p, w, h, 13, y, 102, min(h - 5, y + 14), yellow_dark)
        _line(p, w, h, 26, y - 5, 96, y + 8, steel, 5)
        _line(p, w, h, 84, y - 8, 32, y + 9, yellow, 4)
        if frame in "HI":
            _disc(p, w, h, 80, y - 2, 7, red)
        _write_png(path, w, h, p, (w // 2, h - 2))
        return

    phase = "ABCD".index(frame) if frame in "ABCD" else 0
    bob = (0, -2, 0, 2)[phase]
    lunge = 0
    if frame == "E":
        lunge = 6
    elif frame == "F":
        lunge = 13
    elif frame == "G":
        lunge = -2

    body_y = 38 + bob
    body_x = 54 + lunge

    # powered body and haunted status panel
    _rect(p, w, h, body_x, body_y, min(w - 8, body_x + 40), body_y + 28, yellow)
    _rect(p, w, h, body_x + 5, body_y + 6, min(w - 12, body_x + 34), body_y + 21, yellow_dark)
    _rect(p, w, h, body_x + 10, body_y + 8, min(w - 14, body_x + 30), body_y + 16, dark)
    _disc(p, w, h, body_x + 15, body_y + 12, 3, red)
    _disc(p, w, h, body_x + 25, body_y + 12, 3, red)
    _rect(p, w, h, body_x + 10, body_y + 19, min(w - 14, body_x + 30), body_y + 22, teal)

    # steering tiller
    _line(p, w, h, body_x + 30, body_y + 4, min(w - 8, body_x + 42), body_y - 24, steel, 5)
    _line(p, w, h, min(w - 9, body_x + 41), body_y - 24, min(w - 3, body_x + 48), body_y - 20, dark, 5)

    # fork rails point at the player
    fork_y = body_y + 27
    fork_end = max(6, 36 - lunge)
    _line(p, w, h, body_x + 4, fork_y, fork_end, fork_y + 4, steel, 5)
    _line(p, w, h, body_x + 7, fork_y + 8, fork_end + 2, fork_y + 13, steel, 5)
    _rect(p, w, h, fork_end - 2, fork_y + 2, fork_end + 9, fork_y + 6, yellow)
    _rect(p, w, h, fork_end, fork_y + 11, fork_end + 10, fork_y + 15, yellow)

    # wheels
    _disc(p, w, h, body_x + 7, body_y + 31, 7, dark)
    _disc(p, w, h, min(w - 8, body_x + 34), body_y + 31, 7, dark)

    if frame in "EF":
        # attack tell: fork tips and eyes pulse before impact
        _disc(p, w, h, fork_end + 2, fork_y + 4, 10 if frame == "F" else 7, (237, 68, 58, 95))
        _disc(p, w, h, fork_end + 4, fork_y + 13, 10 if frame == "F" else 7, (237, 68, 58, 95))
        _line(p, w, h, body_x + 13, body_y + 12, body_x + 28, body_y + 12, red, 3)
    elif frame == "G":
        _line(p, w, h, body_x + 3, body_y + 3, min(w - 8, body_x + 38), body_y + 26, red, 4)

    _write_png(path, w, h, p, (w // 2, h - 2))


def generate_vehicle_enemy_assets(game_dir: Path) -> None:
    (game_dir / "sprites").mkdir(parents=True, exist_ok=True)
    (game_dir / "sounds").mkdir(parents=True, exist_ok=True)

    for frame in "ABCDEFGHIJK":
        _cart_sprite(game_dir / "sprites" / f"CART{frame}0.png", frame)
        _pallet_jack_sprite(game_dir / "sprites" / f"PJCK{frame}0.png", frame)

    _write_tone(game_dir / "sounds" / "cartidle.wav", (118.0, 176.0, 236.0), 0.38, 0.16, -0.18)
    _write_tone(game_dir / "sounds" / "cartcharge.wav", (270.0, 520.0, 92.0), 0.42, 0.30, -0.48)
    _write_tone(game_dir / "sounds" / "carthit.wav", (190.0, 132.0), 0.24, 0.22, -0.24)
    _write_tone(game_dir / "sounds" / "cartdown.wav", (142.0, 88.0, 54.0), 0.68, 0.31, -0.52)

    _write_tone(game_dir / "sounds" / "palletidle.wav", (84.0, 126.0, 168.0), 0.40, 0.17, -0.15)
    _write_tone(game_dir / "sounds" / "palletattack.wav", (96.0, 310.0, 610.0), 0.45, 0.34, -0.50)
    _write_tone(game_dir / "sounds" / "pallethit.wav", (205.0, 118.0), 0.26, 0.23, -0.26)
    _write_tone(game_dir / "sounds" / "palletdown.wav", (126.0, 74.0, 42.0), 0.72, 0.33, -0.55)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_vehicle_enemy_assets(root / "game")
    print("Generated original Cart of Doom and Possessed Pallet Jack combat presentation.")
