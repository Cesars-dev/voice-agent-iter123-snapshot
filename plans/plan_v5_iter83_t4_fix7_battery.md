# plan_v5_iter83_t4_fix7_battery — FIX 7 battery: Scenarios A + B through the FROZEN fake caller (one at a time, one session)

## Meta
- Date: 2026-09-28. Executes ONE task of `plans/plan_v5_iter83_t4_wave1_engine_fixes.md` (T1 battery step)
  under the workflow law of THE master plan `plans/plan_v5_iter81_master_ladder.md` — read its STATUS
  block FIRST (SESSION CLOSE 2026-09-28 entry is the resume point).
- WORKING MODE (two-box law): session on FINLAND (46.62.233.228). ALL repo ops via
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<command>"` to OREGON
  (hostname ubuntu-4gb-hil-1). OREGON checkout = source of truth; Finland tree is a read-only plan mirror.
- Project root: /home/julio/projects/clean_diallux_SDR (OREGON checkout).
- Scope: FIX 7 (STT liveness) acceptance battery ONLY — Scenario A (age-gate corpse refusal) then
  Scenario B (mid-call socket kill → zombie watchdog) — then §11.1 pass signals + owner ear A/B + HITL.
  NO other fix, NO code changes to FIX 7 (committed `fa62162` is frozen unless the battery fails).
- CODE ANALYSIS: DONE AND AUDITED — lives in the sources below. The next agent must NOT re-derive,
  re-verify seams, re-read engine internals beyond the anchors quoted here, or "double check" the FIX 7
  design. The only accepted re-checks are the mechanical T0 state checks (sha, .env presence, 5/5 test
  re-run) — evidence the tree is intact, not new analysis. Battery FAIL = exception path only.
- Status: EXECUTED 2026-09-28 — Scenarios A + B PASS (§11.1 all green), latency T4 added at owner request, ledger imported, report `research/surgeon/iter83-t4-wave1/01_fix7_battery.md`. AWAITS: owner ear A/B (HITL) before FIX 7 is declared done.
- EXECUTION SUMMARY (2026-09-28): A = prewarm ON via boot variant `boot_lane_t4_fix7_pw.sh` (env-only
  deviation: `CALL_PREWARM=false` in .env made the frozen boot untestable; code untouched) —
  `prewarm: refused stale stt (age > 120s)` @ +136s → fresh connect +141ms → normal 288s arc, 0
  reconnects, no booking (trace 1acda411a0ff). B = `ss -K` hard-kill fires the PRE-EXISTING instant
  reconnect (not FIX 7); true silent-zombie lever = `iptables OUTPUT DROP` on the STT conn's local
  port — B2: watchdog fired 15.8s (mic chunks=7840, audio flowed), single `stt:zombie_reconnect`
  span (trace 2f625c70052a), turns continued, no false fires, no booking. T4 latency scorecard in
  report: FIX 7 zero latency cost; e2e p50 ~1.2s LLM-bound; ~300ms eager overlap still UNBANKED
  (head_start ~40ms @0.70) → FIX 1 eager hold is the lever (owner leaning: pull FIX 1 forward).

## Compaction Context (2026-09-28 FIX 7 build session — carried verbatim)

**Where FIX 7 lives:** branch `engine/iter83-stt-liveness` @ commit `fa62162` (pushed to origin),
worktree `/tmp/opencode/wt-iter83a` on OREGON, cut from `engine/iter82-pause-nudge` tip `4459f9f`
(iter82 pause-ladder files committed there 5/5 green same day). Patch contents:
1. `engine/diallux/media/prewarm.py` — `get(kind, max_age_s=None)` refuses pooled sockets older than
   the gate (`_spawn_ts` backdating is the test lever), closes corpse, returns None → caller falls
   back to fresh connect (call never fails on the pool).
2. `engine/diallux/media/deepgram_stt.py` — `_last_rx` stamped at `connect()` (adopt + fresh paths)
   and on EVERY inbound frame in `_recv_loop`; public `last_rx` property.
3. `engine/diallux/media/session.py` — `_stt_liveness_watchdog()` task (started in `start()` when
   `stt_rx_zombie_ms > 0`, cancelled in `stop()`): ticks 1s, fires ONLY when `self._mic_chunks > 0`
   AND `time.monotonic() - self.stt.last_rx > stt_rx_zombie_ms/1000`; on fire: tracer span
   `stt:zombie_reconnect` (metadata silent_s + mic_chunks) + `await self._on_stt_disconnect()`
   (the EXISTING transparent reconnect; a fresh watchdog is NOT restarted — new socket is
   fresh-connect young; noted in fixes MD §8.4 as a tuning option).
4. `engine/diallux/config.py` — knobs `stt_adopt_max_age_s: float = 120.0`, `stt_rx_zombie_ms: int = 15000`
   (0 = off for both; watchdog exits immediately when 0).

**Test state (verified this session):** `tests/test_iter80_stt_liveness.py` 5/5 green
(stale_socket_refused, fresh_socket_adopted, zombie_fires_reconnect, silent_caller_no_premature_fire,
knob_zero_off) + `tests/test_iter82_pause_ladder.py` 5/5 (loop-hardened rewrite inside iter83a) +
`test_iter44_cache_floor.py` green. FULL SUITE = same 7 stale pre-existing reds as the iter82 base
(4 in `tests/test_delivery.py`, 1 `test_iter46_latency_floor.py` fast_first_flush, 1
`test_iter59_dedupe_semantic.py`, 1 `test_iter60_audit_fixes.py`) — ZERO new failures from FIX 7.

**ENV LAW (paid lesson this session):** fresh worktrees MUST copy the runtime env before any
pytest/lane run: `cp /tmp/opencode/wt-iter82/engine/.env <new-wt>/engine/.env` — config.py reads
`env_file=".env"` cwd-relative, file is gitignored; a fresh worktree without it gets empty keys →
real Deepgram connect 401 → `test_iter44_cache_floor.py::test_session_start_dead_and_hanging_store_proceeds`
false-reds (looks like a code regression, is not). wt-iter83a ALREADY has its `.env` copied.

**Sanity baseline (BEFORE any fix, lane 8037, driver FROZEN):** booking gate FAILED —
`turn_cap_goodbye`, 31 caller turns (cap 30), 57 agent turns, 300s; NO booking created (nothing to
cancel); root cause = arc bloat: duplicate one-word caller turns ("Danny." x2, "Reyes" x2, "Yes,
that's the best number." x2), 5-round discovery extraction, 4-round name capture; transport clean
(e2e 1.1–1.5s, 0 wedges). Trace `micbridge-0744d744506d` = `946cc93d8d80` on Langfuse; earlier aborted
run `micbridge-aac5c3b5b256` = `0f8a5ffac70f`. Report:
`research/surgeon/iter83-t4-wave1/00_sanity_baseline.md` (+ `00_sanity_t4_fake_v8.json`).

**FROZEN instrument (untouchable):**
- Lane boot: `/tmp/opencode/boot_lane_t4_fix7.sh <port>` (OREGON; wt-iter83a engine; PAUSE_LADDER knobs
  ON: PAUSE_LADDER_MODE=reminder PAUSE_REASK_MS=15000 PAUSE_LADDER_MAX=1; FIX 7 knobs ON:
  STT_RX_ZOMBIE_MS=15000 STT_ADOPT_MAX_AGE_S=120; 127.0.0.1; fresh port per run, never prod
  :8026/:8000-8003; launched via `systemd-run --unit=<name> --collect`, killed at session end).
- Driver: `/tmp/opencode/run_driver_t4.sh` (OREGON; PORT= must be edited to the lane port; args frozen:
  --scenario happy --persona Danny --agent-idle-s 5.5 --max-turn-wait 60 --min-gap 2.5 --max-gap 6
  --caller-model gpt-4.1-mini --max-caller-turns 30; env wt-iter83a/engine/.env; journal-log + --out
  under /tmp/opencode/). Driver code = `engine/scripts/llm_mic_caller.py` at `d70c438` — NEVER edit.
- Evidence: driver json (--out), Langfuse http://46.62.233.228:3001 traces `micbridge-<sid>` via
  `scripts/lf.py traces --name micbridge --limit N` / `lf.py tools <trace-id>` / `lf.py gens <trace-id>`
  run from `/tmp/opencode/wt-iter83a/engine` with `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`,
  lane journal via `journalctl --user -u <unit> --no-pager`. Tool lines do NOT print in uvicorn logs.
- MODEL LAW: caller gpt-4.1-mini (temp 0.3 pin), agent gpt-5.4 everywhere.

**Pass signals (fixes MD §11.1, FIX 7 row):**
- Killed pooled socket: reconnect fires ≤ 15s, call continues audibly.
- Normal calls: zero spurious reconnects.
- Existing metric/span proof: `stt:zombie_reconnect` span; `prewarm: refused stale` log line;
  turn reports (`e2e_response_ms`, `barge_in`, `resumed_count`) must NOT regress vs the sanity run.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| FIX 7 code FROZEN at `fa62162` — battery tests it as-built; any defect = new commit on same branch, not a rewrite | LAW 0; one variable per battery |
| Scenarios A + B, ONE AT A TIME, same session: A first (cheap, deterministic), then B (mid-call kill) | owner: "run both scenarios... one at the time" |
| Sabotage = EXTERNAL shell action (timestamp backdate / socket kill) — NO test-only code paths added to the engine | owner pollution worry; FIX 7 patch has zero test hooks |
| Lanes = fresh port per run via boot_lane_t4_fix7.sh + systemd-run --collect, killed + port-verified at session end; teardown line goes in every run report | owner: "how do we make sure we dont run those shells again" |
| Driver FROZEN (d70c438 code); arc-bloat finding (duplicate caller turns) = ledger-note only, owner decides | master plan T3 law |
| Battery with STT knobs ON only — no A/B lane pair needed for the pass signal (span presence/absence is the gate); owner ear A/B (knob on/off) comes AFTER battery | §11.1; owner listens per fix |
| Cancel any test booking created (Cal.com event 3801235 REAL) | paid lesson |
| Docs (md/plans) straight to main; engine code waits for owner merge | LAW 0 |
| ENV LAW: before ANY run on a worktree, verify `<wt>/engine/.env` exists (copy from wt-iter82) | false-red lesson 2026-09-28 |

## BLOCKED / NEEDS INPUT
| Item | Where |
|---|---|
| Owner GO to start the battery session | this plan (T0) |
| Owner ear A/B availability after battery passes | owner schedules |

## Environment & Dependencies
- OREGON venv (shared): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (never
  `<venv>/bin/pip` — copy-mirror trap; use `<venv>/bin/python -m pip`).
- Worktree: `/tmp/opencode/wt-iter83a` (exists, at `fa62162`, `.env` present — VERIFY at session open).
- Lane ports: pick a FRESH port this session (8038 used 2026-09-28; never prod :8026/:8000-8003).
- Langfuse server: http://46.62.233.228:3001 (keys in worktree `.env`).
- Ledger DB: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (NO sqlite3 CLI — venv python; import via `scripts/live_sql.py import --window "HH:MM-HH:MM" --run <name> --commit <sha>`).
- Bookings: any test booking MUST be cancelled (event 3801235 REAL); check driver json for
  `create_livecall_booking` / trace for a booking tool call.

## Architecture (one block)
```
FROZEN driver (gpt-4.1-mini, callback inject) --> lane 8039 (wt-iter83a engine, FIX 7 knobs ON, flux STT -> gpt-5.4 graph -> Cartesia TTS)
Scenario A: pool corpse (backdate _spawn_ts >120s) -> expect "prewarm: refused stale" + fresh connect + normal call
Scenario B: kill STT ws mid-call (external) -> expect stt:zombie_reconnect span <=15s + transparent reconnect + turns continue
```

## File Map
| File (absolute path, OREGON) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | THE master plan (STATUS = resume point; session closes update it) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter83_t4_wave1_engine_fixes.md | wave-1 loop plan | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter83_t4_fix7_battery.md | THIS plan | itself |
| /tmp/opencode/wt-iter83a (branch engine/iter83-stt-liveness @ fa62162) | FIX 7 code under test | read-only (unless battery fails) |
| /tmp/opencode/wt-iter83a/engine/diallux/media/prewarm.py | age gate under test | read-only |
| /tmp/opencode/wt-iter83a/engine/diallux/media/deepgram_stt.py | heartbeat under test | read-only |
| /tmp/opencode/wt-iter83a/engine/diallux/media/session.py | watchdog under test | read-only |
| /tmp/opencode/boot_lane_t4_fix7.sh | lane boot (knobs ON) | use as-is; fresh port arg |
| /tmp/opencode/run_driver_t4.sh | FROZEN driver launcher | edit PORT only |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/ | battery + teardown evidence | append |

## Deploy Rules
- NEVER checkout/switch/reset/pull the OREGON prod checkout; worktrees only.
- NEVER touch diallux.service / :8026 / :8000-8003 / :8090. Lanes: fresh port + systemd-run --collect
  + killed at session end; verify `ss -ltnp | grep :<port>` returns 0.
- NEVER inline `&` in ssh; pkill bracket patterns only; use `kill <pid>` on the uvicorn pid.
- OREGON pushes: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push ...`
  (absolute path — relative breaks in worktrees).
- Doc commits: worktree from origin/main, commit, `push origin HEAD:main`, re-sync Finland plan mirror
  (`scp` the committed file back), then remove the docs worktree.
- Cancel every test booking; Cal.com event 3801235 REAL.

## Tasks (in order)

### T0 — session open (10 min)
1. Read STATUS of `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md`
   (SESSION CLOSE 2026-09-28 entry) — confirms resume point and pins.
2. Verify worktree state: `git -C /tmp/opencode/wt-iter83a log --oneline -1` must print `fa62162`;
   `ls /tmp/opencode/wt-iter83a/engine/.env` must exist (if missing: `cp /tmp/opencode/wt-iter82/engine/.env /tmp/opencode/wt-iter83a/engine/.env`).
3. Quick re-run of the FIX 7 tests to confirm the tree is sane:
   `cd /tmp/opencode/wt-iter83a/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests/test_iter80_stt_liveness.py -q`
   → expect 5 passed.
Verification: sha + .env + 5/5 green. Unblocks: T1.
NOTE (anti-double-work): T0 is MECHANICAL verification only — sha match, file exists, tests pass. Do NOT
re-open the engine files to re-analyze the patch, re-verify seams, or audit the FIX 7 design: the code
analysis is DONE and audited (master plan Compaction + this plan's Compaction Context, patch @ fa62162
pushed). Re-deriving it wastes the session and risks diverging from the audited verdict.

### T1 — Scenario A: age-gate corpse refusal (cheap, deterministic, ~5 min)
Goal: a >120s-old pooled STT socket is refused; the call falls back to fresh connect and runs normally.
Files: none changed (test lever only).
Commands (OREGON, full):
1. Pick fresh port P1 (e.g. 8039): `systemd-run --unit=diallux-fix7-a-<P1> --collect /tmp/opencode/boot_lane_t4_fix7.sh <P1>`
2. Wait for health: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<P1>/health` → 200.
3. Backdate the pool timestamp INSIDE the lane process via the prewarm module (external lever, no engine
   edit): on the NEXT call the pool will be empty of a fresh socket — simplest deterministic lever:
   wait >120s after lane boot before the first call (age gate uses real `_spawn_ts`, so a socket spawned
   at boot is naturally >120s old by then) — NO code surgery needed. Wait: `sleep 125`.
4. Run the frozen driver once: edit PORT in `/tmp/opencode/run_driver_t4.sh` to P1, then run it
   (foreground via ssh, timeout 240s) — same flags as compaction context.
5. Verify pass signal: `journalctl --user -u diallux-fix7-a-<P1> | grep 'refused stale'` MUST show
   `prewarm: refused stale stt (age > 120s)`; driver json shows a normal arc; NO
   `stt:zombie_reconnect` span (watchdog idle on a healthy call); call continues.
6. If booking created → CANCEL (see driver json / trace tools for `create_livecall_booking`).
Verification: refused-stale line + normal call + zero reconnect spans. Unblocks: T2.

### T2 — Scenario B: mid-call zombie kill → watchdog reconnect (the money shot)
Goal: caller audio flowing + dead STT socket → `stt:zombie_reconnect` span ≤15s → transparent
reconnect → turns continue; no mute; no false fires on healthy turns.
Files: none changed.
Commands (OREGON, full):
1. Kill any lane from T1; boot a FRESH lane on port P2 (same script, `--unit=diallux-fix7-b-<P2>`).
2. Launch the frozen driver (PORT=P2) in BACKGROUND on OREGON:
   `ssh ... "cd /tmp/opencode/wt-iter83a/engine/scripts && set -a && . ../.env && set +a && nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python llm_mic_caller.py <frozen flags> --out /tmp/opencode/t4_fix7_b.json > /tmp/opencode/t4_fix7_b.log 2>&1 &"`
   (copy the exact flag set from `/tmp/opencode/run_driver_t4.sh`, PORT→P2).
3. Wait until the call is mid-arc (first Discovery transition in `journalctl --user -u diallux-fix7-b-<P2>`),
   then KILL the STT websocket externally WITHOUT touching the engine: find the lane's established
   connections to Deepgram: `ss -tnp | grep 731819-STYLE 'pid=<lane pid>'` → identify the flux socket
   (dst 443 / deepgram domain via `ss -tnp state established`), then `kill -9 <ss fd target>` is NOT
   possible for TCP alone — use the deterministic lever: `ss -K dst <deepgram-ip>` (kernel socket kill,
   needs root — OREGON ssh is root). Alternative (equally external): `nsenter`/`gdb` NOT needed;
   `ss -K` is the standard tool. Record kill timestamp T_kill.
   IMPORTANT: only kill the socket to api.deepgram.com; NEVER the Twilio/browser ws or Cartesia.
4. Watch the lane journal: within ≤15s expect
   `stt zombie suspected: no frames for Xs (mic chunks=N) - forcing reconnect` then the existing
   `deepgram dropped mid-call; reconnecting` line; call continues (mic audio keeps flowing).
5. Driver json: turns continue past the event (no wedge, no mute gap >15s); compare turn reports
   `e2e_response_ms` before/after the event (no regression).
6. Langfuse: `lf.py traces --name micbridge --limit 2` → find trace; `stt:zombie_reconnect` span with
   metadata silent_s ≈ 15 (not less — proves no premature fire) + mic_chunks > 0.
7. Booking created → CANCEL. Kill the lane; verify port free.
Verification: journal warning + span ≤15s + turns continue + zero false fires elsewhere in the run.
Unblocks: T3.

### T3 — report + ledger + ear A/B request (30 min)
1. Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter83-t4-wave1/01_fix7_battery.md`:
   scenario A + B evidence (journal excerpts, trace ids, span timestamps, driver json paths), §11.1
   verdict row, teardown line ("lane(s) killed, ports verified 0 listeners"), booking-cancel status.
2. Import to ledger: `cd /tmp/opencode/wt-iter83a/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/live_sql.py import --window "<HH:MM-HH:MM>" --run fix7-battery --commit fa62162`.
3. Copy the driver json into the surgeon folder.
4. Update master plan STATUS (session close ritual) + commit docs straight to main.
5. ASK owner for the ear A/B (knob on/off) — HITL gate before declaring FIX 7 done and moving to FIX 5.

## Validation Plan (end-to-end)
Scenario A pass (refusal + fresh connect) → Scenario B pass (zombie span ≤15s + continuation + zero
false fires) → ledger import → owner ear A/B → HITL (owner decides merge readiness) → FIX 5 next
(plan `plan_v5_iter83_t4_wave1_engine_fixes.md` T2). Abort: `STT_RX_ZOMBIE_MS=0` + `STT_ADOPT_MAX_AGE_S=0`
on the lane env = byte-exact off behavior (§8.6 rollback).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| FIX 5 battery (POST_INTERRUPT_BACKOFF_MS=500 owner value) | next loop after FIX 7 HITL |
| FIX 8 battery (SOFT_FILLER_MS=3000 + redundancy check vs existing prompt filler words) | wave-1 order |
| Arc-bloat fix (duplicate caller turns / turn-cap margin) | driver FROZEN — ledger note, owner decision |
| Suite debt (7 stale reds) | separate owner decision, not wave-1 |
