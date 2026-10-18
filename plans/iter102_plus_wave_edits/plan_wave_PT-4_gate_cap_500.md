# Wave plan PT-4 — gate cap 500, "a cap, not a rule" (runs 4th inside the stack branch)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: SentenceGate never trims spoken sentences mid-phrase: flush at natural sentence boundaries (already the mechanism); `_FLUSH_LEN` 140 → 500 promoted to a Settings field per SWITCH LAW. 500 = runaway safety valve ONLY. Kills FIND-38: 11 of 23 turns of `CAcf047fe3fd9075` cut at exactly char 140 mid-clause.
- Status: PLAN ONLY (awaits owner GO; runs as commit #4 of the wave stack branch)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: THE STACK BRANCH — this PT is its FOURTH commit.

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-4 specific: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` as read 2026-10-10 on origin/main — `_FLUSH_LEN = 140` (:46), `_MIN_LEN = 25` (:47), `_IDLE_FLUSH_MS = 150` (:48). The gate ALREADY flushes at natural sentence boundaries: on every `add()` (token deltas), when buffer ≥ `_MIN_LEN` and a `[.!?](\s|$)` match exists, it flushes upto the sentence end (:198-201); the hard cut at `_FLUSH_LEN` (:202-203) fires mid-word/mid-clause whenever a single sentence runs past 140 chars — THE disease (the Oct-8 T20 233-char single-sentence shape got chopped at 140 eleven times across the call). Same hard-cut exists on the held-release path (`release()`, :111-116). An idle-flush (150 ms without a token) also exists (:308-318) so half-sentences still voice.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| "A cap, not a rule" — the model decides its output; 500 is a runaway valve only | Owner verdict on FIND-38 (the 11 mid-clause cuts at exactly 140 were the disease) |
| Promotion to a Settings field `gate_flush_len` (code default **500** = tested value) | SWITCH LAW rule 4: load-bearing switches carry code defaults matching the tested-on value; `_FLUSH_LEN` constant stays as the no-arg fallback for direct constructions (tests) |
| Sentence-boundary + idle-flush logic UNTOUCHED | They are already correct; only the hard-cap number changes |
| PT-2's future chop arm is written against THIS commit's boundary flush | Chain law handles it (PT-2 cuts from PT-1's tip which carries this commit); recorded as the dependency edge |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO (stack branch already carries PT-8+PT-5+PT-6) | master plan ASK |

## Environment & Dependencies
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` (constructor wiring), `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` (Settings field), `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` (registration), `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_gate_cap.py`.
- No new packages.

## Architecture (the exact diff shape)
```python
# sentence_gate.py
- _FLUSH_LEN = 140
+ _FLUSH_LEN = 140          # fallback only — direct constructions (tests) keep today's default
+                           # production value = Settings.gate_flush_len (SWITCH LAW)

  class SentenceGate:
-     def __init__(self, on_sentence, managed: bool = False):
+     def __init__(self, on_sentence, managed: bool = False, flush_len: int | None = None):
+         self._flush_len = flush_len if flush_len and flush_len > 0 else _FLUSH_LEN
  # then EVERY `len(self._buffer) >= _FLUSH_LEN` site reads self._flush_len:
  #   add()      :202   →  if len(self._buffer) >= self._flush_len
  #   release()  :115   →  if len(self._buffer) >= self._flush_len

# session.py:212
- self.gate = SentenceGate(self._speak_chunk, managed=...)
+ self.gate = SentenceGate(self._speak_chunk, managed=...,
+                          flush_len=self.settings.gate_flush_len)

# config.py (Settings, near the tts_gate_* fields :207-208)
+ gate_flush_len: int = 500     # PT-4: hard-cap safety valve; sentence boundaries flush first
```
That is the WHOLE change: boundary flush (MIN_LEN 25 + sentence-end) and idle flush (150 ms) stay byte-identical; only the runaway threshold moves 140→500 and becomes env-overridable (`GATE_FLUSH_LEN` env var — registered in ENV-SWITCHES §4; agents never edit `.env`).

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` | ctor param + both `_FLUSH_LEN` sites read `self._flush_len` (sites :115 and :202) | EDIT (stack branch, commit #4) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | gate construction :212 passes `flush_len` | EDIT (same commit) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | `gate_flush_len: int = 500` field | EDIT (same commit) |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | register `GATE_FLUSH_LEN` (default 500; note: 140 restores legacy behavior) | EDIT (same commit or the stack docs commit) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_gate_cap.py` | pins (below) | NEW (same commit) |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Commit #4: `iter<NN> PT-4: gate cap 500 — _FLUSH_LEN promoted to Settings.gate_flush_len (a cap, not a rule; boundary+idle flush untouched)`.
- NEVER touched: `_MIN_LEN`, `_IDLE_FLUSH_MS`, the epoch/hold machinery (iter93), the sender queue, `tts_gate_fast_first_flush` (stays False per PT-71 lesson).

## Tasks (in order)
### T1 — The promotion (one commit)
- Pins (`test_iter<NN>_gate_cap.py`, gate driven directly with scripted token streams):
  1. `test_233char_single_sentence_no_mid_clause_cut`: the Oct-8 T20 shape — a 233-char single-sentence stream (from `/tmp/opencode/call_cf047_transcript.txt`, regenerable via `engine/scripts/lf.py gens be7bb8e7404b76d2c0b50ddc9636e4d2`) → under `gate_flush_len=500` the sentence flushes WHOLE at its end (or at idle); ZERO cuts inside a clause.
  2. `test_flag_140_byte_parity`: with `gate_flush_len=140` (Settings-pinned), the flush sequence reproduces TODAY's behavior exactly — feed the same 233-char stream, assert chunk boundaries == the current-constant behavior (snapshot pin: the 140-cut lands at char 140 as on the real call).
  3. `test_runaway_valve_still_fires`: a 600-char no-punctuation stream → exactly one flush at 500 (the valve) + remainder at end/idle.
  4. `test_env_override`: pydantic Settings with `GATE_FLUSH_LEN=200` env → gate sees 200 (SWITCH LAW proof).
  5. `test_no_arg_ctor_fallback`: `SentenceGate(cb)` (no flush_len) → `_flush_len == 140` (tests/uniform default unchanged).
  6. `test_release_path_respects_cap`: the held-release path (:111-116) flushes under the same cap (drives `hold()`→`add()`→`release()` with a long held buffer).
- Verification: replay ALL 23 spoken texts of CAcf047 through the gate sim (the eval's data gate): 11 mid-clause cuts → 0 at cap 500. First-flush latency unchanged on sentence-boundary inputs (the first sentence still leaves at MIN_LEN 25 + sentence-end — unchanged path).
- Dependencies: stack branch @ PT-6 commit.
### T2 — ASK
- ASK text: suite delta, 6 pins, the 23-text replay table (11→0), parity pin proof.

## Validation Plan (end-to-end)
1. Suite red set byte-identical + 6 pins green.
2. CAcf047 23-text gate simulation: zero mid-clause cuts (evidence into `research/surgeon/iter102-fix-wave/`).
3. No prompt/KB/env changes; ENV-SWITCHES row added; rollback = `GATE_FLUSH_LEN=140` (one env line) or revert the commit.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Clause-boundary (`,` `;` `—`) intermediate flushes | owner's wording is sentence boundaries only; clauses re-enter only if a real call shows a >500-char no-sentence monster |
| First-flush acceleration | owned by `tts_gate_fast_first_flush` (False by law, PT-71) — not this PT |
