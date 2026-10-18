# 01 — AUDIT — iter70 speech fixes (T2 pause re-prompt / T3 transition beat / T4' same-turn jaccard dedupe / T4p prompt wording / T5 observability)

Procedure: `tasks/surgeon/iter70-speech-fixes/` · Audit date: 2026-09-23
Plan under execution: `plans/plan_v5_iter70_speech_fixes_merged.md` (committed main `ced8538`)
Code base audited: branch `engine/iter70-speech-fixes` @ `2d9385d`, worktree `/tmp/opencode/wt-iter70`
(`git diff 2d9385d ced8538 -- engine/` is EMPTY — main tip is docs-only ahead; engine code identical.)

---

## 0. Ground truth verified (environment)

| Item | State | Evidence |
|---|---|---|
| Branch + worktree | LIVE, clean | `git -C /tmp/opencode/wt-iter70 status` clean @ `2d9385d` |
| Worktree `.venv` | Symlink → main `engine/.venv` (3.12.3) | `readlink` verified |
| Worktree `.env` | Voice LAW knobs present: `TTS_PROVIDER=cartesia` (L34), `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` (L30), `TTS_GATE_FAST_FIRST_FLUSH=false` (L36), `TTS_DEDUPE_SEMANTIC=false` (L52) | grep verified |
| Suite runs in worktree | `pytest tests/test_iter43_prompts.py tests/test_dedupe_window.py -q` → 10 passed | run 2026-09-23 |
| Lane `diallux-8024.service` | active (systemd --user) | `systemctl --user is-active` |
| Parked branches | `engine/iter68-speech-flow` @ `cc34343`, `engine/iter68-speech-lite` @ `95f7ace` — untouched, read-only refs | `git branch -a` |
| Main checkout | `ced8538`, one PRE-EXISTING uncommitted mod: `docs/Testing_guidelines/MIC-CALL-ANALYSIS-SOP.md` + untracked `tasks/surgeon/iter68-speech-flow/` — DO NOT TOUCH | `git status` |
| Reference commits | `651e567` (lite T3, +75/-3), `22e6f88` (T2 transition beat, +228/-17), `c6159ce` (T1 observability), `c3022c3` (T3 orig) — all read in full | `git show` |

---

## 1. T2 — Pause re-prompt (PT-68) — audit of the touch surface

### session.py (`engine/diallux/media/session.py`, 889 lines) — EXISTS / MISSING

| Anchor | Line(s) | State |
|---|---|---|
| `_run_turn(self, transcript: str)` | 638 | EXISTS, **NO `extra_payload` param** — the plan's `_run_turn("", extra_payload={"pause_reask": True})` call shape does not compile against today's signature. Reference 651e567 adds `extra_payload: dict | None = None` + `payload.update(extra_payload)` (2 lines, L649-651 region). |
| Payload build | 645-648 | `payload = {"user_text": transcript}` + `_initial_payload` on first turn. Re-ask turn is never `_first_turn` (greeting never runs `_run_turn`). |
| Turn completion → late report | 663-674 | `gate.end_of_turn()` → report → `create_task(self._late_turn_report(clock))`. |
| `_late_turn_report` | 676-717 | Waits ≤~3s (20×0.15s) for `t_audio_out` drain, sends mark frame, aget_state (ended check / `_turn_state` / `_turn_dvs`). **Reference arms the timer AT THE END of this method** (= "after the agent turn drains"). Cancelled turns (barge-in/exception) never reach here → never arm. Correct semantics. |
| `_on_start_of_turn` (disarm point) | 583-606 | Cancels running turn on barge-in, gate reset, TTS cancel, clear. Reference inserts `_cancel_silence_reask()` after the clear send (L598 region). |
| `stop()` | 273-311 | Reference inserts `self._cancel_silence_reask()` right after `_turn_task.cancel()` (L278 region). |
| `__init__` attrs | 104-140 | Class-level defaults exist for no-`__init__` tests (L67-74). New `_pause_reask_task` needs a class-level `None` default too (same pattern as `_eager_transcript`). |
| Greeting | 256-271 | Spoken via `tts.speak` directly, NOT `_run_turn` → **no pause timer after the greeting** (matches reference; owner ear-check is "answer a question, go silent ~11s"). |

### builder.py — ingest guard (the no-empty-user-message shape)

`ingest` at builder.py:2716-2755. Current append guard (L2737-2742):
```python
text = state.get("user_text", "")
last_user = next((m for m in reversed(state.get("history", []))
                  if m.get("role") == "user"), None)
if not (text and last_user is not None
        and last_user.get("content", "") == text):
    patch["history"] = [{"role": "user", "content": text}]
```
**FLAW if unchanged:** with `text=""` this appends `{"role":"user","content":""}` — an EMPTY user message in history (the exact thing the plan forbids: "no empty user message in history"). Reference 651e567 fix (builder.py L2802-2812 region):
```python
reask_turn = bool(state.get("silence_reask"))
patch["silence_reask"] = reask_turn
...
if reask_turn:
    pass
elif not (text and last_user is not None and ...):
    patch["history"] = [...]
```
(renamed `pause_reask` for iter70).

### state.py — MISSING
`GraphState` (state.py:22-51) has NO `pause_reask` field. LangGraph builds channels from the TypedDict — ingest writing an undeclared key breaks. Reference (lite branch state.py:36) declares `silence_reask: bool`. iter70 adds `pause_reask: bool` (same line region).

### builder.py — re-ask round routing
- entry_lite guard at builder.py:1803-1808 — reference adds `and not state.get("silence_reask")` (re-ask round is ALWAYS heavy: needs full state prompt + directive). Without it: a re-ask arriving right after a transition turn would render a speech-only entry_lite ack with no directive.
- Directive rides the post-history delta: builder.py:2229-2234 (`elif runtime.settings.state_in_delta and not lite:` → `if state_delta_block: rag_delta = state_delta_block + rag_delta`).
  **FLAW IN THE REFERENCE (found in audit):** 651e567 nests the directive append INSIDE `if state_delta_block:` — when ALL dvs are empty (`_state_block` returns "", builder.py:1726-1727), the directive is silently LOST. Re-implementation must append the directive to the delta regardless of `state_delta_block` emptiness (see 02 action plan).
- Directive text (reference, verbatim): `"THIS ROUND: the caller has gone SILENT after your last question. Re-ask it ONCE — shorter, warmer, differently worded (never the same sentence). Then stop and listen. Do not call any tool this round."`

### config.py — MISSING
No `pause_reask` / `pause_reask_ms` knobs (plan: `pause_reask=True`, `pause_reask_ms=10000` — owner "~10s", NOT lite's 2000).

### Re-ask turn dedupe safety (verified SAFE)
Ingest resets `tts_sentence_window: []` (builder.py:2734) every turn — the re-ask sentence is a NEW turn, never deduped against the original question (cross-turn re-asks stay audible — the iter59 disaster cannot recur structurally).

---

## 2. T3 — Transition beat / silent acks (PT-70)

### builder.py one-trip routing — EXISTS (old shape)
`route_after_deterministic` builder.py:2784-2803:
```python
if self.settings.one_trip and executed and all(
        FIRE_AND_FORGET.match(t["name"])
        or (t["name"].startswith("transition_to_")
            and t.get("status") == "ok")
        for t in executed):
    if state.get("round_spoke"):
        return "finalize"      # ← flat ack ("Makes sense — …." + ok transition) finalizes HERE = dead air
```
The flat-ack finalize is the bug PT-70 describes. Reference 22e6f88 replaces the inner check with:
```python
if state.get("round_spoke") and (
        state.get("turn_asked")
        or not any(t["name"].startswith("transition_to_")
                   for t in executed)):
    return "finalize"
if not state.get("round_spoke"):
    pass        # silent round: today's loop/force-speech path
elif not any(t["name"].startswith("transition_to_")
             and t.get("status") == "ok" for t in executed):
    return "finalize"
# else: flat transition ack -> fall through to the continuation round
```
Behavior delta vs today (verified by reading both): ONLY the `round_spoke + ok-transition + !turn_asked` case changes (finalize → destination continuation round). Silent rounds, bookkeeping-only rounds, and asked transitions are byte-identical behavior. The continuation round is the EXISTING `entry_lite` ack round (builder.py:1803-1808 trigger: state changed vs `_prev_round_state`) — speech-only, bounded to ONE round (a pure-speech round finalizes via `after_state`, builder.py:2770-2771; it cannot loop).
PhaseB chain transitions are UNAFFECTED (`engine_fired` branch at 2787-2788 returns before the one-trip block).

### `turn_asked` flag — MISSING
- state.py: no `turn_asked` field (22e6f88 adds `turn_asked: bool` next to `round_spoke`).
- state_node: seed `turn_asked = bool(state.get("turn_asked"))` near the window seed (builder.py:2259-2267 region); set `True` when a FLUSHED, SPOKEN sentence contains "?" — at both window-append sites: mid-stream (builder.py:2354-2361) and stream-end (builder.py:2440-2447). Post-filter truth: dropped (sanitize/exact/semantic) sentences never set it — dedupe-mute cannot fake "asked".
- `updates["turn_asked"] = turn_asked` in the updates dict (builder.py:2469-2481).
- ingest reset `"turn_asked": False` (builder.py:2722-2736 patch dict).

### Prompts — MISSING the directives (current state read in full)
- Intake.md Critical Rules L48-52: no turn-end/transition-ack lines.
- Discovery.md Critical Rules L52-62: none.
- Closer.md Critical Rules L99-105: none ("Closing the beat" L74-75 already says "Always end your turn with a question" for the math phase only).
- Offer.md Critical Rules L53-58: none.
- Reference 22e6f88 directive lines (verbatim, to re-apply):
  1. `Every turn ends with a question to the caller — never a flat statement.` (Intake + Discovery + Closer + Offer)
  2. `When a stage transition just moved you here, your ack ends with EITHER the next scripted question (if it fits the live conversation) OR one short contextual question that keeps the flow — never a flat ack.` (Discovery + Closer + Offer)
- 22e6f88 ALSO added a third line to Discovery only: `First time a company name comes up, spell it back letter-by-letter and get confirmation ("Everlast — E-V-E-R-L-A-S-T, right?") — exact names only.` — **OUT of merged-plan scope** (not a transition-ack directive). EXCLUDE unless owner asks.

### llm.json — parity state (MEASURED, important)
| State | .md == llm.json state_prompt? |
|---|---|
| Offer | YES (byte-identical, 3774) |
| contact_details | YES (5145) |
| ConfirmSlots | YES (4166) |
| Intake | **NO** (md 2992 vs emb 2815) |
| Discovery | **NO** (5656 vs 5508 — md has the `#[refer pain-points-kb …]` inline tag, llm.json does not) |
| Closer | **NO** (5794 vs 5710) |
| VerifyLead / Booking / Closing | NO (pre-existing drift, untouched by this plan) |

⇒ The plan's "byte-parity lockstep" is only literally true for Offer (of the T3 states). The mirror rule must be: **add the SAME directive lines into llm.json's own state_prompt base** (not sync the whole file). Offer stays byte-identical after the edit (same lines into both) → `test_iter43_prompts.py::test_llm_json_lockstep_byte_identical` stays green. "refer-count 36 preserved" = the word "refer" appears exactly 36 times in llm.json today (verified); the T3 directive lines contain no "refer" → count stays 36.

### Legacy tests pinning the OLD flat-ack one-trip (WILL BREAK — must update)
| File:line | Current flat round |
|---|---|
| tests/test_iter31_c3_prefix.py:201 | `["Let","'s"," dig"," in","."]` + intake_completed + transition_to_Discovery |
| tests/test_iter40_spike_readback.py:364 | `["Perfect",","," moving"," on","."]` + transition_to_Booking (test_l3_one_trip_ok_transition) |
| tests/test_iter44_cache_floor.py:388 | `["Let","'s"," dig"," in","."]` + transition_to_Discovery |
| tests/test_iter46_latency_floor.py:215 | same as above |
22e6f88 updated exactly these 4 (same fix: append `— what breaks first?`-style tokens so the round asks → one-trip still finalizes).

### 22e6f88 parts that are OUT of merged-plan scope (EXCLUDE)
- `tts_gate_fast_first_flush` code default → False + `tts_gate_fast_first_flush_min_chars` knob (PT-71 already carries this as env; config.py is NOT in T3's file list).
- The letter-spelling Discovery directive (above).
- test_iter46 `test_fast_first_flush_before_stream_end` explicit-knob update (only needed if the default flips — it does not here).

---

## 3. T4' — Same-turn jaccard dedupe (owner option 2)

### Flush sites — EXISTS (iter42 machinery, fully read)
- Mid-stream token loop: builder.py:2268-2373. Order today: sentence split (2281) → fast-flush cut (2284-2294) → sanitize (2316-2321) → exact-window drop (2322-2324) → semantic check (dormant via env; 2325-2353) → speak (2354-2355) → window append + cap (2356-2373).
- Stream-end flush: builder.py:2408-2458: sanitize (2412-2418) → exact gate (2419-2420) → semantic (dormant; 2421-2439) → speak + append (2440-2457).
- Window: seeded from `state["tts_sentence_window"]` (2259-2260), carried cross-ROUND via `updates["tts_sentence_window"]` (2474), RESET at ingest (2734) — **the structural same-turn scope** (cross-turn scripted re-asks can never be touched).
- Window entries are normalized KEYS (`_norm_sentence`, builder.py:214-216: casefold + whitespace-collapse). Jaccard must re-tokenize keys on the fly (punctuation + filler strip per owner spec).

### MISSING
- No `_similar_dup` helper, no `tts_dedupe_similar` / `tts_dedupe_similar_overlap` / `tts_dedupe_similar_min_words` knobs.
- Insert point (owner-approved spec): after the exact-window check, before the (dormant) semantic check, BOTH sites. Drop the SECOND from speech; it never joins the window; log via the T5 `similar` stage line.
- Silence-guard parity: exact drop requires `spoken_any` (2323); similar must too. Note: if nothing was spoken yet this turn the window is empty → no false mute; a turn whose round-2+ sentences are ALL near-dupes goes silent exactly like the iter42 exact rule already allows (accepted semantics).
- min_words=4 naturally excludes fast-flush fragments (clause cuts are short) — G5 parity with iter59's "fragments never check".
- speech_replay.py mirror: `replay()` (L107-182) checks sanitize → exact → semantic; needs the similar check after exact (L154-157 region) + `_S` stub knobs + summary counter + import of the helper from builder (existing import pattern L27-33).
- **Owner threshold sign-off (min_words=4, overlap=0.80, filler list `well|so|ok|okay|um|uh|hey|sorry|alright`) is a HITL gate — plan BLOCKED item, stop after T3.**

---

## 4. T4p — Prompt-side repetition wording — BLOCKED (owner must approve exact lines)

- Current prompt-side repetition rules (EXISTING, scattered): Discovery.md:61 (pricing deferral "vary the wording every time"), Offer.md:10 ("never read one verbatim twice"), Booking.md:22 / contact_details.md:18,59 area rules; the general "vary it, never verbatim twice in one call" directives per plan §Compaction live in prompts the engine reads.
- DRAFT line from the plan (NOT yet owner-approved): `never say the same or near-same sentence twice this call; when re-asking, change the wording AND shorten`
- **AMBIGUITY FOUND:** the plan says the line goes "in the VOICE OUTPUT rules block" — that block is `VOICE_OUTPUT_RULES`, a builder.py constant (builder.py:62-70) appended to every head — but the T4p Files row lists `prompts Intake/Discovery/Closer/Offer/contact_details .md + llm.json mirror`. Two different targets:
  - Option A: one line in builder.py `VOICE_OUTPUT_RULES` (all states, single edit, head bytes change once per state — one-time cache re-warm).
  - Option B: per-state Critical Rules line in 5 .md files + llm.json mirrors (matches Files row; more edits, same drift risk as T3).
  Owner must pick + approve the exact wording (T4p is a HITL stop by law).

---

## 5. T5 — Observability lines (SOURCE A, re-scoped tiny)

### EXISTS
- mic_events.py RULES (L33-53): no CUT/REASK tags; `_CALL_TAGS` (L87-88) without them.
- speech_replay.py: mirrors sanitize/exact/semantic only.

### MISSING (per reference c6159ce, re-scoped)
- `_log_filter(settings, stage, sent, state_name, state)` helper in builder.py — `log.info("speech_filter stage=%s sent=%r state=%s turn=%s", …)`; stages: `sanitize` (both sites), `exact` (both), `similar` (the new T4' sites), `fast_flush` (mid-stream cut site, ff_cut flag). Reference gated it on a `speech_filter_observability` knob (default True); merged plan T5 file list does NOT include config.py ⇒ log unconditionally (INFO volume is low: drops are rare; fast_flush never fires on the lane because `TTS_GATE_FAST_FIRST_FLUSH=false`).
- mic_events.py: `("CUT", re.compile(r"speech_filter stage="))`, `("REASK", re.compile(r"pause[ _-]re.?ask|re-ask firing"))` (iter70 wording `pause re-ask firing`; reference regex was `silence_reask`) + add both to `_CALL_TAGS`.
- speech_replay.py: `[CUT similar …]` print + `cuts["similar"]` counter + knob passthrough.
- Pin: FakeLLM round with an artifact + a near-dupe → caplog shows both lines.

### c6159ce parts OUT of re-scoped scope (EXCLUDE)
- Cancel-safe Langfuse generation spans (the "round-4 gen gap" fix) — a behavior change, not forensics.
- The `speech_filter_observability` config knob (keeps T5 out of config.py per the file map).

---

## 6. Bugs / risks / conflicts found (full list)

| # | Finding | Severity | Disposition |
|---|---|---|---|
| A1 | Reference 651e567 directive append is nested under `if state_delta_block:` → all-empty dvs turn LOSES the pause_reask directive | HIGH | Fix in re-impl: append to delta independent of state_delta_block emptiness |
| A2 | llm.json is NOT byte-parity for Intake/Discovery/Closer (only Offer/contact_details/ConfirmSlots) — plan's "byte-parity lockstep" claim is only true for Offer | MEDIUM | Mirror = same lines into llm.json's own base; Offer stays byte-identical; lockstep test stays green |
| A3 | 4 legacy tests pin the flat-ack one-trip (test_iter31:201, test_iter40:364, test_iter44:388, test_iter46:215) — T3 breaks them | CERTAIN | Update tokens to "?"-ending (same as 22e6f88 did) in the T3 commit |
| A4 | T4p target ambiguity: VOICE_OUTPUT_RULES (builder.py) vs per-state .md+llm.json (Files row) | MEDIUM | HITL: owner picks target + approves exact wording (already a plan gate) |
| A5 | `_run_turn` lacks `extra_payload` param (plan's call shape doesn't compile today) | EXPECTED | Part of T2 (2-line reference change) |
| A6 | GraphState missing `turn_asked` + `pause_reask` — undeclared keys in updates raise InvalidUpdateError in LangGraph | CERTAIN | state.py edit in T2/T3 commits (reference did the same) |
| A7 | 22e6f88 extras NOT in merged plan: fast-flush default flip + min_chars knob, letter-spelling directive | MEDIUM | EXCLUDE (PT-71 env carries the fast-flush kill; letter-spelling not a transition fix) — owner may re-add later |
| A8 | c6159ce extras NOT in re-scoped T5: cancel-safe gen spans, observability knob | LOW | EXCLUDE — T5 is forensics-only per plan |
| A9 | Timer arm point = end of `_late_turn_report` (~3s drain wait AFTER graph turn) → re-ask fires ~pause_reask_ms after the DRAIN check, not after last audio byte | LOW | Accept (reference semantics; "~10s" is owner-ear approx). No browser-transport mark echo exists — nothing better to anchor on |
| A10 | Greeting never arms the timer (no `_run_turn`) — silent-after-greeting caller gets no re-prompt | LOW | Accept (matches reference; ear-check scenario is "answer a question, go silent") |
| A11 | Re-ask turn counts toward `max_call_turns` (64) / `max_call_seconds` (900) via `_real_turns` | LOW | Accept (safety caps should count engine-initiated turns) |
| A12 | `_cap_hit()` checked at BOTH arm and fire (reference) — keep both | LOW | Copy reference |
| A13 | Re-ask turn + RAG: no laneB fire (no `_fire_live_retrieve` on the re-ask path); laneA may serve the previous turn's landed set — dvs-driven, same state → still relevant | LOW | Accept |
| A14 | config.py has duplicated blocks (prompts_dir/database_url/metrics_enabled/hangup_mode defined twice, L428-433 vs L444-448, L228 vs L431) — pre-existing, harmless (later value wins, same value) | INFO | Do NOT fix (out of scope, PT-73 minimalism) |
| A15 | `tts_provider` code default = elevenlabs; `.env` pins cartesia (env wins). `tts_dedupe_semantic` code default True; env false. Both MUST stay untouched | LAW | Never-touch list honored |
| A16 | T3 continuation round = entry_lite ack → its "SPEECH ONLY" directive (builder.py:2219-2221) + the new prompt directive coexist; executor still runs any tool the model calls (documented behavior, state_entry_lite_off escape hatch) | INFO | Accept (reference shipped exactly this) |
| A17 | contact_details/ConfirmSlots/VerifyLead/Booking/Closing transitions ALSO fall under the T3 engine one-trip change but only Intake/Discovery/Closer/Offer carry the prompt directive | MEDIUM | Mirror reference scope (4 states); ConfirmSlots entry has its own scripted opener — flag to owner in report |
| A18 | Deploy block copies `prompts/*.md` wholesale (all 9 files) — files not in the map are byte-identical branch↔main (verified empty engine diff), so the copy is a no-op for them | LOW | Accept |
| A19 | Suite expectation: 476 passed + 1 known env fail (`test_tts_providers.py::test_factory_switches_provider`) + 1 known flake (`test_iter46_latency_floor.py::test_fast_first_flush_before_stream_end`) | INFO | Re-verify per task commit; flake is perf-timer only, unrelated |
| A20 | HITL gates INSIDE the task order: T4' thresholds (stop after T3), T4p exact lines (stop before any .md edit), merge ASK (T7) | LAW | Preserve exactly in master plan |
| A21 | `PENDING_TASKS.md` + plan status updates are docs → main (LAW 0) — they commit on the MAIN checkout, not the branch | LAW | Closeout mechanics; main checkout has a pre-existing unrelated dirty doc file — never stage it |
| A22 | New session attr must be class-level default (`_pause_reask_task: asyncio.Task | None = None`) for tests that build CallSession without `__init__` (existing pattern L67-74) | LOW | Copy reference (it sets both class-level and init) |

---

## 7. What EXISTS vs MISSING — one-line summary per task

- **T2 pause re-prompt:** timer mechanics 100% specified by reference 651e567 (session.py ~52 lines, builder.py ~19, config 7); MISSING entirely on main; flaws A1/A6 to fix in re-impl.
- **T3 transition beat:** one-trip change + `turn_asked` flag + 2 directive lines × 4 prompts + llm.json mirror + 4 legacy test updates, fully specified by reference 22e6f88; MISSING entirely on main; exclude its fast-flush/letter-spelling extras (A7).
- **T4' jaccard dedupe:** flush sites + window machinery exist; helper + knobs + replay mirror MISSING; spec owner-approved except threshold sign-off (HITL).
- **T4p prompt wording:** draft line exists in plan; target ambiguous (A4); owner approval MISSING (HITL).
- **T5 observability:** `_log_filter` + mic_events tags + replay parity MISSING; reference c6159ce shows the shape; exclude its gen-span/knob extras (A8).

Audit complete. No unknowns remain on the code surface; every planned edit has a verified anchor line.
