from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile


def collect_json_text(save_path: Path) -> tuple[list[str], str]:
    if not save_path.is_file():
        raise ValueError(f"Savegame does not exist: {save_path}")
    if not zipfile.is_zipfile(save_path):
        raise ValueError(f"Savegame is not a readable GZDoom ZIP archive: {save_path}")

    names: list[str] = []
    chunks: list[str] = []
    with zipfile.ZipFile(save_path) as archive:
        for info in archive.infolist():
            if info.is_dir() or not info.filename.lower().endswith(".json"):
                continue
            names.append(info.filename)
            payload = archive.read(info)
            try:
                text = payload.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise ValueError(f"JSON entry is not UTF-8: {info.filename}") from exc
            # Parsing catches truncated/corrupt snapshots while the text aggregation below
            # deliberately stays schema-agnostic across compatible GZDoom save versions.
            json.loads(text)
            chunks.append(text)

    if not names:
        raise ValueError("Savegame contains no JSON snapshot entries")
    return names, "\n".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a GZDoom save archive used by CI.")
    parser.add_argument("savegame", type=Path)
    parser.add_argument("required", nargs="*", help="Case-sensitive strings that must occur in serialized JSON")
    args = parser.parse_args()

    try:
        names, text = collect_json_text(args.savegame)
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"Savegame validation failed: {exc}", file=sys.stderr)
        return 1

    missing = [needle for needle in args.required if needle not in text]
    if missing:
        print(
            f"Savegame validation failed: serialized JSON is missing {missing!r}",
            file=sys.stderr,
        )
        return 1

    print(
        f"GZDoom save archive: PASS ({args.savegame.name}; "
        f"{len(names)} JSON entries; required state present)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
