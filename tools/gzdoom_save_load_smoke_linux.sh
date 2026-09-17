#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/dist/save-load-linux"
RUNTIME="$WORK/runtime"
SAVES="$WORK/saves"
INI="$WORK/gzdoom-ci.ini"
SAVE_LOG="$WORK/save.log"
LOAD_LOG="$WORK/load.log"
COMBINED="$ROOT/dist/gzdoom-save-load-smoke.log"
SAVE_STEM="coh-ci-roundtrip"
PK3="$ROOT/dist/checkout-of-hell-prototype.pk3"
FREEDOOM_WAD="$RUNTIME/freedoom2.wad"
GZDOOM_DEB="$RUNTIME/gzdoom.deb"
DISPLAY_NUM=99
DISPLAY=":$DISPLAY_NUM"
XVFB_LOG="$WORK/xvfb.log"
RESULT="FAIL - runtime gate did not complete"
XVFB_PID=""
ENGINE_PID=""

mkdir -p "$RUNTIME" "$SAVES"
rm -f "$SAVE_LOG" "$LOAD_LOG" "$COMBINED" "$XVFB_LOG"
python "$ROOT/tools/build.py"

api_get() {
  local url="$1"
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl --fail --silent --show-error --location --retry 3 --retry-all-errors \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "Authorization: Bearer $GITHUB_TOKEN" "$url"
  else
    curl --fail --silent --show-error --location --retry 3 --retry-all-errors \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" "$url"
  fi
}

download() {
  local url="$1"
  local dest="$2"
  curl --fail --silent --show-error --location --retry 3 --retry-all-errors \
    -H "User-Agent: checkout-of-hell-runtime-test" "$url" -o "$dest"
}

readarray -t LOCK_VALUES < <(python - "$ROOT/runtime-lock.json" <<'PY'
import json, sys
lock = json.load(open(sys.argv[1], encoding="utf-8"))
print(lock["gzdoom"]["repo"])
print(lock["gzdoom"]["tag"])
print(lock["freedoom"]["repo"])
print(lock["freedoom"]["tag"])
print(lock["freedoom"]["asset_regex"])
print(lock["freedoom"]["checksum_regex"])
PY
)
GZ_REPO="${LOCK_VALUES[0]}"
GZ_TAG="${LOCK_VALUES[1]}"
FD_REPO="${LOCK_VALUES[2]}"
FD_TAG="${LOCK_VALUES[3]}"
FD_ASSET_REGEX="${LOCK_VALUES[4]}"
FD_CHECKSUM_REGEX="${LOCK_VALUES[5]}"

GZ_RELEASE="$WORK/gzdoom-release.json"
FD_RELEASE="$WORK/freedoom-release.json"
api_get "https://api.github.com/repos/$GZ_REPO/releases/tags/$GZ_TAG" > "$GZ_RELEASE"
api_get "https://api.github.com/repos/$FD_REPO/releases/tags/$FD_TAG" > "$FD_RELEASE"

readarray -t GZ_ASSET < <(python - "$GZ_RELEASE" <<'PY'
import json, re, sys
release = json.load(open(sys.argv[1], encoding="utf-8"))
matches = [a for a in release.get("assets", []) if re.fullmatch(r"gzdoom_.*_amd64\.deb", a["name"])]
if len(matches) != 1:
    raise SystemExit(f"Expected exactly one official amd64 GZDoom DEB, found {len(matches)}")
a = matches[0]
print(a["name"])
print(a["browser_download_url"])
PY
)

readarray -t FD_ASSETS < <(python - "$FD_RELEASE" "$FD_ASSET_REGEX" "$FD_CHECKSUM_REGEX" <<'PY'
import json, re, sys
release = json.load(open(sys.argv[1], encoding="utf-8"))
asset_re = re.compile(sys.argv[2])
checksum_re = re.compile(sys.argv[3])
assets = [a for a in release.get("assets", []) if asset_re.fullmatch(a["name"])]
checks = [a for a in release.get("assets", []) if checksum_re.fullmatch(a["name"])]
if len(assets) != 1 or len(checks) != 1:
    raise SystemExit(f"Expected one Freedoom ZIP and one checksum asset, found {len(assets)} and {len(checks)}")
print(assets[0]["name"])
print(assets[0]["browser_download_url"])
print(checks[0]["name"])
print(checks[0]["browser_download_url"])
PY
)

printf 'Pinned runtime: GZDoom %s / %s\n' "$GZ_TAG" "${GZ_ASSET[0]}"
printf 'Pinned content: Freedoom %s / %s\n' "$FD_TAG" "${FD_ASSETS[0]}"

download "${GZ_ASSET[1]}" "$GZDOOM_DEB"
FD_ZIP="$RUNTIME/${FD_ASSETS[0]}"
FD_CHECKSUM="$RUNTIME/${FD_ASSETS[2]}"
download "${FD_ASSETS[1]}" "$FD_ZIP"
download "${FD_ASSETS[3]}" "$FD_CHECKSUM"

EXPECTED_FD_SHA="$(python - "$FD_CHECKSUM" "${FD_ASSETS[0]}" <<'PY'
import re, sys
lines = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
name = sys.argv[2]
for line in lines:
    if name in line:
        m = re.search(r"\b([0-9A-Fa-f]{64})\b", line)
        if m:
            print(m.group(1).lower())
            break
else:
    raise SystemExit("Official Freedoom checksum file has no SHA-256 entry for the selected ZIP")
PY
)"
ACTUAL_FD_SHA="$(sha256sum "$FD_ZIP" | awk '{print $1}')"
if [[ "$EXPECTED_FD_SHA" != "$ACTUAL_FD_SHA" ]]; then
  echo "Freedoom SHA-256 mismatch: expected $EXPECTED_FD_SHA, got $ACTUAL_FD_SHA" >&2
  exit 1
fi
echo "Freedoom SHA-256 verified."

rm -rf "$RUNTIME/freedoom-stage"
mkdir -p "$RUNTIME/freedoom-stage"
unzip -q "$FD_ZIP" -d "$RUNTIME/freedoom-stage"
FOUND_WAD="$(find "$RUNTIME/freedoom-stage" -type f -name freedoom2.wad -print -quit)"
if [[ -z "$FOUND_WAD" ]]; then
  echo "Official Freedoom archive does not contain freedoom2.wad" >&2
  exit 1
fi
cp "$FOUND_WAD" "$FREEDOOM_WAD"

# Hosted Windows can parse the pinned package with -norun, but its live runner has
# no usable graphics adapter. For the actual serialization round-trip, run the
# exact same pinned GZDoom version under Xvfb and Mesa llvmpipe, then drive the
# real in-game console through X11. This exercises a live game loop rather than a
# parser-only path or a mocked serializer.
sudo apt-get update -qq
sudo apt-get install -y -qq xvfb xdotool libgl1-mesa-dri "$GZDOOM_DEB"
GZDOOM_BIN="$(command -v gzdoom)"
if [[ -z "$GZDOOM_BIN" ]]; then
  echo "The official GZDoom DEB did not install a gzdoom executable" >&2
  exit 1
fi

cat > "$INI" <<'EOF'
[GlobalSettings]
vid_preferbackend=0
vid_fullscreen=false
vid_vsync=false
i_pauseinbackground=false
i_soundinbackground=false
storesavepic=false
EOF

COMMON=(
  -nosound
  -noautoload
  -width 640
  -height 480
  -config "$INI"
  -iwad "$FREEDOOM_WAD"
  -file "$PK3"
  -savedir "$SAVES"
)

write_combined() {
  {
    echo "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke"
    echo
    echo "Pinned engine: $GZ_TAG"
    echo "Pinned base data: $FD_TAG"
    echo
    echo "=== SAVE PASS ==="
    [[ -f "$SAVE_LOG" ]] && cat "$SAVE_LOG" || true
    echo
    echo "=== LOAD PASS ==="
    [[ -f "$LOAD_LOG" ]] && cat "$LOAD_LOG" || true
    echo
    echo "=== XVFB ==="
    [[ -f "$XVFB_LOG" ]] && cat "$XVFB_LOG" || true
    echo
    echo "RESULT: $RESULT"
  } > "$COMBINED"
}

cleanup() {
  if [[ -n "$ENGINE_PID" ]] && kill -0 "$ENGINE_PID" 2>/dev/null; then
    kill "$ENGINE_PID" 2>/dev/null || true
    wait "$ENGINE_PID" 2>/dev/null || true
  fi
  if [[ -n "$XVFB_PID" ]] && kill -0 "$XVFB_PID" 2>/dev/null; then
    kill "$XVFB_PID" 2>/dev/null || true
    wait "$XVFB_PID" 2>/dev/null || true
  fi
  write_combined
}
trap cleanup EXIT

Xvfb "$DISPLAY" -screen 0 800x600x24 -nolisten tcp >"$XVFB_LOG" 2>&1 &
XVFB_PID=$!
export DISPLAY
for _ in $(seq 1 40); do
  if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then break; fi
  sleep 0.25
done
if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
  echo "Xvfb did not become ready" >&2
  exit 1
fi

launch_engine() {
  local log="$1"
  shift
  rm -f "$log"
  env LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe SDL_AUDIODRIVER=dummy \
    "$GZDOOM_BIN" "${COMMON[@]}" +logfile "$log" "$@" >/dev/null 2>&1 &
  ENGINE_PID=$!

  local window=""
  for _ in $(seq 1 120); do
    if ! kill -0 "$ENGINE_PID" 2>/dev/null; then
      echo "GZDoom exited before creating its runtime window" >&2
      return 1
    fi
    window="$(xdotool search --pid "$ENGINE_PID" 2>/dev/null | tail -n 1 || true)"
    if [[ -n "$window" ]]; then
      echo "$window"
      return 0
    fi
    sleep 0.25
  done
  echo "GZDoom did not create a runtime window within 30 seconds" >&2
  return 1
}

send_console_command() {
  local window="$1"
  local command="$2"
  xdotool windowfocus "$window"
  xdotool type --clearmodifiers --window "$window" --delay 2 "$command"
  xdotool key --clearmodifiers --window "$window" Return
  sleep 0.35
}

open_console() {
  local window="$1"
  xdotool windowfocus "$window"
  xdotool key --clearmodifiers --window "$window" grave
  sleep 0.5
}

wait_for_log_marker() {
  local log="$1"
  local marker="$2"
  for _ in $(seq 1 80); do
    if [[ -f "$log" ]] && grep -Fq "$marker" "$log"; then return 0; fi
    if [[ -n "$ENGINE_PID" ]] && ! kill -0 "$ENGINE_PID" 2>/dev/null; then return 1; fi
    sleep 0.25
  done
  return 1
}

stop_engine() {
  if [[ -n "$ENGINE_PID" ]] && kill -0 "$ENGINE_PID" 2>/dev/null; then
    kill -TERM "$ENGINE_PID" 2>/dev/null || true
    for _ in $(seq 1 20); do
      if ! kill -0 "$ENGINE_PID" 2>/dev/null; then break; fi
      sleep 0.1
    done
    if kill -0 "$ENGINE_PID" 2>/dev/null; then kill -KILL "$ENGINE_PID" 2>/dev/null || true; fi
    wait "$ENGINE_PID" 2>/dev/null || true
  fi
  ENGINE_PID=""
}

assert_no_runtime_errors() {
  local log="$1"
  for pattern in 'Script error' 'Execution could not continue' 'Unknown class' 'Unknown identifier' 'Invalid parameter' 'Parse error' 'Cannot load savegame' 'Could not open savegame'; do
    if grep -Fq "$pattern" "$log"; then
      echo "GZDoom reported runtime error: $pattern" >&2
      return 1
    fi
  done
}

# PASS 1: create state in a live MAP01 session and serialize it.
SAVE_WINDOW="$(launch_engine "$SAVE_LOG" +map MAP01)"
sleep 3
open_console "$SAVE_WINDOW"
send_console_command "$SAVE_WINDOW" "give CheckoutFuse 2"
send_console_command "$SAVE_WINDOW" "printinv"
send_console_command "$SAVE_WINDOW" "save $SAVE_STEM \"CHECKOUT OF HELL CI ROUNDTRIP\""
sleep 1
send_console_command "$SAVE_WINDOW" "echo COH_RUNTIME_SAVE_WRITTEN"
if ! wait_for_log_marker "$SAVE_LOG" "COH_RUNTIME_SAVE_WRITTEN"; then
  echo "Save pass did not reach its completion sentinel" >&2
  exit 1
fi
if ! grep -Eq 'CheckoutFuse[[:space:]]+#[0-9]+[[:space:]]+\(2/3\)' "$SAVE_LOG"; then
  echo "Save pass did not expose CheckoutFuse 2/3 before saving" >&2
  exit 1
fi
SAVE_FILE="$(find "$SAVES" -maxdepth 1 -type f -name "$SAVE_STEM*.zds" -print -quit)"
if [[ -z "$SAVE_FILE" || ! -s "$SAVE_FILE" ]]; then
  echo "GZDoom did not create a non-empty savegame" >&2
  exit 1
fi
if [[ "$(stat -c %s "$SAVE_FILE")" -lt 4096 ]]; then
  echo "GZDoom savegame is unexpectedly small" >&2
  exit 1
fi
assert_no_runtime_errors "$SAVE_LOG"
stop_engine

# PASS 2: new GZDoom process, load the actual save file, inspect serialized state.
LOAD_WINDOW="$(launch_engine "$LOAD_LOG" -loadgame "$SAVE_STEM")"
sleep 3
open_console "$LOAD_WINDOW"
send_console_command "$LOAD_WINDOW" "printinv"
send_console_command "$LOAD_WINDOW" "echo COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE"
if ! wait_for_log_marker "$LOAD_LOG" "COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE"; then
  echo "Load pass did not reach its completion sentinel" >&2
  exit 1
fi
if ! grep -Eq 'CheckoutFuse[[:space:]]+#[0-9]+[[:space:]]+\(2/3\)' "$LOAD_LOG"; then
  echo "CheckoutFuse 2/3 did not survive save -> process exit -> load" >&2
  exit 1
fi
assert_no_runtime_errors "$LOAD_LOG"
stop_engine

RESULT="PASS - CheckoutFuse 2/3 survived real save -> process exit -> load"
write_combined
echo "GZDoom runtime save/load round-trip: PASS"
