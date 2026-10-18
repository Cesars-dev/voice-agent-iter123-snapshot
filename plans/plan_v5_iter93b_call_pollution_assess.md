# plan_v5_iter93b — CRITICAL: the call is being destroyed — agent barges in every 8 seconds ("Hey, are you still there?") + Linda speaks mid-thought. Find the pollution, fix the call.

## Meta
- Date: 2026-10-06
- Project root (OREGON source of truth): `/home/julio/projects/clean_diallux_SDR`
- Session box: Finland (julio @ 46.62.233.228). ALL repo git ops ssh-wrapped to OREGON:
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'`
  Git WRITES: docs via OREGON `/tmp/opencode/wt-main-docs`; code (ONLY after owner GO)
  via a fresh `wt-94` lane. OR main checkout is FROZEN: never checkout/switch/reset/pull there.
  **SYNC LAW (owner, 2026-10-06): everything lands on GitHub — push from OREGON, pull in
  Finland (`git fetch && git merge --ff-only origin/main`); NEVER rsync/scp. Evidence must
  be queryable from Finland or GitHub alone — the next agent MUST NOT go blind.**
- **Numbering (owner correction, 2026-10-06, HARD):** this is **iter93b**, NOT iter94.
  iterNN mints ONLY when `engine/diallux/` code is modified. This mission is ANALYSIS:
  no code changes yet — it carries the last cut code iter (the race fix iter93) with the
  suffix `b`. The eventual CODE fix mints iter94 only when that branch is cut.
- Scope: **CRITICAL CALL-POLLUTION ASSESSMENT.** The live call (owner, 2026-10-06) was
  destroyed: Linda barged in with "Hey, are you still there?" on a loop every ~8s and
  spoke mid-thought ("Absolutely, go ahead") while the caller was mid-sentence. The
  offline suite is green and the previous disease (the FIND-35 swallow) tested clean —
  **none of that matters if the real call is wrecked.** The measure of success is the
  CALL, not the suite. Find what is polluting the call, assess in depth, propose the
  minimal fix, get owner GO — only then cut code.
- Status: PLAN ONLY (not started — owner called the bug in-session 2026-10-06; analysis GO)

## Compaction Context

### iter93 state at handoff (VERIFIED this session)
- Branch `engine/iter93-held-adopt-race` on GitHub @ tip `e57d2b2`. 3 commits: `fdadf22`
  (observability: raw flux TurnInfo dump env-gated default OFF, `held_epoch`/`released_epoch`
  stamps, `held_swallow` detector, PT-79 rag provenance), `3bf86fc` (epoch discipline:
  `_eager_held` DELETED → `_epoch`/`_held`/`_tts_ctx_epoch`/`_turn_task_epoch`; hold arms
  in the eager-fire SYNC zone; sync `gate.invalidate(upto)`; adopt = transcript-equality
  contract; `reset()` = teardown only), `e57d2b2` (race battery: 48.94 headphone regression
  pin, 200-seed random interleavings, stutter persona; gate `_floor`+`advance()` —
  cross-gen buffer mixing closed; resume acts on finished-but-held turns — orphan 2 closed).
- Suite: **502 passed / 3 skipped / 0 failed**. iter93 UNMERGED (owner say-so pending).

### THE DISASTER (owner live call 2026-10-06 02:18–02:20, headphones, mic bridge, lane 8049)
- Langfuse trace `2d3cfa48773a` (micbridge-b244c634a9ee), 5 LLM generations, 70 spans.
- What iter93 DID prove live: zero `held_swallow` anomalies; false starts discarded
  silently (`resumed_count` reached 2); confirmed EOTs released with epoch stamps.
  **But the caller experience was destroyed anyway:**
  1. **"Hey, are you still there?" on a LOOP, every ~8 seconds.** Our pause ladder, not
     Deepgram: `pause_ladder_mode="reminder"` + `pause_reask_ms=8000` (code defaults,
     iter87 pack — `config.py:470-475`; lane .env has NO `PAUSE_*` overrides; text =
     `pause_reminder_text = "Hey, are you still there?"`). Nudges in the trace at
     02:19:01 and 02:19:31. **Loop mechanism:** `_ladder_arm()` (session.py:374) RESETS
     `_ladder_step = 0` and is called from TWO sites that fire on EVERY agent turn —
     `on_twilio_mark` (session.py:446, mark echo = playback done) and
     `_late_turn_report` (session.py:935, browser arm). Every agent turn re-arms a fresh
     8s reminder clock; the close rung (`pause_close_ms=45000`) only lives inside ONE
     ladder run and keeps getting reset. The caller experiences: every time Linda stops
     talking, 8s later she asks "are you still there?" — forever. A caller THINKING
     after Linda's question gets stepped on.
  2. **Linda speaks MID-THOUGHT.** Transcript turn 4: caller said "Okay. Uh, Yeah. I was
     about to speak." — a fragment; Deepgram CONFIRMED EOT on it (`eot_threshold=0.65`
     hit in ~2–600ms on the owner's pause cadence: turn 6 eager→confirm 121ms; turn 7
     **2ms**) → engine released the held draft → Linda: "Absolutely, go ahead." The
     engine followed protocol; the CONFIRMS were false positives from Deepgram's
     detection cadence on fragment-paced speech. Owner suspects a Deepgram param
     ("probably an eager, a deepgram param… probably one string, two string code block").
- The "could you repeat that again?" repair does NOT exist (branch C, gated on the T5
  confidence table) — no such generation this call.

### Owner words (2026-10-06 — DO NOT re-ask)
- "We had a disaster. The agent was barging in every 8,000 milliseconds… we need to find
  what's polluting the call and we gotta fix it. That's the point of the plan."
- "This is not iter 94 — iteration means we're modifying code. We're not modifying
  anything right now." → renumbered iter93b.
- "By the way, make sure everything lands, even the new plan. Make sure it's queryable
  via Finland or even GitHub… push from Oregon, pull in Finland… not via rsync or SCP."

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| **CRITICAL framing: the call is broken; the suite being green is NOT success** | owner: "no matter how good it looks… find what's polluting the call" — the call IS the validation surface |
| Numbering = **iter93b** (zero-code analysis); iter94 mints ONLY when the code branch is cut | ITERATION NUMBERING LAW + owner's hard correction (drift on record: iter90/92/92b took bare numbers with zero code — do not repeat) |
| Analysis BEFORE any edit; no blind one-line fix | owner: "analyze the code… check it in depth" |
| Reminder timing/mode knobs stay OWNER-SET (`.env` owner-set only); agent proposes, owner says the numbers | SWITCH LAW; 8s is owner-ratified (iter87 pack) until the owner changes it |
| `CALL_PREWARM=true` flipped LANE-LOCAL on 8049 per owner order; canonical still false — owner ratifies or reverts | owner directive; on the record |
| Prewarm stack verified live (STT 88ms ready, TTS 89ms ready, RAG 1044ms, OpenAI boot prewarm 2500ms) | owner asked pre-call; evidence in `/tmp/opencode/lane-8049.log` |
| All git sync via GitHub (push OREGON → pull Finland); evidence dirs stay gitignored; registry + ledger are the queryable layer | owner sync law |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner knob decisions: `DEEPGRAM_EOT_THRESHOLD` (0.65), `DEEPGRAM_EAGER_EOT_THRESHOLD` (0.35), `PAUSE_REASK_MS` (8000), `PAUSE_LADDER_MODE` (reminder) | owner says the numbers in-session; agent never edits canonical `.env` without owner say-so |
| Owner GO on the fix shape (after iter93b analysis) → THEN the code branch cuts as **iter94** | iter93b T2 output |
| iter93 merge say-so | after a clean fragment replay on the fixed lane |

## Environment & Dependencies
- Python venv (ONLY this): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`
  (Py 3.12; never `bin/pip`, always `-m pip`).
- Suite (only if/when code is cut): `cd /tmp/opencode/wt-94/engine && .venv/bin/python -m pytest tests -q`
  (expect 502 passed / 3 skipped baseline).
- Lane boot (reuse 8049; stop the wt-93 server first — it was pid 1545931):
  `cd /tmp/opencode/wt-94/engine && set -a && . ./.env && set +a && setsid nohup .venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8049 > /tmp/opencode/lane-8049.log 2>&1 < /dev/null &`
- Key files (absolute, line numbers @ iter93 tip `e57d2b2`):
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` — ladder:
    `_ladder_disarm` :360, `_ladder_arm` :374 (resets `_ladder_step=0` — THE LOOP),
    `_ladder_run` :387 (8s rungs + `pause_close_ms=45000` close), `_ladder_close` :411,
    `_speak_exact` :343; re-arm sites: `on_twilio_mark` :446, `_late_turn_report` :935
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` — `pause_ladder_mode`
    :470, `pause_reask_ms` :471, `pause_reminder_text` :474, `pause_reminder_text_2` :475,
    `pause_ladder_max`; Deepgram: `deepgram_eot_threshold` :354,
    `deepgram_eot_timeout_ms` :355, `deepgram_eager_eot_threshold` :356
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/deepgram_stt.py` — connect
    URL params `eot_threshold`/`eot_timeout_ms`/`eager_eot_threshold` :82-86
  - Existing green pins: `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter93_epoch_race.py`,
    `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter93_observability.py`
- Langfuse (OREGON, `http://localhost:3001`): from the engine dir with `.env` loaded:
  `sys.path.insert(0, 'scripts'); import lf; lf._get('/api/public/traces?fromTimestamp=' + lf._iso(2) + '&limit=20')`,
  then `lf._get(f'/api/public/traces/{tid}')` for observations. Trace of record: `2d3cfa48773a`.
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (import via `/home/julio/projects/clean_diallux_SDR/scripts/live_sql.py`; no sqlite3 CLI).
- Registry: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db`
  (generator `/home/julio/projects/clean_diallux_SDR/scripts/call_ledger.py` — run with
  `build` from the MAIN checkout engine dir; backup `ledger.db` first — refreshed this
  session, iter93 @ e57d2b2 `open`).
- GitHub push (any OREGON worktree): `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push origin <ref>`
  (flag ORDER: `-c` before `push`); keyhound before EVERY push — standing 259-hit noise =
  legacy services/*; only the NEW diff must be 0 key-shaped strings.
- Owner access: ssh tunnel Mac→OR (`ssh -N -L 8049:127.0.0.1:8049 root@5.78.83.174`), URL
  `http://localhost:8049/mic?k=<VOICE_TEST_TOKEN>` (page forwards `?k=` to the WS;
  fail-closed gate, 4401 on mismatch). Token NEVER printed in chat/logs/git.

## Architecture (one diagram)

```
caller silent after ANY agent turn
        │
        ▼
mark echo (twilio) or browser drain ──► _ladder_arm()  ← RESETS _ladder_step=0 (THE LOOP)
        │                                                        │
        ▼                                                        ▼
_ladder_run(): wait 8s (pause_reask_ms) ──► nudge: "Hey, are you still there?"
        │                                                        │
        ▼                                                        ▼
wait close_ms=45s from t0 ──► _ladder_close()          …next agent turn re-arms → LOOP
(hangup, honest goodbye)

Deepgram fragment-confirm cadence (the mid-thought speaks):
fragment ("Okay.") ──► EagerEOT@0.35 (draft held) ──► EOT confirm@0.65 in 2–600ms
        ──► release ──► Linda speaks ──► mark echo ──► ladder re-arms → the felt cadence
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter93b_call_pollution_assess.md` | THIS plan; verdict appended at close | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/` | `01_evidence.md` (loop anatomy + trace timeline + DG params), `02_fix_shape.md` (proposal + owner GO), `03_validation.md` (post-fix replay, if GO), `04_report.md` (gitignored) | NEW (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-84 pointer update to this plan | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | ONLY IF OWNER GO: the ladder fix (expected 1-3 strings; NOT in this analysis session's scope) | EDIT (branch engine/iter94-*, future) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter94_ladder_loop.py` | ONLY IF OWNER GO: ladder pins | NEW (branch, future) |

## Deploy Rules
- NO /opt. NO original-repo services. Lanes 127.0.0.1 only. OR listening now:
  8001/8002/8003/8026/8090 + 8080 caddy — NEVER touch. Stop the wt-93 server (pid on
  8049) before any wt-94 boot.
- OR main checkout: NEVER checkout/switch/reset/pull. Writer = `/tmp/opencode/wt-main-docs` only.
- CODE (only after owner GO): branch `engine/iter94-<slug>` from main tip → suite green →
  live replay → report → ASK JULIO → merge ONLY on say-so (--no-ff, tag `engine/iter94`,
  `scripts/git-tree.sh`, registry refresh, ITERATIONS line).
- Docs straight to main. keyhound + diff-scoped scan (0 key-shaped strings) before every push.
- All evidence sync OREGON → GitHub → Finland. No rsync/scp.
- Cal.com test bookings: cancel everything after ANY booking-touching battery (event
  3801235 REAL).

## Tasks (in order)

### T1 — Evidence + anatomy (NO EDITS)
Goal: pin the exact pollution anatomy: (a) read the ladder code + both re-arm sites
(session.py:374/446/935) and write the loop truth table; (b) replay trace `2d3cfa48773a`
(nudge times vs turn times vs caller speech); (c) enumerate the Deepgram connect params
actually sent on the lane; (d) quantify: how many reminders per silence stretch TODAY vs
SPEC (one nudge → close at 45s total silence).
Files: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/01_evidence.md`
Commands: reads + Langfuse pulls per Environment §.
Verification: 01_evidence.md has the anatomy with line numbers + the TODAY-vs-SPEC table.

### T2 — Fix-shape proposal + owner GO (HITL)
Goal: propose the minimal fix (owner expects 1-2 strings): candidates to evaluate —
`_ladder_arm` stops resetting the step counter mid-stretch (key the stretch to caller
speech, not agent turns); the ladder never re-arms from its own `_speak_exact`; optionally
`pause_ladder_max`/timing knobs. Present the exact diff shape → owner GO (or knob numbers).
Files: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/02_fix_shape.md`
Verification: owner GO recorded (or knobs re-set — also owner).

### T3 — Code fix + pins (ONLY IF OWNER GO)
Goal: cut `engine/iter94-<slug>` from main tip; implement; add
`/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter94_ladder_loop.py`
(fake-clock: one nudge per stretch; no self-re-arm; close fires; fragment-cadence sim).
Verification: suite green (502+new); pins FAIL on the pre-fix tree (stash proof).

### T4 — Live replay (owner validation)
Goal: owner fragment pattern on the fixed lane; the ladder per SPEC; iter93's outstanding
validation rides the same session if the owner opts in (fragment replay T4, confidence
table T5 via scripted fake caller, twilio preview T6 on 8050).
Verification: `/tmp/opencode/lane-8049.log`: zero `held_swallow`, one nudge per stretch,
release+tts_first paired per confirmed turn → `03_validation.md`; ledger import
(`scripts/live_sql.py import --window "…" --run iter94-ladder-validate --commit <tip>`).

### T5 — Report + close-out + ASK JULIO
Goal: `04_report.md`; PT-84 → DONE at merge; registry refresh (backup first); ITERATIONS
lines; plan verdicts; docs push via wt-main-docs; Finland sync verify.
Verification: ASK JULIO contains SHAs, suite counts, evidence links, asks (iter93+iter94
merge say-so; knob numbers; cleanup say-so for wt-92 / engine/92-92b-4gk-quant /
wt-merge87 / wt-iter91 lane).

## Validation Plan (end-to-end)
T1 anatomy pinned → T2 owner GO → T3 fix green + pins proven → T4 live replay: the CALL
is clean (one reminder per stretch, zero swallows, fragment cadence works) → T5 records +
ASK. The success metric is the CALL, not the suite. NO merges without owner say-so.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter93 merge + tag | owner say-so after clean fragment replay |
| C — confidence-band repair ("say that again?") | own branch; gated on the confidence table |
| Savage piece 1 — warm abort cap (`_await_warm` builder.py:633-669) | next branch after iter93 merge |
| PT-81 same-state re-round warm | after savage piece 1 |
| PORT-list remainder (P4/P7/P6) | later, one per branch |
| Real Twilio PSTN cutover | own session after merges |
| py playback time-stretch accelerator | iter94+ prod work, parked |
| Cleanup deletions (wt-92, engine/92-92b-4gk-quant, wt-merge87, wt-iter91 lane) | owner trigger word; T5 asks |
| iter77-twilio-iter70 (parked merge-ready @ 8c5f72f) | owner decision after fixes |
