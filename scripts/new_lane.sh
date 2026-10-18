#!/usr/bin/env bash
# new_lane.sh — open an iteration lane in ONE audited step (iter91 tooling).
#
# Kills the recurring env/venv drift class: worktrees are created naked
# (gitignored .venv/.env do not follow), so sessions improvised — copied envs
# from other worktrees (carrying stale values like WARM_AWAIT_DEST_MS=250 and
# DEEPGRAM_EAGER_EOT_THRESHOLD=0.7) and "borrowed" venvs by remembered paths.
#
# Usage:
#   scripts/new_lane.sh <iterNN> <base-sha-or-branch> <slug>
#   scripts/new_lane.sh --list
#
# What it does:
#   1. git worktree add /tmp/opencode/wt-<iterNN> -b engine/<iterNN>-<slug> <base>
#   2. symlink  <worktree>/engine/.venv -> canonical venv (shared, read-only)
#   3. generate <worktree>/engine/.env FROM THE CANONICAL env (never from a worktree)
#   4. AUDIT GATE against known-bad values (FIND-37/38, Deepgram 400 probe 2026-10-03):
#        - WARM_AWAIT_DEST_MS=250            (stale; ratified 2500)
#        - missing CARTESIA_MODEL_ID pin     (2026-09-23 paid lesson)
#        - DEEPGRAM_EAGER_EOT_THRESHOLD > DEEPGRAM_EOT_THRESHOLD → Deepgram 400
#   5. append verdict line to /tmp/opencode/lane_manifest.txt
#
# Exit 0 = lane READY; exit 1 = lane DOA (audit failed — fix env before boot).
# It ONLY creates new lane folders. It never touches the OREGON main checkout,
# existing worktrees, services, or anything already running.

set -euo pipefail

REPO=${REPO:-/home/julio/projects/clean_diallux_SDR}
TMP=${TMP:-/tmp/opencode}
CANON_VENV="$REPO/engine/.venv"
CANON_ENV="$REPO/engine/.env"
MANIFEST="$TMP/lane_manifest.txt"

if [ "${1:-}" = "--list" ]; then
    git -C "$REPO" worktree list
    echo "--- manifest (last 20) ---"
    [ -f "$MANIFEST" ] && tail -20 "$MANIFEST"
    exit 0
fi

[ $# -eq 3 ] || { echo "usage: new_lane.sh <iterNN> <base-sha-or-branch> <slug> | --list"; exit 2; }

iter="$1"; base="$2"; slug="$3"
echo "$iter" | grep -Eq '^[0-9]+$' || { echo "REFUSE: iterNN must be numeric (got: $iter)"; exit 2; }
[ -d "$CANON_VENV" ] || { echo "REFUSE: canonical venv missing: $CANON_VENV"; exit 2; }
[ -f "$CANON_ENV" ] || { echo "REFUSE: canonical env missing: $CANON_ENV"; exit 2; }

WT="$TMP/wt-$iter"
BR="engine/$iter-$slug"
[ -e "$WT" ] && { echo "REFUSE: $WT already exists (pick the next iter or remove it)"; exit 1; }
git -C "$REPO" rev-parse --verify --quiet "$base^{commit}" || { echo "REFUSE: base not resolvable: $base"; exit 2; }

echo "== 1/5 worktree add ($WT @ $base, branch $BR)"
git -C "$REPO" worktree add "$WT" -b "$BR" "$base"

echo "== 2/5 venv symlink -> $CANON_VENV"
ln -s "$CANON_VENV" "$WT/engine/.venv"

echo "== 3/5 env generated from canonical (NOT from another worktree)"
cp "$CANON_ENV" "$WT/engine/.env"
env_md5=$(md5sum "$WT/engine/.env" | cut -d' ' -f1)

echo "== 4/5 audit gate"
fails=0
if grep -q '^WARM_AWAIT_DEST_MS=250$' "$WT/engine/.env"; then
    echo "  AUDIT FAIL: stale WARM_AWAIT_DEST_MS=250 (FIND-37; ratified 2500)"
    fails=1
fi
if ! grep -q '^CARTESIA_MODEL_ID=sonic-3.6-2026-08-27$' "$WT/engine/.env"; then
    echo "  AUDIT FAIL: CARTESIA_MODEL_ID dated pin missing (2026-09-23 lesson)"
    fails=1
fi
eager=$(sed -n 's/^DEEPGRAM_EAGER_EOT_THRESHOLD=//p' "$WT/engine/.env" | head -1)
eot=$(sed -n 's/^DEEPGRAM_EOT_THRESHOLD=//p' "$WT/engine/.env" | head -1)
if [ -n "$eager" ] && [ -n "$eot" ] && awk -v a="$eager" -v b="$eot" 'BEGIN{exit !(a>b)}'; then
    echo "  AUDIT FAIL: DEEPGRAM_EAGER_EOT_THRESHOLD($eager) > DEEPGRAM_EOT_THRESHOLD($eot) -> Deepgram 400 (probed 2026-10-03)"
    fails=1
fi

echo "== 5/5 manifest"
verdict="READY"; [ $fails -ne 0 ] && verdict="DOA"
echo "$iter|$BR|$base|env:$env_md5|$verdict|$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$MANIFEST"

if [ $fails -eq 0 ]; then
    echo "LANE $iter READY: $WT  ($BR @ $base, venv->canonical, env md5 $env_md5)"
    exit 0
else
    echo "LANE $iter DOA: audit failed — fix the env (or canonical) before boot. Manifest records DOA."
    exit 1
fi
