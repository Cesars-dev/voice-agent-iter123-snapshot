# plan_v5_iter82_fake_caller_booking_gate — WHY the fake caller never books: root-cause analysis + instrument fix

## Meta
- Date: 2026-09-28. Supersedes nothing; refines `plans/plan_v5_iter81_master_ladder.md` T2/T3 (read it first: /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md on OREGON = source of truth).
- WORKING MODE (two-box law, unchanged): session runs on FINLAND (MainVps). ALL repo ops via
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<command>"`.
  OREGON hostname = ubuntu-4gb-hil-1. Never run bare repo commands on Finland except reading
  /home/julio/projects/vps-inbox/ and scratch under /tmp/opencode/.
- Project root: /home/julio/projects/clean_diallux_SDR (OREGON checkout = source of truth; Finland copy is a stale mirror).
- Scope: make the fake caller (engine/scripts/llm_mic_caller.py) complete a happy-path booking, using
  root-cause evidence, NOT blind retries. One battery proves the gate, then the driver freezes.
- Status: PLAN ONLY (not started — awaits owner GO)

## Compaction Context
(2026-09-28 session, iter81/iter82 — everything needed to continue without chat history)

**Project:** Dialux SDR v5 voice engine (LangGraph + Deepgram flux STT + gpt-5.4 agent + EL TTS).
Repo /home/julio/projects/clean_diallux_SDR. Boxes: Helsinki 46.62.233.228 (MainVps, session base)
/ OREGON 5.78.83.174 (root, key ~/.ssh/id_ed25519_hetznor, hostname ubuntu-4gb-hil-1).

**Branches (both pushed):**
- `engine/iter80-el-flip-mic-phone-fix` @ `149a8d5` — iter80 EL flip + driver work: room-tone (continuous
  silence streaming in gaps = THE stream-parity fix, PROVEN: 23k chunks continuous, 0 wedged turns,
  barge-ins survived across 5 runs), uncapped caller replies, scripted phased mode (--scripted),
  caller default gpt-4o-mini, wait-question-answer prompt (no unprompted goal push, driver owns pause
  timing via --min-gap/--max-gap flags; the PROMPT must not mention seconds — an LLM cannot pace time).
  Worktree /tmp/opencode/wt-iter80.
- `engine/iter82-pause-nudge` @ `f0fde1b` — STACKED on iter80 tip. Engine FIX 2 pause ladder
  (owner spec: ONE nudge after 15s caller silence: PAUSE_LADDER_MODE=reminder, PAUSE_REASK_MS=15000,
  PAUSE_LADDER_MAX=1, PAUSE_CLOSE_MS=45000; knobs default OFF in /home/julio/projects/clean_diallux_SDR/engine/diallux/config.py;
  implementation in /home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:
  _speak_exact (say.exact — no LLM round, no history), _ladder_arm/_ladder_disarm/_ladder_run/_ladder_close,
  wired at on_twilio_mark (turn-N-done), _late_turn_report (browser arm), _on_start_of_turn (disarm),
  _on_stt_update growth (disarm), stop() (disarm)). Unit tests /tmp/opencode/wt-iter82/engine/tests/test_iter82_pause_ladder.py
  = 5/5 PASS. Worktree /tmp/opencode/wt-iter82. Lane boot script /tmp/opencode/boot_lane_t4.sh sets the
  knob env; driver run script /tmp/opencode/run_driver_t4.sh (port 8033).
- ALSO on iter82: caller-brain format fixes ( CallerBrain.reply now plain-text chat-harness format;
  conversation_pairs now chronological interleave — it was block-appending all-agent-then-all-caller,
  so the small model answered its own last line; facts now land: "15 missed calls a week", "$450").

**Verified TODAY (green):**
- Engine brain (agent gpt-5.4): 10/10 chat calls booked (T0 battery 5/5 luna mock + 3/3 luna REAL slots
  (bookings created then ALL cancelled) + 1 gpt-4o-mini default mock run BOOK Danny 26 turns).
- Live human call (owner, browser mic via Mac SSH local-forward localhost:8030): full arc + REAL booking
  uid soWHP6TM57C37s6MNAPb6Q (cancelled 200). Trace 1666e287ae4d, sid 629e333bd7a9, 51 llm rounds.
- Fake-caller TRANSPORT parity: room-tone = continuous chunk flow identical to live mic; all turns closed;
  e2e 1.1-1.7s; barge-ins survived (6 runs v1-v10, evidence /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/).

**The UNPROVEN gate (this plan's target):** fake caller never completed a booking on the voice lane.
Last run (v10, sid 3dbdca45e4bc, trace 4b9958ed50ee): caller answered facts correctly (15/wk, $450)
but the run hit the driver's turn cap (13) mid-Discovery; agent re-asked some questions. Chat lane
needs 18-26 turns for the same arc -> cap raised to 30 in /tmp/opencode/run_driver_t4.sh, NOT yet run.
Owner verdict 2026-09-28: "cut the attempted tests, continue the plan" — no more blind retries; this
plan replaces them with root-cause analysis first.

**Key facts pinned:**
- Fake caller = Cartesia sonic-3.6 caller voice; agent voice = ElevenLabs (turbo_v2_5/flash; lane health
  prints the active one). Engine lane boots via /tmp/opencode/boot_lane_t4.sh <port> (iter82 engine,
  127.0.0.1). Fresh port per run; systemd-run --collect; NEVER touch prod :8026/:8000-8003.
- Turn reports print `turn N report/final report` in the lane journal; STT states `stt state: StartOfTurn
  (turn N)`; tool lines do NOT print in uvicorn log (only in mic_events + Langfuse).
- Evidence SDK: /tmp/opencode/wt-iter82/engine/scripts/mic_events.py --log <lane.log> --sid <sid> --langfuse
  (lane log = journalctl -u <unit> because boot_lane_t4.sh does not tee to a file; mic_events reads a FILE
  — so `journalctl -u t4-lane-8033b --no-pager > /tmp/opencode/t4_lane_8033.log` FIRST).
- Langfuse at http://46.62.233.228:3001; traces `micbridge-<sid>`; chat traces `llm2llm-graph-<persona>`.
- Scripts lf.py / call.py / live_sql.py / latency_pull.py / sop_mechanicals.py per SOP
  /home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/full_call_analysys.md.
- Chat harness: /tmp/opencode/wt-iter80/engine/tests/llm2llm/harness.py — caller CallerLLM uses
  plain-text user msg ('Agent said: "<last>"\nReply in <=20 words as the customer.') — THIS format books
  with gpt-4o-mini (26-turn run today). The mic driver's CallerBrain.reply was aligned to it (f0fde1b).
- Personas: /tmp/opencode/wt-iter80/engine/tests/llm2llm/personas.py — Danny system prompt carries ALL
  facts (15/wk, 60%, $450, Precision Auto Care, Central, +15123120001, 'Yes, book it.' rule).
- VOICE_TEST_TOKEN in engine .env (worktree); 4401 = gate fail-closed. Cal.com bookings REAL (event
  3801235): cancel every test booking via /home/julio/projects/clean_diallux_SDR/services/cal_slots_endpoint/.env
  CAL_ACCOUNTS first account key, POST api.cal.com/v2/bookings/<uid>/cancel with
  User-Agent 'diallux-cal-slots/1.0' (Cloudflare 1010 otherwise), cal-api-version 2024-08-13.

**Known failure modes observed (to root-cause in T1, NOT to guess):**
- v1: 30-char cap -> thin replies, agent re-ask loops, turn_cap at 14. (fixed: cap removed)
- v3: goal-push prompting -> fixation. (fixed: wait-question-answer prompt)
- v9: conversation_pairs mangled order -> caller answered its own line, "Yeah, go on" x9. (fixed: interleave)
- v10: facts land, agent re-asks ("average repair order worth?" twice) -> SHORT caller utterances may
  fragment/under-deliver via eager EOT adoption, OR the caller is too thin to satisfy the agent's
  discovery-completion heuristics. UNROOT-CAUSED — this is T1's question.
- v11: never observed (owner cut the run).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Agent LLM = gpt-5.4 everywhere (MODEL LAW) | owner; luna banned as agent (zero tool calls, API forbids effort!=none + tools) |
| Caller = gpt-4o-mini, temperature 0.3 (or omitted on gpt-5-family — API constraint) | owner pins 2026-09-28; chat lane books with it |
| Caller prompt = WAIT for agent's question, answer ONLY it; intent passive; NEVER count seconds in prompt | owner: "wait-get question-answer thats it" |
| Room-tone stays (proven stream parity); C3 answer-first prompt stays REVERTED | caused goal-fixation |
| Scripted phased mode exists (--scripted) for transport tests only, NOT the booking instrument | owner: agent improvises, fixed script desyncs |
| Engine fixes on NEW branches stacked from iter82 tip f0fde1b; driver/harness commits ride the iter82 linear branch | LAW 0 + owner option 2 branch law |
| Every fix gated: ONE battery through the driver + §11.1 pass signals + owner ear A/B + HITL stop | master plan law; no blind retries |
| Test bookings CANCELLED immediately after each run | Cal.com 3801235 REAL |
| Stop root-causing when the booking gate passes ONCE clean; then FREEZE the driver | owner: instrument must not drift |

## BLOCKED / NEEDS INPUT
| Item | Where |
|---|---|
| Owner GO to start T1 | this plan |
| If T2 fix touches ENGINE code (not just driver): new iterNN assignment at branch cut | owner/plan law |

## Environment & Dependencies
- OREGON root@5.78.83.174; repo /home/julio/projects/clean_diallux_SDR; venv
  /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python (pip: `<venv>/bin/python -m pip` ONLY).
- Worktrees: /tmp/opencode/wt-iter80 (iter80 @ 149a8d5), /tmp/opencode/wt-iter82 (iter82 @ f0fde1b, has
  driver + ladder + .env copied from wt-iter80 incl VOICE_TEST_TOKEN + CARTESIA keys).
- Lane: /tmp/opencode/boot_lane_t4.sh <port> (iter82 engine + PAUSE_LADDER knob env ON).
- Driver: /tmp/opencode/run_driver_t4.sh (port 8033 hardcoded — edit PORT when lane port changes;
  flags: --scenario happy --persona Danny --agent-idle-s 5.5 --max-turn-wait 60 --min-gap 2.5 --max-gap 6
  --max-caller-turns 30). Driver out: /tmp/opencode/t4_fake_v8.json (overwrites each run).
- Langfuse server http://46.62.233.228:3001 (keys in wt .env LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY).
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (read via /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -c sqlite3; SDK scripts/live_sql.py).

## Architecture (one block diagram)
```
Cartesia sonic (caller voice) -> 20ms PCM frames --WS /mic/ws?k=TOKEN--> flux STT -> eager EOT
   CallerBrain gpt-4o-mini (persona + wait-answer)  -->  agent gpt-5.4 (graph, tools) --> EL TTS
   room-tone zero-frames between bursts (iter80)  |  engine: 15s silence -> "are you still there" (iter82 knob)
```

## File Map
| File (absolute path) | What | When |
|---|---|---|
| /tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py | THE driver — brain format already fixed; next: whatever T1 root cause demands | T2 |
| /tmp/opencode/wt-iter82/engine/diallux/media/session.py | engine pause ladder (knob OFF default; lane env turns ON) | unchanged this plan unless T1 finds engine fault |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/07_caller_root_cause.md | THE root-cause report (T1 deliverable) | T1 |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/08_booking_gate_run.md | battery report + freeze declaration (T3 deliverable) | T3 |
| /tmp/opencode/wt-iter80/engine/tests/llm2llm/personas.py | Danny persona facts (READ-ONLY reference) | ref |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/02_live_call_baseline.md | THE baseline the instrument must match | ref |

## Deploy Rules
- NEVER checkout/switch/reset/pull the Oregon prod checkout; worktrees only.
- NEVER touch diallux.service / :8026 / :8000-8003. Lanes: /tmp/opencode/boot_lane_t4.sh, fresh port,
  systemd-run --collect, killed at session end.
- NEVER inline `&` in ssh; pkill self-match hazard: use bracket pattern 'llm_mic_[c]aller'.
- Cancel every test booking created (uid from create_livecall_booking response or lf.py tools).

## Tasks (in order)

### T1 — ROOT CAUSE: why the arc stalls in Discovery / why the agent re-asks
Goal: name THE reason the fake caller's arcs died at turn cap with the agent re-asking answered questions,
using evidence per turn — transcript text the AGENT actually received (Langfuse gens input) vs what the
caller TTS spoke (driver json caller_turns), plus STT turn reports.
Commands (all via the ssh wrapper, on OREGON):
1. `journalctl -u t4-lane-8033b --no-pager | grep 3dbdca45e4bc` (v10 evidence, lane already dead — use saved logs:
   /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/ has t1/t2 logs; for v10:
   `journalctl -u t4-lane-8033b --no-pager > /tmp/opencode/v10_lane.log`)
2. `cd /tmp/opencode/wt-iter82/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/lf.py gens 4b9958ed50ee`
   — read EVERY gen: does the user_text/context the agent saw contain the caller's spoken facts?
3. `cd /home/julio/projects/clean_diallux_SDR && python3 scripts/sop_mechanicals.py /tmp/opencode/wt-iter80/engine/tests/llm2llm/json_logs/BOOKDanny_l2l-bookdanny-6b3f50e7.json`
   — the CHAT reference arc for contrast (what the caller said when it worked).
4. Compare per-turn: agent question -> caller TTS text -> what STT committed (turn reports user_text via
   `mic_events.py --log /tmp/opencode/v10_lane.log --sid 3dbdca45e4bc --langfuse`).
Verification: root cause named with 3+ quoted evidence lines (agent heard X, caller said Y, engine did Z).
Deliverable: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/07_booking_root_cause.md
Dependencies: none. Unblocks: T2.

### T2 — the instrument fix (driver only; commits on iter82 linear)
Goal: change ONLY /tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py per T1's root cause.
Candidate fixes BY ROOT CAUSE (do exactly the one T1 convicts, nothing else):
- Caller too terse for discovery-completion heuristics -> CallerBrain reply length floor: instruct
  "give the number AND one short reason sentence" (prompt-only, in /tmp/opencode/wt-iter82/engine/scripts/llm_mic_caller.py PACING_PROMPT).
- Caller answers land but agent can't extract (STT ate them) -> raise --agent-idle-s to 6.5 and/or caller
  dur (slower Cartesia speed) — config only in /tmp/opencode/run_driver_t4.sh.
- Agent's discovery-completion needs numbers EARLIER -> re-order what the caller volunteers when asked
  "what about the ad" (persona fact phrasing) — prompt-only edit.
- Turn pacing (2.5-6s gaps) collides with eager EOT -> widen --min-gap to 3.5.
Files: driver + run script ONLY. NO engine changes (if T1 convicts the ENGINE, STOP and report — engine
fixes need their own branch per LAW 0; ask owner).
Verification: `cd /tmp/opencode/wt-iter82/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m py_compile scripts/llm_mic_caller.py`.
Commit message: `iter82 T3: caller <what changed> (root cause: <T1 finding>)`.
Dependencies: T1. Unblocks: T3.

### T3 — THE booking-gate battery (one run, no blind retries)
Goal: fake caller books ONCE through the whole voice lane with the ladder knob ON.
Commands:
1. Lane (fresh port if 8033 busy): `ssh ... "systemd-run --unit=t5-lane-8035 --collect /tmp/opencode/boot_lane_t4.sh 8035"` (edit PORT in /tmp/opencode/run_driver_t4.sh to 8035 first).
2. Health: `curl -s http://127.0.0.1:8035/health` must print `"ok":true`.
3. `systemd-run --unit=t5-driver --collect /tmp/opencode/run_driver_t4.sh`
4. Poll: `journalctl -u t5-lane-8035 --no-pager -n 500 | grep -E 'create_livecall_booking|ladder rung|stopped'`
5. On booking: get uid `cd /tmp/opencode/wt-iter82/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/lf.py tools <trace>` → CANCEL it (v2 cancel script pattern, User-Agent diallux-cal-slots/1.0).
Pass gates (ALL must hold):
1. stop_reason == booked_goodbye (create_livecall_booking fired, booked=true)
2. zero wedged turns (every StartOfTurn -> eot adopted/turn report)
3. chunk flow continuous (no >30s gap; room-tone proven)
4. IF the test includes a deliberate >15s pause: `pause_ladder:nudge` span + "are you still there" heard
   (owner's knob test — only if owner asks for it in this run)
5. booking CANCELLED after (print the cancel 200).
Deliverable: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/08_booking_gate_run.md
Dependencies: T2. Unblocks: FREEZE + master-plan update (owner sees the report, then plan STATUS flips).

## Validation Plan (end-to-end)
1. T1 root cause quoted from traces -> 2. T2 single targeted fix -> 3. T3 battery passes ALL gates ->
4. owner reads 08 report -> 5. master plan updated (T3 frozen / T4 unblocked). Abort: if T3 fails, ONE
autopsy row (no second run without owner).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| 4 stale delivery/iter44 suite reds | parked test debt (owner knows) |
| FIX 7/5/8 wave-1 batteries | T4 of master ladder — needs the frozen instrument first |
| Ear A/B of the 15s nudge | separate owner listening session |
