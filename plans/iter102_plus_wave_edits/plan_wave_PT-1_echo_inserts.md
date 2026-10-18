# Wave plan PT-1 — echo inserts: one user entry per utterance (FIND-37, P0; own branch off the stack tip)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: the confirmed-EOT final transcript REPLACES the eager fragment in history — the model's history sees exactly ONE user entry per utterance (the final). Evidence: Oct-8 `CAcf047fe3fd9075` echo shapes at 22:48:43 / 22:48:57 / 22:50:53 — one utterance → 2–3 history variants (FIND-37, P0).
- Status: PLAN ONLY (awaits owner GO; cuts from the STACK BRANCH TIP after the stack's five commits are tested)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: OWN branch `engine/102-echo-accounting` (reserved name; number ratifies at cut), cut from the stack branch tip. PT-3's fate is decided AFTER this verifies.

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-1 specific — the mechanism, read out of origin/main 2026-10-10 (this is the root cause, verified end-to-end):
1. EagerEOT fires `_on_eager_eot(transcript)` (session.py:621-698): snapshots `_eager_transcript = transcript` (:636), spawns `_run_turn(fragment)` (:698). That run's graph invoke passes through `ingest` (builder.py:2804-2843) which APPENDS `{"role":"user","content":fragment}` to history (:2825-2830).
2. Final EOT arrives `_on_eot(final)` (session.py:459-560). Adopt happens ONLY when `self._eager_transcript == transcript` (:472-474) — the Deepgram no-resume contract. When the final GREW (fragment ≠ final): the eager task is cancelled (:507) BUT the ingest update already committed (astream `updates` mode + MemorySaver checkpoint — ingest ran to completion before the cancel) → **the fragment is already in history**.
3. The fresh `_run_turn(final)` (:559-560) → `ingest` again: the idempotent guard (:2825-2830) skips the append ONLY when the last user entry is BYTE-IDENTICAL to the new text. `final ≠ fragment` → **a SECOND user entry appends**. History now holds the caller twice (fragment + final) — the echo the model then parrots back (the Oct-8 shapes; `lf.py pair` counts them as variant-aware echo inserts).
4. The 3-variant shapes (22:50:53) = the same dance repeated across a resume cycle.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| REPLACE semantics: the final transcript replaces the eager fragment entry within the turn | Owner-ratified row text: "the model's history sees ONE user entry per utterance" |
| Byte-identical final still SKIPPED (idempotent guard intact) | The adopt path never re-runs; the guard stays the first line of defense |
| The fix is CODE (session + ingest + state), not prompts | Owner: hard gates live in code |
| PT-1 runs BEFORE PT-2 in the chain; PT-3's fate decided after PT-1 verifies | Owner directives 7 (2026-10-10): verify PT-1 → decide PT-3; PT-2's spoken-only history builds on one-entry-per-utterance |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO to cut this branch off the stack tip | master plan ASK |
| Suite baseline (inherited from the stack branch gate — re-measure at this branch's cut) | cut-time measurement |

## Environment & Dependencies
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/state.py` (history reducer), `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (ingest), `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` (the growth-rerun payload).
- `lf.py pair` (echo accounting SDK) is ON MAIN (cherry-picked from `engine/iter97-research-adaptation` @ `c877e51` by owner order 2026-10-10 — the wave's echo gates run it from any main checkout).
- Evidence: `research/surgeon/iter102-fix-wave/00_pt_deepdive.md` §B + the two transcripts (regenerable via `engine/scripts/lf.py gens be7bb8e7404b76d2c0b50ddc9636e4d2`).

## Architecture (the fix design — replace via a history reducer extension)
The `history` field is `Annotated[list[dict], operator.add]` (state.py:29) — append-only; ingest cannot "un-append". The replace semantic therefore needs the reducer to understand ONE new patch shape:

```
state.py:
  def merge_history(a: list[dict] | None, b: list[dict] | None) -> list[dict]:
      """operator.add + the PT-1 replace marker: a patch entry
      {"role": "user", "content": X, "supersedes": True} pops the LAST user
      entry from `a` before appending itself (X replaces the eager fragment).
      Every other patch shape = exact operator.add (byte-identical semantics)."""
      out = list(a or [])
      for m in (b or []):
          if m.get("role") == "user" and m.pop("supersedes", False) and out \
                  and out[-1].get("role") == "user":
              out.pop()
          out.append(m)
      return out
  # GraphState: history: Annotated[list[dict], merge_history]

builder.py ingest (:2804-2843):
  read the new payload flag: supersede = bool(state.get("user_text_supersedes"))
  the guard becomes:
      last_user = <last user entry>
      identical = text and last_user and last_user.get("content") == text
      if supersede and not identical and last_user is not None:
          patch["history"] = [{"role": "user", "content": text, "supersedes": True}]
      elif not identical:
          patch["history"] = [{"role": "user", "content": text}]        # today's line, unchanged

session.py _on_eot growth path (:505-560):
  before spawning the fresh run, capture the fragment:
      self._supersede_fragment = self._eager_transcript      # set on the RERUN path only
  and _run_turn's payload gains the flag when set (cleared after use):
      payload = {"user_text": transcript}
      if self._supersede_fragment is not None:
          payload["user_text_supersedes"] = True
          self._supersede_fragment = None
  GraphState (state.py:22-51) gains the pass-through key: user_text_supersedes: bool
```
Why this shape and not "don't write the fragment at all": the eager round NEEDS the fragment in its LLM payload to answer speculatively — suppressing the write would blind the eager turn. The replace happens only on the growth-rerun path, where the fragment is provably the immediately-preceding user entry (the eager run wrote it and nothing else writes user entries mid-turn).

Safety rails (both pinned): the reducer pops AT MOST one entry and ONLY a trailing user entry — a `supersedes` patch can never eat an assistant/tool message; a second consecutive `supersedes` with no user entry above it degrades to a plain append (never a no-op write).

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/state.py` | `merge_history` reducer + `user_text_supersedes: bool` GraphState key | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | ingest guard extension (:2825-2830) — the supersede arm | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | `_on_eot` growth path sets `_supersede_fragment`; `_run_turn` payload carries the flag | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter102_echo_accounting.py` | pins (below) | NEW (branch) |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Branch message: `iter102 PT-1: echo accounting — confirmed-EOT final supersedes the eager fragment in history (one user entry per utterance)`.
- NEVER touched: the adopt path (byte-identical case — no rerun, no flag), `_on_turn_resumed` (its invalidate already handles the cancelled eager generation's GATE artifacts; only the HISTORY entry needed this fix), the ingest bookkeeping keys.

## Tasks (in order)
### T1 — The replace path (one commit, ~3 hunks + pins)
- Pins (`test_iter102_echo_accounting.py`):
  1. `test_growth_rerun_single_entry`: the Oct-8 22:48:43 shape — eager fragment `"Yeah. Exactly. That I'm missing business"` runs a turn, then EOT final `"Yeah. Exactly. That I'm missing business. So how much…"` reruns → history holds EXACTLY ONE user entry, content == the final.
  2. `test_adopt_unchanged`: fragment == final (adopt path) → no rerun, no second entry, no flag consumed (the guard's identical-skip still fires).
  3. `test_reducer_replaces_only_trailing_user`: `merge_history([user,assistant,user],"[user supersedes]")` → [user, assistant, user_new]; a supersedes patch with a trailing ASSISTANT entry degrades to append (nothing popped).
  4. `test_plain_append_untouched`: ordinary patches (assistant, tool, user) merge byte-identically to `operator.add` (the parity pin — every existing writer is unaffected).
  5. `test_three_variant_shape`: two consecutive growth reruns (the 22:50:53 3-variant shape) → still exactly ONE user entry (the second supersede pops the first final, appends the second).
  6. `test_history_window_renders_final`: `_build_messages` on the post-replace state shows the final text exactly once (the model's view pin).
- Commands: cut `engine/102-echo-accounting` from the stack tip on OR (`bash scripts/new_lane.sh`), FI worktree, targeted pins then full suite gate.
- Dependencies: stack branch green (master plan chain law).
### T2 — Data gate replay + ASK
- Replay the Oct-8 window scripted: 3 echo shapes → 0 variant inserts; `lf.py pair` on a scripted mic run reports echo count 0 (runs from any main checkout now that the SDK is on main).
- ASK text: suite delta, 6 pins, replay numbers. **PT-3's fate question rides this ASK** (owner directive 7).

## Validation Plan (end-to-end)
1. Suite red set byte-identical (stack baseline) + 6 pins green.
2. Echo count 0 on the replayed shapes; history == spoken-heard contract: every user entry corresponds to exactly one caller utterance.
3. Chain position verified: this branch contains the stack's five commits (it cut from the tip) — the suite run proves the combination.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| PT-3 transition beat decision | owner decides at this branch's ASK (collision analysis lives in the PT-3 file) |
| Cross-turn dedupe of near-identical caller texts | different disease (STT fragmentation / FIND-39) — owner-deferred Deepgram EOT knob territory |
