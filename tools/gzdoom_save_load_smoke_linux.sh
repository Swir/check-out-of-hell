#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/dist/save-load-linux"
RUNTIME="$WORK/runtime"
SAVES="$WORK/saves"
SAVE_CFG="$WORK/save-roundtrip.cfg"
LOAD_CFG="$WORK/load-roundtrip.cfg"
INI="$WORK/gzdoom-ci.ini"
SAVE_LOG="$WORK/save.log"
LOAD_LOG="$WORK/load.log"
COMBINED="$ROOT/dist/gzdoom-save-load-smoke.log"
SAVE_STEM="coh-ci-roundtrip"
PK3="$ROOT/dist/checkout-of-hell-prototype.pk3"
FREEDOOM_WAD="$RUNTIME/freedoom2.wad"
GZDOOM_DEB="$RUNTIME/gzdoom.deb"

mkdir -p "$RUNTIME" "$SAVES"
python "$ROOT/tools/build.py"

api_get() {
  local url="$1"
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl --fail --silent --show-error --location \
      --retry 3 --retry-all-errors \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      "$url"
  else
    curl --fail --silent --show-error --location \
      --retry 3 --retry-all-errors \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$url"
  fi
}

download() {
  local url="$1"
  local dest="$2"
  curl --fail --silent --show-error --location \
    --retry 3 --retry-all-errors \
    -H "User-Agent: checkout-of-hell-runtime-test" \
    "$url" -o "$dest"
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
text = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
name = sys.argv[2]
for line in text:
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

# GitHub's Windows hosted runner exposes no usable OpenGL/Vulkan adapter for a
# live GZDoom game loop. Use the exact same pinned engine version on Ubuntu with
# Xvfb and Mesa llvmpipe so save serialization is exercised by the real engine.
sudo apt-get update -qq
sudo apt-get install -y -qq xvfb libgl1-mesa-dri "$GZDOOM_DEB"
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
EOF

cat > "$SAVE_CFG" <<EOF
wait 70; give CheckoutFuse 2; wait 5; printinv; save $SAVE_STEM "CHECKOUT OF HELL CI ROUNDTRIP"; wait 10; echo COH_RUNTIME_SAVE_WRITTEN; quit
EOF
cat > "$LOAD_CFG" <<'EOF'
wait 70; printinv; echo COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE; wait 5; quit
EOF

run_gzdoom() {
  local log="$1"
  shift
  set +e
  timeout 50s xvfb-run -a -s "-screen 0 800x600x24" \
    env LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    "$GZDOOM_BIN" "$@" >"$log" 2>&1
  local rc=$?
  set -e
  if [[ $rc -eq 124 ]]; then
    echo "GZDoom runtime phase timed out" >&2
    return 124
  fi
  if [[ $rc -ne 0 ]]; then
    echo "GZDoom runtime phase failed with exit code $rc" >&2
    return "$rc"
  fi
}

COMMON=(
  -stdout
  -nosound
  -noautoload
  -config "$INI"
  -iwad "$FREEDOOM_WAD"
  -file "$PK3"
  -savedir "$SAVES"
)

write_combined() {
  {
    echo "CHECKOUT OF HELL - pinned GZDoom save/load runtime smoke"
    echo
    echo "=== SAVE PASS ==="
    [[ -f "$SAVE_LOG" ]] && cat "$SAVE_LOG" || true
    echo
    echo "=== LOAD PASS ==="
    [[ -f "$LOAD_LOG" ]] && cat "$LOAD_LOG" || true
  } > "$COMBINED"
}
trap write_combined EXIT

run_gzdoom "$SAVE_LOG" "${COMMON[@]}" +map MAP01 +exec "$SAVE_CFG"
if ! grep -q 'COH_RUNTIME_SAVE_WRITTEN' "$SAVE_LOG"; then
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

run_gzdoom "$LOAD_LOG" "${COMMON[@]}" -loadgame "$SAVE_STEM" +exec "$LOAD_CFG"
if ! grep -q 'COH_RUNTIME_SAVE_LOAD_ROUNDTRIP_COMPLETE' "$LOAD_LOG"; then
  echo "Load pass did not reach its completion sentinel" >&2
  exit 1
fi
if ! grep -Eq 'CheckoutFuse[[:space:]]+#[0-9]+[[:space:]]+\(2/3\)' "$LOAD_LOG"; then
  echo "CheckoutFuse 2/3 did not survive save -> process exit -> load" >&2
  exit 1
fi

for pattern in 'Script error' 'Execution could not continue' 'Unknown class' 'Unknown identifier' 'Invalid parameter' 'Parse error' 'Cannot load savegame' 'Could not open savegame'; do
  if grep -Fq "$pattern" "$SAVE_LOG" "$LOAD_LOG"; then
    echo "GZDoom reported runtime error: $pattern" >&2
    exit 1
  fi
done

echo "PASS: CheckoutFuse 2/3 survived a real GZDoom save -> process exit -> load round-trip." >> "$COMBINED"
echo "GZDoom runtime save/load round-trip: PASS"
