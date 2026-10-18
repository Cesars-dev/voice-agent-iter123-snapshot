# plan_v5_iter87_prewarm_owner_design — the owner's OWN prewarm redesign (session handoff)

## Meta
- Date: 2026-09-29 (written at iter86 close).
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Scope: ONE session. T0 captures the owner's NEW prewarm design VERBATIM (my iter86
  warm-sync proposal was REJECTED — see Compaction Context). Then the tasks are cut from
  THAT design: design doc → engine branch `engine/iter87-<slug>` → tests → lane battery
  → ledger rows → report → HITL.
- Status: BLOCKED at T0 (owner must dictate the design; nothing may be built before).

## Compaction Context (iter86 session close 2026-09-29 — carried verbatim)

**State of the engine ladder:**
- FIX 1 (eager hold, iter85 branch `engine/iter85-eager-hold` @ `542d3e8`, worktree
  /tmp/opencode/wt-iter85) EXECUTED + PASS: build b97957f + T3 DELETES 542d3e8 both pushed;
  UNMERGED (LAW 0 — branch law, owner merge pending). Round-B lint knobs are the PASS base:
  eager 0.35 / eot 0.65 / timeout 3000 CONFIDENCE gates, EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true,
  POST_INTERRUPT_BACKOFF_MS=500, PAUSE_REASK_MS=8000 (declared env-only deviation, driver
  frozen), PAUSE_LADDER_MODE=reminder, MAX=1; booking gate PASS (REAL booking created →
  CANCELLED 200; cal cancel POST REQUIRES cancellationReason body; Cal event 3801235 REAL).
- Battery calls + BOTH live calls are REGISTERED in the SQLite ledger:
  /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db → table
  `forensics_calls` (12 rows seeded 2026-09-29: 9 harness calls across commits fix7/fix5/fix1
  with per-call e2e/uperm/eager/cache0 columns + 2 REAL live-mic calls prod_mic_sep24_1514 /
  prod_mic_sep24_1336 + 1 unusable greeting-only trace). Read it with the venv python
  (/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python + sqlite3; NO sqlite3 CLI).
  New analyzed calls MUST be appended as rows (id convention: call_kind = llm_mic_harness |
  live_mic, stable call_name, date).
- The forensics SDK EXISTS and is COMMITTED: /tmp/opencode/wt-iter86/engine/scripts/call_forensics.py
  (branch engine/iter86-warm-sync @ d158b4c, pushed to origin). Modes: --trace <id-prefix>
  [--journal <journalctl.txt>] (per-turn matrix: real round TTFT, cache-0 colds, user-perceived
  = S2L−HS+L2T+T2A, eager/wait/cold counters), --compare <A> <B> (fidelity), --run <ledger
  run_id>, --costs. Engine root for it: /tmp/opencode/wt-iter86 (it reads
  /home/julio/projects/clean_diallux_SDR/engine/.env no other deps — stlib-only). Reports:
  /home/julio/projects/clean_diallux_SDR/research/surgeon/iter86-warm-sync/ (01..04 + 00 SDK outputs).
  The pack is ALSO public at github.com/Cesars-dev/diallux-voice-engine-iter86
  (main = 1-commit snapshot f078fa4 + 8e3eafc outside_fixes pack).

**Forensics VERDICTS (proven, DO NOT re-litigate):**
- K1: ENGINE transitions (phaseb chain, builder _deterministic_node) NEVER fire the prewarm:
  0 warm:Closing spans; await no_task Closing ×7 in the PRE-fix1 baseline TOO (K1 predates
  fix1). K2: tool-detect warm can lose the destination round by ~0-200ms (t30 knife-edge:
  warm landed 09.136, request left 09.136-09.208, paid cache_read=0). K3: await_warm found an
  in-flight warm ZERO times in 57 spans (47 already_done + 10 no_task) — awaiting alone cannot
  fix anything; scheduling does.
- E2E was NOT degraded by fix1: best happy E2E in the ladder = the LAST commit (p50 1120 /
  p90 1395, uperm p50 867); barge p90 3076 beats both pre-fix1 baselines (3320/3661).
  2-4s transition tails + 2-4 round/turn multi-round turns EXIST IN THE BASELINE (12 multi-round
  turns pre-fix1). The fake caller is 3x faster-paced than a real caller (6.03 vs 1.97 turns/min,
  gap p50 8.3s vs 17.2s); agent-side user-perceived p50 is IDENTICAL (~1.2s) in both worlds.

**OWNER DECISION at iter86 close (2026-09-29): the iter86 warm-sync fix proposal (T1.1 chain-path
warm + T1.2 WARM_AWAIT_MS bounded-await gate + T1.3 one-ahead map + T1.4 ttft-on-tool-rounds)
is REJECTED / DEPRECATED — the workflow was suboptimal; the owner has his OWN optimized prewarm
design that supersedes it. The eager-async release-by-ID design is ALSO parked with it.**
- plan_v5_iter86_warm_sync_call_fidelity.md is marked DEPRECATED in its header; SDK + evidence
  + forensics_skills_calls表 rows remain valid and usable.
- Ops done at close: OpenAI key ROTATED (new key in ALL .env files on both boxes; old key
  /home/julio+OREGON sk-proj-H7rXY… revoked-by-owner pending, 43 files updated, backups deleted);
  master plan STATUS updated; this plan written per the PLAN SOP.

**Other open owner items (unchanged):** FIX 1 ear A/B + eager-0.35 keep-vs-revert (owner
schedules); PAUSE_REASK_MS 8000=lane-default verdict; FIX 8 soft filler redundancy check;
cal_live key rotation bundle (4 keys × ~140 refs across retell configs — bundle with next
retell config deploy, NOT urgent: private repo exposure only); dialux_sdr_almost_there repo
returns 404 via API (moved private or deleted — uninvestigated).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| iter86 warm-sync PROPOSAL = DEPRECATED, do NOT build or re-propose it | owner verdict 2026-09-29: suboptimal; his own design replaces it |
| New session = ONE variable again, cut from the owner's dictation at T0 | LAW 0 iteration discipline; the owner has been burned by bundled work before |
| Forensics calls live in ledger.db `forensics_calls` (12 rows seeded) | owner-ordered persistent record; every future analyzed call appends a row |
| SDK = engine/scripts/call_forensics.py on branch engine/iter86-warm-sync @ d158b4c (pushed) | owner-ordered instrument; use it, extend it, don't rebuild it |
| FIX 1 knobs = the PASS base for every lane | 0.35/0.65/3000 + hold ON + backoff 500 + PAUSE_REASK 8000 |
| Docs (md) straight to main; CODE waits for owner merge | LAW 0 |
| Two-box law: session on Finland, repo ops ssh-wrapped to OREGON (or bare if hostname=ubuntu-4gb-hil-1) | iter81 Meta |
| Never touch: Finland repo tree (stale mirror), prod :8026/:8000-8003/:8090, diallux.service | deploy rules |
| Cancel every test booking (event 3801235 REAL) | paid lesson |
| totalTimeStamps in plan paths = FULL ABSOLUTE PATHS | SOP hard rule |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| **Owner's new prewarm design (THE blocker)** — dictate it at T0: exact trigger moments, target states, knobs, expected behavior on the transition fork | owner speech or MD/e messages captured verbatim into T0 art in this plan file or a fresh design doc |
| FIX 1 ear A/B + eager-0.35 keep-vs-revert | owner schedules |
| PAUSE_REASK_MS 8000 as lane default verdict | owner after next battery |
| FIX 8 soft filler + redundancy check order | owner (wave-2 call) |
| cal key rotation bundle | owner (next retell config deploy) |
| OREGON boots every session from scratch (wt list persists; no lane alive now) | mechanical |

## Environment & Dependencies
- OREGON venv (shared): /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python
  (never <venv>/bin/pip — copy-mirror trap; use <venv>/bin/python -m pip).
- Worktrees live under /tmp/opencode/wt-iterNN (persist across sessions). Current stack:
  wt-iter85 = FIX-1 PASS tip 542d3e8 (basis for next engine branch); wt-iter86 = SDK + docs
  (branch engine/iter86-warm-sync @ d158b4c, pushed).
- New branch law: cut engine/iter87-<slug> FROM /tmp/opencode/wt-iter85 tip 542d3e8:
  git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter87
  -b engine/iter87-<slug> 542d3e8  && cp /tmp/opencode/wt-iter85/engine/.env
  /tmp/opencode/wt-iter87/engine/.env (ENV LAW).
- OREGON .env = /home/julio/projects/clean_diallux_SDR/engine/.env (has the NEW rotated
  OpenAI key sk-proj-U7zPicu… — never print it).
- Lane ports: FRESH (8047/8048 suggested; never prod :8026/:8000-8003/:8090). Boot style:
  /tmp/opencode/boot_lane_t4_fix1.sh PORT pattern → systemd-run --user --collect; verify
  journalctl "connected" shows elevenlabs Sarah; killed + ss -ltnp port-verified at close.
- Driver: FROZEN at wt-iter82 (llm_mic_caller.py / llm_mic_caller_b52.py). New battery
  jsons → /tmp/opencode/*.json; journals per lane unit.
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (venv python + sqlite3 only; forensics_calls table EXISTS — append rows, don't re-seed).
- MODEL LAW: agent gpt-5.4 everywhere. VOICE LAW: tests = EL Sarah. Push law:
  git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'
  push (file-lock warning is benign). keyhound before any push.
- OpenAI key = NEW (sk-proj-U7zPicuIRmtPejiaX…, present in both boxes' engine .env files) —
  the OLD key (sk-proj-H7rXY…) is REVOKED-by-owner once he clicks; any env referencing it is
  stale by definition.

## Architecture (one block)
```
YOUR DESIGN (T0) → design decision (T1)
  → engine branch engine/iter87-<slug> from iter85 tip (T2 build + tests)
  → lane battery: happy + barge scenario, round-B knobs + YOUR knobs (T3)
  → SDK matrices → forensics_calls ledger rows (T3)
  → report → HITL: owner ear + merge call (T4)
```

## File Map
| File (absolute path, OREGON) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | THE ladder (STATUS = resume point) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter87_prewarm_owner_design.md | THIS plan | itself |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter86_warm_sync_call_fidelity.md | DEPRECATED proposal (evidence-referenced only) | read-only |
| /tmp/opencode/wt-iter85 (branch engine/iter85-eager-hold) | base tip for the new engine branch | read only |
| /tmp/opencode/wt-iter86 (branch engine/iter86-warm-sync) | SDK + deprecating docs | SDK use |
| /tmp/opencode/wt-iter87 (branch engine/iter87-<slug>, cut at T1) | the build | build here |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db | ledger; forensics_calls table seeded (12 rows) | append |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-<slug>/ | battery + SDK outputs + reports (01_*.md naming) | append |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter85*.md / _t4_wave1 | prior wave plans | reference |

## Deploy Rules
- NEVER touch the OREGON prod checkout (df23d37) / diallux.service / :8026/:8000-8003/:8090.
- Lanes: fresh ports, systemd-run --user --collect, killed at close + `ss -ltnp` verified.
- ENV LAW: before ANY run on a new worktree, copy wt-iter85 engine/.env (it carries the new key).
- Cancel every test booking (Cal event 3801235 REAL; cancel POST needs cancellationReason).
- Doc commits: docs worktree off origin/main, commit, push origin HEAD:main, then re-sync
  FINLAND mirror (scp committed files back), remove docs worktree.

## Tasks (in order)
### T0 — HITL: capture the owner's new prewarm design (15 min, NO tooling)
1. Ask the owner to dictate the design IN FULL and paste it VERBATIM into
   `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter86-warm-sync/07_owner_design_capture.md`
   (create the file; timestamp + source line). It must answer:
   (a) WHERE the prewarm is scheduled (which state transitions / events);
   (b) WHAT it warms (payload shape + the dvs state at fire time);
   (c) HOW the destination round syncs with it (the deterministic moment);
   (d) any eager-EOT interaction (is the eager flow part of the design?);
   (e) knobs + defaults.
2. Sanity-read it back to the owner in ONE paragraph — wrong guesses = start over.
Verification: capture file exists with ALL of (a)-(e); owner confirms wording.
Unblocks: T1.
### T1 — design synthesis + branch cut (30 min)
1. Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-<slug>/00_design.md`
   mapping the owner design onto the code surface (fire-sites, awaits, caches, knobs) — NO
   code yet. Verify every hook exists at the named files/lines (grep anchors, builder.py /
   session.py as of wt-iter85 542d3e8).
2. Cut /tmp/opencode/wt-iter87 from 542d3e8 (commands in Environment). Copy .env.
Verification: worktree exists; .env has OPENAI_API_KEY (new key prefix present).
Unblocks: T2.
### T2 — build + unit tests (60 min, exact scope = T1 mapping)
1. Implement per 00_design.md. Unit tests per test convention (fake clock / fake gate /
   fake stream, pattern from wt-iter85 tests/test_iter85_eager_hold.py).
2. pytest engine/tests -q: zero NEW reds (7 stale reds acceptable: test_delivery ×4,
   iter46 fast-first-flush, iter59, iter60 — never re-derived).
3. Anyone new env knob: config.py field default = OFF (knob law), lane-export value in the
   boot script.
Verification: pytest green + keyhound clean + commit + push.
Unblocks: T3.
### T3 — battery + ledger registration (60 min)
1. Boot lane (round-B knobs + T1 knobs). Happy + barge scenario (fresh ports; FROZEN driver).
2. Gates (§11.1 as in iter85 battery): turn-1 e2e <1000ms, eager_final_match 100%, zero
   held-path cancels, booking created → cancelled 200, cache0 COUNT from the SDK matrix.
3. Run the SDK (--trace on both traces; --journal optional), save outputs to
   /home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-<slug>/ .
4. APPEND forensics_calls rows for both new calls (call_kind llm_mic_harness; date; the
   current commit sha; uperm/e2e/eager/cache0 columns per public schema).
Verification: gates + SDK outputs in place + ledger rows queryable.
Unblocks: T4.
### T4 — report + HITL (30 min)
1. Write /home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-<slug>/01_*.md with
   the verdict per the owner's design intent, gaps, next options.
2. Update plan_v5_iter81_master_ladder.md STATUS (session close ritual: report folder,
   branch state, next step, ledger rows added), commit docs to main, re-sync Finland mirror.
Verification: STATUS block updated; docs pushed; mirror re-synced.

## Validation Plan (end-to-end)
T0 capture → design mapping 00_design.md → unit tests green → battery gates PASS →
forensics_calls rows present → STATUS update. Abort/rollback: any knob added defaults OFF;
the battery runs from round-B base so a bad toggle = lane re-boot unchanged.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| FIX 1 merge / ship | owner merge call; battery knobs proven but branch UNMERGED |
| cal_live key rotation bundle | next retell config deploy (owner) |
| FIX 8 + ack filter wave 2 | wave-2 order AFTER this session (owner) |
| AXON / barge harness fidelity tweak | evidence parked in 03_call_fidelity; separate owner call |
| 2-trip transition redesign as a whole | owner will decide after the ear A/B + his prewarm design lands |
