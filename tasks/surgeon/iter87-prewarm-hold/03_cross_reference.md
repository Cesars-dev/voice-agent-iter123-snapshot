# 03_CROSS_REFERENCE — audit (01) vs action plan (02)

Method: every audit finding ↔ every planned change. Three questions: (1) does the plan
address every issue the audit found? (2) does the audit support every change the plan
proposes? (3) contradictions / gaps / redundancies.

## 1. Audit issues → plan coverage

| Audit item | Plan coverage | Verdict |
|---|---|---|
| R1 anchor drift (chain sites ±lines) | 02 Steps 5-6 pin exact insertion points (after `plan = [...]` :2660-2668; before `phaseb:chain_ok` return :2712-2715) | ✅ addressed |
| R2 T1.4b vs "only builder.py+config.py" | 02 Step 8: resolved as SDK-side, owner ratification required in 04 | ✅ addressed (pending owner) |
| R3 one-ahead latch → F3 becomes no-op; recency via F4 force | 02 Step 4 keeps F4 untouched + comment states the supersede dependency; test 5 asserts supersede | ✅ addressed |
| R4 chain abort repair round cold | 02 Step 5 warms ALL chain destinations (VerifyLead, Booking, Closing) — plural, rationale in comment | ✅ addressed (pending owner ratification of plural reading) |
| R5 master gate PROMPT_PREWARM | All fire sites (Steps 4-6) route through `warm_prompt_cache`; test 8 asserts the gate | ✅ addressed |
| R6 byte-exact default | Knob default 0 (Step 1); Step 3 guard `> 0`; test 1 | ✅ addressed |
| R7 head byte parity ack-vs-warm (comment-level proof only) | NOT closed in 02 — carried to 04 preflight as a mandatory code check (`_head_for` vs `_entry_lite_head`) | ⚠️ open → 04 |
| R8 eager interaction | No code change; documented (hold bounded by fence, degrades to cold round). No test — acceptable (integration-level) | ✅ documented |
| R9 state_entry_lite_off states | No change by design; battery readout note only | ✅ documented |
| R10 gate telemetry naming (`warm_waited` not an outcome) | 02 Step 10 gates defined on actual outcomes (`landed/already_done/no_task/timeout`, `waited_ms`, `cap_ms=2500`) | ✅ addressed |
| R11 non-lite await key | Step 3 note + design snippet uses bare `state_name` | ✅ addressed |
| R12 turn-2 initial-state ack | Covered by existing F1 greeting warm; no change | ✅ documented |

## 2. Plan changes → audit support

| Plan change | Audit support | Verdict |
|---|---|---|
| Step 1 knob `warm_await_dest_ms=0` @ config ~:219 | B4 (await chain), design knob law; config :212-219 block verified | ✅ |
| Step 2 successor map from `edges` | B6 + C1: edges are the source of truth (llm.py:196-204); 3-line derivation verified against llm.json (single-chain FSM) | ✅ |
| Step 3 HOLD in entry_lite `pass` | B4/B5: `_await_warm` :627-668 (task await, shield, span); ack prefix = warm prefix (full tools FIND-5 + same head bytes R7-pending) | ✅ (R7 check pending) |
| Step 4 one-ahead after F4 | B1/B2: F4 unconditional on `new_state`; latch dedupes non-force; `_latest_warm` supersede semantics :500-504 | ✅ |
| Step 5 chain-start fire | B7: no warm exists in chain (K1); chain appends no history → `state["history"]` byte-exact for the ack; webhook idle 1.5-4.5 s | ✅ |
| Step 6 chain post-patch re-fire | B2: `force=True` supersedes `_latest_warm` (owner-designed mechanism, :473-479 doc); dvs not in prefix under state_in_delta | ✅ |
| Step 7 ttft any-delta | B8: current code sets ttft only on `"token"` (:2271-2272); loop-top hoist is behavior-preserving for speech-first rounds | ✅ |
| Step 9 tests | F: patterns exist (test_iter46 asserts `_prewarmed`; test_iter85 fake style); 7-stale-red baseline known | ✅ |
| Step 10 battery | Master plan T3 + round-B knobs; SDK exists (d158b4c); forensics_calls table seeded | ✅ |

## 3. Contradictions / gaps / redundancies

1. **"builder.py (5 sites)" vs 6 edit sites (A-F).** The design's count undercounts (the
   successor map + ttft are sites too, or the map rides inside "one-ahead"). Immaterial —
   scope is unchanged (builder.py + config.py only). RESOLVED: no action.
2. **T1.4b scope (design §3.3 vs §5).** §3 includes "re-anchor turn reports at confirmed
   EOT"; §5 says the diff touches only builder.py+config.py; turn reports live in
   session.py/latency.py. RESOLVED in 02 Step 8 via the SDK (which already does the
   conv-side re-anchor + per-turn counts). **Owner must ratify** — flagged in 04.
3. **Chain destination singular vs plural.** Design §3.1 says "destination derived from the
   `transition_to_*` step name" (ambiguous); audit R4 + 02 Step 5 choose plural (all three).
   Cost: 2 extra 64-token warm requests per chain run. **Owner must ratify** — flagged in 04.
4. **Gate wording.** Design gate `outcome=warm_waited` names a nonexistent outcome value.
   RESOLVED: gates defined on real outcome values (R10). No action needed beyond 02 Step 10.
5. **R7 (head parity)** — the only technical open item; must be closed by CODE inspection
   in 04 preflight before the plan is airtight.
6. Redundancies: none found (no double-await: entry_lite branch is exclusive of the
   eot/mid-turn branches; hold fires once per round).

## 4. Verdict
02 addresses every audit issue except R7 (deferred to preflight by design of the
framework) and two owner-ratification items (T1.4b scope, chain plural). The audit
supports every planned change. → Proceed to 04 PREFLIGHT with mandatory checks:
(a) `_head_for` vs `_entry_lite_head` byte parity (R7); (b) exact insertion-context line
re-verification; (c) `warm_prompt_cache` / `_await_warm` signature match; (d) variable
context (`runtime` in state_node vs `self` in _deterministic_node); (e) test-pattern
feasibility (how tests construct the runtime).
