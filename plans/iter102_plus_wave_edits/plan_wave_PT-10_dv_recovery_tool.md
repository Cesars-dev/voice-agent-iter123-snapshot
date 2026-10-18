# Wave plan PT-10 — dv-failure-gated recovery tool on the verify-data state (own branch; BLOCKED on the owner's design dictation)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: a recovery tool accessible on the verify-data state ONLY while a dv-capture failure flag is OPEN — default CLOSED, gated in CODE (the LLM must never be able to call it on a whim). Recovery path candidate: the caller's own number from caller-ID (rides PT-11's wire).
- Status: PLAN ONLY — BLOCKED on the owner's design dictation (HITL, same pattern as the iter87 prewarm dictation). NO branch cut, NO code, until the dictation lands.
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: OWN branch (owner 2026-10-10), number + slug ratify at cut — cut AFTER PT-11's wire lands (dependency edge).

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-10 specific — what the code says TODAY (verified on origin/main 2026-10-10), so the dictation starts from facts:
- The verify-data state is **`VerifyLead`** in this engine (Retell-speak "Verify Data"). Its chain step is `verify_lead_data` (builder.py:2726, `_PHASEB_SLOW` :302); the Phase-B booking chain gate at builder.py:2710-2716 requires `slot_verified`, `selected_time`, `prospect_timezone`, `callback_number`, `first_name` — a missing `callback_number` (the Oct-6/8 empty-value disease PT-11 fixes at the transport layer) blocks the whole deterministic chain today, with no in-conversation recovery path other than the model re-asking.
- The engine ALREADY has the pattern for code-gated tool availability: state-scoped tool arrays (`build_tool_schemas` per state, builder.py:575-583/:2189-2197/:2227-2235) and the per-state opt-out list (`state_entry_lite_off`). A tool that exists ONLY in VerifyLead's array AND only when a boolean dv is open = a two-line gate around the schema assembly.
- dv booleans ride `DynamicVariables` (schema.py; seeded via `state.py:59-64`, written via `dvs_patch` in tool outcomes).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| The tool is CLOSED by default and gated in CODE | Owner-added row verbatim: "the LLM must never be able to call it on a whim" |
| Own branch, after PT-11's wire | Owner branching directives 5 + the dependency edge (caller-ID fallback needs the number to actually arrive) |
| Design-first via HITL dictation — nothing is built before it | Owner pattern (iter87 precedent); three open questions below are the dictation agenda |

## BLOCKED / NEEDS INPUT (the dictation agenda — these are DICTATION ANSWERS, not TBD rows)
| Question | The code fact the answer must resolve |
|---|---|
| 1. Exact state name — `VerifyLead` only, or also `ConfirmSlots`/`Booking`? | the Phase-B chain spans ConfirmSlots → VerifyLead → Booking (builder.py:2724-2731); a failure can surface at any chain gate, but the verify STATE is VerifyLead |
| 2. The dv-failure boolean's trigger list — which failed captures OPEN it? | candidate triggers: `verify_lead_data` returning a missing/invalid field; the chain gate at :2710-2716 failing on a required dv; the booking 400 class (`invalid_number`) |
| 3. The recovery action set — what may the tool DO? | candidate: seed the failed dv from caller-ID (PT-11's `callback_number`), retry the failed chain step, or hand control back to the model with a targeted re-ask directive |
| 4. (design consequence) The boolean's lifetime — per-turn, per-call, or until resolved? | dv booleans persist for the call; a stale OPEN flag would leave the tool callable too long — needs the owner's intent |

## Environment & Dependencies
- Files (post-dictation, expected): `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (tool-array gate), `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/tools.py` (the recovery tool's executor arm), `/home/julio/projects/clean_diallux_SDR/engine/agent/llm.json` + the VerifyLead prompt (prompt-layer = CODE, LAW 0, same branch) IF the dictation requires the model to know the tool exists.
- Depends on: PT-11's wire (merged or at least on the chain), the dictation.

## Architecture (pre-dictation sketch — every element subject to the owner's answers)
```
dv: dv_recovery_open: bool = False            (schema.py DynamicVariables; default CLOSED)
trigger (candidate): verify_lead_data failure / chain-gate miss writes dvs_patch {"dv_recovery_open": True}
gate (code, two lines at the tool-array assembly):
    tools = base_tools
    if state_name == "VerifyLead" and dvs.get("dv_recovery_open"):
        tools = base_tools + [RECOVERY_TOOL_SCHEMA]
executor arm (tools.py, next to the memory_note swallow :304):
    if name == "recover_dv_capture": ...   (action set = dictation answer 3)
close: the successful recovery (or the model's natural re-ask) writes {"dv_recovery_open": False}
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| TBD by the dictation — expected: builder.py tool-array gate + tools.py executor arm + schema.py dv field + (maybe) VerifyLead prompt/llm.json lockstep | smallest change per dictation | TBD |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. This branch cuts from wherever the chain stands AFTER PT-11's wire (owner decides the exact base at dictation time).
- HARD LAW: the tool is NEVER in a state's base array; the gate is code, not a prompt instruction.

## Tasks (in order)
### T0 — The dictation (HITL, the only executable task now)
- Run the 4-question agenda with the owner; capture verbatim into `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/04_pt10_design_dictation.md`; write the real plan (this file gains the concrete design) and ASK for the branch GO.
### T1+ — build per the dictated design (own branch → suite → pins → battery → ASK per LAW 0)

## Validation Plan (end-to-end)
- (Post-dictation) The code-gate pin class: the tool schema is ABSENT from every state's array with the flag closed; PRESENT only on the dictated state(s) with the flag open; the executor refuses (unknown_tool) when called out of band — the "never on a whim" guarantee pinned, not promised.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Everything concrete | blocked on the dictation — by design, not by neglect |
