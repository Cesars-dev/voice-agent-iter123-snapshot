# 02_ACTION_PLAN — iter87 prewarm VERSION B (build plan, pre-execution)

Follows 01_audit.md. Base: wt-iter85 `542d3e8`. All line anchors below are @ 542d3e8
(re-verified in 04 preflight). Scope law: **only `engine/diallux/graph/builder.py` +
`engine/diallux/config.py` + one new test file.** No session.py, no llm.py, no STT changes.

## Step 0 — branch cut (mechanical, per master plan Environment)
```bash
ssh root@5.78.83.174
git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter87 \
  -b engine/iter87-prewarm-hold 542d3e8
cp /tmp/opencode/wt-iter85/engine/.env /tmp/opencode/wt-iter87/engine/.env   # ENV LAW
```
Verify: worktree exists; `.env` has `OPENAI_API_KEY` (new key prefix, never printed).

## Step 1 — config.py (1 knob)
Insert next to `prewarm_entry_wait_eot_ms` (:219), same block:
```python
    # iter87 VERSION B hold law: the state-entry ack (entry_lite) round
    # bounded-awaits the DESTINATION state's in-flight prewarm TASK before
    # sending — ordering, not timing; the cap is a dead-provider fence.
    # 0 = off (byte-exact iter85). Lane/battery runs 2500 (> measured warm
    # worst case 2059 ms).
    warm_await_dest_ms: int = 0
```
Compile-check: `.venv/bin/python -c "from diallux.config import Settings; s=Settings(); assert s.warm_await_dest_ms == 0"`.

## Step 2 — builder.py site A: successor map (graph-build derived, no hand table)
After `self.states` init (:352):
```python
        # iter87 VERSION B fire law: FSM successor map derived from the SAME
        # edges that generate the transition_to_* tool schemas (llm.py
        # build_tool_schemas) — one source of truth, no hand-written table.
        self._state_successors: dict[str, list[str]] = {
            name: [e["destination_state_name"] for e in cfg.get("edges", [])]
            for name, cfg in self.states.items()}
```

## Step 3 — builder.py site B: the HOLD (entry_lite branch)
Replace the `pass` body of the entry_lite await branch (:1846-1852) — keep the surrounding
`if runtime.settings.prewarm_entry_wait_eot_ms > 0 or ...:` structure intact:
```python
                elif entry_lite:
                    # iter87 VERSION B hold law: ordering, not timing — the
                    # ack's payload is NEVER sent before the destination warm
                    # has landed (TASK await: success/error/HTTP-timeout all
                    # release; 0-200 ms typical, fence 2500 only on a dead
                    # provider day). 0 = byte-exact iter85 (pass).
                    if runtime.settings.warm_await_dest_ms > 0:
                        await runtime._await_warm(
                            state_name,
                            wait_ms=runtime.settings.warm_await_dest_ms)
```
Note: NON-lite key (`state_name`) — the ack carries full tools (FIND-5) and destination
warms register under the bare state name (audit R11).

## Step 4 — builder.py site C: one-ahead FIRE (speech path)
Immediately after the post-execute force warm F4 (:2552-2554), still inside
`if new_state:`:
```python
                    # iter87 VERSION B fire law (one-ahead): entering X also
                    # warms X's FSM successors — lands during the caller's
                    # think time (real p50 17 s). Non-force: the latch dedupes;
                    # the eventual real transition re-fires with force=True
                    # (above) which supersedes _latest_warm.
                    for succ in runtime._state_successors.get(new_state, ()):
                        runtime.warm_prompt_cache(
                            succ, list(history) + list(new_history),
                            dvs=dict(dvs))
```

## Step 5 — builder.py site D: chain-start FIRE
In `_deterministic_node`, after the `plan = [...]` list (:2660-2668) and before
`cur_state = state_name`:
```python
            # iter87 VERSION B fire law (chain): every transition_to_*
            # destination in the plan warms at chain start — the warm lands
            # inside the webhook idle (1.5-4.5 s) the caller already
            # tolerates. ALL destinations (not just Closing) so an abort's
            # repair round in a mid-chain state holds on a landed warm too.
            # state["history"] is byte-exact for the post-chain ack (the
            # chain appends no history).
            for _step, _home, _needs in plan:
                if _step.startswith("transition_to_"):
                    _dest = _step[len("transition_to_"):]
                    if _dest in self.states:
                        self.warm_prompt_cache(
                            _dest, list(state.get("history") or []),
                            dvs=dict(dvs))
```
(`self.` — this is the runtime's own method context, matching `self.warm_slots_async` above.)

## Step 6 — builder.py site E: chain post-patch re-fire
After the plan loop completes, immediately before the `phaseb:chain_ok` span/return
(:2712-2715):
```python
            # iter87: re-fire the final destination with POST-PATCH dvs
            # bytes (force=True supersedes the chain-start warm in
            # _latest_warm — the Closing ack's hold target).
            self.warm_prompt_cache(
                "Closing", list(state.get("history") or []),
                dvs=dict(dvs), force=True)
```
Abort path: NO re-fire (early return inside the loop) — the chain-start warm already
covers the repair round; dvs does not affect prefix bytes under `state_in_delta`.

## Step 7 — builder.py site F: T1.4 ttft on first delta of ANY type
In the `async for ev in runtime.llm.astream(...)` loop: hoist the timestamp to the loop
top and delete the inner copy at :2271-2272:
```python
            async for ev in runtime.llm.astream(messages, tools,
                                                verbosity=runtime._verbosity_for(state_name)):
                if ttft_s is None:
                    ttft_s = time.perf_counter() - t0   # iter87 T1.4: first delta of ANY type
                if ev["type"] == "token":
                    ...  # (existing body, minus the old ttft lines)
```
Effect: tool-only rounds now log a real ttft (first `tool_call_start`) instead of `None`.

## Step 8 — T1.4b: RESOLVED as SDK-side (owner ratifies in 04)
No engine change. The iter86 SDK (`engine/scripts/call_forensics.py`, run from
wt-iter86) already re-anchors the conv-side metric at confirmed EOT
(user-perceived = S2L−HS+L2T+T2A) and emits per-turn eager/wait/cold counters. Design
§5's "only builder.py + config.py" is preserved. If the owner wants engine-side
turn-report re-anchoring instead, that is a NEW session (session.py/latency.py).

## Step 9 — unit tests: `engine/tests/test_iter87_prewarm_hold.py`
Fake clock/gate/stream pattern from `test_iter85_eager_hold.py` / `test_iter46_latency_floor.py`:
1. `test_default_off_byte_exact` — `warm_await_dest_ms=0`: entry_lite round never calls
   `_await_warm` with the dest cap (spy), behavior identical to iter85.
2. `test_hold_awaits_task` — pending fake task in `_latest_warm[state]`, knob 2500 →
   `_await_warm(state, wait_ms=2500)` called; outcome `landed`; round proceeds.
3. `test_hold_fence_timeout` — never-completing task, small `wait_ms` → outcome `timeout`,
   round STILL proceeds (shield keeps warm alive).
4. `test_hold_no_task` — empty `_latest_warm` → outcome `no_task`, waited 0, proceeds.
5. `test_oneahead_warms_successors` — transition into ConfirmSlots → `VerifyLead` in
   `_prewarmed`; force re-fire supersedes `_latest_warm["ConfirmSlots"]`.
6. `test_chain_fires_all_destinations` — `_deterministic_node` under phaseb conditions →
   `{VerifyLead, Booking, Closing}` ⊆ `_prewarmed`; `_latest_warm["Closing"]` set.
7. `test_successor_map_from_edges` — `_state_successors["Intake"] == ["Discovery"]`,
   `["Closing"] == []`.
8. `test_prewarm_master_gate` — `prompt_prewarm=False` → no task ever registered.
9. `test_ttft_any_delta` — fake astream yielding `tool_call_start` first → ttft non-None.

Run: `.venv/bin/python -m pytest tests/test_iter87_prewarm_hold.py -q` → green;
then full `pytest engine/tests -q` → the 7 known stale reds ONLY, zero new.

## Step 10 — battery + ledger (master plan T3, condensed)
- Boot lanes 8047/8048 from `boot_lane_t4_fix1.sh` pattern (round-B knobs) **+
  `WARM_AWAIT_DEST_MS=2500`**; verify journalctl `connected` = elevenlabs Sarah.
- Happy + barge scenarios, FROZEN driver (wt-iter82 caller), fresh battery JSONs.
- Gates (design §4, terminology per audit R10):
  1. ZERO destination rounds with `cache_read=0` (input>1000) on ANY transition (7/7).
  2. `await_warm` spans with `cap_ms=2500`: `waited_ms` p50 ≈ 0, p99 ≤ a few hundred,
     `timeout` count 0 in normal runs.
  3. Default-0 byte-exact + suite green (7 stale reds only).
  4. `PROMPT_PREWARM=false` still kills every warm.
  5. SDK conv-side: destination rounds inside plain-turn budget (~<1.2 s).
- SDK `--trace` on both traces → outputs to
  `research/surgeon/iter87-prewarm-hold/`; APPEND `forensics_calls` rows (venv python +
  sqlite3, call_kind `llm_mic_harness`, commit sha, e2e/uperm/eager/cache0 columns).
- Cancel every test booking (Cal 3801235 REAL; cancel POST needs `cancellationReason`).

## Step 11 — report + close (master plan T4)
- `research/surgeon/iter87-prewarm-hold/01_battery_verdict.md` (verdict vs owner intent,
  gaps, next options).
- Update `plan_v5_iter81_master_ladder.md` STATUS; docs commit → main; re-sync Finland
  mirror; kill lanes + `ss -ltnp` verify.
- keyhound before any push; push law: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push`.

## Execution discipline
- Compile-check after EACH builder.py step (`python -m py_compile`); targeted pytest after
  Steps 3-7; full suite at Step 9 end.
- One commit per logical unit (config+map / hold / fires / ttft / tests) or one build
  commit — follow repo style (single descriptive commits per iteration phase).
- NO merges to main (LAW 0). Owner ear + merge call = T4 HITL.
