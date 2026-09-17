#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PK3="$ROOT/dist/checkout-of-hell-prototype.pk3"
RUNTIME_MANIFEST="$ROOT/external/linux-ci/runtime.json"
WORKDIR="$ROOT/dist/save-load-roundtrip"
SAVEDIR="$WORKDIR/saves"
CONFIG="$WORKDIR/gzdoom-ci.ini"
CREATE_CFG="$WORKDIR/create-save.cfg"
LOAD_CFG="$WORKDIR/load-save.cfg"
CREATE_LOG="$WORKDIR/create-save.log"
LOAD_LOG="$WORKDIR/load-save.log"
TIMEOUT_SECONDS="${COH_GZDOOM_TIMEOUT:-35}"

python3 "$ROOT/tools/build.py"
python3 "$ROOT/tools/bootstrap_linux_ci_runtime.py"

if [[ ! -f "$RUNTIME_MANIFEST" ]]; then
    echo "ERROR: Linux CI runtime manifest was not created: $RUNTIME_MANIFEST" >&2
    exit 1
fi

FREEDOOM_WAD="$(python3 - "$RUNTIME_MANIFEST" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["freedoom_wad"])
PY
)"

for required in "$PK3" "$FREEDOOM_WAD"; do
    if [[ ! -f "$required" ]]; then
        echo "ERROR: Save/load prerequisite is missing: $required" >&2
        exit 1
    fi
done

if ! command -v gzdoom >/dev/null 2>&1; then
    echo "ERROR: gzdoom is not installed. Install the pinned official .deb resolved by bootstrap_linux_ci_runtime.py." >&2
    exit 1
fi
if ! command -v xvfb-run >/dev/null 2>&1; then
    echo "ERROR: xvfb-run is required for headless CI gameplay validation." >&2
    exit 1
fi

rm -rf "$WORKDIR"
mkdir -p "$SAVEDIR"

# GZDoom's wait command delays only the remainder of the same command string.
# Keep each phase on one semicolon-delimited line so map startup and save I/O
# happen on later tics instead of racing initial command dispatch. Use -exec,
# which GZDoom processes as a startup configuration file, rather than relying
# on a late +exec console command while the title loop is already active.
printf '%s\n' 'echo COH_SAVE_ROUNDTRIP_CREATE_BEGIN; map MAP01; wait 70; give CheckoutFuse; give CheckoutFuse; give CorporateMemo; wait 2; save coh-ci-roundtrip; wait 20; echo COH_SAVE_ROUNDTRIP_CREATE_DONE; quit' > "$CREATE_CFG"
printf '%s\n' 'echo COH_SAVE_ROUNDTRIP_LOAD_BEGIN; wait 70; echo COH_SAVE_ROUNDTRIP_LOAD_DONE; quit' > "$LOAD_CFG"

COMMON_ARGS=(
    -stdout
    -nostartup
    -nosound
    -nojoy
    -noautoload
    -iwad "$FREEDOOM_WAD"
    -file "$PK3"
    -config "$CONFIG"
    -savedir "$SAVEDIR"
    +vid_preferbackend 0
    +vid_fullscreen 0
)

run_gzdoom() {
    local phase="$1"
    local logfile="$2"
    shift 2
    echo "Running pinned GZDoom $phase phase under Xvfb..."
    set +e
    NO_AT_BRIDGE=1 SDL_AUDIODRIVER=dummy \
        timeout --signal=KILL "${TIMEOUT_SECONDS}s" \
        xvfb-run -a --server-args="-screen 0 1280x720x24 -nolisten tcp" \
        gzdoom "${COMMON_ARGS[@]}" "$@" >"$logfile" 2>&1
    local status=$?
    set -e
    cat "$logfile"
    if [[ $status -eq 124 || $status -eq 137 ]]; then
        echo "ERROR: GZDoom $phase phase exceeded the ${TIMEOUT_SECONDS}s timeout. See $logfile" >&2
        exit 1
    fi
    if [[ $status -ne 0 ]]; then
        echo "ERROR: GZDoom $phase phase failed with exit code $status. See $logfile" >&2
        exit 1
    fi

    local patterns=(
        "Script error"
        "Execution could not continue"
        "Unknown class"
        "Unknown identifier"
        "Unknown command"
        "Invalid parameter"
        "Parse error"
        "Could not save"
        "Could not load"
        "Savegame is from a different"
        "No such savegame"
        "File not found"
    )
    local pattern
    for pattern in "${patterns[@]}"; do
        if grep -Fqi "$pattern" "$logfile"; then
            echo "ERROR: GZDoom reported '$pattern' during the $phase phase." >&2
            exit 1
        fi
    done
}

run_gzdoom "save-create" "$CREATE_LOG" -skill 2 -exec "$CREATE_CFG"
grep -Fq "COH_SAVE_ROUNDTRIP_CREATE_DONE" "$CREATE_LOG" || {
    echo "ERROR: Save-create command sequence did not reach its completion sentinel." >&2
    exit 1
}

mapfile -d '' SAVE_FILES < <(find "$SAVEDIR" -type f -name '*.zds' -print0)
if [[ ${#SAVE_FILES[@]} -ne 1 ]]; then
    echo "ERROR: Expected exactly one .zds save after create phase, found ${#SAVE_FILES[@]}." >&2
    find "$SAVEDIR" -maxdepth 3 -type f -print >&2 || true
    exit 1
fi
SAVE_FILE="${SAVE_FILES[0]}"
SAVE_SIZE="$(stat -c '%s' "$SAVE_FILE")"
if (( SAVE_SIZE < 4096 )); then
    echo "ERROR: Generated save is unexpectedly small: $SAVE_SIZE bytes." >&2
    exit 1
fi
python3 - "$SAVE_FILE" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
if path.read_bytes()[:2] != b"PK":
    raise SystemExit(f"ERROR: {path} does not have the expected ZIP-based ZDoom save header")
print(f"Verified ZIP-based save container: {path} ({path.stat().st_size} bytes)")
PY

run_gzdoom "save-load" "$LOAD_LOG" -loadgame "$SAVE_FILE" -exec "$LOAD_CFG"
grep -Fq "COH_SAVE_ROUNDTRIP_LOAD_DONE" "$LOAD_LOG" || {
    echo "ERROR: Save-load command sequence did not reach its completion sentinel." >&2
    exit 1
}

echo "Pinned GZDoom save/load roundtrip: PASS"
