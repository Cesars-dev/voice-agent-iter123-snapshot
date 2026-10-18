# plan_v5_iter93 — FIND-35 turn-engine race fix: EPOCH DISCIPLINE (variant B+) + data-first dump + twilio-transport preview

## Meta
- Date: 2026-10-05 (T0 answered in-session 2026-10-05; plan rewritten per Plan SOP)
- Project root (OREGON source of truth): `/home/julio/projects/clean_diallux_SDR`
- Session box: Finland (julio @ 46.62.233.228). ALL repo git ops ssh-wrapped to OREGON:
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'`
  All git WRITES go via `/tmp/opencode/wt-main-docs` on OREGON (OR main checkout is FROZEN:
  never checkout/switch/reset/pull there; its FILES are stale — code reads come from
  `/tmp/opencode/wt-main-docs/engine/…` or the FI checkout, which is synced).
- Scope: ONE code iteration `engine/iter93-held-adopt-race` — the FIND-35 race fix as
  **variant B+ (epoch discipline)** per owner research, + data-first raw TurnInfo dump
  + telemetry stamps + PT-79 provenance probe (observability commit) + stutter persona
  test + confidence-semantics check (read-only) + Twilio-transport preview battery.
  NOT in this branch: confidence-band repair C (own branch later), savage warm abort
  (next branch), PT-81 same-state warm, PORT-list remainder.
- Status: **PLAN ONLY (T0 ANSWERED — awaits owner GO to cut the branch)**

## Compaction Context

### Landed state (verified this session)
- main = origin/main = **e2a562d** (docs-only: plan iter91b EXECUTED + PT-83).
  Engine code byte-equal to iter91 tip: tag `engine/iter91` @ 6d9f277; iter91 pack
  @ 2b3e900 through merge S3. Suite on main: 490 passed / 3 skipped / 0 failed.
- FI checkout `/home/julio/projects/clean_diallux_SDR` synced to e2a562d (safe code source).
- iter91b assessment (this ladder's origin): evidence
  `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter91b-savage-cancel-assess/`
  (01 palette, 02 research recheck, 03 matrix, 04 verdict — gitignored).
- Lane RUNNING: `wt-iter91` @ 2b3e900 on 127.0.0.1:8049 (OREGON), pid 1471973,
  log `/tmp/opencode/lane-8049.log`, Hannah EL pure-globals env, VOICE_TEST_TOKEN gate.

### FIND-35 — the disease (T2-VERIFIED anatomy, current code, session.py line numbers @ e2a562d)
Owner symptom: confirmed EOT adopts a live speculative turn, LLM completes (out=20 tok),
`tts_first` stays null — reply silently swallowed. Fires on PSTN humans (mid-sentence
pauses), never on battery personas. Owner live repro 2026-10-05 08:11 (headphones):
2× false-start discard (held 1500/1300 ms) + adopt at 48.947s without release log.
Trace a6f7c585a68f; ledger FIND-35 row registered.

THREE live orphan paths (verified by direct read; the owner research doc's exact
interleaving — deferred resume write — does NOT exist in this tree; its "secondary
variant" and "sibling hazard" DO):
1. **Fire-lag adopt (THE owner trace):** `_on_eager_eot`
   (`/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:573-634`)
   never sets `_eager_held`; it spawns `asyncio.create_task(self._run_turn(...))` at
   session.py:634. The write `self._eager_held = True` + `gate.hold()` happens at
   session.py:794-798 — at least ONE event-loop tick later. A confirmed EOT arriving in
   that gap (owner trace: eager 48.94a → confirm 48.94c, ~5 ms) passes the adopt checks
   (session.py:450-451), reads `_eager_held=False` at session.py:477 → NO release →
   task then arms the hold and streams into a gate nobody will ever release.
2. **Stranded parked-final:** LLM finishes BEFORE TurnResumed → `end_of_turn()` parks
   the final (`sentence_gate.py:117-121`, `_held_final=True`); resume guard
   `self._turn_task and not self._turn_task.done()` (session.py:640) FAILS (task done)
   → no discard → gate stays held → the NEXT non-eager turn buffers into the still-held
   gate (`sentence_gate.py:101-102`) → cascading silent turns until a barge-in reset().
3. **Clobber class (not reachable today; must stay impossible):** today's
   `gate.discard()` (sentence_gate.py:84-92) has no real yield, but ANY future await
   inside discard/drain lets a stale cleanup wipe a NEWER generation's hold+buffer.
   The epoch design makes this structurally impossible.

Supporting sites: `_eager_held` declared session.py:80; adopt guard session.py:477-486;
resume held-branch session.py:641-663 (flags written SYNC at 649-652 — correct already);
barge-in session.py:692-722; cap-close safety session.py:933-935 (same disease class);
gate primitives sentence_gate.py:52-95; queue items `(text, continue_)` sentence_gate.py:43.

### The cure (owner research = truth; FIND35 doc §(b) "epoch discipline")
Source of truth: `FIND35_TURN_ENGINE_RACE_DIAGNOSIS.md` — Mac
`/Users/Cesar_1/vps-inbox/FIND35_TURN_ENGINE_RACE_DIAGNOSIS.md`; FI mutagen copy
`/home/julio/projects/vps-inbox/FIND35_TURN_ENGINE_RACE_DIAGNOSIS.md` (§(b) = the patch,
§(d) = the test recipes). Three laws: (1) all generation-state mutations synchronous at
handler entry, before the first await; (2) all slow cleanup epoch-tagged — a stale
discard becomes harmless instead of impossible; (3) no side-channel boolean: the gate's
barrier + epoch-tagged chunks are the truth. "One boolean and one counter" — no
turn-machine rewrite.

### Savage cross-check (why no collision — owner-verified question)
- Savage piece 1 (warm abort cap, `builder.py:633-669` `_await_warm` timeout→shield
  keeps warm alive today) = NEXT branch, untouched by iter93.
- Savage piece 2 (abort speculative call on resume) ALREADY EXISTS (session.py:652
  `task.cancel()`); the epoch fix KEEPS it (first in the sync zone). Cache survives
  aborts (savage README Proof 1) — unaffected.
- FIND-35 fix adds/removes NO OpenAI stream; one-stream-per-key rule untouched.

### T0 ANSWERS (owner, 2026-10-05, in-session — DO NOT re-ask)
1. Ladder adopted: iter93 B+ → savage warm abort → PT-81 same-state warm → PORT remainder.
2. Variant = **B+ epoch discipline**; branch = race-fix only; C (confidence repair) =
   OWN branch later, gated on the T1 dump.
3. PT-79 provenance probe FOLDED INTO iter93's observability commit.
4. Stutter persona (permanent battery character) INCLUDED.
5. Confidence check via SCRIPTED FAKE CALLER (no manual-only session).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Variant B+ (epoch discipline), NOT A (unconditional flush), NOT plain B | A leaves orphan paths 2+3 open → second iteration guaranteed; B+ = B with sync-zone law, same file footprint, closes all 3 paths |
| `_epoch: int` + `_held: int\|None` + `_tts_ctx_epoch: int` replace `_eager_held` | FIND35 §(b) State; zero new env knobs (epoch is internal) |
| Gate ops epoch-tagged: `hold(epoch)`, `release(upto)`, `discard(upto)`; queue items `(epoch, text, continue_)`; `_barrier: int\|None` | FIND35 §(b) gate valve; queue valence |
| `gate.reset()` survives as CALL TEARDOWN ONLY | FIND35 §(b) implementation notes; resume/discard use `discard(upto)` |
| Adopt = transcript-equality contract (Deepgram); growth/none → discard + fresh epoch, never answer the prefix | FIND35 §(c) Q4; matches existing `eager_final_match` guard |
| Barge-in: bump epoch FIRST, cleanup second | FIND35 §(b) `_on_start_of_turn` |
| Telemetry: `held_epoch`/`released_epoch` stamps + `held_swallow` detector in `_late_turn_report` | FIND35 §(b) traceability; every future real call becomes a sensor |
| Tests = FIND35 §(d): properties A-E + regression pin + stutter persona scenario | owner asked "does the plan cover the new test persona" — YES, now explicit |
| T1 data-first: raw TurnInfo dump BEFORE fix code lands (env-gated, default off) | owner law: "we fix this thing with data"; also un-gates C |
| PT-79 probe rides the observability commit | owner T0 answer 3 |
| Twilio-transport preview battery INCLUDED | owner: "find out if this bites us in twilio migration" (same CallSession serves /media) |
| Branch `engine/iter93-held-adopt-race` cut from main tip e2a562d | fix sits on the real landed tip; manual worktree (branch-name law `engine/iterNN-*`) |
| Savage piece 1 + C + PT-81 + PORT remainder NOT in this branch | one variable per branch; ladder order |
| NO merges without owner say-so; docs straight to main | LAW 0 |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Flux TurnInfo confidence FIELD semantics (per-word? per-utterance? range?) | T1 raw dump on lane 8049 (scripted fake caller + owner manual confirm). NEVER assume nova3 semantics (task 4610 note) |
| C (confidence repair) buildability | T1c table: mangled fragments vs clean speech confidence separation → separated = buildable; overlap = C dies |
| Twilio fake client feasibility | T5: reuse any existing twilio-era fake in `/home/julio/projects/clean_diallux_SDR/engine/tests` (check `test_iter80_stt_liveness.py` + twilio-era tests); if too thin to reach the session layer, ESCALATE to owner BEFORE improvising |

## Environment & Dependencies
- Python venv (ONLY this): `/home/julio/projects/clean_dialux_SDR/engine/.venv/bin/python`
  (NEVER bin/pip; use `-m pip`). Py 3.12.
- Suite: `cd /tmp/opencode/wt-93/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q`
  (NO env export; conftest blocks ambient .env; expect 490 passed / 3 skipped baseline + new pins).
- Branch cut (OREGON, manual — keeps iter-law branch name):
  `cd /home/julio/projects/clean_diallux_SDR && git worktree add /tmp/opencode/wt-93 -b engine/iter93-held-adopt-race e2a562d`
  `ln -s /home/julio/projects/clean_diallux_SDR/engine/.venv /tmp/opencode/wt-93/engine/.venv`
  `cp /home/julio/projects/clean_diallux_SDR/engine/.env /tmp/opencode/wt-93/engine/.env`
  (env audit: WARM_AWAIT_DEST_MS=2500 not 250; CARTESIA_MODEL_ID dated pin; eager 0.35 < EOT 0.65.)
- Lane boot (OREGON; reuse 8049 after stopping the wt-iter91 server):
  `cd /tmp/opencode/wt-93/engine && set -a && . ./.env && set +a && setsid nohup .venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8049 > /tmp/opencode/lane-8049.log 2>&1 < /dev/null &`
  Twilio preview lane: same recipe, port 8050, env `AUDIO_TRANSPORT=twilio` (verify exact
  var name in `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py`: `audio_transport`).
- Key files (absolute):
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` (fix target; handlers at 444-488, 573-634, 636-676, 692-722, 785-829, 933-935 @ e2a562d)
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` (gate ops 52-95, queue 43, add 95-110, end_of_turn 112-130, reset 132-139)
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/deepgram_stt.py` (confidence + raw dump logger)
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` (knobs; add `deepgram_raw_dump` default False)
  - `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter93_epoch_race.py` (NEW pin file)
  - `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/` (stutter persona scenario; harness base)
  - `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93-held-adopt-race/` (evidence, gitignored)
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (import via `/home/julio/projects/clean_diallux_SDR/scripts/live_sql.py`; no sqlite3 CLI — venv python).
- Registry: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db`
  (refresh ritual from MAIN checkout engine dir at session end; backup first).
- GitHub push (from wt-main-docs): `-c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'`;
  keyhound `/home/julio/projects/clean_diallux_SDR/scripts/keyhound` diff-scoped scan before EVERY push
  (standing 259-hit noise = legacy services/*; only the NEW diff must be 0 key-shaped strings).
- Owner access: ssh tunnel Mac→OR, URL `ws://…/mic/ws?k=<VOICE_TEST_TOKEN>` — token read from
  `/tmp/opencode/wt-93/engine/.env` via ssh; NEVER print it.

## Architecture (the fix, one diagram)

```
Deepgram Flux WS ──(TurnInfo: EagerEOT / TurnResumed / EOT / confidence)──► deepgram_stt.py
      │                        │                        │
      │  (T1: raw dump, env-gated DEEPGRAM_RAW_DUMP, default off; confidence pass-through)
      ▼                        ▼                        ▼
  _on_eager_eot           _on_turn_resumed          _on_eot
  SYNC ZONE:              SYNC ZONE:                transcript-equal? ──yes──► SYNC: _held=None
   _epoch += 1             _held=None if ==k         │                        gate.release(k)
   _held = k               task.cancel()             no (growth/none)
   _tts_ctx_epoch = k     ASYNC (epoch-tagged):      │  task.cancel(); _held=None if ==k
  ASYNC:                  gate.discard(upto=k)       │  gate.discard(upto=k)
   gate.hold(k)            tts.cancel if ctx<=k       │  _epoch += 1; fresh task
   task = _run_turn(…, epoch=k)                       ▼
   ▼                                              SentenceGate (queue valence)
  _run_turn(epoch=k)                               _barrier: int|None
   tokens → gate.add(epoch, tok)                   items (epoch, text, cont)
   parked while epoch >= barrier                   sender parks/discards by epoch
   end_of_turn → park final(k)                     reset() = TEARDOWN ONLY
      │
      ▼
  TTS EL Hannah turbo_v2_5 (pure globals, TTS_DELIVERY_PROFILES=false)
```
Invariant: **held-state lives in the gate keyed by epoch; a stale discard can only touch
artifacts of generations ≤ its own epoch; adopt releases the CURRENT confirmed epoch.**
All three orphan paths become impossible by construction.

## File Map
| File (absolute path) | What changes | New/Edit |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter93_held_adopt_race_fix.md` | THIS plan (rewritten per SOP, T0 answers baked in); verdict appended at close | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | Replace `_eager_held` with `_epoch`/`_held`/`_tts_ctx_epoch`; sync-zone writes in all 4 handlers; epoch-threaded `_run_turn`; `held_swallow` detector + `held_epoch`/`released_epoch` stamps in `_late_turn_report`; PT-79 provenance field on turn report | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` | `_barrier: int\|None`; `hold(epoch)`, `release(upto)`, `discard(upto)`; queue items `(epoch, text, continue_)`; sender parks while `epoch >= barrier`; park-before-send + `task_done` accounting; `reset()` teardown-only | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/deepgram_stt.py` | Raw TurnInfo DEBUG dump (env-gated); confidence pass-through on EOT | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | Knob `deepgram_raw_dump: bool = False` | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter93_epoch_race.py` | NEW: fake-clock property tests A-E + regression pin (exact 48.94 repro) + interleaving pins | NEW (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/` | NEW stutter persona scenario file (300-700ms bursts, 250-400ms micro-pauses, two false starts per real EOT) wired into the battery runner | NEW (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/ITERATIONS.md` | iter93 close-out line | EDIT (branch end → main at merge) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-82 row (the fix, status UNMERGED → DONE at merge) | EDIT (docs → main, same landed tip) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93-held-adopt-race/` | `01_flux_raw_dump.md`, `02_confidence_table.md`, `03_race_log.md`, `04_validation.md`, `05_twilio_preview.md`, `06_report.md` (gitignored) | NEW (gitignored) |

## Deploy Rules
- NO /opt. NO original-repo services. Lanes on 127.0.0.1 only: 8049 (fix lane + live
  replay), 8050 (twilio preview). OR listening now: 8001/8002/8003/8026/8090 + 8080
  caddy — NEVER touch. Stop the current wt-iter91 server (pid 1471973 on 8049) before
  booting wt-93 there.
- OR main checkout: NEVER checkout/switch/reset/pull. Writer = `/tmp/opencode/wt-main-docs` only.
- Engine code = branch law: `engine/iter93-held-adopt-race` from e2a562d → suite green →
  live replay → twilio preview → report → ASK JULIO → merge ONLY on owner say-so
  (--no-ff, tag `engine/iter93`, `scripts/git-tree.sh`, registry refresh, ITERATIONS line).
- Docs land straight to main. keyhound + diff-scoped scan (0 key-shaped strings) before every push.
- Cal.com test bookings: cancel everything after ANY booking-touching battery (event 3801235 REAL).

## Tasks (in order)

### T1 — Observability commit (data-first): raw dump + telemetry + PT-79
Goal: land the FIRST commit of the branch = observability-only (no behavior change):
`deepgram_raw_dump` knob + raw TurnInfo logger + `held_epoch`/`released_epoch` stamps +
`held_swallow` detector + PT-79 provenance field (laneA/laneB/fallback + pre-llm gap
breakdown on the turn report).
Files: `config.py`, `deepgram_stt.py`, `session.py` (telemetry lines only), tests pinning
the dump default-off.
Commands (OREGON): branch cut per Environment §Branch cut, then edits, then
`cd /tmp/opencode/wt-93/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q 2>&1 | tail -3`
Verification: suite green (490/3 baseline unchanged); dump OFF by default (no log noise
without the env flag); commit message marks it observability-only.

### T2 — The epoch-discipline fix code
Goal: implement B+ per Architecture: session.py state + 4 handlers sync zones;
sentence_gate.py epoch-tagged ops + queue valence; remove `_eager_held` entirely
(decl session.py:80, uses 477-486, 641-663, 794-798, 933-935).
Files: session.py, sentence_gate.py.
Verification: suite green; `grep -rn "_eager_held" /tmp/opencode/wt-93/engine/diallux/`
returns ZERO hits (the side-channel boolean is gone — law 3).

### T3 — Tests: property harness + regression pin + stutter persona
Goal: `test_iter93_epoch_race.py` — fake gate/TTS/LLM with injection points at the
known await sites (gate discard drain, tts.cancel, sink.clear, each 0-400ms fake time);
properties A (no-swallow) B (no-leak) C (no-clobber) D (ordering) E (barrier sanity);
regression pin = the exact headphone repro script (0ms eot_confirm / 640 start_of_turn /
1440 eager gen3 / 1510 resumed tail_delay 250 / 1740 eager gen4 / 1745 eot_confirm →
assert spoken.count(epoch=4) > 0 AND drain sets ≤ {3}); seeded-random generator
(200 seeds pre-commit). Stutter persona scenario file in
`/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/`.
Verification: all new pins green; the regression pin FAILS if the fix code is reverted
(prove it by stashing T2 once); stutter persona runs one scripted call end-to-end on the
lane without a swallowed reply.

### T4 — Live replay of the EXACT disease (owner validation)
Goal: prove the fix on the lane with the owner's fragment-paced speech.
Commands (OREGON): stop wt-iter91 server on 8049, boot wt-93 per Environment §Lane boot;
owner tunnels and speaks the fragment pattern (speak fragment → pause → continue →
pause → confirm), 3-5 rounds, plus a couple of clean sentences.
Verification: `/tmp/opencode/lane-8049.log` shows the release FOLLOWED by tts_first on
the same turn; ZERO `held_swallow` anomalies; turn reports show `tts_first_ms` NOT null
where the old code swallowed. Evidence → `04_validation.md`. Langfuse trace imported
(run `iter93-fix-validate`, commit = branch tip).

### T5 — Confidence-semantics check (read-only; un-gates C)
Goal: decide if the "say that again?" repair (C) is buildable, via the scripted fake
caller — NO manual-only session.
Method: with `DEEPGRAM_RAW_DUMP=1` on lane 8049, script the fake caller (LLM-mic-driver
path) to play two audio sets: clean sentences + deliberately mangled fragments
(cut-off words, mumbling, half-sentences). Tabulate confidence per word/utterance.
Decision criterion: mangled fragments score clearly BELOW clean speech (two separated
groups) → C buildable; overlap → C dies (recorded, no build). Numbers MUST come from
this lane config in streaming mode — never assume nova3 semantics.
Verification: `02_confidence_table.md` with the raw payloads, the table, and the
buildable/not-buildable verdict + the band values proposed for C if buildable.

### T6 — Twilio-TRANSPORT preview
Goal: prove the fix holds on `transport=twilio` (/media) before any real migration.
Method: lane on 127.0.0.1:8050 with `AUDIO_TRANSPORT=twilio`; drive the same pipeline
with the fake media-stream client — REUSE any existing twilio fake from
`/home/julio/projects/clean_diallux_SDR/engine/tests` (check test_iter80_stt_liveness.py
+ twilio-era tests) — read `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py`
/media handler for the EXACT start/descriptor frames FIRST. Replay the identical
fragment pattern. No real PSTN spend.
Verification: `05_twilio_preview.md`: reply SPOKEN through /media, zero false-start
orphans. If the fake client is too thin to reach the session layer, ESCALATE to owner
BEFORE improvising (BLOCKED).

### T7 — Report + ledger + close-out + ASK JULIO
Goal: durable record; owner decides the merge.
Files: `06_report.md`; ledger import (`live_sql.py import --window "…" --run
iter93-fix-validate --commit <tip>`); findings status update (FIND-35 → FIXED @ <sha>
AFTER merge, not before); registry refresh (backup `ledger.db` first, run from MAIN
checkout engine dir); ITERATIONS line (UNMERGED note before merge); PT-82 choreography;
plan file verdict appended.
Commands: docs commit via `/tmp/opencode/wt-main-docs` (plan + PENDING_TASKS), keyhound
diff-scan, push, FI sync (`git fetch && git merge --ff-only origin/main`).
Verification: ASK JULIO message contains branch SHAs, suite counts, validation +
confidence + twilio evidence links, and the asks (merge say-so; cleanup say-so for
wt-92 / engine/92-92b-4gk-quant / wt-merge87 / wt-iter91 lane).

## Validation Plan (end-to-end)
T1 observability lands green → T2 epoch fix green + zero `_eager_held` hits → T3 pins
green (regression pin proven to catch the bug) → T4 owner live replay: reply SPOKEN where
it was silent, zero `held_swallow` → T5 confidence verdict recorded (C gated/un-gated) →
T6 twilio preview: same → T7 records + ASK. NO merges without owner say-so.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| C — confidence-band repair ("say that again?" reply) | own branch; gated on T5 verdict (owner T0 answer 2) |
| Savage piece 1 — warm abort cap (`_await_warm` builder.py:633-669, ~300-400ms) | next branch after iter93 live validation (owner parking call); NO collision with iter93 (verified) |
| Savage piece 2 — spec abort on resume | already in the tree (session.py:652); kept + hardened by T2 |
| PT-81 same-state re-round warm | after savage piece 1 (it adds rehearsals; savage keeps them cheap) |
| PORT-list remainder (P4 ack filter, P7 said-truth, P6 soft filler) | later, one per branch; P4 wants the epoch gate merged first |
| Real Twilio PSTN cutover | own session after iter93 merge + cutover plan |
| py playback time-stretch accelerator | iter94+ prod work, parked |
| Cleanup deletions (wt-92, engine/92-92b-4gk-quant, wt-merge87, wt-iter91 lane) + frozen-checkout strays (GIT_TREE.md mod + untracked scripts/call_ledger.py) | owner trigger word; folded into T7 asks |
| iter77-twilio-iter70 (parked merge-ready @ 8c5f72f) | owner decision AFTER this fix exists |


## Verdict (2026-10-06, appended at close)
EXECUTED T1-T3 on `engine/iter93-held-adopt-race` (pushed @ `e57d2b2`; commits `fdadf22`
observability, `3bf86fc` epoch fix, `e57d2b2` race battery + hardening). Suite **502/3/0**.
Live owner call (trace `2d3cfa48773a`): **zero `held_swallow` anomalies**, both false
starts discarded silently, every confirmed EOT released with epoch stamps — the
fire-lag/swallow disease is dead. NOT yet done: fragment-pattern clean replay (T4),
confidence-semantics table (T5), twilio preview (T6) — ride plans/plan_v5_iter94_pause_ladder_loop.md
T4 if the owner opts in. Merge = owner say-so only. The call also surfaced PT-84 (the
pause-ladder re-arm loop — a SEPARATE disease, pre-existing, now planned as iter94).