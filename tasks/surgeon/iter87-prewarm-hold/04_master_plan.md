# 04_MASTER_PLAN — iter87 prewarm VERSION B (THE DETERMINISTIC HOLD) — AIRTIGHT

Status: **PREFLIGHT COMPLETE — OWNER GO GRANTED 2026-09-30 (build executing).**
Zero open technical items.

## Owner verdicts (2026-09-30, ratified)
- **D1 T1.4b = SDK-side ONLY** (no engine turn-report change). Ratified.
- **D2 chain fire = ALL THREE destinations (VerifyLead, Booking, Closing).** Ratified
  ("keep it engine side"). Rationale: only LLM-led chain round in the happy path is the
  Closing ack (slot confirmation already happened at ConfirmSlots); VerifyLead/Booking
  mid-chain rounds = abort-repair only; speech-path transitions to them are covered by
  the one-ahead S4.
- **NEW — 10 ms settle (owner, 2026-09-30):** after `_await_warm` returns inside the hold
  branch, the round sleeps a fixed `await asyncio.sleep(0.01)` before the LLM send —
  "not instant, so we never race an incomplete warm". Gated behind `warm_await_dest_ms > 0`
  (default 0 = byte-exact). Cost p50 ≈ 0-10 ms on ack rounds only; STT/eager untouched.
  Folded into S3 (amendment, not a rewrite). Covered by test `test_settle_sleep_present`.
- **NICE-TO-HAVE → plans/NEXT_STEPS.md:** per-state prewarm on/off switch (owner
  deprioritized for this build; master gate + hold knob suffice).

- Base: `542d3e8` (`engine/iter85-eager-hold`, wt-iter85) — audited, every anchor re-verified.
- New branch: `engine/iter87-prewarm-hold`, worktree `/tmp/opencode/wt-iter87` (OREGON).
- Design contract (owner, verbatim in `research/surgeon/iter86-warm-sync/07_owner_design_capture.md`):
  *the destination payload is NEVER sent before the warm has landed — every single time,
  no milliseconds gambled.* Option B (eager-off) REJECTED. Eager/EOT contract untouched.

## Preflight verification results (all against real code @ 542d3e8)

| Check | Result |
|---|---|
| `_await_warm(state_name, wait_ms=None)` signature | ✅ builder.py:627 — design snippet calls it correctly |
| `warm_prompt_cache(state_name, history=None, dvs=None, lite=False, force=False)` | ✅ :460-462 — all fire sites compatible |
| entry_lite `pass` body at :1846-1852 | ✅ exact; surrounding if/elif chain verified, insertion safe |
| state_node variable is `runtime.`; `_deterministic_node` uses `self.` | ✅ both verified in source |
| chain `plan` tuples are `(step, home, needs)` | ✅ :2660-2668 |
| successor map derivable from `edges` (no hand table) | ✅ llm.py:196-204 generates transition_to_* from edges; FSM = single chain, Closing terminal |
| chain appends no history → chain-start warm history byte-exact for the Closing ack | ✅ `_deterministic_node` returns no history update |
| **R7 head parity ack-vs-warm** | ✅ CLOSED: `_expand_kb` returns False whenever a store exists (:799-801) → `_head_for` == `_entry_lite_head` bytes in every live configuration (incl. rag_keep_markers both ways). Divergence ONLY in degraded no-store+`fallback_inline_kb=True` mode — pre-existing iter49 condition, not introduced by this build; ack would cache on the tools prefix only there. |
| test pattern feasibility | ✅ tests construct `CallRuntime(Settings(...), LLM_JSON)` directly + `SpyLLM(FakeLLM)` records `warm()` calls (test_iter46_latency_floor.py:44-60) |
| F4 (post-execute force warm) unconditional on `new_state` | ✅ :2548-2554 — R3's recency guarantee holds; F4 must NOT be removed |
| `_prewarmed` call-scoping | ✅ runtime constructed per call (session.py:174) — no cross-call latch leak |

## Owner ratification items (defaults chosen; say-so required)

| # | Decision | Default (built unless vetoed) | Rationale |
|---|---|---|---|
| D1 | T1.4b scope | **SDK-side only** (no engine turn-report change). The iter86 SDK (`call_forensics.py`) already re-anchors conv-side at confirmed EOT + counts eager/wait/cold per turn. Keeps diff = builder.py + config.py per design §5. | design §3.3 vs §5 contradiction (cross-ref #2) |
| D2 | Chain fire targets | **ALL** `transition_to_*` destinations in the plan (VerifyLead, Booking, Closing), not just Closing. +2 × 64-token requests per chain run. | covers abort-repair rounds (audit R4) |

## The build (execute ONLY on owner GO; compile-check after each step)

### S0 — branch cut (OREGON)
```
git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter87 \
  -b engine/iter87-prewarm-hold 542d3e8
cp /tmp/opencode/wt-iter85/engine/.env /tmp/opencode/wt-iter87/engine/.env
```
Verify: `.env` has `OPENAI_API_KEY` (new prefix `sk-proj-U7zPicu…`; never print).

### S1 — config.py (1 knob, next to :219)
`warm_await_dest_ms: int = 0` — default 0 = byte-exact iter85 (knob law). Battery: 2500
(> measured warm worst-case 2059 ms).

### S2 — builder.py site A (successor map, after :352)
`self._state_successors` from `self.states[*]["edges"]` — same source of truth that
generates the transition tools. 3 lines.

### S3 — builder.py site B (THE HOLD, replaces the `pass` at :1846-1852)
```python
                elif entry_lite:
                    # iter87 VERSION B hold law: ordering, not timing — the
                    # ack's payload is NEVER sent before the destination warm
                    # has landed (TASK await: success/error/HTTP-timeout all
                    # release; fence 2500 only on a dead-provider day).
                    # 0 = byte-exact iter85.
                    if runtime.settings.warm_await_dest_ms > 0:
                        await runtime._await_warm(
                            state_name,
                            wait_ms=runtime.settings.warm_await_dest_ms)
```
NON-lite key (ack carries full tools, FIND-5). The existing eot/mid-turn/lite branches
ABOVE it stay untouched.

### S4 — builder.py site C (one-ahead FIRE, inside `if new_state:` after F4 :2552-2554)
```python
                    for succ in runtime._state_successors.get(new_state, ()):
                        runtime.warm_prompt_cache(
                            succ, list(history) + list(new_history),
                            dvs=dict(dvs))
```
Non-force (latch dedupes); the eventual real transition's F4 re-fires force=True and
supersedes `_latest_warm`.

### S5 — builder.py site D (chain-start FIRE, after `plan = [...]` :2660-2668, before `cur_state = state_name`)
```python
            for _step, _home, _needs in plan:
                if _step.startswith("transition_to_"):
                    _dest = _step[len("transition_to_"):]
                    if _dest in self.states:
                        self.warm_prompt_cache(
                            _dest, list(state.get("history") or []),
                            dvs=dict(dvs))
```

### S6 — builder.py site E (chain post-patch re-FIRE, before the `phaseb:chain_ok` span/return :2712-2715)
```python
            self.warm_prompt_cache(
                "Closing", list(state.get("history") or []),
                dvs=dict(dvs), force=True)
```
Abort path: no re-fire (early return) — chain-start warm covers the repair round; dvs is
not in the prefix under `state_in_delta`.

### S7 — builder.py site F (T1.4: ttft on first delta of ANY type)
Hoist `if ttft_s is None: ttft_s = time.perf_counter() - t0` to the top of the
`async for ev in runtime.llm.astream(...)` loop; delete the inner copy at :2271-2272.
Tool-only rounds now log real ttft.

### S8 — tests: `engine/tests/test_iter87_prewarm_hold.py` (9 tests, per 02 Step 9)
default-off byte-exact / hold-lands / fence-timeout-proceeds / no-task-proceeds /
one-ahead-successors / chain-fires-all-destinations / successor-map-from-edges /
PROMPT_PREWARM-master-gate / ttft-any-delta. Patterns: `CallRuntime` + `SpyLLM`
(test_iter46_latency_floor.py:44-60).
Gate: targeted green + full suite = the 7 known stale reds ONLY (test_delivery ×4,
iter46 fast-first-flush, iter59, iter60 — never re-derived).

### S9 — commit + push (branch only — LAW 0)
keyhound → `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push`.

### S10 — battery (lanes 8047/8048; round-B knobs + `WARM_AWAIT_DEST_MS=2500`)
`boot_lane_t4_fix1.sh` pattern, systemd-run --user --collect; journalctl `connected` =
elevenlabs Sarah; FROZEN driver (wt-iter82); happy + barge. Gates:
1. ZERO destination rounds `cache_read=0` (input>1000) on ANY transition — 7/7.
2. `await_warm` spans `cap_ms=2500`: waited_ms p50 ≈ 0, p99 ≤ few hundred, `timeout` = 0.
3. Default-0 byte-exact + suite green (7 stale reds only).
4. `PROMPT_PREWARM=false` still kills every warm.
5. SDK conv-side: destination rounds ~<1.2 s.
SDK `--trace` both traces → `research/surgeon/iter87-prewarm-hold/`; APPEND
`forensics_calls` rows (venv python + sqlite3; call_kind `llm_mic_harness`; commit sha;
e2e/uperm/eager/cache0). Cancel every test booking (Cal 3801235 REAL; cancel POST
requires `cancellationReason`).

### S11 — report + close
`research/surgeon/iter87-prewarm-hold/01_battery_verdict.md`; ladder STATUS update;
docs → main; Finland mirror re-sync; lanes killed + `ss -ltnp` verified; owner ear +
merge call (HITL).

## Guardrails (unchanged, binding)
- NEVER touch prod checkout df23d37 / diallux.service / :8026/:8000-8003/:8090.
- Two-box law: session on Finland; repo ops ssh-wrapped to OREGON.
- MODEL LAW gpt-5.4; VOICE LAW tests = EL Sarah; no merges without owner say-so.
- Abort/rollback: every knob defaults OFF; battery runs from round-B base — a bad toggle
  = lane re-boot unchanged.

## Archive
Source docs archived → `tasks/surgeon/iter87-prewarm-hold/archive/`
(01_plan_VERSION_B.md + plan_v5_iter87_prewarm_owner_design.md + 07_owner_design_capture.md).
