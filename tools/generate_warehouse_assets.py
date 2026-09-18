from __future__ import annotations

from pathlib import Path

from generate_environment_assets import _standing_sign


def generate_warehouse_assets(game_dir: Path) -> None:
    """Generate project-owned Warehouse 13.5 objective/signage sprites deterministically."""
    sprites = game_dir / "sprites"
    _standing_sign(sprites / "WCTLA0.png", "LIFT", "OVERRIDE", (98, 205, 218, 255))
    _standing_sign(sprites / "WSGNA0.png", "FREIGHT", "ONLY", (218, 166, 64, 255))
    _standing_sign(sprites / "WLOKA0.png", "LOCKOUT", "TAG OUT", (98, 205, 218, 255))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_warehouse_assets(root / "game")
    print("Generated CHECKOUT OF HELL Warehouse 13.5 assets.")
