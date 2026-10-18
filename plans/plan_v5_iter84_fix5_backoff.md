# plan_v5_iter84_fix5_backoff — FIX 5 post-interrupt backoff (owner 500ms): one branch, unit tests, ONE barge-in battery through the FROZEN fake caller

## Meta
- Date: 2026-09-28. Executes the NEXT fix of `plans/plan_v5_iter83_t4_wave1_engine_fixes.md`
  (FIX 5 of wave 1) under the workflow law of THE master plan
  `plans/plan_v5_iter81_master_ladder.md` — read its STATUS block FIRST
  (SESSION CLOSE 2026-09-28 FIX 7 BATTERY EXECUTED entry is the resume point).
- WORKING MODE (two-box law): session on FINLAND (46.62.233.228). ALL repo ops via
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<command>"` to OREGON
  (hostname ubuntu-4gb-hil-1). OREGON checkout = source of truth; Finland tree is a read-only plan mirror.
- Project root: /home/julio/projects/clean_diallux_SDR (OREGON checkout).
- Scope: FIX 5 ONLY — build (config knob + session patch + 4 unit tests), ONE battery via the frozen
  driver `--scenario barge-in-only`, §11.1 pass gate, owner ear A/B. NO other fix. FIX 1 (eager hold)
  is explicitly HELD per owner (small fix first, pleasant surprise). FIX 8 stays queued after.
- CODE ANALYSIS: DONE AND AUDITED — lives in the fixes MD §6 (quoted below). The next agent must NOT
  re-derive the design or re-audit FIX 5. The ONLY accepted code inspection is the mechanical T0
  state check (sha, .env, test re-run). One DECLARED adaptation exists (see Resolved Decisions) —
  apply it as written, do not redesign.
- Status: EXECUTED + CLOSED 2026-09-28 — build @ `0693a9d` (14/14 targeted green, suite debt unchanged),
  battery §11.1 owner-500ms gate PASS (all 5 barge events, zero fires, zero cost — window never binds in this
  engine shape; owner pin: KEEP 500, revisit after FIX 1), report
  `research/surgeon/iter83-t4-wave1/02_fix5_battery.md`, ledger runs fix5-b/fix5-happy/fix5-bargeloop @ 0693a9d,
  booking cancelled 200 (cal id 26001405), lanes 8043/8044 torn down. Owner-ordered extras: driver variant
  `llm_mic_caller_b52.py` committed `aaba8ff` on `engine/iter82-pause-nudge`; AGENTS.md VOICE LAW corrected on
  main `4159f30` (EL default, prod Hannah, tests Sarah, Cartesia=HIPAA only). Ear A/B FIX 5 = moot (no audible
  change live); pending HITL = FIX 7 ear A/B (from iter83). NEXT: FIX 1 (eager hold), owner pulled forward.

## Compaction Context (2026-09-28 FIX 7 battery session — carried verbatim)

**Wave-1 state:** FIX 7 (STT liveness) BUILT + BATTERY-PASSED on branch `engine/iter83-stt-liveness`
@ `fa62162` (pushed), worktree `/tmp/opencode/wt-iter83a` on OREGON, cut from `engine/iter82-pause-nudge`
tip `4459f9f`. Scenarios A (age-gate refusal, `prewarm: refused stale stt (age > 120s)` log +
fresh connect +141ms, normal 288s arc, trace 1acda411a0ff) and B (silent-zombie watchdog 15.8s,
single `stt:zombie_reconnect` span, mic chunks 7840, turns continued, trace 2f625c70052a) PASS.
Hard-kill (`ss -K`) fires the PRE-EXISTING instant reconnect — silent-zombie lever is
`iptables -I OUTPUT -p tcp --sport <stt-local-port> -j DROP` (external, no engine hooks).
Zero false fires, zero bookings, zero latency cost. Report:
`research/surgeon/iter83-t4-wave1/01_fix7_battery.md`. Ledger runs imported:
fix7-sanity-ref (4459f9f) / fix7-a2 / fix7-b1 / fix7-b2 (fa62162).

**T4 latency verdict (owner add, LATENCY-PERCENTILE-SOP):** e2e p50 ~1.2s is LLM-bound
(gpt-5.4 TTFT ~770-790ms = ~65% of the turn); turn-1 e2e 1064-1157ms; the ~300ms eager overlap
is UNBANKED (head_start ~40ms @ EAGER threshold 0.70). FIX 1 eager hold + threshold 0.65/0.6 is
the big lever — owner: "lets hold fix 1, lets do the other [FIX 5] first".

**OWNER DECISIONS 2026-09-28 (this plan's mandate):** (1) one fix per session, small first:
FIX 5 NOW, FIX 1 held, FIX 8 after; (2) FIX 5 value = **`POST_INTERRUPT_BACKOFF_MS=500`**
(owner-specified 2026-09-28, recorded in master plan OWNER NOTE — overrides the fixes MD's
1000ms default; the MD §11.1 "≥1s gap" gate reads "≥500ms gap" under the owner value);
(3) same workflow: new plan SOP, no code analysis, one battery, docs to main.

**FIX 5 design (fixes MD §6, VERBATIM ANCHORS — do not re-derive):**
Ports Vapi D8 `stopSpeakingPlan.backoffSeconds`. After any REAL barge-in, block new agent audio
for `backoff_ms` so the caller's answer lands before the agent speaks again. Pure guardrail: no
structure deleted; hot-path cost = one timestamp comparison on the first chunk of the next turn.
- Knob: `post_interrupt_backoff_ms: int = 0` (0 = off; default OFF in config.py per knob law;
  the LANE env turns it ON = 500 for the battery).
- Stamp: `_backoff_until: float | None = None` class attr; stamped where a real barge-in is
  confirmed: `self._backoff_until = time.perf_counter() + backoff / 1000.0`.
- Wait: in `_speak_chunk`, inside the first-TTS-request guard, ONE-SHOT: read + clear
  `_backoff_until`, `await asyncio.sleep(wait)` if positive, BEFORE stamping `t_tts_req`.
- `_speak_exact` lines bypass `_speak_chunk` deliberately (ladder rungs own their own silence
  logic; ladder disarms on user speech anyway).
- Tests (MD §6.3, 4): first chunk waits out remaining window (mock asyncio.sleep); one-shot
  (second chunk no wait); no barge no wait; knob 0 = no sleep. Test file name for this iteration:
  `tests/test_iter84_backoff.py` (MD's `test_iter78_backoff.py` name was a placeholder).

**DECLARED ADAPTATION (the one and only, apply as written):** the fixes MD stamps the backoff in
`_barge_resolve`'s real branch — that is a FIX 4 primitive that does NOT exist at `fa62162`
(verified: `grep -n '_barge_resolve|_barge_hold' media/session.py` = no matches). TODAY's
real-barge confirm point is `_on_start_of_turn`'s `interrupted` branch. So: stamp
`_backoff_until` there (after `self._turn_task.cancel()` / BARGEINS.inc()), NOT in
`_barge_resolve`. The `_speak_chunk` wait patch applies AS-WRITTEN (anchor verified below).
This adaptation is battery-neutral: today every StartOfTurn-with-turn-in-flight IS treated as a
real interruption (the ack distinction is FIX 4, later wave).

**Verified code anchors @ fa62162 (`/tmp/opencode/wt-iter83a/engine/diallux/media/session.py`):**
- `_on_start_of_turn` at line 681; interrupted branch lines 687-693
  (`self._clock.barge_in = True` / `t_barge_in = time.perf_counter()` / `self._turn_task.cancel()`
  / BARGEINS.inc()); `log.info("barge-in on call %s")` line 705. Stamp goes in this branch.
- `_speak_chunk` at line 919; the first-TTS-request guard at lines 925-928
  (`clock = getattr(self, "_speak_clock", None) or getattr(self, "_clock", None)`
  / `if clock is not None and clock.extra.get("t_tts_req") is None:` then
  `clock.extra["t_tts_req"] = time.perf_counter()`). The MD wait block inserts between the
  guard and the stamp — matches current code shape exactly (MD patch applies as-written).
- `config.py`: `post_interrupt_backoff_ms` NOT present yet (verified) — add near the FIX 7 knobs
  (`stt_adopt_max_age_s` at line 469, `stt_rx_zombie_ms` line 470).

**Frozen instrument (untouchable):**
- Driver: `/tmp/opencode/run_driver_t4.sh` (OREGON; PORT= edit only; exec
  `engine/scripts/llm_mic_caller.py` @ d70c438 from wt-iter82). Driver scenarios exist:
  `--scenario {happy,barge-in-only,dump-only,watchdog}` (verified in driver argparse) — this
  battery uses `--scenario barge-in-only` for the money shot and `--scenario happy` as the
  no-barge control. Other flags frozen: `--persona Danny --agent-idle-s 5.5 --max-turn-wait 60
  --min-gap 2.5 --max-gap 6 --caller-model gpt-4.1-mini --max-caller-turns 30`.
- Lane boot: `/tmp/opencode/boot_lane_t4_fix7.sh <port>` (wt-iter83a engine; PAUSE_LADDER knobs ON;
  STT_RX_ZOMBIE_MS=15000 STT_ADOPT_MAX_AGE_S=120). FIX 5 variant: copy to
  `/tmp/opencode/boot_lane_t4_fix5.sh` adding `export POST_INTERRUPT_BACKOFF_MS=500` after the
  .env sourcing (same pattern as the proven `boot_lane_t4_fix7_pw.sh`).
- MODEL LAW: caller gpt-4.1-mini (temp 0.3 pin), agent gpt-5.4 everywhere.
- ENV LAW: before ANY run on a worktree: `cp /tmp/opencode/wt-iter83a/engine/.env <new-wt>/engine/.env`.
- Evidence: driver json (--out), Langfuse http://46.62.233.228:3001 traces `micbridge-<sid>` via
  `scripts/lf.py` from `/tmp/opencode/wt-iter84/engine` with
  `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`, lane journal via
  `journalctl --user -u <unit> --no-pager`. Tool lines do NOT print in uvicorn logs.
- Ledger DB: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (NO sqlite3 CLI — venv python; import via `scripts/live_sql.py import --window "HH:MM-HH:MM"
  --run <name> --commit <sha>`).
- Cal.com event 3801235 REAL — cancel every test booking.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| FIX 5 value = `POST_INTERRUPT_BACKOFF_MS=500` on the lane (MD default 1000 overridden) | owner pin 2026-09-28, recorded in master plan OWNER NOTE |
| FIX 1 held; FIX 8 queued after FIX 5 | owner: small fix first, pleasant surprise; one at a time |
| Branch `engine/iter84-post-interrupt-backoff` cut from `engine/iter83-stt-liveness` tip `fa62162`; worktree `/tmp/opencode/wt-iter84` | branch law: fix branches stack on current tip; iterNN assigned at cut (MD's `engine/iter78-backoff` was a placeholder) |
| Stamp ADAPTATION: `_on_start_of_turn` interrupted branch instead of MD's `_barge_resolve` real branch | `_barge_resolve` is a FIX 4 primitive, absent at fa62162 (verified); `_speak_chunk` wait applies as-written |
| Knob default 0 (off) in config.py; lane env = 500 | knob law, iter82/83 precedent; rollback = 0 |
| Battery: `--scenario barge-in-only` (money shot) + `--scenario happy` (no-barge control) through the FROZEN driver | driver has the scenario (verified in argparse); §11.1 needs barge + next-turn audio delta |
| §11.1 FIX 5 gate under owner value: post-barge next-turn TTS starts ≥500ms after the barge-in, never overlapping | owner 500ms pin overrides MD's 1s example |
| No A/B lane pair needed: unit tests prove the sleep; battery proves no-overlap + no-regression; owner ear A/B after | §11.1 + owner per-fix loop |
| Docs (md/plans) straight to main; engine code waits for owner merge | LAW 0 |
| Lanes: fresh port per run via systemd-run --collect, killed + port-verified at session end; teardown line in every report | owner teardown law |
| Cancel any test booking (Cal.com event 3801235 REAL) | paid lesson |

## BLOCKED / NEEDS INPUT
| Item | Where |
|---|---|
| Owner GO to start the FIX 5 session | this plan (T0) |
| Owner ear A/B availability after battery passes | owner schedules |

## Environment & Dependencies
- OREGON venv (shared): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`
  (never `<venv>/bin/pip` — copy-mirror trap; use `<venv>/bin/python -m pip`).
- Base worktree: `/tmp/opencode/wt-iter83a` (branch `engine/iter83-stt-liveness` @ `fa62162`,
  `.env` present). New worktree: `git -C /home/julio/projects/clean_diallux_SDR worktree add
  /tmp/opencode/wt-iter84 -b engine/iter84-post-interrupt-backoff fa62162` then copy `.env` (ENV LAW).
- Lane ports: pick FRESH ports this session (8039-8042 used 2026-09-28; never prod :8026/:8000-8003/:8090).
- Langfuse server: http://46.62.233.228:3001 (keys in worktree `.env`).
- OREGON pushes: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push ...`.

## Architecture (one block)
```
FROZEN driver (gpt-4.1-mini, barge-in-only + happy) --> lane (wt-iter84 engine, POST_INTERRUPT_BACKOFF_MS=500, flux STT -> gpt-5.4 graph -> TTS)
real barge-in (_on_start_of_turn interrupted branch) -> _backoff_until = now + 0.5s -> next turn FIRST _speak_chunk sleeps out the window (one-shot) -> caller's answer lands -> agent speaks
```

## File Map
| File (absolute path, OREGON) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | THE master plan (STATUS = resume point) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter83_t4_wave1_engine_fixes.md | wave-1 loop plan | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter84_fix5_backoff.md | THIS plan | itself |
| /tmp/opencode/wt-iter84 (branch engine/iter84-post-interrupt-backoff) | FIX 5 code under test | build here |
| /tmp/opencode/wt-iter84/engine/diallux/config.py | add `post_interrupt_backoff_ms: int = 0` | edit |
| /tmp/opencode/wt-iter84/engine/diallux/media/session.py | `_backoff_until` attr + stamp in `_on_start_of_turn` + wait in `_speak_chunk` | edit |
| /tmp/opencode/wt-iter84/engine/tests/test_iter84_backoff.py | 4 unit tests (MD §6.3) | new |
| /tmp/opencode/boot_lane_t4_fix5.sh | lane boot variant (FIX 7 knobs + POST_INTERRUPT_BACKOFF_MS=500) | new (copy of fix7 boot) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/ | battery + teardown evidence (02_fix5_battery.md) | append |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter80-el-flip-mic-phone-fix-src/voice-sdr-turn-taking-fixes.md | FIX 5 design source (§6, §11.1) | read-only |

## Deploy Rules
- NEVER checkout/switch/reset/pull the OREGON prod checkout; worktrees only.
- NEVER touch diallux.service / :8026 / :8000-8003 / :8090. Lanes: fresh port + systemd-run --collect
  + killed at session end; verify `ss -ltnp | grep :<port>` returns 0.
- NEVER inline `&` in ssh; pkill bracket patterns only; `kill <pid>` on uvicorn pid.
- ENV LAW: before ANY run on a worktree, verify `<wt>/engine/.env` exists (copy from wt-iter83a).
- OREGON pushes: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push ...`
  (absolute path — relative breaks in worktrees).
- Doc commits: docs worktree from origin/main, commit, `push origin HEAD:main`, re-sync Finland
  plan mirror (scp committed files back), remove the docs worktree.
- Cancel every test booking; Cal.com event 3801235 REAL.

## Tasks (in order)

### T0 — session open (10 min, MECHANICAL ONLY — no re-analysis)
1. Read STATUS of `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md`
   (SESSION CLOSE 2026-09-28 FIX 7 BATTERY EXECUTED entry).
2. Verify: `git -C /tmp/opencode/wt-iter83a log --oneline -1` = `fa62162`;
   `ls /tmp/opencode/wt-iter83a/engine/.env` exists.
3. Re-run: `cd /tmp/opencode/wt-iter83a/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests/test_iter80_stt_liveness.py tests/test_iter82_pause_ladder.py -q` → 10 passed.
Verification: sha + .env + 10/10 green. Unblocks: T1.

### T1 — build FIX 5 (30 min)
1. `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter84 -b engine/iter84-post-interrupt-backoff fa62162`
   && `cp /tmp/opencode/wt-iter83a/engine/.env /tmp/opencode/wt-iter84/engine/.env`.
2. config.py: add `post_interrupt_backoff_ms: int = 0   # FIX 5 (PORT 5): post-interrupt backoff; 0 = off`
   next to the FIX 7 knobs (line ~470).
3. session.py, three edits:
   a. class attr: `_backoff_until: float | None = None      # FIX 5 (PORT 5)`.
   b. `_on_start_of_turn` interrupted branch (after BARGEINS.inc()):
      `backoff = getattr(self.settings, "post_interrupt_backoff_ms", 0)` /
      `if backoff > 0:` / `self._backoff_until = time.perf_counter() + backoff / 1000.0`.
   c. `_speak_chunk` first-request guard — insert BEFORE the `t_tts_req` stamp (MD §6.2 as-written):
      one-shot read+clear of `_backoff_until`, `await asyncio.sleep(wait)` when positive.
4. `tests/test_iter84_backoff.py` — 4 tests per MD §6.3 (adapted: real barge = call
   `_on_start_of_turn` with a running `_turn_task`; mock `asyncio.sleep`).
5. Run: `cd /tmp/opencode/wt-iter84/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests/test_iter84_backoff.py tests/test_iter80_stt_liveness.py tests/test_iter82_pause_ladder.py -q` → 14 passed.
6. Commit on the branch; push with gh-creds helper.
Verification: 14/14 green; full-suite stale-red set UNCHANGED (same 7 as iter82 base). Unblocks: T2.

### T2 — battery: barge-in-only (money shot) + happy control (60 min)
1. Create `/tmp/opencode/boot_lane_t4_fix5.sh` = copy of `boot_lane_t4_fix7.sh` +
   `export POST_INTERRUPT_BACKOFF_MS=500` after the .env sourcing.
2. Lane B: fresh port P (e.g. 8043): `systemd-run --user --unit=diallux-fix5-b-<P> --collect /tmp/opencode/boot_lane_t4_fix5.sh <P>`;
   wait `/health` = 200.
3. Run driver `--scenario barge-in-only` (copy `run_driver_t4.sh`, PORT→P, `--scenario barge-in-only`,
   out `/tmp/opencode/t4_fix5_b.json`, journal-log `/tmp/opencode/t4_fix5_b.log`), foreground, timeout 420.
4. Verify §11.1 (owner 500ms gate): for every barge-in in the journal
   (`barge-in on call <sid>` timestamps) the NEXT turn's TTS start must be ≥500ms later and never
   overlapping — compute from turn reports (`t_barge_in` vs `t_tts_req` / journal deltas); driver json
   turns continue; zero mid-speech agent audio after a barge-in until the window elapses.
5. Lane H (control): kill lane B; fresh lane port P2, driver `--scenario happy`, out
   `/tmp/opencode/t4_fix5_h.json` — ZERO barge-ins expected → zero backoff waits (no `_backoff_until`
   stamps in journal); turn reports no regression vs fix7-a2/b2 baselines (e2e p50 within ~10%).
6. Langfuse: `lf.py traces --name micbridge --limit 4`; confirm spans; booking check in json/traces
   → any booking CANCELLED.
7. Kill lanes; verify ports 0 listeners.
Verification: ≥500ms post-barge gap + zero overlaps + control clean. Unblocks: T3.

### T3 — report + ledger + close (30 min)
1. Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/02_fix5_battery.md`:
   evidence (journal excerpts, trace ids, per-barge gap table, driver json paths), §11.1 verdict row,
   teardown line, booking-cancel status.
2. Ledger: `cd /tmp/opencode/wt-iter84/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/live_sql.py import --window "<HH:MM-HH:MM>" --run fix5-battery --commit <sha>` (+ control run).
3. Copy driver jsons into the surgeon folder.
4. Update master plan STATUS (session close ritual) + wave-1 plan status + commit docs to main;
   re-sync Finland plan mirror.
5. ASK owner: ear A/B for FIX 5 (hear the 500ms floor after an interruption) — HITL gate before FIX 8
   (or the held FIX 1).

## Validation Plan (end-to-end)
Build 14/14 green → barge-in battery (gap ≥500ms, zero overlap) → happy control (zero waits, no
regression) → ledger import → owner ear A/B → HITL → next = FIX 8 (`SOFT_FILLER_MS=3000`, watch
owner's existing-filler redundancy) or FIX 1 eager hold (owner call). Abort/rollback:
`POST_INTERRUPT_BACKOFF_MS=0` = byte-exact off behavior (knob law; MD §6.4).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| FIX 1 eager hold (`EAGER_HOLD_AUDIO_UNTIL_CONFIRM`, threshold 0.65/0.6) | HELD by owner this session — the big latency lever (~300ms bank), next after FIX 8 or pulled forward by owner call |
| FIX 8 soft filler (`SOFT_FILLER_MS=3000`) + existing-filler redundancy check | wave-1 order, after FIX 5 |
| FIX 4 ack filter (the `_barge_resolve` primitive) | wave 2; FIX 5 adaptation intentionally independent of it |
| Owner ear A/B for FIX 7 (STT liveness) | still pending from 2026-09-28 battery session |
| Arc-bloat ledger note (duplicate caller turns, turn cap margin) | driver FROZEN — owner decision |
