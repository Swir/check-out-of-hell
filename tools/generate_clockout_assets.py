from __future__ import annotations

from pathlib import Path

from generate_environment_assets import _standing_sign


def generate_clockout_assets(game_dir: Path) -> None:
    """Generate the project-owned post-boss CLOCK OUT wayfinding sign."""
    _standing_sign(
        game_dir / "sprites" / "COUTA0.png",
        "CLOCK",
        "OUT",
        (98, 229, 255, 255),
    )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_clockout_assets(root / "game")
    print("Generated CHECKOUT OF HELL clock-out guidance asset.")
