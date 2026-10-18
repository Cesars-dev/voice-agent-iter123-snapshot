# 01 AUDIT — iter95/sdk fast-test-lane

- **Procedure:** `tasks/surgeon/iter95-sdk-fast-test-lane/`
- **Subject plan:** `plans/plan_v5_iter95_sdk_fast_test_lane.md` (written 2026-10-06, Finland; **NOT yet on main** — untracked on the Finland mirror)
- **Audited:** 2026-10-06 ~07:10–07:30 UTC, from Finland (`MainVps`), all repo reads ssh-wrapped to OREGON (`root@5.78.83.174`, `ubuntu-4gb-hil-1`) per the two-box law.
- **Method:** every plan claim traced to real files/commands; read-only spot-runs of pytest in `wt-95` for verification (no source files modified; only gitignored `.pytest_cache` + scratch files `/tmp/opencode/audit95_{quick,82,46}.txt`).

---

## 1. Environment & tooling (verified)

| Plan claim | Verified reality |
|---|---|
| Python 3.12 | ✅ 3.12.14 (canonical venv) |
| pytest 9.1.1, no upgrade | ✅ `pytest 9.1.1`; the ONLY pytest-family package (no pytest-asyncio, no pytest-cov) |
| pytest-xdist NOT installed | ✅ absent from pip list |
| Canonical venv `/home/julio/projects/clean_diallux_SDR/engine/.venv`, lanes symlink it | ✅ `wt-95/engine/.venv -> …/engine/.venv` (lrwxrwxrwx, Oct 6 06:01) |
| `engine/pytest.ini` | ✅ `testpaths = tests` + `addopts = -q` (see F5 — this matters) |
| conftest hermeticity | ✅ `engine/tests/conftest.py` autouse fixture sets `Settings.model_config.env_file=None` + `get_settings.cache_clear()` |
| Evidence dir `research/iter95-sdk/` (gitignored) | ✅ does not exist yet; `research/` IS gitignored (`git check-ignore` ✅) |
| `scripts/fast_suite.sh` is NEW | ✅ does not exist; `scripts/` = new_lane.sh, git-tree.sh, keyhound, call_ledger.py, etc. |
| Box health | 3.7Gi RAM (951Mi used), swap 1.1Gi used, load 0.00, `/` 16% used, `/tmp` tmpfs 52% — healthy |
| Test count | 499 `def test_` across `engine/tests` (incl. `tests/llm2llm/test_harness_units.py`); suite state ≈ 496/3/0 on wt-95 |

## 2. Repo / session state (verified — MOVED since the plan was written)

| Plan claim (at write time) | Verified reality (audit time) |
|---|---|
| iter94 branch @ 3ac544a, unmerged, wt-94 | ✅ unchanged (`engine/iter94-ladder-stretch` @ 3ac544a, "suite 495/3/0") |
| iter95 UNCOMMITTED in wt-95 @ 06bdd97 | ⚠️ **STALE**: iter95 is now COMMITTED — `engine/iter95-savage-warm-abort` @ **63e013c** ("suite 496/3/0"), containing config.py + builder.py + test_iter95_warm_abort.py |
| iter95 final suite pending (`iter95-suite2.txt`) | ⚠️ suite2 ran 06:51; no verdict line visible (see F5) but commit message records **496/3/0**. NOTE: wt-95 still has **2 dirty test files** (`test_iter48_rag_truth.py` +3, `test_iter55_observability.py` +3/-1) NOT in 63e013c — the committed tip alone may not reproduce the green suite (F9) |
| main tip 06bdd97 = suite baseline 490/3/0 | ✅ `wt-main-docs` on main @ 06bdd97; ledger records "490 passed, 3 skipped, 0 failed in 88s" for this engine state (2026-10-05) — see §3 |
| (not in plan) | ⚠️ **Concurrent activity**: lane `9494` (`engine/9494-test-merge` @ 06bdd97) created 07:19:51 TODAY with 2 TEST-ONLY commits merging iter94 then iter95 (3e5210c, 9eb341c) — someone is rehearsing the 94+95 merge. No pytest running at audit time. (R1) |
| OREGON main checkout | on old branch `engine/iter73-oregon-wip-20260924` @ df23d37, dirty with untracked old plans — the docs writer is `wt-main-docs` (clean, on main) |

## 3. THE CORE QUESTION: is the suite really 20–25 minutes?

The plan's whole premise. Evidence gathered:

1. **Ledger (engine/ITERATIONS.md, 2026-10-05):** "Suite on merged main: 490 passed, 3 skipped, 0 failed **in 88s**" — at the SAME engine code as today's main tip (06bdd97 contains only plan/docs commits since 6d9f277).
2. **Sleep census (all 56 test files, wt-95):** 19 files contain real sleeps. Sleep-value histogram: 14×0.01s, 12×0.05s, 5×0s, 4×0.25s, 3×1.6s, 2×5s, 1×5.0s, 1×1.4s, 1×1.2s, 1×0.6s, 1×0.4s, 1×0.3s, + the measured 2.3s/2.23s spikes. The BIG sleeps (6×3600s, 4×30s) are **cancel targets inside fakes** ("never returns (cancel target)" — e.g. `test_iter38:109`, `test_iter59:255`) — zero wall cost. **Total real-sleep budget ≈ 30–45s.**
3. **Spot-runs on wt-95 (audit, measured):** `test_iter95_warm_abort.py` → 6 passed, ~2s. `test_iter82_pause_ladder.py` → 5 passed in ~3s (slowest test 2.30s). `test_iter46_latency_floor.py` → 15 passed in ~5s (slowest 2.23s). `test_iter84_backoff.py` → 4 passed in **1.15s**.
4. **Suite logs:** `iter94-baseline.txt` (04:53), `iter94-suite.txt` (05:16), `iter95-suite.txt` (06:19, had ≥4 failures), `iter95-suite2.txt` (06:51). None contains a final "N passed" line (see F5) and none has `--durations`. The ~20–30 min mtime gaps are consistent with 20–25 min/run, but also with runs interleaved with coding.
5. **The engine's only real `time.sleep`** (`observability/tracer.py:230`, tail-confirm poll loop) is **not referenced by any test** — ruled out as a hidden cost.

**Conclusion:** the test CONTENT cannot cost 20–25 min. Either (a) the 88s ledger figure is right and today's wall-time perception came from interleaved work/re-runs, (b) something environmental stalled today's runs (e.g. network-timeout tests on a degraded egress path — precedent: the iter44 dead-store REAL-Deepgram-connect lesson), or (c) concurrent load. **Unresolvable from logs; T1 (--durations) is the decider — and the plan's ROI hinges on it.** The audit turns this into a hard decision gate (see 02, T1).

## 4. The verdict-line disease (NEW finding, F5)

`engine/pytest.ini` sets `addopts = -q`. The canonical command `pytest tests -q` therefore runs at **-qq**, and pytest 9.1.1 at -qq **suppresses the final "N passed … in Xs" line**. Verified live: every suite log on the box ends at the warnings "-- Docs:" footer; audit runs with explicit `-q` ended at `[100%]` with no verdict; the same run WITHOUT the extra `-q` printed `4 passed in 1.15s`. Consequences: (1) operators literally cannot see if a run passed — probable multiplier of today's re-run pain; (2) the plan's own T1 command (`-q --durations=50`) would hide its own measurement; (3) `fast_suite.sh` as specced (`pytest "$@" -q`) inherits the disease.

## 5. Proven fast-test patterns that ALREADY exist (pattern catalog)

| Pattern | File | Mechanism | Status |
|---|---|---|---|
| **Virtual clock (module-level)** | `wt-94/engine/tests/test_iter94_ladder_loop.py` (`_clocked`, ~lines 120-140) | saves `asyncio.sleep`/`time.perf_counter`, replaces both with a test-owned `VClock.now`; test advances `clock.now += 8.0` explicitly; runs SPEC deadlines (8s/45s) instantly | ✅ COMMITTED (3ac544a), suite-green — **the template** |
| **Fake clock-state + per-test monkeypatch** | `engine/tests/test_iter84_backoff.py` (FakeClock :41, `sess._clock` injection, `monkeypatch.setattr(asyncio, "sleep", fake_sleep)` per test) | engine's `_clock` state object faked; sleep fast-forwards a window counter | ✅ already on main — **iter84 is NOT a slow offender (F2)** |
| **Small-real-sleep + generous bounds** | `wt-95/engine/tests/test_iter95_warm_abort.py` | real 0.01–0.05s sleeps, asserts `waited_ms < 300` etc. | ✅ committed in 63e013c — **NOT virtual-clock, plan mischaracterizes it (F3)** |

## 6. Clock usage inside `engine/diallux` (T3 patch-surface map)

Engine reads **two** wall clocks:
- `time.perf_counter` — session.py (ladder windows :381/:405, call guard :911, backoff :709/:961, barge-in :699), latency.py marks, rag.py timings, prewarm.py timings. → covered by the iter94 template.
- `time.monotonic` — rag.py:231/243/367 (failure backoff), session.py:741 (caller-silence stretch), tracer.py:202/223 (tail deadline), prewarm.py:90/114/152 (spawn ts). → **NOT patched by the iter94 template**; each converted file must be checked, and if the code-under-test reads monotonic, the patch must extend to it (keeping both clocks on the SAME virtual time).
- `asyncio.sleep` — 15 call sites in engine (module-attribute access → patchable). `time.sleep` — 1 site (tracer, untested).

## 7. Tooling interfaces

- **`new_lane.sh <iterNN> <base> <slug>`**: iterNN must match `^[0-9]+$` (REFUSES "95sdk" — F8). House workaround precedent: lane **9494** (numeric doubling), branch renamed after cut. It creates `/tmp/opencode/wt-<NN>`, branch `engine/<NN>-<slug>`, symlinks canonical venv, generates .env from canonical + audit gate, logs to `/tmp/opencode/lane_manifest.txt`.
- **`wt-main-docs`** (Mode A's work location): on main @ 06bdd97, clean — but has **NO `engine/.venv` and NO `.env`** (F11). Canonical-venv-by-absolute-path in fast_suite.sh solves it without mutating the worktree.
- **Surgeon dossiers** live committed on main under `tasks/surgeon/` (iter87-prewarm-hold etc.) — this folder follows that convention.
- **Ledger of record:** `engine/ITERATIONS.md` (NOT `plans/ITERATIONS.md` — F1). Commit registry: `research/surgeon/iter47-call-ledger/ledger.db`, refresh ritual per AGENTS.md rule 8.

## 8. FLAWS FOUND IN THE PLAN (each with evidence)

| # | Flaw | Evidence |
|---|---|---|
| **F1** | File Map targets `plans/ITERATIONS.md`; the ledger is `engine/ITERATIONS.md` | `wt-main-docs/plans/` has no ITERATIONS.md; `engine/ITERATIONS.md` exists and is the ledger used by every past iteration |
| **F2** | Suspect list stale: `test_iter84_backoff.py` already virtual (1.15s whole-file); `test_iter48_rag_truth.py` has ZERO real sleeps (not in census); measured suspects are seconds-fast (iter82 ≈3s, iter46 ≈5s) | §3, §5 spot-runs |
| **F3** | Plan claims `test_iter95_warm_abort.py` uses the virtual-clock pattern — it uses small REAL sleeps | §5; file read in full |
| **F4** | Core premise unproven and likely wrong: ledger says 88s at the same engine code; sleep budget ≈30–45s; suspects are fast. "20–25 min" has no durations evidence anywhere | §3 |
| **F5** | `-q` stacking (ini + CLI) = -qq hides the verdict line; plan's T1 command and fast_suite spec both inherit it | §4; verified live both ways |
| **F6** | T2 verification command broken as written: from `<lane>/engine`, `bash scripts/fast_suite.sh …` does not resolve (script lives at repo-root `scripts/`); and lanes won't contain the script until it's committed to main | path arithmetic; worktree layout |
| **F7** | `--touched` with empty selection must not fall through to bare `pytest` (testpaths would run the FULL suite) | pytest.ini `testpaths = tests` |
| **F8** | Mode B impossible as written: `new_lane.sh 95sdk …` refuses non-numeric iter names | new_lane.sh `grep -Eq '^[0-9]+$'`; 9494 precedent |
| **F9** | iter95 state moved: committed @ 63e013c ("496/3/0") but 2 test files still dirty in wt-95 (+3/+3,-1 lines) — committed tip may not reproduce green; plus merge-rehearsal lane wt-9494 exists → SDK base commit must be re-confirmed at T0 | §2 |
| **F10** | The plan file itself is not on main yet (untracked on Finland) — paper-trail law wants it landed before/with execution | Finland `git status`: `?? plans/plan_v5_iter95_sdk_fast_test_lane.md` |
| **F11** | Mode A work location (wt-main-docs) cannot run pytest (no venv, no .env) | `ls` audit |
| **F12** | Virtual-clock patch surface must be per-file: engine reads monotonic in paths the iter94 template does not patch | §6 |
| **F13** | `--touched` import mapping is heuristic; `diallux/config.py` is imported by ~every test via Settings → mapping explosion; needs defined behavior (fall back to --full) | conftest imports `diallux.config` |
| **F14** | (Minor) Transient ENOENT anomalies observed on OREGON during audit: `git -C` on the main checkout failed twice, `wt-95/engine/diallux` grep failed once — all succeeded on retry; box healthy otherwise. On record; long runs should pre-verify paths | audit log |

## 9. RISKS

- **R1 — concurrency:** another session created lane 9494 (merge rehearsal) minutes before this audit. Executing SDK work must first confirm no active merge/session work (and T0 must confirm the base: post-merge tip if 94+95 land first).
- **R2 — xdist on 2 vCPU:** limited gain; suite has self-looping event-loop tests (safe across processes) but count-identity must be proven; opt-in only (plan already gates).
- **R3 — T3 ROI:** ~19 files have real sleeps but only ≈30–45s total budget; conversions are only worth it for files T1 proves ≥5s cumulative (else: leave 0.01–0.05s settle-sleeps and cancel-target sleeps alone — converting them adds risk for zero gain).
- **R4 — Mode A is a law change:** straight-to-main for test-infra needs a one-line AGENTS.md amendment when the owner picks it, else it's an undocumented exception.

## 10. EXISTS vs MISSING

**EXISTS:** canonical venv + pytest 9.1.1 (no xdist) · hermetic conftest · two proven fast-test patterns (iter94 template committed; iter84 style on main) · new_lane.sh + lane manifest · gitignored research/ · surgeon dossier convention · suite green states recorded (iter94 495/3/0; iter95 496/3/0 per commit msg) · merge rehearsal lane wt-9494.

**MISSING:** `scripts/fast_suite.sh` (to build, T2) · `research/iter95-sdk/` evidence (T1) · any durations measurement of a full-suite run — **nobody has ever run the suite with --durations on this box** (no log contains one) · the plan on main (F10) · venv/.env in wt-main-docs (F11) · a single complete suite log with a visible verdict line (F5).
