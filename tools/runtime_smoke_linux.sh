#!/usr/bin/env bash
set -euo pipefail

GZDOOM="${1:-/usr/games/gzdoom}"
IWAD="${2:-external-linux/freedoom2.wad}"
PK3="${3:-dist/checkout-of-hell-prototype.pk3}"
LOG="${4:-dist/gzdoom-linux-validation.log}"

for required in "$GZDOOM" "$IWAD" "$PK3"; do
  if [[ ! -f "$required" ]]; then
    echo "Runtime validation prerequisite is missing: $required" >&2
    exit 2
  fi
done

mkdir -p "$(dirname "$LOG")"
rm -f "$LOG"

# GZDoom returns the special value 1337 from GameMain for -norun. POSIX exit
# codes are 8-bit, so the shell observes 1337 % 256 = 57. Xvfb + Mesa's
# software renderer gives the hosted Linux runner a real graphics context while
# -errorlog enables GZDoom's batch path and -norun stops before gameplay.
set +e
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a "$GZDOOM" \
  -iwad "$IWAD" \
  -file "$PK3" \
  -noautoload \
  -nosound \
  -nomusic \
  -errorlog "$LOG" \
  -norun
status=$?
set -e

if [[ -f "$LOG" ]]; then
  echo "----- GZDoom validation log -----"
  tail -n 250 "$LOG"
fi

if [[ ! -f "$LOG" ]]; then
  echo "GZDoom did not create its batch validation log." >&2
  exit 3
fi

if grep -Eiq 'DIED WITH FATAL ERROR|Execution could not continue|Script error|Unknown class|Invalid data encountered' "$LOG"; then
  echo "GZDoom reported a fatal/parser error." >&2
  exit 4
fi

if ! grep -Fq "checkout-of-hell-prototype.pk3" "$LOG"; then
  echo "GZDoom validation log does not show the project PK3 being loaded." >&2
  exit 5
fi

if [[ "$status" -ne 0 && "$status" -ne 57 ]]; then
  echo "GZDoom batch validation exited unexpectedly with status $status." >&2
  exit "$status"
fi

echo "GZDoom headless startup/parser validation: PASS (status $status)"
