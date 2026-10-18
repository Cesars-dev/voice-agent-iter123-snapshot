# iter96c — the loop-tax probe: size and name the ~250–350 ms mic-path overhead (zero behavior change)

## Meta
- Date: 2026-10-07
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE code variable — add asyncio event-loop-lag measurement beside the engine `ttft=` metric, run it on FI + OR lanes, and either (a) convict the loop contention as the chat→mic TTFT gap (~728→~950-1065 ms) and name the culprit callback, or (b) acquit it and point the hunt elsewhere. NO behavior change: probe only logs.
- Status: PLAN ONLY (not started — awaits owner go)

## Compaction Context (everything that matters, imported)

### Where the work stands (2026-10-07)
- Repo: `/home/julio/projects/clean_diallux_SDR` (FINLAND box). main = origin/main = OR main @ **`314c13a`** (SYNCED: iter96b plan + ENV-SWITCHES registry + PT-85 row; commits `d09aa10`, `314c13a`, `726bc77` are docs-only on main).
- iter93+94+95 = MERGED to main (merge commit `eb54217`, tags `engine/iter93|94|95` on OREGON), **live-validated on the owner's real Twilio call** (trace `152d98c0c8d73f27680d950f2914e1bb`, 2026-10-06) — that call is the latency BASELINE for everything after.
- **iter96 (`b81b382`, branch `engine/iter96-delta-cache-layout`) = PARKED, UNMERGED, DO NOT STACK ON IT.** Synthetic A/B passed; real-Twilio verdict (PT-85) awaits owner firing a call at parked OR lane :8063 (`wt-96`). 96b forensics verdict: latency gain honest ≈ **−0…20 ms** (the fix is a token-COST win, sold as a latency lever — root cause: uncached-prefill slope is 8–22 ms per 1,000 tokens, R²≈0; a ~730 ms model/API first-token floor dominates). Owner priority: LOW. The lane runs from the branch — `:8063` untouched all session.
- THE YARDSTICKS (96b forensics, `research/surgeon/iter96-delta-cache-layout/96b_ttft_forensics.md`): chat-path TTFT p50 **728 ms** (43 llm2llm traces, Langfuse FI, Sep-24..Oct-2; ~650 ms on a US box idle run); mic-path engine ttft p50 **900–1,065 ms** (OR/FI journals). Gap ≈ **250–350 ms**, hypothesized = single-threaded asyncio event-loop contention (STT WS frames in, TTS streaming out, per-frame base64/mulaw work) delaying pickup of the first LLM stream event. **Hypothesis NOT yet proven — this plan proves or acquits it.**
- Engine `ttft=` definition (pinned): t0 = `perf_counter()` right before `runtime.llm.astream(...)` (`/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py:2404`); anchor = FIRST stream event of any type (`builder.py:2439`); logged in the round-usage line `builder.py:2573`. ttft includes prefill+queue+first-token+network; EXCLUDES STT/EOT/dispatch.
- OR test lanes `:8049`/`:8050` run from `wt-9494` (`test/iter93-94-95` @ `9eb341c`, TEST-ONLY mirror — same engine code as main@iter95, docs stripped). Keep running; they are the owner's Twilio voicetest targets until re-pointed.
- Owner's real goal: **e2e_turn p50 ≤ 1,200 ms** (today ≈ 1,882). With a ~730 ms TTFT floor, the reachable levers are the loop tax, STT finalize (Deepgram EOT knobs — owner-set), TTS TTFB, playback accel.
- Owner is running a DEEP RESEARCH (dual-model "fast mouth gpt-4.1 / smart hands gpt-5.4" architecture = future iter97; repo published for it: https://github.com/Cesars-dev/diallux-sdr-v5-engine-research). iter97 design BLOCKED on those results — NOT in this plan.
- Deep-research prompt saved at `/home/julio/projects/clean_diallux_SDR` chat + `/tmp/opencode/iter96b/deep_research_prompt.md` (also pushed to the public repo as `RESEARCH_QUESTIONS.md`).

### Resolved decisions (carried, DO NOT revisit)
- One-variable law; branch ceremony; OREGON transport = git push/pull only (never rsync); `delta_tokens` meaning unchanged; model stays gpt-5.4 (MODEL LAW); voices = Sarah for tests; `.env` values owner-set only; switch register = `docs/Testing_guidelines/ENV-SWITCHES.md`; nothing merges without owner say-so (LAW 0).

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| iter96 real-Twilio verdict (PT-85) → merge decision | owner fires the call at parked lane :8063; NOT this session |
| iter97 (dual-model) design | owner's deep-research results (external); NOT this session |
| Deepgram EOT knob values | owner call (biggest STT-side lever, out of agent hands) |

## Environment & Dependencies
- FINLAND = this box; engine venv `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`.
- OREGON: `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — repo `/home/julio/projects/clean_diallux_SDR` there; lane opener `scripts/new_lane.sh <iterNN> <base-sha-or-branch> <slug>` (run from repo root on OREGON; it creates worktree `/tmp/opencode/wt-<iterNN>` + symlinks canonical venv + generates `.env` from canonical + audit gate).
- Suite: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q` — current expected: **516 passed / 1 skipped / 5 failed** (pre-existing reds, identical on main tip).
- Langfuse FI: `cd /home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5 && python3 scripts/lf.py health|traces|show|gens` (keys in its `.env`; ingest quirk: `lf.py health` may say NO RECENT TRACES while traces still ingest — verify with a 48h trace scan before trusting absence).
- Python 3.12 asyncio debug surface: `loop.set_debug(True)` + `loop.slow_callback_duration = X` makes asyncio LOG every callback exceeding X seconds with traceback (`Executing <Task...> took X.XX seconds`) — zero behavior change, the culprit-finder.
- Ports: FI lane probe = `:8021` (free; `:8020` was the iter96 FI lane port, idle). OREGON iter96c lane = `:8065` (free; `:8063`/`:8064` parked/A-B history, `:8049`/`:8050` = owner's live voicetest lanes). NEVER touch 8001–8003 (live ORIGINAL services), 8080 (Caddy), OR service ports.

## Architecture (what the probe measures)
```
one asyncio loop per session (FI/OR lane):
  [deepgram WS frames in] [TTS stream out + base64/mulaw] [OTEL spans] [warm tasks]
        ── all compete for loop turns ──▶ graph task waits to PICK UP the first
                                            astream event (already arrived!)
  watchdog task: sleep(0.02) → measure overshoot = loop hold time since last turn
  per-round line: lag measured in the ttft window (t0 → first event)
  asyncio debug mode: slow_callback_duration=0.05 → NAMES the callback that held the loop
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | +2 Settings fields: `loop_lag_probe: bool = True` (default ON = tested value, SWITCH LAW rule 4), `loop_lag_slow_ms: float = 50.0` | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | watchdog task: when `loop_lag_probe`, start one per-session task that loops `await asyncio.sleep(0.02)`, computes overshoot vs target, keeps max-overshoot-since-last-emission; on ≥2× threshold or every ~5 s emit `log.info("loop lag: sid=%s max_over=Xms threshold=20ms")`; cancel on session close. Enable `loop.set_debug(True)` + `loop.slow_callback_duration=0.05` when probe on (log-only) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | round-usage line EXTENSION ONLY: add `loop_lag=Xms` (max overshoot recorded during the ttft window; reuses session watchdog's shared counter via runtime) — appended to the existing line at :2573, no format break (call_forensics regex must still match: add field at END of line) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter96c_loop_lag_probe.py` | NEW: watchdog overshoot math (fake clock), round-line still parses, switch-off = no task | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-loop-lag-probe/96c_report.md` | NEW: lag stats per box, slow-callback offender table, ttft-vs-lag correlation, verdict | NEW (research/, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/engine/scripts/call_forensics.py` | +regex group for trailing `loop_lag=(\d+)` field (optional group — backward compatible) | EDIT |
| engine behavior | NOTHING beyond logging | — |

## Deploy Rules
- No prod deploys. OREGON lane = `scripts/new_lane.sh iter96c 314c13a loop-lag-probe` (repo root, OREGON), then boot uvicorn from `/tmp/opencode/wt-iter96c/engine` with `HTTP_PORT=8065` foreground + pid file `/tmp/opencode/voice_8065.pid` (reuse the `lane-8049.log` boot pattern; notify owner before touching any running lane state).
- NEVER touch: `:8001-8003` (live ORIGINAL), `:8080` Caddy, parked `:8063` (wt-96/iter96), owner's `:8049`/`:8050` voicetest lanes, prod agents, `.env` values.
- FI probe lane `:8021` same pattern, foreground uvicorn, pid `/tmp/opencode/voice_8021.pid`.

## Tasks (in order)
### T0 — Cut the branch
Goal: `engine/iter96c-loop-lag-probe` from main tip `314c13a` (NEVER from iter96 — parked).
Commands: `cd /home/julio/projects/clean_diallux_SDR && git switch -c engine/iter96c-loop-lag-probe 314c13a`
Verification: `git merge-base HEAD main` → `314c13a`.

### T1 — Probe code (the ONE variable)
Goal: config fields + session watchdog + round-line extension + call_forensics regex + test, exactly per File Map.
Files: as mapped above.
Commands: implement; then `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests/test_iter96c_loop_lag_probe.py -q` then full `pytest tests -q`.
Verification: suite = **516/1/5 + new tests green** (no new reds; count shifts only by the new file's test count).

### T2 — OREGON lane battery
Goal: probe under realistic phone-path load.
Commands:
```
ssh ... root@5.78.83.174 "cd /home/julio/projects/clean_diallux_SDR && git pull origin main && git pull origin engine/iter96c-loop-lag-probe && scripts/new_lane.sh iter96c 314c13a loop-lag-probe"
# boot lane :8065 per lane law; then the mic-ws driver battery (Danny full arc) — same driver/journal shape as iter96 A/B (journals to /tmp/opencode/iter96c_or.json)
```
Verification: journal has ≥20 rounds, every round line carries `loop_lag=`; resolved-switch snapshot recorded next to evidence (ENV-SWITCHES §2 command).

### T3 — FI lane battery
Goal: same probe on the LOADED box (expect visibly worse lag — that's the FI-vs-OR p90 story).
Commands: FI lane `:8021`, scripted llm_mic happy path (same shape as `/tmp/opencode/iter96_baseline_happy.json` runs) → `/tmp/opencode/iter96c_fi.json`.
Verification: ≥14 rounds with `loop_lag=`; resolved-switch snapshot recorded.

### T4 — Forensics: convict or acquit the loop tax
Goal: per box: lag p50/p90/max; correlation lag↔ttft (same round); slow-callback offender table (top 10 named tasks); the decomposition table chat-728 → mic-XXX: how much of the gap is lag?
Verification: verdict line in `96c_report.md`: "loop tax = X ms (p50) / Y ms (p90); offenders = [task names]" — plus CONFIRMED/REFUTED for the 250–350 ms hypothesis.

### T5 — Write-up + LAW 0 closeout
Goal: append verdict to `96_report.md` (append-only); PT-86 row in `plans/PENDING_TASKS.md` with the named fix candidate (chunking / to_thread / side-loop — chosen by T4 evidence); commit docs to main; ASK JULIO.
Verification: registry refresh ritual (call_ledger.py rebuild from MAIN checkout engine/ dir, backup ledger.db first); git log shows docs commit on main.

## Validation Plan (end-to-end)
- Branch diff = File Map exactly (no behavior change: probe + logging only).
- Suite green vs 516/1/5 baseline (+new probe tests).
- Both boxes' journals carry `loop_lag=` on every round.
- 96c_report.md answers: gap 728→950 decomposed; named offender(s); CONFIRMED/REFUTED.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter96 merge / its Twilio verdict | PT-85 — owner-gated, parked until owner tests at :8063 |
| iter97 dual-model (gpt-4.1 mouth / gpt-5.4 hands) | BLOCKED on owner's deep-research results |
| Deepgram EOT knob changes | owner-set values (biggest STT-side lever, separate) |
| The actual loop-tax FIX (once T4 names it) | next branch after this probe's verdict — one variable at a time |
