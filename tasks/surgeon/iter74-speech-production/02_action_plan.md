# 02 ACTION PLAN — iter74 SpeechLedger

Maps every audit gap/finding (F1..F11) to a concrete change. Commit ladder = plan T1..T5, one commit each.

## Design: `SpeechLedger` (builder.py, placed after `_log_filter` / before `_sanitize_spoken` region)

One class owns EVERY speech cut. Both flush sites (mid-stream builder.py:2279-2373, stream-end 2408-2458)
delegate to it; nothing else cuts speech.

```python
class SpeechLedger:
    # fields: settings, state_name, turn, window, stem_window, spoken_any,
    #         round_flushed=0, round_questions=0, turn_questions,
    #         cuts=[]  # (stage, text) — revivable stages: exact|similar|clamp (NOT sanitize)
    # def flush(self, sent_raw, tokens, *, fast_flush=False) -> (spoke: bool, out_tokens: list[str])
    #     async — stages in order:
    #       0. fast_flush split log (if fast_flush=True)
    #       1. sanitize      -> None drop, log stage=sanitize, DEAD (not revivable)
    #       2. exact window  -> log stage=exact, cuts.append
    #       3. similar jaccard (ported 02b4bef) -> log stage=similar, cuts.append
    #       4. semantic stem (port of 2339-2353; log stage=semantic)
    #       5. question clamp: "?" in sent and
    #          (round_questions >= tts_max_questions_round or turn_questions >= tts_max_questions_turn)
    #          -> log stage=clamp, cuts.append
    #       6. emit: window.append(key), spoken_any=True, round_flushed+=1,
    #          round_questions/turn_questions bump on "?" sentences
    # def revive(self) -> list[str]   # called at stream end when round_flushed==0 and cuts:
    #     emits revivable cuts in order, appends window keys, bumps question counts, logs stage=revive
    # def snapshot(self) -> dict      # {flushed, cuts, round_questions, turn_questions} bounded (~20 cuts)
```

Ledger takes an `embedder` callable so `speech_replay.py` can import the SAME class (F-plan mirror requirement).
In builder the embedder is `lambda sent: _embed_stem(runtime, sent)`; in replay it wraps `local_embed_fn`.

## File changes per commit

### Commit 1 — T1 SpeechLedger core
- **diallux/graph/builder.py**: port `_similar_dup` + `_log_filter` (verbatim from 02b4bef/87a0ce5); add
  `SpeechLedger`; mid-stream sentence loop and stream-end pending block become `await ledger.flush(...)`
  calls; `writer` emits the returned tokens; revive pass at stream end (F3/F5: separator when
  `turn_spoke`-at-round-start and nothing flushed); `updates` += `round_spoke_audio` = bool(round_flushed),
  `turn_questions`, `speech_ledger` (dict, merge_dict reducer — F2), window/back-compat keys unchanged.
- **diallux/state.py**: + `speech_ledger: Annotated[dict[str, Any], merge_dict]`,
  + `round_spoke_audio: bool`, + `turn_questions: int`, + `reconcile_note: str` (T3 needs it in the schema).
- **ingest (builder.py:2722-2736)**: + `"turn_questions": 0`; copy payload `reconcile_note` → patch.
- **scripts/speech_replay.py**: `from diallux.graph.builder import SpeechLedger`; replay loop feeds each
  sentence through one ledger; CUT labels = stage (sanitize/exact/similar/semantic/clamp).
- **scripts/mic_events.py**: RULES += `("CUT", speech_filter stage=)`, `("REASK", pause|re-ask)`;
  `_CALL_TAGS` += CUT, REASK (port 87a0ce5).
- **tests/test_iter74_speech_ledger.py** (pins): sanitize drop logged; exact dup dropped; jaccard near-dup
  dropped (knob on); `round_spoke_audio` True only when a sentence flushed; window resets at ingest;
  speech_ledger rides updates.

### Commit 2 — T2 question clamp + never-mute
- **builder.py**: clamp inside `ledger.flush` (knob `tts_max_questions_round=1`, `tts_max_questions_turn=2`);
  revive pass at stream end (cuts stage ∈ {exact, similar, clamp}); force-speech site L2125 reads
  `round_spoke_audio` (default False); `route_after_deterministic` one-trip/silence-guard finalize reads
  `round_spoke or round_spoke_audio` (F6) so a revived round finalizes with ZERO extra LLM rounds.
- **config.py**: + the 2 knobs.
- **tests/test_iter74_clamp_nevermute.py**: 4-question one-breath dump → exactly 1 spoken;
  ConfirmSlots ask→tool→reveal (2 questions over 2 rounds) unaffected; fully-muted round revived
  straight to TTS, zero extra rounds; sanitizer artifacts stay dead (revive skips them).

### Commit 3 — T3 cancel-reconcile
- **sentence_gate.py**: track flushed text (`_spoken` list; append in `_flush_upto` + `end_of_turn`);
  `heard_prefix(limit=400)` accessor; cleared in `reset()`/`close()`.
- **session.py**: `_reconcile_note: str|None = None` in `__init__`; `_capture_reconcile()` (async): heard-prefix
  from gate + fired-tools/result snapshot from `await runtime.graph.aget_state(_thread_config)`
  (`last_round_tool_calls`, `dvs.chain_aborted_*`); note text EXACTLY:
  "Continue the conversation naturally from [last heard context]. Don't repeat full sentences you already said."
  with heard-prefix + fired tools + "do not repeat, reveal" framing (resolved-decisions wording). Called in
  `_on_start_of_turn` (BEFORE gate.reset()), `_on_turn_resumed` cancel path, `_grace_then_cancel` expiry,
  and `_on_eot` non-eager cancel (F4). `_run_turn` payload += `reconcile_note` when set (then clears).
- **builder.py**: ingest passes `reconcile_note` through; state_node appends it to the post-history delta on
  the FIRST round only and clears via updates (F8).
- **tests/test_iter74_reconcile.py**: cancel mid-round after `extract_*` fired → NEXT turn's first-round delta
  contains the note; no note without cancel; history gains no text beyond the note.

### Commit 4 — T4 STT watchdog
- **deepgram_stt.py**: port 95f7ace verbatim (~45 lines) with `_watchdog_ms` from `settings.stt_watchdog_ms`
  (3000) replacing the 6s constant; fire `on_disconnect` ONCE; disarm after first server message (F10);
  cancel in `close()` loop.
- **config.py**: + `stt_watchdog_ms: int = 3000`.
- **tests/test_iter74_stt_watchdog.py**: fake WS; 3s streamed audio zero server messages → exactly one
  reconnect; first message <3s → disarmed, zero reconnects.

### Commit 5 — T5 env-trap flips + llm.json parity (includes F1 test repairs)
- **config.py**: L206 `tts_gate_fast_first_flush: bool = False`; L309 `tts_dedupe_semantic: bool = False`.
- **tests/test_iter46_latency_floor.py**: `test_fast_first_flush_before_stream_end` → construct settings with
  explicit `tts_gate_fast_first_flush=True` (behavior pin when knob on; default-off pinned in a new assert).
- **tests/test_iter59_dedupe_semantic.py**: `test_semantic_threshold_config_defaults` → `is False` + knobs;
  `_t4_settings` users that test the SEMANTIC path (test_iter60 AUD-6) get explicit `tts_dedupe_semantic=True`.
- **tests/test_iter60_audit_fixes.py**: AUD-6 test settings gain explicit `tts_dedupe_semantic=True`.
- **llm.json**: READ-ONLY parity check (fillers live in prompts/*.md; drift = report only, edit on owner GO).
  `refer` substring count must stay 36.

## Validation per commit
Subset pins → full suite (canonical env ritual) before next commit. After commit 5: suite green
(3 baseline failures resolved by F1 repairs). T6 = battery + lane + ear test (owner-gated), T7 = closeout.
