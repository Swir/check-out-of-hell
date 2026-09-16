from __future__ import annotations

from pathlib import Path

from generate_assets import _canvas, _disc, _line, _rect, _write_png, _write_tone


def _receipt_ripper_view(path: Path, frame: str) -> None:
    w, h = 176, 120
    p = _canvas(w, h, (0, 0, 0, 0))
    shell = (36, 43, 49, 255)
    shell_light = (65, 78, 86, 255)
    teal = (42, 185, 174, 255)
    paper = (236, 230, 202, 255)
    warning = (238, 188, 52, 255)
    glove = (226, 180, 82, 255)

    recoil = {"A": 0, "B": 8, "C": 13, "D": 5, "E": 2}[frame]
    body_y = 63 + recoil
    _rect(p, w, h, 45, body_y, 139, 108, shell)
    _rect(p, w, h, 55, body_y + 7, 129, 98, shell_light)
    _rect(p, w, h, 61, body_y + 14, 122, 86, teal)
    _rect(p, w, h, 71, body_y + 20, 112, 31 + body_y, paper)
    _rect(p, w, h, 76, body_y + 23, 107, body_y + 25, (87, 92, 92, 255))
    _rect(p, w, h, 76, body_y + 28, 104, body_y + 30, (87, 92, 92, 255))
    _rect(p, w, h, 50, body_y + 34, 61, body_y + 39, warning)
    _rect(p, w, h, 126, body_y + 34, 137, body_y + 39, warning)

    if frame in "BCD":
        strip_len = {"B": 20, "C": 34, "D": 24}[frame]
        _rect(p, w, h, 83, max(4, body_y - strip_len), 100, body_y - 1, paper)
        for yy in range(max(8, body_y - strip_len + 5), body_y - 4, 7):
            _rect(p, w, h, 86, yy, 97, yy + 1, (92, 95, 91, 255))

    if frame == "C":
        _disc(p, w, h, 91, max(8, body_y - 38), 12, (245, 206, 80, 110))

    _rect(p, w, h, 41, 96, 67, 119, glove)
    _rect(p, w, h, 118, 96, 145, 119, glove)
    _write_png(path, w, h, p, (w // 2, h))


def _receipt_ripper_pickup(path: Path) -> None:
    w, h = 68, 48
    p = _canvas(w, h, (0, 0, 0, 0))
    shell = (39, 47, 52, 255)
    shell_light = (72, 85, 91, 255)
    teal = (42, 185, 174, 255)
    paper = (236, 230, 202, 255)
    _rect(p, w, h, 4, 15, 62, 40, shell)
    _rect(p, w, h, 10, 19, 56, 36, shell_light)
    _rect(p, w, h, 18, 20, 49, 32, teal)
    _rect(p, w, h, 27, 3, 40, 18, paper)
    _rect(p, w, h, 29, 8, 38, 9, (87, 92, 92, 255))
    _rect(p, w, h, 29, 12, 37, 13, (87, 92, 92, 255))
    _write_png(path, w, h, p, (w // 2, h - 2))


def _checkout_sprite(path: Path, frame: str) -> None:
    w, h = 82, 104
    p = _canvas(w, h, (0, 0, 0, 0))
    casing = (49, 57, 61, 255)
    casing_light = (77, 89, 93, 255)
    screen = (22, 41, 45, 255)
    angry = (240, 83, 67, 255)
    scanner = (48, 208, 191, 255)
    warning = (239, 188, 48, 255)
    metal = (124, 135, 137, 255)

    if frame in "HIJ":
        y = 75 + (5 if frame in "IJ" else 0)
        _rect(p, w, h, 9, y, 72, min(h - 3, y + 18), casing)
        _rect(p, w, h, 18, y - 5, 58, min(h - 5, y + 10), screen)
        if frame != "J":
            _line(p, w, h, 20, y + 4, 63, y + 10, angry, 3)
        _write_png(path, w, h, p, (w // 2, h - 3))
        return

    phase = "ABCD".index(frame) if frame in "ABCD" else 0
    xshift = (0, 2, 0, -2)[phase]
    body_left = 17 + xshift
    body_right = 64 + xshift
    _rect(p, w, h, body_left, 33, body_right, 91, casing)
    _rect(p, w, h, body_left + 4, 37, body_right - 4, 70, casing_light)
    _rect(p, w, h, body_left + 8, 41, body_right - 8, 61, screen)
    _line(p, w, h, body_left + 13, 49, body_left + 22, 45, angry, 3)
    _line(p, w, h, body_right - 13, 49, body_right - 22, 45, angry, 3)
    _rect(p, w, h, body_left + 11, 74, body_right - 11, 80, scanner)
    _rect(p, w, h, body_left + 3, 84, body_left + 12, 89, warning)
    _rect(p, w, h, body_right - 12, 84, body_right - 3, 89, warning)
    _rect(p, w, h, 23 + xshift, 91, 31 + xshift, 101, metal)
    _rect(p, w, h, 50 + xshift, 91, 58 + xshift, 101, metal)

    if frame in "EF":
        beam_y = 76 if frame == "E" else 69
        _disc(p, w, h, 41 + xshift, beam_y, 10, (48, 208, 191, 90))
        _rect(p, w, h, 35 + xshift, beam_y - 3, 47 + xshift, beam_y + 3, scanner)
    elif frame == "G":
        _line(p, w, h, 18, 37, 65, 72, warning, 4)
        _line(p, w, h, 65, 37, 18, 72, warning, 4)

    _write_png(path, w, h, p, (w // 2, h - 3))


def _receipt_projectile(path: Path, frame: str) -> None:
    w = h = 44
    p = _canvas(w, h, (0, 0, 0, 0))
    paper = (239, 233, 209, 255)
    ink = (68, 72, 73, 255)
    glow = (61, 220, 197, 110)
    if frame in "AB":
        shift = 2 if frame == "B" else 0
        _disc(p, w, h, 22, 22, 18, glow)
        _rect(p, w, h, 13 + shift, 4, 29 - shift, 39, paper)
        for y in (10, 16, 22, 28, 34):
            _rect(p, w, h, 16 + shift, y, 26 - shift, y + 1, ink)
    else:
        radius = 10 if frame == "C" else 18
        _disc(p, w, h, 22, 22, radius, (244, 194, 65, 175))
        _disc(p, w, h, 22, 22, max(3, radius // 2), (245, 236, 196, 230))
    _write_png(path, w, h, p, (w // 2, h // 2))


def generate_combat_assets(game_dir: Path) -> None:
    (game_dir / "sprites").mkdir(parents=True, exist_ok=True)
    (game_dir / "sounds").mkdir(parents=True, exist_ok=True)

    for frame in "ABCDE":
        _receipt_ripper_view(game_dir / "sprites" / f"RRPV{frame}0.png", frame)
    _receipt_ripper_pickup(game_dir / "sprites" / "RRPKA0.png")

    for frame in "ABCDEFGHIJ":
        _checkout_sprite(game_dir / "sprites" / f"SCKO{frame}0.png", frame)
    for frame in "ABCD":
        _receipt_projectile(game_dir / "sprites" / f"RCPT{frame}0.png", frame)

    _write_tone(game_dir / "sounds" / "ripperfire.wav", (125.0, 240.0, 510.0), 0.30, 0.33, -0.55)
    _write_tone(game_dir / "sounds" / "rippercycle.wav", (92.0, 145.0), 0.26, 0.24, 0.35)
    _write_tone(game_dir / "sounds" / "checkoutidle.wav", (380.0, 760.0), 0.24, 0.14)
    _write_tone(game_dir / "sounds" / "checkoutattack.wav", (820.0, 410.0), 0.34, 0.25, -0.38)
    _write_tone(game_dir / "sounds" / "checkouthit.wav", (250.0, 180.0), 0.22, 0.20, -0.20)
    _write_tone(game_dir / "sounds" / "checkoutdown.wav", (210.0, 105.0, 70.0), 0.66, 0.28, -0.48)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_combat_assets(root / "game")
    print("Generated Receipt Ripper and Angry Self-Checkout combat assets.")