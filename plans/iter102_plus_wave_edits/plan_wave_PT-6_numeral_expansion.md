# Wave plan PT-6 — numeral expansion before TTS ($ amounts, dates, times; runs 3rd inside the stack branch)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: deterministic expansion of digits in spoken text right before the TTS socket — `$1,250` → owner-picked wording, dates `04/20/2026` → words, times. Kills the fast-number disease (FIND-40: the Oct-6 caller ON TAPE "I didn't get the number. Can you slow down?" @09:26:38, agent conceded too fast).
- Status: PLAN ONLY (awaits owner GO; runs as commit #3 of the wave stack branch)
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`
- Branch: THE STACK BRANCH — this PT is its THIRD commit.

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-6 specific: the normalize layer is `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/normalize.py` — `normalize_for_tts()` (:57-102) already handles markdown/emoji strip, phone-shaped strings (`tts_phone_style`), bare 5+ digit runs, mixed-alnum UIDs, terminal punctuation. It runs per flushed sentence in `session._speak_chunk` (`session.py:1056-1057`, gated `settings.tts_normalize` = True default) — µs of regex, never touches history/dvs/prompts. MISSING arms: `$` amounts, dates, times — the leak-math money line and slot times ride the digit-run rule at best (a "$1,250" reads as "one comma two five zero" class garbage or machine-fast digits).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Expansion lives in `normalize_for_tts` (speech-only layer) | The module's own law: never to history, never to dvs, never to the prompt — the model's output is untouched |
| Deterministic pure-regex + mapping tables — no LLM, no API | Module doctrine ("zero latency, zero API calls"); FIND-40 is a pacing/rendering defect, not a content defect |
| Wording = owner EAR PICK during verification, not before | Owner verdict on record: pick while listening, e.g. "$1,250" → "twelve fifty dollars" vs "one thousand two hundred fifty dollars" |
| Phone-style rules UNCHANGED | The existing phone/digit-run/UID arms already pass batteries; numerals are a NEW arm ordered BEFORE the digit-run arm (so "$1,250" never reaches the bare-digit splitter) |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner wording pick: "$1,250" style; date style ("April twentieth twenty twenty-six"); time style ("two thirty PM" vs "fourteen thirty") | Owner ear at verification — pins written against the chosen wording AFTER the pick; until then the plan's tables carry PLACEHOLDER wording marked UNKNOWN |
| Owner GO (stack branch already carries PT-8+PT-5) | master plan ASK |

## Environment & Dependencies
- Files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/normalize.py` (only engine file), `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_numerals.py`.
- No new packages, no new Settings fields (rides `tts_normalize: bool = True`, config.py:383; `tts_phone_style` config.py:384 untouched).

## Architecture (arm order inside `normalize_for_tts`)
```
current order (normalize.py:73-101):
  1. strip markdown/emoji, collapse whitespace
  2. phone-shaped (per tts_phone_style)
  3. bare 5+ digit runs
  4. mixed alnum UIDs
  5. terminal punctuation

new order after this PT:
  1. strip markdown/emoji, collapse whitespace
  2. NEW: $-amount arm        "$1,250" / "$19.99" / "$28,100" → words
  3. NEW: date arm            "04/20/2026", "4/20/26" → words
  4. NEW: time arm            "3:00pm", "14:30", "2:45 PM" → words
  5. phone-shaped (per tts_style)   ← unchanged
  6. bare 5+ digit runs             ← unchanged (now only sees non-$ non-date digits)
  7. mixed alnum UIDs               ← unchanged
  8. terminal punctuation           ← unchanged
```
Placement law: the numeral arms run BEFORE phone/digit-run so a matched money/date/time token is consumed whole; a NON-matching token falls through byte-untouched to the existing arms (parity for everything that isn't money/date/time).

Implementation shape (deterministic tables):
```python
_ONES = ["zero","one",...,"nine"]; _TEENS = [...]; _TENS = [...]
def _number_to_words(n: int) -> str: ...          # 0-999,999; standard decomposition
_MONEY_RE  = re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b")
_DATE_RE   = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b")
_TIME_RE   = re.compile(r"\b(\d{1,2}):(\d{2})\s?(am|pm|a\.m\.|p\.m\.)?\b", re.I)
_MONTHS = ["January",...]
```
Wording inside each substitution = the owner pick (BLOCKED above); the STRUCTURE (which regex, which order, word-count decomposition) is fixed by this plan.

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/normalize.py` | three new arms + `_number_to_words` + regex tables, inserted between the whitespace step (:77) and the phone_style branch (:79) | EDIT (stack branch, commit #3) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter<NN>_numerals.py` | pins (below) | NEW (same commit) |

## Deploy Rules
- Shared wave deploy rules = master plan §Deploy Rules. Commit #3: `iter<NN> PT-6: numeral expansion before TTS — $ amounts, dates, times (owner-worded; speech-only layer)`.
- NEVER touched: `session.py` wiring (the arm rides the existing `tts_normalize` call site — zero session changes), phone/digit-run/UID arms, history/dvs/prompts, `tts_phone_style`.

## Tasks (in order)
### T1 — Expansion tables (one commit)
- Goal: the three arms with the owner's picked wording (get the pick FIRST — HITL at the stack-branch GO or at verification; if not yet picked, build with the wording as a single `_WORDING` dict so the pick is a 3-line change, and mark the pins xfail until picked).
- Pins (`test_iter<NN>_numerals.py`):
  1. `test_money_expansion`: "$1,250 a week" → expanded words + " a week" preserved (the Oct-6 leak-math line shape).
  2. `test_date_expansion`: "04/20/2026" → month-day-year words.
  3. `test_time_expansion`: "2:45 PM" / "14:30" → words.
  4. `test_order_stable_deterministic`: same input → same output across 100 calls; input order in the sentence preserved (no reordering around matched tokens).
  5. `test_terminal_punctuation_preserved`: expansion never eats the sentence-final period.
  6. `test_fallthrough_parity`: inputs with NO money/date/time tokens produce byte-identical output to the pre-change module (snapshot a corpus: the existing test_delivery/normalize fixtures).
  7. `test_history_untouched`: (guard pin) `normalize_for_tts` output never feeds `assistant_text` — assert via the existing speech-only wiring (the module docstring contract).
- Dependencies: stack branch @ PT-5 commit; owner wording pick (or the `_WORDING` placeholder route).
### T2 — Ear verification + ASK
- EL-side A/B on the lane: synthesize "…$1,250 a week…" raw vs expanded; owner listens; wording confirmed or adjusted (3-line change + pin re-run). ASK carries: suite delta, pin count, the owner's ear verdict.

## Validation Plan (end-to-end)
1. Suite red set byte-identical + 7 pins green (wording pinned to the owner pick).
2. Oct-6 leak math line render check: the exact sentence from trace `152d98c0c8d73f27680d950f2914e1bb` t~09:26 replayed through `normalize_for_tts` → fully worded output (evidence into `research/surgeon/iter102-fix-wave/`).
3. Fall-through parity: zero change for any sentence without money/date/time (pin 6 = the regression gate).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Phone-number word expansion | already owned by `tts_phone_style` ("digits" default reads slow digit-by-digit — that behavior is correct and untouched) |
| Ordinals ("21st"), percentages ("50%") | not in evidence; add on a future say-so if a real call shows the need |
