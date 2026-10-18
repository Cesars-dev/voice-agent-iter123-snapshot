# plan_v5_iter94_95_validation_close — live validation + merge ceremony + close-out (continuation of plan_v5_iter94)

## Meta
- Date: 2026-10-06 (continuation plan written same day, new session per owner order)
- Project root (OREGON source of truth): `/home/julio/projects/clean_diallux_SDR`
- Session box: Finland (julio @ 46.62.233.228). ALL repo git ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=15 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'`
- Numbering: continues the iter94/iter95 chain (parent plan:
  `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter94_ladder_silence_savage_warm.md`).
  This plan itself mints NO new iter (no engine code changes are planned here beyond
  what is already committed).
- Status: **PLAN ONLY — awaits owner GO. No validation run, no merges, no commits until owner GO.**

## Compaction Context

### What is DONE (committed, verified, UNMERGED)
1. **iter94 — the silence-stretch ladder guard** ("I am sorry, are you still there?" every-8s
   nag): branch `engine/iter94-ladder-stretch`, tip `3ac544a`, worktree `/tmp/opencode/wt-94`.
   The fix: 3-line guard in `_ladder_arm` (`/tmp/opencode/wt-94/engine/diallux/media/session.py`
   at main-tip line 372): `if self._ladder_task is not None: return` (+comments) — an agent
   turn must NOT restart a running ladder; only caller speech (disarm :559/:695) resets it.
   Pins: `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter94_ladder_loop.py`
   (5 pins, virtual clock: patch asyncio.sleep + time.perf_counter; SPEC values 8000/1/45000).
   Suite: **495 passed / 3 skipped / 0 failed** (main-tip baseline measured 490/3/0).
   Stash proof: 3 fix-pins fail pre-fix, 2 spec pins pass both ways.
2. **iter95 — savage piece 1, warm cancel-not-wait** (the 1.2-2.4s dead-air lost races):
   branch `engine/iter95-savage-warm-abort`, tip `63e013c`, worktree `/tmp/opencode/wt-95`.
   The fix: `_await_warm` in
   `/tmp/opencode/wt-95/engine/diallux/graph/builder.py` (:648-690) — a warm still
   streaming at the bound is CANCELLED (outcome `aborted`; prefill cache survives
   server-side per savage Proof 1); new Settings field `prewarm_abort_cap_ms: int = 400`
   in `/tmp/opencode/wt-95/engine/diallux/config.py` (:220) — **CEILING semantics**:
   effective bound = `min(context wait_ms, cap)` when cap>0 (mid-turn 100 stays 100; EOT
   500 and dest 2500 clamp to 400); **cap=0 = legacy iter46 wait-shield** (timeout keeps
   the warm, outcome `timeout`); entry flag 0 still short-circuits everything.
   Pins: `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter95_warm_abort.py`
   (6 pins incl. no-garbage invariant + code-default pin). Suite: **496/3/0**.
   Stash proof: 4 fix-pins fail pre-fix. Audit parser
   `/tmp/opencode/wt-95/scripts/savage_latency/warm_race_audit.py` reads the new
   `aborted` outcome (verified with a synthetic log probe).
3. **Test-merge lane** (owner opted in): worktree `/tmp/opencode/wt-9494`, branch
   `test/iter93-94-95` @ `9eb341c` = main tip `06bdd97` + iter93 (`e57d2b2`,
   `engine/iter93-held-adopt-race`) + iter94 + iter95 merged TEST-ONLY (3 merge commits,
   zero conflicts). Its 23 pin tests (93+94+95 files) pass. **Main untouched. Not for merge.**

### The validation state (T4 of the parent plan)
- Lane server UP on OREGON: `127.0.0.1:8049`, pid 1582724, log
  `/tmp/opencode/lane-8049.log`, booted from `/tmp/opencode/wt-9494/engine` with
  `.env` sourced + `DEEPGRAM_RAW_DUMP=true` (diagnostic, boot-command env only —
  no `.env` edited). Env md5 a40d01b17fc7b1ebb942ef1a111417f6 (= canonical).
- **Self-test call PASSED end-to-end** (2026-10-06 07:46): synthetic caller clip
  (`/tmp/opencode/selftest_mic.py` — EL test voice Sarah, 3.9s, fed into the same
  `/mic/ws` the browser uses) → Deepgram StartOfTurn/Updates/EagerEndOfTurn/EndOfTurn
  all in the log → Linda replied (3 audio frames + `turn-1-done` mark).
- **Mic mystery SOLVED:** the owner's browser fed Deepgram ~37s of SILENCE in the
  07:35 call — client-side capture issue (Mac input device/permission), NOT code.
  The owner was given 3 checks (macOS Sound input meter, Chrome site mic permission,
  competing apps). His mic may still be broken; the validation does NOT need it.
- **What was being run when the owner stopped the session:** the iter80 LLM caller
  driving the live validation call (see T1 below) — aborted mid-run, no journal written.

### Owner decisions ratified this session (DO NOT revisit)
| Decision | Value |
|---|---|
| iter94 build + shape | Fix B 2-line guard (done as 3-line with comments) |
| iter95 build + cap | **400ms as a CEILING** (min(wait,cap)); 0 = legacy shield |
| Deepgram EOT knobs (`DEEPGRAM_EOT_THRESHOLD`, `DEEPGRAM_EOT_TIMEOUT_MS`) | DEFERRED — owner decides AFTER hearing a test call; agent never edits `.env` |
| Merge order | iter93 → iter94 → iter95; every merge = separate owner say-so |
| Combined test-merge lane for iter93's owed fragment replay | OPTED IN (done: wt-9494) |
| Merges | NEVER without explicit owner say-so (LAW 0) |
| Owner's "same branch next time" wish | NOTE for future plans only — AGENTS branch law still stands until owner changes it |
| SDK (fast test lane) | SEPARATE plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter95_sdk_fast_test_lane.md` — owner says it is being written in a PARALLEL session; this session must NOT duplicate it |

### Key reference numbers
- Suite baselines: main tip `06bdd97` = 490/3/0; iter94 tip = 495/3/0; iter95 tip = 496/3/0.
- Full-suite wall time on OREGON: ~20-25 min (the reason the SDK plan exists).
- Savage evidence: 169 awaits → 163 already_done, 6 lost races 1,218-2,324ms (Proof 2,
  `/tmp/opencode/wt-95/scripts/savage_latency/README.md`).
- iter93b evidence: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/`
  (01_evidence.md, 02_fix_shape.md exist; 03_validation.md + 04_report.md to write; 05_ttft_benchmark.md at T6).

## BLOCKED / NEEDS INPUT
| Item | How to unblock |
|---|---|
| **Owner GO on this plan** | owner says GO |
| Merge say-so x3 (93, 94, 95) | owner in-chat after validation evidence shown |
| Owner's Mac mic (optional, only for HIS ear verdict) | his side; not blocking the scripted validation |

## Environment & Dependencies
- OREGON ssh (top of file). Python venv: `/tmp/opencode/wt-9494/engine/.venv` (symlink to
  `/home/julio/projects/clean_diallux_SDR/engine/.venv`, Py 3.12, pytest 9.1.1).
- Lane boot (if 8049 is down): `cd /tmp/opencode/wt-9494/engine && set -a && . ./.env && set +a && DEEPGRAM_RAW_DUMP=true setsid nohup .venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8049 > /tmp/opencode/lane-8049.log 2>&1 < /dev/null &`
- NEVER touch OREGON ports 8001/8002/8003/8026/8090/8080. NEVER checkout/switch/reset the
  OREGON main checkout. Docs writer = `/tmp/opencode/wt-main-docs` only.
- Owner mic page (optional): `http://localhost:8049/mic?k=$VOICE_TEST_TOKEN` via his SSH
  tunnel; token lives in `/tmp/opencode/wt-9494/engine/.env` (line 51, 48 chars — print it
  FULL, never truncated).
- Evidence ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (import: `scripts/live_sql.py import --window "…" --run <name> --commit <sha>`).
- Registry: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db`
  (refresh = `scripts/call_ledger.py` from the MAIN checkout `engine/` dir; backup first).

## Architecture
```
validation (scripted, no owner mic needed):
  scripts/llm_mic_caller.py --persona Sam, gaps 9-13s  ──►  ws://127.0.0.1:8049/mic/ws
        (the iter80 battery transport — Cartesia caller voice, real-time PCM)
  expected in /tmp/opencode/lane-8049.log:
    "pause ladder rung 1 spoken"  — exactly ONE per silence stretch
    NO second rung while stretch continues; fragment replies do NOT re-arm
    "pause ladder close" + goodbye + ws close 1000 at ~45s of true silence
    "await_warm ... outcome=aborted ... cap_ms=400" (iter95) — waits ≤ ~450ms
then: owner say-so → merge --no-ff x3 in order 93→94→95 → tag each → git-tree.sh
      → registry refresh (backup first) → ITERATIONS.md lines → docs push → FI ff-sync.
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/03_validation.md` | validation evidence (gitignored) | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/04_report.md` | close-out report (gitignored) | NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter94_ladder_silence_savage_warm.md` | verdict appended at close | EDIT |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter93b_call_pollution_assess.md` | T2-T5 superseded pointer (verify it exists; write if missing) | EDIT/NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-84 → DONE at merge | EDIT |
| `/home/julio/projects/clean_diallux_SDR/plans/ITERATIONS.md` | iter94 + iter95 + iter93 merge lines | EDIT |
| NO engine/ files | everything already committed on branches | — |

## Deploy Rules
- Lanes ONLY via `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh` (numeric iter).
- Merge ceremony per branch, ONLY on owner say-so: on the branch's worktree
  `git merge --no-ff` is NOT how it works — merges land INTO main: switch
  `/tmp/opencode/wt-main-docs` (which IS main) — NO: main merges happen on a THROWAWAY
  main worktree only if owner approved; the standing procedure per AGENTS: merge on the
  main checkout is forbidden — use `/tmp/opencode/wt-main-docs` (tracks main):
  `git -C /tmp/opencode/wt-main-docs merge --no-ff <branch> && git -C /tmp/opencode/wt-main-docs tag engine/iterNN && bash /home/julio/projects/clean_diallux_SDR/scripts/git-tree.sh`
  (run git-tree.sh from wt-main-docs). Registry refresh AFTER all merges (backup first).
- keyhound before every push; docs push via wt-main-docs:
  `git -C /tmp/opencode/wt-main-docs -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push origin main`
- Finland sync at the end: `git -C /home/julio/projects/clean_diallux_SDR fetch origin && git -C /home/julio/projects/clean_diallux_SDR merge --ff-only origin/main`
- NEVER rsync/scp repo content. Cal.com test bookings (event 3801235 REAL): cancel
  everything after any booking-touching run.

## Tasks (in order)

### T0 — Owner GO (HITL — the only gate)
Goal: owner reads this plan; GO on validation-first (recommended) or skip-to-merges.
Verification: owner GO recorded in-chat; Status flips to IN PROGRESS.

### T1 — Live validation call (scripted — owner mic NOT required)
Goal: run the caller and collect the proof lines.
Commands (OREGON):
`cd /tmp/opencode/wt-9494/engine && set -a && . ./.env && set +a && timeout 260 .venv/bin/python scripts/llm_mic_caller.py --ws-url "ws://127.0.0.1:8049/mic/ws?k=$VOICE_TEST_TOKEN" --scenario happy --persona Sam --min-gap 9 --max-gap 13 --max-run-s 240 --out /tmp/opencode/iter94-live-journal.jsonl`
Then:
`grep -a -E "pause ladder|await_warm|round usage" /tmp/opencode/lane-8049.log | tail -40`
Verification (ALL must hold): exactly one "rung 1 spoken" per silence stretch; NO repeat
rungs while a stretch continues; close + goodbye + ws close 1000 only after ~45s true
silence; `await_warm` outcomes include `aborted` with `cap_ms` ≤ 400 and `waited_ms`
≤ ~450; zero `held_swallow` warnings; caller completed a real booking flow (happy).
Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/03_validation.md`
with the excerpts. Ledger import: `scripts/live_sql.py import --window "<HH:MM-HH:MM of run>" --run iter94-ladder-validate --commit 9eb341c`.
If the owner WANTS his own ear call (optional): give him the full token URL, wait for his
verdict — his call may replace/augment the scripted one.

### T2 — ASK JULIO: merge say-so x3 (LAW 0)
Goal: show the validation evidence + suite counts; ask for merges in order 93 → 94 → 95.
Verification: three explicit say-so in-chat (or explicit refusals).

### T3 — Merge ceremony (only on say-so)
Goal: per branch in order: merge --no-ff on wt-main-docs, tag `engine/iter93`,
`engine/iter94`, `engine/iter95`, `scripts/git-tree.sh`, ITERATIONS.md lines,
registry refresh (backup `ledger.db` first), docs push, FI ff-sync.
Verification: tags exist on main; GIT_TREE.md fresh; registry rows for the three tips;
Finland `git log origin/main` shows them.

### T4 — Close-out report
Goal: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/04_report.md`
(SHAs, suite counts, evidence links, what remains); PT-84 → DONE; parent plan verdict
appended; Deepgram knob decision reminder TO THE OWNER (still his call).
Verification: files exist; PENDING_TASKS updated; this plan Status = DONE.

### T5 — TTFT benchmark (the chain's LAST commit)
Goal: prove the stack returns toward the 650ms TTFT run (ledger `rounds.ttft_ms` joined
`runs`, candidates iter90-mic-b0-class; savage README b0 @ 765). Battery on the merged
lane vs main lane; decomposition (ladder waste gone by construction; aborted=0ms waits;
single-stream rounds). Evidence
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/05_ttft_benchmark.md`
+ ledger run `iter95-ttft-benchmark`. Verification: median TTFT ≤ 650ms or per-round
accounting of every ms above it. Commit the evidence docs LAST.

## Validation Plan (end-to-end)
T0 GO → T1 scripted call clean (one nudge/stretch, close@45s, aborted ≤400ms waits) →
T2 say-so → T3 merges+tags+registry → T4 report → T5 benchmark LAST. The success metric
is the CALL, not the suite. NO merges without owner say-so.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Deepgram EOT knob values | owner-set, after he hears the call |
| SDK fast-test-lane build | separate parallel session, own plan (see Compaction Context) |
| Owner's Mac mic repair | his side; scripted validation does not need it |
| Savage candidates 3 (RAG off hot path) / 4 (process split) | own branches later |
| Cleanup deletions (wt-92, engine/92-92b-4gk-quant, wt-merge87, wt-iter91 lane, wt-94/wt-95/wt-9494 after merges) | owner trigger word |
| iter77-twilio-iter70 parked merge @ 8c5f72f | owner decision after fixes |
---

## Verdict (CLOSED 2026-10-06)
- T0 GO: owner in-chat ("ok run the merge"). T1 scripted validation: Maria booked live (uid r3F7uGWKd4M7baLatzPczi, cancelled+verified). T2/T3: merges executed 93→94→95, zero conflicts, tags engine/iter93|94|95, GIT_TREE regenerated, ITERATIONS line, PT-84 DONE.
- Bonus live evidence: owner's REAL Twilio call via voicetest.diallux-ai.site (OREGON): TTFT p50 962 / e2e_turn p50 1882, iter95 aborted x12 @ waited_ms=0, ladder idle, 0 held_swallow/degraded/errors — trace 152d98c0c8d73f27680d950f2914e1bb.
- T4 report: superseded by plans/SESSION_2026-10-06_iter93_94_95_working-but-not-great.md (owner-ordered session save; status WORKING BUT NOT GREAT).
- T5 benchmark: NOT run — carried into the next mission (e2e_turn p50 <= 1200ms goal).
- Status: DONE except T5.
