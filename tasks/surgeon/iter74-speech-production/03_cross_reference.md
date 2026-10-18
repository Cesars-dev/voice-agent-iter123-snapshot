# 03 CROSS-REFERENCE — audit ↔ action plan

Does the plan address every audit issue? Does the audit support every plan change? Verdict per item.

| # | Audit finding | Plan coverage | Verdict |
|---|---|---|---|
| F1 | T0 "suite green" false: 3 env-trap test failures pre-exist | 02 §Commit-5 repairs the 3 tests; master plan re-baselines T0 as "3 failed / 460 passed, all 3 = env-trap pins" | RESOLVED — plan flaw documented + fix folded into T5 |
| F2 | `speech_ledger: list[str]` + merge_dict is type-inconsistent | 02 §Design: dict + `Annotated[dict, merge_dict]` | RESOLVED (typed as plan File Map's "window+counts" intent) |
| F3 | Revive vs clamp interplay | 02 §Design: revive keys on `round_flushed==0 AND cuts`; revived questions re-count | RESOLVED |
| F4 | Third cancel site `_on_eot` L395 unnamed by plan | 02 §Commit-3 hooks it | RESOLVED (superset of plan, same mechanism) |
| F5 | Revive separator space | 02 §Design: separator when turn_spoke and nothing flushed | RESOLVED |
| F6 | Revive round would loop in routing | 02 §Commit-2: finalize reads `round_spoke or round_spoke_audio` | RESOLVED — required by T2's "zero extra LLM rounds" verification |
| F7 | `stage=semantic` + `stage=revive` log lines | mic_events CUT regex is stage-agnostic | RESOLVED (superset, observable) |
| F8 | Note must not repeat per round | 02 §Commit-3: first-round-only consumption + clear | RESOLVED |
| F9 | `turn_questions` reset at ingest | 02 §Commit-1 ingest patch | RESOLVED |
| F10 | Watchdog constants → knob | 02 §Commit-4: `stt_watchdog_ms=3000` replaces 6s | RESOLVED |
| F11 | heard-prefix ≈ flushed-to-TTS | 02 §Commit-3 capture-before-reset + bound 400 chars | RESOLVED (documented approximation) |

## Plan asks the audit supports (existence verified)

- ONE flush owner replacing inline filters: inline sites verified at builder.py:2317-2358 + 2408-2458; the
  sanitizer/exact/semantic stages port VERBATIM (lines read). SUPPORTED.
- Jaccard `_similar_dup` port: verified complete in `02b4bef` (self-contained, stdlib re). SUPPORTED.
- `_log_filter` port: verified in `87a0ce5` (pure logging). SUPPORTED.
- Watchdog port: verified in `95f7ace` — self-contained in deepgram_stt.py, no deps. SUPPORTED (knob swap only).
- force-speech site reads audio truth: site verified at builder.py:2125. SUPPORTED.
- state keys absent today (verified state.py) — additions only, no reducer conflicts. SUPPORTED.
- ingest is the natural note/clear/reset owner (verified builder.py:2716-2755). SUPPORTED.
- payload channel exists (session.py:644). SUPPORTED.
- prompts/*.md is source of truth; llm.json fallback (builder.py:1657-1666) — parity check scope correct.
  SUPPORTED. `refer`=36 verified TODAY (recheck at T5).
- Battery/ledger/rollback rituals all referenced from repo AGENTS/plan; no new infra needed. SUPPORTED.

## Contradictions / gaps found in cross-reference

- **C1:** plan T2 says never-mute is "at the force-speech site L2125-2153" while its verification describes
  revive at flush time. Resolution: BOTH — revive at stream end (the audible fix) AND force-speech reads
  audio truth (the directive fix for a round that produced content but zero audio with mechanical tools).
  Recorded in 02; consistent with resolved-decisions ("REVIVE, not retry").
- **C2:** plan T1 verification requires jaccard pins but jaccard is ported in commit 1 (not 2). Sequence OK —
  commit 1 carries the port, knob `tts_dedupe_similar` default OFF until T2 ships it with clamp? Plan T1
  verification says "jaccard near-dup dropped" — pin with knob ON in test (default stays False in config;
  .env does not set it → prod OFF until owner ear test? Plan decision table: jaccard 0.80 as iter70 shipped.
  iter70 shipped it ON by default). DECISION: `tts_dedupe_similar: bool = True` code default (owner settled
  "questions NOT exempt; jaccard 0.80 as shipped"), tests pass knobs explicitly anyway. Consistent with
  "config values belong in code defaults".
- **C3:** plan File Map lists `reconcile_note` state key only implicitly ("ingest (~L2716) consumes reconcile
  note") — schema addition made explicit in 02 (needed by LangGraph to route the payload key).
- **C4:** T5 llm.json command in plan is garbled pseudocode — replaced by a deterministic parity script check
  (state_prompt vs prompts/*.md diff + filler-line scan + `refer`=36 pin).
- **C5:** no contradiction remains: every planned file in the File Map is touched by exactly one commit, and
  every commit's file set ⊆ File Map ∪ {3 baseline test files from F1}.

Verdict: plan and audit are mutually consistent; open items C1..C5 resolved above and folded into 04.
