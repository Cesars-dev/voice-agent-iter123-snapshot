# 01_AUDIT — iter87 prewarm VERSION B (THE DETERMINISTIC HOLD)

- Procedure: `tasks/surgeon/iter87-prewarm-hold/`
- Date: 2026-09-30. Session box: Finland (MainVps). Code box: OREGON (5.78.83.174).
- Base audited: **wt-iter85 = `542d3e8`** (branch `engine/iter85-eager-hold`) — the commit the
  new `engine/iter87-<slug>` branch will be cut from, per the master plan.
- Design input (owner, verbatim): `research/surgeon/iter86-warm-sync/07_owner_design_capture.md`
  (= `/Users/Cesar_1/vps-inbox/01_plan_VERSION_B.md`, "plan_iter86 VERSION B — THE
  DETERMINISTIC HOLD"). NOTE: the design's line anchors were verified by its author @
  `8e3eafc` (outside-fixes pack); this audit re-verifies every anchor @ `542d3e8`.
- Governing plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter87_prewarm_owner_design.md`.

## A. Files read (all @ 542d3e8, OREGON)

| File | Size | Role |
|---|---|---|
| `engine/diallux/graph/builder.py` | 2865 ln | rounds, warms, awaits, chain, graph wiring |
| `engine/diallux/config.py` | 482 ln | knobs |
| `engine/diallux/graph/llm.py` | — | `build_tool_schemas` (:145), `warm` (:288), `astream` |
| `engine/diallux/media/session.py` | — | per-call runtime, greeting warms, turn reports |
| `engine/diallux/observability/latency.py` | — | `TurnClock` (:17) |
| `engine/agent/llm.json` | — | states + edges (FSM), per-state tools |
| `engine/tests/` | — | test_iter43/44/46/59/61/65_prewarm*, test_iter85_eager_hold |

## B. The prewarm system AS IT EXISTS (@ 542d3e8)

### B1. Fire sites — COMPLETE inventory
| # | Site | Line | Trigger | Force? | History snapshot |
|---|---|---|---|---|---|
| F1 | `session.py` greeting full warm | :256 | during greeting playback, initial state | no | initial payload history |
| F2 | `session.py` greeting lite warm | :264 | same, `lite=True` (key `lite:<state>`) | no | same |
| F3 | `builder.py` tool-detect warm | :2387 | `tool_call_start` event whose name is `transition_to_*` | no | `list(history)` (WITHOUT this round's new tool msgs) |
| F4 | `builder.py` post-execute warm | :2552-2554 | round executed a tool that set `new_state` | **yes** | `list(history)+list(new_history)` + post-patch dvs |
| F5 | `builder.py` RAG prefetch | :2560 (`warm_rag_async`, def :876) | same as F4 (+ConfirmSlots entry) | n/a | n/a (chunks, not LLM prefix) |
| — | **CHAIN path (`_deterministic_node`)** | :2622-2715 | phaseb chain runs `transition_to_VerifyLead/Booking/Closing` | — | **ZERO warms fired — K1, confirmed: no `warm_prompt_cache` call anywhere in the node** |

**MISSING (per design §3):** one-ahead successor warms (speech path) and all chain-path
warms. Nothing warms a state before the model actually calls `transition_to_X`, except the
knife-edge F3.

### B2. Latch + task registry
- `warm_prompt_cache` (builder.py:460-504): latch `self._prewarmed` (init :393, set :488,
  checked :482 — skipped when latched unless `force=True`); task registered in
  `self._warm_tasks` (:394, cancelled in `aclose` :443-456) and `self._latest_warm[state_name]`
  (:398; non-lite key = bare state name, lite key = `lite:<state>`, :500-504). **`force=True`
  re-fires and supersedes `_latest_warm`** — the await target is always the newest task.
- `_prewarmed` has NO `.clear()` in `initial_state()` (:2820-2846) — **not a bug**: the
  runtime itself is constructed per call (`session.py:174 CallRuntime(...)`), so the latch is
  call-scoped by construction. `_latest_warm` IS additionally cleared per call (:2839).
- Master gate: `prompt_prewarm` (config :118, default True; env `PROMPT_PREWARM=false` kills
  every warm — checked at :479 BEFORE anything fires). All new fire sites MUST route through
  `warm_prompt_cache` to keep this gate intact.

### B3. Warm payload shape (`_warm`, builder.py:543-625)
- Composes through the SAME `_build_messages` as the hot path (byte-exact prefix):
  `[tools][head][history-window]`; under `state_in_delta` (current default) NO pre-history
  state-block tail (:567-573 comment block; dvs rides the post-history delta in the hot path,
  which re-bills anyway) — so **the warm's prefix bytes do not depend on dvs**; they depend on
  tools + head + history window.
- Failure path: one lite-shape retry, diag recorded for the span (:612-624). Warm durations
  measured 994-2059 ms (b3, per design).
- `llm.warm` (llm.py:288-295): `bind_tools(tools)` + `ainvoke`, output capped at
  `prewarm_max_completion_tokens=64` (config :119). No internal try/except (by design).

### B4. Await paths — COMPLETE inventory (the round-assembly await chain, :1838-1857)
| Round kind | Behavior | Cap |
|---|---|---|
| turn-1 lite | awaits `lite:<state>` warm, EOT rounds only | `prewarm_entry_wait_eot_ms` = 500 (:219) |
| **entry_lite (state-entry ack)** | **`pass` — NEVER awaits (:1846-1852)** | — |
| heavy, EOT boundary | `_await_warm(state_name)` | 500 |
| heavy, mid-turn | `_await_warm(state_name)` | `prewarm_entry_wait_ms` = 100 (:214) |

- `_await_warm` (builder.py:627-668): awaits a **TASK** via `asyncio.wait_for(asyncio.shield(task),
  wait_ms/1000)` — event-driven release, 0 ms if done, instant return if no task; outcomes
  `no_task/already_done/landed/timeout/task_error`; spanned `await_warm` with
  `waited_ms`/`cap_ms` under `warm_observability` (config :339, default True).
- **K3 (proven, do not re-litigate):** in 57 spans the await found an in-flight warm ZERO
  times (47 already_done + 10 no_task) — awaiting alone fixes nothing without SCHEDULING.

### B5. The entry_lite ack round (the destination round the HOLD guards)
- Defined :1797-1808: fires when `state_name != runtime._prev_round_state` (and turn>1, not
  turn-1 lite, not in `state_entry_lite_off`). Covers post-transition acks AND turn-2 entry
  into the initial state (whose warm = F1 greeting warm, fired during greeting playback).
- Payload (:1813-1818, :2165-2190, :2210-2218): FULL tool array (FIND-5 port — byte-identical
  `(state, expand_kb)` cache key to the heavy round's) + `_entry_lite_head` (kb=False, same
  strip decision → same head bytes) + history + post-history delta (speech-only directive +
  state block under `state_in_delta`). **Its `[tools][head]` prefix IS the heavy/warm prefix**
  — a landed destination warm gives the ack round cache_read directly.
- The ack round's history after a speech-path transition = `history + new_history` — exactly
  F4's warm snapshot → byte parity through the history window.
- After a chain pass: `_deterministic_node` returns NO history update (tool results of chain
  steps never enter history) → the Closing ack round's history = `state["history"]` as it
  stands at chain start → **a chain-start warm using `list(state.get("history") or [])` is
  byte-exact for the ack**.

### B6. FSM + successor-map derivation surface
- `self.states` (builder.py:352) = `llm_json["states"]`; each state cfg carries `edges: [
  {destination_state_name, ...}]`; `build_tool_schemas` (llm.py:196-204) generates the
  `transition_to_<dest>` tool schemas FROM those edges. The FSM is a single chain:
  Intake→Discovery→Closer→Offer→contact_details→ConfirmSlots→VerifyLead→Booking→Closing
  (Closing: no edges). **The successor map the design wants = 3 lines:
  `{s["name"]: [e["destination_state_name"] for e in s.get("edges", [])] for s in
  llm_json["states"]}` — derivable at build, NO hand-written table needed.** (The chain's
  `plan = [...]` at :2660-2668 IS a hand-written step list — different concern, stays.)

### B7. Chain path (`_deterministic_node`, :2622-2715)
- Gate :2645-2652 (phaseb_chain + ConfirmSlots/VerifyLead/Booking + slot_verified etc.).
- `plan` :2660-2668: `validate_lead`, `transition_to_VerifyLead`, `verify_lead_data`,
  `transition_to_Booking`, `create_livecall_booking`, `record_booking_uid`,
  `record_booking_outcome`, `transition_to_Closing` — executed in one pass, fillers via
  stream writer, abort → `chain_aborted_step` + return with `cur_state` = the state reached
  so far; success → returns `state_name: "Closing"`.
- **No `warm_prompt_cache`, no `warm_rag_async` anywhere in the node → every chain-produced
  destination round (the Closing ack, and any abort-repair round) runs on a cold prefix. K1.**
- Webhook idle 1.5-4.5 s exists inside the chain (slow steps `_PHASEB_SLOW` + fillers) — the
  design's chain-start warm lands inside it for free.

### B8. Telemetry (T1.4/T1.4b surface)
- `ttft_s` (builder.py:2244) set ONLY on the first `"token"` event (:2271-2272,
  "time to FIRST spoken token (TTS-visible)"). On tool-only rounds ttft stays `None`
  (round usage log :2397-2406 prints `ttft=None`). T1.4 = set it on the first event of ANY
  type (`token` OR `tool_call_start`).
- Round usage log :2397-2406: turn, state, input, **cache_read**, output, ttft,
  state_in_delta, delta_tokens — the K-gate readout.
- Turn reports: `TurnClock` (observability/latency.py:17); `clock.report()` appended in
  `session.py:819-821` at `gate.end_of_turn()` + `mark_turn_done()`; late report
  (:829-843) waits ≤3 s for audio drain, adds `resumed_count`, emits
  `turn:{n}:final` span + `metrics.observe_turn_report`.
- **The iter86 SDK (`engine/scripts/call_forensics.py`, branch engine/iter86-warm-sync @
  d158b4c) already computes the conv-side metric offline (user-perceived = S2L−HS+L2T+T2A,
  per-turn eager/wait/cold counters).** Relevance for T1.4b: see R2.

## C. Design anchors re-verified @ 542d3e8 (design said @ 8e3eafc)

| Design claim | Design anchor | Actual @ 542d3e8 | Status |
|---|---|---|---|
| entry_lite branch body is `pass` | :1846-1852 | :1846-1852 — exact, incl. the "NEVER awaits — speak now" comment | ✅ EXACT |
| `_await_warm` exists (shielded/spanned/event-driven) | :627 | :627-668 — exact | ✅ EXACT |
| post-execute force=True warm | :2552-2554 | :2548-2554 (call at 2552-2554) | ✅ (comment starts 2548) |
| chain start fire site | :2668 | phaseb gate :2645-2652, `plan` list :2660-2668, loop from :2670 | ✅ ≈ (insert after gate, before/around plan) |
| re-fire post-patch site | :2699 | chain loop :2670-2712; post-loop return block :2712-2715 | ✅ ≈ (insert post-loop) |
| `state_entry_lite` default True | config:95 | config:95 — exact | ✅ |
| knob slot next to | config:219 | :214 `prewarm_entry_wait_ms`, :219 `prewarm_entry_wait_eot_ms` | ✅ |
| successors derivable from `transition_to_*` tools, 3-line loop, no hand table | §3.1 | via `edges` in llm.json (llm.py:196-204) — NOT via tool-name strings | ✅ with mechanism note (C1) |

**C1 (mechanism note):** state cfgs contain no literal `transition_to_*` strings; the tools
are GENERATED from `state_cfg["edges"]` in `build_tool_schemas`. The successor map must be
derived from `edges` (same source of truth), not from scanning tool names.

## D. EXISTS vs MISSING

**EXISTS (reuse, do not rebuild):** `_await_warm` (:627), warm latch/registry
(`warm_prompt_cache` :460-504), byte-exact warm composer (`_warm` :543-625), tool-detect warm
(F3 :2387), post-execute force warm (F4 :2552-2554), RAG transition prefetch (F5), greeting
warms (F1/F2), warm/await spans + round usage log (cache_read, ttft), master gate
`prompt_prewarm`, per-call runtime scoping.

**MISSING (the build):**
1. HOLD: entry_lite branch awaits the destination warm (knob `warm_await_dest_ms`, default 0
   = today byte-exact).
2. FIRE speech one-ahead: after F4, warm `new_state`'s FSM successors (edges-derived map).
3. FIRE chain: warm at chain start (destinations from the plan's `transition_to_*` steps) +
   post-patch re-fire (force=True) after the chain loop.
4. T1.4: ttft on first delta of ANY type.
5. (T1.4b — see R2 for scope resolution.)

## E. Bugs / risks / conflicts found

- **R1 — anchor drift:** none material; all design anchors verified at the actual base
  (table C). Two are ±few lines (chain sites) — exact insertion points pinned in
  02_action_plan.
- **R2 — T1.4b vs "only builder.py + config.py":** turn reports live in
  `media/session.py` + `observability/latency.py` (TurnClock). "Re-anchor turn reports at
  confirmed EOT + per-turn fire/resume/head-start counts" as an ENGINE change would touch
  session.py — contradicting design §5's diff scope. **Resolution candidate:** the iter86 SDK
  already re-anchors conv-side (user-perceived from confirmed EOT) and counts eager/wait/cold
  per turn offline; engine-side only T1.4 (builder.py) is needed. Owner must ratify this
  scope reading in the master plan.
- **R3 — one-ahead latch interaction:** one-ahead warm latches the successor (non-force) →
  the later tool-detect warm (F3, non-force) becomes a no-op → recency relies on F4's
  force re-fire, which always fires on `new_state` (:2548). `_latest_warm` then points at the
  F4 task, so the HOLD awaits the freshest bytes. Correct — but only because F4 is
  unconditional on transition. Do not remove F4.
- **R4 — chain abort repair round:** on abort, `cur_state` may be VerifyLead/Booking
  (mid-chain); the repair ack in that state would hold on `no_task` (safe: proceeds cold,
  never stalls). Warming ALL chain destinations at chain start (VerifyLead, Booking, Closing —
  3 × 64-token requests, negligible cost) also covers abort repairs. Design §3 says
  "destination derived from the `transition_to_*` step name" (singular) — action plan pins
  plural (all three) with this rationale.
- **R5 — master gate:** all new fire sites route through `warm_prompt_cache` →
  `PROMPT_PREWARM=false` keeps killing everything (design gate §4). No new fire path may
  bypass it.
- **R6 — byte-exact default:** `warm_await_dest_ms=0` → the new branch is dead code at
  default (knob law; repo rollback). Suite must stay at the known 7 stale reds, zero new.
- **R7 — head byte parity ack-vs-warm:** ack head = `_entry_lite_head` (kb=False + strip);
  warm head = `_head_for(state, store)`. With a store present, live rounds render expand=False
  and the same strip decision (comment :834-847 "head bytes IDENTICAL"); with no store both
  are kb=False. Preflight re-checks `_head_for` to confirm no divergent path (e.g. inline
  expand) exists.
- **R8 — eager interaction:** an entry_lite ack can occur inside an eager turn (caller kept
  talking through the transition). The hold inserts before the LLM send; with FIRE law the
  warm is typically `already_done` (0 ms). Worst case it waits ≤ warm remainder — bounded by
  the 2500 ms fence, degrades to today's cold round on timeout. No change to the eager/EOT
  contract (design §2.3: eager path stays as-is).
- **R9 — `state_entry_lite_off` states:** destination rounds in opted-out states skip the
  ack path entirely → they keep the existing heavy-round awaits (500/100). Unchanged by
  design; documented so the battery readout doesn't misattribute those rounds.
- **R10 — gate telemetry naming:** design gate says `outcome=warm_waited`; actual outcomes
  are `no_task/already_done/landed/timeout/task_error`. The gate must be defined on the
  `await_warm` spans with `cap_ms=2500`: waited_ms p50 ≈ 0 (mostly already_done), p99 ≤ a few
  hundred, `timeout` count = 0 in normal runs. Terminology pinned in the master plan.
- **R11 — `_await_warm` key:** the hold must await the NON-lite key (`state_name`) — the ack
  carries full tools (FIND-5) and destination warms register under the bare state name.
  Design snippet already does this. ✅
- **R12 — turn-2 initial-state ack:** covered by the F1 greeting warm (fired at greeting
  start, ~always done by turn 2) → hold ≈ 0 ms there. No new fire needed.

## F. Test surface (for 02_action_plan)
- Patterns: `tests/test_iter46_latency_floor.py` (asserts `rt._prewarmed`, await outcomes),
  `tests/test_iter43_prewarm.py`, `tests/test_iter44_prewarm_bytes.py` (byte parity),
  `tests/test_iter85_eager_hold.py` (fake clock/gate/stream style).
- Suite baseline: 7 known stale reds (test_delivery ×4, iter46 fast-first-flush, iter59,
  iter60) — never re-derived; zero NEW reds is the gate.
