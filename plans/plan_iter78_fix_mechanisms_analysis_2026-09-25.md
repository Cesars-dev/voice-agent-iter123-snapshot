# iter78 — fix-analysis session: why the iter70/74/78 "polish" fixes misfired + what to delete or port

## Meta
- Date: 2026-09-25
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Work box: OREGON `5.78.83.174` (`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`); Helsinki `46.62.233.228` = local (analysis, Langfuse :3001).
- Scope: ONE session — deep-dive the actual code of the failed "fix" line (iter70 T2/T3/T4', iter74, iter78 T2/T3) against the proven-broken mechanisms (PT-74/PT-75/PT-77), and produce a DELETE-or-PORT decision list per fix. **This is ANALYSIS — NOT a new iteration. No code changes, no new branch, no iter-number increment.** Per owner 2026-09-25: iteration numbers only increment when code changes on a branch.
- Status: PLAN ONLY (not started — awaits owner GO)

## Compaction Context (fresh-agent handoff)
**Project:** Dialux SDR v5 voice engine (LangGraph + Deepgram Flux STT + gpt-5.x LLM + Cartesia/EL TTS).
Server transition done: Helsinki (Finland, 46.62.233.228) = Langfuse :3001 + original repo; OREGON
5.78.83.174 = work box (host `ubuntu-4gb-hil-1`; lanes :8025/8026/8090; worktrees under
`/tmp/opencode/wt-iter*`). Helsinki kept the worktree lab (`/tmp/opencode/wt-*`, one per iter).

**iter78d audit (this session, DONE, report at
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/03_autopsy.md`,
plan updated + pushed to main `2e9e013`):**
- The "working call" (`micbridge-96746e56d2fa`, Sep 24 06:54, 43 turns BOOKED, EL Hannah
  turbo_v2_5 1.0/0.7/1.0, eager=ON threshold=0.6) ran on **Helsinki :8024** from the checkout
  `engine/iter73-playback-rate` ≈ `9ccdccf` — engine = **iter66-era** (main). NO iter70/74/78
  session-layer code. Env frozen in `/proc/1196492/environ` — still running.
- Broken sessions (Sep 25 08:12/08:46 on OR :8025, iter78 branch): **S1 pause_reask (iter70 T2)
  CONFIRMED root** of the re-ask loop (fires ≥10s after every agent turn incl. question-ending;
  caller answers into it → barge-in dumps in-flight STT → fragment/no-turn → re-ask → loop).
  S2 "not listening" = consequence of that STT dump (turn 8 finalized before turn 7). S3
  `TTS_YIELD_ON_QUESTION` = amplifier, not root; never tested OFF. Voice config EXONERATED.
- The iter70 fixes' fake-call pass (Sep 23 15:07-15:10, danny/susan/marcus all booked, from
  `/tmp/opencode/wt-iter70` Helsinki) was **chat-plane only** — it cannot see the audio seam.
- Git mess mapped: OR prod tree on WIP branch `engine/iter73-oregon-wip-20260924 @ df23d37`;
  Helsinki checkout on `engine/iter76-harness-firesim @ c1f2f1b`; 4 plan files never committed
  (iter74/76/78b/78c); cherry-pick duplicates. GitHub main == local main @ `2e9e013`.

**Owner corrections (law, 2026-09-25):**
1. iter70 was supposed to POLISH the agent (verbosity down, dupes down, turns down) — instead
   each "fix" created new problems (this is the second overengineering verdict after iter68).
   The iter66-era "fabulous voice" call was good VOICE quality, not a perfect agent — it still
   had dup/loop/double-triple turns, occasional mute, and transition silence, just rarer.
   OR chat-lane TTFT is excellent (≈630ms vs ≈950ms on Helsinki) — do not degrade latency.
2. **Iteration numbering law:** +1 ONLY when code changes on a branch. Analysis/plans/docs under
   the CURRENT iteration being worked (this = iter78 line). Do not mint iter79/80/…
3. **Snapshot repo exists:** `/home/julio/projects/diallux_sdr_almost_there_b` (Finland, local
   git `main` @ `0ce798f`, pushed public:
   https://github.com/Cesars-dev/diallux_sdr_almost_there) — byte-identical tree of the
   working-call state `9ccdccf` with leaked secrets masked (`${RETELL_KEY_*}` etc.; value ledger
   at `/tmp/opencode/leaked_secrets.env`, 600). It has NO venv; to run it: create fresh venv from
   `/home/julio/projects/diallux_sdr_almost_there_b/engine/requirements.txt` (fastembed pinned).
4. A deep-research prompt for Vapi/Retell turn-taking mechanisms (prompt drafted this session:
   EOT endpointing, barge-in transcript handling, silence recovery, dup prevention, agent-mute
   recovery, turn-manager ownership). Research results are INPUT to this analysis when available.

**Laws in force:** LAW 0 (no code merges without owner); VOICE LAW
`CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` env pin preserved; MODEL LAW gpt-5.4; evidence →
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/` (gitignored);
bookings → cancel every one (Cal.com event 3801235 REAL); engine lane :8025 = test only, prod
:8026 + mic :8090 untouchable; no `rm -rf`瘾/stop/disable/reboot on this box (owner permission set).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| This is an ANALYSIS plan under the iter78 line — no iter79 number, no new branch, zero code edits | Owner rule: iteration +1 = code change only |
| The "fix" line to dissect = iter70 T2/T3/T4'/T5 (`65f3567`,`94f5164`,`02b4bef`,`87a0ce5`,`dc62fb9`) + iter74 (`9c486b8`,`5dac0d4`,`3f8a79a`,`634159c`,`5ffcc67`) + iter78 T2/T3 (`05be69e`,`d4fe473`) | Per owner: these created more problems than they solved; each needs a written mechanism autopsy + verdict before any next code move |
| Working baseline for every comparison = `9ccdccf` tree (= `/home/julio/projects/diallux_sdr_almost_there_b`) + working-call env (EL Hannah turbo_v2_5 1.0/0.7/1.0, eager=ON 0.6) | Only real-human BOOKED audio call with full Langfuse evidence |
| Verdict format per fix: KEEP / DELETE / REDESIGN, with removal diff-shape | Gives the next (owner-gated) code iteration a shopping list instead of more knob-flipping |
| TTFT 630ms (OR chat lane) is non-negotiable | Owner measurement; any recommendation that adds prefill or extra LLM rounds fails review |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Deep-research results (Vapi/Retell/LiveKit/Pipecat mechanisms dossier) | Owner runs the research prompt (delivered earlier this session); paste/findings file into `research/surgeon/iter78-merged-turn-yield/04_platform_mechanisms.md` before T3 |
| Owner pick: analysis-only vs analysis+proposal-of-next-code-itter | owner, at T5 sign-off |

## Environment & Dependencies
- Boxes: Finland local (`MainVps`) + OREGON `root@5.78.83.174`. OR worktree:
  `/tmp/opencode/wt-iter78` @ `d8260c2` (branch `engine/iter78-merged-turn-yield`). Helsinki
  checkouts: `/home/julio/projects/clean_diallux_SDR` (HEAD `engine/iter76-harness-firesim` @
  `c1f2f1b`) and snapshot `/home/julio/projects/diallux_sdr_almost_there_b`.
- Branch refs available locally on Helsinki (fetched): `origin/engine/iter78-merged-turn-yield`,
  `engine/iter70-speech-fixes` @ `dc62fb9`, `engine/iter74-speech-production` @ `5ffcc67`,
  `engine/iter77-twilio-iter70` @ `8c5f72f`, `main` @ `2e9e013`.
- Python for any read-only analysis scripts: system `python3` (no repo venv needed); notebooks of
  evidence pull via `jq`/`python3` only.
- Langfuse API (Helsinki :3001): read `LANGFUSE_HOST`/`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`
  from `/home/julio/projects/clean_diallux_SDR/engine/.env` (env names only — never print values).
  Trace ids: working `fe687befd6027609c62d11ff15b1ba7b`; 08:12 `c2f292881ac5a37b5f88db4dc7cb4e24`;
  08:46 `70983c3dbb1d020aea195c1700548d31`. OR copies: `/tmp/opencode/trace_working.json`,
  `/tmp/opencode/trace_0846.json`.
- Lane log (broken sessions): OREGON `/tmp/opencode/voice_server_8025.log`. Working-call journal:
  `journalctl --user -u diallux-8024` (Helsinki).
- OR .env baseline backups: `/tmp/opencode/wt-iter78/engine/.env.bak_iter78c` (compare ONLY).

## Architecture (block diagram — the seams under analysis)
```
browser/Twilio audio → WS /mic/ws → session.py
   ├─ deepgram flux STT socket (eager-EOT speculate/adopt, EOT final, 2.5s backstop)
   ├─ barge-in handler (TTS cancel + <SEAM: what happens to in-flight STT?>
   ├─ pause_reask 10s one-shot timer (iter70 T2) <SEAM — CONFIRMED loop root>
   ├─ graph round (gpt-5.x, state machine, entry_lite post-history delta)
   ├─ speech filters at flush (sanitize | exact | jaccard-similar | clamp | yield-on-?) <SEAMS>
   └─ media/delivery.py per-state profiles → TTS stream (EL turbo_v2_5 / Cartesia sonic-3.6)
analysis: mechanism per seam → KEEP/DELETE/REDESIGN → next code-iteration shopping list
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/04_fix_mechanisms.md` | the analysis deliverable: per-fix mechanism + verdict table + port/deletion list | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/05_diff_notes.md` | per-hunk notes for every diff hunk in the fix line (T1 raw notes) | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-74/77 updated with analysis verdicts at close | Edit (docs → main) |
| code | **NONE** — analysis only | — |

## Deploy Rules
- Nothing deploys. No lane restarts, no env edits, no `.env` touches on either box.
- Read-only git commands everywhere; OR access strictly `ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<read cmd>'`.
- NEVER touch: OR prod `diallux.service` :8026 / `diallux-mic.service` :8090, OR :8001-8003,
  `/opt/diallux-production/`, Helsinki live lanes (:8020-:8024, :8000/:8005-:8008), Langfuse stack,
  `/home/julio/projects/diallux_sdr_almost_there_b` contents (snapshot is read-only reference).
- Docs commits go straight to main (LAW 0): from `/home/julio/projects/clean_diallux_SDR`, run
  `/home/julio/projects/clean_diallux_SDR/scripts/keyhound` on the diff, then `git push origin main`.

## Tasks (in order)

### T1 — Mechanism extraction from the fix line (diff reading)
Goal: for each fix-commit, extract THE MECHANISM (not the intent) with file:line citations at its
Tip commit, and note what it assumed about the audio plane.
Commands (full; run from `/home/julio/projects/clean_diallux_SDR`):
```
git show 65f3567 --stat
git show 65f3567 -- engine/diallux/config.py engine/diallux/media/session.py engine/diallux/graph/builder.py
git show 94f5164 --stat
git show 02b4bef --stat
git show 87a0ce5 --stat
git show 9c486b8 5dac0d4 3f8a79a 634159c 5ffcc67 --stat
git show d4fe473 -- engine/diallux/media/session.py engine/diallux/config.py | head -400
git show 05be69e --stat
```
Files: record per mechanism in
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/05_diff_notes.md`:
- pause_reask: where armed, what cancels it, what happens at fire (session.py:739±30 area @`d8260c2`)
- transition beat (one-trip, turn_asked gate)
- jaccard dedupe (tts_dedupe_similar/_overlap/_min_words) at BOTH flush sites
- yack clamp + never-mute REVIVE + cancel-reconcile note + zombie watchdog (iter74: NOT in iter78!)
- yield-on-? cut + said-truth `last_spoken` rewrite
- state-prompt directive removals (05be69e) + entry_lite delta directive
Verification: every mechanism has ≥1 file:line cite + 1 line on "why this cannot fix F1/F2/F3/F4/F6".

### T2 — Cross-check against the proven break (per-fix verdict)
Goal: for each fix, answer: did it CAUSE the Sep 25 failure, MASK a real bug, or MISS the seam
(needed bug never fixed)? Use `03_autopsy.md` chains as ground truth.
Deliverable table in
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/04_fix_mechanisms.md`:
`fix | mechanism one-liner | audio-plane assumption | real failure at Sep 25 | verdict KEEP/DELETE/REDESIGN`.
Known anchors: pause_reask=DELETE-or-REDESIGN (PT-74); yield=REDESIGN-or-DELETE (PT-77); clamp/REVIVE
= evaluate vs F6 mid-sentence cuts; cancel-reconcile = candidate to RESURRECT from iter74 (it is the
only existing mechanism aimed at the barge-in heard-truth problem); keepalive (iter75) = KEEP.
Verification: table complete, 0 unknowns; each verdict cites log/trace ids.

### T3 — Platform-mechanism mapping (if research results are in)
Goal: map the Vapi/Retell/LiveKit dossier onto our seams; decide what a minimal turn-manager port
replaces (deletes pause_reask? replaces barge-in dump? EOT adopt rules?).
Output: the "PORT LIST" section of `04_fix_mechanisms.md` — one variable per mechanism,
smallest-change-first. If research not yet available, record `UNKNOWN — blocked on research` and
skip.
Verification: each candidate names the knob, the code site it replaces, and the expected diff size.

### T4 — The restore-experiment spec (written spec, NOT executed)
Goal: define the owner-gated next code iteration so it is ONE variable: expected shape =
"iter79-ish on the owner's say-so — removes pause_reask arming on question-ending turns and
replaces the barge-in STT dump with finalize-or-reconcile", with exact env parity list
(`DEEPGRAM_EAGER_EOT_THRESHOLD=0.6`, EL 1.0/0.7/1.0, eager=ON) and the 8-probe ear-test script.
Stop at spec; execution = owner GO + a new code iteration (then, and only then, +1 number).
Verification: spec contains exact commands (lane restart, pytest gate, caller smoke) and pytest
file names for pins.

### T5 — Persist + closeout
1. Append analysis section to
   `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` (PT-74/77 verdict columns +
   delete-list); commit docs → main, push.
2. Write one-paragraph session verdict into
   `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md`.
Verification: `git log --oneline -1 main` shows the docs commit; PENDING_TASKS table updated.

## Validation Plan (end-to-end)
1. `05_diff_notes.md` covers every fix commit T1 listed, with file:line.
2. `04_fix_mechanisms.md` has a verdict for all six seams + the PORT LIST (+ T3 if research ready).
3. Zero code files changed (`git status --short` in both checkouts shows only the two reports).
4. PENDING_TASKS + report updated and pushed; owner gets the verdict summary in chat.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Executing the fix spec / any lane restart / env edits | owner-gated; needs its own code iteration |
| GK battery + room-tone driver fix | blocked until human path clean (iter78c gates stand) |
| iter74 revival as a branch merge | separate LAW 0 decision; T2 only grades its value |
| Repo-h fixes (OR prod tree branch, orphan plans commits) | PT-76, owner decisions |
