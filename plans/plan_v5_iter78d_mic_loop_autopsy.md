# plan_v5_iter78d_mic_loop_autopsy — full audit: working mic bridge → iter78 loop regression + fix plan

## Meta
- Date: 2026-09-25
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Work box: OREGON `5.78.83.174` (`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`)
- Scope: ONE question answered with EVIDENCE (no guesses): which exact change(s) between the
  working 2026-09-24 mic-bridge call and today's iter78 lane break the real-human mic path
  (re-ask loop + "agent does not hear me"), then a gated fix plan.
- Status: T1+T2 EXECUTED 2026-09-25 (Helsinki session) — full report:
  `research/surgeon/iter78-merged-turn-yield/03_autopsy.md`. T3 (A/B) awaits owner.

## Compaction Context (fresh-agent handoff)
**Project:** Dialux SDR v5 voice engine (LangGraph + Deepgram flux STT + gpt-5.4 + EL/Cartesia
TTS). Work box OREGON 5.78.83.174; Helsinki 46.62.233.228 = Langfuse :3001 + reference. OR main
checkout `/home/julio/projects/clean_diallux_SDR` = prod tree, NEVER switch it. Worktree
`/tmp/opencode/wt-iter78` @ branch `engine/iter78-merged-turn-yield` @ `d8260c2`. Lane :8025 =
uvicorn from worktree cwd with OR venv
`/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`; log
`/tmp/opencode/voice_server_8025.log`; token `/tmp/opencode/iter78_mic_token` (never print);
mic page `http://127.0.0.1:8025/mic?rate=<0.80-1.15>&k=<TOKEN>` (browser playback-rate knob,
read per page load; server restart needed for env changes).

**THE WORKING STATE (baseline, do not degrade it):** 2026-09-24 06:54, mic-bridge call
`96746e56d2fa`, 43 turns, BOOKED, Langfuse trace `fe687befd6027609c62d11ff15b1ba7b` on
Helsinki :3001. Proven config from the trace metadata: `transport=browser`, `stt_mode=flux`,
`eager_eot=true`, `tts=elevenlabs/eleven_turbo_v2_5`, voice `ZSNL4hPqCnqoMPaI4jGX` (Hannah),
llm `gpt-5.4`. Voice settings per state come from
`/tmp/opencode/wt-iter78/engine/diallux/media/delivery.py` `DELIVERY_PROFILES` (per-provider
dict per state; e.g. Intake EL stability 0.50 / style 0.30 / speed 1.02) — this file is
byte-identical on every branch since the restructure (`b94dad4`), so VOICE CONFIG IS NOT THE
REGRESSION. The browser `?rate=` knob was BROKEN on the working call (iter73 fixed it) — the
working call ran rate=1.0. Zero `pause_reask` spans in the working trace (the 10s
caller-silence timer never fired in 43 turns).

**THE BROKEN STATE (2026-09-25, four real-human sessions on :8025, owner Julio speaking):**
1. `08:12` sid `96136c7baef0`, eager=ON yield=ON rate=1.0: RE-ASK LOOP — Intake stuck turns
   1-11, `eager turn started (speculative)` + `eot adopted running eager turn` churn,
   `barge-in` from turn 6, `pause re-ask firing (armed at turn 6)`, delta_tokens stuck at
   638/839 (same fragment re-fed), input crawls 3096→3360. Langfuse `c2f292881ac5a37b5f88db4dc7cb4e24`.
2. `08:33` `d4ba54991b9d` + `08:35` `d003e67b411c`: short owner voice/rate tests (eager=OFF
   yield=ON), no full transcript analyzed yet.
3. `08:46` sid `73c8a7a97d34`, eager=OFF yield=ON rate=1.15: STILL LOOPED — Intake stuck turns
   1-9; `pause re-ask firing (armed at turn 6)` at 08:47:38 (11s after turn 6 finished) +
   `barge-in` at the same instant; turns 8/9 = "So... what kind of business are you in?" /
   "What line of work are you in?" (re-asks). STT gap: `stt state: StartOfTurn (turn 7)` at
   08:47:45 with NO graph round between turn 6 and turn 8 — owner states "I spoke and the
   agent did not listen": owner speech produced NO complete user_text turn.
   Langfuse `70983c3dbb1d020aea195c1700548d31`.
**OWNER VERDICT:** "yield fucked it up" (declared 08:5x after the 08:46 run). Knobs flipped
today, in order: eager true→false + THRESHOLD commented (08:3x), EL speed 1.1→1.0 (08:4x),
yield true→false (08:5x, NOT yet re-tested by owner). Current lane env state: eager=OFF,
THRESHOLD commented, yield=OFF, EL speed=1.0, `PAUSE_REASK` NOT SET (code default TRUE).
Env backup: `/tmp/opencode/wt-iter78/engine/.env.bak_iter78c`.

**PRIME SUSPECTS (ranked by evidence, NOT yet proven):**
- S1 `pause_reask` timer (iter70 T2, `config.py:180` `pause_reask: bool = True`, `pause_reask_ms:
  10000`, `session.py:739`): fired in BOTH looped sessions at the exact cut instant; never fired
  in the working call. With a real human it fires during natural >10s pauses and barge-in's the
  caller.
- S2 STT "not listening": owner speech produced fragments (delta_tokens 638/839 repeated) or NO
  turn (gap turn 7). Possible causes: fragment adoption ordering, barge-in dump clearing STT
  buffers, mic page not streaming during pause, flux socket starvation. UNPROVEN — needs T2.
- S3 `TTS_YIELD_ON_QUESTION` (iter78 `d4fe473`): cuts agent TTS after first spoken "?";
  present in both looped sessions, absent in working call. Owner blames it; eager exoneration
  (eager off still looped) is consistent but yield-off is NOT yet tested live.
- S4 directive-line removals from the 4 state .md files (`05be69e`, iter78 commit 1): changes
  agent prompt behavior; cannot cause STT "not listening" but could change re-ask phrasing.
- S5 cherry-picked mic-caller artifacts (`bf21983` + `d8260c2`): driver-only; CANNOT affect the
  browser path (owner ran browser mic) — lowest priority.
- EXONERATED: eager-EOT (loop reproduced with eager=OFF), voice config/delivery.py, EL voice
  identity, model (gpt-5.4 both eras).

**GIT GENEALOGY (verified):** iter78-merged-turn-yield = iter77-twilio-iter70 + iter76
cherry-picks (`bf21983` driver, `d8260c2` persona ext) + iter78 commits (`05be69e` directive
removal, `d4fe473` yield, `6001f53`+`746fbd8` evidence/harness). `engine/iter74-speech-production`
(SpeechLedger + cancel-reconcile) is NOT an ancestor of iter78. iter72-voice-lab is NOT an
ancestor either. Delta iter77→iter78 code: prompts/*.md line removals + yield machinery +
driver/tests. delivery.py, deepgram_stt.py, session.py EOT logic identical to working era
EXCEPT whatever iter73-77 landed on session.py — UNVERIFIED, task T1 must diff it exactly.

**Laws in force:** VOICE LAW `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` preserved in any env
edit; MODEL LAW gpt-5.4; LAW 0 no merges without owner; evidence → `research/surgeon/`;
bookings → cancel every one (Cal.com event 3801235 REAL).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| NO code changes until the audit (T1-T3) is complete | Owner: "we are not fucking guessing" — 4 iters of knob-flipping without a controlled verdict is how we got here |
| Working baseline = call `96746e56d2fa` (2026-09-24 06:54) config | Only BOOKED real-human mic-bridge call with full Langfuse evidence |
| Verdict requires controlled A/B on the LIVE lane with the SAME probes | Owner's earlier probes varied (deliberate pauses, different rate) — confounded |
| `PAUSE_REASK` treat-as-suspect, not default-off fix yet | Fired in both broken sessions but a controlled no-pause-reask run has never been done |
| All fixes ride `engine/iter78-merged-turn-yield` or a NEW branch cut by owner order — no new unstaged work | LAW 0 + owner branch trigger word rule |
| Lane :8025 is the only lane touched | Prod :8026 + mic :8090 untouchable |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Which exact branch/commit served the working 06:54 call | OR/Helsinki journald or lane log around 2026-09-24 06:54; session metadata only says `diallux-langgraph-production` |
| Whether Deepgram flux returned full transcripts for owner speech in `73c8a7a97d34` | lane log STT lines / mic_events table / Langfuse obs for turn 7 gap |
| What the 08:33/08:35 short sessions were (owner memory) | owner |
| Owner availability for the T3 controlled probe runs | owner |

## Environment & Dependencies
- Boxes: OREGON `root@5.78.83.174` (work), Helsinki `46.62.233.228` (Langfuse :3001).
- Langfuse API: `${LANGFUSE_HOST}/api/public/traces` basic-auth
  `${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}` (both in
  `/home/julio/projects/clean_diallux_SDR/engine/.env`). Trace ids pinned in Compaction Context.
- Worktree `/tmp/opencode/wt-iter78` @ `d8260c2`; venv
  `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (pytest 9.1.1, pydantic 2.13.5,
  langfuse 4.15.1). Run pytest from worktree cwd.
- Lane :8025 restart command in Deploy Rules below. Mic page URL pattern
  `http://127.0.0.1:8025/mic?rate=<R>&k=<TOKEN>`; token read via
  `TOKEN=$(cat /tmp/opencode/iter78_mic_token)` on OR.
- Evidence dir: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/`
  (gitignored). Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  via `/home/julio/projects/clean_diallux_SDR/scripts/live_sql.py` (no sqlite3 CLI — use the venv).
- Suite gate: exactly 3 known env-knob fails (test_iter46_latency_floor,
  test_iter59_dedupe_semantic, test_iter60_audit_fixes), everything else green.

## Architecture (block diagram)
```
browser mic page (?rate) --WS /mic/ws (token)--> session.py
   STT deepgram flux ──(EagerEOT?/EOT/2.5s backstop)──> graph round (gpt-5.4)
        pause_reask 10s timer (iter70 T2) ──> engine-initiated RE-ASK turn
        TTS_YIELD_ON_QUESTION (iter78) ──> TTS cut after first "?"
        barge-in (caller speech) ──> TTS cancel + STT dump
   audit: git genealogy (T1) + STT forensics (T2) + controlled 2x2 A/B (T3) → verdict (T4) → fix (T5)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/03_autopsy.md` | the audit report: genealogy table, STT forensics, A/B matrix, verdict | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/ab_<cfg>.json` | per-config A/B evidence json | New (gitignored) |
| `/tmp/opencode/wt-iter78/engine/.env` | ONLY knob flips for A/B (each restored after; backup exists at `.env.bak_iter78c`) | Edit (restore after) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | new PT rows from verdict (T5) | Edit (docs → main) |
| branch code (only if verdict demands): `session.py` `pause_reask` gating or `config.py` default | one-variable fix per verdict | Edit (owner-gated) |

## Deploy Rules
- Lane restart (OR): `pkill -f "uvicorn diallux.app:app.*8025"; sleep 2; cd
  /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && setsid nohup
  /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app
  --host 127.0.0.1 --port 8025 </dev/null >> /tmp/opencode/voice_server_8025.log 2>&1 & sleep 5;
  ss -tln | grep "127.0.0.1:8025 "`
- NEVER touch: OR prod `diallux.service` :8026 + `diallux-mic.service` :8090, OR :8001-8003,
  `/opt/diallux-production/.env`, Helsinki :8020/:8024, `CARTESIA_MODEL_ID` pin.
- After EVERY A/B config: restore env to the audit-start state (eager=OFF, THRESHOLD commented,
  yield=OFF, EL speed=1.0) and diff against `/tmp/opencode/wt-iter78/engine/.env.bak_iter78c`.

## Tasks (in order)

### T1 — Git genealogy audit (code truth, no owner needed)
Goal: the EXACT code delta between the working mic-bridge era and the iter78 lane, file by file.
1. Identify the commit that served the 06:54 working call: `ssh -i
   /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'journalctl --user -u diallux-8025*
   --since "2026-09-24 06:40" --until "2026-09-24 07:10"'` (or grep
   `/tmp/opencode/voice_server_8025.log*` + any rotated logs for the 06:54 window; also check
   Helsinki lane logs if OR has none). Record branch+sha in `03_autopsy.md`. If UNKNOWN after
   honest search → BLOCKED table, fall back to branch-level diff (iter72-voice-lab..iter78).
2. Full-tree diff: `cd /home/julio/projects/clean_diallux_SDR && git diff --stat
   engine/iter72-voice-lab..engine/iter78-merged-turn-yield -- engine/diallux/
   engine/diallux/prompts/` then per-file diffs for EVERY changed file under `engine/diallux/`
   (session.py, app.py, graph/*, media/*, config.py, prompts/*). For each: one-line verdict —
   could it contribute to (a) re-ask loop, (b) STT ignoring owner speech?
3. Same diff for `engine/iter73*`, `engine/iter74-speech-production`, `engine/iter75*`,
   `engine/iter76*`, `engine/iter77*` individually vs their merge-bases to date each behavior
   (pause_reask came from iter70 T2 — verify it was IN the working call's code and simply never
   triggered, or landed later).
Verification: `03_autopsy.md` has a table: file → iter introduced → risk verdict. ZERO
unexplained behavioral deltas remain.

### T2 — STT forensics: "the agent did not hear me"
Goal: explain the 08:47:23-38 window of `73c8a7a97d34` — owner spoke, no turn happened.
1. Pull every log line for the call: `ssh OR 'grep "73c8a7a97d34"
   /tmp/opencode/voice_server_8025.log'` — save to
   `research/surgeon/iter78-merged-turn-yield/stt_forensics_73c8a7a97d34.log`.
2. From Langfuse trace `70983c3dbb1d020aea195c1700548d31` pull ALL observations for turns 6-9
   (inputs, `eot_silence_wait`, `rag`, `await_warm`) and reconstruct: what user_text did each
   graph round actually receive? What did STT produce between 08:47:27 and 08:47:38?
3. Read the mic page code `/tmp/opencode/wt-iter78/engine/diallux/static/mic/index.html`: does
   it stream frames continuously (including silence) or gate on VAD/mute? Does barge-in dump
   STT state server-side (`session.py` barge-in handler: does it flush/drop the flux socket
   buffer or `finalize` a fragment)?
4. Compare with the working call's turn rhythm (trace
   `fe687befd6027609c62d11ff15b1ba7b`): gap lengths between user end and agent start; whether
   any >10s user pause existed (if none, the working call simply never exercised S1/S2 — say so).
Verification: a written causal chain for the turn-7 gap with line/log citations, or explicit
UNKNOWN + what evidence is missing.

### T3 — Controlled A/B on the live lane (2x2 matrix, owner probes)
Goal: isolate S1 (pause_reask) and S3 (yield) with everything else pinned. Eager stays OFF
(exonerated); rate=1.0; EL speed=1.0; THRESHOLD stays commented.
Configs: A = pause_reask ON, yield ON (today's broken state) · B = pause_reask OFF, yield ON ·
C = pause_reask ON, yield OFF · D = pause_reask OFF, yield OFF (proven-config-minus-knobs).
Procedure per config: set BOTH env lines (`PAUSE_REASK=true|false`,
`TTS_YIELD_ON_QUESTION=true|false`), restart lane (Deploy Rules), owner runs the SAME
4 probes (mid-sentence pause ≥10s, short ack, listen for glue, transition ack) TWICE, save
evidence json + log excerpt per run. Watch live: `ssh OR 'tail -f
/tmp/opencode/voice_server_8025.log | grep -E "pause re-ask|barge-in|turn=.*state="'`.
Record per config: loop? re-ask count? pause_reask fired? owner speech heard (turns produced)?
Verification: 8 runs total, each with evidence json in
`research/surgeon/iter78-merged-turn-yield/ab_<A|B|C|D>_<1|2>.json`; matrix filled in
`03_autopsy.md`. Cancel any booking created immediately (event 3801235 REAL).

### T4 — Verdict
Goal: name the culprit(s) with the matrix + forensics. Write into `03_autopsy.md`:
- per-suspect verdict (S1..S5): CONFIRMED / EXONERATED / CONTRIBUTING, with the run ids
- the single minimal fix (expected shape: `PAUSE_REASK=false` default for human-facing lanes +
  possibly a re-arm guard "never arm when agent turn ended with a question", but ONLY what the
  matrix proves)
- what to restore: the proven env (eager per owner choice — eager exonerated, working call ran
  it ON; yield per matrix; PAUSE_REASK per matrix).
Verification: owner signs off the verdict in chat before any code move.

### T5 — Fix + closeout (owner-gated)
1. Apply the minimal fix on `engine/iter78-merged-turn-yield` (if env-only: env only; if code:
   ONE commit, one variable, pins in `engine/tests/`).
2. Suite gate: `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a &&
   /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q 2>&1 |
   tail -6` → exactly the 3 known env-knob fails.
3. Owner re-runs the T0 ear probes on the fixed lane → PASS verdict recorded.
4. Ledger: `scripts/live_sql.py import --window "<HH:MM-HH:MM>" --run autopsy-iter78d --commit
   <sha>` from the main checkout cwd; findings rows for each CONFIRMED suspect.
5. `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md`: add PT rows (mic loop
   regression: verdict + fix; the STT turn-7 gap finding). Append the iter78d section to
   `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md`.
6. Push via `/home/julio/projects/clean_diallux_SDR/scripts/keyhound` + `git push origin
   engine/iter78-merged-turn-yield` FROM the main checkout cwd. Docs (report paths aside —
   gitignored) → main: PENDING_TASKS only, committed straight to main per LAW 0.

## Validation Plan (end-to-end)
1. T1 table complete — no unexplained delta between working and broken eras.
2. T2 causal chain for the turn-7 gap (or documented UNKNOWN with the exact missing evidence).
3. T3 matrix filled with 8 runs; the culprit reproduces ON and disappears OFF in isolation.
4. Fix applied → owner ear PASS → suite green (3 known fails only) → ledger + PENDING_TASKS
   persisted → branch pushed.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter74 SpeechLedger / cancel-reconcile merge into iter78 | separate merge decision, LAW 0; note it as candidate fix ONLY if the matrix points there |
| GK battery (5 personas) | blocked until loop confirmed GONE (iter78c plan T3 gate stands) |
| Browser `?rate=` clamp raise / buffer-starvation investigation | owner parked it ("leave it") pending the loop fix |
| iter76 driver room-tone fix | fake-caller path; only after the human path is clean |
| Prod :8026 knob alignment | separate owner decision after the verdict (prod runs eager=true today) |

## AUDIT RESULTS — T1+T2 executed 2026-09-25 (see research/surgeon/iter78-merged-turn-yield/03_autopsy.md)

**T1 (genealogy) — the plan's BLOCKED item #1 is RESOLVED, and it flips the premise:**
- The working call `96746e56d2fa` (Sep 24 06:54) ran on **Helsinki :8024**
  (`diallux-8024.service`, pid 1196492, started 06:53:59 — journal: 60 lines for the sid) from the
  Helsinki main checkout @ `engine/iter73-playback-rate` ≈ `1a8e04a`, whose diff vs main is 4 lines
  of mic-page JS only → **engine = main = iter66-era. NO pause_reask, NO yield, NO iter70 stack.**
  The 06:47 outage trio ran on the same lane; the RATE fix was hot-patched on disk before the
  06:53:59 restart (committed 09:01 `9ccdccf`).
- Working-call env frozen in `/proc/1196492/environ`: EL Hannah `turbo_v2_5` 1.0/0.7/1.0,
  `DEEPGRAM_EAGER_EOT=true` **THRESHOLD=0.6**, gpt-5.4, Cartesia pin intact — env byte-identical
  to the broken lane's EL block; `delivery.py` identical main..iter78 (empty diff).
- The iter70 fixes' fake-call pass (owner memory, CONFIRMED): Langfuse Sep 23 15:07-15:10
  bookdanny/susan/marcus, all pass — from Helsinki wt-iter70, **chat plane only**. The iter70+
  stack's first real-human audio-plane test = the Sep 25 broken sessions.

**T2 (STT forensics) — causal chain proven (08:46 session):** turn 6 ends 08:47:27 → owner silent
10.3s → **pause re-ask firing (armed at turn 6)** 08:47:38.086 → owner answers into the re-ask →
**barge-in 08:47:38.459** → STT dump swallows the in-flight speech (turn 7 gap; turn 8 completes
BEFORE turn 7) → fragment user_text ("said you can.") → re-ask → loop. Same pattern at 08:12 from
turn 5. **The 07:39-07:51 driver smokes' "fake-caller re-ask loop" is the same mechanism** (pause
re-ask firing ×6 during the driver's 5-15s gaps) — the iter78c eager-EOT hypothesis was wrong.

**Verdicts:** S1 pause_reask **CONFIRMED root** (fired at the loop instant in both owner sessions +
driver smokes; absent from the working baseline's code; complete mechanism). S2 not-listening
**= consequence of S1's barge-in STT dump**. S3 yield **CONTRIBUTING amplifier** (shorter turns →
wider silence windows → more S1 firings; audible mid-sentence cuts; yield-off NEVER tested —
flipped after 08:46, lane down 08:48). S4/S5 standdown/exonerated. eager-EOT exonerated (again).
**Voice config EXONERATED** — env byte-identical (frozen /proc proof), delivery.py identical;
"voice was sht" = yield cuts + re-ask stutter + the 08:12 speed-1.1 experiment (owner-reverted).

**T3 A/B configs updated (restore working-call parity):** eager stays **ON with
DEEPGRAM_EAGER_EOT_THRESHOLD=0.6** (the working call ran 0.6; the broken lane ran 0.7/default —
restore it). D (both OFF + eager ON @0.6) = expected working-state restore. B isolates yield.
Add to the env-restore rule: `PAUSE_REASK=false`, `TTS_YIELD_ON_QUESTION=false`,
`DEEPGRAM_EAGER_EOT=true`, `DEEPGRAM_EAGER_EOT_THRESHOLD=0.6`, EL speed 1.0 (already), Cartesia
pin preserved.

**Git-mess findings (separate owner decision, none touched):** OR prod tree (:8026/:8090,
restarted 06:17 Sep 25) is checked out on WIP branch `engine/iter73-oregon-wip-20260924 @ df23d37`
(NOT main; iter73-era engine + validator→127.0.0.1:8080 WIP edit). Helsinki main checkout parked on
`engine/iter76-harness-firesim` with 4 never-committed plan files (iter74/76/78b/78c). Reflogs
rsync-mirrored through Sep 24 09:01 then diverged. Cherry-pick duplicates (iter73/75 on ≥2 lines;
iter76 driver 24991b8=bf21983). GitHub: origin/main == local main @ 6d668ca; iter78 pushed.
