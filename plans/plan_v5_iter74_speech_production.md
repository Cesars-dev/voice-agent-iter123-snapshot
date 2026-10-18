# plan_v5_iter74_speech_production — SpeechLedger (spoken-truth layer) on clean 9ccdccf

## Meta
- Date: 2026-09-24
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE new layer — a spoken-truth ledger that owns every speech cut/dedup/count decision in the engine, plus the 3 fixes that derive from it (cancel-reconcile, question clamp, STT watchdog @3s) and 2 env-trap default flips. No timers, no routing changes, no transition-beat port.
- Status: PLAN ONLY (not started — awaits owner approval; branch already cut per owner instruction, nothing committed on it)
- Branch: `engine/iter74-speech-production` (already created 2026-09-24, cut from `9ccdccf` = `engine/iter73-playback-rate` tip, which contains the 50a453f lineage + EL cutover + iter73 playback-rate)
- Work location: MAIN checkout `/home/julio/projects/clean_diallux_SDR` on the branch above (no separate worktree; owner works here)

## Compaction Context
(condensed session record — a fresh agent continues from this block alone)

**What this project is:** Dialux SDR v5 voice engine (LangGraph 9-state + STT/LLM/TTS loop) in
`/home/julio/projects/clean_diallux_SDR/engine`, serving mic lane `diallux-8024.service`
(`https://flores.diallux-ai.site/voice24/mic?k=$VOICE_TEST_TOKEN`, token-gated) and a Twilio lane.
Prod voice = ElevenLabs Sarah `uG1JFy6xppqckhHCs2KG` turbo_v2_5 speed 1.06 (+ browser-side
playback-rate knob from iter73); Cartesia sonic-3.6-2026-08-27 env block kept dormant for rollback.

**Git topology (audited 2026-09-24):**
- Two checkpoints, BOTH already ancestors of HEAD: `40b3b40` (iter52..64c ladder merge, suite 427)
  and `50a453f` (iter65-over-iter66 merge, adds EL adapter + sanitizer + gpt-5.4 MODEL LAW +
  boot prewarm). Delta between them = exactly iter66 (EL TTS adapter rewrite) + iter65
  (sanitizer, boot prewarm, model defaults, mic spans) — 1461 insertions, 27 files.
- Prod head = `9ccdccf` (`engine/iter73-playback-rate`): 50a453f lineage + EL provider default
  (f236697) + 900s cap (87e173f) + replay SDK (8e06fe9) + docs/plans + iter73 rate fix.
- Local branch named `main` is STALE at `078f06d`; production line tip = `9ccdccf`. Verdict:
  fixes branch from `9ccdccf` (DONE — branch `engine/iter74-speech-production` created).
- Parked branches (reference only, NEVER cherry-pick wholesale): `engine/iter68-speech-flow` @
  `cc34343` (TOTAL FAILURE: semantic cos-dedupe, scripted-pass registries, chain-link buffering,
  ?-yield backstop — muted/truncated real speech); `engine/iter68-speech-lite` @ `95f7ace`
  (STT zombie watchdog = the ONE piece worth porting); `engine/iter70-speech-fixes` @ `dc62fb9`
  (5 commits: pause re-ask `65f3567`, transition beat `94f5164`, same-turn jaccard dedupe
  `02b4bef`, filter observability `87a0ce5`, prompt rule `dc62fb9` — battery chat-iter70-happy
  3/3 BOOK but owner mic test = disaster: laggy + cutting; chat can never catch voice-class bugs
  because personas answer in 1-2s).
- A second agent ALSO created `engine/iter74-staging-twilio-speech` @ `8286fc5` (2026-09-24
  09:37) merging iter70+iter67 onto `078f06d` — DISJOINT from prod (lacks EL pin + iter73).
  Unresolved consolidation decision: tri-merge (9ccdccf + dc62fb9 + 0394a3b) later; NOT this plan.

**Root-cause verdict (code-audited, owner-corroborated):** the engine has NO layer that knows what
the caller actually HEARD. All guards guess from content (`round_spoke = bool(content)` at
`/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py:2471`) — so every dedupe/
sanitizer/gate patch mutes something legit, silent rounds "speak" per the engine, cancelled turns
(barge-in / eager-rerun: 7 barge-ins, resumed_count=5, 14 eager cancels in ONE live call
2026-09-24 07:01-07:03, journal `diallux-8024.service`) leave polluted history, and the model
answers text the caller never heard ("loses context", asks 4 questions at once).

**Decisions settled this session (do not revisit):** fix on 50a453f lineage = current HEAD
`9ccdccf`; questions NOT exempt from dedupe (owner: "agent is trained to ask questions every
time"); watchdog faster than 6s; NO question-exemption; NO ?-yield routing change (cc34343
dropped it — killed calculate→reveal chains); NO pause-re-ask timer in this plan; owner already
added ~8 filler phrases to prompts themselves (verify llm.json parity only).

**What remains:** implement the SpeechLedger + 3 derived fixes + 2 default flips on the branch,
suite green, battery, owner ear test, ledger gates, then owner-gated merge.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Base = `9ccdccf`, branch `engine/iter74-speech-production` (already cut) | 40b3b40 is a strict code subset of 50a453f; EL voice path + sanitizer + MODEL LAW only exist on the 50a453f line; 9ccdccf is ear-tested prod and is the rollback point |
| SpeechLedger = ONE flush owner for sanitize + exact-window + jaccard-similar + question count + observability, at BOTH flush sites | The muting/cutting class exists because 3+ inline filters each decide speech independently with no shared truth; one owner kills the class by construction |
| `round_spoke_audio` (audio-truth) becomes the guard input for never-mute; `round_spoke` stays content-based for compatibility | Content-based truth is the root of silent-finalize; guards must read what was flushed |
| Questions NOT exempt from the similar-dedupe (jaccard 0.80, min 4 words, as iter70 `02b4bef` shipped) | Owner call 2026-09-24: agent is trained to ask a question every turn — exempting "?" disables dedupe |
| Question clamp: max 1 spoken "?" sentence per ROUND + max 2 per TURN (tool-chain reveal gets the turn's 2nd slot), TTS-only drop, history untouched | Owner 2026-09-24: "only one question is allowed"; per-round cap kills the one-breath 4-question dump, per-turn 2 preserves the engine ask→tool→reveal chain; the routing-yield version (cc34343) broke calculate→reveal chains and is NOT copied |
| Never-mute = REVIVE, not retry: if the engine muted a round's speech entirely (flushed 0, cuts > 0), the muted sentences are revived and passed straight to the TTS gate — zero extra LLM rounds, no retry loop | Owner 2026-09-24: "if the engine shuts the agent, we revive it and pass it to the TTS tool"; retries cost latency; redundancy > dead SDR |
| Sanitizer-dropped code artifacts stay dead (revive covers dedupe/clamp cuts only) | Speaking `function_calls`-style garbage is not redundancy — it's broken audio |
| Cancel-reconcile note on barge-in/eager-cancel (heard-prefix + fired tools + result) | Live evidence: cancelled turns leave model-imagined history; model then answers fragments (context loss, 4-question dumps) |
| STT watchdog port from `95f7ace` with knob default 3000ms (not the branch's 6s) | Owner: 6s too long; Deepgram TTFB measured 457-586ms; disarms after first message |
| Code-default flips: `tts_dedupe_semantic` True→False, `tts_gate_fast_first_flush` True→False | Mirrors current `.env` state; removes the env-loss trap (PT-58/CARTESIA lesson) with zero behavior change when env present |
| Config values belong in code defaults; `.env` holds secrets + deliberate overrides only | Owner 2026-09-24 ("why are we storing this on .env"); pydantic env override still wins when present |
| Cancel-reconcile note wording: "Continue the conversation naturally from [last heard context]. Don't repeat full sentences you already said." — no task pressure, improvisation allowed via general prompt + state | Owner 2026-09-24; worst case = a slightly wrong question, corrected next turn — never dead air |
| History perception = ONLY what the caller heard: a cancelled turn's ghost speech never counts as "the agent already said it" | Owner 2026-09-24: the agent "should never have the perception it already spoke, only what the user heard" |
| NO pause re-ask timer, NO transition-beat routing, NO latency work in this iteration | Owner rejected timer/beat designs; latency = "later" bucket (iter71) |
| Sanitizer stays ON, becomes ledger-visible (every drop logged) | It kills real artifacts; unlogged whole-sentence drops were an unmeasured muting surface |
| Owner's prompt fillers (8) are DONE — parity check only | Owner edited prompts in-session 2026-09-24 |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Question cap exact value — SET: 1 per round, 2 per turn (knobs `tts_max_questions_round=1`, `tts_max_questions_turn=2`) | Owner 2026-09-24 |
| Watchdog exact ms (proposed default 3000) | Owner GO — knob `stt_watchdog_ms` |
| Whether PT-68 pause re-ask joins a later iteration | Owner decides after ear test; reference impl exists on `65f3567` (session.py timer machinery) |
| Consolidation of `engine/iter74-staging-twilio-speech` @ `8286fc5` (twilio lane + iter70 line) | Owner call AFTER iter74 merges — tri-merge plan drafted in session, not executed |

## Environment & Dependencies
- Python venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv` (run via `.venv/bin/python -m pytest`, NEVER the pip script — copy-mirror venv)
- No new packages (watchdog = stdlib asyncio; ledger = stdlib)
- Suite command: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q`
- Secrets: `/home/julio/projects/clean_diallux_SDR/engine/.env` (gitignored) — `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`, `ELEVENLABS_*`, `CARTESIA_*` (dormant rollback block, MUST keep `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` on any env edit), `VOICE_TEST_TOKEN`, `LANGFUSE_*`
- Mic lane: systemd user unit `diallux-8024.service`; mic page `https://flores.diallux-ai.site/voice24/mic?k=$VOICE_TEST_TOKEN`
- Call ledger DB: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db` (no sqlite3 CLI on box — use `.venv/bin/python -c "import sqlite3,...`)
- Import SDK: `/home/julio/projects/clean_diallux_SDR/scripts/live_sql.py` (MAIN-repo copy — worktree copies miss micbridge-*)
- Cal.com test bookings: event 3801235 is REAL — cancel every test booking after batteries
- Boot secrets: `set -a; . /home/julio/projects/clean_diallux_SDR/engine/.env; set +a`

## Architecture (block diagram)

```
caller audio ─▶ DeepgramSTT (Eager/EOT/Start/Update) ─▶ CallSession clocks (session.py)
                                                        │ _run_turn
                                                        ▼
              LangGraph turn: ingest ─▶ state_node round ─▶ LLM astream ─▶ deterministic ─┐
                                         ▲ (loop ≤ rounds_left)                          │
                                         └───────────────────────────────────────────────┘
              [NEW] SpeechLedger sits at the ONLY speech exit: every flushed sentence
              passes ONE ledger.flush() → sanitize → exact-window → jaccard-similar →
              question count → emit {tts_token} + log line. Ledger truth (flushed/cut/
              questions) rides GraphState updates round-to-round.
                                                        │
                                                        ▼
              SentenceBufferGate (sentence_gate.py add/end_of_turn) ─▶ TTS (EL adapter)
                                                        │
              [NEW] cancel-reconcile: barge-in/eager-cancel snapshot → ingest note
              [NEW] STT watchdog inside DeepgramSTT (3000ms no-message → reconnect once)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | SpeechLedger class (near `_sanitize_spoken` ~L216); both flush sites (~L2276-2373 mid-stream, ~L2408-2458 stream-end) call `ledger.flush()`; updates carry `speech_ledger`/`round_spoke_audio`/`turn_questions`; never-mute condition at L2125 reads audio truth; ingest (~L2716) consumes reconcile note | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/state.py` | GraphState keys: `speech_ledger: list[str]` (window+counts, reducer `merge_dict`), `round_spoke_audio: bool`, `turn_questions: int` | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | +`tts_max_questions_round: int = 1`, +`tts_max_questions_turn: int = 2`, +`stt_watchdog_ms: int = 3000`; flips: L309 `tts_dedupe_semantic`→False, L206 `tts_gate_fast_first_flush`→False | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | cancel hooks at `_on_start_of_turn` (L583) + `_on_turn_resumed` (L517): capture heard-prefix from gate + fired-tools snapshot → `self._reconcile_note` | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` | add `heard_prefix()` accessor (last flushed-and-played text) for reconcile | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/deepgram_stt.py` | watchdog port (95f7ace, ~45 lines): while streaming audio, zero server messages within `stt_watchdog_ms` → fire `on_disconnect` reconnect ONCE; disarm after first message | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/scripts/speech_replay.py` | ledger mirror (same flush fn import; CUT labels: sanitize/exact/similar/clamp) | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/scripts/mic_events.py` | RULES: `("CUT", speech_filter stage=)`, `("REASK", pause|re-ask)`; `_CALL_TAGS` += CUT, REASK | Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/agent/llm.json` | READ-ONLY parity check vs prompts (owner's 8 fillers) — edit ONLY on drift | Verify/Edit |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter74_speech_ledger.py` | pins T1 | New |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter74_clamp_nevermute.py` | pins T2 | New |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter74_reconcile.py` | pins T3 | New |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter74_stt_watchdog.py` | pins T4 | New |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter74-speech-production/` | report(s) | New (gitignored) |

## Deploy Rules
- Lane test (owner-ordered only): `systemctl --user restart diallux-8024.service && sleep 5 && journalctl --user -u diallux-8024.service -n 10 --no-pager | grep -E "elevenlabs|cartesia connected"` — verify provider/model pin matches `/home/julio/projects/clean_diallux_SDR/engine/.env`
- NEVER touch: `/home/julio/projects/clean_diallux_SDR/services/` ports 8001-8003 (original still serving), production Retell agents (`agent_16985b5d087e56c35141983396`, `agent_87e4d5f08475e5bc558b2f390f`), `engine/.env` voice pins (`CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` survives ANY env edit)
- Never run `pytest` with secrets unset; always `set -a; . /home/julio/projects/clean_diallux_SDR/engine/.env; set +a` first
- Cancel ALL test bookings after batteries (Cal.com event 3801235 is REAL)

## Tasks (in order)

### T0 — Baseline pin (no code)
Goal: prove the branch starts green.
Files: none.
Commands (full):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python -m pytest tests -q 2>&1 | tail -3
git -C /home/julio/projects/clean_diallux_SDR log --oneline -1
```
Dependencies: none.
Verification: suite green; recorded baseline count goes into the plan Status line (updated once, by owner-approved docs commit).

### T1 — SpeechLedger core (ONE flush owner) — commit 1
Goal: one function owns every speech cut; engine learns audio truth.
Files: builder.py, state.py, speech_replay.py, mic_events.py, tests/test_iter74_speech_ledger.py.
Commands (full): edit in `/home/julio/projects/clean_diallux_SDR/engine/…` (see File Map), then
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python -m pytest tests/test_iter74_speech_ledger.py tests/test_v2.py tests/test_graph.py tests/test_iter42_dedupe_window.py -q
```
Dependencies: T0. Ledger bodies port verbatim: `_sanitize_spoken` (builder.py:232), exact-window (iter42 L2323), jaccard `_similar_dup` from `git show 02b4bef`, observability line shape from `87a0ce5` (`speech_filter stage=<sanitize|exact|similar|clamp> sent=%r state=%s turn=%s`).
Verification: pins green (sanitize drop logged; exact dup dropped; jaccard near-dup dropped; `round_spoke_audio` true only when a sentence flushed; window resets at ingest); full suite green.

### T2 — Question clamp + never-mute via audio truth — commit 2
Goal: owner's one-question-per-breath rule + no more silent rounds.
Clamp: max 1 spoken "?" per round (kills the one-breath dump), max 2 per turn (the ConfirmSlots ask→tool→reveal chain keeps its 2nd slot) — TTS-only drop, history untouched. Never-mute = REVIVE, not retry: zero-flushed round with cut sentences → the muted sentences are re-sent directly to the TTS gate in order (no new graph round, zero added latency); sanitizer artifacts stay cut (garbage ≠ redundancy).
Files: builder.py (clamp inside `ledger.flush`, cap knob; never-mute at the force-speech site L2125-2153 keyed on `round_spoke_audio`), config.py (knob), tests/test_iter74_clamp_nevermute.py.
Commands (full): same pytest pattern as T1 + `tests/test_iter32*.py` regression.
Dependencies: T1 (ledger carries `turn_questions`).
Verification: one-breath 4-question dump → exactly 1 spoken; ConfirmSlots ask→tool→reveal (2 questions, 2 rounds) unaffected; a fully-muted round gets its sentences revived straight to TTS with ZERO extra LLM rounds; suite green.

### T3 — Cancel-reconcile (barge-in / eager-rerun) — commit 3
Goal: cancelled turns stop poisoning history; model knows what the caller heard and what tools fired.
Files: session.py, sentence_gate.py, builder.py (ingest delta directive), tests/test_iter74_reconcile.py.
Commands (full): same pytest pattern + `tests/test_iter38*.py tests/test_iter46*.py` (eager/barge-in pins).
Dependencies: T1 (`round_spoke_audio` truth from the gate side).
Verification: pin — cancel mid-round after `extract_*` fired → NEXT turn's post-history delta contains the reconcile note (heard-prefix + tool + result + "do not repeat, reveal"); no note when no cancel; history contains NO text the caller never heard beyond the note; suite green.

### T4 — STT zombie watchdog @3s knob — commit 4
Goal: adopted half-dead socket self-heals once, call continues.
Files: deepgram_stt.py (port of `git show 95f7ace -- engine/diallux/media/deepgram_stt.py`), config.py (knob), tests/test_iter74_stt_watchdog.py.
Commands (full): port diff, then
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python -m pytest tests/test_iter74_stt_watchdog.py tests/test_iter61*.py -q
```
Dependencies: none (isolated).
Verification: pin — 3s of streamed audio with zero server messages → exactly one reconnect; healthy socket (first message <3s) → watchdog disarmed, zero reconnects; suite green.

### T5 — Env-trap default flips + llm.json parity — commit 5
Goal: 40b3b40-era latent traps defused in code; owner's fillers verified mirrored.
Files: config.py (L309 `tts_dedupe_semantic=False`, L206 `tts_gate_fast_first_flush=False`), llm.json read-only check.
Commands (full):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python -m pytest tests -q
.venv/bin/python -c "import json;d=json.load(open('agent/llm.json'));print([s for s in json.dumps(d) if False] or 'loaded')"   # then diff each state_prompt vs prompts/*.md filler lines
```
Dependencies: T1 (semantic branch is dead-code by default; fast-flush off).
Verification: full suite green with ZERO behavior change when `.env` is present (pydantic env override still wins); llm.json word-count of `refer` = 36 stays; filler lines byte-parity (report drift, edit only on owner GO).

### T6 — Battery + lane deploy + owner ear test + ledger + report (no new code)
Goal: prove it on VOICE, not chat.
Files: none.
Commands (full):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && setsid nohup .venv/bin/python tests/llm2llm/harness.py --personas happy3 --rag --langfuse --max-turns 48 > /tmp/opencode/iter74_battery.log 2>&1 < /dev/null &
systemctl --user restart diallux-8024.service && sleep 5 && journalctl --user -u diallux-8024.service -n 10 --no-pager | grep -iE "elevenlabs|cartesia"
python3 /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py import --window "<HH:MM-HH:MM>" --run chat-iter74-happy --commit <sha>
python3 /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py gates --a chat-iter65-happy --b chat-iter74-happy
```
Dependencies: T1-T5 suite green.
Verification: battery 3/3 BOOK; gates G1/G2 green; lane journal shows provider pin; OWNER EAR CHECKLIST (mic page with `$VOICE_TEST_TOKEN`): (1) answer→agent never goes silent mid-flow, (2) forced repeat → journal shows `speech_filter stage=similar`, (3) 4-question scenario (tell it to dump several) → only 2 spoken, (4) interrupt mid-sentence → next turn acknowledges WITHOUT re-asking answered things, (5) voice unchanged. Then CANCEL all test bookings (event 3801235 REAL). Report → `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter74-speech-production/01_report.md`.

### T7 — Closeout (owner-gated)
Lane restore: `git -C /home/julio/projects/clean_diallux_SDR checkout -- engine/diallux engine/agent/llm.json engine/scripts && systemctl --user restart diallux-8024.service`. `hitl_ping.py` merge ASK (LAW 0). PENDING_TASKS rows updated (docs). Merge/tag only on owner say-so.

## Validation Plan (end-to-end)
1. Every commit: subset pins green → full suite green before the next task.
2. Battery happy3 3/3 BOOK; ledger gates green via SQL (live_sql.py, MAIN-repo SDK only).
3. Owner ear checklist (5 items above) = the ONLY behavior gate; journal `speech_filter` lines must match what the ear heard.
4. Suite count before/after recorded in the report; ledger.db backup ritual (`ledger.db.bak`) before import.
5. No merge without owner say-so (LAW 0); rollback = `git switch engine/iter73-playback-rate` (prod untouched at 9ccdccf).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Pause re-ask timer (PT-68) | Owner rejected timer-first design; revisit after ear test with ledger-truth data; reference `65f3567` |
| Eager-resume grace A/B (`eager_resume_grace_ms`, session.py:529, default 0) | Knob already exists; 14 eager cancels logged today; tuning = latency bucket, separate session |
| Latency floor / flat-ack continuation (iter71) | Owner: latency later, bugs first |
| T3 transition-beat routing port (94f5164) | Rejected shape (same-turn cold continuation = the mic lag) |
| Staging branch consolidation (`8286fc5` tri-merge) + branch graveyard cleanup (tag-and-delete 47 merged branches, prune 31 worktrees, push main) | Owner-gated, AFTER iter74 verdict; decisions drafted in session, not executed |
| iter72 voice-lab EL matrix | Separate plan, owner-gated |
