from __future__ import annotations

from pathlib import Path

from generate_environment_assets import _standing_sign


def generate_closing_time_polish_assets(game_dir: Path) -> None:
    """Generate project-owned wayfinding signs for the Closing Time polish candidate."""
    sprites = game_dir / "sprites"

    # Text carries the meaning so the routes do not depend on color alone. Accents deliberately
    # reuse the existing supermarket presentation family instead of introducing a new art style.
    _standing_sign(sprites / "LFSNA0.png", "FUSE", "LEFT", (98, 229, 255, 255))
    _standing_sign(sprites / "RFSNA0.png", "FUSE", "RIGHT", (0, 136, 255, 255))
    _standing_sign(sprites / "SFSNA0.png", "FUSE", "STAFF", (239, 190, 53, 255))
    _standing_sign(sprites / "OTSNA0.png", "OVERTIME", "LANE", (213, 84, 90, 255))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_closing_time_polish_assets(root / "game")
    print("Generated CHECKOUT OF HELL Closing Time polish-candidate assets.")
