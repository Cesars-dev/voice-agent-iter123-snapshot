# 04 — MASTER PLAN: iter70 speech fixes (airtight — all flaws resolved, preflight-verified against branch `engine/iter70-speech-fixes` @ `2d9385d`)

- Date: 2026-09-23 · Status: **MASTER PLAN — awaiting owner GO. EXECUTE ONLY ON APPROVAL. HITL STOP AT EVERY T.**
- Sources: `plans/plan_v5_iter70_speech_fixes_merged.md` (owner-approved, main `ced8538`) + `archive/01_audit.md`, `archive/02_action_plan.md`, `archive/03_cross_reference.md` (this folder)
- Base: branch `engine/iter70-speech-fixes` @ `2d9385d`, worktree `/tmp/opencode/wt-iter70` (venv symlink + voice-LAW `.env` verified 2026-09-23; `git diff 2d9385d ced8538 -- engine/` = empty)
- All anchor line numbers below were re-verified against the worktree files on 2026-09-23 (preflight §8 of 03_cross_reference: PASS on all 8 items; no name collisions — `_similar_dup`, `_log_filter`, `_WORD_RE`, `_SIMILAR_FILLERS`, `_similar_tokens`, `pause_reask`, `turn_asked` all absent from the codebase today).

---

## 0. Execution rules (LAW — read before every task)

1. **HITL stop at EVERY T.** At each stop: show the owner the exact planned diff (this doc's section) → owner decides/acts → only then commit. Commits go on the BRANCH (never main). PT-73: each diff shown at its stop IS the owner sign-off.
2. **Never touch:** `:8021`/`:8022` (pids 3834955/884638), `:8000-8003`, `engine/diallux/media/prewarm.py`, `elevenlabs_tts.py`, `tts_factory.py`, live agent IDs, Cal.com event 3801235 real bookings, `CARTESIA_MODEL_ID` in any .env, `TTS_DEDUPE_SENTENCES`, `TTS_DEDUPE_SEMANTIC` (stays env-false). Cherry-pick/merge from `engine/iter68-*` branches: FORBIDDEN (reference diffs only — already read, they are embedded below as code).
3. **Docs → main** (PENDING_TASKS.md, plan status): committed on the MAIN checkout at closeout; NEVER stage the pre-existing dirty `docs/Testing_guidelines/MIC-CALL-ANALYSIS-SOP.md` or untracked `tasks/surgeon/iter68-speech-flow/`.
4. Suite after every commit (worktree): `.venv/bin/python -m pytest tests -q` — expected: 476 passed baseline + 1 known env fail (`test_tts_providers.py::test_factory_switches_provider`) + 1 known flake (`test_iter46_latency_floor.py::test_fast_first_flush_before_stream_end`, perf-timer, unrelated). Any NEW failure = stop and report.
5. Reference-commit extras are EXCLUDED by law (audit A7/A8): fast-flush default flip + min_chars knob, letter-spelling directive, cancel-safe gen spans, `speech_filter_observability` knob.
6. Push = owner terminal (agent shell has no creds).

---

## TASK T2 — Pause re-prompt (PT-68) — ONE commit — **START HERE: owner GO required before any edit**

**Commit 1:** `iter70 T2: pause re-prompt (PT-68) — one-shot 10s session timer + ingest no-empty-user guard + re-ask-round-always-heavy + post-history directive; knobs pause_reask/pause_reask_ms=10000 (port of 651e567, renamed, audit flaw A1 fixed)`

### T2.1 `engine/diallux/config.py` — after the `tts_sanitize_tokens` block (L174)
```python
    # iter70 T2 (PT-68, owner "~10s"): caller-silence pause re-prompt — when
    # the caller goes silent after the agent's turn, ONE engine-initiated
    # rephrased re-ask fires after pause_reask_ms. ONE-SHOT per turn;
    # cancelled the instant the caller speaks; never loops.
    pause_reask: bool = True
    pause_reask_ms: int = 10000
```

### T2.2 `engine/diallux/state.py` — GraphState, after `round_spoke` (L34)
```python
    pause_reask: bool           # iter70 T2: this turn is an engine-initiated pause re-ask (no caller input)
```

### T2.3 `engine/diallux/media/session.py` — 7 edits (verified anchors)
1. Class-level default (next to `_resumed_count = 0`, L68): `_pause_reask_task: asyncio.Task | None = None`
2. `__init__` (after `self._resumed_count = 0`, L128): `self._pause_reask_task: asyncio.Task | None = None`
3. `stop()` — after `self._turn_task.cancel()` (L278): `self._cancel_pause_reask()   # iter70 T2: no dangling re-ask timer`
4. `_on_start_of_turn` — after `self._send({"event": "clear", ...})` (L598): `self._cancel_pause_reask()   # iter70 T2: the caller began speaking — pending re-ask dies`
5. `_run_turn` (L638): signature → `async def _run_turn(self, transcript: str, extra_payload: dict | None = None):`; after `payload: dict[str, Any] = {"user_text": transcript}` (L645):
```python
            if extra_payload:
                payload.update(extra_payload)       # iter70 T2: pause_reask flag
```
6. END of `_late_turn_report` (new code after L717, end of method):
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

### T2.4 `engine/diallux/graph/builder.py` — 3 edits
1. entry_lite guard (L1803-1808) — add one condition line:
```python
                and not state.get("pause_reask")   # iter70 T2: a re-ask round is always heavy
```
2. ingest (L2737-2742) — replace the 6-line guard block with:
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
3. Directive ride — **FLAW A1 FIX** (L2229-2233): replace
```python
            elif runtime.settings.state_in_delta and not lite:
                # iter56 (C2.2): state FIRST, RAG after — the delta IS the
                # last message the model reads; the state block anchors the
                # live values before the knowledge section tails it.
                if state_delta_block:
                    rag_delta = state_delta_block + rag_delta
```
with
```python
            elif runtime.settings.state_in_delta and not lite:
                # iter56 (C2.2): state FIRST, RAG after — the delta IS the
                # last message the model reads; the state block anchors the
                # live values before the knowledge section tails it.
                # iter70 T2: the re-ask directive rides the delta REGARDLESS
                # of state-block emptiness (audit A1: the reference lost it
                # when all dvs were empty).
                if state.get("pause_reask"):
                    state_delta_block = (
                        state_delta_block + "\n\n" if state_delta_block else ""
                    ) + ("THIS ROUND: the caller has gone SILENT "
                         "after your last question. Re-ask it ONCE — shorter, "
                         "warmer, differently worded (never the same sentence). "
                         "Then stop and listen. Do not call any tool this round.")
                if state_delta_block:
                    rag_delta = state_delta_block + rag_delta
```
(Directive text = VERBATIM 651e567 — cross-ref C-1 resolution; the merged plan's paraphrase does not ship.)

### T2.5 Pin — new `engine/tests/test_iter70_pause_reask.py` (~90 lines; FakeLLM/tool_call/mock_client harness shape from parked `test_iter68_round_yield.py` — verified to exist in `tests/fake_llm.py:13,60`, `tests/mock_webhooks.py:270`)
- pin 1: re-ask turn leaves NO empty/duplicate user message in final history
- pin 2: directive rides the delta (FakeLLM `match_system="caller has gone SILENT"`)
- pin 3: re-ask round after a transition turn is HEAVY (full state head, not entry_lite)
- pin 4: session double, `pause_reask_ms=10` → exactly ONE `_run_turn("", {"pause_reask": True})`; the re-ask's own turn never re-arms (clock extra latch)
- pin 5: `_on_start_of_turn` cancels the pending timer

### T2.6 Verify + HITL stop
`pytest tests -q` (rule 4 baseline). Report diff + results → owner. Live-mic proof happens at T6 (battery cannot exercise the session-layer timer — cross-ref G-2).

---

## TASK T3 — Transition beat / silent acks (PT-70) — ONE commit

**Commit 2:** `iter70 T3: deterministic transition beat (ok transition one-trips ONLY when turn_asked; flat ack → destination entry_lite continuation round) + turn_asked post-filter flag + prompt directives (Intake/Discovery/Closer/Offer + llm.json mirror, refer=36) + 4 legacy test updates (port of 22e6f88, fast-flush/letter-spelling extras EXCLUDED)`

### T3.1 `engine/diallux/state.py` — GraphState, after `round_spoke` (L34, same region as T2.2)
```python
    turn_asked: bool            # iter70 T3: the caller HEARD a '?' sentence this turn (post-filter truth)
```

### T3.2 `engine/diallux/graph/builder.py` — 6 edits (verified anchors)
1. Seed — after `spoken_any = bool(state.get("turn_spoke"))` (L2267):
```python
            turn_asked = bool(state.get("turn_asked"))   # iter70 T3: caller-heard '?' truth
```
2. Mid-stream append — inside `if key:` after `spoken_any = True` (L2358):
```python
                                        if "?" in sent:
                                            turn_asked = True   # iter70 T3: the caller HEARD a question
```
3. Stream-end append — after `spoken_any = True` (L2444):
```python
                            if "?" in pending_text:
                                turn_asked = True   # iter70 T3: the caller HEARD a question
```
4. `updates` dict — after the `"round_spoke"` line (L2471): `"turn_asked": turn_asked,   # iter70 T3: caller-heard '?' truth`
5. ingest patch dict — after `"round_spoke": False,` (L2725): `"turn_asked": False,`
6. `route_after_deterministic` (L2793-2799) — replace the inner `if state.get("round_spoke"): return "finalize"` with the 22e6f88 shape:
```python
                # iter70 T3: DETERMINISTIC TRANSITION BEAT — a round that fired
                # an ok transition_to_* may only one-trip-finalize when the
                # caller HEARD a '?' (post-filter turn_asked, not content).
                # Otherwise the turn routes into the destination state, where
                # the EXISTING entry_lite ack renders exactly ONE speech-only
                # continuation round (destination's first scripted question
                # if it fits, else one contextual question — prompt rule).
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
Behavior delta vs today = ONLY `round_spoke + ok-transition + !turn_asked` (flat ack): finalize → one continuation round. PhaseB `engine_fired` path (L2787-2788) returns before this block — chain transitions unaffected.

### T3.3 Prompts (2 verbatim directive lines; positions verified)
- `Intake.md` after L51 (`Keep replies 1–2 sentences.`): + `Every turn ends with a question to the caller — never a flat statement.`
- `Discovery.md` after L55 (`ONE question at a time, then STOP and listen.`): + the same line, then + `When a stage transition just moved you here, your ack ends with EITHER the next scripted question (if it fits the live conversation) OR one short contextual question that keeps the flow — never a flat ack.`
- `Closer.md` after L102 (`ONE question at a time, then STOP and listen.`): + the same two lines.
- `Offer.md` after L57 (`ONE question at a time, then STOP and listen.`): + the same two lines.
EXCLUDED (audit A7): the letter-spelling Discovery line; any fast-flush change.

### T3.4 `engine/agent/llm.json` — mirror the SAME lines into Intake/Discovery/Closer/Offer `state_prompt` strings at the same positions (llm.json's own base — NOT a full sync; Intake/Discovery/Closer are pre-drifted, audit A2). Lines verified JSON-safe (no `"`/`\`, zero `refer` occurrences → refer-count stays 36). After edit: `python3 -c "import json; json.load(open('agent/llm.json'))"` + `pytest tests/test_iter43_prompts.py` (Offer lockstep stays byte-identical).

### T3.5 Legacy tests (audit A3 — exact updates)
- `tests/test_iter31_c3_prefix.py` L201: `["Let", "'s", " dig", " in", "."]` → `["Let", "'s", " dig", " in", " —", " what", " breaks", " first", "?"]`
- `tests/test_iter40_spike_readback.py` L364: `["Perfect", ",", " moving", " on", "."]` → `["Perfect", ",", " moving", " on", " —", " good", "?"]`
- `tests/test_iter44_cache_floor.py` L388 + `tests/test_iter46_latency_floor.py` L215: → the test_iter31 tokens.

### T3.6 Pin — new `engine/tests/test_iter70_transition_beat.py` (~130 lines)
- pin 1: flat transition ack → exactly ONE continuation round in the destination (3 LLM rounds total), continuation ends in a spoken "?"
- pin 2: ack WITH a spoken "?" → one-trip finalize (no continuation)
- pin 3: ack whose "?" sentence is exact-window-dropped → continuation fires (post-filter truth)
- pin 4: silent + transition round → today's routing (no finalize, destination round)
- pin 5 (cross-ref G-4): turn_asked CARRIES across rounds — round 1 asks, round 2 flat-transitions → finalize (no continuation)

### T3.7 Verify + HITL stop (two owner items)
`pytest tests -q`. Report diff + results. **Owner flag (cross-ref G-1/A17):** "Engine guarantee applies to ALL state transitions (incl. contact_details→ConfirmSlots, phaseb-excluded); the scripted-question prompt directive ships only in Intake/Discovery/Closer/Offer (reference scope) — OK?" Then ask the **T4' threshold sign-off** (next gate).

---

## TASK T4' — Same-turn jaccard dedupe — ONE commit — **owner must sign off thresholds first: min_words=4, overlap=0.80, fillers `well|so|ok|okay|um|uh|hey|sorry|alright`**

**Commit 3:** `iter70 T4': same-turn near-duplicate dedupe — token jaccard >= 0.80 (min 4 words, filler-stripped) after the exact-window check at BOTH flush sites; own knobs tts_dedupe_similar/_overlap/_min_words; speech_replay mirror; NO embedder, same-turn scope only`

### T4'.1 `engine/diallux/config.py` — after the T2 block
```python
    # iter70 T4' (owner option 2): same-turn NEAR-duplicate sentence dedupe —
    # after the exact-window check, a sentence whose normalized token jaccard
    # vs any spoken sentence of THIS turn >= overlap is dropped from SPEECH
    # only. Same-turn scope (window resets at ingest); NO embedder.
    tts_dedupe_similar: bool = True
    tts_dedupe_similar_overlap: float = 0.80
    tts_dedupe_similar_min_words: int = 4
```

### T4'.2 `engine/diallux/graph/builder.py` — helper after `_norm_sentence` (L216) + 2 insertions
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
Mid-stream (after the exact check L2323-2324, BEFORE the semantic block — cross-ref G-3 order):
```python
                            if key and spoken_any and runtime.settings.tts_dedupe_similar \
                                    and _similar_dup(key, window, runtime.settings):
                                continue            # in-turn near-duplicate — never spoken
```
Stream-end (top of the `if not (pending_key and spoken_any and pending_key in window):` gate, L2420):
```python
                        if pending_key and spoken_any \
                                and runtime.settings.tts_dedupe_similar \
                                and _similar_dup(pending_key, window, runtime.settings):
                            pending_key = None      # in-turn near-duplicate — never spoken
```
Plus one-word guard on the semantic line below it (prevents a dead-path embed after the drop; no behavior change when similar is off):
`pending_is_q = runtime.settings.tts_dedupe_semantic and pending_key and "?" in pending_text`
Size law: ≤15 lines per flush site — met (4 + 5).

### T4'.3 `engine/scripts/speech_replay.py` — mirror
- `_S.__init__` (after L46): `tts_dedupe_similar` / `tts_dedupe_similar_overlap` / `tts_dedupe_similar_min_words` env passthroughs (defaults True/0.80/4)
- import list (L27-33): + `_similar_dup`
- `replay()` after the exact check (L154-157):
```python
            if key and spoke_any and s.tts_dedupe_similar \
                    and _similar_dup(key, exact, s):
                cuts["similar"] += 1
                print(f"  [CUT similar jaccard] {sent!r}")
                continue
```
- `cuts` init (L111) + summary print (L287-289): + `"similar"`.

### T4'.4 Pin — new `engine/tests/test_iter70_similar_dedupe.py` (~80 lines)
near-dupe dropped (window unchanged by the drop) · distinct question kept (jaccard < 0.80) · **cross-turn near-dupe KEPT** (ingest reset — the iter59 guarantee pin) · <4-token sentence never checked · knob off = byte-exact today.

### T4'.5 Verify + HITL stop
`pytest tests -q`; report; owner A/B by ear happens at T6 (knob `TTS_DEDUPE_SIMILAR=false` toggles on the lane).

---

## TASK T4p — Prompt-side repetition wording — **DROPPED by owner (2026-09-23, in-session)**
Owner verdict after reading `general_prompt.md`: "no that's stupi… I have a rule about it". The rule ALREADY EXISTS:
- `general_prompt.md:21` — `NEVER repeat yourself; if you just covered something, don't bring it up again` (rides EVERY state head)
- `general_prompt.md:9` — `NEVER REPEAT A FILLER PHRASE DURING A CALL` · `:20` — vary openings
- Per-state variants already live: `Discovery.md:61` (pricing deferral varies wording), `Offer.md:10` (never read one verbatim twice)
Adding a near-duplicate directive = the iter68 overengineering class. No commit. Cross-turn redundancy handling stays prompt-side as-is. (Draft line + target options below are VOID.)
Draft line (owner must approve VERBATIM in chat): `never say the same or near-same sentence twice this call; when re-asking, change the wording AND shorten`

---

## TASK T5 — Observability lines — ONE commit

**Commit 5:** `iter70 T5: speech_filter observability — INFO line per filter drop/split (sanitize|exact|similar|fast_flush, 7 sites) + mic_events CUT/REASK tags + replay parity (forensics only, zero behavior change; port of c6159ce re-scoped tiny)`

### T5.1 `engine/diallux/graph/builder.py` — helper (after `_similar_dup`) + 7 call sites
```python
def _log_filter(settings, stage: str, sent: str, state_name: str,
                state: dict) -> None:
    """iter70 T5: ONE INFO line per speech-filter drop/split so every cut is
    visible live (journal + mic_events CUT tag). stage ∈ {sanitize, exact,
    similar, fast_flush}; observability only — never changes behavior."""
    log.info("speech_filter stage=%s sent=%r state=%s turn=%s",
             stage, sent, state_name, state.get("turn_index"))
```
Sites (cross-ref C-3: SEVEN):
1. mid-stream fast-flush split — set `ff_cut = bool(cut)` in the elif branch (L2284-2294), log `"".join(head_tokens)` as `fast_flush` right after the token-split loop
2. mid-stream sanitize drop (before `continue` at L2319) — `sent_raw`
3. mid-stream exact drop (L2323-2324) — `sent`
4. mid-stream similar drop (the T4' site) — `sent`
5. stream-end sanitize drop (L2413-2414) — `pending_text`
6. stream-end exact drop — companion branch BEFORE the existing gate (cross-ref C-4 shape, zero behavior change):
```python
                    if pending_key and spoken_any and pending_key in window:
                        _log_filter(runtime.settings, "exact", pending_text,
                                    state_name, state)
                    if not (pending_key and spoken_any and pending_key in window):
                        …existing block…
```
7. stream-end similar drop (the T4' site) — `pending_text`
`semantic` stage intentionally NOT logged (env-dead branch — cross-ref C-2).

### T5.2 `engine/scripts/mic_events.py` — RULES after `TURN` (L51):
```python
    ("CUT",     re.compile(r"speech_filter stage=")),
    ("REASK",   re.compile(r"pause[ _-]re.?ask|re-ask firing")),
```
`_CALL_TAGS` (L87-88) += `"CUT", "REASK"`.

### T5.3 Pin — extend `test_iter70_similar_dedupe.py` (or `test_iter70_filter_log.py`): FakeLLM round with a code artifact + a near-dupe → caplog asserts `speech_filter stage=sanitize` AND `stage=similar` lines with state/turn fields.

### T5.4 Verify + HITL stop
`pytest tests -q`; `speech_replay.py <recent-micbridge-trace>` output shape matches journal CUT lines.

---

## TASK T6 — Battery + lane deploy + owner ear test (no code)
1. Battery (background-safe): `cd /tmp/opencode/wt-iter70/engine && set -a && . ./.env && set +a && setsid nohup .venv/bin/python tests/llm2llm/harness.py --personas happy3 --rag --langfuse --max-turns 48 > /tmp/opencode/iter70_battery.log 2>&1 < /dev/null &` — gate **3/3 BOOK**. (Proves T3/T4'/T5 speech behavior + booking flow; T2 is session-layer — mic-lane proof only, cross-ref G-2.)
2. Lane deploy (verbatim plan block): `git checkout-index --prefix=/tmp/opencode/iter70_stage/ -af` from the worktree → copy builder.py / config.py / state.py / session.py / llm.json / prompts/*.md / mic_events.py / speech_replay.py into the main checkout's engine → `systemctl --user restart diallux-8024.service && sleep 5 && journalctl --user -u diallux-8024.service -n 10 --no-pager | grep "cartesia connected"` — MUST print `model=sonic-3.6-2026-08-27`.
3. Owner ear checklist (`https://flores.diallux-ai.site/voice24/mic?k=$VOICE_TEST_TOKEN`): (1) pause re-prompt ~10s ONCE, rephrased, no loop; (2) transition acks carry the next question in the SAME turn; (3) same-turn near-dupe NOT spoken; (4) cross-turn scripted re-asks STILL AUDIBLE (iter59 must not return); (5) voice UNCHANGED.
4. Ledger (MAIN-repo SDK only): `python3 /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py import --window "HH:MM-HH:MM" --run chat-iter70-happy --commit <sha>` → `gates --a chat-iter65-happy --b chat-iter70-happy` green on G1/G2/G4 → report `research/surgeon/iter70-speech-fixes/01_report.md` → CANCEL test bookings (event 3801235 is REAL).

## TASK T7 — Closeout
Lane RESTORE: `git -C /home/julio/projects/clean_diallux_SDR checkout -- engine/diallux engine/agent/llm.json engine/scripts && systemctl --user restart diallux-8024.service`. `hitl_ping.py` the merge ASK (LAW 0). PENDING_TASKS PT-68/69(second row)/70 status updates → docs commit on MAIN (rule 3).

---

## Validation sequence (end-to-end)
1. Every T: HITL stop (diff shown → owner GO → commit → suite green → report).
2. Suite baseline discipline at every commit (rule 4).
3. Battery happy3 3/3 BOOK; ledger gates green via SQL.
4. Lane serves the branch for the ear test; cartesia pin verified; lane restored after.
5. Owner ear verdict = the ONLY merge gate; merge = owner only (LAW 0).

## Deferred / excluded (do not do)
Fast-flush default flip + min_chars knob (PT-71 env carries it) · letter-spelling directive · cancel-safe gen spans · `speech_filter_observability` knob · STT zombie watchdog (PT-72) · mic WS 11-12s (PT-72) · Twilio merge (iter67) · industry KB pin · any cherry-pick from `engine/iter68-*`.

— MASTER PLAN complete. Zero open items. Awaiting owner GO on T2.
