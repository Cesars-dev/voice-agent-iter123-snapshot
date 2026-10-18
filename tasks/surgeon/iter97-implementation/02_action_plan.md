# 02_action_plan — iter97 implementation (T1–T3 + T4-eval; iter98 service_tier)

Procedure: `tasks/surgeon/iter97-implementation/` · Date: 2026-10-08 · Base: main @ `61bfc7e`
Based on: `01_audit.md` (same folder). Owner verdicts on record there.

## Branch & lane strategy (owner design, 2026-10-08)

```
main @ 61bfc7e
  └─ cut ──▶ engine/97-implementation   (lane wt-97 on OR; ALL loop-hygiene commits here)
                 │  T1 clock-truth → T2 uvloop → T3 frame lane → measure → T4-eval verdict
                 └─ cut from TIP ──▶ engine/98-service-tier  (lane wt-98; tier knob only)
                                        (iter99 = stale, owner-rejected, never cut)
```

- Lane opens on OREGON with `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh 97 61bfc7e implementation` (numeric guard: pass `97`, NOT `iter97`) → worktree `/tmp/opencode/wt-97`, branch `engine/97-implementation`, audited `.env` from canonical. Same pattern as the iter96 lane (`engine/96-delta-cache-layout` @ `wt-96`).
- Finland develops on the same branch: `git fetch origin && git switch --track origin/engine/97-implementation` (after OR creates+pushes it, or FI cuts and OR bases the lane on it — ONE branch either way).
- iter98 lane: `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh 98 engine/97-implementation service-tier` — cut FROM THE TIP of iter97 (owner directive; overrides the no-stacking clause of LAW 0 v2.1 — recorded).
- Commits: one commit per T-number, each behavioral change behind a pydantic Settings flag defaulting to OFF (= byte-exact current behavior). T1 (pure observability) is exempt from the flag but must not rename/alter any existing report field.

## T0 — baseline snapshot (no code)
1. Full suite once on the lane: `cd /tmp/opencode/wt-97/engine && .venv/bin/python -m pytest tests -q` → record the EXACT 5 red test names (expected 516 passed / 1 skipped / 5 failed). Every later gate = "identical red set + all new tests green".
2. Mic-bridge baseline: boot lane, run `scripts/llm_mic_caller.py --scenario happy` (≥50 caller turns), pull `scripts/latency.py` → save to `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/baseline_mic/`. Record p50/p95 of `stt_eot_to_llm_first_ms`, `llm_first_to_tts_first_ms`, `tts_first_to_audio_out_ms`, `e2e_response_ms`, `e2e_turn_ms`. Phone-path (real Twilio) numbers = pending-owner; mark them as such.
3. `/health` snapshot BEFORE T2 (record `event_loop` absence — T2 adds the field; for the uvloop-already-active question, check the running lane process first: `ps aux | grep uvicorn` + `python -c "import uvloop"` in the venv).

## T1 — clock truth (pure additive observability) — commit 1
1. `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/latency.py` — `TurnClock`: add fields `t_llm_dispatch: float | None = None`, `t_llm_first_event: float | None = None` + `mark_llm_dispatch()` / `mark_llm_first_event()`. In `report()` ADD (never rename existing keys): `stt_eot_to_llm_dispatch_ms`, `llm_dispatch_to_first_event_ms`, `llm_first_event_to_tts_token_ms`.
2. `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` round loop: `writer({"llm_dispatch": True})` immediately after `t0` (`:2287`, beside `tracer.start_llm` `:2288`); `writer({"llm_first_event": True})` inside the `if ttft_s is None:` anchor (`:2322`). Both fire EVERY round.
3. `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` `_run_turn` custom-event branch (`:877`): BEFORE the `"tts_token"` check, add first-only stamps — `if "llm_dispatch" in data and clock.t_llm_dispatch is None: clock.mark_llm_dispatch()`; same for `llm_first_event`. (New keys flow through the existing `mode == "custom"` stream; today they fall through silently.)
4. `_late_turn_report` (`:904`): append `final["bench_aliases"] = {"llm_ttft": <llm_dispatch_to_first_event_ms>, "tts_ttfb": <t_tts_req → t_tts_first>, "e2e_latency": <e2e_response_ms>}` — None-safe. NOTE: `t_tts_req` does not exist in TurnClock today — if the TTS request stamp is not reachable cheaply, ship `bench_aliases` with `llm_ttft` + `e2e_latency` only and record the omission in the report (do NOT invent a clock in this commit).
5. `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/metrics.py`: `diallux_stt_eot_to_llm_dispatch_ms` (buckets 25/50/100/150/250/500), `diallux_llm_dispatch_to_first_event_ms` (200/300/400/600/800/1200/2000), `diallux_twilio_media_interarrival_ms` (mirror mic buckets 20/35/50/65/80/100/150/200/300/500), counter `diallux_media_lane_dropped_total`; observe the two new spans in `observe_turn_report`.
6. New test `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter97_clock_dispatch.py`: writer events fire per round; first-only stamping; report has new keys AND existing keys byte-identical; eager-turn anchoring sane (R3: base = EagerEOT when eager on).
**Gate:** new test green + fast_suite pin set green + full suite identical red set.
**STOP CHECKPOINT (owner data review):** with T1 on the lane, record the decomposition. If `stt_eot_to_llm_dispatch_ms` p50 < 100ms on the mic lane already, the loop-adder thesis needs revision → report before building T3.

## T2 — uvloop pin + proof — commit 2
1. `/home/julio/projects/clean_diallux_SDR/engine/requirements.txt`: add explicit `uvloop>=0.21` (Core runtime; do not rely on the `uvicorn[standard]` extra).
2. `/home/julio/projects/clean_diallux_SDR/engine/deploy/diallux.service` ExecStart and `/home/julio/projects/clean_diallux_SDR/engine/Dockerfile:17` CMD: append `--loop uvloop`.
3. Lane boots: every lane-start command carries `--loop uvloop` (lanes are bare background uvicorn — documented in the lane boot step of the master plan).
4. `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py`: `_lifespan` logs `type(asyncio.get_running_loop()).__name__`; `/health` adds `"event_loop": <loop class name>`.
5. Do NOT set the loop policy from app code (uvicorn creates the loop before importing the app; the launch arg is the switch, `/health` is the proof).
**Gate:** lane `/health` shows `uvloop.Loop`. If the running lane ALREADY showed uvloop before the arg (R7 — `uvicorn[standard]` auto-select), SAY SO in the report and skip the latency claim for T2. Rollback = remove the launch arg.

## T3 — media frame lane (head-of-line kill) — commit 3, flag OFF
1. `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` — NEW section `# ---- iter97: loop hygiene ----` (NOT in either "V2 production" copy): `media_frame_lane: bool = False`, `media_lane_queue_size: int = 50`.
2. `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py`:
   - Class-level `_media_queue = None`, `_media_drain_task = None` (R6 pattern, copy `_ladder_task` `:368–369`).
   - `__init__`: `asyncio.Queue(maxsize=settings.media_lane_queue_size)` only when flag on.
   - `enqueue_media(payload_b64)` — SYNC: while full → `get_nowait()` (drop-oldest) + increment `diallux_media_lane_dropped_total` + one WARNING per burst; then `put_nowait`.
   - `_media_drain()` — `while True: payload = await q.get(); await self.on_media(payload)` in try/except-log; spawned in `start()` beside `_writer_task` (`:214`) ONLY when flag on; cancelled in `stop()` beside `_liveness_task` (`:302`).
   - Ordering law (R8): ONE queue, ONE drain task, no other consumer touches `_media_queue`.
3. `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py` `/media` (`:167–170`): branch — flag on → `session.enqueue_media(payload)` (sync, never awaits); flag off → today's inline `await session.on_media(payload)`. Add Twilio interarrival stamp in the reader BEFORE dispatch (local `last_media_mono` → `diallux_twilio_media_interarrival_ms`). `mark`/`warning`/`stop` handling stays inline.
4. `/mic/ws` (`:224–225`): same branch; KEEP the existing `MIC_CHUNK_INTERARRIVAL_MS` stamp on the receive side BEFORE enqueue (R4).
**Gate:** new test `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter97_frame_lane.py` (FIFO order; overflow drop-oldest + counter; flag-off byte-exact inline path; `stop()` cancels drain without leaking; class-level defaults safe for no-`__init__` sessions) + re-run `test_iter38_turn_lifecycle.py`, `test_iter93_epoch_race.py`, `test_iter80_stt_liveness.py` + full suite identical red set.
**A/B gate (lane, `MEDIA_FRAME_LANE=1`, ≥50 mic turns):** `stt_eot_to_llm_dispatch_ms` p50 ≤150ms / p95 ≤250ms; interarrival p95 ≤65ms during LLM bursts; `media_lane_dropped_total` == 0; `e2e_response_ms` p50 ≥100ms better than T0 baseline. Miss → report numbers, keep flag OFF, do NOT proceed to contingency ideas.

## T4-EVAL — worthiness verdict only (NO build; owner-gated)
From lane data: compare lane `llm_dispatch_to_first_event_ms` against a raw-API TTFT probe on the SAME payload shape (`scripts/llm_tier_probe.py` measures raw TTFT — reuse its request composer). Verdict rule:
- lane dispatch→first ≈ raw TTFT (within ~50ms p50) → langchain adds ~nothing → **T4 DEAD** (record, close).
- lane dispatch→first >> raw TTFT (≥150ms sustained p50 delta) → **T4 CANDIDATE** → separate owner-gated phase (the raw-SDK spec lives in the owner plan §T4: serializer sha256 parity, same-commit warm parity, stop-on-divergence — unchanged, deferred).
Verdict goes in the iter97 report + `ITERATIONS.md` entry.

## iter98 — service_tier knob (SEPARATE branch `engine/98-service-tier`, cut from iter97 tip)
1. `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` LLM section (after `openai_verbosity` `:45`): `openai_service_tier: str = ""` (comment: `""` = off; `"fast"` = Fast mode (ex-Priority), ~2x token price).
2. `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py` `StreamingLLM.__init__` (`:216–263`): hoist the `mk` dict so it exists for ALL models (today it only exists inside the reasoning-model branch `:231–238`); reasoning keys still conditional; `mk["service_tier"] = settings.openai_service_tier` when non-empty; **attach `kwargs["model_kwargs"] = mk` ONLY when mk non-empty (R1 — byte-parity law)**. Same addition in `llm_for_verbosity` twins (`:279–283`). `_warm_llm` inherits via `**kwargs` — keep. `llm_boot_prewarm` NOT tiered (R2).
3. `/health`: add `"service_tier": getattr(s, "openai_service_tier", "")`.
4. New probe `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_tier_probe.py` (standalone, zero engine imports, `llm_mic_caller.py` pattern): verify the tier NAME — evidence was measured under `service_tier="priority"` (97_analysis #3); confirm `"fast"` is accepted (no 400) on gpt-5.4 + TTFT delta vs default over ≥10 paired requests.
5. Register the switch in `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md` (SWITCH LAW).
6. New test `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter98_service_tier.py`: kwarg present-when-set / absent-when-empty across main + warm + verbosity twins + `/health` field; **byte-equality pin: serialized request kwargs with `""` == today's bytes**; re-run `test_iter44_prewarm_bytes.py`, `test_iter65_boot_prewarm.py`.
**Lane flip `OPENAI_SERVICE_TIER=fast` = OWNER-gated.** Keep/revert gate: `llm_dispatch_to_first_event_ms` p50 −100ms minimum + `lf.py costs` delta in the report.

## fast_suite.sh update (rides the branch; whitelist-lane file)
`/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh`: add named pin groups so the owner's "500 pins light speed" covers the new work:
- `--iter97` → `tests/test_iter97_clock_dispatch.py tests/test_iter97_frame_lane.py tests/test_iter38_turn_lifecycle.py tests/test_iter93_epoch_race.py tests/test_iter80_stt_liveness.py`
- `--iter98` → `tests/test_iter98_service_tier.py tests/test_iter44_prewarm_bytes.py tests/test_iter65_boot_prewarm.py`
(`--touched` keeps working — a `config.py` edit still forces the full suite; that is intended.)

## Reporting (both iterations)
- Evidence → `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/` (gitignored): baseline, per-phase lane pulls, T4-eval verdict, iter98 A/B + costs.
- `ITERATIONS.md` ledger entry per repo convention; `GIT_TREE.md` refresh only after owner-approved merges.
- LAW 0: NO merges without owner say-so. `.env` flips on lanes only, owner-gated for anything prod.
