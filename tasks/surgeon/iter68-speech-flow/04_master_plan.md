# 04 — MASTER PLAN: iter68 speech-flow (airtight — all flaws resolved, preflight-verified against main @ 8e06fe9)

- Date: 2026-09-23 · Status: **MASTER PLAN — awaiting owner GO. EXECUTE ONLY ON APPROVAL. STOP AT HITL.**
- Sources: `plans/plan_v5_iter68_speech_flow_v2.md` (owner-approved spec) + `archive/01_audit.md`, `archive/02_action_plan.md`, `archive/03_cross_reference.md` (this folder)
- **Twilio coexistence (owner directive): VERIFIED NO CONFLICT** with `engine/iter67-twilio-live-lane` @ `0394a3b` — single file overlap (`engine/diallux/config.py`), regions ≥45 lines apart, clean auto-merge in both orders (`git merge-tree` exit 0). See §9.

---

## 0. Preconditions

0.1 **Branch cut (LAW 0 — never stack onto an awaiting-merge branch):**
```
git -C /home/julio/projects/clean_diallux_SDR branch engine/iter68-speech-flow main
git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter68 engine/iter68-speech-flow
```
0.2 **Baseline recount (never hardcode):** `cd /tmp/opencode/wt-iter68/engine && .venv/bin/python -m pytest tests -q` → record N (expected 463; **470 if the Twilio branch already merged**). The worktree has no `.env` → code defaults rule. The main checkout shows 2 env-override failures (cartesia provider pin, fast-flush-off pin) — expected, NOT regressions (owner-confirmed intended env).
0.3 `engine/scripts/speech_replay.py` is ALREADY on main (`8e06fe9`) — no commit step anywhere in T1.
0.4 **Lane-deploy hygiene (Twilio coexistence):** :8024 test copies into the main checkout are TEMPORARY — after each live ear test: `git -C /home/julio/projects/clean_diallux_SDR checkout -- engine/diallux engine/scripts && systemctl --user restart diallux-8024.service`. The main checkout must be clean (except the pre-existing `docs/Testing_guidelines/MIC-CALL-ANALYSIS-SOP.md` mod) whenever the owner merges the Twilio branch, or git refuses (uncommitted `config.py`).
0.5 **Invariants (VOICE LAW / MODEL LAW):** any `.env` edit preserves `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27`, `TTS_PROVIDER=cartesia`, `OPENAI_MODEL=gpt-5.4`. `TTS_GATE_FAST_FIRST_FLUSH=false` stays (owner: fast-flush OFF). NEVER touch `:8021`/`:8022`, `engine/diallux/media/{prewarm,elevenlabs_tts,tts_factory}.py`, Cal.com event 3801235.

## 1. T1 — Speech-filter observability + cancel-safe gen spans

**`engine/diallux/graph/builder.py`:**
- Helper `_log_filter(stage, sent, state_name, state)` gated `settings.speech_filter_observability`:
  `log.info("speech_filter stage=%s sent=%r state=%s turn=%s", …)`.
- Instrument BOTH flush sites: `stage=sanitize` (:2318 mid, :2413 end), `stage=exact` (:2323, :2420), `stage=semantic` (:2352, :2436), `stage=fast_flush` (:2294 — a SPLIT event, log the fragment).
- Wrap the `astream` loop (:2268-2391) in try/except CancelledError → `finish_llm(gen_obs, output="", extra_meta={"cancelled": True})` → re-raise. Fixes the round-4 Langfuse gen gap (cancelled rounds never ended their spans).

**`engine/diallux/config.py`:** `speech_filter_observability: bool = True` (new iter68 block after :317).

**`engine/scripts/mic_events.py`:** RULES += `("CUT", re.compile(r"speech_filter stage="))`; Langfuse regex :148 += `|speech_filter|silence_reask`. Usage string documents the journald gotcha: `journalctl --user -u diallux-8024.service > /tmp/opencode/voice_server_journal.log` + `--log`.

**`engine/scripts/speech_replay.py`:** `--knobs` passthrough (`tts_dedupe_cos_threshold`, `scripted_pass_cos_threshold`, `tts_dedupe_semantic_exempt_states`, `tts_gate_fast_first_flush`) for offline calibration A/B.

**NEW `engine/tests/test_iter68_speech_filters.py`:** caplog pin per drop class (stage+state+turn correct); sanitizer byte-identical with observability off; fast-flush default False; `…_min_chars` + `…_chars` coexist.

**Verify:** compile-check (§8) · suite (N + new pins, 0 failed) · `speech_replay.py micbridge-ccacb090cc54` runs.

## 2. T2 — Deterministic transition beat + fast-flush OFF in code

1. **config.py :206:** `tts_gate_fast_first_flush: bool = True` → `False` (env already false — aligned). New `tts_gate_fast_first_flush_min_chars: int = 12` replacing hardcoded `comma >= 12` at builder.py:194; comments cross-reference `…_chars` (=28, total-buffer threshold).
2. **UPDATE existing pin** `engine/tests/test_iter46_latency_floor.py::test_fast_first_flush_before_stream_end` — construct Settings with `tts_gate_fast_first_flush=True` explicitly (default is now False; the pin asserted default-ON).
3. **`turn_asked` flag (new GraphState key):** set True in the token loop when a SPOKEN sentence contains `?` (mid-stream :2356-2358, stream-end :2440-2444 — post-filter truth); reset in `ingest` next to `turn_spoke` (:2722); carried in `updates` (:2469).
4. **Transition continuation — reuse the EXISTING entry_lite ack (:1803-1808), routing change only** in `route_after_deterministic` (:2784):
```python
if self.settings.one_trip and executed and all(
        FIRE_AND_FORGET.match(t["name"])
        or (t["name"].startswith("transition_to_") and t.get("status") == "ok")
        for t in executed):
    if state.get("round_spoke") and (
            state.get("turn_asked")
            or not any(t["name"].startswith("transition_to_") for t in executed)):
        return "finalize"
    # ok transition + caller heard no '?' → destination state node:
    # entry_lite renders EXACTLY ONE speech-only continuation round
```
5. **Prompts `Intake.md`/`Discovery.md`/`Closer.md`:** turn-end question rule; transition directive (ack → destination's first scripted question IF it fits, else ONE contextual question — no blind splicing, owner rule); letter-by-letter company spelling + confirmation on first capture. Regenerate `agent/llm.json` `state_prompt` fields minus `#[refer]`; parity `grep -c 'refer' agent/llm.json` = 36 before/after.
6. **NEW `engine/tests/test_iter68_round_yield.py` (part 1):** ack-without-`?` → exactly one continuation round ending in `?`; ack-with-`?` → none; muted-`?` (content had `?`, dedupe cut it) → continuation fires.

## 3. T3 — Scripted full-pass + per-state gate + 2-strike + silence re-ask

1. **Scripted registry (graph init, off hot path):** `<...>` spans per state from `runtime.prompts` (`_SCRIPTED_RE = re.compile(r"<([^<>\n]{4,200})>")`), `_norm_sentence` keys, ONE batched embed (store absent → empty registry, tiers no-op, never block).
2. **Full-pass BEFORE the semantic drop (both sites :2340/:2427):** tier 1 exact dict hit → speak; tier 2 flex cos ≥ `scripted_pass_cos_threshold` (0.85) vs the CURRENT state's span vecs (reuses the :2343 qvec) → speak; else existing semantic check.
3. **Per-state gate (both semantic sites):** skip the semantic check when `state_name in tts_dedupe_semantic_exempt_states`. Exact casing (`"Intake"`; states are mixed-case — `contact_details` is lowercase).
4. **config.py:** `scripted_pass_cos_threshold: float = 0.85`; `tts_dedupe_semantic_exempt_states: tuple = ("Intake",)`; `silence_reask: bool = True`; `silence_reask_ms: int = 2000`.
5. **`contact_details.md`:** 2-strike (strike-1 rephrase + alternative; strike-2 skip to next required field; NEVER verbatim ×3). Regenerate llm.json.
6. **Silence re-ask (`session.py` + `builder.py`):**
   - Timer armed after the turn's drain (post `_late_turn_report` :676-689); `silence_reask_ms` (2000); CANCEL on `StartOfTurn` / transcript growth / `_stopped` / `_ended`; ONE-SHOT per turn (no re-arm after the re-ask).
   - Invoke `graph.astream({"user_text": "", "silence_reask": True}, …)`. **ingest guard: silence_reask payload → NO history append** (today :2736-2739 appends an empty user message). State node injects post-history directive: "The caller went silent after your last question. Rephrase it ONCE, shorter and warmer, then stop. Do not call tools."
   - **Re-ask rounds are EXEMPT from the cross-turn semantic check** (engine-initiated, owner-sanctioned — the rephrase must not be muted by the dedupe this iteration fixes).
   - tracer span `silence_reask` (ms, turn, state).
7. **NEW `engine/tests/test_iter68_reask_escalation.py`:** 2-strike wording (no verbatim third ask); silence re-ask fires once at ~2s, cancels on speech, no empty user message, no second re-ask; scripted full-pass beats the semantic cut (exact + flex); Intake exempt; true loops (cos ≥ 0.95 non-scripted) still cut.

**Calibration (offline, before any live call):**
```
cd /tmp/opencode/wt-iter68/engine && set -a && . ./.env && set +a && \
.venv/bin/python scripts/speech_replay.py micbridge-ccacb090cc54 --fast-flush
```
→ the 8 previously-muted scripted re-asks now SPOKEN (flex tier); true loops still cut.

## 4. T4 — One spoken reply per turn (turn-32 fix)

**Design constraint:** tool calls are known only at stream END; TTS sentences flush DURING — suppression must be PREDICTIVE (prev-round), never retroactive.

1. **config.py:** `mechanical_round_silent: bool = True`.
2. **Chain-silencing (token loop):** a round whose PREVIOUS round's executed tools (`state["last_round_tool_calls"]` — pattern proven at :2124) were non-empty and all `_MECHANICAL_RE`-matched routes its tokens to a NULL writer (pending maintained, dropped at stream-end). Round 1 of a turn always speaks.
3. **Chain-end re-open:** `tool_call_start` naming `transition_to_*` mid-stream (same detection as the prewarm :2384-2387) → the current round IS the chain end: flush buffered pending + stream the remainder (this is the T2 ack).
4. **INVARIANT (F2):** `round_spoke` stays `bool(content)` — suppression is TTS-stream-only. The iter32 force_speech rule (:2124-2126) therefore NEVER fires mid-chain (tools stay available to `calculate_*`). Loop protection = `rounds_left` + `?`-yield.
5. **`?`-yield backstop (`route_after_deterministic`):** `if state.get("turn_asked") and executed: return "finalize"` — once the caller HEARD a question, no further LLM rounds without new caller input. **Pre-approved fallback (if battery shows lost leak-reveals): narrow to FIRE_AND_FORGET-only rounds** — one-line change.
6. **`test_iter68_round_yield.py` (part 2):** exact turn-32 sequence (extract_leak_inputs → calculate_monthly_leak → extract_closer_details+transition_to_Offer) → ONE spoken reply, ack at chain end; `?`-yield pin; force_speech-never-fires-during-chain pin.
7. **Accepted tradeoff:** silent chains = caller-side silence until the ack (owner-approved; no chain fillers this iteration — one-variable rule).

## 5. T5 — read-only TTFT autopsy + KB-coverage gate

No code. `journalctl --user -u diallux-8024.service` (dump → mic_events `--log`) + Langfuse `turn:1`/`warm:*` spans + ledger SQL. Decompose the 1,558 ms turn-1 TTFT (suspect `stt_eot_to_llm_first` 1,259 ms — flux handshake/adopt path). KB-coverage: chunks-per-turn, degraded%, KBs/call; starving → recommend industry pin (iter52 lane) as a SEPARATE owner decision. Any fix = NEW branch.

## 6. T6 — battery + report + ASK (HITL STOP)

```
cd /tmp/opencode/wt-iter68/engine && set -a && . ./.env && set +a && date +%H:%M && \
.venv/bin/python tests/llm2llm/harness.py --personas happy3 --rag --rag-fire-sim --langfuse --max-turns 48; date +%H:%M
```
- Import: `scripts/live_sql.py import --window "<HH:MM-HH:MM>" --run chat-iter68-happy --branch engine/iter68-speech-flow --commit <sha> --db research/surgeon/iter48-rag-truth/ledger.db`
- Gates: happy3 3/3 + Rourke booked; replay battery traces — no muted-scripted-question pattern; no 4-round leaks; ≤2 asks per missing field; transition acks never flat.
- Report → `research/surgeon/iter68-speech-flow/01_report.md` · `scripts/hitl_ping.py` the ASK · **STOP. Merge = owner only (iter68 AND Twilio).**
- Cancel ALL test bookings after the battery (Cal.com event 3801235 is REAL).

## 7. Docs (straight to main per LAW 0 docs lane)

`plans/PENDING_TASKS.md` += PT-65 (speech-filter observability), PT-66 (re-ask escalation + 2s silence rule), PT-67 (one-reply-per-turn + scripted full-pass). Plan file status field update.

## 8. Compile-check + suite (after EVERY file touched)

```
cd /tmp/opencode/wt-iter68/engine && .venv/bin/python -m py_compile diallux/graph/builder.py diallux/config.py diallux/media/session.py scripts/speech_replay.py scripts/mic_events.py
.venv/bin/python -m pytest tests -q     # N (from 0.2) + new pins, 0 failed
```
Lane deploy for live ear tests: copy edited files into the main checkout + `systemctl --user restart diallux-8024.service`; **restore per §0.4 after testing.** NEVER touch `:8021`/`:8022`.

## 9. Twilio branch coexistence (`engine/iter67-twilio-live-lane` — the open gap)

- **Files:** Twilio touches 10 files; iter68 touches none of them EXCEPT `engine/diallux/config.py` (Twilio adds `twilio_signature_check` @ ~:389-394; iter68 edits :165-:344) — ≥45 lines apart, clean auto-merge BOTH orders (`git merge-tree` verified, exit 0).
- **app.py** (Twilio's `transport="twilio"` pin) is never touched by iter68; **session.py** (iter68's silence re-ask) is transport-agnostic with `_stopped/_ended` guards incl. Twilio mark-hangup.
- **Suite:** Twilio = +7 pins. Baseline recount at cut (§0.2) handles either merge order.
- **Order:** any. Default = iter68 executes now, Twilio merges whenever the owner is ready. NO rebase, NO stacking (LAW 0 v2.1). `scripts/git-tree.sh` after both merges (LAW 5).

## 10. Resolved-flaws ledger (all F1-F12 closed)

F1 staleness (§0.1/0.3) · F2 force_speech (§4.4 invariant + pin) · F3 entry_lite reuse (§2.4) · F4 turn_asked (§2.3) · F5 silence-re-ask path (§3.6) · F6 knob naming (§2.1) · F7 iter46 pin (§2.2) · F8 journald (§1) · F9 baseline (§0.2) · F10 dead-air (§4.7) · F11 casing (§3.3) · F12 lane-deploy hygiene (§0.4). **Zero open issues. Awaiting owner GO.**
