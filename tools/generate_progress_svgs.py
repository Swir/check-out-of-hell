from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from math import isfinite
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "ROADMAP.md"
README = ROOT / "README.md"
CARD = ROOT / "assets" / "readme" / "progress-card.svg"
MINI = ROOT / "assets" / "readme" / "progress-mini.svg"
TEMPLATE = ROOT / "assets" / "readme" / "progress-template.svg"

PROJECT_NAME = "CHECKOUT OF HELL"
WEIGHTS_BEGIN = "<!-- SWIR-PROGRESS-WEIGHTS:BEGIN -->"
WEIGHTS_END = "<!-- SWIR-PROGRESS-WEIGHTS:END -->"

PHASE_RE = re.compile(r"^## Phase\s+\d+\s+—\s+(.+?)\s+—\s+(\d+(?:\.\d+)?)%\s*$", re.MULTILINE)
WEIGHT_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+(?:\.\d+)?)%\s*\|\s*$", re.MULTILINE)
OVERALL_RE = re.compile(r"\*\*Overall progress:\*\* `[^`]*?\s(\d+(?:\.\d+)?)%`")
README_PROGRESS_RE = re.compile(r"Implemented/testable progress \| \*\*(\d+(?:\.\d+)?)%\*\*")
DEMO_RE = re.compile(r"^## Phase\s+3\s+—\s+Demo Release\s+—\s+(\d+(?:\.\d+)?)%\s*$", re.MULTILINE)
SCOPE_RE = re.compile(r"^\*\*Measured scope:\*\*\s+(.+?)\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^\*\*Progress status:\*\*\s+([A-Z][A-Z ]+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ProgressData:
    fraction: Decimal | None
    display_percent: str
    phase_count: int
    demo_percent: str
    measured_scope: str
    status: str


def _display_percent(value: Decimal | None) -> str:
    if value is None:
        return "N/A"
    rounded = (value * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{rounded:.1f}%"


def parse_progress(roadmap_text: str) -> ProgressData:
    phases = {name.strip(): Decimal(percent) / Decimal("100") for name, percent in PHASE_RE.findall(roadmap_text)}
    scope_match = SCOPE_RE.search(roadmap_text)
    status_match = STATUS_RE.search(roadmap_text)
    scope = scope_match.group(1).strip() if scope_match else "N/A"
    status = status_match.group(1).strip() if status_match else "N/A"

    if not phases:
        return ProgressData(None, "N/A", 0, "N/A", scope, status)

    if WEIGHTS_BEGIN not in roadmap_text or WEIGHTS_END not in roadmap_text:
        return ProgressData(None, "N/A", len(phases), "N/A", scope, status)
    block = roadmap_text.split(WEIGHTS_BEGIN, 1)[1].split(WEIGHTS_END, 1)[0]
    weights: dict[str, Decimal] = {}
    for name, percent in WEIGHT_RE.findall(block):
        name = name.strip()
        if name in {"Phase", "---"} or set(name) <= {"-", ":"}:
            continue
        weights[name] = Decimal(percent) / Decimal("100")

    if not weights or set(weights) != set(phases):
        return ProgressData(None, "N/A", len(phases), "N/A", scope, status)
    if sum(weights.values(), Decimal("0")) != Decimal("1"):
        return ProgressData(None, "N/A", len(phases), "N/A", scope, status)
    if scope == "N/A" or status == "N/A":
        return ProgressData(None, "N/A", len(phases), "N/A", scope, status)

    weighted = sum((phases[name] * weights[name] for name in phases), Decimal("0"))
    if weighted < 0 or weighted > 1:
        raise AssertionError(f"Weighted progress out of bounds: {weighted}")

    demo_match = DEMO_RE.search(roadmap_text)
    demo = f"{Decimal(demo_match.group(1)):.1f}%" if demo_match else "N/A"
    return ProgressData(weighted, _display_percent(weighted), len(phases), demo, scope, status)


def _trim_label(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 1)].rstrip() + "…"


def _fill_width(track_width: Decimal, fraction: Decimal | None) -> Decimal:
    if fraction is None:
        return Decimal("0")
    return max(Decimal("0"), min(track_width, track_width * fraction))


def _fmt_num(value: Decimal) -> str:
    text = format(value.quantize(Decimal("0.01")), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def render_card(data: ProgressData) -> str:
    fraction = data.fraction
    fill = _fill_width(Decimal("1100"), fraction)
    fill_markup = ""
    if fraction is not None and fraction > 0:
        fill_markup = f'''\n  <rect id="progress-fill" x="50" y="126" width="{_fmt_num(fill)}" height="18" rx="9" fill="url(#progressGradient)" clip-path="url(#trackClip)" filter="url(#softGlow)"/>'''
    description = (
        f"{PROJECT_NAME} {data.measured_scope}: {data.display_percent} across {data.phase_count} weighted roadmap phases. "
        f"Demo Release readiness is {data.demo_percent} and tracked separately."
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-labelledby="title desc">
  <title id="title">{escape(PROJECT_NAME)} project progress</title>
  <desc id="desc">{escape(description)}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient>
    <linearGradient id="progressGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#62E5FF" stroke-opacity="0.055" stroke-width="1"/></pattern>
    <filter id="softGlow" x="-20%" y="-100%" width="140%" height="300%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="trackClip"><rect x="50" y="126" width="1100" height="18" rx="9"/></clipPath>
  </defs>
  <rect x="1" y="1" width="1198" height="178" rx="20" fill="url(#bg)" stroke="#0088FF" stroke-opacity="0.55" stroke-width="2"/>
  <rect x="1" y="1" width="1198" height="178" rx="20" fill="url(#grid)"/>
  <path d="M24 28 H166" stroke="#62E5FF" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
  <text x="50" y="48" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="25" font-weight="700">{escape(PROJECT_NAME)}</text>
  <text x="50" y="78" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="15">{escape(_trim_label(data.measured_scope, 70))}</text>
  <text x="50" y="107" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700">{escape(data.status)}</text>
  <text x="190" y="107" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="14">{data.phase_count} weighted phases</text>
  <text x="390" y="107" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="14">Demo Release readiness {escape(data.demo_percent)} · tracked separately</text>
  <text x="1150" y="88" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="42" font-weight="800">{escape(data.display_percent)}</text>
  <rect id="progress-track" x="50" y="126" width="1100" height="18" rx="9" fill="#0A1A29" stroke="#62E5FF" stroke-opacity="0.25"/>{fill_markup}
  <text x="50" y="164" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">Source: ROADMAP.md · weighted verified phase progress · generated deterministically</text>
</svg>
'''


def render_mini(data: ProgressData) -> str:
    fraction = data.fraction
    fill = _fill_width(Decimal("700"), fraction)
    fill_markup = ""
    if fraction is not None and fraction > 0:
        fill_markup = f'''\n  <rect id="progress-fill" x="170" y="42" width="{_fmt_num(fill)}" height="12" rx="6" fill="url(#progressGradient)" clip-path="url(#trackClip)"/>'''
    description = (
        f"{PROJECT_NAME} project progress {data.display_percent}; {data.phase_count} weighted phases. "
        f"Demo Release readiness {data.demo_percent}, tracked separately."
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-labelledby="title desc">
  <title id="title">{escape(PROJECT_NAME)} compact project progress</title>
  <desc id="desc">{escape(description)}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient>
    <linearGradient id="progressGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient>
    <clipPath id="trackClip"><rect x="170" y="42" width="700" height="12" rx="6"/></clipPath>
  </defs>
  <rect x="1" y="1" width="898" height="70" rx="14" fill="url(#bg)" stroke="#0088FF" stroke-opacity="0.5" stroke-width="2"/>
  <text x="20" y="27" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="15" font-weight="700">{escape(PROJECT_NAME)}</text>
  <text x="220" y="27" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700">PROJECT · {escape(data.status)}</text>
  <text x="870" y="27" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="20" font-weight="800">{escape(data.display_percent)}</text>
  <text x="20" y="52" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="11">{data.phase_count} weighted phases</text>
  <rect id="progress-track" x="170" y="42" width="700" height="12" rx="6" fill="#0A1A29" stroke="#62E5FF" stroke-opacity="0.25"/>{fill_markup}
</svg>
'''


def render_template() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-labelledby="title desc">
  <title id="title">SWIR Progress SVG PRO template</title>
  <desc id="desc">TEMPLATE / NOT PROJECT DATA. Replace labels only through a project generator; N/A means no verified progress source.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient>
    <linearGradient id="progressGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#62E5FF" stroke-opacity="0.055" stroke-width="1"/></pattern>
  </defs>
  <rect x="1" y="1" width="1198" height="178" rx="20" fill="url(#bg)" stroke="#0088FF" stroke-opacity="0.55" stroke-width="2"/>
  <rect x="1" y="1" width="1198" height="178" rx="20" fill="url(#grid)"/>
  <text x="50" y="48" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="25" font-weight="700">PROJECT NAME</text>
  <text x="50" y="78" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="15">MEASURED SCOPE</text>
  <text x="50" y="107" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700">TEMPLATE / NOT PROJECT DATA</text>
  <text x="300" y="107" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="14">COUNTER LABEL</text>
  <text x="1150" y="88" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="42" font-weight="800">N/A</text>
  <rect id="progress-track" x="50" y="126" width="1100" height="18" rx="9" fill="#0A1A29" stroke="#62E5FF" stroke-opacity="0.25"/>
  <text x="50" y="164" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">TEMPLATE ONLY · no live project percentage · no progress fill</text>
</svg>
'''


def verify_svg(svg_text: str, expected_track_width: Decimal, expected_fill: Decimal) -> None:
    root = ET.fromstring(svg_text)
    if "viewBox" not in root.attrib:
        raise AssertionError("SVG is missing viewBox")
    lower = svg_text.lower()
    for forbidden in ("<script", "<foreignobject", "href=\"http://", "href=\"https://", "xlink:href=\"http://", "xlink:href=\"https://"):
        if forbidden in lower:
            raise AssertionError(f"SVG contains forbidden external/script content: {forbidden}")
    ns = {"svg": "http://www.w3.org/2000/svg"}
    if root.find("svg:title", ns) is None or root.find("svg:desc", ns) is None:
        raise AssertionError("SVG requires title and description")
    track = next((e for e in root.iter() if e.attrib.get("id") == "progress-track"), None)
    if track is None:
        raise AssertionError("SVG progress track not found")
    track_width = Decimal(track.attrib["width"])
    if track_width != expected_track_width:
        raise AssertionError(f"Unexpected track width {track_width}")
    fill = next((e for e in root.iter() if e.attrib.get("id") == "progress-fill"), None)
    actual_fill = Decimal(fill.attrib["width"]) if fill is not None else Decimal("0")
    if actual_fill < 0 or actual_fill > track_width:
        raise AssertionError(f"Progress fill out of bounds: {actual_fill} / {track_width}")
    if actual_fill != expected_fill.quantize(Decimal("0.01")):
        raise AssertionError(f"Progress fill {actual_fill} != expected {expected_fill}")
    for element in root.iter():
        for key, value in element.attrib.items():
            if key in {"x", "y", "width", "height", "rx", "stroke-width", "font-size"}:
                try:
                    numeric = float(value)
                except ValueError:
                    continue
                if not isfinite(numeric):
                    raise AssertionError(f"Non-finite SVG numeric attribute: {key}={value}")


def verify_document_links(data: ProgressData, readme_text: str, roadmap_text: str) -> None:
    expected = data.display_percent.rstrip("%")
    overall = OVERALL_RE.search(roadmap_text)
    readme = README_PROGRESS_RE.search(readme_text)
    if not overall or not readme:
        raise AssertionError("README/ROADMAP progress markers could not be parsed")
    if Decimal(overall.group(1)) != Decimal(expected) or Decimal(readme.group(1)) != Decimal(expected):
        raise AssertionError(
            f"Progress mismatch: generated={data.display_percent}, ROADMAP={overall.group(1)}%, README={readme.group(1)}%"
        )
    for text, needle, source in (
        (readme_text, 'src="assets/readme/progress-card.svg"', README),
        (roadmap_text, 'src="assets/readme/progress-mini.svg"', ROADMAP),
        (roadmap_text, "<!-- SWIR-PROGRESS-SVG-PRO:v1 -->", ROADMAP),
        (roadmap_text, f"**Measured scope:** {data.measured_scope}", ROADMAP),
        (roadmap_text, f"**Progress status:** {data.status}", ROADMAP),
    ):
        if needle not in text:
            raise AssertionError(f"{source}: missing {needle}")
    fallback = f"**{data.display_percent}** implemented/testable project progress across **{data.phase_count} weighted roadmap phases**"
    if fallback not in readme_text or fallback not in roadmap_text:
        raise AssertionError("Textual progress fallback is missing or stale")
    demo = f"**Demo Release readiness: {data.demo_percent}**"
    if demo not in readme_text or demo not in roadmap_text:
        raise AssertionError("Separate Demo Release readiness fallback is missing or stale")


def self_test() -> None:
    scope = "Verified test scope"
    partial = ProgressData(Decimal("0.5"), "50.0%", 1, "N/A", scope, "IN PROGRESS")
    zero = ProgressData(Decimal("0"), "0.0%", 1, "N/A", scope, "PLANNING")
    complete = ProgressData(Decimal("1"), "100.0%", 1, "N/A", scope, "COMPLETE")
    unknown = ProgressData(None, "N/A", 0, "N/A", "N/A", "N/A")
    for case in (partial, zero, complete, unknown):
        card = render_card(case)
        expected = _fill_width(Decimal("1100"), case.fraction)
        verify_svg(card, Decimal("1100"), expected)
    long_scope = "A very long measured scope label that must not collide with the numeric progress area or overflow the intended text lane"
    if not _trim_label(long_scope, 50).endswith("…"):
        raise AssertionError("Long-label truncation self-test failed")
    escaped = escape("A & B < C > D")
    if "&amp;" not in escaped or "&lt;" not in escaped:
        raise AssertionError("XML escaping self-test failed")


def expected_outputs(data: ProgressData) -> dict[Path, str]:
    return {CARD: render_card(data), MINI: render_mini(data), TEMPLATE: render_template()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or verify SWIR Progress SVG PRO assets.")
    parser.add_argument("--check", action="store_true", help="Fail if committed SVGs or README/ROADMAP progress are stale.")
    args = parser.parse_args()

    roadmap_text = ROADMAP.read_text(encoding="utf-8")
    readme_text = README.read_text(encoding="utf-8")
    data = parse_progress(roadmap_text)
    if data.fraction is None:
        raise SystemExit("Progress source is incomplete/unverifiable; expected a complete weighted ROADMAP model with measured scope/status, refusing to fabricate a percentage.")

    self_test()
    outputs = expected_outputs(data)
    verify_svg(outputs[CARD], Decimal("1100"), _fill_width(Decimal("1100"), data.fraction))
    verify_svg(outputs[MINI], Decimal("700"), _fill_width(Decimal("700"), data.fraction))
    ET.fromstring(outputs[TEMPLATE])
    verify_document_links(data, readme_text, roadmap_text)

    if args.check:
        stale = []
        for path, expected in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            raise SystemExit("Stale/missing progress SVG output: " + ", ".join(stale) + ". Run: python tools/generate_progress_svgs.py")
        print(f"SWIR Progress SVG PRO: PASS ({data.display_percent}, {data.phase_count} weighted phases; Demo Release {data.demo_percent})")
        return

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated SWIR Progress SVG PRO assets at {data.display_percent}; Demo Release readiness {data.demo_percent}.")


if __name__ == "__main__":
    main()
