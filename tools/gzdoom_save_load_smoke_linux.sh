#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK="$ROOT/runtime-lock.json"
CACHE="$ROOT/.cache/runtime-linux"
RUNTIME="$ROOT/external/linux-runtime"
PROBE="$ROOT/dist/runtime-save-load-linux"
SAVES="$PROBE/saves"
CONFIG="$PROBE/gzdoom-runtime-probe.ini"
SAVE_LOG="$PROBE/save-pass.log"
LOAD_LOG="$PROBE/load-pass.log"
COMBINED_LOG="$ROOT/dist/gzdoom-save-load-smoke.log"
PK3="$ROOT/dist/checkout-of-hell-prototype.pk3"

mkdir -p "$CACHE" "$RUNTIME" "$SAVES" "$ROOT/dist"

api_headers=(-H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" -H "User-Agent: checkout-of-hell-runtime-smoke")
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  api_headers+=(-H "Authorization: Bearer $GITHUB_TOKEN")
fi

read_lock() {
  python3 - "$LOCK" "$1" "$2" <<'PY'
import json, sys
lock_path, section, key = sys.argv[1:]
with open(lock_path, encoding="utf-8") as f:
    data = json.load(f)
value = data[section][key]
if not isinstance(value, str) or not value:
    raise SystemExit(f"Missing runtime-lock value {section}.{key}")
print(value)
PY
}

download_retry() {
  local url="$1" destination="$2"
  local attempt
  for attempt in 1 2 3; do
    if curl --fail --location --silent --show-error "${api_headers[@]}" "$url" --output "$destination"; then
      return 0
    fi
    if [[ "$attempt" -lt 3 ]]; then
      sleep $((attempt * 2))
    fi
  done
  echo "Download failed after 3 attempts: $url" >&2
  return 1
}

resolve_asset() {
  local repo="$1" tag="$2" regex="$3" description="$4"
  local metadata="$CACHE/release-$(echo "$repo-$tag" | tr '/:' '__').json"
  download_retry "https://api.github.com/repos/$repo/releases/tags/$tag" "$metadata"
  python3 - "$metadata" "$regex" "$description" <<'PY'
import json, re, sys
path, pattern, description = sys.argv[1:]
with open(path, encoding="utf-8") as f:
    release = json.load(f)
for asset in release.get("assets", []):
    if re.search(pattern, asset.get("name", "")):
        print(asset["name"])
        print(asset["browser_download_url"])
        raise SystemExit(0)
raise SystemExit(f"Could not find {description} in official release {release.get('tag_name', '?')}")
PY
}

assert_clean_log() {
  local log="$1" phase="$2"
  local pattern='Script error|Execution could not continue|Unknown class|Unknown identifier|Invalid parameter|Parse error|VM execution aborted|Could not load savegame|Savegame is from a different version|Savegame uses a different set of files|Fatal error|Segmentation fault'
  if grep -Eiq "$pattern" "$log"; then
    echo "GZDoom reported an error during $phase. See $log" >&2
    cat "$log" >&2
    return 1
  fi
}

run_probe() {
  local phase="$1" log="$2"
  shift 2
  set +e
  LIBGL_ALWAYS_SOFTWARE=1 timeout --signal=TERM --kill-after=2s 10s \
    xvfb-run -a "$GZDOOM" "$@" >"$log" 2>&1
  local code=$?
  set -e

  # 124 is expected when the interactive engine stays healthy until the probe window ends.
  if [[ "$code" -ne 0 && "$code" -ne 124 && "$code" -ne 143 ]]; then
    echo "GZDoom $phase probe failed with exit code $code." >&2
    cat "$log" >&2
    return 1
  fi
  assert_clean_log "$log" "$phase"
}

echo "Building current prototype..."
python3 "$ROOT/tools/build.py"
[[ -f "$PK3" ]] || { echo "Prototype build did not produce $PK3" >&2; exit 1; }

GZ_REPO="$(read_lock gzdoom repo)"
GZ_TAG="$(read_lock gzdoom tag)"
GZ_REGEX="$(read_lock gzdoom linux_asset_regex)"
FD_REPO="$(read_lock freedoom repo)"
FD_TAG="$(read_lock freedoom tag)"
FD_REGEX="$(read_lock freedoom asset_regex)"
FD_CHECKSUM_REGEX="$(read_lock freedoom checksum_regex)"

mapfile -t gz_meta < <(resolve_asset "$GZ_REPO" "$GZ_TAG" "$GZ_REGEX" "GZDoom Linux amd64 DEB")
mapfile -t fd_meta < <(resolve_asset "$FD_REPO" "$FD_TAG" "$FD_REGEX" "Freedoom ZIP")
mapfile -t fd_sum_meta < <(resolve_asset "$FD_REPO" "$FD_TAG" "$FD_CHECKSUM_REGEX" "Freedoom checksum")

GZ_DEB="$CACHE/${gz_meta[0]}"
FD_ZIP="$CACHE/${fd_meta[0]}"
FD_SUM="$CACHE/${fd_sum_meta[0]}"
download_retry "${gz_meta[1]}" "$GZ_DEB"
download_retry "${fd_meta[1]}" "$FD_ZIP"
download_retry "${fd_sum_meta[1]}" "$FD_SUM"

expected_sha="$(grep -F "${fd_meta[0]}" "$FD_SUM" | grep -Eo '[A-Fa-f0-9]{64}' | head -n 1 || true)"
if [[ -z "$expected_sha" ]]; then
  echo "Official Freedoom checksum file did not contain a parseable SHA-256 entry for ${fd_meta[0]}." >&2
  exit 1
fi
actual_sha="$(sha256sum "$FD_ZIP" | awk '{print $1}')"
if [[ "${actual_sha,,}" != "${expected_sha,,}" ]]; then
  echo "Freedoom SHA-256 mismatch. Expected $expected_sha but got $actual_sha." >&2
  exit 1
fi
echo "Freedoom SHA-256 verified."

rm -rf "$RUNTIME/freedoom"
mkdir -p "$RUNTIME/freedoom"
unzip -q "$FD_ZIP" -d "$RUNTIME/freedoom"
FREEDOOM_WAD="$(find "$RUNTIME/freedoom" -type f -name freedoom2.wad -print -quit)"
[[ -n "$FREEDOOM_WAD" && -s "$FREEDOOM_WAD" ]] || { echo "Official Freedoom archive did not contain freedoom2.wad." >&2; exit 1; }

# The official GZDoom .deb plus distro-provided runtime libraries are used only on the
# disposable CI runner. Xvfb + Mesa llvmpipe provides a software display/GPU so the real
# engine can enter a level and exercise save serialization without physical graphics hardware.
sudo apt-get update -qq
sudo apt-get install -y -qq xvfb libgl1-mesa-dri "$GZ_DEB"
GZDOOM="$(command -v gzdoom || true)"
if [[ -z "$GZDOOM" ]]; then
  GZDOOM="$(dpkg -L gzdoom 2>/dev/null | grep -E '/gzdoom$' | head -n 1 || true)"
fi
[[ -x "$GZDOOM" ]] || { echo "Installed official GZDoom package did not expose an executable." >&2; exit 1; }

rm -rf "$PROBE"
mkdir -p "$SAVES"

common=(
  -stdout
  -nosound
  -nomusic
  -noautoload
  -config "$CONFIG"
  -savedir "$SAVES"
  -iwad "$FREEDOOM_WAD"
  -file "$PK3"
  +vid_fullscreen 0
  +vid_preferbackend 0
  +vid_rendermode 0
)

echo "Creating an actual MAP01 savegame with pinned GZDoom $GZ_TAG..."
run_probe save "$SAVE_LOG" "${common[@]}" \
  +map MAP01 \
  +give CheckoutFuse 2 \
  +give CorporateMemo 1 \
  +save coh-runtime-probe

SAVE_FILE="$(find "$SAVES" -type f -name '*.zds' -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2- || true)"
if [[ -z "$SAVE_FILE" || ! -f "$SAVE_FILE" ]]; then
  echo "GZDoom ran without script errors but did not create a .zds savegame under $SAVES." >&2
  cat "$SAVE_LOG" >&2
  exit 1
fi
if [[ "$(stat -c %s "$SAVE_FILE")" -lt 1024 ]]; then
  echo "Created savegame is unexpectedly small: $SAVE_FILE" >&2
  exit 1
fi

python3 - "$SAVE_FILE" <<'PY'
import sys, zipfile
path = sys.argv[1]
with zipfile.ZipFile(path) as zf:
    names = set(zf.namelist())
    if len(names) < 3:
        raise SystemExit(f"Save archive contains too few entries: {len(names)}")
    if "globals.json" not in names:
        raise SystemExit("Save archive is missing globals.json")
print(f"Validated GZDoom save archive: {path}")
PY

echo "Reloading that savegame in a fresh pinned GZDoom process..."
run_probe load "$LOAD_LOG" "${common[@]}" -loadgame "$SAVE_FILE"

{
  echo "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke"
  echo "GZDoom: $GZ_TAG / ${gz_meta[0]}"
  echo "Freedoom: $FD_TAG / ${fd_meta[0]}"
  echo "Savegame: $SAVE_FILE"
  echo "Save bytes: $(stat -c %s "$SAVE_FILE")"
  echo
  echo "===== SAVE PASS ====="
  cat "$SAVE_LOG"
  echo
  echo "===== LOAD PASS ====="
  cat "$LOAD_LOG"
  echo
  echo "Runtime save/load smoke: PASS"
} >"$COMBINED_LOG"

echo "Runtime save/load smoke: PASS"
echo "Created and reloaded $(basename "$SAVE_FILE") using official pinned upstream releases."
