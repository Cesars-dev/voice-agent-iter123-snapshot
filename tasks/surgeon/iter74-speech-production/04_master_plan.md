# 04 MASTER PLAN — iter74 SpeechLedger (airtight)

All preflight claims traced to live code on `engine/iter74-speech-production` @ `9ccdccf`. Zero open issues
(C1..C5 resolved in 03; F1..F11 folded in). This is the file the executor follows.

## Preflight verdicts (verified against actual code)

| Claim | Verified |
|---|---|
| Mid-stream flush site spans builder.py:2279-2373; stream-end 2408-2458; both under `tts_dedupe_sentences` | YES |
| `_sanitize_spoken` importable standalone (settings-only) | YES (builder.py:226) |
| `_similar_dup` verbatim-portable from `02b4bef` (needs `re`, `_SIMILAR_FILLERS`, `_WORD_RE`) | YES |
| `_log_filter` verbatim-portable from `87a0ce5` | YES |
| Watchdog diff `95f7ace` applies to current deepgram_stt.py (no drift: __init__/connect/send_audio/close/_recv_loop anchors all match) | YES |
| `writer` in scope at both flush sites + revive site (`get_stream_writer()` bound before token loop) | YES |
| `state_node` has `state` (round-start dict), `dvs`, `updates` in scope at flush sites | YES |
| force-speech site builder.py:2125 reads `state` (previous round's flags) | YES |
| `route_after_deterministic` builder.py:2784-2803 | YES |
| ingest builder.py:2716-2755; payload builder at session.py:644-651 | YES |
| GraphState additions safe (total=False TypedDict; no unknown-key errors) | YES |
| pydantic Settings reads `.env` from cwd (F1 root cause) | YES (config.py:33-35) |
| Suite baseline canonical: 3 failed (F1 list) / 460 passed | YES (measured 2026-09-24) |

## Exact execution steps (in order)

### Commit 1 — T1 (files: builder.py, state.py, speech_replay.py, mic_events.py, tests/test_iter74_speech_ledger.py)
1. builder.py — after `_norm_sentence` (L216): insert `_SIMILAR_FILLERS`, `_WORD_RE`, `_similar_tokens`,
   `_similar_dup` (verbatim 02b4bef) + `_log_filter` (verbatim 87a0ce5, docstring stage set extended:
   sanitize|exact|similar|semantic|clamp|revive).
2. builder.py — after `_log_filter`: `SpeechLedger` class per 02 §Design. Constructor:
   `SpeechLedger(settings, state_name, state, embedder=None)`. `flush()` is `async`; stage order
   fast_flush-log → sanitize → exact → similar → semantic → clamp → emit. Clamp knobs via
   `getattr(settings, "tts_max_questions_round", 1) / ("tts_max_questions_turn", 2)` with
   `tts_max_questions_enabled` implicit by knob>0.
3. builder.py — state_node: replace `window`/`stem_window`/`spoken_any` init block (L2257-2267) with ledger
   construction (window copied from state; `spoken_any = bool(state.get("turn_spoke"))`);
   mid-stream sentence handling (L2297-2373) → cut head, `spoke, out = await ledger.flush(sent_raw,
   head_tokens, fast_flush=ff_cut)`, emit `out` via writer when spoke; stream-end block (L2408-2458) → same
   via `ledger.flush(pending_text, [pending_sent], stream_end=True)`.
4. builder.py — revive pass immediately after the stream-end flush block:
   `revived = ledger.revive()` → emit tokens (leading " " if round-start `turn_spoke` and no separator sent
   yet) — F5.
5. builder.py — `updates` (L2469+): add `"round_spoke_audio": bool(ledger.round_flushed)`,
   `"turn_questions": ledger.turn_questions`, `"speech_ledger": ledger.snapshot()`; keep
   `tts_sentence_window: ledger.window`.
6. builder.py — ingest patch += `"turn_questions": 0` and copy `reconcile_note` from payload state.
7. state.py — add 4 keys (incl. `reconcile_note: str`; speech_ledger = merge_dict — F2).
8. speech_replay.py — import SpeechLedger; replace `exact/stems` bookkeeping with one ledger per call
   (window reset per turn as today); CUT print uses the stage the ledger logged; knobs: add
   `tts_dedupe_similar/_overlap/_min_words` + `tts_max_questions_*` to `_S`.
9. mic_events.py — RULES += CUT/REASK, `_CALL_TAGS` += CUT, REASK (verbatim 87a0ce5).
10. tests/test_iter74_speech_ledger.py — pins (caplog for stage lines; FakeLLM/tool pattern from
    test_iter60; knobs set explicitly).

### Commit 2 — T2 (builder.py, config.py, tests/test_iter74_clamp_nevermute.py)
1. config.py — `tts_max_questions_round: int = 1`, `tts_max_questions_turn: int = 2`
   (place near `tts_dedupe_*` block ~L304-317).
2. builder.py — clamp already in ledger (commit 1); wire revive stage list {exact, similar, clamp};
   L2125 `force_speech = (not (state.get("round_spoke", True) or state.get("round_spoke_audio", False)))...`
   (audio truth; round_spoke kept in the OR for compatibility).
   route_after_deterministic: replace `state.get("round_spoke")` in BOTH one-trip checks (L2798, L2800)
   with `state.get("round_spoke") or state.get("round_spoke_audio")`.
3. tests/test_iter74_clamp_nevermute.py — the 4 pins of 02 §Commit-2.

### Commit 3 — T3 (session.py, sentence_gate.py, builder.py, tests/test_iter74_reconcile.py)
1. sentence_gate.py — `_spoken: list[str] = []` in `__init__`; append flushed text in `_flush_upto` (L125)
   and `end_of_turn` (L69-70); in managed mode append in `add` when buffer flushed (managed forwards tokens:
   append token to `_spoken` too); `heard_prefix(limit=400)` = tail of "".join; clear in `reset`/`close`.
2. session.py — `_reconcile_note` field; `_capture_reconcile()`; call sites: `_on_start_of_turn` before
   `gate.reset()`, `_on_turn_resumed` cancel path before `gate.reset()`, `_grace_then_cancel` expiry path,
   `_on_eot` non-eager cancel (L395 region). `_run_turn`: payload += note (clear after use).
   Note = "Your last turn was interrupted mid-speech before the caller could hear all of it. The caller last
   heard: \"{prefix}\". Tools already fired: {names or none}; their results are already in the conversation.
   {plan wording: Continue the conversation naturally from [last heard context]. Don't repeat full sentences
   you already said.}" — no task pressure (resolved decision).
3. builder.py — state_node first-round delta: if `state.get("reconcile_note")` and
   `rounds_left == self.settings.max_tool_rounds` → prepend to `rag_delta` as a system directive block +
   `updates["reconcile_note"] = ""`.
4. tests/test_iter74_reconcile.py — pin via captured deltas (stream_mode custom + updates; assert the
   post-history delta string contains the note fragments; no-note control).

### Commit 4 — T4 (deepgram_stt.py, config.py, tests/test_iter74_stt_watchdog.py)
1. config.py — `stt_watchdog_ms: int = 3000` (Deepgram section ~L351).
2. deepgram_stt.py — verbatim 95f7ace port; `_watchdog_loop` dead-threshold = `max(1.0,
   settings.stt_watchdog_ms / 1000)`; poll stays 2.0s; flowing window 3.0s; `_last_send_ts` stamp in
   `send_audio`; `_last_recv_ts` in `_recv_loop`; cancel watchdog in `close()`.
3. tests/test_iter74_stt_watchdog.py — fake ws; monkeypatched time/sleep via small real sleeps (2.0s poll →
   use watchdog knob small (e.g. 300ms) + poll sleep constant read from settings? NO — poll constant is
   hard-coded 2.0s; test drives real asyncio sleeps with tiny knob = still 2s wall → acceptable (T4 pins run
   in <6s) or patch asyncio.sleep in the loop module. DECISION: monkeypatch `asyncio.sleep` inside
   `_watchdog_loop` scope via `diallux.media.deepgram_stt.asyncio.sleep` replacement for speed, real
   behavior for send/recv stamps.

### Commit 5 — T5 (config.py, 3 baseline test files, llm.json parity report)
1. config.py — L206 → `tts_gate_fast_first_flush: bool = False`; L309 → `tts_dedupe_semantic: bool = False`.
2. tests/test_iter46_latency_floor.py — `_settings()` stays; the failing test passes
   `tts_gate_fast_first_flush=True`; add `test_fast_first_flush_default_off` pin.
3. tests/test_iter59_dedupe_semantic.py — default pin `is False`; `_t4_settings` callers that exercise the
   semantic path set `tts_dedupe_semantic=True` explicitly (test_iter60 AUD-6 does this in its own file).
4. tests/test_iter60_audit_fixes.py — AUD-6 test passes `tts_dedupe_semantic=True` to `_t4_settings`.
5. llm.json parity check (read-only): state_prompt vs prompts/*.md byte-diff; filler-line scan; `refer`=36.
   Drift → report only.

### T6 — battery + lane + report (no code)
Per plan T6 commands verbatim; ledger backup ritual first (`ledger.db` → `.bak`); import window filled from
actual battery timestamps; gates vs `chat-iter65-happy`; lane restart + journal provider-pin grep;
report to `research/surgeon/iter74-speech-production/01_report.md`; cancel test bookings (event 3801235 REAL);
OWNER EAR CHECKLIST = the behavior gate (5 items).

### T7 — closeout (owner-gated, LAW 0)
Lane restore `git checkout -- engine/diallux engine/agent/llm.json engine/scripts` + service restart; docs
(PENDING_TASKS rows, ITERATIONS note) straight to main per DOCS rule; `hitl_ping.py` ASK; merge/tag only on
owner say-so. Rollback point = `9ccdccf` (`git switch engine/iter73-playback-rate`).

## Test-count ledger
| Stage | Expected |
|---|---|
| T0 baseline (canonical) | 3 failed, 460 passed (F1) |
| After commit 1 | +5-7 new pins, baseline failures unchanged (fixed only in commit 5) |
| After commit 5 | suite GREEN (baseline 3 resolved) |
| T6 battery | 3/3 BOOK happy3 |

## Rollback
Per-commit revert on the branch; prod rollback = `git switch engine/iter73-playback-rate` (prod untouched at
9ccdccf). No merge without owner say-so.

Archive: this folder holds 01-04; execution evidence goes to `research/surgeon/iter74-speech-production/`.
