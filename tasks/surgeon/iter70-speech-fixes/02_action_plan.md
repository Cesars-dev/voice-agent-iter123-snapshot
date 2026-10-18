# 02 — ACTION PLAN — iter70 speech fixes

Based on: `01_audit.md` (same folder). Executed on branch `engine/iter70-speech-fixes`, worktree `/tmp/opencode/wt-iter70`.
Task order + HITL gates come verbatim from `plans/plan_v5_iter70_speech_fixes_merged.md` (stop at EVERY T; T4' thresholds + T4p wording + merge = owner gates).
All edits below cite anchor lines in the worktree @ `2d9385d`. One commit per task; `pytest` subset green after each; ≤60-line diffs per task (PT-73).

---

## T2 — Pause re-prompt (PT-68) — commit 1 — HITL: owner GO received ("NEXT, awaiting owner GO" per plan — ask before starting)

Port of reference `651e567` (renamed `silence_reask`→`pause_reask`, 2000ms→10000ms), with audit flaw A1 fixed.

### 2.1 `engine/diallux/config.py` (+7 lines, after the `tts_sanitize_tokens` block L174)
```python
    # iter70 T2 (PT-68, owner "~10s"): caller-silence pause re-prompt — when
    # the caller goes silent after the agent's turn, ONE engine-initiated
    # rephrased re-ask fires after pause_reask_ms. ONE-SHOT per turn;
    # cancelled the instant the caller speaks; never loops.
    pause_reask: bool = True
    pause_reask_ms: int = 10000
```

### 2.2 `engine/diallux/state.py` (+1 line, in GraphState after `round_spoke` L34)
```python
    pause_reask: bool           # iter70 T2: this turn is an engine-initiated pause re-ask (no caller input)
```

### 2.3 `engine/diallux/media/session.py` (~52 lines, reference shape)
1. Class-level default next to `_resumed_count` (L68): `_pause_reask_task: asyncio.Task | None = None`
2. `__init__` (after `_resumed_count = 0` L128): `self._pause_reask_task: asyncio.Task | None = None`
3. `stop()` (after `self._turn_task.cancel()` L278): `self._cancel_pause_reask()`
4. `_on_start_of_turn` (after the `self._send({"event": "clear", ...})` L598): `self._cancel_pause_reask()`
5. `_run_turn` signature L638 → `async def _run_turn(self, transcript: str, extra_payload: dict | None = None):` and after `payload: dict[str, Any] = {"user_text": transcript}` (L645):
```python
            if extra_payload:
                payload.update(extra_payload)       # iter70 T2: pause_reask flag
```
6. END of `_late_turn_report` (after the state-check try/except, L717) — arm block:
```python
        # iter70 T2 (PT-68): arm the caller-pause re-ask (the agent's turn is
        # done and its audio drained). ONE-SHOT: the re-ask turn's own clock
        # is flagged, so it never re-arms itself; cancelled on caller speech.
        if (self.settings.pause_reask and not self._stopped and not self._ended
                and not clock.extra.get("pause_reask")
                and not self._cap_hit()):
            self._cancel_pause_reask()
            self._pause_reask_task = asyncio.get_event_loop().create_task(
                self._pause_reask_timer(clock.turn_index))
```
7. New methods (after `_late_turn_report`, before `_greeting_drain`):
```python
    async def _pause_reask_timer(self, armed_turn: int):
        """iter70 T2 (PT-68): the caller said NOTHING for pause_reask_ms
        after the agent's turn — fire ONE engine-initiated re-ask turn (a
        REPHRASED ask). Never loops (one-shot latch)."""
        try:
            await asyncio.sleep(self.settings.pause_reask_ms / 1000.0)
        except asyncio.CancelledError:
            raise
        if self._stopped or self._ended:
            return
        if self._cap_hit():
            await self._graceful_cap_close()
            return
        if self._turn_task and not self._turn_task.done():
            return                      # caller spoke / a turn is running
        log.info("pause re-ask firing (armed at turn %s)", armed_turn)
        self.tracer.span("pause_reask", metadata={
            "ms": self.settings.pause_reask_ms, "turn": armed_turn,
            "call_sid": self.call_sid})
        prev = self._clock
        self._clock = TurnClock(turn_index=prev.turn_index + 1,
                                extra={"pause_reask": True})
        self._turn_task = asyncio.create_task(
            self._run_turn("", extra_payload={"pause_reask": True}))

    def _cancel_pause_reask(self):
        task = getattr(self, "_pause_reask_task", None)
        if task and not task.done():
            task.cancel()
        self._pause_reask_task = None
```

### 2.4 `engine/diallux/graph/builder.py` (~14 lines)
1. entry_lite guard (L1803-1808): add `and not state.get("pause_reask")   # iter70 T2: a re-ask round is always heavy`
2. ingest (L2737-2742) — no-empty-user guard + flag carry:
```python
            # iter70 T2: a pause re-ask turn arrives with NO caller input —
            # never append an empty user message; the flag rides the turn.
            reask_turn = bool(state.get("pause_reask"))
            patch["pause_reask"] = reask_turn
            text = state.get("user_text", "")
            last_user = next((m for m in reversed(state.get("history", []))
                              if m.get("role") == "user"), None)
            if reask_turn:
                pass
            elif not (text and last_user is not None
                      and last_user.get("content", "") == text):
                patch["history"] = [{"role": "user", "content": text}]
```
3. Directive ride — FIXED A1 (insert BEFORE the `if state_delta_block:` composition at L2229-2234, inside the `elif runtime.settings.state_in_delta and not lite:` branch):
```python
            elif runtime.settings.state_in_delta and not lite:
                # iter56 (C2.2): state FIRST, RAG after …
                if state.get("pause_reask"):
                    # iter70 T2: engine-initiated pause re-ask — the directive
                    # rides the post-history delta REGARDLESS of state-block
                    # emptiness (audit A1: the reference lost it when dvs
                    # were all empty).
                    state_delta_block = (
                        state_delta_block + "\n\n" if state_delta_block else ""
                    ) + ("THIS ROUND: the caller has gone SILENT "
                         "after your last question. Re-ask it ONCE — shorter, "
                         "warmer, differently worded (never the same sentence). "
                         "Then stop and listen. Do not call any tool this round.")
                if state_delta_block:
                    rag_delta = state_delta_block + rag_delta
```

### 2.5 Pin — `engine/tests/test_iter70_pause_reask.py` (new, ~90 lines, modeled on the parked `test_iter68_round_yield.py` harness shape: FakeLLM + run_turns + mock_client)
- pin 1: re-ask turn runs with NO empty user message in final history (assert no `{"role":"user","content":""}` and no duplicate user append).
- pin 2: the directive text rides the delta (FakeLLM `match_system="caller has gone SILENT"` round consumed).
- pin 3: re-ask round is HEAVY (not entry_lite): after a transition turn, the re-ask renders the full state head (FakeLLM match_system on the state prompt's kb-stripped head marker).
- pin 4: unit — timer one-shot: session double with `pause_reask_ms=10`; simulate `_late_turn_report` completion without caller speech → exactly ONE `_run_turn("", {"pause_reask": True})` call; second arm never fires (clock extra latch).
- pin 5: unit — `_on_start_of_turn` cancels the pending timer (task.cancel called).

### 2.6 Verification
- `pytest tests/test_iter70_pause_reask.py tests/test_v2.py tests/test_graph.py -q` then full suite subset.
- Live mic (after T6 deploy): answer a question, go silent ~11s → agent re-asks ONCE rephrased; `journalctl --user -u diallux-8024.service | grep "pause re-ask firing"`; NO loop after the single re-ask.

---

## T3 — Transition beat / silent acks (PT-70) — commit 2

Port of reference `22e6f88` EXCLUDING the fast-flush default flip, min_chars knob, and letter-spelling directive (audit A7).

### 3.1 `engine/diallux/state.py` (+1 line)
```python
    turn_asked: bool            # iter70 T3: the caller HEARD a '?' sentence this turn (post-filter truth)
```

### 3.2 `engine/diallux/graph/builder.py` (~30 lines)
1. Seed near the window seed (after L2267 `spoken_any = bool(state.get("turn_spoke"))`):
```python
            turn_asked = bool(state.get("turn_asked"))   # iter70 T3: caller-heard '?' truth
```
2. Mid-stream window-append site (inside `if key:` block, after `spoken_any = True` L2358):
```python
                                        if "?" in sent:
                                            turn_asked = True   # iter70 T3: the caller HEARD a question
```
3. Stream-end window-append site (after `spoken_any = True` L2444):
```python
                            if "?" in pending_text:
                                turn_asked = True   # iter70 T3: the caller HEARD a question
```
4. `updates` dict (L2469, after `"round_spoke"`): `"turn_asked": turn_asked,`
5. ingest patch dict (L2722-2728, after `"round_spoke": False`): `"turn_asked": False,`
6. `route_after_deterministic` (L2793-2799) — replace the inner one-trip check with the 22e6f88 shape (verbatim from reference):
```python
            if self.settings.one_trip and executed and all(
                    FIRE_AND_FORGET.match(t["name"])
                    or (t["name"].startswith("transition_to_")
                        and t.get("status") == "ok")
                    for t in executed):
                # iter70 T3: DETERMINISTIC TRANSITION BEAT — a round that fired
                # an ok transition_to_* may only one-trip-finalize when the
                # caller HEARD a '?' (post-filter turn_asked, not content).
                # Otherwise the turn routes into the destination state, where
                # the EXISTING entry_lite ack renders exactly ONE speech-only
                # continuation round (its directive: destination's first
                # scripted question if it fits, else one contextual question).
                if state.get("round_spoke") and (
                        state.get("turn_asked")
                        or not any(t["name"].startswith("transition_to_")
                                   for t in executed)):
                    return "finalize"            # ONE TRIP: speech + bookkeeping/ok-transition
                if not state.get("round_spoke"):
                    pass                         # silent round: today's loop/force-speech path
                elif not any(t["name"].startswith("transition_to_")
                             and t.get("status") == "ok" for t in executed):
                    return "finalize"            # bookkeeping-only, no transition: today's rule
                # else: flat transition ack -> fall through to the continuation round
```

### 3.3 Prompts (4 files, 2 directive lines each — verbatim 22e6f88)
- `Intake.md` Critical Rules (after `Keep replies 1–2 sentences.` L51): + `Every turn ends with a question to the caller — never a flat statement.`
- `Discovery.md` Critical Rules (after `ONE question at a time…` L55): + the same line + `When a stage transition just moved you here, your ack ends with EITHER the next scripted question (if it fits the live conversation) OR one short contextual question that keeps the flow — never a flat ack.`
- `Closer.md` Critical Rules (after `ONE question at a time…` L102): + the same two lines.
- `Offer.md` Critical Rules (after `ONE question at a time…` L57): + the same two lines.

### 3.4 `engine/agent/llm.json` — mirror the SAME lines into each state's own `state_prompt` (Intake/Discovery/Closer/Offer), same positions. Offer stays byte-identical to its .md (audit A2). Verify: word `refer` count in llm.json still 36; `pytest tests/test_iter43_prompts.py` green.

### 3.5 Legacy tests (audit A3 — same edits as 22e6f88)
- `test_iter31_c3_prefix.py:201` tokens → `["Let", "'s", " dig", " in", " —", " what", " breaks", " first", "?"]`
- `test_iter40_spike_readback.py:364` tokens → `["Perfect", ",", " moving", " on", " —", " good", "?"]`
- `test_iter44_cache_floor.py:388` + `test_iter46_latency_floor.py:215` tokens → same as test_iter31.

### 3.6 Pin — `engine/tests/test_iter70_transition_beat.py` (new, modeled on parked `test_iter68_round_yield.py`, ~120 lines)
- pin 1: flat transition ack → exactly ONE continuation round in the destination (3 LLM rounds total), continuation ends in a spoken "?".
- pin 2: ack WITH a spoken "?" → one-trip finalize (2 rounds, no continuation).
- pin 3: ack whose "?" sentence is dropped by the exact-window dedupe → continuation fires (turn_asked is post-filter truth).
- pin 4: silent + transition round → same routing as today (no finalize, destination round).

### 3.7 Verification
Full suite subset green. Live mic (T6): after each state transition the next question arrives in the SAME spoken turn.

**HITL STOP after T3: owner signs off T4' thresholds (min_words=4, overlap=0.80, filler list) before T4' starts.**

---

## T4' — Same-turn jaccard dedupe — commit 3 (after owner threshold GO)

### 4.1 `engine/diallux/config.py` (+9 lines, after the T2 block)
```python
    # iter70 T4' (owner option 2): same-turn NEAR-duplicate sentence dedupe —
    # after the exact-window check, a sentence whose normalized token jaccard
    # vs any spoken sentence of THIS turn >= overlap is dropped from SPEECH
    # only. Same-turn scope (window resets at ingest); NO embedder.
    tts_dedupe_similar: bool = True
    tts_dedupe_similar_overlap: float = 0.80
    tts_dedupe_similar_min_words: int = 4
```

### 4.2 `engine/diallux/graph/builder.py` — one shared helper + ≤4 lines per flush site
Module level (after `_norm_sentence` L216):
```python
# iter70 T4': near-duplicate token prep — filler words + punctuation stripped
# from the normalized key; jaccard runs on the remaining word set.
_SIMILAR_FILLERS = {"well", "so", "ok", "okay", "um", "uh",
                    "hey", "sorry", "alright"}
_WORD_RE = re.compile(r"[a-z0-9']+")


def _similar_tokens(key: str) -> set[str]:
    return {w for w in _WORD_RE.findall(key) if w not in _SIMILAR_FILLERS}


def _similar_dup(key: str, window: list[str], settings) -> bool:
    """iter70 T4': True when `key` near-duplicates (token jaccard >=
    tts_dedupe_similar_overlap) a sentence already spoken THIS TURN. Both
    sides need >= tts_dedupe_similar_min_words tokens (fragments and short
    acks never check). Pure python, deterministic, no embedder."""
    min_words = int(getattr(settings, "tts_dedupe_similar_min_words", 4))
    toks = _similar_tokens(key)
    if len(toks) < min_words:
        return False
    thr = float(getattr(settings, "tts_dedupe_similar_overlap", 0.80))
    for prev in window:
        ptoks = _similar_tokens(prev)
        if len(ptoks) < min_words:
            continue
        inter = len(toks & ptoks)
        if inter and inter / len(toks | ptoks) >= thr:
            return True
    return False
```
Mid-stream insert (after the exact check L2323-2324, before the semantic block):
```python
                            if key and spoken_any and runtime.settings.tts_dedupe_similar \
                                    and _similar_dup(key, window, runtime.settings):
                                continue            # in-turn near-duplicate — never spoken
```
Stream-end insert (inside the `if not (pending_key and spoken_any and pending_key in window):` gate, after the exact-pass, before the semantic check — set `pending_key = None` so the `if pending_key and pending_tokens:` speak block skips):
```python
                        if pending_key and spoken_any \
                                and runtime.settings.tts_dedupe_similar \
                                and _similar_dup(pending_key, window, runtime.settings):
                            pending_key = None      # in-turn near-duplicate — never spoken
```
(Exact T5 log lines ride these two sites — added in T5, same commit positions.)

### 4.3 `engine/scripts/speech_replay.py` — mirror (truthful replay)
- `_S.__init__`: + `self.tts_dedupe_similar = _envbool("TTS_DEDUPE_SIMILAR", True)` / `self.tts_dedupe_similar_overlap = float(os.getenv("TTS_DEDUPE_SIMILAR_OVERLAP", "0.80"))` / `self.tts_dedupe_similar_min_words = int(os.getenv("TTS_DEDUPE_SIMILAR_MIN_WORDS", "4"))`
- import `_similar_dup` from builder (extend L27-33 import).
- In `replay()` after the exact check (L154-157):
```python
            if key and spoke_any and s.tts_dedupe_similar \
                    and _similar_dup(key, exact, s):
                cuts["similar"] += 1
                print(f"  [CUT similar jaccard] {sent!r}")
                continue
```
- `cuts` dict init + summary line gain `"similar"`.

### 4.4 Pin — `engine/tests/test_iter70_similar_dedupe.py` (new, ~80 lines)
- near-dupe dropped (jaccard ≥ 0.80 same-turn, e.g. filler-swapped variant); window unchanged by the drop.
- distinct question KEPT (jaccard < 0.80).
- cross-turn near-dupe KEPT (ingest reset — the iter59 guarantee).
- short sentence (< 4 tokens after filler strip) never checked.
- knob off → byte-exact today behavior.

### 4.5 Verification
Suite subset green; owner A/B by ear via `TTS_DEDUPE_SIMILAR=false` toggle on the lane.

---

## T4p — Prompt-side repetition wording — commit 4 — BLOCKED until owner approves exact lines + target

- HITL: paste the draft line in chat: `never say the same or near-same sentence twice this call; when re-asking, change the wording AND shorten`
- HITL: owner picks target (audit A4): (A) builder.py `VOICE_OUTPUT_RULES` (one edit, all states, no llm.json) or (B) per-state Critical Rules in Intake/Discovery/Closer/Offer/contact_details .md + llm.json mirrors.
- Only after both approvals: edit, mirror (same-lines rule), suite + lockstep pins, battery transcripts show ≤2 asks per missing field.

---

## T5 — Observability lines — commit 5

### 5.1 `engine/diallux/graph/builder.py`
Module-level helper (after `_similar_dup`):
```python
def _log_filter(settings, stage: str, sent: str, state_name: str,
                state: dict) -> None:
    """iter70 T5: ONE INFO line per speech-filter drop/split so every cut is
    visible live (journal + mic_events CUT tag). stage ∈ {sanitize, exact,
    similar, fast_flush}; observability only — never changes behavior."""
    log.info("speech_filter stage=%s sent=%r state=%s turn=%s",
             stage, sent, state_name, state.get("turn_index"))
```
Call sites (6 total): mid-stream ff_cut split (set `ff_cut = bool(cut)` at the fast-flush branch, log `"".join(head_tokens)` after the token split), mid-stream sanitize drop (before `continue`), mid-stream exact drop, mid-stream similar drop (T4' site), stream-end sanitize drop, stream-end exact + similar drops (log before the pending clear). NO knob (audit A8) — unconditional INFO.

### 5.2 `engine/scripts/mic_events.py` (+4 lines)
RULES (after TURN, L51):
```python
    ("CUT",     re.compile(r"speech_filter stage=")),
    ("REASK",   re.compile(r"pause[ _-]re.?ask|re-ask firing")),
```
`_CALL_TAGS` += `"CUT", "REASK"`.

### 5.3 `engine/scripts/speech_replay.py` — the `[CUT …]` prints from T4' + this task already mirror the journal shape (stage names in the CUT labels); add the sanitizer/exact print parity if missing (already present L139/156).

### 5.4 Pin — extend `test_iter70_similar_dedupe.py` or new `test_iter70_filter_log.py`: FakeLLM round with a code artifact + a near-dupe → caplog asserts both `speech_filter stage=sanitize` and `stage=similar` lines.

---

## T6 — Battery + lane deploy + owner ear test (no new code)
1. Battery: `cd /tmp/opencode/wt-iter70/engine && set -a && . ./.env && set +a && setsid nohup .venv/bin/python tests/llm2llm/harness.py --personas happy3 --rag --langfuse --max-turns 48 > /tmp/opencode/iter70_battery.log 2>&1 < /dev/null &` — gate 3/3 BOOK.
2. Lane deploy (copy + restart + verify) — exact block from the plan's Deploy Rules.
3. Ear checklist (owner, `https://flores.diallux-ai.site/voice24/mic?k=$VOICE_TEST_TOKEN`): (1) pause re-prompt ~10s ONCE; (2) transition acks carry the next question; (3) same-turn near-dupe not spoken; (4) cross-turn scripted re-asks STILL audible; (5) voice unchanged — journal prints `cartesia connected` with `model=sonic-3.6-2026-08-27`.
4. Ledger: import via MAIN-repo SDK `scripts/live_sql.py`; gates `--a chat-iter65-happy --b chat-iter70-happy` green on G1/G2/G4; report → `research/surgeon/iter70-speech-fixes/01_report.md`; cancel test bookings.

## T7 — Closeout (no new code)
Lane RESTORE block; `hitl_ping.py` the merge ASK (LAW 0 — merge = owner only); PENDING_TASKS PT-68/69/70/71 status updates (docs → main, never stage the unrelated dirty SOP file).

---

## Commit map (branch `engine/iter70-speech-fixes`)

| Commit | Files | ~Size |
|---|---|---|
| 1 (T2) | config.py, state.py, session.py, builder.py, tests/test_iter70_pause_reask.py | ~75 lines |
| 2 (T3) | state.py, builder.py, 4 prompts, llm.json, 4 legacy tests, tests/test_iter70_transition_beat.py | ~60 lines |
| 3 (T4') | config.py, builder.py, speech_replay.py, tests/test_iter70_similar_dedupe.py | ~60 lines |
| 4 (T4p) | TBD by owner (VOICE_OUTPUT_RULES or 5 prompts + llm.json) | ≤20 lines |
| 5 (T5) | builder.py, mic_events.py, speech_replay.py, pin | ~25 lines |

Diff budget check (PT-73 law: ≤60 lines, >50 needs owner sign-off): T2 ~75 and T3 ~60 land at/over the line — the plan already carries owner sign-off for the merged scope (verbatim-from-reference, HITL at every T); each commit is shown to the owner at its HITL stop before it is made.
