# plan_v5_iter81_master_ladder — THE master plan: instrument trust → fake-caller parity → turn-taking fix ladder

## Meta
- Date: 2026-09-27. Supersedes `plans/plan_v5_iter81_fake_caller_human_parity.md` (absorbed 100%: T0 verdict, room-tone patch, gates).
- WORKING MODE (default, read this first): the session runs on FINLAND = Helsinki box (MainVps, 46.62.233.228, user julio).
  OREGON is a REMOTE box reached ONLY over ssh - every repo command is typed on Finland and executed on Oregon:
      ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<full command>"
  NOTHING repo-related runs bare on Finland except: reading reference copies (the 2 owner MDs in
  /home/julio/projects/vps-inbox/ ; the stale clone /home/julio/projects/clean_diallux_SDR ;
  /home/julio/projects/diallux_sdr_almost_there_b) and temp scratch under /tmp/opencode/ (Finland-local).
- SESSION BOOTSTRAP - who am I? (run this FIRST in every session, before anything else):
      hostname
    * MainVps -> you are on FINLAND (default session base). ALL repo ops go through the ssh wrapper
      shown above; repo files on Finland are NEVER edited (scratch under /tmp/opencode/ only).
    * ubuntu-4gb-hil-1 -> you are on OREGON directly. Run repo commands bare (no ssh wrapper).
    * anything else -> STOP and ask the owner which box you are on; never guess.
- Finland-local plan copy: this plan is ALSO pulled to the SAME path on FINLAND (via git fetch from
  origin/main after every docs push) - READ it there, but EDIT it on Oregon only (source of truth = origin/main).
- ONE PATH, TWO BOXES — the classic trap: /home/julio/projects/clean_diallux_SDR exists on BOTH boxes.
  On OREGON it is the LIVE repo (prod checkout on engine/iter73-oregon-wip-20260924 @ df23d37 + worktrees
  /tmp/opencode/wt-iterNN). On FINLAND it is a STALE reference (branch engine/iter76-harness-firesim).
  A bare "git -C /home/julio/projects/clean_diallux_SDR ..." on Finland reads the WRONG tree. Wrap EVERY
  repo command in the ssh line above.
- ALL file paths in this plan and in chat are FULL ABSOLUTE PATHS on their owning box (OREGON for the repo;
  FINLAND only for vps-inbox MDs and Finland-local scratch). No relative paths ever.
- vps-inbox MDs live on FINLAND: /home/julio/projects/vps-inbox/voice-sdr-turn-taking-fixes.md and
  voice-sdr-turn-taking-research.md (copies also on OREGON, see File Map).
- Docs push quirk: commit docs on main via a temp worktree, but PUSH from the prod checkout path (the
  worktree push fails on the relative gh-creds credential path - known quirk, not an error to fix).
 
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "..."`.
  Helsinki (`46.62.233.228`) = session base; never edit repo files there.
- Scope: ONE file carries the whole ladder. Doctrine: **trust the instrument before fixing the engine** —
  (1) prove the brain works cheaply (chat lane), (2) capture a REAL-call baseline (live call, fully traced),
  (3) diff the fake caller against it (byte/stream behavior), (4) tighten the fake caller to parity and FREEZE it,
- Status: PLAN ONLY (T0 assessment verdict DONE; all code work awaits owner GO per task)

## STATUS — read this first (updated at EVERY session close)
- Working mode: FINLAND session box; ALL repo ops = ssh-wrapped commands to OREGON (see WORKING MODE in Meta) - never touch /home/julio/projects/clean_diallux_SDR bare on Finland
- NEXT SESSION (owner 2026-09-30): open plans/plan_v5_iter88_intake_refer_drill.md and work IT —
  T0 = owner GO on the ONE-LINE Intake.md:35 refer-tag rewrite (PT-74) + T2 FIND-9 drill scope;
  plus owner ear/merge on engine/iter87-prewarm-hold @ 02eb2ac (UNMERGED, battery PASS).
- SESSION ADDENDUM 2026-09-30 (latency analysis + THE BUG): ledger run iter87-hold-battery
  imported (calls=2); TTFT p50 853 (gate PASS), cache-0 rounds=1 (Closing same-state trim),
  cache-hit p50 4736; LIVE e2e p50 1385/1321, p90 blown by the PRE-EXISTING S2L spikes
  (hysteretic trim, next surface). G1 FAIL root cause DRILLED to ONE prompt line:
  engine/diallux/prompts/Intake.md:35 — the delivery instruction "for the empathic mirror"
  leaked INTO the refer tag anchor (written in the 2026-09-08 restructure b94dad4, carried
  22 days; fix1 baselines fail identically) -> 16/17 Intake retrievals 0-chunk. Recorded:
  PENDING_TASKS PT-74 (1-line fix, code zone, LAW 0) + findings FIND-9 fix_note updated.
  Report: research/surgeon/iter87-prewarm-hold/02_latency_report.md.
- SESSION CLOSE 2026-09-30 (iter87 VERSION B EXECUTED — THE DETERMINISTIC HOLD): owner design captured
  verbatim (07_owner_design_capture.md), surgeon procedure tasks/surgeon/iter87-prewarm-hold/ (audit/action/cross-ref/master
  plan, owner GO granted), branch engine/iter87-prewarm-hold CUT from 542d3e8 @ 02eb2ac (pushed; builder.py 6 sites +
  config.py 1 knob warm_await_dest_ms default 0 = byte-exact, gates fire+hold as ONE unit; +10ms settle per owner).
  Battery PASS: 2 lanes 8047/8048 happy+barge — ZERO cold destination rounds (K1 FIXED: chain warms landed
  VerifyLead/Booking/Closing), 0 no_task, 0 timeout (fence never bound), eager_final_match 100%, suite 7 stale
  reds / zero new; known trade: eager acks hold ~1-1.6s for in-flight warms (uperm p50 1175/1048 vs baseline 867).
  Bookings 1jSTGwyxzWV7KyfK7SceeE + 6kg7LgGwiq8eJjy7VoJ4jQ CANCELLED 200, 0 upcoming. Ledger forensics_calls rows
  13-14 appended. Reports: research/surgeon/iter87-prewarm-hold/ (01_battery_verdict.md + 2 SDK outputs).
- SESSION CLOSE 2026-09-30 (Real_MVP MERGE — LOCAL ONLY, FROZEN BOX): iter80-87 chain MERGED to the main line @ merge commit 730dfdb in worktree /tmp/opencode/wt-merge87 (conflicts x4 resolved chain-side = iter80-audited battery-proven versions; speech_replay.py + iter66 test pins auto-kept from main). GitHub PUSH IMPOSSIBLE + FORBIDDEN: owner deleted the GitHub PAT from BOTH boxes 2026-09-30 (gh-creds files removed; credential.helper now fails closed) — origin/main stays @ 50ecbaa until owner rotates the token; FROZEN BOX LAW: Oregon local = source of truth, no pushes, no pulls, Finland = untouched backup. Merge validation PASSED: suite 3 stale reds (was 7 on chain — main's iter66 test pins healed test_delivery x4; zero new); live mic validation call (micbridge-cede46476d35, Danny happy, frozen driver) = latency BETTER across the board (uperm p50 1,005 vs 1,176; E2E p50 1,196 vs 1,385; turn-1 682; ttft p50 795; cache0=0; eager match 100%; 0 cold destination rounds — K1 intact). SOP audit (4 planes, report research/surgeon/iter87-prewarm-hold/03_merge_validation_sop_audit.md, 40 sops rows persisted): SAME behavior as chain — R5.5 in-generation verbatim dupes on BOTH trees (t29/t33 vs t36), re-ask loops, Discovery ~10-round shape pre-existing; ONE divergence: leak-reveal speech SKIPPED on the merge call (calculate_monthly_leak returned weekly_leak 4,050 / monthly_leak 17,500 — model read it into extract_closer_details but never SPOKE it; caller never declined; model violated no-empty-text-with-tools x2 + reveal-weekly-first) — single sample, prompts byte-identical, watch on next battery. Chat-lane audit: harness.py delta vs last chat-battery code (2a36c94) = 2 lines; builder delta vs 02eb2ac = EMPTY — chat lane runs the exact battery-proven builder; chat drill of the reveal pattern costs ZERO TTS tokens. NEXT SESSION = plans/plan_v5_iter88_chat_leak_drill_and_intake_fix.md (supersedes plan_v5_iter88_intake_refer_drill.md — absorbed 100%): chat-lane leak-reveal pattern drill + PT-74 one-line Intake fix + md/llm.json lockstep doc + 9-state parity pin. Master ladder = as good as it gets; the ONE pending = PT-74 KB-less state fix + the discovered prompt issues.

- Current task: T4 wave 1 — FIX 7 battery DONE (PASS 2026-09-28); FIX 5 battery DONE (PASS, owner-500ms gate, 2026-09-28); FIX 1 battery DONE (PASS 2026-09-29, eager hold BANKED).
- SESSION CLOSE 2026-09-29 (FIX 1 EXECUTED — PASS + DELETES): branch engine/iter85-eager-hold CUT from
- Session close 2026-09-29 (iter86 forensics + harness-fidelity session): FIX 1 (eager hold) EXECUTED+PASS on engine/iter85-eager-hold @ 542d3e8 (UNMERGED, owner merge pending); forensics SDK committed (engine/scripts/call_forensics.py, branch engine/iter86-warm-sync @ d158b4c, pushed); Step-A commit-history verdict: no E2E regression on fix1, transition tails predate fix1, fake caller 3x faster-paced than real (calls by commit registered in ledger forensics_calls, 12 rows); OWNER REJECTED the warm-sync fix proposal (chain-path warm / WARM_AWAIT_MS / one-ahead) - superseded by his own prewarm design (see plans/plan_v5_iter87_prewarm_owner_design.md; plan_v5_iter86 DEPRECATED); OpenAI key rotated both boxes; reports research/surgeon/iter86-warm-sync/ (01..04) + public mirror github.com/Cesars-dev/diallux-voice-engine-iter86.
  0693a9d + PATCHED (SentenceGate hold/release/discard primitives + add() held early-out + end_of_turn parks
  _held_final + reset() clears hold; session _eager_held wiring: hold in _run_turn after TTS-context mint,
  release at _on_eot adopt, silent-discard FIRST branch in _on_turn_resumed; declared adaptation:
  _graceful_cap_close clears a stale hold; owner-requested measurement trace spans eager_hold:fire
  [silence_ms], eager_hold:release [hold_to_release_ms], eager_hold:false_start [held_ms]; knob
  eager_hold_audio_until_confirm default False) COMMITTED b97957f + PUSHED; 6 unit tests (test_iter85_eager_hold.py)
  -> targeted 20/20 green, full suite SAME 7 stale reds, zero new; T3 DELETES separate commit 542d3e8
  (_grace_then_cancel + eager_resume_grace_ms knob + guarded-mismatch branch + iter38 dance deleted; adopt
  unconditional; 4 iter46 grace tests rewritten to post-delete contracts; suite re-verified same 7 reds).
  Battery TWO param rounds (frozen driver, lanes 8045/8046): ROUND A owner-first-read mapped WRONG by agent
  (eager 0.55 + eot_timeout 600) — TRACE-PROVEN HARMFUL: 600ms backstop forced EOT mid-utterance (fragmented
  the driver's barge line, orphaned the tail, 11s dead air, driver abort no_agent_speech_barge); eager@0.55
  fires at silence p50 161ms. ROUND B owner correction (eager_eot_threshold=0.35 CONFIDENCE, eot_threshold=0.65,
  eot_timeout_ms=3000 — Flux has NO ms-deadline for eager, confidence-gated only; docs verified): happy run
  turn-1 e2e 963.5 (<1000 gate PASS FIRST TIME), head_start p50 280ms BANKED (was ~41 unbanked @0.70),
  e2e p50 1120 (baseline 1180), eager_final_match 30/30; barge-loop round 1 aborted on a DRIVER-TIMING
  artifact (agent replies end before driver's barge speech ends; next ladder rung @15s lands after the
  driver's 60s abort) -> lane env PAUSE_REASK_MS 15000->8000 (declared env-only deviation, driver FROZEN
  untouched) -> barge-loop COMPLETED booked_goodbye 32 caller turns: 45 eager fires -> 10 silent discards,
  0 tts.cancel, 0 held-path clears, eager_final_match 31/31, REAL booking q3DWLDMQbZHs7hZngaxHZo (cal id
  25987397, diallux_live acct) CANCELLED 200. Post-battery call audit (04) + deep latency forensics (05):
  REAL per-round LLM TTFT p50 ~695ms (BETTER than baseline 770-793 — turn-level stt_eot_to_llm is
  eager-anchor-contaminated at 0.35, eager fires ~80ms into speech growth); transition turns E2E 2.3-4.6s
  user-perceived = round-A (ack + TOOL-JSON tokens generated serially, 120-185 tok) + tools + round-B TTFT
  — 2-trip structure BY DESIGN, not a regression; ttft=None on tool rounds = logging gap (ttft_s stamps
  only on token events, builder.py:2271); 3 destination rounds cache_read=0 (t30 ConfirmSlots, t38/t41
  Closing) = warm LOST THE RACE on short transition chains + NO warm:Closing span exists; costs: b3 312k
  in/2.1k out ~$0.63 (blended-est, price table placeholder) vs 0.70-baseline bargeloop 296k = +5.4% input
  tokens (eager-0.35 round churn, 45 fires/32 turns = 1.4x); eager churn is SEQUENTIAL (one turn at a time,
  fires refused while running) not parallel — owner async-release-by-transcript-ID idea = iter86 design
  task. 21 SOP rows in ledger (CALL: FSM/tools/flow PASS, repetition R5.5 FAIL verbatim dupes t25/26+42/43,
  fragments t10/t34 spoken = TTS-channel flush/barge-edge loss -> FIX 3 lever, SALES 12/14 hire-band,
  HUMANIZED R5 FAIL); ledger runs fix1-happy/fix1-bargeloop @ b97957f (micbridge import via patched-module
  pattern — fetch_traces name filter drops micbridge before window check, must replace whole fetch).
  Booking cancelled; lanes 8045/8046 + all fix1 units torn down, ports 0. PENDING HITL: owner ear A/B for
  FIX 1 + eager-0.35 keep-vs-revert (round churn cost) + FIX 7 ear A/B (from iter83). NEXT SESSION =
  plans/plan_v5_iter86_warm_sync_call_fidelity.md (warm-await fix + harness call-fidelity + forensics SDK;
  branch from 542d3e8).
- SESSION CLOSE 2026-09-28 (FIX 5 EXECUTED — PASS): branch engine/iter84-post-interrupt-backoff CUT from
  fa62162 + PATCHED (config knob post_interrupt_backoff_ms default 0, stamp _backoff_until in _on_start_of_turn
  interrupted branch per DECLARED adaptation — _barge_resolve is a FIX 4 primitive absent at fa62162, one-shot
  wait in _speak_chunk first-request guard before t_tts_req stamp) COMMITTED 0693a9d + PUSHED; tests 4 new
  (test_iter84_backoff.py) -> targeted 14/14 green, full suite SAME 7 stale reds (test_delivery x4, iter46,
  iter59, iter60 — zero new); battery via frozen driver + lane 8043/8044 (boot_lane_t4_fix5.sh,
  POST_INTERRUPT_BACKOFF_MS=500): fix5-b (barge-in-only, e0dc48afb4ff — greeting barge, zero overlap),
  fix5-happy control (7db172d1efbd — 31 turns, ZERO barge-ins, zero waits, llm->tts p50 204.7ms vs baselines
  202.6/206.1 = zero latency added), fix5-bargeloop (09a4a1ac8108 — OWNER-ORDERED: driver variant
  llm_mic_caller_b52.py scenario barge-loop + --max-caller-turns 52; 4 scripted barges + 1 natural interrupt;
  every barge = agent audio killed 0.5-0.8s, reply e2e 1.3-1.4s; the 500ms window NEVER binds live — engine
  never re-speaks within 500ms of a barge; booking biZAhvfspYogdbBffGefna created + CANCELLED 200 cal id
  26001405); OWNER DECISIONS 2026-09-28: keep backoff at 500ms (insurance, revisit after FIX 1 — eager-adopt
  path is where it can bind); VOICE LAW CORRECTED in AGENTS.md on main @ 4159f30 (ElevenLabs DEFAULT — prod
  Hannah ZSNL4hPqCnqoMPaI4jGX speed 1.0/stability 0.6/style 1.0 + py playback accel 1.08-1.15, tests keep
  Sarah, Cartesia ONLY for HIPAA/lower-quality deployments+tests, "out of this world" verdict corrected — it
  was vs sonic-3.6 not the current model); driver variant committed aaba8ff on engine/iter82-pause-nudge;
  lanes 8043/8044 torn down + ports 0; ledger runs fix5-b/fix5-happy/fix5-bargeloop @ 0693a9d (import trap:
  live_sql.py fetch_traces name filter hardcodes llm2llm-graph-/diallux-call — micbridge imports need the
  locally-patched-module pattern, PT candidate); report research/surgeon/iter83-t4-wave1/02_fix5_battery.md;
  pending HITL: FIX 7 ear A/B (from iter83); FIX 5 ear A/B = moot (no audible change live).
- SESSION CLOSE 2026-09-28 (FIX 7 BATTERY EXECUTED — PASS): branch engine/iter83-stt-liveness @ fa62162 tested as-built; Scenario A age-gate PASS (prewarm ON via boot variant boot_lane_t4_fix7_pw.sh — env-only deviation, CALL_PREWARM=false had made the frozen boot untestable; 'prewarm: refused stale stt (age > 120s)' @ +136s -> fresh connect +141ms -> normal 288s arc, trace 1acda411a0ff); Scenario B PASS — hard-kill (ss -K) fires the PRE-EXISTING instant reconnect (transparent reconnect proven healthy, not a FIX 7 test), true silent-zombie lever = iptables OUTPUT DROP on the STT conn: watchdog fired 15.8s (mic chunks=7840, audio flowed), single stt:zombie_reconnect span (trace 2f625c70052a), turns continued, ZERO false fires, reconnect-completion delay (~29s) = lever artifact (DROP rule blocked close handshake), tuning note §8.4; NO bookings created anywhere; lanes 8039/8040/8041/8042 killed + ports verified 0; iptables rule removed; T4 latency scorecard (owner add, LATENCY-PERCENTILE-SOP): FIX 7 zero latency cost (B2 best p90 1353), e2e p50 ~1.2s LLM-bound (gpt-5.4 TTFT ~770-790 = ~65% of turn), ~300ms eager overlap UNBANKED (head_start ~40ms @0.70, eager_final_match 100%) -> FIX 1 eager hold + threshold 0.65 = the lever (turn-1 e2e ~1064 -> ~760-860, p50 -> ~0.9s); ledger runs fix7-sanity-ref/fix7-a2/fix7-b1/fix7-b2 @ fa62162 imported; report research/surgeon/iter83-t4-wave1/01_fix7_battery.md; BLOCKED ON: owner ear A/B (FIX 7 HITL) + owner call on fix order (FIX 5 next per plan, or FIX 1 pulled forward)
- SESSION CLOSE 2026-09-28 (T1 FIX 7 build DONE, battery PENDING): iter82 ladder files COMMITTED to engine/iter82-pause-nudge @ 4459f9f (5/5 green, pushed); FIX 7 branch engine/iter83-stt-liveness CUT @ 4459f9f + PATCHED (prewarm.get max_age_s age gate + deepgram_stt._last_rx heartbeat on adopt/fresh/recv + session watchdog _stt_liveness_watchdog fires existing _on_stt_disconnect + knobs STT_ADOPT_MAX_AGE_S=120/STT_RX_ZOMBIE_MS=15000, 0=off) COMMITTED fa62162 + PUSHED; tests 5/5 new (test_iter80_stt_liveness.py) + ladder 5/5 loop-hardened (asyncio loop fix), full suite = SAME 7 stale reds as iter82 base (4 delivery + iter46 + iter59 + iter60), ZERO new; ENV LAW learned: fresh worktree needs engine/.env copy (test_iter44 401 false-red — now a Deploy Rule @ 069d76d); sanity baseline run done BEFORE fixes (lane 8037, driver frozen): booking gate FAILED turn_cap_goodbye 31/30 turns — arc bloat via duplicate one-word caller turns + 5-round discovery; report research/surgeon/iter83-t4-wave1/00_sanity_baseline.md; NO booking created (nothing to cancel); lanes 8037/8038 verified KILLED; NEXT SESSION: FIX 7 battery Scenarios A (age-gate corpse refusal, timestamp backdate) + B (mid-call socket kill -> zombie_reconnect span <=15s) via boot_lane_t4_fix7.sh (wt-iter83a, fresh port), then §11.1 + ear A/B + HITL — per-fix loop (branch from d70c438, MD patch, unit tests, ONE battery through the FROZEN driver, §11.1, ear A/B, HITL)
- Next task: T5 wave 2 (FIX 1 eager hold / FIX 4 ack filter) after wave 1 batteries + owner ear A/B
- Blocked on: owner GO for the FIX 1 session (new plan per SOP); FIX 7 ear A/B (HITL, from iter83)
- Branch law (owner 2026-09-28): OPTION 2 - iter80 stays UNMERGED until owner says production grade; driver commits ride iter80 linear; engine fix branches stack from ef627ba
- Last session: 2026-09-28 — FIX 5 executed (see SESSION CLOSE above); before that: BOOKING GATE PASSED: v14 (sid 71ca29961a6c, trace 17ed3274dafd) booked uid 88jbmgqNZsQQcWQ9AqYiS1 -> cancelled 200 (cal id 25984606); 3 root causes fixed (false booked_goodbye, empty dvs callback_number, caller drift -> gpt-4.1-mini); driver commits pushed @ d70c438; reports 07/08 written; OREGON now pushes to GitHub (gh-creds)
- Instrument status: fake caller FROZEN + TRUSTED (booking gate PASS 2026-09-28, @ d70c438, run script /tmp/opencode/run_driver_t4.sh) — T4 batteries may run
- Evidence index: research/surgeon/iter81-fake-caller-human-parity/ (00_assessment.md + 01_chat_brain_report.md exist)
- iter80 branch tip now 2a36c94 (T0 caller-compat + owner temp 0.3 pin commits on top of ef627ba; worktree wt-iter80 matches)
- Owner pin 2026-09-28: caller temperature 0.3 in CallerLLM (gpt-5-family callers reject ANY temperature - API constraint, knob omitted for them)
- OWNER NOTE 2026-09-28 (T4 wave 1 params): FIX 5 backoff owner-specified to **500ms** (`POST_INTERRUPT_BACKOFF_MS=500`, not the MD's 1000ms). FIX 8 soft filler kept at 3000ms BUT owner already has filler words (in the agent's own phrasing/prompt) — wave-1 battery must CHECK FOR REDUNDANCY (double-filler: knob filler + existing filler words in answers); full verdict deferred until we hear the battery ("check for redundancy, but later"). Params recorded here + in iter83 plan execution.

## Compaction Context
(iter80 session 2026-09-26 + iter81 T0 assessment 2026-09-27 + seam verification 2026-09-27)

**Project:** Dialux SDR v5 voice engine (LangGraph + Deepgram flux STT + gpt-5.4 + EL TTS), repo
`/home/julio/projects/clean_diallux_SDR`. Boxes: Helsinki 46.62.233.228 (reference) / OREGON 5.78.83.174
(root, key `~/.ssh/id_ed25519_hetznor`, hostname `ubuntu-4gb-hil-1`). Oregon prod checkout: branch
`engine/iter73-oregon-wip-20260924` @ df23d37 — NEVER checkout/switch/reset/pull there. Engine worktree:
`/tmp/opencode/wt-iter80` on `engine/iter80-el-flip-mic-phone-fix` @ ef627ba (pushed, unmerged, clean).

**iter80 recapped:** EL adapter fork + EL plumbing sync + fake-caller driver ported + pacing tweaks; 7 smoke runs;
branch UNMERGED (LAW 0). Prod :8026 diallux.service restored + verified after tests.

**iter81 T0 verdict (DONE, evidence `research/surgeon/iter81-fake-caller-human-parity/00_assessment.md`):**
fake caller starves the engine's flux STT between bursts (sends frames ONLY while speaking; real mics stream
always). Flux closes turns ONLY on RECEIVED trailing silence — starved gap = no evidence; the engine's
`deepgram_eot_timeout_ms=2500` backstop counts received silence only. Run 7: flux turn 3 never finalized →
engine mute 65s → driver talked 10 bursts into the void. Engine exonerated (callback completed, fresh socket,
survived both barge-ins). Fix = room-tone task in the driver (owner's proposal, adopted + 4 integration pins).

**Seam verification (2026-09-27, read-only):** the 2 owner MDs' patches were mapped against snapshot 0ce798f;
`media/session.py`, `media/sentence_gate.py`, `media/deepgram_stt.py` are **md5 byte-identical** between that
snapshot and wt-iter80 @ ef627ba; every cited anchor exists at its cited line (_on_eager_eot:466,
_on_start_of_turn:583, _update_fired:601, _last_update_len:604, KeepAlive:169). Patches apply as-written.
`config.py` DIVERGED (88381a2 added EL knobs) — the knob-registry patch needs an adaptation diff.

**Chat lane (brain test):** `engine/tests/llm2llm/harness.py` — `--transport graph --personas happy --slots mock
--langfuse --caller-model <model> --agent-model gpt-5.4`; no voice layer; personas from tests/llm2llm/personas.py.
luna = gpt-5.6-luna: banned as AGENT (reasoning_effort=none → zero tool calls; API forbids effort≠none + function
tools on chat/completions); FINE as cheap chat CALLER (caller never calls tools in the harness).

**Voice test orchestration (proven):** Oregon `/tmp/opencode/boot_lane.sh <port>` (worktree uvicorn 127.0.0.1),
`/tmp/opencode/run_driver.sh <port>`, `/tmp/opencode/smoke_orchestrator.sh <port>`; launch
`systemd-run --unit=<name> --collect ...`; health grep `"ok":true` (NO space); WS `?k=$VOICE_TEST_TOKEN`
from worktree .env. Fake caller: `engine/scripts/llm_mic_caller.py` (Cartesia sonic-3.6-2026-08-27 voice,
Deepgram flux ear, LLM brain, scenarios happy/barge-in-only/dump-only/watchdog).

**Pins:** agent model gpt-5.4 (MODEL LAW); EL Sarah uG1JFy6xppqckhHCs2KG turbo_v2_5 1.06/0.5/1.0/0.75;
EL credits ~112,691 left (reset Oct 22 20:50 UTC); smoke ≈ $0.07-0.16, booking call ≈ $0.45-0.65.
Services read-only :8001/:8002/:8003; Cal.com event 3801235 REAL — cancel every test booking.
Langfuse `http://46.62.233.228:3001`, traces `micbridge-<sid>`; ledger SQL per SOP.

**The 2 owner MDs (the fix ladder's source, carried 3 locations):**
`/home/julio/projects/vps-inbox/voice-sdr-turn-taking-fixes.md` (F1-F6 graph; knob registry §1; FIX 1-8 patches
with code + tests + rollout; ship order §10.1: wave1 FIX 7/5/8 → wave2 FIX 1/4 → wave3 FIX 6/3/2; pass signals
§11.1; abort flags §10.3) and `voice-sdr-turn-taking-research.md` (F-table, dossiers D1-D11, PORT list 1-8).
Copies: `research/surgeon/iter80-el-flip-mic-phone-fix-src/` + `tasks/surgeon/iter80-el-flip-mic-phone-fix/`.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Trust pyramid BEFORE any fix: chat brain test → live real call trace → fake-vs-real diff → tighten fake caller → freeze | owner: "stop wasting tokens on something that might not work"; "we dont fix sht that wont exist" — batteries only mean something once the instrument matches a real call |
| Driver/harness changes = commits on the LINEAR branch `engine/iter80-el-flip-mic-phone-fix` | owner + suffix law: engine/scripts changes ride iterNN; no new branch for test-harness work |
| Engine code: NEW branch per fix, STACKED from engine/iter80 tip ef627ba (unmerged) - option 2, owner 2026-09-28: NO merge until owner declares production grade; iter73-oregon-wip = harvest-and-abandon candidate (its 2 engine deltas already upstreamed: 471e50c, 3829d16) | owner pick 2026-09-28; fixes MD 10.1; iterNN assigned at cut time (MD branch names are placeholders) |
| Every fix is gated: battery through the FROZEN fake caller + §11.1 pass signal + owner ear A/B, then next | owner: "we test the desired outcome on every fix then we move to the next step" |
| Fake caller FROZEN after T3 passes; any later driver touch = ledger note in this file | battery deltas must measure the ENGINE fix, never harness drift |
| Room-tone fix ADOPTED (owner's proposal + 4 integration pins) | restores real-mic contract; root-cause fix for the wedge (proof: 00_assessment.md) |
| luna allowed as CHAT caller only; agent stays gpt-5.4 (MODEL LAW) | luna fires zero tools as agent at reasoning_effort=none |
| Fresh port per run; systemd-run --collect; never inline `&` in ssh; never touch prod :8026/8000-8003 | iter80 lessons (4 failed runs to port races) |
| MDs' patches apply as-written on media/* (md5-verified 2026-09-27); config.py needs adaptation diff | seam verification above |

## BLOCKED / NEEDS INPUT
| Item | Where |
|---|---|
| Owner GO for T0 (chat brain run) — first executable task | this plan |
| Owner availability + phone/mic for T1 (the live real call) | owner schedules |
| Public mic-page URL for T1 (Caddy route + token) — pin from Oregon Caddyfile at execution | Oregon /etc/caddy or equivalent |
| Commit-split preference for T3 (recommended: C1 room-tone, C2 pacing) | owner |

## Environment & Dependencies
- OREGON: root@5.78.83.174; repo `/home/julio/projects/clean_diallux_SDR`; venv
  `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (pip: always `<venv>/bin/python -m pip`).
- Worktree `/tmp/opencode/wt-iter80` (exists, iter80 branch, clean). New worktrees `/tmp/opencode/wt-iterNN` per engine fix.
- Chat lane: harness runs from the worktree (no port needed, direct graph transport, --langfuse).
- Voice lanes: fresh free port (8030+), 127.0.0.1 bind. Evidence → `research/surgeon/iter81-fake-caller-human-parity/`.

## Architecture (one block diagram)
```
            T0 chat lane (harness.py, luna caller, no audio)      → brain trust
            T1 REAL call (owner, mic page or phone, fully traced)  → the baseline signature
            T2 fake call on same lane → diff vs T1                 → parity gap table
            T3 tighten driver (room-tone etc, iter80 linear)       → parity gates green → FREEZE
                     │ frozen instrument
                     ▼
  T4 wave1 FIX 7 STT liveness · FIX 5 backoff · FIX 8 soft filler   (engine/diallux, new branch each)
  T5 wave2 FIX 1 eager hold · FIX 4 ack filter                      (FIX 4 reuses FIX 1's primitive)
  T6 wave3 FIX 6 said-truth · FIX 3 conf band · FIX 2 reminder      (+ confidence observation rider)
```

## File Map
| File (absolute path) | What | When |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md (OREGON) | THIS file - the ladder + status; updated at every session close | living doc (SOURCE OF TRUTH on OREGON/origin-main; FINLAND gets a read-only pull for context) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/00_assessment.md (OREGON, gitignored) | T0-era wedge verdict (DONE) | exists |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/01_chat_brain_report.md | T0 deliverable | T0 |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/02_live_call_baseline.md (+ trace exports) | T1 deliverable - THE baseline | T1 |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/03_parity_diff.md | T2 deliverable (gap table becomes T3 gates) | T2 |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter81-fake-caller-human-parity/04_tighten_report.md | T3 deliverable (gates green, then FREEZE) | T3 |
| /tmp/opencode/wt-iter80/engine/scripts/llm_mic_caller.py (OREGON worktree) | T3 edits: room-tone + pacing - the ONLY driver file touched | T3 |
| /home/julio/projects/vps-inbox/voice-sdr-turn-taking-fixes.md + voice-sdr-turn-taking-research.md (FINLAND) | the 2 owner MDs - the fix ladder source. Copies on OREGON: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter80-el-flip-mic-phone-fix-src/ and /home/julio/projects/clean_diallux_SDR/tasks/surgeon/iter80-el-flip-mic-phone-fix/ | reference |
| Engine files per fix (under /home/julio/projects/clean_diallux_SDR/engine/diallux/ in each T4+ fix worktree): media/session.py, media/sentence_gate.py, media/deepgram_stt.py, diallux/config.py, graph/builder.py, media/prewarm.py | T4-T6 per MD patches; config.py needs an adaptation diff (diverged in 88381a2) | T4-T6 |

## Deploy Rules
- NEVER checkout/switch/reset/pull the Oregon prod checkout; edits only in worktrees.
- NEVER touch diallux.service / :8026 / :8000-8003. Test lanes: foreground uvicorn via boot_lane.sh, fresh port, killed at session end.
- NEVER inline `&` in ssh; use `systemd-run --unit=<name> --collect`.
- LAW 0: engine code commits on their fix branch; merges = owner say-so. Driver/harness commits on iter80 linear branch.
- **ENV LAW (owner, 2026-09-28, paid by test_iter44 false-red):** EVERY new worktree MUST copy the
  runtime env before ANY pytest/lane run: cp /tmp/opencode/wt-iter82/engine/.env NEW-WT/engine/.env
  (or point the run at the canonical env). config.py reads env_file=.env cwd-relative and the
  file is gitignored — a fresh worktree has NO env, so settings get empty keys (real Deepgram/Cal
  connects 401) and tests fail for INFRA reasons that look like code regressions. Rule: a test that
  passes on wt-iter82 and fails on a fresh worktree = env suspect FIRST, check .env exists before
  any code debugging.
- Cancel ALL test bookings after batteries (Cal.com 3801235 REAL).

## Tasks (in order — renumbered per owner; status updated at every session close)

### T0 — brain trust: chat lane with luna as caller (cheap, no audio)
Goal: prove the ENGINE's brain (states, tools, extraction, booking arc) works before spending voice-lane money.
If chat fails → engine bug hunt, NOT a voice/turn-taking problem; stop the ladder and fix that first.
Commands (typed ON FINLAND, executed ON OREGON - wrap exactly as WORKING MODE shows: ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174) - Oregon worktree cmd: `cd /tmp/opencode/wt-iter80/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python
tests/llm2llm/harness.py --transport graph --personas happy --slots mock --langfuse --caller-model gpt-5.6-luna
--agent-model gpt-5.4` (verify exact model id in worktree .env OPENAI_MODEL/LUNA pin at execution; luna = the
gpt-5.6-luna id from iter80 evidence).
Verification: happy personas complete; Intake → contact_details → ConfirmSlots → Booking reached; booking created
on mock slots → CANCEL if real slots were touched; Langfuse trace present.
Deliverable: `research/surgeon/iter81-fake-caller-human-parity/01_chat_brain_report.md` (verdict + trace ids).
Dependencies: none. Unblocks: T1.

### T1 — the baseline: LIVE real call, fully traced (owner on the phone/mic)
Goal: capture THE reference signature of a REAL human call on the current engine.
Commands: boot a fresh lane (smoke_orchestrator pattern); owner calls via the token-gated mic page (pin public
URL + token from Oregon Caddyfile/.env at execution; VOICE_TEST_TOKEN law) or the Twilio lane if owner prefers a
phone. Owner speaks naturally ~2-4 min incl. at least one barge-in and one silence pause.
Trace everything: lane log, Langfuse trace (`micbridge-<sid>`), turn reports, chunk-flow cadence
(MIC_CHUNK_INTERARRIVAL_MS), ledger import per SQL SOP.
Verification: ≥10 turns; ≥1 barge-in survived; ≥1 ≥3s pause survived; call completes an arc (info + booking attempt).
Deliverable: `research/surgeon/iter81-fake-caller-human-parity/02_live_call_baseline.md` + exported traces.
Dependencies: T0 green. Unblocks: T2.

### T2 — the measurement: fake call vs real call parity diff
Goal: quantified gap table between the frozen-instrument-candidate (current driver) and the T1 baseline.
Commands: same lane type, fake caller: `/tmp/opencode/run_driver.sh <port>` flags
`--scenario happy --persona Danny --caller-model gpt-5.4 --agent-idle-s 5.5 --max-turn-wait 60 --min-gap 2.5 --max-gap 6`;
plus `barge-in-only` and `dump-only`. Then compare vs T1 on:
(1) stream continuity — chunk interarrival/cadence (real: continuous ~50ms frames incl. silence; fake: starved gaps);
(2) turn contract — every StartOfTurn → EOT latency distribution (real: all close; fake today: wedge);
(3) turn-report shapes vs baseline; (4) round shapes vs mic-iter64-live ledger signature (already held);
(5) barge-in + pause survival.
Deliverable: `research/surgeon/iter81-fake-caller-human-parity/03_parity_diff.md` — the gap table becomes T3's
acceptance gates. Dependencies: T1. Unblocks: T3.

### T3 — tighten the fake caller to parity (driver only; commits on the LINEAR iter80 branch)
Goal: driver streams like a real mic; replies rich enough; then FREEZE.
Files: `/tmp/opencode/wt-iter80/engine/scripts/llm_mic_caller.py` ONLY.
Commit C1 — room tone (THE wedge fix; owner's proposal + pins):
- `MicDriver.__init__`: add `self._speaking = False`
- `connect()`: add `asyncio.create_task(self._room_tone())` next to `_recv_loop`
- `stream_pcm()`: `self._speaking = True` / `finally: self._speaking = False`; after the send loop, 15×20ms
  zero frames (300ms deterministic terminator)
- new method:
```python
async def _room_tone(self):
    """Continuous silence frames while not speaking — keeps BOTH the engine's
    flux VAD fed (trailing silence -> EOT commits) and the WS alive."""
    frame = zero_pcm(FRAME_SECS)
    while self.open:
        if not self._speaking:
            try: await self.ws.send(frame)
            except Exception: return
        await asyncio.sleep(FRAME_SECS)
```
Commit C2 — pacing richness: PACING_PROMPT drop the 30-char cap (keep 1-2 short sentences + 2-6s gaps);
`max_completion_tokens` 40 → 120.
Config-only: `run_driver.sh` flags per T2.
Commands: edit in wt-iter80; `<venv>/bin/python -m py_compile engine/scripts/llm_mic_caller.py`; commit messages:
`iter80 T3-c1: driver room-tone (real-mic stream contract — fixes flux starved-EOT wedge)` /
`iter80 T3-c2: driver pacing — drop 30-char cap, tokens 40->120`.
Verification (T2 gates re-run, all green): zero wedged turns (every StartOfTurn → eot adopted/turn report within
max-turn-wait); no engine silence gap >30s; barge-in-only + dump-only complete without mute; happy: Intake ≤6
turns, phone ≤2 asks, books on mock slots → CANCEL. Then declare the driver FROZEN in this file.
Dependencies: T2. Unblocks: T4. Evidence: `04_tighten_report.md`.

### T4 — wave 1 (engine fixes; NEW branch per fix, cut from merged iter80 tip)
Per-fix loop (repo-proven, adapted from fixes MD §10.2): branch `engine/iterNN-<slug>` + worktree → apply MD
patch (media/* as-written; config.py via adaptation diff) → `pytest tests/ -k <fix>` green + full suite
baseline unchanged → battery through the FROZEN fake caller + fix's own scenario → Langfuse span check →
owner ear A/B (knob on/off) → HITL stop (LAW 0) → merge → next.
| Fix | Kills | Knob (default OFF) | Passes when (§11.1) |
|---|---|---|---|
| FIX 7 STT liveness | F2 zombie mute | `STT_RX_ZOMBIE_MS=15000` | killed socket → reconnect ≤15s, call continues; 0 spurious |
| FIX 5 post-interrupt backoff | collide-re-speak | `POST_INTERRUPT_BACKOFF_MS=1000` | post-barge replies start after caller finishes, never overlap |
| FIX 8 soft filler | tool-wait dead air | `SOFT_FILLER_MS=3000` | one filler ~3s into wait, once per turn, then the real answer |
Rider (any time in T4, read-only): FIX 3 confidence observation — does flux send confidence? (answers MD §4.4 deferral).
Dependencies: T3 frozen. Unblocks: T5.

### T5 — wave 2 (the architectural core)
| Fix | Kills | Knob | Passes when |
|---|---|---|---|
| FIX 1 eager hold | F5 + talk-over F1 | `EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true` | 0 mid-speech collisions; TTFT p50 regression ≤600ms; resumed_count unchanged |
| FIX 4 ack filter + false-interrupt resume | F4 silent "yeah" | `BARGE_ACK_FILTER=true` (+`BARGE_FALSE_INTERRUPT_TIMEOUT_MS=2000`) | "yeah" mid-question → agent resumes sentence (≤500ms dip), no new turn |
NOTE: FIX 4 reuses FIX 1's hold/release/discard primitive — FIX 1 ships first (MD §10.1). DELETES per MD PORT 1
(`_grace_then_cancel` family) only after FIX 1's battery passes.
Dependencies: T4. Unblocks: T6.

### T6 — wave 3 (cleanup + the ladder)
| Fix | Kills | Knob | Passes when |
|---|---|---|---|
| FIX 6 said-truth commit | F3 stacked recounts | `HISTORY_SAID_TRUTH_ONLY=true` | recount battery clean; THEN the deferred dedupe-family deletion battery |
| FIX 3 confidence band | fragment re-asks | `STT_CONFIDENCE_FLOOR=0.2` + `STT_CONFIDENCE_REASK_CEIL=0.4` (gated on the T4 rider observation) | fragments → canned "you cut out" line, never a model re-ask |
| FIX 2 reminder ladder | F1 re-ask loop | `PAUSE_LADDER_MODE=reminder` | silent caller: nudge ~10s/~20s, close ~30s; normal calls: zero audible difference |
Dependencies: T5. Completes the ladder.

### Session-close invariant (the "T x done → move to T y" rule)
Every session working this plan ends by: (1) archiving evidence to the research folder, (2) updating the STATUS
block + the task statuses above, (3) appending ONE row to the Session Log at the bottom of this file, (4) stating
in chat the current task and the next one. A fresh session starts by reading the STATUS block, then the current
task's section, then Compaction Context — this ONE file carries all past decisions, verdicts, and pointers.

## Validation Plan (end-to-end)
1. T0 chat green (brain works) → 2. T1 baseline captured → 3. T2 parity gaps quantified → 4. T3 parity gates
green + driver frozen → 5. each fix in T4-T6 lands with its §11.1 signal + owner ear A/B → 6. final full battery
(happy3 + barge + dump through the frozen caller) + owner live-call ear test vs T1 baseline.

## Abort flags (fixes MD §10.3 — roll back to knob-off, investigate before re-testing)
- Any battery call that fails to BOOK where happy3 passed on main.
- resumed_count climbing without caller speech (FIX 1 leaking audio early).
- Agent audio overlapping caller speech in ear test (FIX 5 not stamping).
- Nudges firing during tool waits (FIX 2 armed before FIX 8 — wrong order).
- Latency regression: tts_first_byte p90 growing > ~1.2s over pre-fix eager p90.

## Adapt-to-diffs (MD was written against 0ce798f; pinned 2026-09-27)
| What the MD says | What we actually do |
|---|---|
| §10.2 deploy to :8024 lane + journalctl | fresh-port foreground uvicorn lanes (boot_lane.sh), systemd-run --collect |
| branch names `engine/iter74-*`...`engine/iter81-*` | placeholders — real iterNN assigned at branch cut (numbers already consumed through 81) |
| test files `test_iter74_eager_hold.py` etc. | renumber to the real iteration at cut time |
| config.py knob registry §1 pasted as-is | config.py diverged (EL knobs from 88381a2) — adaptation diff, same knobs |
| media/* patches | apply as-written (md5-verified identical) |

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Merging iter80 (now carrying driver + room-tone after T3) | owner say-so (LAW 0); T3 green makes it merge-ready |
| Dedupe-family deletion | only after FIX 6 battery (MD PORT 6 law) |
| Voice provider decision (EL vs Cartesia prod) | separate owner call |
| Async RAG retrieval | own design round after the ladder |
| Semantic turn-detection models / waitFunction / TTS-side filtering | deliberately NOT ported (MD §11.2 — nobody re-litigates) |


## Session Log (the "report" — append ONE row per session, newest at TOP; this is what keeps small sessions moving)
| Date | Task touched | Outcome | Evidence | Next |
|---|---|---|---|---|
| 2026-09-28 | FIX 7 BATTERY (Scenarios A+B + owner T4 latency add) PASS: A age-gate refusal (env deviation CALL_PREWARM boot variant, code untouched) + B silent-zombie watchdog 15.8s/single span/zero false fires + B1 hard-kill proved pre-existing instant reconnect; zero latency cost, no bookings, lanes 8039-8042 torn down; ledger fix7-* runs @ fa62162; T4 verdict: ~300ms eager overlap UNBANKED -> FIX 1 eager hold = latency lever (owner leaning pull-forward) | 01_fix7_battery.md + traces 1acda411a0ff / 2f625c70052a / 2577b7dff5cc | owner ear A/B FIX 7 (HITL) + fix order call (FIX 5 vs FIX 1) |
| 2026-09-28 | T2/T3 SESSION (owner: cut attempted-test churn, continue plan): T1 baseline audited (full 4-SOP, t0-chat-iter81 145 rows persisted); fake-caller 7 runs on wt-iter80/82 lanes — room-tone PROVEN (continuous stream, 0 wedges, barge-ins ok), caller brain fixed twice (conversation_pairs order mangling; JSON blob -> chat-harness plain-text format), facts land (15/wk, $450) but booking gate NOT reached (turn cap cut arcs; scripted desync); scripted phased mode committed for transport tests; caller default gpt-4o-mini; ENGINE iter82 pause-ladder (FIX 2, owner 15s single-nudge: PAUSE_REASK_MS=15000, PAUSE_LADDER_MAX=1) built on branch engine/iter82-pause-nudge @ f0fde1b (config knobs default OFF + media/session.py ladder + say.exact + 4 wiring points) 5/5 unit tests green; suite debt surfaced: 9 stale pre-existing reds (4 tts FIXED provider-agnostic, 4 delivery + 1 iter44 remain); lanes/logs evidence in research/surgeon/iter81-fake-caller-human-parity/ | 02/03 files + t4_fake_v8.json + traces 4b9958/082e52/1277c2 | T4 wave 1 (FIX 7/5/8) — owner GO per fix |
| 2026-09-28 | T1 EXECUTED: live human call via browser mic (owner Mac SSH local-forward localhost:8030, no Caddy, no double-hop after owner overrule); full arc incl REAL booking soWHP6TM57C37s6MNAPb6Q (today 4:30pm) CANCELLED 200; 51 llm rounds, 37 tts bytes, pauses survived; flags: rag degraded=true + 0 chunks most rounds (likely the "horrible" verdict), 16 contact_details rounds, no barge-in events logged | 02_live_call_baseline.md + 02_live_call_events.txt (mic_events.py) + trace 1666e287ae4d | T2 — fake-vs-real parity diff |
| 2026-09-28 | T0 RERUN (owner GO): real slots --slots live, Danny/Marcus/Mike — 3/3 PASS booked on REAL Cal.com (turns 18/20/22); caller temp 0.3 owner pin applied (gpt-5 callers: API rejects any temperature≠1, knob omitted — 3 crash runs cost /bin/bash bookings); ALL 3 test bookings CANCELLED (uids above in report; CF 1010 workaround = UA header); 3x end_call on Mike closing turn noted non-blocking; commits 15bf1f4 + 2a36c94 pushed | 01_chat_brain_report.md (rerun section) | T1 — live real call baseline (owner availability + mic-page URL/token) |
| 2026-09-28 | T0 EXECUTED (owner GO received in-session): chat brain lane, luna caller, graph transport, mock slots — 5/5 PASS (Maria16/Danny24/Susan25/Marcus25/Mike23 turns, all booked + end_call, full arc incl. leak calc); Langfuse traces verified (5 ids in report); 2 crash runs fixed by harness CallerLLM param-compat patch (gpt-5 callers: max_completion_tokens, no temperature) COMMITTED iter80 linear 15bf1f4 pushed; 01_chat_brain_report.md written; T1 owner-scheduling prompt sent; NOTHING to cancel (mock slots) | 01_chat_brain_report.md + traces llm2llm-graph-book* | T1 — live real call baseline (owner availability + mic-page URL/token) |
| 2026-09-27 | Plan build (supersedes plans/plan_v5_iter81_fake_caller_human_parity.md, deleted) + wedge assessment (old T0) | Verdict pinned: driver starves flux STT between bursts, turn never finalizes, 65s mute; room-tone fix adopted w/ 4 integration pins; MD seam md5-verified (media/* byte-identical, config.py diverged); master ladder T0-T6 written; plans COMMITTED to origin/main 0ca44ce (master + iter80 backlog, superseded plan removed); BRANCH LAW pinned option 2 (stack from ef627ba, no merge until production grade). 2026-09-28 WORKING-MODE patch: two-box law + absolute paths pinned into this file plans COMMITTED to origin/main 6e6e19f; two-box WORKING MODE + who-am-I bootstrap pinned; plan mirrored to Finland (fetch) | research/surgeon/iter81-fake-caller-human-parity/00_assessment.md + this file | Owner GO -> run T0 chat brain (harness.py, luna caller, mock slots) |
