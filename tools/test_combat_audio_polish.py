from array import array
from pathlib import Path
import re
import sys
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PK3 = ROOT / "dist" / "checkout-of-hell-prototype.pk3"

sys.path.insert(0, str(ROOT / "tools"))
from generate_combat_audio_polish import COMBAT_AUDIO_FAMILIES  # noqa: E402

if not PK3.exists():
    raise SystemExit("PK3 missing. Run: python tools/build.py")

sndinfo = (GAME / "SNDINFO").read_text(encoding="utf-8")
decorate = (GAME / "DECORATE").read_text(encoding="utf-8")
build = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")

if "from generate_combat_audio_polish import generate_combat_audio_polish" not in build:
    raise SystemExit("Combat-audio polish generator is not imported by the build")
if "generate_combat_audio_polish(GAME)" not in build:
    raise SystemExit("Combat-audio polish generator is not executed by the build")

expected_files: list[str] = []
for cue, spec in COMBAT_AUDIO_FAMILIES.items():
    variant_count = spec[-1]
    expected_aliases = [f"coh/{cue}_v{index}" for index in range(1, variant_count + 1)]

    group = re.search(rf"\$random\s+coh/{re.escape(cue)}\s*\{{([^}}]+)\}}", sndinfo)
    if not group:
        raise SystemExit(f"Randomized SNDINFO group missing for combat cue: {cue}")
    aliases = group.group(1).split()
    if aliases != expected_aliases:
        raise SystemExit(f"Unexpected SNDINFO family for {cue}: {aliases}")

    if re.search(rf"(?m)^coh/{re.escape(cue)}\s+sounds/{re.escape(cue)}\s*$", sndinfo):
        raise SystemExit(f"Combat cue still bypasses its randomized family: {cue}")

    if f'"coh/{cue}"' not in decorate:
        raise SystemExit(f"Gameplay actor no longer references logical combat cue: coh/{cue}")

    for index, alias in enumerate(expected_aliases, start=1):
        rel = f"sounds/{cue}_v{index}.wav"
        expected_files.append(rel)
        if f"{alias} sounds/{cue}_v{index}" not in sndinfo:
            raise SystemExit(f"Physical sound alias missing from SNDINFO: {alias}")

        path = GAME / rel
        if not path.exists():
            raise SystemExit(f"Generated combat-audio variant missing: {rel}")
        with wave.open(str(path), "rb") as stream:
            if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
                raise SystemExit(f"Combat-audio variant must be mono 16-bit PCM: {rel}")
            if stream.getframerate() != 22050 or stream.getnframes() < 4000:
                raise SystemExit(f"Combat-audio rate/duration is invalid: {rel}")
            samples = array("h", stream.readframes(stream.getnframes()))
            if sys.byteorder != "little":
                samples.byteswap()
            peak = max((abs(sample) for sample in samples), default=0)
            if peak < 500:
                raise SystemExit(f"Combat-audio variant is unexpectedly silent: {rel}")
            if peak > 30000:
                raise SystemExit(f"Combat-audio variant exceeds safe prototype headroom: {rel} -> {peak}")

with zipfile.ZipFile(PK3, "r") as archive:
    names = set(archive.namelist())
    missing = set(expected_files) - names
    if missing:
        raise SystemExit(f"Combat-audio variants missing from PK3: {sorted(missing)}")
    packed_sndinfo = archive.read("SNDINFO").decode("utf-8")
    for cue in COMBAT_AUDIO_FAMILIES:
        if f"$random coh/{cue}" not in packed_sndinfo:
            raise SystemExit(f"Packaged SNDINFO lost randomized combat cue: {cue}")

print("Combat audio polish contract: PASS")
print(
    f"{len(COMBAT_AUDIO_FAMILIES)} logical combat cues resolve through "
    f"{len(expected_files)} deterministic generated variants with PCM/headroom checks."
)
