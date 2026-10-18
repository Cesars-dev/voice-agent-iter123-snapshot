# 01 AUDIT — iter74 SpeechLedger (spoken-truth layer)

Date: 2026-09-24 · Branch: `engine/iter74-speech-production` @ `9ccdccf` (verified)
Plan: `plans/plan_v5_iter74_speech_production.md` · Framework: SURGEON (audit before blade)

## 1. Git state (verified)

- Branch `engine/iter74-speech-production` exists, tip = `9ccdccf` (iter73 playback-rate) ✓
- Working tree: engine CODE is clean. Dirty = `GIT_TREE.md`, `docs/Testing_guidelines/MIC-CALL-ANALYSIS-SOP.md`,
  `engine/eval/llm2llm_report.json` (evidence/docs) + untracked plan/surgeon folders. No conflict with the
  files this plan edits.
- Salvage refs verified: `02b4bef` (jaccard `_similar_dup`), `87a0ce5` (`_log_filter` + mic_events CUT/REASK),
  `95f7ace` (STT watchdog) all reachable.

## 2. What EXISTS (traced to real lines, builder.py @ 9ccdccf)

| Mechanism | Where | Notes |
|---|---|---|
| `_sanitize_spoken` | builder.py:226-238 | knobs `tts_sanitize_tokens` (config.py:174). Drops `function_calls` token, `{}` `[]` `=>` `":` |
| Exact-window dedupe (mid-stream) | builder.py:2323-2324 (`key in window and spoken_any → continue`) | window = `state["tts_sentence_window"]`, reset at ingest (builder.py:2734) |
| Exact-window dedupe (stream-end) | builder.py:2420 (`if not (pending_key and spoken_any and pending_key in window)`) | |
| Semantic stem dedupe | builder.py:2339-2353 (mid), 2426-2439 (end) | gated `tts_dedupe_semantic` (config.py:309, default True); embed via `_embed_stem` (builder.py:241) |
| `round_spoke = bool(content)` | builder.py:2471 | CONTENT-based truth — the root-cause line |
| force-speech guard | builder.py:2125-2153 (`force_speech = (not state.get("round_spoke", True)) and prev_tools all-mechanical`) | reads content truth, not audio truth |
| `turn_spoke` | builder.py:2470 | content-based, kept for compatibility |
| Silence-guard routing | builder.py:2784-2803 (`route_after_deterministic`), 2798-2802 one-trip checks `state.get("round_spoke")` | a revived-but-content-empty round would loop → must read audio truth for finalize |
| `_fast_flush_cut` | builder.py:190-199 | gated `tts_gate_fast_first_flush` (config.py:206, default True) |
| Engine fillers | builder.py:292-299, emitted direct via `writer` at 2512-2516 + 2675-2681 | NOT in the ledger path (not LLM sentences; not questions) |
| Sentence gate | sentence_gate.py:35-147 | `_flush_upto` L125, `end_of_turn` L62, `reset` L77 (barge-in), NO spoken-text tracking |
| Barge-in cancel | session.py:583-606 `_on_start_of_turn` (cancel L590, gate.reset L595) | |
| Eager cancel | session.py:517-546 `_on_turn_resumed` (cancel L541); session.py:548-567 `_grace_then_cancel` | third cancel site: `_on_eot` non-eager path session.py:395 `self._turn_task.cancel()` |
| Ghost-speech pollution | session.py:656-658 CancelledError → `gate.reset()` only | history keeps speech the caller never heard (the root class) |
| STT watchdog | DOES NOT EXIST on this branch | lives on parked `95f7ace` (6s hard-coded) |
| Jaccard similar dedupe | DOES NOT EXIST on this branch | lives on parked `02b4bef` (verbatim portable) |
| `_log_filter` observability | DOES NOT EXIST | lives on parked `87a0ce5` (verbatim portable) |
| mic_events RULES | scripts/mic_events.py:31-49, `_CALL_TAGS` :88-89 | no CUT/REASK tags |
| speech_replay | scripts/speech_replay.py:37-50 `_S` stub, `replay()` L107 | no similar/clamp stages |
| GraphState | state.py:22-51 | keys: turn_spoke/round_spoke/tts_sentence_window/question_stem_window; NO speech_ledger/round_spoke_audio/turn_questions |
| ingest | builder.py:2716-2755 | resets window; NO turn_questions reset; NO reconcile note |
| payload flow | session.py:644-651 (`payload = {"user_text": transcript}`) | the channel for a reconcile note |
| prompts source of truth | builder.py:1657-1666 `_load_prompts` (prompts/*.md beats llm.json fallback) | |
| llm.json `refer` count | 36 substring hits (verified) | plan pin holds |
| Tests pinning OLD defaults | tests/test_iter46_latency_floor.py:323, tests/test_iter59_dedupe_semantic.py:46, tests/test_iter60_audit_fixes.py:266 | see flaw F1 |

## 3. What's MISSING (the gaps the plan fixes)

- No layer knows what was SPOKEN AUDIO-wise: `round_spoke`/`turn_spoke` are `bool(content)`.
- 3 independent inline filters (sanitize / exact / semantic) decide speech with no shared owner, no per-cut log.
- No question-count cap anywhere (the 4-question one-breath dump).
- No revive path: a round where every sentence was cut leaves the caller in silence; engine thinks it spoke.
- Cancelled turns leave no note; model answers fragments of context the caller never heard.
- No STT zombie-socket watchdog (the 2026-09-23 39s-dead adopted socket incident).
- Code defaults still the env-trap values (`tts_dedupe_semantic=True` @ config.py:309,
  `tts_gate_fast_first_flush=True` @ config.py:206) while `.env` carries the deliberate False overrides.

## 4. Bugs / risks / conflicts found

- **F1 (plan T0 flaw, MUST fix):** T0 claims "suite green"; actual canonical baseline = **3 failed, 460 passed**.
  Cause: `_settings()`/`_t4_settings()` construct pydantic `Settings` which reads `env_file=".env"` from cwd —
  so `TTS_GATE_FAST_FIRST_FLUSH=false` / `TTS_DEDUPE_SEMANTIC=false` leak into tests and break the
  old-default pins (test_iter46 `test_fast_first_flush_before_stream_end`, test_iter59
  `test_semantic_threshold_config_defaults`, test_iter60 AUD-6 `test_turn_opening_reask_dropped_when_window_nonempty`).
  The 3 tests isolate-green without cwd=.env. → T5 must ALSO update these 3 tests (pin new defaults / set knobs explicitly).
- **F2 (File Map typo):** plan says `speech_ledger: list[str]` with reducer `merge_dict` — a list cannot merge via
  a dict reducer. → `speech_ledger: Annotated[dict[str, Any], merge_dict]` (summary dict).
- **F3 (revive vs clamp interplay):** a round that speaks ONLY questions would be clamp-cut to 1 question — that
  is NOT a fully-muted round (1 flushed) → no revive. Revive must key on `flushed == 0 AND cuts non-empty`, and
  revived sentences must re-enter the question counts so the turn cap stays honest.
- **F4 (third cancel site):** `_on_eot` L395 cancels a still-running non-eager turn — a barge-in-class cancel the
  plan's File Map doesn't name. Cheap to hook with the same capture; included.
- **F5 (revive needs separator):** revived sentences appended after prior turns' speech need the leading " "
  separator when `turn_spoke` was True and nothing flushed this round.
- **F6 (revive vs routing):** `route_after_deterministic` finalizes/loops on `round_spoke` (content). A revived
  round with empty content would still loop ("silence guard") → extra LLM round + duplicate speech risk.
  Fix: one-trip/silence-guard finalize checks `round_spoke or round_spoke_audio`.
- **F7 (semantic stage log):** plan's stage list is `sanitize|exact|similar|clamp`; the semantic drop deserves
  `stage=semantic` visibility. mic_events CUT regex (`speech_filter stage=`) catches any stage — safe addition.
- **F8 (note must not repeat per round):** `reconcile_note` persists in GraphState unless cleared → state_node
  consumes it on the FIRST round only and clears via updates.
- **F9 (turn_questions reset):** ingest must reset `turn_questions: 0` (turn-scoped cap), and
  `question_stem_window` semantics stay untouched.
- **F10 (watchdog port nuance):** 95f7ace's watchdog uses hardcoded 6s/2s-poll/3s-flowing constants; plan knob
  `stt_watchdog_ms=3000` replaces the 6s. "Dead" condition = audio flowing and server NEVER sent a message
  (`_last_recv_ts is None`); the port's `return` on recv-once = disarm semantics, kept.
- **F11 (heard-prefix approximation):** "flushed-and-played" is approximated as flushed-to-TTS (the gate does not
  know playback); capture BEFORE `gate.reset()` at every cancel site. Bounded to last ~400 chars.

## 5. Environment (verified)

- Suite command runs green only with the canonical env ritual; venv is a copy-mirror (use
  `.venv/bin/python -m pytest`, never bin/pip). No new deps needed (watchdog/ledger = stdlib asyncio).
- `.env` has `TTS_GATE_FAST_FIRST_FLUSH=false`, `TTS_DEDUPE_SEMANTIC=false` (deliberate prod overrides).
