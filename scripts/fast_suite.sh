#!/usr/bin/env bash
# fast_suite.sh — iter95/sdk fast test gate (whitelist lane: this script + engine/tests/** ONLY).

set -euo pipefail

CANON_VENV="${CANON_VENV:-/home/julio/projects/clean_diallux_SDR/engine/.venv}"
PYT="$CANON_VENV/bin/python"

die() { echo "fast_suite: $*" >&2; exit 2; }

[ -x "$PYT" ] || die "canonical venv python missing: $PYT"
[ -f pytest.ini ] || die "cwd must be <repo>/engine (no pytest.ini here)"

run() {
  if [ $# -eq 0 ]; then
    echo "fast_suite: nothing to run (no touched tests, no affected importers)"
    exit 0
  fi
  echo "fast_suite: pytest $*"
  exec "$PYT" -m pytest "$@"
}

case "${1:-}" in
"")
  echo "usage: fast_suite.sh <node ids...> | --touched | --full   (cwd: <repo>/engine)"
  exit 2
  ;;
--full)
  run tests
  ;;
--touched)
  # (a) modified/untracked test files (porcelain paths are repo-root-relative)
  while IFS= read -r f; do
    case "$f" in engine/tests/*.py) echo "tests/${f#engine/tests/}" ;; esac
  done < <(git status --porcelain | awk '{print $NF}') > /tmp/fs_sel.$$

  # (b) test files importing changed diallux modules (uncommitted diff vs HEAD)
  changed="$(git diff --name-only HEAD -- engine/diallux || true)"
  if [ -n "$changed" ]; then
    pats=""
    for f in $changed; do
      mod="${f#engine/}"; mod="${mod%.py}"; mod="${mod//\//.}"
      if [ "$mod" = "diallux.config" ]; then
        echo "fast_suite: diallux/config.py changed — Settings is imported by ~every test; running FULL suite"
        rm -f /tmp/fs_sel.$$
        run tests
      fi
      leaf="${mod##*.}"; parent="${mod%.*}"
      pats="${pats}${pats:+|}${mod//./\\.}|${parent//./\\.} import ${leaf}"
    done
    grep -rlE "$pats" tests --include="*.py" >> /tmp/fs_sel.$$ 2>/dev/null || true
  fi

  mapfile -t sel < <(sort -u /tmp/fs_sel.$$ | sed '/^$/d'); rm -f /tmp/fs_sel.$$
  run "${sel[@]}"
  ;;
*)
  run "$@"
  ;;
esac
