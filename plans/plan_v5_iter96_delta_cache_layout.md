# iter96 — delta-cache layout: stop re-shipping the static state block every round (TTFT 962 → ~750 on telephony)

## Meta
- Date: 2026-10-06
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE variable — the per-round post-history delta on the voice path carries a byte-identical-per-state ~3.3–4.5k-char block (`state_block + directive + RAG`, `builder.py` scope `delta_tokens = len(rag_delta)`, CHARS not tokens) that OpenAI can never prefix-cache because it is re-sent as fresh trailing bytes every round. Move the static-per-stage part of that block INTO the cacheable prefix; ship only the true per-round change in the delta. Target: phone-path TTFT p50 962 → ~750 ms, e2e_turn p50 1,882 → ~1,500.
- Status: PLAN ONLY (not started — branch cut, code work awaits owner go)

## Compaction Context
(verbatim session compact, 2026-10-06)

- Project: Diallux SDR v5 voice pipeline (LangGraph, repo at `/home/julio/projects/clean_diallux_SDR` on FINLAND = this box); OREGON (5.78.83.174) = lane/battery/validation box, reached via git push/pull through GitHub, NEVER rsync.
- Session chain: iter93/94/95 merged to main (496 passed / 3 skipped / 0 failed), live-validated on real Twilio call trace `152d98c0c8d73f27680d950f2914e1bb` (Langfuse FI, project pk-lf-bba5…). Owner's hard goal: **e2e_turn p50 ≤ 1,200 ms on real telephony** (today 1,882).
- Measured today: TTFT p50 962 / p90 1,252 ms; per-gen in_tok 1,662→10,714; output p50 ~44–49 tok (innocent); history = flat 6-msg sliding window (innocent).
- **Langfuse autopsy done this session (HITL-owned finding, owner call-log memory 650ms p50 era confirmed):** iter78-era llm2llm chat runs today STILL hit TTFT p50 ~690–740 ms (27 runs Sep-24..Oct-2, median-of-p50 714–753). Phone path is +~250 ms over chat on the SAME engine+model (gpt-5.4, ` Observation model=gpt-5.4` both paths). Cause convicted: **per-round delta**. Phone delta_chars p50 3,422 (~855 tok) vs chat 1,261 (~315 tok). The Closer delta is byte-identical 4,501 chars across ≥4 consecutive rounds (`4,501/4,501/4,501/4,501` in trace metadata; `delta_tokens` is `len(rag_delta)` = CHARS, see `engine/diallux/graph/builder.py` log lines "round usage … delta_tokens="). Nothing new arrives turn-to-turn; the same trailing system message is re-shipped as uncached bytes every round ⇒ OpenAI re-prefills ~1k tok per round.
- Code locus (read, not yet edited): `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` — delta composition at ~line 2240–2285: `rag_delta = live_delta` (live rounds) where `live_delta` = `state_delta_block + RAG/pinned + directive`; `_build_messages(...)` appends delta AFTER history as trailing system msg; layout comment block "iter56 (C2.2): state FIRST, RAG after…". `settings.state_in_delta` gates the whole delta mechanism (iter56 C2.2/C3b layout: `[tools][head][history][delta]`, tail riding pre-history under revert flag).
- Chat path delta is small because dvs/state block is tiny there; voice path fatter due to bigger dvs + live RAG. Both confirmed by Langfuse metadata (delta_tokens chars, state_in_delta=True 37/37 gens).
- Decisions taken (owner in-chat 2026-10-06):
  1. Do POINT 1 = delta-cache layout reorder (the convicted lever). Mini-model point 2 = separate owner decision later. Dup-user-turn point 3 = demoted to polish (NOT latency-relevant: history window flat 6 msgs).
  2. Workflow: work FINLAND, deploy OREGON via GitHub (push-pull, no rsync), lanes on OREGON for real-latency tests (Twilio number +1 888 595 8927 → voicetest lane via Caddy block).
  3. Owner EOT knob values still deferred (his call); ElevenLabs V4-turbo TTFB lane test = optional add-on, not this branch; TTFT-archaeology HITL task = COMPLETED this session (verdict above).
- Iteration numbering: this plan = FULL LAW 0 code branch `engine/iter96-delta-cache-layout` ALREADY CUT from main @ 8078ad0.
- Voice law: test battery voices = Sarah; prod untouched. MODEL LAW: gpt-5.4 everywhere — this branch does NOT change model, only message layout.
- Two ledgers + ENV-SWITCHES + SWITCH LAW apply: any switch added must have code default = tested value, registered in `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md`.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| One variable on this iter: delta layout only | Owner verdict 2026-10-06 "lets do 1" — no scope creep into mini-model, dup-ingest guard, EOT knobs, TTS model |
| Work on branch `engine/iter96-delta-cache-layout` (already cut from main 8078ad0) | LAW 0: prompt-layer/pipeline code = full ceremony |
| Suite command: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q` | suite expectation ≥ 496 passed |
| Validation latency numbers come from OREGON lanes (real Twilio), not Finland mic tests | Real telephony is where the 1,882 lives; Finland = authoring + unit suite |
| `delta_tokens` metadata KEEPS its current meaning (chars of rag_delta) | Changing the meaning breaks iter56+ report continuity; instead ADD `delta_static_chars` + `delta_trailing_chars` keys beside it |
| No changes to `_history_window` size or trim | Window measured flat; touching it = second variable |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| OREGON lane bootstrap for live A/B (after suite green) | `scripts/new_lane.sh` runs ON OREGON — wait for suite green, then ask owner to fire the lane (or owner-deployed prior session pattern: OREGON `/tmp/opencode/lane-8049.log` lanes were cut with `scripts/new_lane.sh iterNN base-sha slug`) |
| Owner go for merge | LAW 0 — agent NEVER merges without explicit owner say-so |

## Environment & Dependencies
- Python venv (Finland): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (venv law: symlinked, never pip-installed into).
- Langfuse FI (read-only evidence source): `http://localhost:3001`, keys in `/home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5/.env`; helper `scripts/lf.py` run from `/home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5`.
- Reference traces: phone `152d98c0c8d73f27680d950f2914e1bb` (bad: delta 3,422 p50 chars), chat `e3bea8da71d7017366d38bd81dcdaa12` (good: 1,261 p50 chars).
- OREGON: 5.78.83.174, ssh key `~/.ssh/id_ed25519_hetznor`; GitHub = the only transport for repo content.
- Ports NOT to touch anywhere: 8001-8003 (live ORIGINAL), OREGON 8026/8090/8080/8001-8003, lane ports assigned by `scripts/new_lane.sh`.

## Architecture (one block diagram)

```
NOW (iter56 layout, per round):
  messages = [system head/static][history 6-msg][DELTA: state_block+RAG+directive]  ← trailing, fresh bytes every round → uncached ~1k tok/round

GOAL (iter96):
  messages = [system head/static][STATE-STAGE BLOCK (per-stage anchors: static dvs frame + directive + RAG stage frame — changes only at state TRANSITIONS = once per state)][history 6-msg][DELTA: live dvs values + only-what-changed RAG + per-round directive]  ← static-in-Δ promoted into prefix ONCE per state; per-round trailing bytes shrink to the true diff (~300 tok)
```
Cache timeline per state: [tools][head][stage-block] prefix STABLE across rounds of the same state; only history tail + short live-delta shift. State transitions correctly bust the prefix (unavoidable, rare).

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | delta composition: split `live_delta` into STABLE-PER-STAGE part (promoted into the prefix as its own system msg, byte-stable across rounds while the state lasts + keyed by state) vs TRUE-LIVE part (values changed since last landed round + last-round directive) staying as trailing delta. Keep `state_in_delta` revert path intact (flag-gated NEW switch below) | EDIT (~60–120 lines in the 2100–2300 delta-composition scope + a small `_stage_block()` helper) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | NEW Settings field `delta_stage_static: bool = True` (code default = the tested design per SWITCH LAW 4) + harmony fields if needed (`delta_stage_max_chars` guard) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/tracer.py` | carry-through: add `delta_static_chars`, `delta_trailing_chars` to `extra_meta` chain beside existing `delta_tokens` (no meaning change) | EDIT (few lines in `finish_llm` call) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter96_delta_stage_static.py` | NEW tests: (a) round-2 of same state reuses byte-identical stage block as round-1 (stable prefix assert), (b) dvs value change lands ONLY in trailing live delta, (c) state transition replaces stage block (old stage not orphaned adjacent), (d) `delta_stage_static=False` reproduces iter56 layout byte-exact, (e) tools array unchanged across all rounds (FIND-5 cache floor preserved) | NEW |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | register `DELTAX`… switch name `STATE_DELTA_STAGE_STATIC` + semantics + resolved value | EDIT (docs row) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter96_delta_cache_layout.md` | this plan (docs → main) | NEW/commit |

## Deploy Rules
- Finland authoring + unit suite ONLY in this plan's task list; OREGON deployment = git push origin → owner/lane-bootstrap on OREGON via `scripts/new_lane.sh iter96 <main-sha> delta-cache` — lane env from canonical OREGON `/home/julio/projects/clean_diallux_SDR` (OREGON copy) `.env`, never hand-copied.
- NEVER: touch OREGON main checkout, ports 8001-8003 or 8026/8090/8080, live agent IDs, prod voice Hannah config.
- NEVER: rsync/scp; only git push/pull (LAW).
- Test bookings on Cal.com event 3801235 are REAL — cancel after any battery that books.

## Tasks (in order)
### T1 — Pin the byte-stability target in tests BEFORE code (red first)
Goal: freeze the intended layout as failing tests.
Files: `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter96_delta_stage_static.py`
Commands (full):
```
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests/test_iter96_delta_stage_static.py -q   # expect FAIL (module missing)
```
Dependencies: none new (pure stdlib + engine tests harness patterns per existing `engine/tests/`).
Verification: the 5 tests print FAIL with clear assertion text, not collection errors.

### T2 — Implement the stage-static split in `builder.py`
Goal: per-state stage block (static dvs frame + directive + stage RAG frame) rendered ONCE per state entry and placed EARLY (after head, BEFORE history → grows cacheable prefix); trailing live delta carries only changed dvs values + fresh RAG arrivals + round directive.
Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/tracer.py`
Commands (full):
```
cd /home/julio/projects/clean_diallux_SDR && git status -sb   # confirm branch engine/iter96-delta-cache-layout
```
(In-editor edits; nothing else shelled.)
Dependencies: none beyond existing stdlib/pydantic Settings.
Verification: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests/test_iter96_delta_stage_static.py -q` → 5/5 green.

### T3 — Full suite + regressions
Goal: no layout breakage anywhere else (tool-schema stability, iter48b FIND-5, iter56 revert path, sanitizer, prewarm).
Files: none new.
Commands (full):
```
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q
```
Dependencies: suite expectation ≥ 496 passed (from ITERATIONS.md current).
Verification: 0 failed; any skip count matches latest ledger.

### T4 — Report + registry ritual
Goal: evidence filed, askable state.
Files: report folder `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-delta-cache-layout/96_report.md`; chain `plans/NEXT_STEPS.md` + `plans/PENDING_TASKS.md` only if a new PT is opened.
Commands (full):
```
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q   # capture final line into report
git -C /home/julio/projects/clean_diallux_SDR add engine/tests/test_iter96_delta_stage_static.py engine/diallux/graph/builder.py engine/diallux/config.py engine/diallux/observability/tracer.py && git -C /home/julio/projects/clean_diallux_SDR commit -m "iter96: stage-static delta split — static per-stage block promoted to cacheable prefix, trailing delta = true diff"   # commits stay on BRANCH, never main
```
Dependencies: ENV-SWITCHES row already added (T2 edit).
Verification: report exists w/ before/after delta-chars table + suite line; branch has commit; NO push to main, NO merge (LAW 0 — owner merges).

### T5 (owner-gated, after merge) — OREGON lane A/B + Twilio audit
Goal: real-telephony proof.
Files: lane on OREGON via `scripts/new_lane.sh`; evidence: new Langfuse trace vs baseline `152d98c0…`.
Commands (full, ON OREGON after owner say-so): `scripts/new_lane.sh iter96 <main-sha> delta-cache` then lane boot-env `AUDIO_TRANSPORT=twilio PUBLIC_BASE_URL=wss://voicetest.diallux-ai.site`; one owner call; `scripts/lf.py show <new-trace-id>` (FI Langfuse).
Dependencies: merged main + owner.
Verification: NEW trace phone delta_chars p50 ≤ ~1,500 (from 3,422), TTFT p50 ≤ ~800 ms (from 962), suite-equal behavior (no gate_rejections delta), and the switch resolves to the tested value (SWITCH LAW snapshot + diff vs prod in evidence).

## Validation Plan (end-to-end)
1. T1 red → T2 green on new tests (byte-stability + revert-exactness proven).
2. Full suite ≥ 496 pass.
3. After merge: OREGON lane battery/lane A/B (T5) shows delta_chars p50 ~3,422 → ≤1,500 and TTFT p50 962 → ≤800 on real Twilio; e2e_turn read from lane logs.
4. SWITCH LAW: resolved-switch snapshot filed next to evidence; zero behavioral deltas besides latency.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Mini-model for mechanical states (TTFT floor ~950 gpt-5.4 → ~350 mini) | MODEL LAW = owner say-so; separate iter if ratified |
| Dup-user-turn ingest guard (Deepgram cumulative Update slices land as separate user msgs) | demoted: window is flat 6-msg; quality polish not latency |
| Deepgram EOT knob values | owner-set, pending his value pick; zero-code A/B lane ready |
| ElevenLabs turbo_v4 TTFB lane test | optional add-on post-iter96; VOICE LAW gate |
| Prefill-able handoff warm re-fires | existing iter93 mechanism — untouched |

## Compaction note
Written per SOP from live session 2026-10-06; branch already cut: `engine/iter96-delta-cache-layout` (from main@8078ad0). Doc commits (this plan) go to main per rule 0; code commits stay on the branch.