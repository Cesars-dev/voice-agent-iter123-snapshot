# 04 MASTER PLAN — iter95/sdk fast-test-lane (AIRTIGHT; awaits owner GO)

**Status: EXECUTED per owner GO 2026-10-06. Owner gates recorded: landing mode = A (straight to main, whitelist-gated); xdist = SKIPPED by owner (T4 not run — revisit only if T1 shows a slow suite); base = wt-95 @ 63e013c + 2 dirty test files; step 5 GO given in-chat.**

**Status: SURGEON STEP 4 COMPLETE — STOPPED HERE PER OWNER INSTRUCTION. No execution (step 5) until explicit owner GO.**

- Ride `iter95/sdk` (numbering law; ZERO `engine/diallux/**` touches — that boundary is the law of this lane).
- Whitelist: `scripts/fast_suite.sh`, `engine/tests/**`, `research/iter95-sdk/` (gitignored evidence), docs (`engine/ITERATIONS.md`, this dossier, the plan). NEVER `engine/diallux/**`, `retell/**`, `services/**`.
- All work on OREGON (two-box law; Finland mirror read-only, ff-sync at the end).

## Preflight verification (step 4 — done, evidence)

The `fast_suite.sh` draft was dry-run VERBATIM from a scratch path (`/tmp/opencode/fs_draft.sh`, never in the repo) against real trees:

| Test | Context | Result |
|---|---|---|
| A usage | wt-95/engine, no args | usage + exit 2 ✅ |
| B targeted | wt-95/engine, `tests/test_iter84_backoff.py` | **"4 passed in 1.19s" — verdict line VISIBLE** ✅ |
| C --touched | wt-95/engine (2 dirty test files, empty diallux diff) | selected EXACTLY `tests/test_iter48_rag_truth.py tests/test_iter55_observability.py` → "27 passed in 8.11s" ✅ |
| D no-venv worktree | wt-main-docs/engine (NO local .venv/.env) via canonical venv path | "4 passed in 1.12s" ✅ |
| E clean tree | wt-main-docs/engine, --touched | "nothing to run", exit 0 ✅ |

Also verified: porcelain paths are root-relative from `engine/` cwd; `git diff --name-only HEAD -- engine/diallux` on wt-95 is empty post-commit; the 2 dirty wt-95 test files PASS on top of 63e013c (the "suite 496/3/0" state = committed tip + those 2 files — F9).

## OPEN ITEMS — owner gates ONLY (T0; everything else is resolved)

1. **Landing mode:** A = whitelist straight to main (recommended; requires the one-line AGENTS.md amendment) or B = one branch `engine/iter95-sdk` + single batched merge ask.
2. **xdist dep bump:** GO or skip (T4).
3. **Base commit:** main tip at execution time (merge rehearsal lane `wt-9494` exists — confirm the 94/95 merge decision first; SDK has zero conflict surface either way).
4. Confirm the iter95 loose ends are someone else's task: wt-95's 2 dirty test files (+3/+3,-1) should be committed to `engine/iter95-savage-warm-abort` by the iter95 session, not by this lane.

## EXECUTION SEQUENCE (step 5 — only after GO; compile/verify check after each step)

### T-1 — Land the paper trail (docs law)
Copy the plan + this dossier into `wt-main-docs` → keyhound → commit to main → push → Finland `git merge --ff-only origin/main`.

### T0 — Record gates; pre-flight
`ps aux | grep -E "pytest|git"` + `git worktree list` — no concurrent session/merge work. Record mode A/B, xdist GO/skip, base.

### T1 — FIRST instrumented full suite run (binding decision gate)
```bash
mkdir -p /home/julio/projects/clean_diallux_SDR/research/iter95-sdk
cd /tmp/opencode/wt-95/engine    # or owner-confirmed base lane; touch nothing
{ time .venv/bin/python -m pytest tests --durations=50 ; } \
  > /home/julio/projects/clean_diallux_SDR/research/iter95-sdk/durations.txt 2>&1
echo "exit=$?" >> /home/julio/projects/clean_diallux_SDR/research/iter95-sdk/durations.txt
```
**NO extra `-q`** (ini `addopts=-q` already applies; a second `-q` = -qq hides the verdict AND the wall time — verified). GATES:
- Red suite → STOP, report (not this lane's job).
- **Wall ≤ ~3 min → premise void** (ledger says 88s at this engine code; sleep budget ≈30–45s): T3 CANCELLED, report to owner with durations.txt, proceed to T5. The F5 verdict-line cure (T2) already removes the likely pain multiplier (blind re-runs).
- Wall > ~3 min → T3 work list = files with ≥5s cumulative. If top offenders are network-timeout tests, not sleep tests → report before converting (virtual clocks don't fix network).

### T2 — Ship `scripts/fast_suite.sh`
The verified draft (02_action_plan §T2, byte-identical to the preflighted `/tmp/opencode/fs_draft.sh`) → `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh`, `chmod +x`. Verify tests A–E from the preflight table against the installed script. Commit (mode A: via wt-main-docs; mode B: lane branch). Every later whitelist commit passes `--touched` before landing (mode A).

### T3 — Virtual-clock conversions (ONLY files T1 flagged ≥5s)
- Template: the COMMITTED iter94 `_clocked` pattern (`engine/tests/test_iter94_ladder_loop.py`). If the code-under-test reads `time.monotonic` (sites: rag.py:231/243/367, session.py:741, tracer.py:202/223, prewarm.py:90/114/152), extend the SAME patch to it — one virtual time for all clocks.
- Do NOT touch: settle-yields (≤0.05s), cancel-target sleeps (3600s/30s inside fakes), zero-sleep files.
- Preserve every pin/deadline/outcome. Per file: BEFORE timing → convert → AFTER timing → both into `research/iter95-sdk/conversions.md`; same pass/skip counts or revert. One file per commit.
- After all: one `--full` = same totals as T1, faster; record.

### T4 — xdist (only on GO)
`engine/.venv/bin/python -m pip install pytest-xdist` (never `bin/pip`); record version; serial vs `-n 2` counts identical → adopt as OPTION; else uninstall + record. Never default.

### T5 — Close
`engine/ITERATIONS.md` line (path corrected from the plan's `plans/ITERATIONS.md`) · verdict appended to the plan · commit-registry refresh ritual (backup ledger.db first, run from MAIN checkout `engine/`) · keyhound → push per mode · Finland ff-sync · archive this dossier (source plan already in `archive/`).

## Mode B mechanics (if owner picks B)
`bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh 9595 <base> sdk` (numeric-only gate — "95sdk" is refused; 9494-doubling precedent) → `git branch -m engine/9595-sdk engine/iter95-sdk` pre-commit → commits free on the branch → ONE merge ask batched with iter94/iter95.

## Residual risks (accepted, on record)
- Transient ENOENT anomalies on OREGON (3 hits during audit, all retried OK; box healthy) — long runs pre-verify paths.
- `--touched` import mapping is heuristic (untracked new diallux modules invisible; renames take the new path); mitigated by `--full` fallbacks and the once-per-branch full-suite merge gate.
- Concurrency: coordinate if lane 9494's merge work resumes mid-lane.

## Non-goals (unchanged from the plan)
pytest-cov/coverage gates · off-box CI · fixing parallel-unsafe tests for default xdist · ANY `engine/diallux/**` change (forbidden — new iteration plan if needed) · the iter94/iter95 merge ceremony itself.

## EXECUTION RESULTS (step 5, 2026-10-06)
- T0: mode A / xdist SKIP / GO — recorded above.
- T-1: landed (absorbed into 784a424 by the concurrent iter94/95 session).
- T1: **496/3/0 in 90.75s** (research/iter95-sdk/durations.txt) — DECISION GATE: <=3 min -> **T3 CANCELLED, premise void**.
- T2: script landed at scripts/fast_suite.sh + verified (usage exit 2; targeted "4 passed in 1.21s"; --touched correct; empty exit 0).
- T3: CANCELLED. T4: SKIPPED by owner. T5: ITERATIONS.md line + plan verdict + ff-sync done. Commit registry refresh NOT owed by this lane: this session authored zero commits (all content landed inside the concurrent session's 784a424).
- Outcome: per-change cycle target achieved via fast_suite.sh + restored verdict visibility; suite was already fast (90.75s).
