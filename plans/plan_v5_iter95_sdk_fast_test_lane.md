# plan_v5_iter95/sdk — TEST-LANE SDK: fast gate script + slow-test killer + optional parallel run

## Meta
- Date: 2026-10-06
- Written on: Finland box (julio @ 46.62.233.228). Lands on main via the OREGON docs
  writer (see Deploy Rules), then Finland ff-syncs.
- Project root (OREGON source of truth): `/home/julio/projects/clean_diallux_SDR`
- Finland reference checkout: `/home/julio/projects/clean_diallux_SDR` (julio @ 46.62.233.228)
- Numbering: rides **iter95/sdk** (numbering law — SDK/outer-code edits carry the last
  cut code iteration with a suffix; mints NO new iter number; touches ZERO
  `engine/diallux/`).
- Scope: make the test cycle fast so iterations stop burning 20-25 min per suite run:
  (1) `scripts/fast_suite.sh` targeted runner, (2) convert slow real-sleep tests to
  virtual clocks, (3) optional parallel pytest. Test infra ONLY.
- Status: **EXECUTED 2026-10-06 (T-1, T1, T2, T5 done; T3 CANCELLED by the T1 decision
  gate; T4 skipped by owner). Verdict at the end of this file.**

## Compaction Context

### Why this plan exists (owner, 2026-10-06)
The owner watched iter94+iter95 execution stall on full-suite runs: ~20-25 min each on
the 4GB OREGON VPS, run once before + once after EACH branch (4 runs today, ~90 min of
waiting). Owner: "cant we make a fucking SDK for the pin test... that takes a million
years to land?" and "next time we work on the same fucking branch to avoid this
hassle". Owner also proposed the landing mode: test-infra that does not touch the
engine should commit straight to main (his question — answered below).

### Session state at plan time (2026-10-06)
- iter94 (ladder silence-stretch guard): DONE, committed on branch
  `engine/iter94-ladder-stretch` @ `3ac544a` (OREGON worktree `/tmp/opencode/wt-94`),
  suite 495/3/0 green, stash-proven. UNMERGED — merge awaits owner say-so.
- iter95 (savage warm cancel-not-wait, abort cap 400ms ceiling semantics): code + 6 pins
  green in `/tmp/opencode/wt-95` (branch `engine/iter95-savage-warm-abort` @ `06bdd97`);
  final full suite still running when this plan was written. UNMERGED, UNCOMMITTED.
- Suite baseline at main tip `06bdd97` = 490 passed / 3 skipped / 0 failed (measured).
- Full-suite wall time on OREGON: ~20-25 min (measured 4x today). pytest 9.1.1,
  Python 3.12, box = Hetzner 4GB / 2 vCPU.
- Suspected slow offenders (to be CONFIRMED by profiling in T1, never guessed):
  `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter82_pause_ladder.py`
  (real sleeps ~2.3s per scenario), `test_iter84_backoff.py`,
  `test_iter46_latency_floor.py` (token_pause), iter85/iter87 hold-wait tests,
  iter48/iter55 await-timing tests.
- The virtual-clock conversion pattern ALREADY EXISTS, proven this session:
  `/tmp/opencode/wt-94/engine/tests/test_iter94_ladder_loop.py` and
  `/tmp/opencode/wt-95/engine/tests/test_iter95_warm_abort.py` — both patch
  `asyncio.sleep` + `time.perf_counter` to a test-owned virtual clock; they run
  instantly at SPEC timing values (8s nudge / 45s close).

### Landing-mode analysis (the owner's question)
LAW 0 as written: "any code -> branch". Owner proposes straight-to-main for this class.
Recommendation: **owner-granted, narrowly-scoped exception** — whitelist test-infra
paths may commit straight to main, because (a) zero prod blast radius (nothing in
`engine/diallux/` changes), (b) every future suite run validates the suite itself,
(c) the pain being fixed is ceremony, not safety. Guard: the exception covers ONLY the
File Map whitelist; any change needing `engine/diallux/` leaves this lane into a normal
engine branch. Alternative (laws-as-written): ONE branch `engine/iter95-sdk`, free
commits on it, single batched merge ASK — same work, one ceremony. T0 = owner picks
A (straight to main, recommended) or B (one branch).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Rides `iter95/sdk` — no new iter number | numbering law: SDK changes carry the last cut code iter |
| Whitelist-only lane: `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` + `/home/julio/projects/clean_diallux_SDR/engine/tests/**` + pytest config. NEVER `engine/diallux/**`, NEVER `retell/**`, NEVER `services/**` | straight-to-main is safe ONLY because prod code is out of scope |
| Virtual-clock conversions must preserve assertion strength (same pins, same deadlines, faster wall time) | a conversion that weakens a pin is a regression, not an optimization |
| Profile FIRST (T1); convert only measured offenders | no guessing; durations data decides the work list |
| xdist is OPT-IN (`-n 2`), never default | 2 vCPU box; parallel-unsafe tests would poison the gate; needs owner-approved dep bump |
| Full suite still runs ONCE at the end of every branch/session | the full suite is the merge gate (AGENTS.md); the SDK shrinks the per-change cycle, not the final gate |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| **T0: owner GO + landing mode** — A = straight to main for whitelist paths (recommended); B = one branch `engine/iter95-sdk`, single merge ask | owner says "A" or "B" |
| **T4: pytest-xdist into the canonical venv** `/home/julio/projects/clean_diallux_SDR/engine/.venv` (LANE LAW 2 dependency change = owner-approved bump) | owner GO at T0, or skip T4 |
| iter95 final suite result must be green before SDK work starts on the same box | poll `/tmp/opencode/iter95-suite2.txt` on OREGON |

## Environment & Dependencies
- OREGON access: `ssh -o ConnectTimeout=15 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'`
- Python: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (3.12; never
  `bin/pip`, always `-m pip`)
- pytest 9.1.1 (as installed; no upgrade in this plan)
- pytest-xdist: NOT installed; T4 installs ONLY on owner GO (record exact version in the
  ITERATIONS.md line)
- Profiling worktree: any existing lane, e.g. `/tmp/opencode/wt-95/engine` (read-only)
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/iter95-sdk/`
- The command being sped up: `cd /tmp/opencode/wt-95/engine && .venv/bin/python -m pytest tests -q`
- No new Python deps for T1-T3. Bash only.

## Architecture
```
fast_suite.sh  (lives at /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh)
  no args      -> usage + exit 2
  <node ids…>  -> .venv/bin/python -m pytest <node ids…> -q          (seconds)
  --touched    -> changed/untracked files under engine/tests/ (git status)
                  + every test file importing a changed diallux module
                  -> pytest <those> -q                               (~1-2 min)
  --full       -> pytest tests -q                                    (merge gate)

slow-test killer (T3): per-file virtual clocks — patch asyncio.sleep +
time.perf_counter inside the test module (pattern: engine/tests/test_iter94_ladder_loop.py
on OREGON wt-94) -> same pins, same deadlines, wall time ~ 0.

xdist (T4, opt-in): pytest -n 2 — adopted only if counts identical vs serial.
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` | the targeted runner (whitelist lane) | NEW |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter82_pause_ladder.py` | real sleeps -> virtual clock (ONLY if T1 flags it) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter84_backoff.py` | same (ONLY if T1 flags it) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter46_latency_floor.py` | token_pause -> virtual clock (ONLY if T1 flags it) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/<every file T1 flags>` | same pattern | EDIT |
| `/home/julio/projects/clean_diallux_SDR/research/iter95-sdk/durations.txt` | profiling evidence (gitignored) | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/iter95-sdk/conversions.md` | per-file before/after timings | NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/ITERATIONS.md` | `iter95/sdk` line | EDIT |
| NEVER: `/home/julio/projects/clean_diallux_SDR/engine/diallux/**` | out of scope by the law of this lane | — |

## Deploy Rules
- Mode A (owner-picked): whitelist commits go straight to main from the OREGON docs
  writer `/tmp/opencode/wt-main-docs`; every commit passes
  `scripts/fast_suite.sh --touched` BEFORE it lands; full suite once at session end;
  then Finland syncs:
  `git -C /home/julio/projects/clean_diallux_SDR fetch origin && git -C /home/julio/projects/clean_diallux_SDR merge --ff-only origin/main`
- Mode B: all work on branch `engine/iter95-sdk` (lane via
  `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh 95sdk 06bdd97 fast-test-lane`,
  branch renamed `engine/iter95-sdk` pre-commit — same rename move used for iter94/95);
  commits free on the branch; ONE merge ask batched with iter94/iter95.
- NEVER touch `engine/diallux/**` in this lane — a needed engine change = new normal
  iteration plan.
- NEVER rsync/scp repo content; sync is OREGON -> GitHub -> Finland only.
- keyhound before every push (standing rule).

## Tasks (in order)

### T0 — Owner GO (HITL — the only gate)
Goal: owner picks landing mode A (recommended) or B; GO/skip for the xdist dep bump.
Files: none (this file is the artifact).
Verification: owner GO recorded in-chat; Status flips to IN PROGRESS.

### T1 — Profile the suite (evidence, no changes)
Goal: exact offender list with measured wall times; no edits.
Commands (OREGON):
`mkdir -p /home/julio/projects/clean_diallux_SDR/research/iter95-sdk && cd /tmp/opencode/wt-95/engine && .venv/bin/python -m pytest tests -q --durations=50 > /home/julio/projects/clean_diallux_SDR/research/iter95-sdk/durations.txt 2>&1`
(~20-25 min, runs ONCE; reuse an existing lane, touch nothing)
Verification: durations.txt exists; top-10 cumulative offenders named with seconds;
T3 work list = every test file with >=5s cumulative self time.

### T2 — Build `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh`
Goal: three modes per Architecture. Bash, no deps, ~60 lines.
Spec: `--touched` = union of (a) `git status --porcelain` modified/untracked files under
`engine/tests/`, (b) test files whose text imports any `engine/diallux/` module that
`git diff --name-only HEAD` shows changed. Runs from `<lane>/engine` cwd;
`.venv/bin/python -m pytest "$@" -q`.
Commands (OREGON): write file; `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` (expect usage, exit 2);
`bash scripts/fast_suite.sh tests/test_iter95_warm_abort.py` from `/tmp/opencode/wt-95/engine` (expect 6 passed in seconds).
Verification: the three modes behave as specified on wt-95; nothing else changed.

### T3 — Convert the measured offenders to virtual clocks
Goal: for each file on the T1 list: replace real sleeps with the proven virtual-clock
pattern (patch `asyncio.sleep` + `time.perf_counter` inside the module), preserving
every assertion and deadline value. One file per commit.
Commands (per file): run BEFORE timing `bash scripts/fast_suite.sh tests/<file>.py`,
convert, run AFTER, record both to
`/home/julio/projects/clean_diallux_SDR/research/iter95-sdk/conversions.md`.
Verification: per file — same pass/skip counts before vs after; wall time drop recorded;
after ALL conversions one `fast_suite.sh --full` = same totals as the T1 run
(490/3/0-class count + any new pins), only faster.

### T4 — Parallel run (OPT-IN, only on owner GO)
Goal: `pytest -n 2` adopted as an OPTION if and only if counts are identical.
Commands: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pip install pytest-xdist`
(OWNER-APPROVED bump); then twice: `pytest tests -q` vs `pytest tests -q -n 2` on the
same tree; compare counts.
Verification: identical counts and 0 failures both ways; else NOT adopted, uninstall,
record why. Never default.

### T5 — Docs + close
Goal: ITERATIONS.md line `iter95/sdk — fast_suite.sh + N virtual-clock conversions +
suite wall time X min -> Y min (evidence: research/iter95-sdk/)`; verdict appended to
this plan; commit + push per the picked mode; Finland ff-sync.
Verification: `git -C /home/julio/projects/clean_diallux_SDR log --oneline -3` shows the
docs commit; Finland `git merge --ff-only origin/main` clean.

## Validation Plan (end-to-end)
T0 GO -> T1 profiling evidence -> T2 script (fast gate usable in the NEXT iteration) ->
T3 conversions with per-file before/after proof + one full-suite count match ->
T4 optional xdist (only if identical) -> T5 docs. Success metric: the NEXT engine
iteration's per-change cycle runs in minutes, and the once-per-branch full suite runs
in a fraction of today's 20-25 min — with zero assertion strength lost.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| pytest-cov / coverage gates | separate need; own plan |
| CI runner off-box | infra decision, owner call, later |
| Fixing the parallel-unsafe tests for default xdist | only if T4 shows demand |
| Any change under `engine/diallux/**` | forbidden in this lane by design |
| iter94/iter95 merge ceremony | separate pending ASKs from the main session |

## Verdict (appended at close, 2026-10-06 — executed through the Surgeon Framework)

- **T0:** owner GO recorded in-chat — landing mode **A**, xdist **SKIPPED**.
- **T-1:** plan + surgeon dossier + AGENTS.md LAW0 v2.3 whitelist amendment landed on main — absorbed into commit `784a424` (the concurrent iter94/95 session's landing commit; content intact, message attribution theirs).
- **T1 (instrumented, first --durations run ever on this box):** `research/iter95-sdk/durations.txt` → **496 passed, 3 skipped, 0 failed in 90.75s** (real 1m32.28s, exit 0). **DECISION GATE FIRED: premise VOID** — the suite was never slow; surgeon audit F4 confirmed (ledger 88s ≈ measured 90.75s).
- **T2:** `scripts/fast_suite.sh` landed + verified live (usage exit 2; targeted verdict visible; `--touched` selects exactly changed files; empty selection exits 0; canonical-venv path works from venv-less worktrees).
- **T3: CANCELLED** by the gate — top cumulative offender ≈6s/file (iter80 stt-liveness); nothing meets the ≥5s conversion bar except marginal.
- **T4: SKIPPED** by owner.
- **Root cause of the "20–25 min" experience:** `-qq` hiding the final verdict line (F5) → blind re-runs, plus interleaved work between runs — NOT test duration. fast_suite.sh cures the visibility part.
- Dossier: `tasks/surgeon/iter95-sdk-fast-test-lane/` (01 audit → 04 master plan, all four steps, preflighted live).
