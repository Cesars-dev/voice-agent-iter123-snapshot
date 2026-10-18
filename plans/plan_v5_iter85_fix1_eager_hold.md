# plan_v5_iter85_fix1_eager_hold — FIX 1 eager-think/confirmed-speak (owner's big latency lever): one branch, unit tests, ONE battery through the FROZEN driver

## Meta
- Date: 2026-09-28. Executes FIX 1 of `plans/plan_v5_iter83_t4_wave1_engine_fixes.md` (the big wave-1
  latency lever, PULLED FORWARD past FIX 8 by the owner 2026-09-28) under the workflow law of THE master
  plan `plans/plan_v5_iter81_master_ladder.md` — read its STATUS block FIRST (SESSION CLOSE 2026-09-28
  FIX 5 EXECUTED — PASS entry is the resume point).
- WORKING MODE (two-box law): the session runs on **FINLAND** (Helsinki, 46.62.233.228 — hostname
  `MainVps`). ALL repo ops are typed on Finland and executed on **OREGON** via
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<full command>"`
  (hostname `ubuntu-4gb-hil-1`). OREGON checkout = source of truth; the Finland tree
  `/home/julio/projects/clean_diallux_SDR` is a read-only plan mirror — NEVER edit repo files bare on
  Finland; temp scratch under `/tmp/opencode/` (Finland-local) only. Exception: if hostname is
  `ubuntu-4gb-hil-1`, you ARE on OREGON — run repo commands bare (no ssh wrapper). Anything else → STOP
  and ask the owner which box you are on.
- Project root: /home/julio/projects/clean_diallux_SDR (OREGON checkout).
- Scope: FIX 1 ONLY — build (SentenceGate hold/release/discard + session wiring + knob + 6 unit tests),
  ONE battery through the frozen driver, §11.1 pass gate, then (after battery PASS) the T3 DELETES
  commit (separate commit, per MD §2.5). NO other fix. FIX 8 stays queued after (owner call on order).
- CODE ANALYSIS: DONE AND AUDITED — the full FIX 1 design + patch + tests live in the fixes MD §2
  (quoted below). The next agent must NOT re-derive the design or re-audit FIX 1. The ONLY accepted code
  inspection is the mechanical T0 state check (sha, .env, test re-run) + the mechanical anchor check
  (grep the cited lines exist; line numbers may have drifted +~20 after iter84's session.py insert —
  match by code shape, not by line number). No DECLARED adaptations are known at plan time — if an
  anchor does not match, STOP and surface it to the owner before deviating (lesson from iter84).
- Status: EXECUTED 2026-09-29 — T0-T3 DONE. Branch engine/iter85-eager-hold @ 542d3e8 (build b97957f +
  T3 DELETES 542d3e8, both pushed). Battery: happy + barge-loop, TWO param rounds (owner corrected the
  mapping: eager_eot_threshold=0.35 CONFIDENCE, eot_threshold=0.65, eot_timeout_ms=3000 — round A's
  0.55/600 was trace-proven harmful: mid-utterance EOT fragmentation). §11.1 all-PASS: turn-1 e2e 963.5
  (<1000 FIRST TIME), head_start p50 280ms banked (was ~41), eager_final_match 30/30+31/31=100%, 10
  silent discards / 0 tts.cancel / 0 held-path clears, booking REAL (q3DWLDMQbZHs7hZngaxHZo, cal id
  25987397) CANCELLED 200. 6 unit tests 20/20; suite = same 7 stale reds. Reports
  research/surgeon/iter83-t4-wave1/{03_fix1_battery,04_fix1_call_audit_b3,05_b3_latency_forensics}.md;
  21 SOP rows in ledger @ fix1-bargeloop; ledger runs fix1-happy/fix1-bargeloop @ b97957f. Declared
  adaptations: _graceful_cap_close hold-clear; lane PAUSE_REASK_MS 15000->8000 (driver-timing artifact).
  PENDING HITL: owner ear A/B + eager-0.35 cost verdict (45 fires/32 turns = 1.4x rounds). NEXT:
  plans/plan_v5_iter86_warm_sync_call_fidelity.md (warm-race fix + harness fidelity + forensics SDK).

## Compaction Context (2026-09-28 FIX 5 battery session — carried verbatim)

**Wave-1 state:** FIX 5 (post-interrupt backoff) BUILT + BATTERY-PASSED on branch
`engine/iter84-post-interrupt-backoff` @ `0693a9d` (pushed), worktree `/tmp/opencode/wt-iter84` on
OREGON, cut from `engine/iter83-stt-liveness` tip `fa62162`. Knob `post_interrupt_backoff_ms` default 0;
stamped `_backoff_until` in `_on_start_of_turn` interrupted branch (declared adaptation); one-shot wait
in `_speak_chunk`. 4 unit tests, targeted 14/14 green, suite debt unchanged (same 7 stale reds as the
iter82 base: test_delivery x4, iter46, iter59, iter60). Battery §11.1 owner-500ms gate PASS on all 5
barge events — the window NEVER binds live (engine never re-speaks within 500ms of a barge; zero fires,
zero cost; llm→tts p50 204.7ms vs baselines 202.6/206.1). OWNER DECISION: keep 500ms, revisit after
FIX 1 (the eager-adopt path is where it can bind). Report
`research/surgeon/iter83-t4-wave1/02_fix5_battery.md`; ledger runs fix5-b/fix5-happy/fix5-bargeloop @
0693a9d; booking biZAhvfspYogdbBffGefna cancelled 200 (cal id 26001405); lanes 8043/8044 torn down.

**Owner decisions this session (2026-09-28):** (1) FIX 5 battery value stays 500ms; (2) OWNER-ORDERED
driver variant `llm_mic_caller_b52.py` (scenario `barge-loop`: greeting barge + 3 mid-turn barges + happy
arc; `--max-caller-turns 52`) committed on `engine/iter82-pause-nudge` @ `aaba8ff` — the FROZEN original
`llm_mic_caller.py` is untouched; (3) AGENTS.md VOICE LAW corrected on main @ `4159f30`: ElevenLabs is
DEFAULT (prod = Hannah `ZSNL4hPqCnqoMPaI4jGX` speed 1.0/stability 0.6/style 1.0 + py playback accel
1.08–1.15; tests keep Sarah `uG1JFy6xppqckhHCs2KG`); Cartesia ONLY for HIPAA/lower-quality deployments
(and tests); (4) FIX 1 pulled forward — THIS plan; FIX 8 stays queued after (owner call).

**T4 latency verdict (owner add, LATENCY-PERCENTILE-SOP):** e2e p50 ~1.2s is LLM-bound (gpt-5.4 TTFT
~770–790ms ≈ 65% of the turn); turn-1 e2e 1064–1157ms; the ~300ms eager overlap is UNBANKED
(head_start ~40ms @ EAGER threshold 0.70, eager_final_match 100%). FIX 1 eager hold + threshold 0.65
experiment = the lever (turn-1 e2e ~1064 → ~760–860, p50 → ~0.9s). Lane env today:
`DEEPGRAM_EAGER_EOT=true`, `DEEPGRAM_EAGER_EOT_THRESHOLD=0.7`.

**FIX 1 design (fixes MD §2, VERBATIM ANCHORS — do not re-derive):** "Eager-think, confirmed-speak."
Today `EagerEndOfTurn` starts a full turn INCLUDING TTS audio; `TurnResumed` then cancels speech in
flight (the grace-window machinery `eager_resume_grace_ms` / `_grace_then_cancel` exists solely to
manage that waste). The change: the `SentenceGate` gains a HOLD state — an eager turn's tokens still
stream from the LLM (all latency banking: prompt prewarm, RAG fire, first-token head start still
happens) but the gate stops flushing sentences to TTS. When the confirmed `EndOfTurn` adopts the
running turn, the gate RELEASES and audio flows. When `TurnResumed` fires, the turn is discarded
SILENTLY — no TTS cancel, no Twilio clear, because nothing was ever spoken.

```
EagerEndOfTurn ──> LLM round starts, gate.hold()          [think early]
EndOfTurn (adopt)──> gate.release() ──> TTS audio flows    [speak confirmed]
TurnResumed ──────> gate.discard(), task.cancel()          [silent teardown]
```

MD patch anchors (apply as-written; verify code-shape at T0, line numbers drifted after iter84):
- `media/sentence_gate.py`: `__init__` gains `_held = False` + `_held_final = False`; `add()` grows an
  early-out (`if self._held: return` after `_buffer += token`); `end_of_turn()` parks its final marker
  while held (`self._held_final = True; return`); three new primitives `hold()` / `release()` /
  `discard()` (full code in MD §2.2); `reset()` must clear `_held` + `_held_final` too.
- `media/session.py`: class attr `_eager_held: bool = False`; in `_run_turn` after the TTS context is
  minted (`self._tts_context = self.tts.new_context_id() if self.tts else None`) — set `_eager_held`
  from `clock.extra.get("eager")` + knob, and `self.gate.hold()`; in `_on_eot`'s existing adopt branch
  (after `self._update_fired = False`, before the `log.info("eot adopted running eager turn")`) —
  release the gate + `log.info("eager turn audio released at confirmed EOT")`; in `_on_turn_resumed` a
  NEW first branch BEFORE the grace-window logic — if held: silent discard (cancel task, `gate.discard()`,
  clear `extra["eager"]`/`resume_pending`, NO TTS cancel, NO clear) + `log.info("eager turn discarded
  silently (user resumed, audio was held)")`; existing grace path unchanged below it.
- Telemetry: `t_tts_req` / `tts_first_byte` anchor lazily at the release flush (NO code change needed —
  iter84's `_speak_chunk` first-request guard already stamps on the first post-release chunk).
  `head_start_ms` keeps measuring EOT − EagerEOT. `eager_final_match` stays logged.
- MD §2.5 DELETES — SEPARATE COMMIT, ONLY AFTER THE BATTERY PASSES: `_grace_then_cancel()`
  (whole method), the `eager_resume_grace_ms` knob + its branches in `_on_eot` / `_on_turn_resumed`,
  the iter38 F1 race-guard ordering dance (keep the marker-clearing lines only). Rollback = env off.
- MD §2.6 tests (6) — file name for THIS iteration: `tests/test_iter85_eager_hold.py` (MD's
  `test_iter74_eager_hold.py` name was a placeholder): held gate buffers until release /
  end_of_turn parks while held / resume discards silently (no tts.cancel, no clear) / adopt releases
  audio / mismatch rerun not stuck (reset clears hold) / knob off byte-exact.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Branch `engine/iter85-eager-hold` cut from `engine/iter84-post-interrupt-backoff` tip `0693a9d`; worktree `/tmp/opencode/wt-iter85` | branch law: fix branches stack on current tip; owner pulled FIX 1 forward 2026-09-28; iterNN assigned at cut (MD's `engine/iter74-eager-hold` name was a placeholder) |
| Knob `eager_hold_audio_until_confirm: bool = False` default OFF in config.py; lane env `EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true` | knob law (default-off), iter82/83/84 precedent; rollback = env off, zero code path change |
| Threshold experiment = `DEEPGRAM_EAGER_EOT_THRESHOLD=0.65` on the lane (down from 0.70) | owner latency lever: earlier eager fire banks more TTFT; eager_final_match (adoption guard) proves quality; if match rate drops, revert to 0.70 and keep the hold |
| Battery: `--scenario happy` (turn-1 e2e + eager metrics + booking gate) + `--scenario barge-loop` (interrupt safety: held audio never collides) through the FROZEN driver | happy = the §11.1 money shot (head_start banked, turn-1 e2e <1000ms, eager_final_match 100%); barge-loop = the one scenario that exercises real interrupts now that it exists (owner-ordered @ aaba8ff) |
| §11.1 FIX 1 gate: turn-1 e2e_response <1000ms; eager_final_match stays 100%; ZERO mid-speech agent audio collisions in barge-loop; no regression on booking gate | T4 verdict numbers + MD §2.4 telemetry math |
| T3 DELETES (`_grace_then_cancel` + `eager_resume_grace_ms` + iter38 race-guard dance) = separate commit, executed ONLY after the battery passes | MD §2.5: keeps the A/B fix-vs-main, not fix-vs-deleted |
| Suite debt: same 7 stale reds acceptable (test_delivery x4, iter46, iter59, iter60) | unchanged since iter82 base; never re-derived |
| Docs (md/plans) straight to main; engine code waits for owner merge | LAW 0 |
| Lanes: fresh port per run via systemd-run --collect, killed + port-verified at session end; teardown line in every report | owner teardown law |
| Cancel every test booking (Cal.com event 3801235 REAL) | paid lesson |
| Tests keep EL Sarah voice (lane env unchanged) | AGENTS.md VOICE LAW 2026-09-28: prod = Hannah, tests = Sarah |

## BLOCKED / NEEDS INPUT
| Item | Where |
|---|---|
| Owner GO to start the FIX 1 session | this plan (T0) |
| Owner ear A/B after battery passes | owner schedules |
| Owner verdict on threshold 0.65 (keep vs revert to 0.70) | after battery, from eager_final_match + latency table |

## Environment & Dependencies
- OREGON venv (shared): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`
  (never `<venv>/bin/pip` — copy-mirror trap; use `<venv>/bin/python -m pip`).
- Base worktree: `/tmp/opencode/wt-iter84` (branch `engine/iter84-post-interrupt-backoff` @ `0693a9d`,
  `.env` present). New worktree:
  `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter85 -b engine/iter85-eager-hold 0693a9d`
  then `cp /tmp/opencode/wt-iter84/engine/.env /tmp/opencode/wt-iter85/engine/.env` (ENV LAW).
- Lane ports: pick FRESH ports this session (8039-8044 used 2026-09-28; never prod :8026/:8000-8003/:8090;
  suggested 8045-8046).
- Lane boot: copy `/tmp/opencode/boot_lane_t4_fix5.sh` → `/tmp/opencode/boot_lane_t4_fix1.sh` (wt path
  → wt-iter85, keep fix7 knobs + `POST_INTERRUPT_BACKOFF_MS=500`), ADD
  `export EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true` and `export DEEPGRAM_EAGER_EOT_THRESHOLD=0.65` after the
  .env sourcing.
- Driver scripts on OREGON: `/tmp/opencode/run_driver_t4.sh` (frozen original); for this battery copy to
  `/tmp/opencode/run_driver_t4_fix1.sh` (PORT edit + `--scenario happy`) and
  `/tmp/opencode/run_driver_t4_fix1_bl.sh` (`--scenario barge-loop --max-caller-turns 52`) — exec
  `engine/scripts/llm_mic_caller.py` from wt-iter82 as today (the frozen file; barge-loop lives in
  `llm_mic_caller_b52.py` @ aaba8ff — for the barge-loop run the script must exec `llm_mic_caller_b52.py`,
  see `/tmp/opencode/run_driver_t4_fix5_bl.sh` for the working shape).
- MODEL LAW: caller gpt-4.1-mini (temp 0.3 pin), agent gpt-5.4 everywhere.
- ENV LAW: before ANY run on a worktree: `cp /tmp/opencode/wt-iter84/engine/.env <new-wt>/engine/.env`.
- Evidence: driver json (--out), Langfuse http://46.62.233.228:3001 traces `micbridge-<sid>` via
  `scripts/lf.py`, lane journal via `journalctl --user -u <unit> --no-pager`.
- Ledger DB: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (NO sqlite3 CLI — venv python). IMPORT TRAP: `scripts/live_sql.py` `fetch_traces` hardcodes the
  `llm2llm-graph-`/`diallux-call` name prefixes and silently drops `micbridge-` traces — import via the
  locally-patched-module pattern (load live_sql.py as a module, monkeypatch `fetch_traces` to filter
  `micbridge-`, call `import_run`) — same pattern as the fix7/fix5 sessions; report it again in the report.
- Langfuse server: http://46.62.233.228:3001 (keys in worktree `.env`: `LANGFUSE_HOST`,
  `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`).
- OREGON pushes: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push ...`
  (the helper's file-lock error in worktrees is benign — push succeeds via stored creds).

## Architecture (one block)
```
FROZEN driver (gpt-4.1-mini, happy + barge-loop) --> lane (wt-iter85 engine, EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true, EAGER threshold 0.65, EL Sarah TTS -> gpt-5.4 graph)
EagerEndOfTurn -> turn starts, LLM streams, SentenceGate.hold() [think early, NO audio]
EndOfTurn (adopt) -> gate.release() -> first _speak_chunk stamps t_tts_req, audio flows [speak confirmed]
TurnResumed -> gate.discard() + task.cancel() [silent teardown, nothing was ever spoken]
```

## File Map
| File (absolute path, OREGON) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | THE master plan (STATUS = resume point) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter83_t4_wave1_engine_fixes.md | wave-1 loop plan | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter85_fix1_eager_hold.md | THIS plan | itself |
| /tmp/opencode/wt-iter85 (branch engine/iter85-eager-hold) | FIX 1 code under test | build here |
| /tmp/opencode/wt-iter85/engine/diallux/config.py | add `eager_hold_audio_until_confirm: bool = False` (near `eager_resume_grace_ms` at config.py:224) | edit |
| /tmp/opencode/wt-iter85/engine/diallux/media/sentence_gate.py | hold/release/discard primitives + `add()` early-out + `end_of_turn()` park + `reset()` hold-clear (MD §2.2) | edit |
| /tmp/opencode/wt-iter85/engine/diallux/media/session.py | `_eager_held` attr + hold in `_run_turn` + release in `_on_eot` adopt + silent-discard in `_on_turn_resumed` (MD §2.3) | edit |
| /tmp/opencode/wt-iter85/engine/tests/test_iter85_eager_hold.py | 6 unit tests (MD §2.6) | new |
| /tmp/opencode/boot_lane_t4_fix1.sh | lane boot variant (fix5 knobs + EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true + threshold 0.65) | new (copy of fix5 boot) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/ | battery + teardown evidence (03_fix1_battery.md) | append |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter80-el-flip-mic-phone-fix-src/voice-sdr-turn-taking-fixes.md | FIX 1 design source (§2) | read-only |

## Deploy Rules
- NEVER checkout/switch/reset/pull the OREGON prod checkout; worktrees only.
- NEVER touch diallux.service / :8026 / :8000-8003 / :8090. Lanes: fresh port + systemd-run --user
  --collect + killed at session end; verify `ss -ltnp | grep :<port>` returns 0.
- NEVER inline `&` in ssh; pkill bracket patterns only; `kill <pid>` on uvicorn pid.
- ENV LAW: before ANY run on a worktree, verify `<wt>/engine/.env` exists (copy from wt-iter84).
- OREGON pushes: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push ...`
  (absolute path — relative breaks in worktrees; the gh-creds file-lock error in worktrees is benign).
- Doc commits: docs worktree from origin/main, commit, `push origin HEAD:main`, re-sync Finland
  plan mirror (scp committed files back), remove the docs worktree.
- Cancel every test booking; Cal.com event 3801235 REAL.

## Tasks (in order)

### T0 — session open (10 min, MECHANICAL ONLY — no re-analysis)
1. Read STATUS of `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md`
   (SESSION CLOSE 2026-09-28 FIX 5 EXECUTED — PASS entry).
2. Verify: `git -C /tmp/opencode/wt-iter84 log --oneline -1` = `0693a9d`;
   `ls /tmp/opencode/wt-iter84/engine/.env` exists.
3. Re-run: `cd /tmp/opencode/wt-iter84/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests/test_iter84_backoff.py tests/test_iter80_stt_liveness.py tests/test_iter82_pause_ladder.py -q` → 14 passed.
4. Mechanical anchor check (grep-only, NO analysis): `grep -n "_eager_held\|_grace_then_cancel\|eager_resume_grace_ms" /tmp/opencode/wt-iter84/engine/diallux/media/session.py` — expect NO `_eager_held` (not built yet), `_grace_then_cancel` present (~line 649), `eager_resume_grace_ms` present (~lines 456/630); `grep -n "def hold\|def release\|def discard" /tmp/opencode/wt-iter84/engine/diallux/media/sentence_gate.py` — expect NO matches.
Verification: sha + .env + 14/14 green + anchors match. Unblocks: T1.

### T1 — build FIX 1 (45 min)
1. `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter85 -b engine/iter85-eager-hold 0693a9d`
   && `cp /tmp/opencode/wt-iter84/engine/.env /tmp/opencode/wt-iter85/engine/.env`.
2. config.py: add `eager_hold_audio_until_confirm: bool = False   # FIX 1 (PORT 1): hold eager turn audio until confirmed EOT; 0 = off`
   next to `eager_resume_grace_ms` (config.py:224 area).
3. sentence_gate.py: apply MD §2.2 exactly (hold state + add() early-out + end_of_turn() park +
   hold()/release()/discard() primitives + reset() hold-clear).
4. session.py: apply MD §2.3 exactly (class attr `_eager_held`; hold in `_run_turn` after TTS-context
   mint; release in `_on_eot` adopt branch; silent-discard first branch in `_on_turn_resumed`).
5. `tests/test_iter85_eager_hold.py` — 6 tests per MD §2.6 (adapt file name; test shapes as written).
6. Run: `cd /tmp/opencode/wt-iter85/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests/test_iter85_eager_hold.py tests/test_iter84_backoff.py tests/test_iter80_stt_liveness.py tests/test_iter82_pause_ladder.py -q` → 20 passed.
7. Commit on the branch; push.
Verification: 20/20 green; full-suite stale-red set UNCHANGED (same 7 as iter82 base).
Unblocks: T2.

### T2 — battery: happy (money shot) + barge-loop (interrupt safety) (60 min)
1. Create `/tmp/opencode/boot_lane_t4_fix1.sh` (copy of fix5 boot, wt-iter85 engine, +
   `EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true` + `DEEPGRAM_EAGER_EOT_THRESHOLD=0.65`).
2. Lane H: fresh port P (8045): `systemd-run --user --unit=diallux-fix1-h-<P> --collect /tmp/opencode/boot_lane_t4_fix1.sh <P>`;
   wait `/health` = 200; verify `journalctl --user -u <unit> | grep "connected"` shows elevenlabs
   (model=eleven_turbo_v2_5 voice=uG1JFy6xppqckhHCs2KG).
3. Run driver `--scenario happy` (copy run_driver_t4.sh, PORT→P, out `/tmp/opencode/t4_fix1_h.json`),
   foreground, timeout 420.
4. Verify §11.1: turn-1 `e2e_response_ms` <1000ms; `eager_final_match` 100% on all eager turns;
   `head_start_ms` now BANKED (t_tts_req of the adopted turn lands after the confirmed EOT, not before);
   booking gate PASS (`booked_goodbye` on the 52-turn arc or the happy arc completes) — if a booking
   happens, CANCEL it (cal cancel via POST /v2/bookings/{uid}/cancel, UA diallux-cal-slots/1.0,
   cal-api-version 2026-05-01, key = diallux_live.cal_api_key in
   /home/julio/projects/clean_diallux_SDR/services/cal_slots_endpoint/.env CAL_ACCOUNTS).
5. Lane B: kill lane H; fresh port P2 (8046); driver `--scenario barge-loop --max-caller-turns 52`
   (exec llm_mic_caller_b52.py; copy the shape of `/tmp/opencode/run_driver_t4_fix5_bl.sh`, PORT→P2,
   out `/tmp/opencode/t4_fix1_bl.json`).
6. Verify interrupt safety: ZERO mid-speech agent audio after any barge (clear within ~1s each time);
   NO `tts.cancel`/`clear` events on TurnResumed while held (the silent-discard evidence: journal shows
   `eager turn discarded silently (user resumed, audio was held)` instead of a cancel+clear burst);
   any booking CANCELLED.
7. Langfuse: `lf.py traces --name micbridge --limit 4`; confirm spans; kill lanes; verify ports 0.
Verification: §11.1 row all-PASS + control safety. Unblocks: T3.

### T3 — report + ledger + DELETES + close (40 min)
1. Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/03_fix1_battery.md`:
   evidence (journal excerpts, trace ids, latency table turn-1 e2e/head_start/eager_final_match,
   barge safety table, driver json paths), §11.1 verdict row, teardown line, booking-cancel status.
2. Ledger: monkeypatched-module import (fetch_traces → micbridge filter) of the happy + bargeloop
   traces, runs `fix1-happy` / `fix1-bargeloop` @ `<sha>`.
3. DELETES (ONLY if battery PASSED): separate commit on the branch — delete `_grace_then_cancel()`,
   the `eager_resume_grace_ms` knob + its `_on_eot`/`_on_turn_resumed` branches, the iter38 race-guard
   ordering dance (keep the marker-clearing lines). Re-run the 20-test targeted set + full suite
   (expect same 7 stale reds). Push.
4. Copy driver jsons into the surgeon folder.
5. Update master plan STATUS (session close ritual) + wave-1 plan status + commit docs to main;
   re-sync Finland plan mirror.
6. ASK owner: ear A/B for FIX 1 (hear the banked eager overlap: turn-1 reply faster, zero collisions)
   + threshold 0.65 verdict (keep vs revert) — HITL gate before FIX 8 / wave 2.
Verification: report + ledger rows + deletes commit green + docs pushed. Unblocks: owner HITL.

## Validation Plan (end-to-end)
T0 mechanical (sha/env/14 green/anchors) → build 20/20 green → happy battery (turn-1 e2e <1000ms,
eager_final_match 100%, booking gate) → barge-loop safety (silent discards, zero collisions) → ledger
import → T3 deletes (separate commit, suite green) → owner ear A/B + threshold verdict → HITL → next =
FIX 8 (`SOFT_FILLER_MS=3000`, watch existing-filler redundancy) or wave 2 (FIX 4 ack filter). Abort/
rollback: `EAGER_HOLD_AUDIO_UNTIL_CONFIRM=false` = byte-exact off behavior (knob law); threshold revert
= `DEEPGRAM_EAGER_EOT_THRESHOLD=0.7`.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| FIX 8 soft filler (`SOFT_FILLER_MS=3000`) + existing-filler redundancy check | wave-1 order, after FIX 1 (owner call) |
| FIX 4 ack filter (reuses FIX 1's gate-hold primitive) | wave 2 |
| Py playback accelerator (EL Hannah prod voice, speed 1.08–1.15 effective) | separate feature branch (AGENTS.md VOICE LAW 2026-09-28); NOT a turn-taking fix |
| live_sql.py fetch_traces name-filter trap (micbridge imports need patched module) | PT candidate — flagged in 02_fix5_battery.md; do NOT fix in this plan |
| Owner ear A/B for FIX 7 (STT liveness) | still pending from 2026-09-28 |
| Arc-bloat ledger note (duplicate caller turns, turn cap margin) | driver FROZEN — owner decision |
