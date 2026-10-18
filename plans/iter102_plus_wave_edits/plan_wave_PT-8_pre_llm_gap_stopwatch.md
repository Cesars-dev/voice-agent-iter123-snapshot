# Wave plan PT-8 — pre-LLM gap stopwatch (observability-only; runs FIRST inside the stack branch)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: per-round breakdown of the ~300–400 ms un-spanned window between round-start and LLM-call-start. Observability ONLY — zero behavior change. A FIX gets its own iter only if the gap proves real.
- Status: PLAN ONLY (awaits owner GO; runs as commit #1 of the wave stack branch)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: THE STACK BRANCH (`engine/<NN>-wave-stack`, number ratifies at cut, next-free 107+), cut from main `3daf11c`. This PT is its FIRST commit.

## Compaction Context
Shared wave context (all files in `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/` carry it):
- Code state analyzed: `origin/main` @ `10aebad` (engine content = `3daf11c`); every line ref below verified 2026-10-10 against that tip.
- Wave law (owner 2026-10-10): the wave runs as a CHAIN — ONE stack branch carries PT-8→PT-5→PT-6→PT-4→PT-11 as per-PT clean commits (owner run order) cut from main → PT-1 branch off the stack tip → PT-2 branch off PT-1's tip → PT-10 own branch (post-dictation) → PT-9 LAST from `engine/98-service-tier` tip. NEVER branch from main mid-chain; every link tested (suite baseline byte-identical + own pins) before the next cut; serial merge-back at the END, each merge = LAW 0 owner say-so; NO squash.
- Suite gate: measure the baseline at cut time: `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1` (post-97-merge expectation `5 failed, 517 passed, 1 skipped`; otherwise whatever main carries — gate = byte-identical red set, growing ONLY by own pins).
- LANE LAW: `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <NN> <base> <slug>` on OR; one canonical venv symlinked; `.env` generated from canonical; agents NEVER edit `.env` (SWITCH LAW). Provisional wave lane ports 102→:8071 … 106→:8075 (never-touch list unchanged).
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/`.

PT-8 specific: iter97 T1 measured dispatch p50 70 ms (EOT→graph dispatch — loop thesis dead); but turn-3-class stalls remain unexplained: B0 600 ms stall of which only 187.9 ms = rag; B250 clean-turn stalls 291–577 ms vs B0's 68–163 with no paid await (owner row PT-79 remainder / FIND evidence `research/surgeon/iter102-fix-wave/01_wave_eval.md` PT-8 row). Nothing today spans the window between state_node entry and `runtime.llm.astream` dispatch.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Observability-only; no behavior change | Owner approved as such; a fix gets its own iter only if the gap proves real |
| Extends the iter93 `rag_consume` provenance pattern on the turn report | The proven mechanism: `session.py:923-926` already surfaces `runtime._last_consume` into the final turn report |
| Runs FIRST inside the stack branch | Owner run order 2026-10-10 (PT-8 → PT-5 → PT-6 → PT-4 → PT-11) — its stamps also measure the OTHER stack commits' effects later |
| Field names + source stamps close HERE (the 01_wave_eval "spec gap" for PT-8) | This file IS the edit-spec closure for PT-8 |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO to cut the stack branch | master plan ASK |
| Suite baseline number at cut time | measured on the cut worktree (post- or pre-97-merge main — owner's standing BLOCKED on the 97 dial) |

## Environment & Dependencies
- venv (canonical, symlinked into the lane): `/home/julio/projects/clean_diallux_SDR/engine/.venv` (python 3.12; pip via `-m pip` only).
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py`.
- No new packages. No new Settings fields (observability-only; the one-trip knob set is untouched).

## Architecture (what exists today, verified)
```
session._on_eot / _on_eager_eot          (session.py:459-560 / :621-698)
  └─ clock.mark_user_end()               TurnClock t_user_end
  └─ _run_turn → graph.astream           (session.py:874-880)
       └─ ingest                         (builder.py:2804-2843)
       └─ state_node round:              (builder.py:1800+)
            t_entry   = ???              ← NOT stamped today
            await _await_warm(...)       (builder.py:1868-1898)  outcome logged, NOT on report
            _consume_live_retrieve       (builder.py:1952-1987)  rag_ms + await_ms → runtime._last_consume (:1967-1972)
            tools/head cache lookups     (builder.py:2227-2235, :2189-2197)
            _build_messages              (builder.py:2284-2285)
            t0 = perf_counter()          (builder.py:2287)
            llm.astream(...)             (builder.py:2317)       ← the gap ends at FIRST EVENT (ttft stamped :2322-2323)
       report = clock.report() + _late_turn_report   (session.py:893-931; rag_consume stamp :923-926)
```
The un-spanned window = `state_node` entry → `t0` (astream dispatch). Components in between: warm await, live-retrieve consume (embed await + pgvector + merge), tools-schema cache build, message assembly. Today only the rag half is stamped (`_last_consume`), the warm outcome only logged (`log.info` at builder.py:688).

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | state_node round: stamp `t_round_entry` (first line of the round body), record per-round pre-LLM breakdown dict into `runtime._last_round_pre_llm` right before `t0` at :2287 | EDIT (stack branch, commit #1) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | `_late_turn_report` (:904-961): next to the `rag_consume` stamp (:923-926), add `final["pre_llm_ms"] = runtime._last_round_pre_llm` (getattr-guarded, None-safe — same pattern as the rag_consume stamp) | EDIT (same commit) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_gap_stopwatch.py` | pins (below) | NEW (same commit) |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | no switch added — note-only row that the report gained `pre_llm_ms` (schema change list) | EDIT (rides the stack branch's docs commit or the merge commit) |

Exact field names (the spec-gap closure — these are THE names):
```python
runtime._last_round_pre_llm = {
    "state": <state_name>,
    "turn": <turn_index>,
    "entry_to_dispatch_ms": <t0 - t_round_entry>,      # the whole measured window
    "warm_await_ms": <waited from _await_warm, 0 if off>,
    "rag_ms": <rag_ms>,                                 # retrieval itself (already in metrics)
    "rag_await_ms": <await_ms from _last_consume>,      # bounded wait for the in-flight fire
    "other_ms": <entry_to_dispatch_ms - warm_await_ms - rag_await_ms>,   # tools/head cache, message build, residue
}
```
Implementation note: `_await_warm` already computes `waited` (builder.py:687) — surface it via the existing return path or a `runtime._last_warm_wait` scratch in the same style as `_last_consume` (pick the scratch attribute — one line, no signature churn). The rag await comes free from `_last_consume["await_ms"]`. `other_ms` is derived, never measured twice.

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Specifics here: commit #1 of the stack branch, message shape `iter<NN> PT-8: pre-LLM gap stopwatch (observability-only — per-round pre_llm_ms breakdown on the turn report)`.
- NEVER touched: every existing report key, every span, every knob, every `.env` line. The `pre_llm_ms` key is ADDITIVE on the final report only.

## Tasks (in order)
### T1 — Stamp + surface (one commit)
- Goal: the four-line stamp set above. `t_round_entry = time.perf_counter()` as the FIRST statement of the state_node round body (before the lite/entry_lite branches at builder.py:1819 so lite rounds are measured too); the breakdown dict built right before `t0` (:2287); session surfaces it at `_late_turn_report`.
- Commands: edit in the FI worktree of the stack branch; `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests/test_iter<NN>_gap_stopwatch.py -q` then the full suite gate.
- Verification (pins in `test_iter<NN>_gap_stopwatch.py`):
  1. `test_pre_llm_fields_present`: a scripted FakeLLM round → final report carries `pre_llm_ms` with all five keys; values non-negative.
  2. `test_no_existing_key_changes`: the report's key set minus `pre_llm_ms` is byte-identical to a pre-change scripted run (same harness shape as the iter98 byte-parity pin).
  3. `test_other_ms_accounts`: `entry_to_dispatch_ms == warm_await_ms + rag_await_ms + other_ms` (±1 ms float slack).
  4. `test_lite_round_stamped`: turn-1 lite round also stamps (entry stamp precedes the lite branch).
- Dependencies: stack branch cut (master plan T1).
### T2 — Gate + ASK
- Full suite byte-identical + own pins green → battery not required (observability-only; no audible change) — but the stamps must appear on at least one scripted mic/harness run's reports before the ASK. ASK text lists: suite delta, pin count, sample `pre_llm_ms` values.

## Validation Plan (end-to-end)
1. Suite red set byte-identical + 4 pins green.
2. One scripted run (harness or mic lane): every turn report carries `pre_llm_ms`; `other_ms` distribution recorded into `research/surgeon/iter102-fix-wave/02_gap_stopwatch_baseline.md` — THIS table is the deliverable that decides whether a fix iter is ever cut.
3. Zero behavior change: no prompt, no KB, no knob, no span changes; turn reports differ ONLY by the added key.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Any FIX for the gap | own iter, only if the baseline table proves the gap real (owner decision on the data) |
| Span-level (Langfuse) pre-LLM breakdown | report-first (cheaper, same SOP as rag_consume); spans only if the owner wants them on the trace |
