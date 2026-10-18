# iter98 — service_tier: the measured cut + iter97 ledger synthesis (analysis session)

## Meta
- Date: 2026-10-08
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: (1) synthesize the iter97 checkpoint + iter96 evidence, (2) EDIT the executed master
  plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md` to
  reflect what actually ran, (3) cut + land `engine/98-service-tier` (the owner-ratified
  "kwarg" branch: `OPENAI_SERVICE_TIER=fast` behind a byte-parity-safe knob) with probe + A/B.
- Status: EXECUTED (2026-10-08, via the iter99 long-session GO): branch `engine/98-service-tier` @ `abbd9d8` (+ledger line `b06a8c0`) — B1 knob (byte-parity pinned, suite 526/1/5), B2 probe "fast" ACCEPTED (paired p50 1124→856.5), B3 same-lane A/B n=42+42 on OR :8066: dispatch→first p50 −378.5 ms = KEEP GATE PASSED 3.8× (tier=fast stays on lane env, code default ""). STOP branch not triggered. Report: research/surgeon/iter98-service-tier/98_report.md. Merges = owner say-so (LAW 0).
- Input artifacts the session MUST read first:
  1. `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/97_checkpoint_report.md` — today's checkpoint report (why nothing "failed", Langfuse pointers, T1 decomposition, D1/D2 fixes, Langfuse latency audit)
  2. `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-delta-cache-layout/96_report.md` — iter96's measured reality (mic A/B −39/−78 ms p50; phone-path −200–260 was a MODEL estimate, never measured)
  3. `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md` — the executed master plan (TO BE EDITED in T3 below)

## Compaction Context

### Where the mission stands (2026-10-08, after the iter97 execution session)
Goal unchanged: **e2e_turn p50 ≤ 1,200 ms on real telephony** (owner metric; last real call = 1,882 ms p50).
- **T0 done**: baseline n=73 real mic turns on FI lane :8021 (`research/surgeon/iter97-implementation/baseline_mic/t0_final_reports.tsv`): `stt_eot_to_llm_first` p50 1,533 / `e2e_response` p50 1,714 / `e2e_turn` p50 2,022. Suite red set: FI = **510 passed / 1 skipped / 5 failed** (516 collected; the 5 reds: `tests/test_iter48_rag_truth.py::test_eot_and_midturn_entry_awaits_split_caps`, `::test_lite_round_awaits_lite_warm`, `::test_await_warm_none_uses_midturn_flag_and_shield`, `tests/test_iter55_observability.py::test_await_warm_timeout_keeps_warm_alive`, `tests/test_iter65_dv_carryover.py::test_validator_parity_daily_case`). The plan's "516 passed" was the OR-box count; FI collects fewer. No real Cal.com bookings were created today.
- **T1 done (commit `68e5f3c`)**: clock truth instrumented (TurnClock `t_llm_dispatch`/`t_llm_first_event` + 3 report keys; builder `writer({"llm_dispatch"})` at dispatch + `writer({"llm_first_event"})` at first SDK event; session first-only stamps; 2 new Prometheus histograms + `diallux_media_lane_dropped_total` counter + `diallux_twilio_chunk_interarrival_ms`). 5 pins in `/tmp/opencode/wt-97/engine/tests/test_iter97_clock_dispatch.py`.
- **⟙ STOP CHECKPOINT FIRED, verdict recorded**: `stt_eot_to_llm_dispatch_ms` p50 = **70 ms** (< 100 ms threshold) ⇒ the loop-contention thesis (that fix 1/T3 would recover 250–350 ms) is **DEAD at this anchor**. T3 media-frame-lane was NOT built. The adder lives in the OpenAI request itself.
- **D1 (commit `2943d88`)**: mic-caller `ConnectionClosedOK` crash fixed (server-side end_call close = normal end-of-call; evidence json always lands). **D2 (commit `6044b9f`)**: call-end Langfuse tail-confirm moved off the event loop (`_finish_tracer_off_loop` + 2 pins in `engine/tests/test_iter97_d2_offloop_finish.py`) — `session.stop()` used to run sync urllib polls + `time.sleep(5)` ON the loop (up to ~60 s at call end, froze other calls; the 08:51–08:53 handshake-hang window on FI :8021).
- **Owner verdicts today (2026-10-08, on record)**: (a) iter96 "saves nothing" on the mic endpoint — owner is right and the new data sharpens WHY: cache-hot rounds measured TTFT p50 1,159 ms vs cache-cold 1,154 ms (**186, contrast irrelevant**: 38/40 rounds were cache-hot with 100% prefix read, mid-call misses 0, only turn-1 rounds are cold by construction). The fat re-shipped delta's ~100–200 ms prefill is buried under the **~1.15 s API processing floor that is identical hot or cold at default tier.** (b) T4 raw-SDK speak path = **DEAD** by the plan's own rule: lane `llm_dispatch_to_first_event_ms` p50 1,208 ≈ raw-API default-tier TTFT on the same payloads (session-1 cURL evidence: 1.18–1.81 s). (c) The one PROVEN lever for the dominant segment = `service_tier=fast` (session-1, measured from OREGON: TTFT 1.18–1.94 s → 0.72–0.97 s uncached; 0.78 s vs 1.18–1.81 s on a 5,888-token cached prefix; cross-tier cache-read preserved 5,888/5,888; ~2x token price; variance sheet 1.12 s → 0.29 s). TTS flash/turbo bake-off rejected earlier. fast_first_flush stays OFF (PT-71).
- **Branch state**: `engine/97-implementation` @ `6044b9f` = `61bfc7e` + D1 + T1 + D2 (4 commits on the branch incl. base chain). Worktrees: FI `/tmp/opencode/wt-97` (lane :8021), OR `/tmp/opencode/wt-97` (lane :8065; booted, health OK, ssh root@5.78.83.174 `-i /home/julio/.ssh/id_ed25519_hetznor`). Suite on branch tip: **517 passed / 1 skipped / 5 failed** (identical red set). NO merges — LAW 0; iter97 merge = owner say-so, pending.
- **T2 honesty fact**: lanes ALREADY run uvloop (uvicorn[standard] auto-selects; native stack seen in py-spy: `uv__io_poll`/`uv_run`). T2 = pin + `/health` proof only, zero gain available.
- **Measured mic-path budget (FI, T1 live, n=27 deep persona arcs)**: `stt_eot_to_llm_dispatch` p50 70 / `llm_dispatch_to_first_event` p50 1,208 / `llm_first_event_to_llm_first` p50 538 (tool-first rounds delay the spoken token) / `llm_first_to_tts_first` p50 174 / `e2e_response` p50 1,901.

### Langfuse trace map — today's mic runs (ALL pointable, FI Langfuse self-hosted, project `pk-lf-bba5…`)
Pull any of these with (run from `/home/julio/projects/clean_diallux_SDR/engine` — NOTE: the FI `engine/.env` is the canonical env; any lane worktree env works too):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python scripts/lf.py traces --name micbridge --hours 8
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python scripts/lf.py show <trace_id>
cd /tmp/opencode/wt-97/engine && .venv/bin/python scripts/lf.py show 88e33dae89a4   # same CLI inside the lane
```
| time | trace id | sid | shape | json on disk (via /tmp/opencode/) |
|---|---|---|---|---|
| 08:46 | `75da2dce086e` | `63a6abd5552d` | 3 gens, 8k in (scripted) | `iter97_baseline_mic_out.json` |
| 08:50 | `f87bed650a7c` | `5cd52d2c2a06` | 3 gens, 9k in (scripted) | `iter97_baseline_mic_out2.json` |
| 08:51 | `4b95d9ad3347` | `462d7ee0957f` | 2 gens, 5k in (run in the hang window) | `iter97_baseline_mic_out3.json` |
| 09:16 | `dab201451b97` | `014692f01f98` | 2 gens, 5k in (dbg) | `dbg_run1.json` |
| 09:23 | `e405675ef72c` | `9920639153ef` | 13 gens, 61k in (persona, Closer stall, max_run_s) | `iter97_persona_run1.json` |
| 09:31 | `88e33dae89a4` | `cea36e124f81` | 31 gens, 206k in (full classic arc → ConfirmSlots → Closing, clean `end_call`) | `iter97_persona_run2.json` |
| 09:41 | `75219a7a5e52` | `40a37ea8644e` | 34 gens, 233k in (ConfirmSlots → Closing) | `iter97_persona_run3.json` |
| 10:13 | `110fe70fdccd` | `88b8c0702f53` | 22 gens, 110k in (post-D1) | `iter97_t1_run1.json` |
| 10:17 | `1bfaf5cdcf81` | `d283e84c0b96` | 18 gens, 81k in (post-D1, T1 code live — clock keys present) | `iter97_t1_run2.json` |
Join rule: json `started_wall` (unix) ↔ trace start time; sid from the json `events` (`server_text` clear `"streamSid"` / start line) ↔ trace name `micbridge-<sid>`. Trace spans to read per turn: `warm:*` → `rag:fire`/`rag` → `eager_hold:fire` → `eot_silence_wait` → `await_warm` → **`generation llm:<State>`** (TTFT time) → `eager_hold:release` → `tts_first_byte` → `turn:N` → `turn:N:final`. Ground truth for what a run measured = lane journal `turn N final report:` lines: T0-era rows in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/baseline_mic/lane-8021.log`; T1-era rows in `/tmp/opencode/lane-8021.log` (REWRITTEN by reboots — do not confuse the two files).
Token ledger: ≈726k input / ~10k output today across the 9 traces. `lf.py costs --hours 8` 400s on the FI server version (works on OR) — use the traces listing for token math.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| iter98 branch = `engine/98-service-tier`, cut FROM `engine/97-implementation` tip (`6044b9f`) | owner directive (2026-10-08 plan): one cut per fix; supersede check unnecessary — nothing else rode the tip. Numeric lane opener: `scripts/new_lane.sh 98 engine/97-implementation service-tier`. |
| `OPENAI_SERVICE_TIER` tier string = `"fast"` (ex-Priority) | session-1 evidence measured under `priority`; B2 probe confirms `"fast"` accepted (no-400) before any lane flip. |
| Tier ride-along `model_kwargs` hoist keeps flag-off serialization BYTE-IDENTICAL | iter43 cache-disaster class; `llm.py` attaches `model_kwargs` only when non-empty — the byte-equality pin is a merge gate, not a nicety. |
| `llm_boot_prewarm` does NOT get the tier | 16 throwaway tokens at 2× price; cross-tier cache read is proven preserved. |
| T3 (media frame lane) NOT built; skip verdict recorded in the master-plan edit | T1 measured dispatch p50 70 ms; the 250–350 ms loop-adder hypothesis is dead. Sensors it would have carried are already merged (T1 histograms/counter). |
| T4 raw-SDK speak path = DEAD (eval verdict from data, no build) | lane 1,208 ms ≈ raw-API default-tier TTFT (session-1). Rule satisfied: within ~50 ms p50 ⇒ DEAD. |
| iter96 is NOT resurrected for the mic endpoint | owner verdict + today's hot==cold measurement: its saving is buried under the ~1.15 s tier floor. Phone-path verdict (PT-85) stays parked owner-gated; do not re-litigate without owner. |
| A/B gates respect the FI-slower reality: prove on FI lane :8021 (same-box A/B vs T0), confirm on OR | owner workflow: build/dry-test FI, batteries OR. |
| GK stress personas at the END, one at a time, cancel every booking | owner endorsement 2026-10-08; ritual: book → capture validator uid → cancel via `/tmp/opencode/cancel_test_booking.py` pattern (cal.com v2, `cal-api-version: 2024-08-13`). |
| `.env` values owner-set only; agents never edit `.env` | LANE LAW. The B3 flip sets `OPENAI_SERVICE_TIER=fast` in the LANE `.env` copy = owner order (this plan IS the order once owner GOs the plan). |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO on this plan (surgeon step 5) | owner reads this file |
| Exact gpt-5.4 fast-tier pricing | OpenAI pricing page at implementation time; record `lf.py costs` delta in the report |
| iter97 merge say-so (D1/T1/D2 into main) | owner — iter98 would then rebase cleanly; until then iter98 rides on the branch chain |
| Real-Twilio phone-path verdict | owner fires the call (PT-85 class, unchanged) |

## Environment & Dependencies
- FI repo: `/home/julio/projects/clean_diallux_SDR` (checkout currently parked on branch `engine/iter97-research-adaptation`, clean tree). Lane: `/tmp/opencode/wt-97` @ `engine/97-implementation` @ `6044b9f`, venv symlink to canonical, port **8021**, log `/tmp/opencode/lane-8021.log`.
- OR (work box): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — repo `/home/julio/projects/clean_diallux_SDR`; lane `/tmp/opencode/wt-97` @ `:8065`. Transport FI↔OR = git push/pull ONLY (never rsync).
- Python: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (3.12). Suite: `cd /tmp/opencode/wt-97/engine && .venv/bin/python -m pytest tests` → expect **517 passed / 1 skipped / 5 failed** (red set = the 5 named tests above).
- Fast suite: `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` (cwd MUST be a repo engine dir), args: node-ids | `--touched` | `--full`.
- Lane opener (on OR, repo root): `bash scripts/new_lane.sh <NN> <base> <slug>`; `bash scripts/new_lane.sh --list` = inventory. Exit 1 = DOA.
- Mic driver: `/tmp/opencode/wt-97/engine/scripts/llm_mic_caller.py` (D1-fixed). `--journal-log` flag is DEAD (audit F7) — do not pass it; evidence = lane journal + `--out` json.
- Secrets: workspace `.env` files (gitignored). `VOICE_TEST_TOKEN` sits in the lane `.env` (sourced before boot).
- Ports NEVER touched: FI `:8000–8003` (original live), `:8020`, `:8080` Caddy; OR `:8049/:8050` (wt-9494), `:8063` (wt-96). iter98 OR lane = `:8066`; FI dry-run lane = `:8081` (8021 stays iter97).
- Langfuse: FI self-hosted; `lf.py` in every engine dir (`/home/julio/projects/clean_diallux_SDR/engine/scripts/lf.py`).

## Architecture
```
engine/97-implementation @ 6044b9f  (DONE pending merge)
   └─ engine/98-service-tier (cut from the tip, lane wt-98)
        B1  openai_service_tier knob (hoisted mk, byte-parity pinned) + /health field
        B2  llm_tier_probe.py: "fast" accepted (no-400) + ≥10 paired TTFT default vs fast
        B3  lane flip OPENAI_SERVICE_TIER=fast → A/B ≥50 turns: keep gate p50 −100ms + costs delta
        T5' docs: ENV-SWITCHES register + iter98 report + master-plan ledger
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md` | T3 of THIS plan: status line → executed; T0/T1 DONE + checkpoint verdict + numbers; T2 honesty (already-uvloop); T3 SKIPPED (premise dead, sensor already merged); T4-eval DEAD verdict; D1/D2 debug commits recorded; iter98 pointer | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter98_service_tier_synthesis.md` | this plan (commit to main now) | NEW (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | `openai_service_tier: str = ""` (LLM section, after `openai_verbosity`) | EDIT (B1) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py` | hoist `mk` for ALL models + `mk["service_tier"]` when non-empty; verbosity twins same; `_warm_llm` inherits; boot prewarm NOT tiered; attach `model_kwargs` only when non-empty (byte-parity) | EDIT (B1) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py` | `/health` `"service_tier"` field | EDIT (B1) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter98_service_tier.py` | tier pins + **byte-equality pin** (serialized kwargs with `""` == pre-change bytes) | NEW (B1) |
| `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_tier_probe.py` | standalone tier probe (stdlib+openai only, zero engine imports; ≥10 paired streaming TTFT default vs `service_tier="fast"` on gpt-5.4; prints no-400 + delta) | NEW (B2) |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | register `OPENAI_SERVICE_TIER` (what/where/values/price note) | EDIT (B1) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter98-service-tier/98_report.md` | probe + A/B + costs + verdict | NEW (evidence, gitignored) |

## Deploy Rules
- FI lane boot (dry-run, iter98 content, port 8081): worktree `/tmp/opencode/wt-98` after `bash scripts/new_lane.sh` equivalent on FI (`REPO=/home/julio/projects/clean_diallux_SDR TMP=/tmp/opencode bash scripts/new_lane.sh 98 engine/97-implementation service-tier`) → `cd /tmp/opencode/wt-98/engine && set -a && . ./.env && set +a && (setsid .venv/bin/uvicorn diallux.app:app --host 127.0.0.1 --port 8081 > /tmp/opencode/lane-8081.log 2>&1 < /dev/null &)` → `curl -s localhost:8081/health` must show `"service_tier"`.
- OR lane boot (real A/B, port 8066): `bash scripts/new_lane.sh 98 engine/97-implementation service-tier` on OR after pulling the branch; same boot pattern with port 8066.
- B3 flip: edit **lane** `.env` only (`/tmp/opencode/wt-98/engine/.env`, add `OPENAI_SERVICE_TIER=fast`), restart the 8066 uvicorn; bump tier OFF = delete the line (code default `""`).
- NEVER touch: protected `engine/iter73-oregon-wip-20260924` + OR main checkout, lanes `:8049/:8050/:8063/:8065`, FI services `:8000–8003`, `:8020`, `:8021` (iter97 lane stays parked for comparison), `:8080` Caddy, prod agents, `.env` canonical values. `scripts/keyhound` before every push. Commit registry refresh at session end from the MAIN checkout's `engine/` dir (backup `research/surgeon/iter47-call-ledger/ledger.db` first).

## Tasks (in order)

### T1 — Synthesis read (30 min, no edits)
Goal: a fresh agent absorbs the three input artifacts (paths in Meta) + verifies live state.
Commands:
```bash
cd /home/julio/projects/clean_diallux_SDR && git -C . log --oneline -3 engine/97-implementation
curl -s --max-time 5 localhost:8021/health   # FI iter97 lane still parked (may be down — fine, unit work does not need it)
ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'curl -s --max-time 5 localhost:8065/health | head -c 200'
```
Verification: state summary in one paragraph of the session report (branch tip == `6044b9f`, lane states health).

### T2 — Trace verification pass (read-only, Langfuse)
Goal: confirm the 9 micbridge traces above are present + spot-check one per era (T0-era `88e33dae89a4` 31 gens; T1-era `1bfaf5cdcf81` 18 gens).
Commands: the `lf.py traces --name micbridge --hours 8` + `lf.py show <id>` blocks in Compaction Context.
Verification: trace listing contains all 9 ids; the chosen T1-era trace's gen metadata carries round ttft values that match the journal `round usage:` lines of the same window (±5%).

### T3 — Master-plan edit + docs commit (the file the owner pointed at)
Goal: make `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md` tell the truth about what executed.
Exact edits (do these, nothing speculative):
1. `Status:` line → `EXECUTED THROUGH T1 + STOP CHECKPOINT; T2/T3 skipped by verdict; T4-eval DEAD; iter98 = follow-on plan (plan_v5_iter98_service_tier_synthesis.md)`.
2. Tasks section: T0 DONE (n=73 baseline, red set FI 510/1/5, no bookings); T1 DONE (`68e5f3c`) with the decomposition table + checkpoint fired (dispatch p50 70 < 100 → STOP); T2/T3 SKIPPED-VERDICT lines (T2: lanes already uvloop, pin pending; T3: premise dead, sensors merged in T1); T4-EVAL DEAD (lane 1,208 ≈ raw 1,180–1,810 default tier).
3. Architecture block: annotate T3 as skipped + iter98 cut point = `6044b9f`.
4. Add a `2026-10-08 debug commits` line: D1 `2943d88` (caller, owner-authorized), D2 `6044b9f` (langfuse off-loop) + the blocker they killed (call-end loop freeze, handshake hang 08:51–08:53).
Commit pattern (docs straight to main, LAW 0): create a docs worktree because the FI checkout is parked on `engine/iter97-research-adaptation`:
```bash
cd /home/julio/projects/clean_diallux_SDR
git worktree add /tmp/opencode/wt-main-docs-fi main -f || git -C /tmp/opencode/wt-main-docs-fi pull --ff-only
cp /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md /tmp/opencode/wt-main-docs-fi/plans/
cp /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter98_service_tier_synthesis.md /tmp/opencode/wt-main-docs-fi/plans/
cd /tmp/opencode/wt-main-docs-fi && git add plans/ && bash /home/julio/projects/clean_diallux_SDR/scripts/keyhound --staged && git commit -m "iter97/iter98 docs: master plan updated to executed reality (T1 done, checkpoint fired, T3 skip, T4 DEAD) + iter98 synthesis plan" && git push origin main
```
Verification: `git -C /home/julio/projects/clean_diallux_SDR log --oneline -1 origin/main` shows the docs commit; the parked checkout keeps its untracked working copies (already on disk) — do NOT edit `engine/diallux/**` here (whitelist lane only allows this script + tests; the master plan is a plans/ doc).

### T4 — iter98 B1: the knob (branch `engine/98-service-tier`)
Goal: `openai_service_tier` Settings knob, wired via the hoisted mk, byte-parity pinned, OFF by default.
Files: config.py, llm.py, app.py, docs ENV-SWITCHES, tests (File Map).
Mechanics: cut the branch ON OR (`bash scripts/new_lane.sh 98 engine/97-implementation service-tier` after pushing the iter97 branch tip from FI), but AUTHOR the edits in the FI lane worktree (zeropull workflow: FI author → commit → push → OR pull in `/tmp/opencode/wt-98`): `cd /tmp/opencode/wt-98 && git checkout engine/98-service-tier` (the lane opener already created the branch on OR; FI creates worktree `git worktree add /tmp/opencode/wt-98 engine/98-service-tier` after fetching it, or cut the branch locally first and push — EITHER PATH, never rsync).
Code shape (from the ratified owner plan, verbatim intent): hoist the shared `model_kwargs` dict for ALL models (currently gated per-model at `llm.py:237–238` — attach only when non-empty), then `if settings.openai_service_tier: mk["service_tier"] = settings.openai_service_tier` ahead of serialization; `llm_for_verbosity` twins get the same; `_warm_llm` inherits; `llm_boot_prewarm` does NOT get the tier; `/health` gains `"service_tier"`.
Verification: `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh tests/test_iter98_service_tier.py tests/test_iter44_prewarm_bytes.py tests/test_iter65_boot_prewarm.py` green (byte-equality pin included); full suite identical red set (517/1/5 FI baseline + new pins).

### T5 — iter98 B2: tier probe
Goal: prove the API accepts `"fast"` on gpt-5.4 and measure paired TTFT delta.
File: `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_tier_probe.py` (stdlib + `openai` only, zero engine imports, reads `/home/julio/projects/clean_diallux_SDR/engine/.env` for the key; ≥10 paired streaming requests, same ~6k-token payload shape as the hot path — build the payload ONCE, alternate default/fast per pair, report p50/p95 per tier + no-400 line).
Command: `cd /tmp/opencode/wt-98/engine && .venv/bin/python scripts/llm_tier_probe.py`
Verification: output to `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter98-service-tier/98_report.md`. If the API 400s `"fast"` → keep knob `""`, write the verdict, STOP (no B3).

### T6 — iter98 B3: lane A/B with the tier ON (means the 100 ms keep-gate)
Goal: same-lane proof that the flip is worth keeping.
Commands (OR): boot `/tmp/opencode/wt-98/engine` on :8066 with `OPENAI_SERVICE_TIER=fast` in the lane `.env`; run the driver:
```bash
ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'cd /tmp/opencode/wt-98/engine && set -a && . ./.env && set +a && .venv/bin/python scripts/llm_mic_caller.py --ws-url "ws://127.0.0.1:8066/mic/ws?k=$VOICE_TEST_TOKEN" --scenario happy --persona Maria --max-caller-turns 21 --max-run-s 420 --out /tmp/opencode/iter98_fast_run1.json'
```
≥50 turns total; same-lane default-tier A/B first (fresh lane, no tier line, ≥20 turns) — the keep gate is **`llm_dispatch_to_first_event_ms` p50 −100 ms minimum vs the same lane at default tier** (the T1 metric exists on both sides because it rides base `6044b9f`); also pull `lf.py costs --hours 4` (works on OR) for the token-price delta. FI dry-run equivalents on :8081 optional (port listed above).
Verification: numbers into `98_report.md`; pass → keep gate report to owner; miss → delete the tier line from the lane `.env`, report, STOP.

### T7 — Docs + ledger close
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter98-service-tier/98_report.md` (probe, A/B, costs, verdict, trace ids); ENV-SWITCHES register line; commit registry refresh from main checkout; ASK JULIO before any merge (LAW 0). GK stress battery belongs AFTER iter98 lands on a lane the owner blesses (that is this session's tail task, owner-endorsed 2026-10-08).

## Validation Plan (end-to-end)
1. Suite red set identical at every commit gate (FI 517/1/5 shape; new pins green via fast_suite node list).
2. Flag-off byte-parity pinned (B1 test) — `"service_tier"` absent from request kwargs when the knob is `""`.
3. A/B numbers from real turn reports, not estimates: default-tier lane vs `fast` lane, same box, same driver, ≥50 turns, keep gate = −100 ms p50 on `llm_dispatch_to_first_event_ms`.
4. All evidence in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter98-service-tier/` (gitignored) + trace ids recorded; bookings cancelled if any land.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter97 merge to main | owner say-so only (LAW 0); iter98 rides the branch chain meanwhile |
| iter96 merge (PT-85) | parked owner-gated; measured near-dead on mic; phone verdict is the owner's test |
| T3 media-frame-lane build | premise measured dead (dispatch p50 70 ms); sensors already merged |
| Tape-out of uvloop pin (T2) | lanes already run uvloop; pin it during the iter98 session only if there is spare scope — zero gain available |
| Deepgram EOT knob values | owner-owned, deferred (biggest user-perceived lever, outside measured window) |
| prompt-layer branch (strip RAG from hot states) | NEXT iteration after iter98 (the remaining local lever; new iter number at cut) |
