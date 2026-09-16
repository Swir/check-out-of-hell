from hashlib import sha256
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE = DIST / "CHECKOUT-OF-HELL-Windows-Portable-dev.zip"
CHECKSUM = PACKAGE.with_suffix(PACKAGE.suffix + ".sha256")

if not PACKAGE.is_file():
    raise SystemExit("Portable package is missing. Run: python tools/package_portable.py")
if not CHECKSUM.is_file():
    raise SystemExit("Portable package checksum is missing")

required = {
    "PLAY.bat",
    "README-FIRST.txt",
    "runtime-lock.json",
    "tools/bootstrap_runtime.ps1",
    "docs/THIRD_PARTY.md",
    "branding/icon.svg",
    "LICENSE",
    "dist/checkout-of-hell-prototype.pk3",
}

with zipfile.ZipFile(PACKAGE, "r") as archive:
    names = set(archive.namelist())
    missing = required - names
    if missing:
        raise SystemExit(f"Portable package entries missing: {sorted(missing)}")

    forbidden_suffixes = (".exe", ".wad")
    forbidden = [name for name in names if name.lower().endswith(forbidden_suffixes)]
    if forbidden:
        raise SystemExit(f"Portable artifact must not silently bundle runtime binaries/data: {forbidden}")

    source_leaks = [name for name in names if name.startswith("game/")]
    if source_leaks:
        raise SystemExit(f"Portable artifact unexpectedly contains game source files: {source_leaks}")

    launcher = archive.read("PLAY.bat").decode("utf-8", errors="strict").lower()
    if "bootstrap_runtime.ps1" not in launcher:
        raise SystemExit("Portable PLAY.bat does not bootstrap the pinned runtime")
    if "checkout-of-hell-prototype.pk3" not in launcher:
        raise SystemExit("Portable PLAY.bat does not launch the prebuilt PK3")
    if "python" in launcher or "build.py" in launcher or "bootstrap_python" in launcher:
        raise SystemExit("Portable PLAY.bat must not require a Python/build toolchain")

    readme = archive.read("README-FIRST.txt").decode("utf-8", errors="strict")
    if "You do NOT need to search" not in readme:
        raise SystemExit("Portable README must state the no-manual-dependency-search contract")

    pk3_info = archive.getinfo("dist/checkout-of-hell-prototype.pk3")
    if pk3_info.file_size < 1024:
        raise SystemExit("Embedded PK3 looks unexpectedly small")

checksum_text = CHECKSUM.read_text(encoding="ascii").strip()
match = re.fullmatch(r"([0-9a-f]{64})\s{2}(.+)", checksum_text)
if not match:
    raise SystemExit("Portable checksum sidecar has an unexpected format")
if match.group(2) != PACKAGE.name:
    raise SystemExit("Portable checksum sidecar names the wrong artifact")
actual = sha256(PACKAGE.read_bytes()).hexdigest()
if actual != match.group(1):
    raise SystemExit("Portable package SHA-256 sidecar does not match the ZIP")

print("Portable package contract: PASS")
print("Artifact is prebuilt, one-click, runtime-download capable and Python-free for players.")
