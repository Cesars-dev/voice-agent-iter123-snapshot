# audit_iter82 — mic caller booking gate: plan audit + root cause + fix plan (PLAN ONLY)

- Date: 2026-09-28. Session on FINLAND; ALL evidence pulled from OREGON (`ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`).
- Audits: `plans/plan_v5_iter82_fake_caller_booking_gate.md` (exists ONLY on the FINLAND mirror + OREGON draft `/tmp/opencode/plan_v5_iter82_booking_gate.md` — NOT committed to the repo, see §3.4).
- Status: PLAN ONLY — no code touched, no runs started. Awaits owner GO.

## 1. Verdict in one line

The fake caller is NOT failing in the engine, STT, or the caller brain. The DRIVER kills the call at caller turn 3 with a **false `booked_goodbye`**: the booked-hint detector matches the bare substring `"booked"` inside the agent's standard intake question ("...is it more about getting more **booked jobs**"), then orders the caller to wrap up and hangs up. 36 seconds, 3 caller turns, agent still in Intake, **zero** `create_livecall_booking` calls.

## 2. Root cause (deterministic, code-level)

File: `/tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py` (branch `engine/iter82-pause-nudge` @ `f0fde1b`)

- **Line 57:** `BOOKED_HINTS = ("booked", "confirmed", "scheduled", "put you down", "see you on")` — loose substrings.
- **Line 541** (`run_happy`, persona mode): fires the goodbye when ANY of those substrings appears in `" ".join(agent_turns).lower()` — i.e. **all agent turns ever concatenated, not the last turn** — once `len(state.caller_turns) >= 2`.
- **Lines 482-485** (scripted branch) already contain the CORRECT pattern: `strong_booked` = specific phrases ("you're booked", "you are booked", "booked you", "all set for", "see you", "confirmation", "locked in") — the persona branch just never got it.

Evidence chain (run 2026-09-28 **09:22:09–09:23:07 UTC**, sid `05c90a2fc483`, lane `t4-lane-8033b` port 8033, driver output `/tmp/opencode/t4_fake_v8.json`):

1. Agent turn 2 (ear transcript, from the json): *"Yeah. Absolutely. Are you looking to help answer more incoming calls, or is it more about getting more booked jobs"* — contains `booked`.
2. Caller turns 1+2 spoken → `len(state.caller_turns) == 2` → next loop iteration the line-541 `elif` fires: `stop_reason="booked_goodbye"`, directive=`PERSONA_GOODBYE_DIRECTIVE` (line 116).
3. Caller turn 3 = wrap-up line ("I'm interested in exploring how we can improve my services."), driver breaks the loop and closes the WS. `elapsed_s: 36.07`.
4. Lane journal `t4-lane-8033b` since 09:00: **0** `create_livecall_booking` lines; only turn 1 + turn 2 final reports exist for this sid. The claimed booking never happened.
5. No Langfuse trace exists for `micbridge-05c90a2fc483` (trace list jumps from `micbridge-3dbdca45e4bc` 09:18 to nothing) — evidence fallback = lane journal + driver json (both quoted above).

Why v10 (sid `3dbdca45e4bc`, trace `4b9958ed50ee`, turn cap 13) survived: pure phrasing luck — the agent happened never to say a bare "booked/scheduled/confirmed" in those 13 turns. The bug is a landmine in EVERY future run because the agent's stock intake question usually contains "booked jobs".

Transport re-confirmed healthy on the 09:22 run (plan's parity claims hold): turns 1-2 clean, e2e 0.97-1.13s, `eager_final_match=true`, room-tone flowing, no wedged turns.

## 3. Audit of the plan file

| # | Finding | Severity |
|---|---|---|
| 1 | **STALE:** plan says "cap raised to 30 in run_driver_t4.sh, NOT yet run" — a run DID happen 09:22 UTC with cap 30 and died as §2. Failure table has no row for it; "v11: never observed" is overtaken by events. | high |
| 2 | **Unsafe pass gate:** T3 gate 1 = `stop_reason == booked_goodbye` — stop_reason provably lies (§2). Gate must key on the `create_livecall_booking` tool call in Langfuse + booking uid + cancel 200. | high |
| 3 | T2 candidate-fix list contains nothing for the false-goodbye detector — T1 would have chased the v10 re-ask question while the deterministic kill sits in the driver's own goodbye logic. | high |
| 4 | **Plan not in the repo:** OREGON `plans/` holds only `plan_v5_iter81_master_ladder.md`; the iter82 plan exists only on the FINLAND mirror + `/tmp/opencode/plan_v5_iter82_booking_gate.md` draft. Docs go straight to main per LAW 0 — commit it (or this audit supersedes). | med |
| 5 | Deliverable filename inconsistency: File Map says `07_caller_root_cause.md`, T1 says `07_booking_root_cause.md`. Pick `07_booking_root_cause.md`. | low |
| 6 | Ops: the 09:06 lane boot ran without `VOICE_TEST_TOKEN` (mic ws rejected 09:08, fail-closed 4401, driver crash). Always boot lanes via `/tmp/opencode/boot_lane_t4.sh` (it sources the worktree `.env`). | low |
| 7 | `--journal-log /tmp/opencode/t4_lane_8033.log` in `/tmp/opencode/run_driver_t4.sh` never exists (lane doesn't tee; json `journal_lines` always `[]`). Keep the plan's journalctl-export workaround or drop the flag. | low |
| 8 | What the plan got RIGHT: two-box law, root-cause-first (no blind retries), branch law (driver rides iter82 linear), cancel-every-booking, transport parity claims (re-verified), pause-ladder knobs. | — |

## 4. Fix plan (PLAN ONLY — awaits owner GO)

### F1 — fix the booked detector (driver-only, ONE variable)
- File: `/tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py` ONLY.
- Replace the line-541 condition (loose `BOOKED_HINTS` over all-turns join) with the scripted branch's STRONG pattern (lines 482-483): strong phrases ("you're booked", "you are booked", "booked you", "all set for", "locked in", "confirmation", "see you on") matched against the **last agent turn only** (`ear.turns[-1].lower()`), keep the `len(state.caller_turns) >= 2` guard.
- Add to the evidence json: `goodbye_trigger: {phrase, agent_turn_idx}` so any future false positive is visible in the artifact.
- Do NOT touch: brain format, pacing, gaps, persona prompt, engine. Nothing else.
- Commit on `engine/iter82-pause-nudge` (driver rides the iter82 linear branch). Message: `iter82 T3: booked detector strong-phrase + last-turn fix (root cause: false goodbye on "booked jobs" intake question, sid 05c90a2fc483)`.
- Verify: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m py_compile /tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py`.

### F2 — battery gate hardening (discipline, no code)
- PASS requires ALL of: `create_livecall_booking` present in `lf.py tools <trace>`; booking uid captured; cancel 200 printed (User-Agent `diallux-cal-slots/1.0`, `cal-api-version: 2024-08-13`).
- `stop_reason == booked_goodbye` with NO tool call = automatic autopsy trigger, never a pass.

### F3 — ONE battery (original plan T3 flow, unchanged)
1. Fresh lane: `systemd-run --unit=t6-lane-8036 --collect /tmp/opencode/boot_lane_t4.sh 8036`; `curl -s http://127.0.0.1:8036/health` must print `"ok":true`; edit `PORT=8036` in `/tmp/opencode/run_driver_t4.sh`.
2. `systemd-run --unit=t6-driver --collect /tmp/opencode/run_driver_t4.sh`.
3. Poll: `journalctl -u t6-lane-8036 --no-pager -n 500 | grep -E 'create_livecall_booking|final report|stopped'`.
4. If booked: `cd /tmp/opencode/wt-iter82/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/lf.py tools <trace>` → uid → cancel → print 200.
5. Deliverables: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/07_booking_root_cause.md` (content = §2 above) and `08_booking_gate_run.md` (battery report).
- Pass gates: F2 gates + zero wedged turns + continuous chunk flow + expected arc length 18-26 turns.
- On pass: FREEZE the driver, update the master ladder.
- On fail: ONE autopsy row, stop, owner decision. The original plan's T1 questions (caller too thin for discovery heuristics vs STT fragmenting short utterances vs agent re-asks) remain the follow-up candidates — judge them from THIS battery's transcript (Langfuse gens), never pre-emptively.

## 5. Needs owner

| Item | Where |
|---|---|
| GO for F1→F3 | this file |
| Commit the iter82 plan file to OREGON `plans/` (docs → main, LAW 0)? Ride the same commit as this audit? | §3.4 |
