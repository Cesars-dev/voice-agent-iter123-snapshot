# Wave plan PT-2 — ask-chop: the owner's 3 rules, in code (own branch off PT-1's tip)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: (a) a sentence released by the gate ending in "?" STOPS that round's stream — no trailing speech after the question; (b) tool-continuation rounds speak NOTHING unless new caller input or decisive tool data arrives; (c) the model's history always equals what the caller HEARD — chopped text never enters history, and the model is told what was not spoken so it asks again. ALL THREE IN CODE, never prompt.
- Status: PLAN ONLY (awaits owner GO + the owner's review of the eval; cuts from PT-1's branch tip)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: OWN branch `engine/103-turn-segregation` (reserved name; number ratifies at cut), cut from the PT-1 branch tip.

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-2 specific — OWNER'S 3 RULES (2026-10-09, on record, DO NOT revisit):
1. **Never stay silent** — the chop removes ONLY the post-question tail; caller silence is owned by the PT-68/iter94 pause ladder (`session.py:367-439`, on main, live-validated).
2. **Never stack questions in one turn** — the chop at the FIRST released '?' guarantees one question per round; the continuation gate guarantees no second asking round without new input.
3. **Spoken-only history** — when text is chopped, the model must know it was not spoken, so it asks again; history == what the caller heard.

The evidence: Oct-6 `CA93823104f61c20d6` 09:27:30→09:27:34 — the tool-result continuation round SPOKE AGAIN in the caller's window ("you asked and answered yourself" ON TAPE @09:28:01, the complaint echo-recorded 3×); 09:26:00→09:26:04 — stacked question-turns around the Discovery→Closer transition. The iter68 "chain-link yield" that tried to solve this = the 527-line entangled trap (contact_details loop, total-failure verdict) — NEVER ported; this is a fresh, small build (owner law).

The trap to avoid (named): the iter68 disease was buffering/deferring speech machinery. This design NEVER buffers: the question speaks the instant it always did; only the TAIL after it dies.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| The 3 rules live in CODE (gate + builder + session), never prompts | Owner correction on record: prompts = suggestions, hard gates = code |
| Chop arm written against PT-4's NEW boundary flush | chain supplies it (PT-2 cuts from PT-1's tip which carries the stack incl. PT-4) — watch-point resolved by construction |
| Never-silent is inherited, not rebuilt | the PT-68/iter94 ladder already owns caller silence (one rung per stretch, iter94 guard) |
| PT-3 (transition beat) stays PARKED until this lands + one real call | owner: the state-transition must be written so the beat and the chop do not collide — the collision analysis is in the PT-3 file |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner review of the eval + GO for this branch | master plan ASK (tier-3 gate) |
| "Decisive tool data" list for the continuation gate (candidate below — needs owner ratification) | HITL at the branch's design checkpoint (same pattern as iter87 dictation) |
| Suite baseline (inherited from PT-1's branch gate) | cut-time measurement |

## Environment & Dependencies
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` (one knob), `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md`.
- Evidence: Oct-6 transcript (regenerable: `engine/scripts/lf.py gens 152d98c0c8d73f27680d950f2914e1bb`); current copy `/tmp/opencode/oct6_transcript.txt`.

## Architecture (the three arms)
```
ARM 1 — GATE CHOP (sentence_gate.py):
  ctor gains on_question: Callable[[str], None] | None = None
  NEW per-ROUND chop state: _chop_round: bool = False  (NOT epoch-based — a chop is
    round-scoped; a new round = a new stream feeding cycle)
  in _flush_upto (or at the two flush call sites :198-203 / :111-116): after computing
    the flushed `text`, if not self._chop_round and text.rstrip().endswith("?"):
        self._chop_round = True
        if self.on_question: self.on_question(text)
  in add(): if self._chop_round: return          # the tail dies HERE, unbuffered
  chop reset: state_node signals round start via a new gate method round_reset()
    (clears _chop_round; called by the session on each new ROUND's first token batch
    or by the writer wiring) — plus reset()/close() clear it (teardown).

ARM 2 — SESSION WIRING (session.py):
  SentenceGate ctor call (:212) gains on_question=self._on_round_question
  _on_round_question(text): records on the CURRENT speak clock:
      clock.extra["round_chopped_at"] = text
      self._round_chopped = True   (class-level default False; cleared per round)
  The turn's report carries round_chopped (observability; the "was chopped" signal
    the builder needs rides the writer channel instead — below).

ARM 3 — BUILDER ROUND LOOP (builder.py :2317-2443 + :2521-2533):
  (a) continuation-silence gate, BEFORE the astream (:2317):
        continuation_round = (state.get("rounds_left", 0) < runtime.settings.max_tool_rounds)
        prev_round_asked  = bool(state.get("round_asked"))          # new state key, set below
        new_caller_input  = <user_text changed since turn start>     # turn-scoped compare
        decisive = executed-outcome class of the PREVIOUS round in {"booking ok",
                   "booking abort", "slots landed"}                  # BLOCKED: owner ratifies
        suppress_speech = continuation_round and prev_round_asked and not new_caller_input
                          and not decisive
      when suppress_speech: the round still runs (tools execute — the model must book),
      but its token events are NOT written to the tts_token channel; the round's
      content still enters history (rule 3 needs it flagged, below).
  (b) spoken-only history + the "not spoken" note:
      the session's writer channel is one-way (builder -> session); the reverse signal
      rides the STATE: the session cannot write graph state mid-round — therefore the
      chopped-tail detection ALSO lives builder-side: mirror the '?' detection on the
      SPOKEN stream at the sentence-split loop (:2331-2362): when a flushed spoken
      sentence ends in '?', stop emitting tts_token for the REST OF THE ROUND
      (the builder-side chop — same rule, enforced at the source) and record
      spoken_cutoff = <text upto the question>.
      at updates (:2521-2533):
        if spoken_cutoff is not None:
            updates["assistant_text"] = spoken_cutoff
            the history assistant entry content = spoken_cutoff          (rule 3: history == heard)
            updates["round_asked"] = True
            updates["unspoken_tail"] = content[len(spoken_cutoff):]      (diagnostic only)
      the NEXT round's post-history delta (the rag_delta assembly :2248-2285) prepends,
      when state.get("unspoken_tail"): "NOTE: your previous reply was cut off after
      your question — the caller did NOT hear the rest. Do not repeat what you already
      asked; wait for their answer." (one engine-authored line, NOT a prompt-file edit.)
  (c) gate chop (arm 1) = the belt to the builder's suspenders (arm 3b): the gate kills
      anything that slips past (filler tokens, stream-end flushes). Both must agree on
      '?'-detection; both are pinned.

  ONE knob (SWITCH LAW): ask_chop: bool = True  (config.py; ENV-SWITCHES registered;
  default ON = tested value; false = byte-exact today). The continuation gate rides the
  SAME knob — one switch, one semantic: "one question then yield".
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` | `on_question` ctor param, `_chop_round` state, flush-site '?' detection, add() early-out, `round_reset()` | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | gate wiring :212, `_on_round_question`, per-round chop reset in `_run_turn` | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | spoken-cutoff detection in the sentence loop, suppress_speech continuation gate, history/delta updates, `round_asked`/`unspoken_tail` state keys | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/state.py` | GraphState keys: `round_asked: bool`, `unspoken_tail: str` | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | `ask_chop: bool = True` | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | register `ASK_CHOP` | EDIT (branch docs commit) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter103_ask_chop.py` + `test_iter103_continuation_silent.py` | pins (below) | NEW (branch) |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Branch message: `iter103 PT-2: ask-chop — the 3 rules in code (gate chop, continuation silence, spoken-only history)`.
- NEVER touched: the pause ladder (`session.py:367-439`), the iter93 epoch machinery, the dedupe windows (they operate BELOW the chop — chopped text never reaches them), prompts/KB files (the engine-authored delta note is code, not a prompt edit).

## Tasks (in order)
### T0 — Design checkpoint (HITL, ~10 min)
- Present the two open lists to the owner: (1) the decisive-tool-data set (candidate: booking ok / booking abort / slots landed — i.e. outcomes that CHANGE what the caller must hear next); (2) the delta-note wording. Ratify, then build.
### T1 — Gate chop + builder cutoff (one commit)
- Pins (`test_iter103_ask_chop.py`):
  1. `test_question_stops_round_stream`: streamed round `"...how many calls a week are you missing? <300 more chars>"` → spoken output ENDS at the question; zero tail chunks (both the builder channel AND the gate pin).
  2. `test_chopped_tail_never_in_history`: the round's history assistant entry == text upto the question; `unspoken_tail` recorded; next-round delta carries the NOTE.
  3. `test_never_silent_inherit`: caller answers nothing → the PT-68 ladder fires its ONE nudge (existing behavior pinned unchanged — the chop must not touch it).
  4. `test_flag_off_byte_parity`: `ask_chop=False` → the streamed output for pin-1's input is byte-identical to the pre-branch behavior (rollback proof).
  5. `test_no_question_no_chop`: a statement-ending round streams whole (no false chops).
  6. `test_chop_reset_per_round`: round 2 of the turn (new stream) starts unchopped.
- Dependencies: PT-1 branch tip (chain law).
### T2 — Continuation silence (one commit)
- Pins (`test_iter103_continuation_silent.py`):
  1. `test_tool_continuation_silent`: the Oct-6 shape — a turn whose round 1 asked "?" then ran `calculate_monthly_leak`; round 2 (tool result, no new caller input, not decisive) speaks NOTHING (zero tts_token writes), tools still execute, history records the round.
  2. `test_new_caller_input_unmutes`: new `user_text` in the turn → continuation round speaks normally.
  3. `test_decisive_outcome_speaks`: booking-ok outcome → the continuation round SPEAKS (the caller must hear the confirmation).
  4. `test_replay_0927_window`: the Oct-6 09:27:30→09:27:34 window replayed scripted → the second round adds ZERO speech (the on-tape complaint shape, killed).
- Dependencies: T1.
### T3 — Gate + ASK
- Full suite + the data-gate replays; battery on the OR lane (mic scripted caller through the frozen driver per the SOP); ASK lists every gate number. One REAL call after merge (owner) re-verifies live before PT-3 is decided.

## Validation Plan (end-to-end)
1. Suite red set byte-identical + 10 pins green.
2. Oct-6 replays: 09:27:30→34 window adds zero speech; 09:26:00→04 stacked-question shape collapses to one question.
3. Rule audit on a scripted battery: (R1) zero dead-air regressions (ladder spans unchanged); (R2) zero multi-question rounds; (R3) every history assistant entry == its round's spoken bytes.
4. Flag-off = byte-exact today (rollback = one env line).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| PT-3 transition beat | PARKED; decided after PT-1 + PT-2 + one real call (collision analysis in `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-3_transition_beat_PARKED.md`) |
| The merged-turn trim hook (>2 questions in one MODEL turn → trim) | superseded by rules 1+2: the chop makes stacking structurally impossible; revisit only if a real call defeats it |
| Cross-round question dedupe (iter59 stem window) | already on main, unchanged, operates below the chop |
