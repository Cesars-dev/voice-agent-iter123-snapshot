# plan_v5_iter94 — THE SILENCE-LOOP FIX (iter94: ladder stretch guard) + SAVAGE WARM ABORT (iter95): two REAL branches from main tip, merge each step of the chain

## Meta
- Date: 2026-10-06
- Project root (OREGON source of truth): `/home/julio/projects/clean_diallux_SDR`
- Session box: Finland (julio @ 46.62.233.228). ALL repo git ops ssh-wrapped to OREGON:
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'`
- Scope: TWO independent code branches cut from MAIN TIP, never stacked:
  **iter94** = the pause-ladder silence-loop fix (the "Hey, are you still there?" every-8s
  disease, 2-line guard) + fake-clock pins; **iter95** = savage piece 1, the warm
  cancel-not-wait abort cap in `_await_warm` (measured 1.2–2.4s lost races, 4% of awaits).
  Each branch: own lane, own pins, own ASK, own merge ceremony. Supersedes
  `plan_v5_iter93b_call_pollution_assess.md` tasks T2–T5 (its T1 evidence is DONE).
- Status: **IN PROGRESS — owner GO 2026-10-06 (in-chat "run", proceed with recommended
  defaults): iter94 Fix B shape GO, iter95 cap `prewarm_abort_cap_ms=400`, Deepgram knobs
  DEFERRED to T4, merge order 93→94→95, combined test-merge lane OPTED IN.**

## Compaction Context

### The disease (iter93b T1 evidence, DONE — `research/surgeon/iter93b-call-pollution-assess/01_evidence.md` on OREGON)
1. **The 8s nag loop (CODE, iter94 fixes it):** `_ladder_arm()` at
   `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:364` (main tip
   `06bdd97`) cancels the running ladder — **including its pending 45s close** — resets
   `_ladder_step = 0` (:373), and starts a fresh `_ladder_run()` (:377: nudge at t0+8s,
   `max_n=1`, close at t0+45s). It is called on **EVERY agent turn** from TWO sites:
   `on_twilio_mark` :434 (every `turn-N-done` mark echo) and `_late_turn_report` :851
   (browser transport — the live mic-bridge call). Every agent turn — including
   fragment-triggered replies like "Absolutely, go ahead" — restarts a full fresh 8s nag
   clock. The caller can never be silent >8s without being nagged; the 45s goodbye can
   never fire while the conversation produces any turns. Verified: the nudge itself
   (`_speak_exact` :343) sends NO turn mark and NO turn report → it never re-arms itself;
   pure-silence behavior is already spec-clean (one nudge → close at 45s). The pollution
   is 100% turn-driven re-arming.
2. **The mid-thought speaks (KNOBS, owner-set only, NOT code):** Deepgram EOT confirm
   (`deepgram_eot_threshold=0.65`, `config.py:354`) lands in 2–600ms on the owner's
   fragment cadence (trace `2d3cfa48773a`: turn 7 eager→confirm **2ms**) → engine releases
   the held draft → Linda answers a fragment → turn report → ladder re-arm. The two
   diseases compound into the felt every-8s cadence.
3. **Fix B (owner-shown, in `02_fix_shape.md`):** one guard in `_ladder_arm`:
   `if self._ladder_task is not None: return` — already armed mid-stretch = agent turn
   must NOT restart it. Effect: ONE nudge per silence stretch (stretch = caller speech →
   disarm :559/:695 → next agent turn end → arm), close at 45s anchored at stretch start.

### The savage assessment (owner question ANSWERED from code)
- **Owner question: "when we cancel the eager EOT releases, are we actually canceling
  the OpenAI code?" — YES, it is a REAL cancel.** Resume/barge does `_turn_task.cancel()`
  → CancelledError is delivered at the innermost await = inside
  `bound.astream(messages)` (`/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py:326`
  `async for chunk in bound.astream(messages)` inside `astream()` :297) → the async
  generator closes → the OpenAI SDK closes the httpx response → the stream is aborted
  client- AND server-side; output tokens stop; only the input/prefill is billed — and
  that prefill IS the prefix cache we keep. NO `asyncio.shield` anywhere in the turn
  path (shields only wrap WARM awaits). **There is no latency left to save on the eager
  cancel — it is already true cancellation. No work needed.**
- **Where latency IS lost: the WARM path (savage piece 1, NOT done, owner-PARKED
  2026-10-05, now proposed as iter95).** Savage doc:
  `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/README.md` (on main,
  landed `b572cb9`). `_await_warm` at
  `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py:635-672` does
  `await asyncio.wait_for(asyncio.shield(task), wait_ms/1000)` — on timeout the shield
  KEEPS the warm running (by design, iter46). Measured (savage README proofs, iter92b
  battery): 169 awaits → 163 already_done (96%), **6 lost races waited 1,218–2,324ms**
  of the 2,500 cap — the wait sits in the S→L window (the caller's ear), NOT in TTFT;
  plus spec+real+warm 3-stream collisions on one key → TTFT spikes 2–2.7s. Savage fix:
  **cancel-not-wait** — when the real turn fires and the warm is mid-completion, ABORT
  the warm; the prefix cache it wrote at prefill survives server-side (Proof 1:
  after-abort TTFT 857ms ≈ hit-class 914 vs cold 1,421).
- **Collision check: NONE.** `git diff origin/main e57d2b2 -- engine/diallux/media/session.py`
  contains ZERO `_ladder` lines — iter93 does not touch the ladder. iter94 touches
  `session.py:_ladder_arm` (2 lines); iter95 touches `builder.py:_await_warm` +
  `config.py` (one knob). Disjoint files, disjoint flows → **no plan C needed; the two
  branches cannot collide with each other or with iter93's pending merge.**

### Git topology (verified this session)
- `origin/main` tip = `06bdd97` (plan iter93b doc). **iter93 branch = `e57d2b2`**
  (3 commits, suite 502/3/0, UNMERGED, owner say-so pending). main is NOT an ancestor of
  `e57d2b2` (iter93 was cut before the last docs commits) — irrelevant for merges:
  iter93 merges to main with --no-ff regardless.
- main HAS the ladder (promoted iter91): `config.py:469-476` (`pause_ladder_mode="reminder"`,
  `pause_reask_ms=8000`, `pause_ladder_max=1`, `pause_close_ms=45000`).
- OREGON main checkout `/home/julio/projects/clean_diallux_SDR` is PARKED on stale branch
  `engine/iter73-oregon-wip-20260924` — its FILES are stale; never trust them; code
  reads come from `git show origin/main:<path>` or `/tmp/opencode/wt-main-docs/`.
- Owner directive (2026-10-06): "really branch this thing… another whole branch, not
  another commit… clear Git structure where we can check which branch is acting each
  way, then safely merge each step of the chain." → TWO branches from MAIN TIP, each
  mergeable alone (per AGENTS.md branch law: NEVER stack onto an existing iteration
  branch — stacking would smuggle one iter's code into the other's merge).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| iter94 = ladder Fix B (the 2-line guard), branch `engine/iter94-ladder-stretch` from main tip | owner shown the diff shape; fewest edits; impossible to desync step state; close anchors at stretch start (truer to "45s total silence" SPEC) |
| iter95 = savage piece 1 (warm cancel-not-wait abort cap), branch `engine/iter95-savage-warm-abort` from main tip | savage README candidate order (1) warm cap first; measured 1.2–2.4s losses; owner asked for it |
| Two branches, NEVER stacked, each with own lane/pins/ASK/merge ceremony | owner directive "really branch it… merge each step of the chain"; AGENTS branch law (iter64c lesson) |
| No changes to the eager-cancel path — it is ALREADY a true OpenAI cancel | code-verified (task.cancel → astream generator close → httpx abort); zero latency to recover there |
| savage candidates 2/3/4 stay deferred (2 is effectively already done via task.cancel + iter93 epoch cleanup; 3 = RAG off hot path; 4 = process split) | savage README adoption gate; scope discipline |
| Deepgram knobs (`DEEPGRAM_EOT_THRESHOLD`, `DEEPGRAM_EOT_TIMEOUT_MS`) = owner-set `.env` only, ride the iter94 lane AFTER owner gives numbers | SWITCH LAW; owner never delegated knob values |
| This plan supersedes iter93b T2–T5; iter93b T1 evidence is DONE (01_evidence.md + 02_fix_shape.md on OREGON) | iter93b plan pointed here |
| Numbering: ladder branch mints **iter94**, savage branch mints **iter95** | ITERATION NUMBERING LAW: each new code branch increments |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| **Owner review + GO on THIS plan** (the only gate) | owner reads this file; nothing below T0 runs before GO |
| Deepgram knob numbers (proposal: `DEEPGRAM_EOT_THRESHOLD` 0.65→0.75–0.85; `DEEPGRAM_EOT_TIMEOUT_MS` 3000→4000–5000) | owner says the numbers; agent never edits canonical `.env` |
| Warm-abort cap number (savage README: ~300–400ms; proposal: `prewarm_abort_cap_ms=400`, 0 = legacy wait-shield) | owner may veto; default rides the branch's own tests per SWITCH LAW point 4 |
| iter93 merge say-so (rides T5 ASK) | after a clean fragment replay |
| Does iter93's outstanding fragment replay ride the iter94 validation lane as a local test-merge (wt lane merges iter93+iter94 for TESTING only, main untouched)? | owner opt-in at T4 |

## Environment & Dependencies
- Python venv (ONLY this): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`
  (Py 3.12; never `bin/pip`, always `-m pip`).
- Lane creation (LANE LAW, ONE command, from repo root on OREGON):
  `ssh … root@5.78.83.174 '/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh iter94 06bdd97 ladder-stretch'`
  and later `… new_lane.sh iter95 <main-tip-after-iter94-merge> savage-warm-abort`.
  Exit 0 = READY; exit 1 = DOA, fix env first. Venv is symlinked; `.env` generated from
  canonical (audited against known-bad values).
- Suite: `cd /tmp/opencode/wt-94/engine && .venv/bin/python -m pytest tests -q`
  (baseline 502 passed / 3 skipped / 0 failed at iter93; main-tip baseline may differ by
  a few — record the pre-change count first, it must not regress).
- Lane boot (after stopping whatever holds the port — wt-93 server was pid 1545931 on 8049):
  `cd /tmp/opencode/wt-94/engine && set -a && . ./.env && set +a && setsid nohup .venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8049 > /tmp/opencode/lane-8049.log 2>&1 < /dev/null &`
- Key files (main tip `06bdd97` line numbers):
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` — `_ladder_arm` :364,
    `_ladder_step = 0` :373, `_ladder_run` :377, `_speak_exact` :343, arm sites :434 (twilio
    mark) and :851 (browser late-report), disarm sites :559 (speech growth) and :695
    (start_of_turn)
  - `/home/julio/projects/clean_dialux_SDR/engine/diallux/graph/builder.py` — `_await_warm`
    :635-672 (shield+wait_for at :656), `warm_prompt_cache` :473, `_latest_warm` :404
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py` — `warm()` :288
    (fire-and-forget `ainvoke`), `astream()` :297 (chunk loop :326 — the cancel point)
  - `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` — ladder :469-476,
    Deepgram :354-356, prewarm `prewarm_entry_wait_ms` (search `prewarm_entry_wait_ms`)
- Savage references: `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/README.md`
  (+ `cache_abort_probe.py`, `warm_race_audit.py` — the auditor for T4:
  `python3 scripts/savage_latency/warm_race_audit.py /tmp/opencode/lane-8049.log`)
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/`
  (01_evidence.md, 02_fix_shape.md written; 03/04 land during execution)
- Langfuse (OREGON, `http://localhost:3001`), from engine dir with `.env` loaded:
  `sys.path.insert(0, 'scripts'); import lf; lf._get('/api/public/traces?fromTimestamp=' + lf._iso(2) + '&limit=20')`
- Ledgers: findings `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  (import `scripts/live_sql.py import --window "…" --run <name> --commit <sha>`); registry
  `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db`
  (generator `scripts/call_ledger.py`, from MAIN checkout engine dir, backup first).
- GitHub push (any OREGON worktree):
  `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push origin <ref>`
  (`-c` BEFORE `push`); keyhound before EVERY push; standing 259-hit noise = legacy
  `services/*`; only the NEW diff must be 0 key-shaped strings.
- Owner access: ssh tunnel Mac→OR (`ssh -N -L 8049:127.0.0.1:8049 root@5.78.83.174`),
  `http://localhost:8049/mic?k=<VOICE_TEST_TOKEN>` (fail-closed gate, 4401 on mismatch).

## Architecture (branch topology)

```
origin/main 06bdd97 ──┬──► engine/iter94-ladder-stretch   (session.py: 2-line guard + pins)
                      │         └─ ASK ─► merge --no-ff, tag engine/iter94 ─┐
                      │                                                     ├─► main
                      ├──► engine/iter93 (e57d2b2, UNMERGED, pending say-so)┤   (each step
                      │         └─ ASK ─► merge --no-ff, tag engine/iter93 ─┤    merged
                      └──► engine/iter95-savage-warm-abort (builder.py cap)┘    alone)

engine/iter95 cut from main tip AFTER iter94 merges (fresh tip, still never stacked)

Runtime effect (iter94):   agent turn ends ─► _ladder_arm ─► ALREADY ARMED? ──► return (no restart)
                           caller speech ──► _ladder_disarm (:559/:695) ──► next turn end arms fresh
                           stretch = ONE nudge @8s ─► close @45s. Forever-nag: DEAD.

Runtime effect (iter95):   real turn fires, warm mid-completion ─► ABORT warm (cache survives)
                           ─► real round reads prefix cache ─► hit-class TTFT, one stream/key.
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | iter94: 2-line guard in `_ladder_arm` (:364): `if self._ladder_task is not None: return` | EDIT (branch iter94) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter94_ladder_loop.py` | iter94 pins: fake-clock — one nudge per stretch; fragment turn mid-stretch does NOT re-nudge; close fires t0+45s despite N agent turns; caller speech resets stretch; nudge never self-re-arms | NEW (branch iter94) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | iter95: `_await_warm` (:635-672) cancel-not-wait — warm mid-completion at cap → `task.cancel()`, outcome `aborted`; the shield-on-timeout "keep running" semantics become opt-out | EDIT (branch iter95) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` | iter95: new Settings field `prewarm_abort_cap_ms: int = 400` (0 = legacy wait-shield behavior) | EDIT (branch iter95) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter95_warm_abort.py` | iter95 pins: nearly-done warm adopts (unchanged); mid-completion warm aborts at cap and round proceeds; pre-inflight abort = baseline round; cap=0 = legacy shield behavior; abort writes NOTHING to history (no garbage) | NEW (branch iter95) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter94_ladder_silence_savage_warm.md` | THIS plan; verdict appended at close | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter93b_call_pollution_assess.md` | Pointer: T2–T5 superseded by this plan | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-84 pointer update; register the iter95 savage piece (PT if owner wants a number) | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter93b-call-pollution-assess/03_validation.md`, `04_report.md` | Execution evidence (gitignored) | NEW (gitignored) |

## Deploy Rules
- LANE LAW: lanes ONLY via `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh` —
  never hand-copied `.env`, never borrowed venvs.
- NO /opt. NO original-repo services. Lanes 127.0.0.1 only. OREGON listening now:
  8001/8002/8003/8026/8090 + 8080 caddy — NEVER touch. Stop the wt-93 server on 8049
  before any new lane boot.
- OREGON main checkout: NEVER checkout/switch/reset/pull. Docs writer =
  `/tmp/opencode/wt-main-docs` only.
- NEVER stack branches: iter94 and iter95 each cut from main tip via new_lane.sh.
- Merge ceremony (each branch, ONLY on owner say-so): `merge --no-ff` → tag
  `engine/iterNN` → `scripts/git-tree.sh` → registry refresh (backup `ledger.db` first)
  → ITERATIONS.md line. keyhound + diff-scanned (0 key-shaped strings) before every push.
- All sync OREGON → GitHub → Finland (`git fetch && git merge --ff-only origin/main` on
  FI). NEVER rsync/scp repo content.
- Cal.com test bookings: cancel everything after ANY booking-touching battery
  (event 3801235 REAL).

## Tasks (in order)

### T0 — Owner review + GO (HITL — THE ONLY GATE)
Goal: owner reads this plan; GO on: (a) iter94 Fix B shape, (b) iter95 warm-abort scope +
cap number, (c) Deepgram knob numbers (may be deferred to T4), (d) merge-order preference
(default: iter93 → iter94 → iter95, all three disjoint), (e) opt-in on the combined
test-merge lane for iter93's fragment replay.
Files: none (this file is the artifact).
Verification: owner GO recorded in-chat; plan Status flips to IN PROGRESS.

### T1 — Cut iter94, implement the guard, pin it (branch `engine/iter94-ladder-stretch`)
Goal: lane via `new_lane.sh iter94 06bdd97 ladder-stretch`; the 2-line guard in
`_ladder_arm`; write `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter94_ladder_loop.py`.
Commands: lane cmd per Environment §; edit; `cd /tmp/opencode/wt-94/engine && .venv/bin/python -m pytest tests -q`.
Verification: suite green (main-tip baseline + new pins, zero regressions); pins FAIL on
the pre-fix tree (stash proof: `git stash && pytest tests/test_iter94_ladder_loop.py -q`
→ red; `git stash pop` → green).

### T2 — ASK JULIO: merge iter94 (branch complete)
Goal: present suite counts + pin proofs; on say-so: merge --no-ff, tag `engine/iter94`,
`scripts/git-tree.sh`, registry refresh (backup first), ITERATIONS.md line.
Verification: `engine/iter94` tag on main; GIT_TREE.md not stale; registry row exists.

### T3 — Cut iter95, implement the warm abort cap (branch `engine/iter95-savage-warm-abort`)
Goal: lane via `new_lane.sh iter95 <main-tip-after-T2> savage-warm-abort`; rework
`_await_warm` per the savage README state table (completed → adopt, unchanged;
mid-completion → wait up to `prewarm_abort_cap_ms` then CANCEL;
pre-inflight → cancel immediately); knob in `config.py` (0 = legacy); pins in
`test_iter95_warm_abort.py` incl. the no-garbage invariant (aborted warm writes nothing
to state/history — adoption only accepts completed warms).
Commands: same pattern as T1.
Verification: suite green; pins FAIL pre-fix (stash proof); `warm_race_audit.py` dry-run
against an old lane log shows the parser still reads outcomes (new `aborted` outcome).

### T4 — Live validation on the lane (owner in the loop)
Goal: boot the fixed lane on 8049 (owner's fragment pattern + a deliberate long thinking
pause). Verify in `/tmp/opencode/lane-8049.log` + Langfuse: ONE nudge per silence
stretch, zero repeat nudges, close fires at 45s of true silence, zero `held_swallow`;
for iter95: `await_warm outcome=aborted` rounds run hit-class TTFT, zero >1s lost-race
waits. If owner opted in: local test-merge lane (iter93+iter94) for the fragment replay
(iter93's outstanding validation rides here).
Commands: lane boot per Environment §; `python3 scripts/savage_latency/warm_race_audit.py /tmp/opencode/lane-8049.log`;
ledger import `scripts/live_sql.py import --window "…" --run iter94-ladder-validate --commit <tip>`.
Verification: `03_validation.md` written with the log excerpts + audit tables; owner ear
verdict on the call.

### T5 — Report, close-out, ASK JULIO
Goal: `04_report.md` (both branches: SHAs, suite counts, evidence links); PT-84 → DONE at
merge; PENDING_TASKS + ITERATIONS lines; registry refresh (backup first); docs push via
`/tmp/opencode/wt-main-docs`; FI sync verify (`git fetch && git merge --ff-only origin/main`).
Verification: ASK JULIO contains: iter95 merge say-so (if not yet merged), iter93 merge
say-so (if fragment replay was clean), knob ratification, cleanup say-so for wt-92 /
engine/92-92b-4gk-quant / wt-merge87 / wt-iter91 lane.

### T6 — TTFT regression benchmark: back to 650 ms (THE LAST COMMIT in the chain)
Goal: measure exactly where iter94+iter95 save TTFT and prove the stack returns to the
**650 ms TTFT run** (owner-cited historical run — pin WHICH run from the ledger
`research/surgeon/iter48-rag-truth/ledger.db` table `rounds` (`ttft_ms`), join `runs`
on `run_id`, order by avg; candidates: the iter90-mic-b0-class pre-tier runs — savage
README has b0 @ 765; the 650 run predates the b250 wait tier). Method: same battery on
the fixed lane vs the current main lane; per-round TTFT + the decomposition
(ladder-restart S→L waste: gone by construction; warm wait: `await_warm outcome=aborted`
= 0 ms vs 1.2–2.4 s lost races; stream collisions: single-stream/key rounds). Evidence =
`05_ttft_benchmark.md` (gitignored) + ledger import run `iter95-ttft-benchmark`. This
task's evidence/docs commit is deliberately the LAST commit of the chain so the ledger
line reads as the chain's final verdict.
Files: `/home/julio/projects/clean_dialux_SDR/research/surgeon/iter93b-call-pollution-assess/05_ttft_benchmark.md`.
Verification: median TTFT ≤ 650 ms on the battery, or a per-round accounting of every ms
above it (named component, measured) — no hand-waving.

## Validation Plan (end-to-end)
T0 owner GO → T1 iter94 green + pins proven → T2 merged (say-so) → T3 iter95 green +
pins proven → T4 the CALL is clean: one reminder per stretch, close at 45s, no
mid-thought barges at the owner's knob settings, no >1s warm waits → T5 records + ASK →
T6 TTFT benchmark: back to 650 ms median, evidence commit LAST in the chain.
The success metric is the CALL, not the suite. NO merges without owner say-so.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Savage candidate 2 (eager spec client-abort on resume) | effectively ALREADY DONE — `task.cancel()` is a true OpenAI stream abort (code-verified this session); nothing to build |
| Savage candidate 3 (RAG off hot path, 85–131ms/round) | savage README order; own branch later |
| Savage candidate 4 (process split) | skipped per savage README — rewrite-grade risk |
| C — confidence-band repair ("say that again?") | own branch; gated on the confidence table |
| PT-81 same-state re-round warm | after savage piece 1 lands |
| PORT-list remainder (P4/P7/P6) | later, one per branch |
| Real Twilio PSTN cutover | own session after merges |
| iter77-twilio-iter70 (parked merge-ready @ 8c5f72f) | owner decision after fixes |
| Cleanup deletions (wt-92, engine/92-92b-4gk-quant, wt-merge87, wt-iter91 lane) | owner trigger word; T5 asks |
