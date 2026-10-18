# plan_v5_iter90_boris_ab_hold_verdict — analyze the Boris knob-250 A/B against knob-0, settle the deterministic-hold design debate (owner claims the await-before-eager-EOT is already solved and the 250 knob is stale — agent claims the knob's one-ahead fire law is the irreplaceable half), verify Deepgram param nativeness, then close iter90 (memos + ledger imports + PT rows) and prep the iter91 skeleton. DOCS-ONLY + read-only analysis. NO code branches cut in this plan.

## Meta
- Date: 2026-10-03
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland/MainVps. ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Scope: read-only forensics + docs commits to LOCAL main (per LAW 0 docs rule). NO code edits, NO config edits, NO service touches.
- Status: EXECUTED 2026-10-03 — T1-T5 DONE. Memos on OREGON research/surgeon/iter89-prompt-enhancements/: 92_boris_ab_hold_verdict.md (T1 tables + T2 verdict), 93_deepgram_param_nativeness.md (T3), 90_rag_zero_main_verdict.md (T4). Ledger runs iter90-mic-b0 + iter90-mic-b250 imported & verified (18/15 rounds, 13/15 rag). PT-75..77 carried + PT-79/80/81 on main (d9616c6); ENV-SWITCHES §3c native-DG + flag-5 closed (79f8669); iter91 skeleton committed (d9616c6). Knob verdict = OWNER decides (92 §2). Compaction corrections: B0 t3 rag DID fire; B0 rag = 13 spans + pin; B250 = 12 reported turns (t4 barge-cancelled); B250 await = 17 already_done + 1 timeout.

## Compaction Context (carried verbatim from the 2026-10-02/03 iter90 session)

**What this session produced:**

1. **Persona/call evidence (LLM mic caller, branch `wt-iter89` @ `30405ad`):**
   - **B0 run (knob=0):** 2026-10-02 12:28-12:32, GK Boris, happy scenario, real `/mic/ws` path, engine booted at `/tmp/opencode/wt-iter89/engine` on port 8030 (temp test lane, started by agent with owner GO). sid `c5aed8b0d1e4`; Langfuse trace `micbridge-c5aed8b0d1e4-27844db0` (trace id `eef77fed30a360e83cf36581c5681f07`). 12 caller turns / 15 agent turns, `stop_reason=turn_cap_goodbye`, elapsed 227.5s. RAG: 11 spans + rag:pin (landscaping pin hit 3 chunks/3.2ms; Intake retrievals carried caller pain text = iter89 G1 fix LIVE). e2e per turn: 1029/953/1768/1011/1580/3016/977/4519/2703/3640/2473/1072 (p50 1580, p90 3016). Stall column (stt_eot_to_llm − Σround ttft): 31/57/**600**/68/106/197/74/**1141**/674/500/344/163. Turn 8 = 3 rounds (Disc 663 + Disc re-round 1676 CACHE DROP 3712→2688 + Closer 723) + Closer warm landed LATE (`warm done key=Closer ms=1167` mid-turn). Turn 3 = 600ms stall with NO rag fire — open mystery.
   - **B250 run (knob=250, WARM_AWAIT_DEST_MS=250 written by owner order):** 2026-10-03 06:02, identical lane/persona. sid `c866214c53fc`, engine log `/tmp/opencode/voice_server_8030b.log`. 13 turns, turn reports e2e: 1045/2257/1650/1482/1779/1588/**4652**(3 rounds Intake→Discovery)/1272/1325/**3254**(2 rounds Discovery×2)/1294/1602. Stall: 179/346/409/466/477/511/1204/310/291/1248/402/576. await_warm 18 lines, 17 with `waited_ms=0`.
   - ⚠️ **OVERWRITE WARNING:** both runs used `--out /tmp/opencode/iter90_mic_gk_boris.json` (launcher `/tmp/opencode/iter90_run_mic.sh` hardcodes it) → the file NOW = B250 evidence (13,805 B, Oct 3 06:02). B0 raw json is GONE; B0 survives only in `/tmp/opencode/voice_server_8030.log` (Oct 2 12:36) + the B0 Langfuse trace + the numbers recorded in this Compaction Context. Also the launcher's `--journal-log` still points at `/tmp/opencode/voice_server_8030.log` while the B250 server wrote to `voice_server_8030b.log` — B250's json `journal_lines` field is STALE (reads the old log tail). T1 must use `/tmp/opencode/voice_server_8030b.log` + Langfuse for B250, never the json's journal field.

2. **The design-balance question (T2's verdict to settle):**
   - Owner position (2026-10-03): "the await design is not the best path — we have something better: we await for the pre-warm to LAND before turning first eager EOT; that has been solved; the 250ms await is stale, but feel free to prove me wrong."
   - Agent's counter-analysis (read from `/tmp/opencode/wt-iter89/engine/diallux/graph/builder.py`): the EOT-class bounded await (task-await, `cap_ms=500` from `prewarm_entry_wait_knot_eot_ms`/`prewarm_entry_wait_eot_ms`) IS deployed and ran 12/12 `already_done waited_ms=0` on B0 — owner's "solved" claim is TRUE for the await plane. BUT `warm_await_dest_ms>0` also gates: (a) the **one-ahead fire law** (builder.py ~2575: entering X warms X's FSM successors — fires during the caller's think time; this is what would have made turn 8's late Closer warm already-done) and (b) the entry_lite hold (builder.py ~1864: ack's payload never speaks before destination warm lands, +10ms settle). So knob=0 = no one-ahead warms anywhere; fire-at-detection (iter46 T4a, fires when `transition_to_X` tool NAME completes mid-stream) remains the only pre-warm signal, which fired LATE on turn 8/9.
   - B250 vs B0 first read: the multi-round turns remain the dominant disease in BOTH runs (B0: t8 4519/t9 2703; B250: t8 4652/t11 3254) — the knob did NOT eliminate the transition-chain tax; whether the warm tail was absorbed (stall composition) is exactly what T2 must prove.

3. **Deepgram param verdict (T3 — DELIVERED 2026-10-03, cite in the register):**
   `eot_threshold` (0.5–1.0, default 0.7), `eager_eot_threshold` (0.3–0.9, default None = eager mode OFF), `eot_timeout_ms` (500–60000, default 5000) are **NATIVE Deepgram flux `/v2/listen` query params** (developers.deepgram.com/docs/flux/configuration + reference/speech-to-text/listen-flux). Our `diallux/media/deepgram_stt.py:77-90` only urlencodes them; the eager flag must be ≤ eot_threshold (API-rejected otherwise). The ONLY thing that is ours = the settings field `deepgram_eager_eot` (code default False — gates whether we append the native param). ENV-SWITCHES.md §3c row wording must be corrected next session to state "native param, pass-through".

4. **env/doc state (owner-ordered, executed 2026-10-02):**
   - `WARM_AWAIT_DEST_MS=250` written into all three env sources: `/tmp/opencode/wt-iter89/engine/.env`, `/home/julio/projects/clean_diallux_SDR/engine/.env` (Oregon), `/opt/diallux-production/.env`. Verified resolved in Settings warm_await_dest_ms=250.
   - `/opt/diallux-production/.env` voice corrected to **Hannah** `ZSNL4hPqCnqoMPaI4jGX` speed 1.0/stability 0.6 (was Sarah 1.06/0.5); `TTS_GATE_FAST_FIRST_FLUSH=false` + `TTS_DEDUPE_SEMANTIC=false` made explicit there; `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` added there. Services (8090/8026) pick up on next restart — NOT restarted.
   - wt-iter89 worktree .env keeps Sarah 1.06/0.5 (VOICE LAW test voice — correct).
   - Docs commits on main (pushed, verified via ls-remote): `b2c9bfd` (ENV-SWITCHES.md register + AGENTS.md SWITCH LAW + full_call_analysys.md Step 0a) and `2f3e380` (§4 flags 1-4 RESOLVED, FLAG 6 open: 4 wrongful code defaults — warm_await_dest_ms 0, tts_gate_fast_first_flush True, tts_dedupe_semantic True, deepgram_eager_eot False — one next-engine-iter commit flips them).

5. **Other session artifacts:**
   - Public repo created: https://github.com/Cesars-dev/diallux-sdr-iter89 (snapshot `29c41e2` of 30405ad; prompts byte-identical to branch; 11 KBs included; live raw keys scrubbed — 7 legacy `sk-proj-` in retell/heating-uk tests, ~50 Retell `key_` in docs, 1 ElevenLabs `sk_` → replaced `REDACTED-public-export-see-env`; final raw scan 0; keyhound report at `/tmp/opencode/keyhound_iter89_report.txt`).
   - T1 (ZERO-RAG-on-main verdict) is EVIDENCE-COMPLETE but the memo `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/90_rag_zero_main_verdict.md` was NEVER WRITTEN — still owed.
   - Ledger (research/surgeon/iter48-rag-truth/ledger.db): `iter90-mic-gkboris` import NOT DONE (neither B0 nor B250). Merged-era baseline in ledger: `iter87-hold-battery` @ 02eb2ac (96 rounds LIVE mic, TTFT p50 853/p90 1572/max 2639, cache-0=1, e2e p50 1321-1385/p90 3707-4193 from its own turn reports). `gk-iter89` @ f7a37c3 = text lane baseline (TTFT p50 710/p90 871).
   - LaneA status: wired (deepgram_stt.py:219 Update→on_update; session.py:192/774) but ZERO `rag` obs from laneA across ALL mic traces; per-turn fires appear only at EagerEOT moment (laneB) + consumer fallback refires mid-turn. Instrumentation probe owed.
   - Temp test lane: engine still running on OREGON port 8030 (uvicorn PID 1240546, boot b, log /tmp/opencode/voice_server_8030b.log) — temporary infra started with owner GO; kill when done (`kill 1240546` via ssh) or restart fresh: `cd /tmp/opencode/wt-iter89/engine && nohup setsid bash -c 'set -a; . ./.env; set +a; exec /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8030' > /tmp/opencode/voice_server_8030c.log 2>&1 &` (env file now carries WARM_AWAIT_DEST_MS=250 automatically).
   - Original iter90 plan: /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter90_assess_rag_zero_and_first_name.md (T1/T2/T3/T4 from it: deliverables still owed; its Sam-autopsy/SOP-rows tasks superseded by this plan's scope).

**Two-box state:** Finland main checkout /home/julio/projects/clean_diallux_SDR has 3 pre-existing modified files (AGENTS.md, plans/NEXT_STEPS.md, plans/PENDING_TASKS.md — dirty BEFORE this session, untouched). Docs worktree on Finland: /tmp/opencode/wt-main-docs (branch main, tip = the b2c9bfd+2f3e380 line). Oregon wt-iter89 @ 30405ad (branch engine/iter89-prompt-enhancements, pushed to GitHub). Oregon main checkout @ df23d37 — NEVER touch its git state (PROD). GitHub PAT: credential store at /home/julio/projects/clean_diallux_SDR/.git/gh-creds (relative-path helper breaks in worktrees — always `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'`; the stale repo-level relative helper prints harmless "unable to open .git/gh-creds" fatals that can be ignored).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Owner's 5 flag resolutions (2026-10-02) = the standard | hold ON (knob 250 — value owner-ordered in-chat "turn it on", 250 set by agent as the design-consistent cap; owner may re-pick); prod voice = Hannah 1.0/0.6; PT-71 pair OFF documented as reversed iter68 measures; Cartesia dated pin everywhere; eager = engine-adapted default TRUE |
| Switch audit is mandatory on every run | ENV-SWITCHES.md + AGENTS.md SWITCH LAW + full_call_analysys.md Step 0a (docs law, committed b2c9bfd/2f3e380) |
| Public repo diallux-sdr-iter89 = evidence export, snapshot-only (no history) | keyhound discipline + contaminated legacy trees |
| Code-default flips (FLAG 6) = NEXT engine branch (iter91), NOT env | SWITCH LAW rule 4; owner wants the defaults right so bare worktrees behave |
| The knob debate gets SETTLED BY DATA (T1/T2), not opinion | owner explicitly invited proof ("feel free to prove me wrong") both directions |
| Do NOT restart 8090/8026 services in this plan | env picked up at their next owned restart; services laws |
| Mic caller scripts reuse = driver artifacts possible ("Customer: " TTS prefix leak documented iter80-82) | input-quality caveats go into the verdict, not ignored |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO on this plan | owner's word in-chat |
| Final knob verdict requires T1/T2 data → owner picks: keep 250, re-pick, or order the iter91 decouple (one-ahead fire unconditional + hold deleted) | after T2 |
| iter89 merge decision (4/5 booked GK battery; Sam first_name gate bug still open) | owner at close-out |
| iter91 branch GO (FLAG 6 defaults + optional decouple + laneA probe) | owner after T5 skeleton |
| PT-74/Sam first_name attendee-fallback archaeology (original plan T2) | separate session — NOT this plan's scope |

## Environment & Dependencies
- All repo ops: OREGON ssh wrapper (Meta). Finland wt-main-docs for docs commits: /tmp/opencode/wt-main-docs (branch main).
- venv: /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python (copy-mirror venv — always `-m pip`, never bin/pip). No sqlite3 CLI: use `.venv/bin/python -c "import sqlite3…"`.
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db (runs/calls/rounds/rag/findings/sops/sessions).
- SDKs: /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py (import/gates/sops), /home/julio/projects/clean_diallux_SDR/scripts/latency_pull.py (percentiles), register /home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md (§2 snapshot command).
- Evidence files (LIVE CALL PATHS for analysis):
  - B0: /tmp/opencode/voice_server_8030.log (turn reports + await_warm + warm-done lines, Oct 2) · Langfuse trace `micbridge-c5aed8b0d1e4-27844db0` (id eef77fed30a360e83cf36581c5681f07) · B0 per-turn numbers also in this plan's Compaction Context (json lost to overwrite).
  - B250: /tmp/opencode/voice_server_8030b.log (Oct 3) · driver json /tmp/opencode/iter90_mic_gk_boris.json (overwritten = B250; its journal_lines field is STALE — do not cite) · Langfuse trace `micbridge-c866214c53fc` (obtain full trace id via `/api/public/traces?sessionId=micbridge-c866214c53fc-…` — sessionId=micbridge-c866214c53fc).
  - Launcher: /tmp/opencode/iter90_run_mic.sh (sources wt-iter89 engine/.env; runs /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python /tmp/opencode/wt-iter89/engine/scripts/llm_mic_caller.py --ws-url "ws://127.0.0.1:8030/mic/ws?k=$VOICE_TEST_TOKEN" --scenario happy --persona Boris --agent-idle-s 4).
  - Merged-era baseline: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-prewarm-hold/{01_battery_verdict.md,02_latency_report.md,sdk_happy_a4de3446.txt} + ledger run `iter87-hold-battery`.
- Langfuse access: engine .env LANGFUSE_* at /tmp/opencode/wt-iter89/engine/.env (host http://46.62.233.228:3001).
- Branch registry: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db (branches/commits — for citation of run commits).

## Architecture (one block diagram)
```
[caller brain gpt-4o-mini → Cartesia TTS] → mic/ws (:8030 token-gated)
   → SttFlux (EagerEOT 0.7) → eager speculative turn → EOT adopt
   → [laneA rag @ first Update · laneB rag @ EOT] → state_node consume (bounded await)
   → warm planes: fire-at-detection (tool name in stream) · post-execute force ·
     one-ahead successors (gated by warm_await_dest_ms>0 = B250 only) · precall lite
   → TTS gate → audio out → turn report (e2e/stall/rounds) → json + Langfuse
```

## File Map (this plan's writes)
| File (absolute path) | What | New/Edit |
|---|---|---|
| /tmp/opencode/wt-main-docs/plans/plan_v5_iter90_boris_ab_hold_verdict.md | this plan | NEW (docs→main) |
| /tmp/opencode/wt-main-docs/research/surgeon/iter89-prompt-enhancements/90_rag_zero_main_verdict.md is GITIGNORED — write instead at OREGON working path below | see T4 | |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/90_rag_zero_main_verdict.md | original plan T1 memo (evidence lives here regardless of git) | NEW (OREGON, untracked research/) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/92_boris_ab_hold_verdict.md | T1/T2 deliverable | NEW (OREGON, untracked research/) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/93_deepgram_param_nativeness.md | T3 deliverable (one page, native-param verdict + register correction note) | NEW (OREGON, untracked research/) |
| /tmp/opencode/wt-main-docs/docs/Testing_guidelines/ENV-SWITCHES.md | §3c deepgram row wording fix (native params) + §4 add knob-verdict note | EDIT (docs→main) |
| /home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md — via wt-main-docs棱 path below | PT-79 (laneA probe) + PT-80 (FLAG 6 defaults) + PT-81 (same-state re-round warm) rows | EDIT (docs→main) |
| /tmp/opencode/wt-main-docs/plans/PENDING_TASKS.md | same rows on the main-line copy | EDIT (docs→main) |

## Deploy Rules
- NO code branches, NO config edits, NO service touches. The ONE allowed env-neutral action: kill/restart the TEMP 8030 test lane (agent-started infra), required only if a re-run is owner-ordered.
- Docs commits only (this plan, PT rows, ENV-SWITCHES edits) on the LOCAL main line (/tmp/opencode/wt-main-docs on Finland; push). Memos land on OREGON research/ as untracked evidence per gitignore law — never committed into git.
- NEVER touch prod checkout git state (df23d37) — read-only.
- After any evidence work: ledger imports (T4) via live_sql.py are WRITE-side (allowed, it is the ledger's design) — session rows tagged with branch engine/iter89-prompt-enhancements + commit 30405ad for both runs.

## Tasks (in order)

### T1 — Boris A/B table (B0 knob-0 vs B250 knob-250), read-only
Goal: one per-turn table (turn · e2e · stall · rounds · state chain · rag-fire moments) for BOTH runs, plus cache_read per round from the B250 Langfuse trace (B0 cache numbers already in Compaction Context).
Commands:
- Rebuild B0 tables exactly as done (numbers in Compaction Context §1 act as ground truth; re-derive only to verify):
  `ssh … "python3 <<'EOF' … parse /tmp/opencode/voice_server_8030.log turn reports + round usage (regex as in session) EOF"`
- Parse B250: `ssh … "python3 … /tmp/opencode/voice_server_8030b.log"` (same regex; turn reports 13, round usage lines, warm done/await_warm lines).
- Langfuse B250 cache/rag rows: `cd /tmp/opencode/wt-iter89/engine && set -a && . ./.env && set +a && .venv/bin/python` pulling `/api/public/observations?traceId=<B250 id>` (find id via `sessionId=micbridge-c866214c53fc`), filter names rag/llm:*/await_warm/tts_first_byte.
Deliverable: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/92_boris_ab_hold_verdict.md` — tables + delta column + cross-run snapshots (B0 = knob0 pre-env-edit; B250 = knob250) per Step 0a.
Verification: every number traceable to a file line or Langfuse obs id; no averages-only claims (owner's rule: turns that matter, per-turn).

### T2 — The hold-design verdict (owner claim vs evidence)
Goal: answer, per TURN CLASS: (a) did knob=250 (one-ahead warms ON) change where warms landed (B250 should show `warm done key=<successor>` BEFORE the destination's EOT, vs B0's late mid-turn `warm done key=Closer ms=1167`)? (b) did the turn-8/11-class multi-round tax change? (c) is the 250 await actually paid (task-await already_done stall≤cap) or dormant? Verdict options written explicitly: (1) owner right overall → iter91 removes knob, keeps EOT await + adds unconditional one-ahead; (2) agent right partially → knob stays as the one-ahead switch with hold as harmless no-op; (3) neither → new mechanism (e.g. deterministic warm at SOT).
Commands: T1 outputs + grep the per-run warm-done sequence:
- `ssh … "grep -nE 'warm done|await_warm|eager turn started|eot adopted' /tmp/opencode/voice_server_8030.log | head -60"`
- `ssh … "grep -nE 'warm done|await_warm|eager turn started|eot adopted' /tmp/opencode/voice_server_8030b.log | head -60"`
Deliverable: §2 of 92_boris_ab_hold_verdict.md — verdict + recommendation for iter91 scope; OWNER decides, not the agent.
Verification: verdict cites per-turn evidence (timestamps) from both logs; explicitly names which mechanism produced each stall.

### T3 — Deepgram param nativeness → register wording fix
Goal: end flag-5 confusion permanently.
Facts (verified 2026-10-03, cite in memo 93): `eot_threshold`, `eager_eot_threshold`, `eot_timeout_ms`, `keyterms`, `numerals` are NATIVE flux `/v2/listen` query params (developers.deepgram.com/docs/flux/configuration); our deepgram_stt.py:77-90 is a urlencoded pass-through; eager threshold must be ≤ eot_threshold (server-rejects otherwise); the only invented part is our settings field `deepgram_eager_eot` (gates append) — its code default False vs owner standard True is FLAG 6 material, not flag 5.
Commands: write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/93_deepgram_param_nativeness.md` (one page: param table w/ ranges+defaults from Deepgram docs, our pass-through code ref, the field-only flag note); edit ENV-SWITCHES.md §3c rows to mark params `native-DG` and move the flag discussion to FLAG 6 note.
Verification: register §3c no longer implies we invented the behavior.

### T4 — Close-out iter90: original-plan memo + ledger imports + PT rows
Goal: make everything queryable and documented.
Commands:
- Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/90_rag_zero_main_verdict.md` (the ORIGINAL plan T1 memo, owed): main-line zero-RAG = harness artifact (iter76 firesim auto-enable never merged to main); main harness ALSO lacks the gpt-5.4 caller fix (max_tokens 400) and main Boris run no-booked (10 turns, tools=[]); branch mic proof shows live RAG (11 spans + pin).
- Ledger imports (from OREGON main checkout engine dir):
  `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py --db ../research/surgeon/iter48-rag-truth/ledger.db import --window "12:24-12:36" --run iter90-mic-b0 --commit 30405ad --branch engine/iter89-prompt-enhancements` (B0 = Oct 2 12:24-12:36 window)
  repeat with `--window "05:57-06:05" --run iter90-mic-b250` (Oct 3 05:57-06:05 UTC).
- Verify: `.venv/bin/python /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py --db ../research/surgeon/iter48-rag-truth/ledger.db runs | tail -4` + `latency_pull.py --run iter90-mic-b0 --run iter90-mic-b250 --run iter87-hold-battery`.
- PT rows via wt-main-docs PENDING_TASKS.md: PT-79 laneA silence probe (mic lane flux Update events never fired laneA in any trace), PT-80 FLAG 6 code-default flips (4 fields, one commit), PT-81 same-state post-execute re-round warm (turn 8/11 class). Keep PT-78 (Sam-gate) from the original plan UNTOUCHED (open).
Verification: ledger SELECT counts; PT rows present; both memos exist with file-line citations.

### T5 — iter91 skeleton (PLAN DRAFT ONLY — new plan file, no branch cut)
Goal: prepare the next engine iteration so the owner only says GO.
Content: single variable = FLAG 6 defaults flip (warm_await_dest_ms default→owner-verified value or 0-with-one-ahead-decoupled per T2 verdict; tts_gate_fast_first_flush→False; tts_dedupe_semantic→False; deepgram_eager_eot→True) + (conditioned on T2 verdict) the one-ahead fire law made unconditional + laneA/fire-sim debug field on the turn report (closes the turn-3-600ms mystery) + same-state re-round warm (PT-81). Draft at /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter91_defaults_and_warm_decouple.md via THIS plan's docs commit (PLAN ONLY status inside).
Deliverable: the skeleton committed to main.
Verification: file exists on main; contents = T1/T2-conditioned; no code touched.

## Validation Plan (end-to-end)
T1 tables → T2 verdict (owner) → T3 register fix → T4 ledger SELECT + PT rows → T5 skeleton on main → (future session, owner GO) iter91 branch per LAW 0.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Sam first_name gate archaeology (original plan T2) | separate session; PT-78 open |
| iter89 merge + tag + git-tree.sh + REAL KB re-ingest | owner say-so, unchanged |
| Priya pricing-leak patch | rides iter91 engine branch or prompt follow-up, owner picks |
| Mic battery 5-persona rerun post-fix | after iter91 |
| /opt prod voice 0.7→0.6 stability remnant in main-checkout .env | cosmetic, owner's env |
