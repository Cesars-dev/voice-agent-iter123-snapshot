# Wave plan PT-9 — SPEAK-FIRST split-round (the big latency lever; LAST in the wave, from the 98 tip)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: spoken text lands FIRST every round — two concurrent requests on the warmed shared pool: a SPEAK stream (messages + `LITE_NOOP_TOOL` ALONE) ∥ a TOOLS stream (full tool array, executes exactly as today at the gather). Engine-enforced (the prompt route measurably failed — "no roulette").
- Status: PLAN ONLY (awaits owner GO; builds LAST per owner 2026-10-10)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: `engine/100-split-round`, cut from the `engine/98-service-tier` TIP (NOT main, NOT the wave chain — per the amended spec).
- THE SPEC (source of truth, amended with the owner addendum): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design.md`. This plan is the EXECUTION wrapper — where the spec's hunks land in the current code, in what order, with which gates. Where this plan and the spec disagree, THE SPEC WINS except where the owner addendum supersedes it (see Resolved Decisions).

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-9 specific: the measured problem — iter97: first-event→first-speech p50 **538 ms** (tool_call deltas stream before speech); iter99 T1a: tool-first turns gap p50 **1,931 ms** vs text-first **388.8 ms** (n=10/27); the prompt-rule A/B (iter99) MISSED every gate → engine-enforced is the only route. Owner update 2026-10-09 (supersedes spec v1/v2): the SPEAK call binds `LITE_NOOP_TOOL` ALONE — never bare `tools=[]` (gpt-5.4 only prompt-caches tool-bearing requests, iter48b FIND-5; the noop binding gives the speak stream its own cache lineage and turn-1 byte-matches the lite warm). Verified on origin/main 2026-10-10: `LITE_NOOP_TOOL` at `llm.py:84-93`; the executor swallows `memory_note` at `tools.py:304-307`; the lite warm binds it at `builder.py:571`; the hot lite round at `builder.py:2203-2207`.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| SPEAK call = `tools=[LITE_NOOP_TOOL]`, never `tools=[]` | Owner addendum 2026-10-09 (cache lineage; turn-1 byte-match to the lite warm `builder.py:569-571`) |
| Speak-stream tool_calls DISCARDED at the gather merge; the tools stream is the ONLY tool source | Owner addendum; executor already swallows `memory_note` (`tools.py:304`) |
| Inside the round loop, NOT LangGraph topology (no Send/parallel-node fan-out) | Spec §1 (owner-rejected refactor) |
| Lite rounds and unarmed rounds NEVER split | Spec §1 — already speech-only by construction; splitting double-charges |
| Flag `round_split_speak_tools` default False; code default flips AT the merge decision, not before | Spec §2 + SWITCH LAW rule 4 |
| PT-9 builds LAST, off the `engine/98-service-tier` tip | Owner 2026-10-10 (most effort; the spec rides the tier-knob era; disjoint touch-set from 99) |
| Spec §9 pin 2's `tools=[]` for the speak call is SUPERSEDED by the addendum — the pin asserts `[LITE_NOOP_TOOL]` | The spec text predates the owner update; this is the one deliberate divergence |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO (the wave's tier-3 gate + this plan) | master plan ASK |
| The 97/98 merge sequencing (98 must be mergeable/reachable at build time — the branch cuts from its TIP, which exists already @ `abbd9d8`) | owner dial decision on 97 (standing BLOCKED from the roadmap) |
| Suite baseline on the 98-tip base (98's own gate said 526/1/5) | cut-time measurement |

## Environment & Dependencies
- Base: `engine/98-service-tier` tip `abbd9d8` (lane env carries the `fast` tier knob — the A/B runs both sides at the SAME tier state per spec §8.3).
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (round loop), `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py` (consume adapter if needed), `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` (flag), `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter100_split_round.py`.
- Lanes: OR `:8068` (A/B), FI dry-run `:8083` (spec §8; never-touch list unchanged; preserve :8066/:8067 iter99 evidence logs before any reboot).
- Cost pull: `engine/scripts/lf.py costs` (fallback: token ledger from trace listings, proven iter98).

## Architecture (spec → current code map, verified 2026-10-10)
```
The split point: the round loop's single stream at builder.py:2317-2443
    async for ev in runtime.llm.astream(messages, tools, verbosity=...):
        ttft stamp :2322-2323 · token/dedupe :2324-2427 · tool_call_start prewarm :2428-2439 · final :2440-2443
becomes (flag ON):
    speak_task = _consume(astream(messages, [LITE_NOOP_TOOL], verbosity), tag="speak")
    tools_task = _consume(astream(messages, tools,         verbosity), tag="tools")
    speak_final, tool_final = await asyncio.gather(speak_task, tools_task)
    — the SPEAK consumer feeds the EXISTING speech pipeline (ttft, dedupe, tts_token writes)
    — the TOOLS consumer records to its final; its token events DISCARD; prewarm fires
      from ITS tool_call_start (spec §4); llm_first_event stamps from the SPEAK
      consumer ONLY (spec §3)
    — after gather: tool_calls = tool_final's (same dedupe-by-name :2536-2539);
      content = speak_final's content (spec §5.2); execute exactly as today :2569-2606;
      rounds_left/metrics unchanged, llm_s = max(speak_ms, tools_ms) (spec §5.4 — wallet
      cost documented, wall = gather total)
Flag OFF: the ORIGINAL call site runs untouched (byte-parity pin requirement — spec §8.6:
the flag-off path must be the original code, not a re-implementation).
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | `round_split_speak_tools: bool = False` | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | `_consume` helper + the split block at the round loop + gather-merge semantics + divergence WARN line (spec §7) | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | register `ROUND_SPLIT_SPEAK_TOOLS` | EDIT (branch docs) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter100_split_round.py` | the 8 spec §9 pins (addendum-corrected) | NEW (branch) |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules, PLUS: this branch does NOT touch the wave chain (stack/PT-1/PT-2) — it cuts from the 98 tip and merges independently; reconcile the round-loop surface at ITS build if the chain merged first (spec §1's line refs shift — re-verify exact lines on the build branch, the spec says so itself).
- Flag OFF = byte-exact current behavior; rollback = one env line; code default flip = merge decision only.
- NEVER touched: iter99's prompt rule (stays on its own branch, owner say-so), the lite/entry_lite rounds, the epoch/hold machinery.

## Tasks (in order)
### T1 — Flag + split (one commit)
- Build the `_consume` adapter + the split block per spec §1; ttft/llm_dispatch stamps per spec §3 (dispatch stamped ONCE before both create_tasks; `llm_first_event` from the speak consumer only); prewarm rewiring per spec §4 (tools-consumer `tool_call_start`, once-per-round latch).
- Pins (spec §9, addendum-corrected — names verbatim from the spec):
  1. `test_flag_off_exactly_one_stream` (FakeLLM counts astream calls == 1, flag False)
  2. `test_flag_on_two_streams_same_messages` (2 calls, same messages; speak call receives `[LITE_NOOP_TOOL]`, tools call receives the full array — ADDENDUM CORRECTION)
  3. `test_speak_stream_wired_to_speech_pipeline` (speak events reach the gate feed; tools tokens DO NOT)
  4. `test_tools_final_merges_after_gather` (same order + same dvs updates as today)
  5. `test_prewarm_fires_from_tools_stream` (once per round)
  6. `test_llm_clock_stamps_from_speak_call` (llm_dispatch once → llm_first_event from speak only)
  7. `test_lite_round_never_splits`
  8. `test_divergence_warn_row` (WARN line + findings importable)
- Gate: targeted pins green + full suite identical red set (526/1/5 shape per the 98 base) + byte-parity flag-off pin (spec §8.6).
### T2 — Lane A/B (the merge-decision numbers)
- Same-box, same-driver (`scripts/llm_mic_caller.py`), personas Maria + Jorge happy + ≥1 deep persona expected to hit tool-first (e.g. Susan full arc); the tool-first subgroup must be RE-PROVEN live: ≥5 tool-first turns on the base side.
- Gates (spec §8.2): `llm_first_event_to_llm_first_ms` p50 ≤ **50 ms** structural AND e2e_response p50 ≤ base − **300 ms** AND compliance ≥ **80%** of branch turns gap < 100 ms AND zero NEW findings-class on the happy path.
- Identical `.env` both sides (SWITCH LAW #3, same tier state); cost pull `lf.py costs` delta + token ledger (spec §8.4).
- Bookings created on test slots: CANCEL (event 3801235 is REAL).
### T3 — ASK (merge decision)
- ASK carries: suite delta, 8 pins, the A/B gate numbers, the cost delta (the §6 tension — the speak stream's cache cost is REAL and must be in the merge answer), the divergence-monitor rows.

## Validation Plan (end-to-end)
1. Suite identical red set + 8 pins + byte-parity pin green.
2. A/B gates all four (§8.2) on the OR :8068 lane; evidence under `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/`.
3. Divergence monitor live: WARN rows imported to the findings ledger (§7); known-benign class listed.
4. No prompt/KB changes on this branch.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| v2 speech-gating on tools outcome | spec §10 — NOT in this build |
| tier=fast on the speak stream / `round_split_speak_cache_guard` tuning | spec §6 — explicitly out of v1 (single-variable A/B) |
| GK stress battery | end-of-queue, after the owner blesses a lane |
