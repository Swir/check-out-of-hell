#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PK3="$ROOT/dist/checkout-of-hell-prototype.pk3"
FREEDOOM="$ROOT/external/freedoom2.wad"
WORK="$ROOT/dist/save-load-smoke-linux"
SAVES="$WORK/saves"
LOG="$ROOT/dist/gzdoom-save-load-smoke.log"
CREATE_CFG="$WORK/create-save.cfg"
LOAD_CFG="$WORK/load-save.cfg"
INSPECTOR="$ROOT/tools/inspect_gzdoom_save.py"

python "$ROOT/tools/build.py"

for required in "$PK3" "$FREEDOOM" "$INSPECTOR"; do
  if [[ ! -f "$required" ]]; then
    echo "Save/load smoke prerequisite is missing: $required" >&2
    exit 1
  fi
done
if ! command -v gzdoom >/dev/null 2>&1; then
  echo "gzdoom is not installed; run the pinned Linux runtime bootstrap/install step first." >&2
  exit 1
fi
if ! command -v xvfb-run >/dev/null 2>&1; then
  echo "xvfb-run is not installed; the hosted live-engine test needs a virtual X display." >&2
  exit 1
fi

rm -rf "$WORK"
mkdir -p "$SAVES"
: > "$LOG"

cat > "$CREATE_CFG" <<'EOF'
wait 70; god; give CheckoutFuse 2; give CorporateMemo 1; wait 4; save coh-save-load-ci "CHECKOUT OF HELL CI SAVE"; wait 35; quit
EOF
cat > "$LOAD_CFG" <<'EOF'
wait 70; save coh-save-load-ci-roundtrip "CHECKOUT OF HELL CI ROUNDTRIP"; wait 35; quit
EOF

run_scenario() {
  local label="$1"
  local cfg="$2"
  shift 2
  local scenario_log="$WORK/$label.log"

  echo "Running pinned GZDoom $label scenario..."
  set +e
  timeout --signal=KILL 25s xvfb-run -a -s "-screen 0 640x480x24" \
    env LIBGL_ALWAYS_SOFTWARE=1 \
    gzdoom \
      -stdout -nosound -window -width 320 -height 200 \
      +vid_preferbackend 0 +vid_rendermode 0 +vid_activeinbackground true \
      -savedir "$SAVES" -iwad "$FREEDOOM" -file "$PK3" \
      "$@" +exec "$cfg" >"$scenario_log" 2>&1
  local status=$?
  set -e

  {
    echo "=== $label (exit $status) ==="
    cat "$scenario_log" 2>/dev/null || true
    echo "--- $label save directory ---"
    find "$SAVES" -maxdepth 1 -type f -printf '%f - %s bytes\n' 2>/dev/null || true
  } >> "$LOG"
  cat "$scenario_log" 2>/dev/null || true

  if [[ $status -ne 0 ]]; then
    echo "Pinned GZDoom $label scenario failed with exit code $status. See $LOG" >&2
    exit 1
  fi

  for pattern in \
    "Script error" \
    "Execution could not continue" \
    "Unknown class" \
    "Unknown identifier" \
    "Invalid parameter" \
    "Parse error" \
    "Cannot execute unsafe command" \
    "Save failed"; do
    if grep -Fqi "$pattern" "$scenario_log"; then
      echo "Pinned GZDoom $label scenario reported '$pattern'. See $LOG" >&2
      exit 1
    fi
  done
}

single_save() {
  local pattern="$1"
  local label="$2"
  mapfile -t matches < <(find "$SAVES" -maxdepth 1 -type f -name "$pattern" -print | sort)
  if [[ ${#matches[@]} -ne 1 ]]; then
    echo "Expected exactly one $label save matching '$pattern', found ${#matches[@]}. See $LOG" >&2
    exit 1
  fi
  local size
  size="$(stat -c '%s' "${matches[0]}")"
  if [[ $size -lt 1024 ]]; then
    echo "$label save is unexpectedly small: $size bytes." >&2
    exit 1
  fi
  printf '%s\n' "${matches[0]}"
}

run_scenario create-save "$CREATE_CFG" +map MAP01
initial_save="$(single_save '*coh-save-load-ci*.zds' initial)"
python "$INSPECTOR" "$initial_save" CheckoutFuse CorporateMemo | tee -a "$LOG"

run_scenario load-save "$LOAD_CFG" -loadgame coh-save-load-ci
roundtrip_save="$(single_save '*coh-save-load-ci-roundtrip*.zds' round-trip)"
python "$INSPECTOR" "$roundtrip_save" CheckoutFuse CorporateMemo | tee -a "$LOG"

{
  echo "Initial save: $(stat -c '%s' "$initial_save") bytes"
  echo "Round-trip save: $(stat -c '%s' "$roundtrip_save") bytes"
  echo "Required serialized objective state: CheckoutFuse, CorporateMemo"
} >> "$LOG"

echo "Pinned GZDoom save/load smoke test: PASS"
