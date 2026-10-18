# Wave plan PT-11 — caller number must reach the engine (trace first, then the wire; runs 5th inside the stack branch)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: the caller's own number (Twilio `From`) must arrive in `dvs["callback_number"]`. Phase A = zero-code runtime trace of where the paper chain dies. Phase B = the 1–2-line wire fix, dictated by the trace findings. Feeds PT-10's caller-ID recovery fallback.
- Status: PLAN ONLY (awaits owner GO; runs as commit #5 — the LAST commit — of the wave stack branch)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: THE STACK BRANCH — trace (phase A) runs inside the stack session BEFORE any commit; the wire (phase B) is the stack's final commit.

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-11 specific: OWNER DIRECTIVE 2026-10-10 — the trace answers WHY the `<Parameter>` injection was chosen + where it dies at runtime. Paper chain (verified on origin/main 2026-10-10, all links present on the serving build `06bdd97` too):
1. `app.py:124-141` `/twiml`: `from_number = (request.query_params.get("From") or "").strip()` (:128) → if non-empty, injects `<Parameter name="callback_number" value="…">` into the `<Stream>` (:130-132).
2. `app.py:144-166` `/media`: `custom_parameters=start.get("customParameters") or {}` (:164) → CallSession ctor.
3. `session.py:163-165` `start()`: persona filter `persona = {k: v for k, v in custom_parameters.items() if k in known}` where `known` = `llm_json["default_dynamic_variables"]` keys — `callback_number` IS in that dict (`engine/agent/llm.json:17` `"callback_number": ""`), so the filter PASSES it.
4. `state.py:59-64` `initial_state`: persona re-filtered against `DynamicVariables.model_fields` → merged into dvs.
5. Consumed at `builder.py:327` (`attendeePhoneNumber` in `_chain_args`) and the Phase-B chain gate `builder.py:2710-2716` (`dvs.get("callback_number")` required for the booking chain).
Despite the chain existing, the value was EMPTY in dvs on both Oct-6/8 real calls (evidence: traces `152d98c0…` / `be7bb8e7…`).

**Prime suspect (code-level, found this session):** `request.query_params` reads ONLY the URL query string. Twilio voice webhooks deliver `From` in the POST body (`application/x-www-form-urlencoded`), NOT the query string. If Twilio POSTs `/twiml` (its default for voice URLs), `query_params.get("From")` is always `""` → `params_xml` empty → `customParameters` empty → `callback_number` stays `""`. The trace (phase A) must CONFIRM this against the live lane before the wire is written.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Trace BEFORE wire — zero-code phase first | Owner directive 2026-10-10 (why was `<Parameter>` chosen + where does it die) |
| The wire rides the stack branch as its final commit | Owner branching directive (PT-11 in the stack) |
| No prompt changes to compensate | The Intake/Discovery prompts already trust `{{callback_number}}`; the defect is transport, not prompting |
| PT-10 (dv recovery tool) consumes this wire but does NOT ride this branch | PT-10 = own branch post-dictation (wave law) |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Confirmation of where the chain dies (query-params hypothesis vs customParameters casing vs persona filter) | Phase A trace (below) — the lane is the only truth |
| A REAL Twilio test call for phase A (the two Oct calls cannot be regenerated) | Owner dials the lane after the stack's earlier commits are lane-booted (or any lane on the serving build) |
| Canonical `.env` `AUDIO_TRANSPORT=twilio` ratification (owner) | needed for REAL dials; unit/trace work not blocked |

## Environment & Dependencies
- OR lane (the dialing place): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`; lane boot per LANE LAW; webhook `https://voicetest.diallux-ai.site/twiml` → Caddy → lane port.
- Files (phase B, only if the trace confirms the suspected site): `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py` (+ possibly `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` for a mic-bridge equivalent).
- Transcripts/dv dumps: `engine/scripts/lf.py` (Langfuse SDK); ledger per SOP.

## Architecture (the trace plan, phase A — zero-code)
```
A1. Lane boot on OR (stack worktree, any port from the wave's provisional set).
A2. Instrument NOTHING — read what already exists:
    a. curl the TwiML endpoint BOTH ways and diff:
       ssh … "curl -s 'http://127.0.0.1:<port>/twiml?From=%2B13125551234'"            # query-string form
       ssh … "curl -s -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
              --data 'From=%2B13125551234' http://127.0.0.1:<port>/twiml'"            # Twilio's actual form
       → EXPECTATION: form (a) injects <Parameter>, form (b) returns NO Parameter — the bug, proven locally.
    b. Add NOTHING to code; inspect the start frame the lane receives: owner dials the lane once;
       the session log line "call … started" + a one-off dbg dump is NOT allowed (zero-code) — instead pull
       the trace's dynamic_variables output (tracer.finish at session.py:327-338 carries dvs) via lf.py.
    c. Cross-check the serving build's /twiml behavior against Twilio's documented request shape
       (POST form-encoded) — record the WHY of the original <Parameter> choice (Twilio Media Streams
       customParameters = the only channel to pass call-scoped data into the media WS).
A3. Write the verdict to /home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/03_caller_number_trace.md:
    the dead link, the evidence (curl diff + real-call dvs), and the dictated wire.
```

## File Map (phase B — the wire, one commit)
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py` | `/twiml` :128: `from_number = (request.query_params.get("From") or (await request.form()).get("From") or "").strip()` — read the POST body FIRST if the trace confirms (exact order per trace verdict); keep the query-param fallback for manual/curl tests | EDIT (stack branch, commit #5) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_caller_number.py` | pins (below) | NEW (same commit) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | (ONLY if the trace also indicts the persona filter) — no change expected; the filter provably passes `callback_number` | EDIT only on trace verdict |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Commit #5: `iter<NN> PT-11: caller-number wire — /twiml reads Twilio's form-encoded From (trace-verified); <Parameter> injection fires on real calls`.
- NEVER touched: the persona filter semantics (state.py:63-64 stays — it is correct), live agent IDs, the Caddy file (owner box discipline), `/mic/ws` token gate.

## Tasks (in order)
### T1 — Phase A: the trace (zero-code, runs at the TOP of the stack session)
- Goal: the dead link proven with the curl diff + one real dial's dvs dump; verdict file `03_caller_number_trace.md`.
- Verification: the verdict names ONE dead link with two pieces of evidence; the wire edit in T2 maps 1:1 to it.
- Dependencies: stack branch lane-booted on OR (after PT-8/5/6/4 commits); owner availability for one dial.
### T2 — Phase B: the wire (one commit)
- Pins (`test_iter<NN>_caller_number.py`):
  1. `test_form_post_injects_parameter`: FastAPI TestClient POST `/twiml` with form-encoded `From=+13125551234` → TwiML contains `<Parameter name="callback_number" value="+13125551234" />`.
  2. `test_query_param_still_works`: GET `/twiml?From=…` → same injection (back-compat).
  3. `test_no_from_no_parameter`: request without From → NO Parameter element (byte-shape of today's empty case).
  4. `test_param_to_dvs_end_to_end`: scripted ws `start` frame with `customParameters: {"callback_number": "+13125551234"}` → session `initial_state` dvs carry it (the paper chain, pinned so it can never silently rot again).
- Verification: one REAL dial on the lane post-wire: dvs dump shows the caller's number; the booking chain gate (`builder.py:2715`) sees it.
- Dependencies: T1 verdict.
### T3 — ASK (stack-branch close)
- The stack's full ASK includes this PT's trace verdict + wire pins.

## Validation Plan (end-to-end)
1. Suite red set byte-identical + 4 pins green.
2. Real dial: `callback_number` in the trace's `dynamic_variables` output (the exact failure evidence from Oct-6/8, now green).
3. PT-10's design dictation (separate branch) consumes this as the caller-ID fallback source.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Mic-bridge equivalent (browser caller passes their number) | no evidence of need; `/mic/ws` callers are test sessions — add on say-so |
| Storing the number earlier than dvs (e.g. call metadata) | dvs is the single source the prompts + chain + booking already read |
