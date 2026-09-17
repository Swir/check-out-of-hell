from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
HERO = ROOT / "assets" / "readme" / "hero.svg"


def require(text: str, needle: str, source: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing README PRO marker/content: {needle!r}")


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    hero = HERO.read_text(encoding="utf-8")

    for marker in (
        "<!-- SWIR-README-STANDARD:v2 -->",
        'src="assets/readme/hero.svg"',
        'src="assets/readme/progress-card.svg"',
        "## 📌 Project status",
        "## ✨ Highlights",
        "## 🚀 Quick Start — Windows",
        "## 🖥️ Requirements & compatibility",
        "## 🧱 Technology & architecture",
        "## 🧭 Roadmap & releases",
        "## 🔎 Search Keywords",
        "No proprietary Doom, Star Wars or other commercial game assets are committed.",
        "PLAY.bat",
        "Not published yet",
        "by Swir",
    ):
        require(readme, marker, README)

    keyword_match = re.search(r"## 🔎 Search Keywords\s+\n\s*([^\n]+)", readme)
    if not keyword_match:
        raise AssertionError("README.md: Search Keywords line not found")
    keywords = [item.strip(" `") for item in keyword_match.group(1).split("•") if item.strip()]
    if not 8 <= len(keywords) <= 20:
        raise AssertionError(f"README.md: expected 8-20 search phrases, found {len(keywords)}")

    readme_progress = re.search(r"Implemented/testable progress \| \*\*(\d+(?:\.\d+)?)%\*\*", readme)
    roadmap_progress = re.search(r"Overall progress:\*\* `[^`]*?\s(\d+(?:\.\d+)?)%`", roadmap)
    if not readme_progress or not roadmap_progress:
        raise AssertionError("README/ROADMAP progress markers could not be parsed")
    if readme_progress.group(1) != roadmap_progress.group(1):
        raise AssertionError(
            f"README progress {readme_progress.group(1)}% != ROADMAP progress {roadmap_progress.group(1)}%"
        )

    for marker in (
        'width="1200"',
        'height="320"',
        "#02050A",
        "#62E5FF",
        "SWIR PROJECT",
        "CHECKOUT OF HELL",
        "SHIFT HAPPENS.",
        "06:00",
    ):
        require(hero, marker, HERO)

    if "branding/icon.svg" in readme:
        raise AssertionError("README.md should use the project-local README hero as the primary hero asset")

    print(
        f"SWIR README PRO v2 contract: PASS ({len(keywords)} search phrases, "
        f"progress {readme_progress.group(1)}%)"
    )


if __name__ == "__main__":
    main()
