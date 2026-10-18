# plan_v5_iter83_t4_wave1_engine_fixes — T4 wave 1: FIX 7 / FIX 5 / FIX 8, per-fix loop through the FROZEN fake caller

## Meta
- Date: 2026-09-28. Continues `plans/plan_v5_iter81_master_ladder.md` (THE master plan — read it FIRST, it owns
  the code analysis, seam verification and pins; this plan carries CONTEXT ONLY and the execution loop).
- WORKING MODE (two-box law): session on FINLAND. ALL repo ops via
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<command>"`.
  OREGON hostname = ubuntu-4gb-hil-1. OREGON repo can now PUSH to GitHub (gh-creds rsynced 2026-09-28).
- Project root: /home/julio/projects/clean_diallux_SDR (OREGON checkout = source of truth).
- Scope: wave 1 of the turn-taking fix ladder (owner MD ship order §10.1): FIX 7 STT liveness → FIX 5
  post-interrupt backoff → FIX 8 soft filler. Each fix = one branch + unit tests + ONE battery through the
  FROZEN instrument + §11.1 pass gates + owner ear A/B + HITL. NOTHING here re-analyzes code — analysis is
  DONE and lives in the sources below.
- Status: EXECUTING — FIX 7 battery DONE 2026-09-28 (Scenarios A+B PASS, report
  `research/surgeon/iter83-t4-wave1/01_fix7_battery.md`, ledger runs fix7-sanity-ref/fix7-a2/fix7-b1/fix7-b2 @ fa62162).
  **FIX 5 battery DONE 2026-09-28** (report `02_fix5_battery.md`, branch `engine/iter84-post-interrupt-backoff`
  @ `0693a9d` pushed, 14/14 targeted green, suite debt unchanged; §11.1 owner-500ms gate PASS on all 5 barge
  events — the window never binds live (zero fires, zero cost), owner pin: KEEP 500; ledger runs fix5-b /
  fix5-happy / fix5-bargeloop @ 0693a9d; booking biZAhvfspYogdbBffGefna cancelled 200; driver variant
  `llm_mic_caller_b52.py` (barge-loop scenario, --max-caller-turns 52) committed on `engine/iter82-pause-nudge`
  @ `aaba8ff`; owner-ordered AGENTS.md VOICE LAW corrected on main @ `4159f30` — ElevenLabs DEFAULT (prod
  Hannah, tests Sarah), Cartesia = HIPAA/low-quality only).
  NEXT: FIX 1 (eager hold) — owner pulled it forward past FIX 8 (2026-09-28). OWNER LATENCY VERDICT 2026-09-28 (T4 scorecard): e2e p50 ~1.2s LLM-bound is acceptable-but-not-best;
  the ~300ms eager overlap is UNBANKED (head_start ~40ms @0.70) — FIX 1 eager hold,
  `EAGER_HOLD_AUDIO_UNTIL_CONFIRM`, threshold 0.65 experiment = the lever (turn-1 e2e ~1064 -> ~760-860, p50 -> ~0.9s).
  **FIX 1 EXECUTED 2026-09-29 — PASS** (branch `engine/iter85-eager-hold` @ `542d3e8` pushed; §11.1 all-PASS:
  turn-1 e2e 963.5 <1000 FIRST TIME, head_start p50 280ms BANKED, eager_final_match 100%, 10 silent discards /
  0 cancels / 0 collisions, REAL booking created + cancelled 200; grace-window DELETES committed separate
  `542d3e8`; reports 03/04/05 in `research/surgeon/iter83-t4-wave1/`; params: eager 0.35 / eot 0.65 /
  timeout 3000 + hold ON). Wave-1 remaining: FIX 8 (soft filler) — owner call on order. Post-FIX-1 findings
  routed to `plans/plan_v5_iter86_warm_sync_call_fidelity.md`: warm-race losses on short transitions
  (destination rounds cache_read=0 x3 + no warm:Closing), transition 2-trip E2E structure, harness pacing
  fidelity, eager-threshold round churn (1.4x).

## Compaction Context (2026-09-28 booking-gate session — carried verbatim)

**Milestone reached:** T3 PASSED. Fake caller (v14, sid 71ca29961a6c, trace `17ed3274dafd`) completed the full
arc Intake→Discovery→Offer→contact_details→ConfirmSlots→Booking→Closing; `create_livecall_booking`
`{"status":"booked","booking_uid":"88jbmgqNZsQQcWQ9AqYiS1","booked_human":"tomorrow at 3"}` @ 10:24:46 UTC;
CANCELLED 200 (cal id 25984606). Zero wedged turns; chunk flow continuous. **Driver FROZEN** — reports:
`research/surgeon/iter81-fake-caller-human-parity/07_booking_root_cause.md` + `08_booking_gate_run.md` (both on OREGON).

**Three booking-gate root causes, all fixed same day (do not re-litigate):**
1. False `booked_goodbye`: loose hint matched "booked jobs" → strong-phrase + last-turn detector (commit `d70c438`).
2. Empty `dvs.callback_number` on mic transport → driver now injects `customParameters.callback_number`
   (default +15123120001) at start — same path as mic page + chat lane (`set_callback_number` verified live).
3. Caller drift (v13 consumer-drift hang-up) → owner pinned CALLER = `gpt-4.1-mini` (run-script flag).

**Branch state:** `engine/iter82-pause-nudge` @ `d70c438` (pushed to origin; OREGON worktree `/tmp/opencode/wt-iter82`
+ Finland push worktree `/tmp/opencode/wt-iter82-push` both at tip; GitHub = OREGON = Finland in lock-step).
UNCOMMITTED in wt-iter82 (pre-existing iter82 ladder work, owner decision pending):
`engine/diallux/config.py`, `engine/diallux/media/session.py`, `engine/tests/test_tts_providers.py` (M) +
untracked `engine/tests/test_iter82_pause_ladder.py` (5/5 PASS per iter82 session).

**FROZEN instrument (T4 batteries run through THIS, untouched):**
- Lane: `/tmp/opencode/boot_lane_t4.sh <port>` (iter82 engine, PAUSE_LADDER knobs ON, 127.0.0.1, fresh port
  per run, `systemd-run --unit=<name> --collect`, never prod :8026/:8000-8003).
- Driver: `/tmp/opencode/run_driver_t4.sh` — `--scenario happy --persona Danny --caller-model gpt-4.1-mini
  --agent-idle-s 5.5 --max-turn-wait 60 --min-gap 2.5 --max-gap 6 --max-caller-turns 30
  --callback-number +15123120001 --out /tmp/opencode/t4_fake_v8.json` (edit PORT when lane port changes).
- Evidence: driver json + Langfuse `http://46.62.233.228:3001` traces `micbridge-<sid>`
  (`scripts/lf.py gens|tools <trace-id>` from `/tmp/opencode/wt-iter82/engine` with worktree .env), lane journal
  via journalctl. Tool lines do NOT print in uvicorn logs.

**Where the code analysis LIVES (read-only sources for T4 — DO NOT re-derive):**
- THE master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md` — T4 table
  (fix → knob → §11.1 pass signal), seam verification verdict, branch law, cost pins.
- THE fix ladder source (2 owner MDs): `/home/julio/projects/vps-inbox/voice-sdr-turn-taking-fixes.md`
  (F1-F6 graph; knob registry §1; FIX 1-8 patches WITH CODE + TESTS + rollout; ship order §10.1 wave1 =
  FIX 7/5/8; pass signals §11.1; abort flags §10.3) + `voice-sdr-turn-taking-research.md` (dossiers D1-D11).
  Copies on OREGON: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter80-el-flip-mic-phone-fix-src/`
  (verify path at execution) and `tasks/surgeon/iter80-el-flip-mic-phone-fix/`.
- Seam verdict (2026-09-27, in master plan Compaction): `media/session.py`, `media/sentence_gate.py`,
  `media/deepgram_stt.py` md5-identical to the MD patch snapshot ⇒ patches apply AS-WRITTEN;
  `config.py` DIVERGED (88381a2 EL knobs) ⇒ knob-registry patch needs an ADAPTATION DIFF.
- The knobs (all default OFF, env-settable): `STT_RX_ZOMBIE_MS=15000` (FIX 7), `POST_INTERRUPT_BACKOFF_MS=1000`
  (FIX 5), `SOFT_FILLER_MS=3000` (FIX 8).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Driver FROZEN at `d70c438` + run script as-is; any touch = master-plan ledger note | master plan T3 law; deltas must measure ENGINE fixes only |
| One branch per fix, cut from `engine/iter82-pause-nudge` tip `d70c438`; iterNN assigned at cut (MD branch names are placeholders) | owner option 2 branch law; LAW 0 |
| Knobs default OFF in `config.py`; lane env turns them ON per battery | master plan; iter82 ladder precedent |
| Battery = ONE per fix through the frozen driver + §11.1 pass + owner ear A/B, then next | owner: "we test the desired outcome on every fix then we move to the next" |
| `media/*` patches as-written; `config.py` via adaptation diff | seam verification (master plan) |
| Caller = gpt-4.1-mini; agent = gpt-5.4 everywhere (MODEL LAW) | owner 2026-09-28; MODEL LAW |
| Cancel every test booking (event 3801235 REAL) | paid lesson |
| Docs (md/plans) straight to main; engine code waits for owner merge | LAW 0 |

## BLOCKED / NEEDS INPUT
| Item | Where |
|---|---|
| Owner GO to start T4 wave 1 | this plan |
| Decision: commit the UNCOMMITTED iter82 ladder files to `engine/iter82-pause-nudge` (recommended: yes, they are the 5/5-test ladder) or park them — BEFORE cutting FIX 7 (touches session.py/deepgram_stt.py) | owner |
| Owner availability for ear A/B after each fix battery | owner schedules |

## Environment & Dependencies
- OREGON venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (pip: `<venv>/bin/python -m pip` ONLY).
- New worktrees per fix: `/tmp/opencode/wt-iterNN` (`git worktree add` from `/home/julio/projects/clean_diallux_SDR`).
- Suite: `cd <worktree>/engine && .venv python -m pytest tests -q` (pin current expected count from ITERATIONS.md first).
- Langfuse + ledger SOPs: `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/full_call_analysys.md`,
  ledger `research/surgeon/iter48-rag-truth/ledger.db` (import every battery run; NO sqlite3 CLI — venv python).
- Langfuse server http://46.62.233.228:3001 (keys in worktree `.env`).

## Architecture
```
FROZEN driver (gpt-4.1-mini + callback injection) --> voice lane (flux STT -> gpt-5.4 graph -> EL TTS)
T4 wave1: FIX 7 zombie-STT reconnect | FIX 5 post-interrupt backoff | FIX 8 soft filler   (knobs OFF by default)
```

## File Map
| File (absolute path, OREGON) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | ladder + STATUS (updated at every session close) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter83_t4_wave1_engine_fixes.md | THIS plan | itself |
| /home/julio/projects/vps-inbox/voice-sdr-turn-taking-fixes.md (+ OREGON copies in research/surgeon/iter80-el-flip-mic-phone-fix-src/) | THE patches (code lives HERE) | READ-ONLY |
| /home/julio/projects/clean_diallux_SDR/engine/diallux/media/deepgram_stt.py, media/session.py | FIX 7 / FIX 5 / FIX 8 patch targets | per-fix branch |
| /home/julio/projects/clean_diallux_SDR/engine/diallux/config.py | knob registry — ADAPTATION DIFF needed | per-fix branch |
| /tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py | FROZEN driver | NEVER |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/ | battery + autopsy evidence | append |

## Deploy Rules
- NEVER checkout/switch/reset/pull the OREGON prod checkout; worktrees only.
- NEVER touch diallux.service / :8026 / :8000-8003. Lanes fresh port + systemd-run --collect + killed at session end.
- NEVER inline `&` in ssh; pkill bracket patterns only.
- OREGON can push: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push ...` (absolute path — the relative one breaks in worktrees).
- Cancel every test booking; Cal.com event 3801235 REAL.

## Tasks (in order)

### T0 — pre-flight (30 min, no fixes)
1. Owner decision on the uncommitted iter82 ladder files (BLOCKED table). If GO: commit on `engine/iter82-pause-nudge`
   (`iter82: pause-ladder knobs + session wiring, 5/5 unit tests`), push.
2. Re-pin the seam: md5 `media/session.py`, `media/sentence_gate.py`, `media/deepgram_stt.py` in the d70c438 tree
   vs the MD snapshot — if still identical, FIX 7/5/8 media patches apply as-written; if not, diff and note.
3. Pin exact patch blocks: fixes MD §1 knob registry + FIX 7/5/8 sections + §11.1 pass signals — quote file+line
   anchors into the surgeon folder `iter83-t4-wave1/00_seam_pin.md`.
Verification: anchors exist in the base tree; blocker list empty. Unblocks: T1.

### T1 — FIX 7 STT liveness (`STT_RX_ZOMBIE_MS=15000`, kills F2 zombie mute)
1. Branch `engine/iter83-stt-liveness` from `d70c438` + worktree `/tmp/opencode/wt-iter83a`.
2. Apply the FIX 7 patch from the fixes MD (media/deepgram_stt.py as-written; config.py knob via adaptation diff).
3. `<venv> -m pytest tests -q -k stt` green; full suite count unchanged vs ITERATIONS.md.
4. Battery: fresh lane port (boot_lane_t4.sh), FROZEN driver unchanged; engineer a dead STT socket scenario per
   fixes MD test; verify reconnect ≤15s, call continues, 0 spurious reconnects; cancel any booking; ledger import.
5. Langfuse span check + owner ear A/B knob on/off → HITL. Report `iter83-t4-wave1/01_fix7_report.md`.
Unblocks: T2.

### T2 — FIX 5 post-interrupt backoff (`POST_INTERRUPT_BACKOFF_MS=500` — owner-specified 2026-09-28, NOT the MD's 1000ms)
Same loop from d70c438 (worktree wt-iter83b): patch → tests → battery: post-barge replies start after caller
finishes, never overlap (§11.1). Report `02_fix5_report.md`. Unblocks: T3.

### T3 — FIX 8 soft filler (`SOFT_FILLER_MS=3000`; OWNER NOTE: agent already has filler words in its prompt — battery must CHECK FOR REDUNDANCY i.e. knob-filler + prompt-filler double-fire; full redundancy verdict deferred to owner ear A/B, "check for redundancy, but later")
Same loop (wt-iter83c): one filler ~3s into tool-wait, once per turn, then the real answer. Report
`03_fix8_report.md`. Unblocks: T5 wave 2 (owner GO).

## Validation Plan (end-to-end)
Per fix: unit green → ONE battery (frozen driver, fresh port) → §11.1 signals + ledger import → owner ear A/B →
HITL commit/merge decision. Abort flags §10.3 of the fixes MD govern any rollback. Master plan STATUS updated at
every session close.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| T5 wave 2 (FIX 1 eager hold / FIX 4 ack filter), T6 wave 3 (FIX 6/3/2) | master ladder order; wave 1 first |
| FIX 3 confidence observation rider | read-only, any time in T4 when owner asks |
| Driver cap 30→36 cosmetic + crash-safe json-on-close | FROZEN instrument — ledger note only, owner decides |
| Live 15s pause-ladder nudge ear test | owner listening session, anytime |
