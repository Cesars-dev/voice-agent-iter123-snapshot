# Wave plan PT-5 — RAG query memo (byte-identical reuse; runs 2nd inside the stack branch)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: per-call dict `{normalized query-set → results}` on the graph runtime. Fire time: byte-identical hit → skip embed+search, reuse stored chunks; miss → fire and store. NO sqlite. Kills the canned-query re-fire waste (Oct-8: 34 fires, 25 identical canned, same top-3 15×, ≈2.5–5 s cumulative dead time).
- Status: PLAN ONLY (awaits owner GO; runs as commit #2 of the wave stack branch)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: THE STACK BRANCH — this PT is its SECOND commit (after PT-8).

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context (identical for every file in this folder — chain law, suite gate, LANE LAW, evidence dir).

PT-5 specific: owner-ratified semantics 2026-10-09: "a chunk retrieved (byte-identical or chunk-identical) should not be retrieved again". Evidence: Oct-8 call `CAcf047fe3fd9075` (trace `be7bb8e7404b76d2c0b50ddc9636e4d2`) — laneA fires 25× with identical canned queries (the caller sat 6 min in Intake with dv values never captured, so `refer_query` produced the same WHATs + caller-text blend every round); each fire ≈100–200 ms embed+search; same top-3 chunks 15×. The identical-chunk append dedupe ALREADY exists at `builder.py` (`seen` set on `(kb, content)` in the drift-append path, :2114-2124) — this PT kills the RE-FIRE cost, not the render cost.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| BYTE-IDENTICAL semantics only — no cosine, no fuzzy | Owner-ratified; the iter59 semantic-dedupe overengineering lesson (PT-73 law) |
| Per-call in-memory dict on CallRuntime — NO sqlite | Owner brainstorm ratified; the stash precedent `_live_consumed_res` (`builder.py:426`) dies with the call = free end_call purge |
| Memo keys the QUERY SET (all lanes of one fire), not a single query | `_live_retrieve` fires multi-lane (laneA refer-tag queries + laneB utterance, `builder.py:1545-1599` hybrid); a hit is only a hit when EVERY lane query matches byte-identically |
| The normalize rule + dict init line close HERE (the 01_wave_eval "spec gap" for PT-5) | This file IS the edit-spec closure for PT-5 |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO (stack branch already cut for PT-8) | master plan ASK |
| Suite baseline (inherited from the stack branch's PT-8 gate) | measured at cut |

## Environment & Dependencies
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (only file touched).
- No new packages, no new Settings fields (pure additive cache; nothing to switch — the memo is always-on per-call, same as `_rag_cache`/`_pinned_industry`).

## Architecture (the fire path today, verified)
```
session._on_eager_eot / _on_eot / _on_stt_update   (session.py:686-695 / :543-552 / :594-619)
  └─ runtime.spawn_live_retrieve(state, dvs, msg, lane)      (builder.py:1402-1434)
       └─ _live_task → _live_retrieve(state, dvs, msg, store, lane)   (builder.py:1305-1332)
            └─ _retrieve_raw(...)  → build_lanes (builder.py:1154+) → ONE batched embed → pgvector → merge_lane_chunks
            returns (delta, kbs, ms, merged_chunks, lane_qs)
  round: _consume_live_retrieve                            (builder.py:1480-1576 / hybrid :1578+)
       stale-or-missing → spawn_live_retrieve AGAIN (builder.py:1540-1542)   ← the re-fire waste
```
Note the consumer ALREADY has same-turn reuse (`_live_merged_turn` stash, builder.py:1595-1599) and msg-text staleness (`_live_msgs` check, :1527-1529) — those are per-turn mechanisms; the memo is the PER-CALL layer beneath them: the Oct-8 shape was the SAME canned query firing fresh across DIFFERENT turns, which every existing guard passes as "fresh".

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | (1) `CallRuntime.__init__`: `self._rag_query_memo: dict[str, dict] = {}` directly under `_live_consumed_res` (:426). (2) `_retrieve_raw`: after lane queries are built (`lane_qs` exists) and BEFORE the embed call — memo check/store (exact edit below). (3) `initial_state` (:2916-2934): `self._rag_query_memo = {}` in the per-call reset block (same place `_pinned_industry` resets, :2933). | EDIT (stack branch, commit #2) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_rag_query_memo.py` | pins (below) | NEW (same commit) |

The edit-spec closure (normalize rule + hit/miss semantics), written against `_live_retrieve`/`_retrieve_raw` as read 2026-10-10:
```python
# inside _retrieve_raw, AFTER lane_qs is built, BEFORE any embed/search:
_memo_key = f"{state_name}|{lane}|" + " || ".join(
    " ".join(str(q or "").split()).lower() for q in lane_qs)   # normalize: whitespace-collapse + lowercase
_hit = runtime._rag_query_memo.get(_memo_key)                  # WAIT — _retrieve_raw is a method: self._rag_query_memo
if _hit is not None:
    return _hit          # (lane_results, owned, ms, lane_qs, pinned_tag, pin) — byte-identical reuse
... existing embed + search + pinned-industry logic ...
self._rag_query_memo[_memo_key] = (lane_results, owned, ms, lane_qs, pinned_tag, pin)
```
Why memoize `_retrieve_raw`'s outputs and not `_live_retrieve`'s: `_live_retrieve` (builder.py:1320-1332) merge+render is deterministic given the raw pieces — memoizing one level down keeps `_ensure_pinned_industry` (its own once-per-dv cache, :1362-1391) untouched and avoids double-bookkeeping of `ms`. The `ms` stored on a hit is the ORIGINAL retrieval's ms — the span will show `rag:pin`-style honesty via a `"memo": true` flag added to the rag span output (builder.py:1974-1987) so ledger rows distinguish reuse from fire (one extra dict key, no behavior).
Cap: `if len(self._rag_query_memo) > 128: self._rag_query_memo.clear()` — same crude cap style as `_rag_cache` (builder.py:2039-2040); a call cannot legitimately produce 128 distinct query-sets.

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Commit #2 of the stack branch: `iter<NN> PT-5: RAG query memo — byte-identical per-call query-set cache (skip embed+search on hit, no sqlite)`.
- NEVER touched: `_live_consumed_res` degrade semantics (C4), the `_live_merged_turn` same-turn stash, seq freshness (a memo hit does NOT fake a seq — the consumer still marks consumption exactly as today), pgvector, prompts.

## Tasks (in order)
### T1 — Memo (one commit)
- Goal: the three hunks above.
- Commands: edit in the FI worktree; `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests/test_iter<NN>_rag_query_memo.py -q` then full suite gate.
- Pins (`test_iter<NN>_rag_query_memo.py`, scripted FakeStore counting embed calls):
  1. `test_three_identical_queries_one_embed`: 3 fires with identical query text (the Oct-8 canned shape) → embed called ONCE, rounds 2–3 serve the memo hit byte-identically (delta/chunks equality asserted).
  2. `test_delta_query_new_fire`: caller text changes → new embed + new memo entry.
  3. `test_normalization_hit`: query differing only by case/whitespace → still a hit.
  4. `test_fresh_runtime_empty_memo`: new CallRuntime → empty dict (call-end purge proof); `initial_state()` re-run → dict cleared.
  5. `test_memo_flag_on_span`: the rag span output carries `"memo": true` on hits, absent/false on fires.
  6. `test_consumer_staleness_untouched`: an "eot"-mode msg-text mismatch still fires (memo never bypasses the consumer's staleness check).
- Dependencies: stack branch @ PT-8 commit.
### T2 — Data gate replay + ASK
- Scripted 3-caller-fast shape replaying the cf047 pattern (34 fires, 25 identical): expect 1 embed + 24 memo hits; dispatch→first p50 unchanged. Numbers into the ASK.

## Validation Plan (end-to-end)
1. Suite red set byte-identical + 6 pins green.
2. cf047 replay: rag table rows distinguish fire vs reuse (`memo` flag); latency counter-style unchanged on non-hit turns.
3. No prompt/KB/env changes. Ledger import per SOP on any lane run.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| PT-7's WHAT-anchor shortening | folded (owner): prompt-ride on say-so only — see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-7_intake_refer_tag_FOLDED.md` |
| Cross-call memo (sqlite or otherwise) | explicitly rejected by owner ("no sqlite"); per-call only |
