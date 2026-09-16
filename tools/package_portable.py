from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PK3 = DIST / "checkout-of-hell-prototype.pk3"
OUTPUT = DIST / "CHECKOUT-OF-HELL-Windows-Portable-dev.zip"
CHECKSUM = OUTPUT.with_suffix(OUTPUT.suffix + ".sha256")

PORTABLE_README = """CHECKOUT OF HELL — Windows Portable Development Build

1. Extract the whole ZIP to a normal writable folder.
2. Double-click PLAY.bat.
3. On the first launch, the game automatically downloads its pinned legal runtime
   dependencies from official upstream releases, verifies them where practical,
   and starts MAP01.
4. Later launches reuse the local runtime cache.

You do NOT need to search for GZDoom, Freedoom, Python, WAD files, or other
runtime files manually.

This is a development artifact, not a public demo release. The current project
still contains placeholder runtime visuals and is not yet representative of the
final art/audio presentation.

Project: https://github.com/Swir/check-out-of-hell
by Swir
"""


def add_bytes(archive: zipfile.ZipFile, archive_name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(archive_name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o644 & 0xFFFF) << 16
    archive.writestr(info, data)


def add_file(archive: zipfile.ZipFile, source: Path, archive_name: str) -> None:
    if not source.is_file():
        raise SystemExit(f"Portable package input is missing: {source}")
    add_bytes(archive, archive_name, source.read_bytes())


def main() -> None:
    DIST.mkdir(exist_ok=True)

    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=ROOT, check=True)
    if not PK3.is_file():
        raise SystemExit("PK3 build did not produce the expected package")

    inputs = [
        (ROOT / "packaging" / "PLAY.bat", "PLAY.bat"),
        (ROOT / "runtime-lock.json", "runtime-lock.json"),
        (ROOT / "tools" / "bootstrap_runtime.ps1", "tools/bootstrap_runtime.ps1"),
        (ROOT / "docs" / "THIRD_PARTY.md", "docs/THIRD_PARTY.md"),
        (ROOT / "branding" / "icon.svg", "branding/icon.svg"),
        (ROOT / "LICENSE", "LICENSE"),
        (PK3, "dist/checkout-of-hell-prototype.pk3"),
    ]

    if OUTPUT.exists():
        OUTPUT.unlink()

    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        add_bytes(archive, "README-FIRST.txt", PORTABLE_README.encode("utf-8"))
        for source, archive_name in inputs:
            add_file(archive, source, archive_name)

    digest = sha256(OUTPUT.read_bytes()).hexdigest()
    CHECKSUM.write_text(f"{digest}  {OUTPUT.name}\n", encoding="ascii")

    print(f"Portable package: {OUTPUT}")
    print(f"SHA-256:          {digest}")
    print("Runtime EXE/WAD files are intentionally obtained by PLAY.bat on first launch.")


if __name__ == "__main__":
    main()
