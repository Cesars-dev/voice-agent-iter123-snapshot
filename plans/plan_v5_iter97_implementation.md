# iter97 — loop hygiene (T1–T3 + T4-eval) and iter98 — service_tier: the measured latency cuts

## Meta
- Date: 2026-10-08
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: implement the owner-ratified latency fixes — iter97 = clock-truth instrumentation, uvloop pin+proof, media frame lane, then MEASURE (T4 raw-SDK = eval only); iter98 = `openai_service_tier` env knob cut from the tip of iter97. One branch per fix.
- Status: EXECUTED THROUGH T1 + STOP CHECKPOINT; T2/T3 skipped by verdict; T4-eval DEAD; iter98 = follow-on plan (plan_v5_iter98_service_tier_synthesis.md). Executed 2026-10-08; branch `engine/97-implementation` @ `6044b9f` (base `61bfc7e` → D1 `2943d88` → T1 `68e5f3c` → D2 `6044b9f`).

## Compaction Context

### What this is and where it stands
Dialux SDR v5 engine (LangGraph voice agent: Twilio mulaw WS → Deepgram flux STT → 9-state graph → gpt-5.4 via langchain ChatOpenAI → SentenceGate → ElevenLabs/Cartesia → Twilio). Owner goal: **e2e_turn p50 ≤ 1,200 ms on real telephony (today ≈ 1,882 ms)**. Measured decomposition (96b forensics, `research/surgeon/iter96-delta-cache-layout/96b_ttft_forensics.md`): chat-path TTFT p50 728 ms vs mic-path 900–1,065 ms — a **250–350 ms unexplained adder** hypothesized = asyncio loop contention (hypothesis NOT yet proven; T1 proves or acquits it). A ~730 ms model/API first-token floor dominates the rest.

### The evaluation that produced this plan
- Session-1 report `research/surgeon/iter97-research-adaptation/97_analysis.md` (six verdicts on the owner's research doc, all cURL-measured from OREGON). Key measured facts:
  - **service_tier (priority)**: TTFT 1.18–1.94 s → 0.72–0.97 s uncached; 0.78 s vs 1.18–1.81 s on a 5,888-token cached prefix; **cross-tier prompt-cache read preserved (5,888/5,888 cached_tokens)**; ~2x token price; variance collapse (spread 1.12 s → 0.29 s).
  - **TTS turbo vs flash**: warm TTFA wash (~255–270 vs ~275–315 ms) — latency claim dead; flash only wins cold-start + ~6x cost. Owner REJECTED the bake-off.
  - **fast_first_flush**: REJECT (PT-71 battery failure class).
  - **Loop-contention surface**: real — `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py:144–185` (inline Twilio frame parse+dispatch), `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:877–880` (inline astream consumption).
- Session-2 (this session) evaluated the owner's implementation prompt (`/home/julio/projects/vps-inbox/IDE_AGENT_PROMPT_latency_fixes_1_3 2.md`, verbatim copy `/tmp/opencode/iter97_owner_plan_source.md`, archived at `tasks/surgeon/iter97-implementation/archive/`) against that report. Owner verdicts 2026-10-08: **Fix 1 run T1–T3 then measure; Fix 2 approved (env knob, best proven gain); Fix 3 rejected (iter99 stale)**. Sequencing: heavy lifting (iter97) first, guaranteed win (iter98) second, cut from iter97's tip.
- Surgeon chain: `tasks/surgeon/iter97-implementation/{01_audit,02_action_plan,03_cross_reference,04_master_plan}.md` — all code anchors verified at **main @ `61bfc7e`** (both boxes synced this session).

### Repo state (2026-10-08, after housekeeping sync)
- main = origin/main = `61bfc7e` on BOTH boxes (FI `46.62.233.228` reference/develop, OR `5.78.83.174` work box). FI checkout parked on `engine/iter97-research-adaptation` @ `61bfc7e` (ff'd, clean).
- OR root checkout = PROTECTED `engine/iter73-oregon-wip-20260924` @ `61a88ff` (owner prod endpoints config — NEVER checkout/reset/pull there). OR docs worktree = `/tmp/opencode/wt-main-docs` @ main.
- Running lanes (NEVER touch): OR `:8049`/`:8050` (`wt-9494`, owner Twilio voicetests), OR `:8063` (`wt-96` parked, PT-85 pending). FI `:8000–8003` = ORIGINAL live services; `:8020` idle iter96 lane; `:8080` Caddy.
- Suite baseline: **516 passed / 1 skipped / 5 failed** (pre-existing reds, identical on main tip). Command: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q`.
- `2026-10-08 debug commits` (on `engine/97-implementation`): **D1 `2943d88`** — mic-caller `ConnectionClosedOK` crash fixed (server-side `end_call` close is a normal close; caller crashed before writing evidence json; owner-authorized debug commit); **D2 `6044b9f`** — call-end Langfuse tail-confirm moved off the event loop (`asyncio.to_thread`): `finish(wait=True)` ran sync urllib polls + `time.sleep(5)` inline and froze the loop up to ~60 s at call end — the blocker behind the 08:51–08:53 handshake-hang window on FI :8021. 2 pins each; suite red set identical at both commits (517/1/5 shape incl. the new pins).
- iter96 merge verdict (PT-85) = owner-gated, parked. iter96c loop-lag probe = **SUPERSEDED by this plan's T1** (better instrument: decomposition vs lag-overshoot); its reserved ports are reused here.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Branch per fix: `engine/97-implementation` (all loop-hygiene commits) → `engine/98-service-tier` cut FROM ITS TIP; NO iter99 | Owner directive 2026-10-08 (one cut per fix so we can go back). Supersedes both the earlier "everything rides one branch" reading and 97_analysis's `iter98-quick-wins`-from-main shape. Owner overrides LAW 0 v2.1 no-stacking clause for the 97→98 cut — on record. |
| Lane branch names are numeric (`engine/97-…`) | `scripts/new_lane.sh` numeric guard refuses `iter97`; precedent `engine/96-delta-cache-layout` @ `wt-96`. |
| Every behavioral change behind a pydantic Settings flag defaulting OFF (= byte-exact current behavior) | SWITCH LAW + owner prompt invariant. T1 (pure observability) exempt but adds keys only — never renames. |
| T4 (raw OpenAI SDK speak path) is NOT built in iter97 | Owner: prove worthiness from data first. Decision rule: lane `llm_dispatch_to_first_event_ms` vs raw-API TTFT on same payload — within ~50 ms p50 = DEAD; ≥150 ms sustained p50 delta = candidate for a future owner-gated phase. |
| `model_kwargs` byte-parity law on the mk hoist (iter98) | `llm.py:237–238` attaches model_kwargs only when non-empty; the hoist must keep flag-off serialization byte-identical (iter43 cache-disaster class). Byte-equality test is a gate. |
| `llm_boot_prewarm` does NOT get the tier | 16 throwaway tokens at 2x price = waste; cross-tier cache read preserved (measured), so warm-at-default → serve-at-fast is safe. |
| Suite gate = identical red set (516/1/5), not "all green" | 5 pre-existing reds on main tip; T0 records their exact names. |
| fast_first_flush stays False; TTS bake-off dead; mouth/brain deferred; warm knobs untouched | Owner + PT-71 + Voice LAW + 97_analysis #2/#5. |
| Tier string is `"fast"` (ex-Priority); evidence was measured under `"priority"` | Probe confirms acceptance before any lane flip (no-400 check). |
| `.env` values owner-set only; lane `.env` generated by `new_lane.sh` from canonical | LANE LAW. |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Real-Twilio phone-path A/B (mic lane gates first; phone verdict = owner fires a call at the lane) | Owner action, same class as PT-85 |
| `OPENAI_SERVICE_TIER=fast` on any prod surface | Owner-gated flip; test lane first |
| Exact gpt-5.4 fast-tier pricing (2x is the working figure) | OpenAI pricing page at implementation time; `lf.py costs` delta in the report |
| Owner GO on this plan (surgeon step 5) | Owner reads this file |

## Environment & Dependencies
- FI (develop box, this one): repo `/home/julio/projects/clean_diallux_SDR`; venv `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (Python 3.12, pytest 9.1.1).
- OR (work box): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — repo at `/home/julio/projects/clean_diallux_SDR`. Lanes live in `/tmp/opencode/wt-*`. Transport FI↔OR = git push/pull ONLY (never rsync).
- Lane opener (run on OR from repo root): `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <NN> <base> <slug>` — creates worktree + branch + venv symlink + audited `.env` from canonical; exit 1 = lane DOA, do not boot.
- Fast suite: `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` (run from `<repo>/engine`): `--touched` | `--full` | node-ids; this plan adds `--iter97` / `--iter98` groups.
- Probes: `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_mic_caller.py` (`--ws-url ws://…/mic/ws?k=<VOICE_TEST_TOKEN> --scenario happy --max-caller-turns N --journal-log <path>`), `/home/julio/projects/clean_diallux_SDR/engine/scripts/latency.py` (`--hours N --name <prefix> --json`).
- Ports: FI lane `:8021`; OR lane `:8065`. NEVER touch `:8000–8003`, `:8020`, `:8049`, `:8050`, `:8063`, `:8080`.
- Langfuse CLI: `cd /home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5 && python3 scripts/lf.py costs --hours 24`.
- Evidence dir: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/` (gitignored).
- Switch register: `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md`.
- Key files: `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/latency.py`, `…/observability/metrics.py`, `…/graph/builder.py`, `…/graph/llm.py`, `…/media/session.py`, `…/app.py`, `…/config.py`, `…/deploy/diallux.service`, `…/Dockerfile`, `…/requirements.txt`.

## Architecture
```
iter97 branch engine/97-implementation (lane wt-97, port 8065 OR / 8021 FI)
  T0  baseline: suite red-set snapshot + mic-bridge ≥50-turn capture + /health snapshot
  T1  clock truth (additive): TurnClock t_llm_dispatch/t_llm_first_event
        builder :2287 writer({"llm_dispatch"})  →  :2322 writer({"llm_first_event"})
        session :877 first-only stamps → report keys + bench_aliases + 2 histograms
        ⟙ STOP CHECKPOINT: stt_eot_to_llm_dispatch p50 <100ms ⇒ thesis revision, report
  T2  uvloop: requirements pin + --loop uvloop on service/Dockerfile/lane boots
        + /health "event_loop" proof (honest: may already be active)
  T3  media frame lane (flag OFF): sync enqueue_media (drop-oldest+counter)   ⟙ SKIPPED (dispatch p50 70 ms — premise dead, sensors already merged)
        + _media_drain task + /media & /mic/ws branch + Twilio interarrival stamp
        ⟙ A/B gate: dispatch p50≤150/p95≤250ms, interarrival p95≤65ms, dropped==0
  T4E eval only: lane dispatch→first vs raw-API TTFT ⇒ T4 DEAD or CANDIDATE   ⟙ DEAD (lane 1,208 ≈ raw 1,180–1,810 default tier)
        └─ report → ASK JULIO (LAW 0)
iter98 branch engine/98-service-tier (cut from engine/97-implementation tip ⟙ cut point = 6044b9f, lane wt-98)
  B1  openai_service_tier knob (hoisted mk, byte-parity pinned) + /health field
  B2  llm_tier_probe.py: "fast" accepted (no-400) + ≥10 paired TTFT
  B3  lane flip OPENAI_SERVICE_TIER=fast (owner-gated) → keep gate: p50 −100ms + costs delta
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/latency.py` | +2 TurnClock fields, +2 marks, +3 report keys | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | +2 writer events in the round loop (:2287/:2322 area) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | +first-only stamps (:877); +bench_aliases (:904); +iter97 media-lane section (class attrs, queue init, enqueue_media, _media_drain, spawn/cancel) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py` | /media + /mic/ws enqueue branch + Twilio interarrival stamp; _lifespan loop log; /health event_loop + service_tier fields | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/metrics.py` | +2 histograms, +Twilio interarrival, +drop counter, observe spans | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | +`# ---- iter97: loop hygiene ----` section (media_frame_lane=False, media_lane_queue_size=50); +`openai_service_tier: str = ""` (LLM section, iter98 branch) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py` | hoist mk (byte-parity law) + service_tier in main mk + verbosity twins (iter98 branch) | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/requirements.txt` | +`uvloop>=0.21` | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/deploy/diallux.service` | ExecStart + `--loop uvloop` | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/Dockerfile` | CMD + `--loop uvloop` | EDIT |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter97_clock_dispatch.py` | T1 pins | NEW |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter97_frame_lane.py` | T3 pins | NEW |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter98_service_tier.py` | tier pins + byte-equality | NEW |
| `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_tier_probe.py` | standalone tier probe | NEW |
| `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` | +`--iter97` / `--iter98` pin groups | EDIT |
| `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` | register `MEDIA_FRAME_LANE`, `OPENAI_SERVICE_TIER` | EDIT |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/` | baseline + A/B pulls + T4-eval verdict + costs (gitignored) | NEW (evidence) |

## Deploy Rules
- Lane open (OR, from repo root): `scripts/new_lane.sh 97 61bfc7e implementation` → boot `/tmp/opencode/wt-97/engine` with `VOICE_TEST_TOKEN` from the lane `.env`: `cd /tmp/opencode/wt-97/engine && set -a; . ./.env; set +a; nohup .venv/bin/uvicorn diallux.app:app --host 127.0.0.1 --port 8065 --loop uvloop > /tmp/opencode/lane-8065.log 2>&1 &` (T2 lands before this arg exists — pre-T2 boots omit `--loop uvloop`; the checkpoint records the difference).
- FI lane for local testing: same boot on `:8021` from the FI checkout of the branch.
- NEVER touch: protected `engine/iter73-oregon-wip-20260924` + OR root checkout, lanes `:8049/:8050/:8063`, FI services `:8000–8003`, `:8080` Caddy, prod agents (`agent_16985b5d087e56c35141983396`, `agent_87e4d5f08475e5bc558b2f390f`), live `validator_endpoint/`, `.env` values (owner-set).
- No merges without owner say-so (LAW 0). `scripts/keyhound` before every push. Commit registry law: refresh `research/surgeon/iter47-call-ledger/ledger.db` at session end (backup first).
- iter98 lane: `scripts/new_lane.sh 98 engine/97-implementation service-tier` (cut from the tip of iter97 — owner directive).

## Tasks (in order)

### T0 — baseline snapshot (no code)
Goal: the A/B denominators + the exact red set.
Commands (OR lane): open lane + boot (above); `curl -s localhost:8065/health | python3 -m json.tool`; `cd /tmp/opencode/wt-97/engine && .venv/bin/python -m pytest tests -q 2>&1 | tail -15` (record the 5 red names — expect 516/1/5); mic run: `.venv/bin/python scripts/llm_mic_caller.py --ws-url "ws://127.0.0.1:8065/mic/ws?k=$VOICE_TEST_TOKEN" --scenario happy --max-caller-turns 12 --journal-log /tmp/opencode/iter97_baseline_mic.jsonl` (≥50 agent turns total across runs if needed); `.venv/bin/python scripts/latency.py --hours 2 --json`.
Files: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/baseline_mic/`.
Verification: red names recorded; baseline p50/p95 table exists for `stt_eot_to_llm_first_ms`, `llm_first_to_tts_first_ms`, `tts_first_to_audio_out_ms`, `e2e_response_ms`, `e2e_turn_ms`; phone-path marked pending-owner.
**⟙ T0 DONE (2026-10-08)**: n=73 real mic turns on FI :8021 (`research/surgeon/iter97-implementation/baseline_mic/t0_final_reports.tsv`); `stt_eot_to_llm_first` p50 1,533 / `e2e_response` p50 1,714 / `e2e_turn` p50 2,022. Suite red set on FI: 510 passed / 1 skipped / 5 failed (516 collected; the OR count 516/1/5 is the OR-box collection difference). No real Cal.com bookings created.

### T1 — clock truth (commit 1; pure additive)
Goal: decompose `stt_eot → llm_dispatch → first_event` on every round.
Files: latency.py, builder.py (:2287/:2322), session.py (:877 stamps, :904 bench_aliases — partial set allowed, `t_tts_req` omission recorded), metrics.py (2 histograms + Twilio interarrival + drop counter), tests/test_iter97_clock_dispatch.py.
Verification: `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh --iter97` green (after fast_suite edit or explicit node-ids before it); full suite identical red set; lane shows the new report keys in `turn N final report:` lines.
**STOP CHECKPOINT:** pull ≥50 mic turns with T1 live. If `stt_eot_to_llm_dispatch_ms` p50 < 100 ms → the loop-adder thesis needs revision: STOP, report the decomposition, ask the owner before building T3.
**⟙ EXECUTED (DONE, commit `68e5f3c`)**: TurnClock `t_llm_dispatch`/`t_llm_first_event` + report keys landed; writer events at `builder.py:2290` (`llm_dispatch`) and `:2332` (`llm_first_event`). Measured (n=73 baseline turns + n=27 T1-era deep persona arcs, FI :8021):
| segment | p50 | p95 |
|---|---|---|
| `stt_eot_to_llm_dispatch_ms` | 70 | — |
| `llm_dispatch_to_first_event_ms` | 1,208 | — |
| `llm_first_event_to_llm_first_ms` | 538 | 2,370 |
| `llm_first_to_tts_first_ms` | 174 | — |
| `e2e_response_ms` | 1,901 | — |
Baseline tsv: `research/surgeon/iter97-implementation/baseline_mic/t0_final_reports.tsv`. **⟙ STOP CHECKPOINT FIRED**: dispatch p50 70 ms < 100 → loop-contention thesis DEAD pre-dispatch; the adder lives in the OpenAI request itself (≈ same-day raw cURL default-tier TTFT 1.18–1.81 s).

### T2 — uvloop pin + proof (commit 2)
Goal: pinned, provable event loop.
Files: requirements.txt, engine/deploy/diallux.service, engine/Dockerfile, app.py (_lifespan log + `/health` `"event_loop"`).
Verification: lane `/health` shows `"event_loop": "uvloop.Loop"`. If the pre-T2 lane already ran uvloop (`uvicorn[standard]` auto-select) — record that fact and make NO latency claim for T2. Rollback = remove the launch arg. Suite unchanged (identical red set).
**⟙ SKIPPED BY VERDICT (honesty)**: lanes ALREADY run uvloop (`uvicorn[standard]` auto-select; native stack seen in py-spy: `uv__io_poll`/`uv_run`). Zero gain available; pin remains pending (tape-out only if spare scope, iter98 Deferred).

### T3 — media frame lane (commit 3; flag OFF)
Goal: kill inbound head-of-line blocking without changing default behavior.
Files: config.py (iter97 section), session.py (class attrs `_media_queue`/`_media_drain_task = None`; `__init__` queue when flag on; sync `enqueue_media` drop-oldest + `diallux_media_lane_dropped_total` + one WARNING per burst; `_media_drain` spawned beside `_writer_task` :214, cancelled beside `_liveness_task` :302; ONE queue ONE drain law), app.py (/media :167–170 and /mic/ws :224–225 branch; Twilio interarrival stamped in the reader BEFORE dispatch; mic stamp stays receive-side BEFORE enqueue), tests/test_iter97_frame_lane.py.
Verification: new pins green; re-run `test_iter38_turn_lifecycle.py`, `test_iter93_epoch_race.py`, `test_iter80_stt_liveness.py`; full suite identical red set. Flag-off path byte-exact (no queue exists, inline call unchanged).
**A/B gate (lane `.env` `MEDIA_FRAME_LANE=1`, ≥50 mic turns):** `stt_eot_to_llm_dispatch_ms` p50 ≤150 ms / p95 ≤250 ms; Twilio/mic interarrival p95 ≤65 ms during LLM bursts; `media_lane_dropped_total` == 0; `e2e_response_ms` p50 ≥100 ms better than T0. Miss → keep flag OFF, report numbers, do NOT improvise.
**⟙ SKIPPED BY VERDICT: T3 NOT BUILT.** The media-frame-lane premise (250–350 ms loop-contention adder inbound) is measured DEAD — dispatch p50 is 70 ms; the adder lives in the OpenAI request, not the loop. Sensors it would have carried (histograms/counter/interarrival) already merged in T1.

### T4-EVAL — worthiness verdict (no build)
Goal: decide whether a raw-SDK speak path (owner-plan §T4) is ever worth building.
Commands: `llm_dispatch_to_first_event_ms` p50/p95 from the T3 A/B pulls vs raw-API TTFT on the same payload shape (reuse the iter98 probe's request composer, or a 10-pair cURL set from OR like session-1).
Verification: verdict written into the report using the rule — within ~50 ms p50 of raw = **T4 DEAD**; ≥150 ms sustained delta = **T4 CANDIDATE** (future owner-gated phase; the byte-parity/warm-parity spec in the owner plan stays the blueprint). Record in `ITERATIONS.md` at merge time.
**⟙ T4-EVAL DEAD.** Lane `llm_dispatch_to_first_event_ms` p50 1,208 ms ≈ same-day raw-API default-tier TTFT on the same payload shape (session-1 cURL evidence: 1.18–1.81 s per request; endpoint plumbing adds ~0–50 ms). Rule satisfied ⇒ raw-SDK speak path is DEAD, no build.

### T5 — fast_suite pin groups + report + ASK (commit 4, docs+tooling)
Files: `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` (+`--iter97`/`--iter98` cases), report `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/97_report.md`, `ITERATIONS.md` entry (on branch).
Verification: `fast_suite.sh --iter97` runs exactly the 5 named files; `--iter98` the 3; `--touched` behavior unchanged (config.py still forces full). Report carries: baseline vs A/B tables, checkpoint verdict, T2 honesty note, T4-eval verdict. **ASK JULIO — LAW 0.**

### iter98-B1 — tier knob (branch `engine/98-service-tier` from iter97 tip; commit 1)
Files: config.py (`openai_service_tier: str = ""` after `openai_verbosity` :45), llm.py (hoist mk for ALL models; reasoning keys stay conditional; `mk["service_tier"]` when non-empty; attach `model_kwargs` only when non-empty — byte-parity; same in `llm_for_verbosity` twins; `_warm_llm` inherits; `llm_boot_prewarm` NOT tiered), app.py `/health` `"service_tier"`, docs/Testing_guidelines/ENV-SWITCHES.md, tests/test_iter98_service_tier.py.
Verification: pins green incl. **byte-equality: serialized kwargs with `""` == pre-change bytes**; re-run `test_iter44_prewarm_bytes.py`, `test_iter65_boot_prewarm.py`; identical red set.

### iter98-B2 — tier probe (commit 2)
Files: `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_tier_probe.py` (standalone, stdlib+openai only, zero engine imports; ≥10 paired streaming TTFT requests default vs `service_tier="fast"` on gpt-5.4; prints no-400 confirmation + delta).
Verification: probe output in the report; if the API rejects `"fast"` on this family, keep the knob `""`, report, stop.

### iter98-B3 — lane A/B (owner-gated flip)
Commands: lane `.env` `OPENAI_SERVICE_TIER=fast` (OWNER sets it — agents never edit `.env` values), reboot lane, ≥50 mic turns, `lf.py costs --hours 24`.
Verification: keep gate = `llm_dispatch_to_first_event_ms` p50 **−100 ms minimum** vs the same lane at default tier + costs delta recorded. Miss → flag back to `""`, report.

## Validation Plan (end-to-end)
1. Suite identical red set (516/1/5) at every commit gate; new pins green via `fast_suite.sh --iter97` / `--iter98`.
2. Flag-off byte-exactness: no queue object exists with `MEDIA_FRAME_LANE` unset; `OPENAI_SERVICE_TIER=""` request bytes identical to today (pinned by test).
3. A/B numbers from real turn reports (not estimates) in `97_report.md`: T0 baseline, T1 decomposition, T2 loop proof, T3 lane gates, T4-eval verdict, iter98 keep/revert.
4. `git status -s engine/diallux/` clean outside the two branches; no merges without owner say-so; registry refreshed; keyhound before pushes.
5. All evidence in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/` (gitignored), never inside `engine/`.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| T4 raw-SDK speak-path BUILD | Eval-gated by T4E rule; owner say-so required; blueprint preserved in the archived owner plan |
| iter99 TTS bake-off | Owner-rejected 2026-10-08 ("dumb, not a gain"); Voice LAW stands |
| fast_first_flush, warm-knob tuning, mouth/brain split, Deepgram EOT knobs | REJECT/deferred per 97_analysis + owner directives |
| Real-Twilio phone-path verdict | Owner fires the call (same class as PT-85) |
| iter96 merge (PT-85) | Owner-gated, parked, unrelated to this branch |
| iter96c loop-lag probe | SUPERSEDED by T1 (do not run it; its reserved ports are reused) |
