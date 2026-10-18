# 02 ACTION PLAN — iter95/sdk fast-test-lane (corrected per 01_audit)

Ride: **iter95/sdk** (numbering law; zero `engine/diallux/**` touches). Whitelist: `scripts/fast_suite.sh`, `engine/tests/**`, `engine/pytest.ini` (only if a change is strictly needed), evidence under `research/iter95-sdk/`, docs (`engine/ITERATIONS.md`, this dossier). NEVER `engine/diallux/**`, `retell/**`, `services/**`.

All commands run on OREGON (ssh-wrapped from Finland). Canonical venv python = `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (never `bin/pip`; always `-m pip`).

---

## T-1 (pre-step, docs law) — Land the paper trail on main

The plan + this surgeon dossier are not on main yet (F10).

1. From `wt-main-docs` (on main, clean): copy in `plans/plan_v5_iter95_sdk_fast_test_lane.md` (from the Finland mirror / the archive copy in this dossier) + `tasks/surgeon/iter95-sdk-fast-test-lane/` (all four docs).
2. `keyhound` → commit (docs straight to main, LAW 0) → push.
3. Finland: `git fetch origin && git merge --ff-only origin/main`.

## T0 — Owner gates (HITL — the only gate; fixes F9's base question)

Ask the owner, in one ask:
1. **Landing mode**: A = whitelist commits straight to main (plan's recommendation) or B = one branch `engine/iter95-sdk`, single batched merge ask.
2. **xdist dep bump**: GO or skip for T4 (pytest-xdist into the canonical venv = LANE LAW 2 owner-approved bump).
3. **Base commit**: confirm SDK base = current main tip **after** the iter94/iter95 merges are decided (merge rehearsal lane `wt-9494` exists). If merges are still pending, SDK work may proceed on the current tip with the explicit note that a rebase is NOT needed (SDK touches no engine code — zero conflict surface).
4. If mode A: owner approves a one-line AGENTS.md amendment (R4): *"Test-infra whitelist (`scripts/fast_suite.sh`, `engine/tests/**`) may commit straight to main per iter95/sdk; anything touching `engine/diallux/**` remains full LAW 0."*

Pre-flight before ANY work (R1): `ps aux | grep -E "pytest|git"` + `git worktree list` — confirm no active session/merge rehearsal is running.

## T1 — Profile the suite (evidence; fixes F4/F5)

Goal: the FIRST-ever instrumented full-suite run on this box. Decision gate included.

```bash
mkdir -p /home/julio/projects/clean_diallux_SDR/research/iter95-sdk
cd /tmp/opencode/wt-95/engine   # or the owner-confirmed base lane; touch nothing
# NOTE: NO extra -q — pytest.ini already has addopts=-q; a second -q (-qq) HIDES
# the verdict line AND the total wall time (audit F5, verified on pytest 9.1.1)
{ time .venv/bin/python -m pytest tests --durations=50 ; } \
  > /home/julio/projects/clean_diallux_SDR/research/iter95-sdk/durations.txt 2>&1
echo "exit=$?" >> /home/julio/projects/clean_diallux_SDR/research/iter95-sdk/durations.txt
```

**Decision gate (binding):**
- Verdict line must read green (496/3/0-class count + any new pins). Red → STOP, report to owner (not this lane's job to fix).
- **Total wall time ≤ ~3 min** → the plan's premise is void: the suite was never slow. STOP. Report to the owner with durations.txt; the "20–25 min" was interleaved work/re-runs (the hidden-verdict disease F5 is the likely multiplier, already cured by T2's verbosity fix). T3 is cancelled; T4 optional; go to T5.
- **Total wall time > ~3 min** → offender list = every file with ≥5s cumulative from the durations block = the T3 work list. (If the top offenders turn out to be network-timeout tests rather than sleep tests — e.g. connect timeouts — report that class to the owner before converting anything: virtual clocks do not fix network waits.)

## T2 — Build `scripts/fast_suite.sh` (fixes F5/F6/F7/F11/F13)

Full draft (bash, no deps):

```bash
#!/usr/bin/env bash
# fast_suite.sh — iter95/sdk fast test gate.
# Whitelist lane: this script + engine/tests/** only. NEVER engine/diallux/**.
#
# Usage (cwd MUST be <repo>/engine — of any worktree or the main checkout):
#   bash <repo>/scripts/fast_suite.sh <pytest node ids...>   targeted (seconds)
#   bash <repo>/scripts/fast_suite.sh --touched              changed tests + importers
#   bash <repo>/scripts/fast_suite.sh --full                 full suite (merge gate)
#
# Laws baked in (audit F5/F7/F11):
#   - NO extra -q: engine/pytest.ini addopts=-q; a 2nd -q = -qq hides the verdict.
#   - canonical venv by ABSOLUTE path (LANE LAW: one venv per box; works from
#     worktrees without a .venv symlink, e.g. wt-main-docs).
#   - empty --touched selection exits 0 (never falls through to a full run).

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
```

Build + verify (OREGON; note corrected invocation — F6):
1. Write to `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh`, `chmod +x`.
2. `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` (from anywhere) → expect usage + exit 2.
3. From `/tmp/opencode/wt-95/engine`: `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh tests/test_iter95_warm_abort.py` → expect **"6 passed … in Xs" VISIBLE** (the F5 proof) in seconds.
4. `--touched` from wt-95 (2 dirty test files) → expect it selects `tests/test_iter48_rag_truth.py` + `tests/test_iter55_observability.py` (no diallux diff on a clean committed lane... on wt-95 the diallux diff is now empty post-commit → selection = the 2 dirty files only).
5. `--touched` from a clean tree → expect "nothing to run", exit 0 (F7 proof).
6. Commit (mode A: wt-main-docs, after copying the script there; mode B: the lane branch). Every subsequent whitelist commit passes `--touched` before landing (mode A).

## T3 — Convert the MEASURED offenders to virtual clocks (fixes F2/F3/F12; gated by T1)

Per file on the T1 list (≥5s cumulative) ONLY:
1. **Pattern choice:** ladder/lifecycle/hold machinery (reads `time.perf_counter` via `asyncio.sleep`) → the committed iter94 template (`test_iter94_ladder_loop.py::_clocked`: patch `asyncio.sleep` + `time.perf_counter` onto one VClock, advance explicitly). If the code-under-test also reads `time.monotonic` (audit §6 sites) → extend the SAME patch to `time.monotonic` (both clocks on one virtual time — a mixed-clock patch is a correctness bug).
2. **Do NOT touch:** settle-yields (0.01–0.05s), zero-sleeps, and cancel-target sleeps inside fakes (3600s/30s — no wall cost; converting adds risk for zero gain).
3. **Preserve assertion strength:** same pins, same deadline values, same outcomes — only wall time drops. A conversion that weakens a pin is a regression.
4. **Per-file protocol:** BEFORE timing (`fast_suite.sh tests/<file>.py`) → convert → AFTER timing → both recorded in `research/iter95-sdk/conversions.md` → same pass/skip count before vs after, else revert.
5. One file per commit; each commit passes `fast_suite.sh --touched` first (mode A).
6. After ALL conversions: one `fast_suite.sh --full` — same totals as T1's run, only faster; record both in conversions.md.

## T4 — xdist (OPT-IN, only on owner GO at T0)

```bash
/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pip install pytest-xdist   # NEVER bin/pip
# record exact version for the ITERATIONS line, then compare on the same tree:
.venv/bin/python -m pytest tests            # serial
.venv/bin/python -m pytest tests -n 2       # parallel
```
Adopted as an OPTION iff counts identical + 0 failures both ways; else uninstall + record why. Never default (2 vCPU box).

## T5 — Docs + close

1. `engine/ITERATIONS.md` (corrected path — F1): line `iter95/sdk — fast_suite.sh + N virtual-clock conversions + suite wall time X → Y (evidence: research/iter95-sdk/)` (or the T1 decision-gate outcome if T3 was cancelled).
2. Verdict appended to the plan file; status flip.
3. Commit registry refresh ritual (AGENTS.md rule 8): backup `research/surgeon/iter47-call-ledger/ledger.db`, re-run the build from the MAIN checkout's `engine/` dir.
4. `scripts/keyhound` before push; push per picked mode; Finland `git merge --ff-only origin/main`.
5. Archive this dossier per framework (source plan already in `archive/`).

## Validation (end-to-end)

T-1 docs landed → T0 gates recorded → T1 instrumented run with binding decision gate → T2 script with visible verdicts + empty-selection guard → T3 only for measured offenders, per-file proof → T4 only if identical → T5 docs + registry + sync. **Success metric (revised by audit): the next iteration's per-change cycle is minutes AND the operator can SEE the verdict line; the once-per-branch full suite is no slower than today, with zero assertion strength lost.**
