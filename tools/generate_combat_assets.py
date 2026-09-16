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


def _price_gun_view(path: Path, frame: str) -> None:
    w, h = 176, 120
    p = _canvas(w, h, (0, 0, 0, 0))
    body = (222, 162, 39, 255)
    body_dark = (123, 83, 22, 255)
    black = (28, 31, 34, 255)
    screen = (61, 216, 188, 255)
    label = (242, 236, 205, 255)
    glove = (226, 180, 82, 255)
    recoil = {"A": 0, "B": 6, "C": 10, "D": 4, "E": 1}[frame]
    y = 61 + recoil
    _rect(p, w, h, 55, y, 128, 103, body)
    _rect(p, w, h, 63, y + 8, 121, 91, body_dark)
    _rect(p, w, h, 71, y + 13, 112, y + 31, black)
    _rect(p, w, h, 76, y + 17, 107, y + 27, screen)
    _rect(p, w, h, 119, y + 18, 146, y + 36, black)
    _rect(p, w, h, 129, y + 22, 157, y + 31, label)
    for x in range(132, 154, 4):
        _rect(p, w, h, x, y + 23, x + 1, y + 30, black)
    if frame in "BCD":
        _disc(p, w, h, 151, y + 27, 10, (61, 216, 188, 100))
    _rect(p, w, h, 70, 92, 85, 119, black)
    _rect(p, w, h, 42, 99, 69, 119, glove)
    _rect(p, w, h, 111, 99, 140, 119, glove)
    _write_png(path, w, h, p, (w // 2, h))


def _price_gun_pickup(path: Path) -> None:
    w, h = 72, 48
    p = _canvas(w, h, (0, 0, 0, 0))
    body = (222, 162, 39, 255)
    dark = (50, 45, 37, 255)
    teal = (61, 216, 188, 255)
    _rect(p, w, h, 8, 12, 54, 36, body)
    _rect(p, w, h, 15, 17, 46, 30, dark)
    _rect(p, w, h, 20, 20, 41, 26, teal)
    _rect(p, w, h, 52, 17, 68, 28, dark)
    _rect(p, w, h, 24, 35, 34, 46, dark)
    _write_png(path, w, h, p, (w // 2, h - 2))


def _price_label_puff(path: Path, frame: str) -> None:
    w = h = 40
    p = _canvas(w, h, (0, 0, 0, 0))
    paper = (244, 238, 205, 255)
    ink = (32, 35, 36, 255)
    glow = (61, 216, 188, 110)
    size = {"A": 16, "B": 13, "C": 9}[frame]
    _disc(p, w, h, 20, 20, 18, glow)
    _rect(p, w, h, 20 - size, 20 - size // 2, 20 + size, 20 + size // 2, paper)
    for x in range(20 - size + 3, 20 + size - 1, 4):
        _rect(p, w, h, x, 20 - size // 2 + 2, x + 1, 20 + size // 2 - 2, ink)
    _write_png(path, w, h, p, (w // 2, h // 2))


def _turbo_launcher_view(path: Path, frame: str) -> None:
    w, h = 176, 120
    p = _canvas(w, h, (0, 0, 0, 0))
    frame_dark = (38, 43, 47, 255)
    frame_light = (73, 82, 88, 255)
    can_blue = (42, 131, 219, 255)
    can_silver = (190, 199, 202, 255)
    warning = (236, 78, 57, 255)
    glove = (226, 180, 82, 255)
    recoil = {"A": 0, "B": 9, "C": 14, "D": 5, "E": 2}[frame]
    y = 56 + recoil
    _rect(p, w, h, 38, y, 140, 108, frame_dark)
    _rect(p, w, h, 48, y + 7, 131, 97, frame_light)
    _rect(p, w, h, 58, y + 14, 122, 89, frame_dark)
    _rect(p, w, h, 121, y + 20, 157, y + 42, can_blue)
    _rect(p, w, h, 125, y + 21, 153, y + 24, can_silver)
    _rect(p, w, h, 125, y + 38, 153, y + 41, can_silver)
    _rect(p, w, h, 49, y + 38, 62, y + 44, warning)
    if frame in "BC":
        _disc(p, w, h, 156, y + 31, 15 if frame == "C" else 10, (244, 192, 64, 130))
    _rect(p, w, h, 44, 96, 70, 119, glove)
    _rect(p, w, h, 115, 96, 143, 119, glove)
    _write_png(path, w, h, p, (w // 2, h))


def _turbo_launcher_pickup(path: Path) -> None:
    w, h = 78, 50
    p = _canvas(w, h, (0, 0, 0, 0))
    dark = (38, 43, 47, 255)
    light = (73, 82, 88, 255)
    blue = (42, 131, 219, 255)
    silver = (190, 199, 202, 255)
    _rect(p, w, h, 4, 14, 62, 41, dark)
    _rect(p, w, h, 10, 19, 55, 35, light)
    _rect(p, w, h, 55, 18, 75, 34, blue)
    _rect(p, w, h, 58, 19, 72, 22, silver)
    _rect(p, w, h, 58, 31, 72, 34, silver)
    _write_png(path, w, h, p, (w // 2, h - 2))


def _turbo_can_projectile(path: Path, frame: str) -> None:
    w = h = 48
    p = _canvas(w, h, (0, 0, 0, 0))
    blue = (42, 131, 219, 255)
    silver = (204, 211, 214, 255)
    red = (239, 72, 58, 255)
    if frame in "AB":
        shift = 3 if frame == "B" else 0
        _disc(p, w, h, 24, 24, 20, (61, 216, 188, 70))
        _rect(p, w, h, 14 + shift, 7, 33 - shift, 40, blue)
        _rect(p, w, h, 15 + shift, 7, 32 - shift, 11, silver)
        _rect(p, w, h, 15 + shift, 36, 32 - shift, 40, silver)
        _rect(p, w, h, 19 + shift, 18, 28 - shift, 28, red)
    else:
        radius = {"C": 10, "D": 16, "E": 22}[frame]
        _disc(p, w, h, 24, 24, radius, (244, 179, 54, 185))
        _disc(p, w, h, 24, 24, max(4, radius // 2), (248, 235, 174, 235))
    _write_png(path, w, h, p, (w // 2, h // 2))


def _scanner_turret(path: Path, frame: str) -> None:
    w, h = 86, 92
    p = _canvas(w, h, (0, 0, 0, 0))
    casing = (52, 59, 63, 255)
    casing_light = (90, 100, 104, 255)
    lens = (62, 224, 197, 255)
    warning = (239, 188, 48, 255)
    red = (235, 70, 58, 255)
    base = (32, 36, 39, 255)
    if frame in "GHI":
        y = 66 + (4 if frame in "HI" else 0)
        _rect(p, w, h, 12, y, 74, min(89, y + 16), base)
        _rect(p, w, h, 24, y - 8, 62, min(87, y + 6), casing)
        if frame != "I":
            _line(p, w, h, 21, y, 65, y + 8, red, 3)
        _write_png(path, w, h, p, (w // 2, h - 2))
        return

    swivel = {"A": -3, "B": 0, "C": 3, "D": 0, "E": 0, "F": 0}.get(frame, 0)
    _rect(p, w, h, 20, 29, 66, 70, casing)
    _rect(p, w, h, 25, 34, 61, 63, casing_light)
    _rect(p, w, h, 13, 70, 73, 83, base)
    _rect(p, w, h, 31 + swivel, 40, 55 + swivel, 57, base)
    _disc(p, w, h, 43 + swivel, 48, 8, lens)
    _rect(p, w, h, 18, 31, 27, 37, warning)
    _rect(p, w, h, 59, 31, 68, 37, warning)
    if frame in "EF":
        _disc(p, w, h, 43, 48, 16 if frame == "F" else 12, (62, 224, 197, 105))
        _line(p, w, h, 43, 48, 82, 48, lens, 3)
    _write_png(path, w, h, p, (w // 2, h - 2))


def _scanner_beam(path: Path, frame: str) -> None:
    w = h = 36
    p = _canvas(w, h, (0, 0, 0, 0))
    teal = (62, 224, 197, 255)
    red = (239, 80, 67, 255)
    if frame in "AB":
        _disc(p, w, h, 18, 18, 14, (62, 224, 197, 90))
        _line(p, w, h, 4, 18, 31, 18, teal, 4 if frame == "A" else 2)
        _line(p, w, h, 18, 4, 18, 31, red, 2)
    else:
        radius = 8 if frame == "C" else 15
        _disc(p, w, h, 18, 18, radius, (239, 188, 48, 180))
        _disc(p, w, h, 18, 18, max(3, radius // 2), teal)
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

    for frame in "ABCDE":
        _price_gun_view(game_dir / "sprites" / f"PGUN{frame}0.png", frame)
    _price_gun_pickup(game_dir / "sprites" / "PGPKA0.png")
    for frame in "ABC":
        _price_label_puff(game_dir / "sprites" / f"PLBL{frame}0.png", frame)

    for frame in "ABCDE":
        _turbo_launcher_view(game_dir / "sprites" / f"TCNV{frame}0.png", frame)
    _turbo_launcher_pickup(game_dir / "sprites" / "TCNPA0.png")
    for frame in "ABCDE":
        _turbo_can_projectile(game_dir / "sprites" / f"TCAN{frame}0.png", frame)

    for frame in "ABCDEFGHI":
        _scanner_turret(game_dir / "sprites" / f"SCNR{frame}0.png", frame)
    for frame in "ABCD":
        _scanner_beam(game_dir / "sprites" / f"SBEA{frame}0.png", frame)

    _write_tone(game_dir / "sounds" / "ripperfire.wav", (125.0, 240.0, 510.0), 0.30, 0.33, -0.55)
    _write_tone(game_dir / "sounds" / "rippercycle.wav", (92.0, 145.0), 0.26, 0.24, 0.35)
    _write_tone(game_dir / "sounds" / "checkoutidle.wav", (380.0, 760.0), 0.24, 0.14)
    _write_tone(game_dir / "sounds" / "checkoutattack.wav", (820.0, 410.0), 0.34, 0.25, -0.38)
    _write_tone(game_dir / "sounds" / "checkouthit.wav", (250.0, 180.0), 0.22, 0.20, -0.20)
    _write_tone(game_dir / "sounds" / "checkoutdown.wav", (210.0, 105.0, 70.0), 0.66, 0.28, -0.48)

    _write_tone(game_dir / "sounds" / "pricefire.wav", (660.0, 930.0), 0.16, 0.24, -0.32)
    _write_tone(game_dir / "sounds" / "pricelabel.wav", (1180.0, 590.0), 0.18, 0.16, -0.12)
    _write_tone(game_dir / "sounds" / "canlaunch.wav", (90.0, 170.0, 360.0), 0.34, 0.32, -0.44)
    _write_tone(game_dir / "sounds" / "canexplode.wav", (76.0, 52.0, 132.0), 0.56, 0.38, -0.55)
    _write_tone(game_dir / "sounds" / "scanneridle.wav", (440.0, 880.0), 0.22, 0.13)
    _write_tone(game_dir / "sounds" / "scannerattack.wav", (980.0, 490.0), 0.27, 0.24, -0.38)
    _write_tone(game_dir / "sounds" / "scannerhit.wav", (330.0, 220.0), 0.21, 0.18, -0.18)
    _write_tone(game_dir / "sounds" / "scannerdown.wav", (180.0, 92.0, 55.0), 0.64, 0.30, -0.50)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_combat_assets(root / "game")
    print("Generated signature retail combat assets for Receipt Ripper, Angry Self-Checkout, Price-Gun SMG, Turbo Can Launcher and Security Price Scanner.")
