# plan_v5_iter88_intake_refer_drill — FIX the Intake refer-tag pollution + drill FIND-9 further

## Meta
- Date: 2026-09-30 (written at iter87 session close).
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Scope: ONE session. (a) Further ANALYSIS of FIND-9 (retrieval quality) — which
  sub-cause dominates, replayed against the ledger rag plane; (b) the ONE-LINE
  prompt fix in /home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/Intake.md:35
  (PT-74) on a fresh engine branch; (c) battery re-run + G1 must go PASS.
- Status: PLAN ONLY (not started — awaits owner approval at T0).

## Compaction Context (iter87 session close 2026-09-30 — carried verbatim)

**iter87 VERSION B EXECUTED — PASS.** Branch `engine/iter87-prewarm-hold` @ `02eb2ac`
(cut from 542d3e8, pushed, UNMERGED — owner merge pending). Worktree
/tmp/opencode/wt-iter87. Diff = builder.py (6 sites: successor map :352, entry_lite
HOLD replacing the `pass` @ :1846-1852 + 10 ms settle `await asyncio.sleep(0.01)`
per owner, one-ahead FSM-successor warms after F4 :2552-2554, chain-start warms ALL
transition_to_* destinations after the `plan` list :2660-2668, Closing post-patch
force re-fire before phaseb:chain_ok, ttft hoisted to stream-loop top T1.4) +
config.py (1 knob `warm_await_dest_ms: int = 0` next to prewarm_entry_wait_eot_ms;
default 0 = byte-exact; gates FIRE+HOLD as ONE unit). T1.4b = SDK-side (owner-ratified).
Tests: /tmp/opencode/wt-iter87/engine/tests/test_iter87_prewarm_hold.py — 10/10 green;
full suite 7 failed / 472 passed = the known stale reds ONLY (test_delivery ×4,
iter46 fast-first-flush, iter59, iter60). One new red was introduced mid-build by the
ungated one-ahead warms (they stage RAG → broke iter31/iter44 pins) — FIXED by gating
all three fire sites behind `warm_await_dest_ms > 0` (S4/S5/S6 gates).

**Battery (lanes 8047 happy / 8048 barge-loop, WARM_AWAIT_DEST_MS=2500 + round-B knobs):**
ZERO cold destination rounds (K1 FIXED — chain warms landed VerifyLead/Booking/Closing,
Closing ack held already_done after booking); 0 no_task, 0 timeout (fence never bound);
eager_final_match 100%; 0 held-path cancels. Known trade: eager acks catching the warm
in flight hold ~1-1.6 s (uperm p50 1,176 happy / 1,048 barge vs baseline 867).
Bookings created (chain `1jSTGwyxzWV7KyfK7SceeE`, speech-path `6kg7LgGwiq8eJjy7VoJ4jQ`)
→ BOTH CANCELLED HTTP 200, 0 upcoming on event 3801235. Ledger `forensics_calls` rows
13-14 appended (iter87_hold_happy / iter87_hold_bargeloop, commit 02eb2ac).

**Latency analysis (LATENCY-PERCENTILE-SOP, ledger run `iter87-hold-battery`):**
rounds=96 · TTFT p50 853 / p90 1,572 · steady p50 853 (≤950 gate PASS) · turn-1
1,957/1664 lite (happy, single sample — drill next) + 724/2688 (barge) · LLM p50 1,221 ·
cache-0 rounds=1 (Closing, same-state mid-turn hysteretic trim — NOT a transition miss;
baselines had 1/3) · cache-hit p50 4,736 (floor 3,712 exceeded = append-only climb OK).
LIVE e2e plane: happy e2e_response p50 1,385 / p90 4,193 / max 5,182 (n=26); barge
p50 1,321 / p90 3,707 / max 4,937 (n=31); STT-EOT→LLM p50 1,096/1,020; LLM→TTS-first
p50 ~205. p90 blown by (a) the S2L spikes (STT-EOT→LLM p90 3.5-3.9k = hysteretic
window trim re-bill every ~5-6 turns, PRE-EXISTING, the next latency surface) and
(b) the eager-ack hold waits. Report:
/home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-prewarm-hold/02_latency_report.md

**THE BUG (PT-74 / FIND-9 drill-down — THIS plan fixes it):**
- G1 (zero 0-chunk state-entries) FAILS on Intake: 16/17 Intake retrievals return
  0 chunks. ROOT CAUSE pinned to ONE prompt line:
  `/home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/Intake.md:35` —
  `#[refer pain-points-kb for the empathic mirror — {{pain_frame}}]` — the DELIVERY
  INSTRUCTION "for the empathic mirror" leaked INTO the refer tag's anchor text,
  so every Intake retrieval query embeds "for the empathic mirror; <caller text>".
- Same family, pre-existing & expected: ConfirmSlots 31/31 and contact_details 27/27
  zero-hits = EMPTY queries (no refer tags with dvs, empty user branch at entry) →
  retrieve("") = 0 chunks by construction (FIND-4 family).
- Ledger: `findings` row **FIND-9** (assessed 2026-09-12, owner request) covers the
  class ("Intake mirror query → 3× industry, pain-points never surfaced"; sub-causes:
  scope dilution, multi-intent single-vector query, no per-KB quota, raw-caller-text
  dilution). `fix_note` updated 2026-09-30 with the pinned line + PT-74 pointer.
- `plans/PENDING_TASKS.md` row **PT-74** (OPEN, 1 line, code zone, LAW 0).
- Provenance: the tag was written in commit `b94dad4` ("c1: RESTRUCTURE", 2026-09-08
  08:25 UTC) — carried 22 days before being drilled to the line.

**Session infrastructure (reusable):**
- Two-box law: session on Finland (MainVps); ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`.
  Worktrees: /tmp/opencode/wt-iter85 (542d3e8), wt-iter86 (d158b4c, SDK), wt-iter87 (02eb2ac).
- Lane boot script EXISTS: /tmp/opencode/boot_lane_iter87.sh (round-B knobs +
  WARM_AWAIT_DEST_MS=2500; systemd-run --user --collect --unit=diallux-<port>.service).
  Lanes 8047/8048 are KILLED and ports free (verified at close).
- Ledger import (working recipe): cd /home/julio/projects/clean_diallux_SDR && set -a &&
  . /tmp/opencode/wt-iter87/engine/.env && set +a && python3 scripts/live_sql.py --db
  research/surgeon/iter48-rag-truth/ledger.db import --window "HH:00-HH:00" --run <run>
  --branch <branch> --commit <sha> (USE THE MAIN-REPO COPY of live_sql.py — the
  worktree copy's window filter returned false-empty; wide windows work).
- SDK: /tmp/opencode/wt-iter86/engine/scripts/call_forensics.py (--trace <id-prefix>
  [--journal]; NOTE: --journal crashed on these traces with a None-ts render bug —
  trace-only works). lf.py: /tmp/opencode/wt-iter86/engine/scripts/lf.py (traces/tools).
- Surgeon procedure: /home/julio/projects/clean_diallux_SDR/tasks/surgeon/iter87-prewarm-hold/
  (01_audit/02_action_plan/03_cross_reference/04_master_plan + archive; committed to main
  @ 308ca5b). Latency report 02_latency_report.md carries the root-cause section.
- Surgoen-framework skill now exists for future sessions (opencode skill).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| iter87 VERSION B = EXECUTED, PASS; branch 02eb2ac UNMERGED (owner merge pending) | LAW 0; battery + gates + ledger complete |
| Hold semantics = TASK await + 10 ms settle; fire+hold gated by ONE knob `warm_await_dest_ms` (default 0 byte-exact) | owner verdicts 2026-09-30; byte-exact suite gate demanded it |
| T1.4b = SDK-side only (no engine turn-report change) | owner-ratified; keeps diff = builder.py + config.py |
| Chain fire = ALL THREE destinations (VerifyLead, Booking, Closing) | owner-ratified ("keep it engine side"); covers abort-repair rounds |
| Per-state prewarm on/off switch = NICE-TO-HAVE in plans/NEXT_STEPS.md | owner deprioritized for this build |
| PT-74 fix = ONE line in engine/diallux/prompts/Intake.md:35 | prompts = code zone → engine branch per LAW 0 |
| FIND-9 stays ONE finding; PT-74 is the drilled sub-cause | avoid duplicate rows; fix_note carries the pointer |
| S2L spike family (hysteretic trim re-bill) = NEXT latency surface, NOT this plan | separate owner decision; needs its own analysis |
| Docs (md) straight to main; CODE waits for owner merge | LAW 0 |
| Two-box law: Finland session, OREGON repo ops ssh-wrapped | iter81 Meta |
| Cancel every test booking (event 3801235 REAL) | paid lesson — done for iter87, repeat for iter88 |
| totalTimeStamps in plan paths = FULL ABSOLUTE PATHS | SOP hard rule |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO on the ONE-LINE rewrite wording (exact new tag text) | T0 = owner approves the proposed line: `#[refer pain-points-kb — missed calls, lost bookings — {{pain_frame}}]` |
| iter87 merge decision (affects the iter88 base) | owner call at T0; plan defaults to base 542d3e8 |
| How much "further analysis" of FIND-9 before the fix | T0 scope call: T2 is read-only drill (bounded 30 min); sub-causes (1)-(3) redesign = DEFERRED unless owner pulls them in |
| happy turn-1 lite 1,957 ms single sample | drill opportunistically in T3 battery; separate surface if confirmed |

## Environment & Dependencies
- OREGON venv (shared): /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python
  (never <venv>/bin/pip — copy-mirror trap; use <venv>/bin/python -m pip).
- Branch base law: cut `engine/iter88-intake-refer-fix` FROM `542d3e8` (the iter85 PASS
  tip — NEVER stack on the unmerged iter87 branch):
  `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter88 -b engine/iter88-intake-refer-fix 542d3e8 && cp /tmp/opencode/wt-iter85/engine/.env /tmp/opencode/wt-iter88/engine/.env`
  (ENV LAW: .env carries the rotated OpenAI key + all round-B knobs).
- If the owner merges iter87 BEFORE this session: cut from origin/main instead.
- Lane ports: FRESH (8047/8048 suggested; verified free). Boot:
  `systemd-run --user --collect --unit=diallux-<port>.service /tmp/opencode/boot_lane_iter87.sh <port>`
  (cd /tmp/opencode/wt-iter87/engine inside the script — EDIT the script's `cd` to
  wt-iter88's engine dir before booting, or make a copy boot_lane_iter88.sh).
- Driver: FROZEN at wt-iter82 (llm_mic_caller.py / llm_mic_caller_b52.py); recipes
  /tmp/opencode/run_driver_iter87_h.sh and /tmp/opencode/run_driver_iter87_bl.sh
  (edit the out/journal names to t88_*).
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (NO sqlite3 CLI — venv python + sqlite3 module only).
- Cal cancel recipe (verified working): read key from
  /home/julio/projects/Retell_AI_MCP_connection/cal_slots_endpoint/.env → `CAL_ACCOUNTS`
  → `dialux_live.cal_api_key`; POST https://api.cal.com/v2/bookings/<uid>/cancel with
  headers `cal-api-version: 2026-02-25` + `User-Agent` mandatory, body
  `{"cancellationReason": "..."}`. HTTP 200 = cancelled.
- MODEL LAW: agent gpt-5.4 everywhere. VOICE LAW: tests = EL Sarah
  (uG1JFy6xppqckhHCs2KG) — verify journalctl `connected`.
- Push law: `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push`
  after scripts/keyhound (246 pre-existing benign doc-noise hits = baseline; ZERO new hits required).

## Architecture (one block)
```
T2 FIND-9 drill (read-only, ledger rag plane) → root-cause ranking
  → T3 ONE-LINE prompt fix (Intake.md:35) on engine/iter88-intake-refer-fix
  → battery re-run (2 lanes) → G1 must PASS + G2/G3/G4 hold
  → ledger rows + report → HITL (owner ear + merge call)
```

## File Map
| File (absolute path) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | THE ladder (STATUS = resume point) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter88_intake_refer_drill.md | THIS plan | itself |
| /home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/Intake.md | THE BUG: line 35 refer tag | T3 — ONE line |
| /home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/ConfirmSlots.md + contact_details.md | empty-query zero-hits (FIND-4 family) — read/analyze only | read (defer fix) |
| /tmp/opencode/wt-iter88 (branch engine/iter88-intake-refer-fix, cut at T1) | the build | build here |
| /tmp/opencode/wt-iter87 (branch engine/iter87-prewarm-hold @ 02eb2ac) | iter87 PASS base + lane script reference | read only |
| /tmp/opencode/wt-iter86 (branch engine/iter86-warm-sync @ d158b4c) | forensics SDK | SDK use |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db | ledger (runs/rounds/rag/findings/sops/forensics_calls) | append |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter88-intake-refer-drill/ | battery + SDK outputs + reports (NN_*.md) | append |
| /home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md | PT-74 row | append/close |

## Deploy Rules
- NEVER touch the OREGON prod checkout git state (df23d37) / diallux.service /
  :8026/:8000-8003/:8090.
- Lanes: fresh ports, systemd-run --user --collect, killed at close + `ss -ltnp` verified.
- ENV LAW: copy wt-iter85 engine/.env into every new worktree before ANY run.
- Cancel every test booking (Cal event 3801235 REAL; cancel POST needs cancellationReason).
- Doc commits: docs worktree off origin/main → commit → push origin HEAD:main →
  re-sync Finland mirror (scp committed files back) → remove docs worktree.

## Tasks (in order)
### T0 — HITL: owner GO + exact fix wording (10 min)
1. Present the ONE-LINE rewrite (old vs new) + the T2 analysis scope. Owner approves
   the wording (or dictates his own). If the owner merges iter87 first, re-pin the
   base commit (Environment).
Verification: owner says GO; base commit pinned in this plan's margin notes.
Unblocks: T1.
### T1 — branch cut + worktree (5 min)
Goal: /tmp/opencode/wt-iter88 on engine/iter88-intake-refer-fix @ 542d3e8.
Commands: exactly as in Environment & Dependencies (branch cut line).
Verification: worktree exists; `.env` has OPENAI_API_KEY (never print the value).
Unblocks: T2.
### T2 — FIND-9 drill (read-only analysis, 30 min, NO code)
Goal: rank the sub-causes with ledger evidence BEFORE the fix.
Commands:
- rag-plane per-KB distribution:
  /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python - <<EOF with sqlite3 on
  /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db:
  SELECT state, kind, COUNT(*), SUM(chunks=0), AVG(ms) FROM rag WHERE run_id='iter87-hold-battery' GROUP BY state, kind;
- zero-hit query text census: SELECT state, chunks, substr(query,1,80) FROM rag WHERE
  run_id='iter87-hold-battery' AND chunks=0 LIMIT 30;
- baseline comparison vs run fix1-happy / fix1-bargeloop (same shape).
Output: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter88-intake-refer-drill/00_find9_drill.md
(table: state | n | zero-hit | query pattern | dominant sub-cause (1)(2)(3)(4)).
Verification: every claim = a SQL row; the Intake dominant cause = (4) tag-text
pollution (expected from iter87 evidence).
Unblocks: T3.
### T3 — the ONE-LINE prompt fix + battery (60 min)
1. Edit /home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/Intake.md line 35
   (worktree copy): replace
   `#[refer pain-points-kb for the empathic mirror — {{pain_frame}}]`
   with the T0-approved line (default:
   `#[refer pain-points-kb — missed calls, lost bookings — {{pain_frame}}]`).
   NOTHING ELSE in the file (one variable).
2. pytest /tmp/opencode/wt-iter88/engine: `.venv/bin/python -m pytest tests -q`
   → 7 stale reds ONLY (zero new).
3. Battery: copy/edit boot script to /tmp/opencode/boot_lane_iter88.sh (cd →
   /tmp/opencode/wt-iter88/engine); boot 8047+8048; journalctl `connected` = elevenlabs
   Sarah; run BOTH drivers (recipes above, outputs t88_*); frozen driver.
4. Gates: G1 zero-chunk state-entries MUST go PASS on Intake (0 zero-chunks);
   G2/G3/G4 unchanged PASS; cache-0 ≤1/call; SDK --trace both traces →
   research/surgeon/iter88-intake-refer-drill/; APPEND forensics_calls rows
   (call_kind llm_mic_harness, commit sha of the iter88 tip, e2e/uperm/eager/cache0).
5. Cancel every test booking created (recipe above; verify 0 upcoming).
Verification: G1 PASS + suite 7-stale + ledger rows queryable + bookings clean.
Unblocks: T4.
### T4 — report + HITL close (30 min)
1. Write /home/julio/projects/clean_diallux_SDR/research/surgeon/iter88-intake-refer-drill/01_verdict.md
   (verdict vs PT-74 intent: G1 flip, retrieval quality on Intake, any latency delta).
2. Update plan_v5_iter81_master_ladder.md STATUS (report folder, branch state, ledger
   rows, next step); commit docs to main (this plan + ladder + PENDING_TASKS close);
   re-sync Finland mirror; kill lanes + ss verify.
3. HITL: owner ear + merge call on BOTH branches (iter87 02eb2ac + iter88 tip).
Verification: STATUS updated; docs pushed; mirror synced; ports free.

## Validation Plan (end-to-end)
T0 GO → T2 drill table → T3 prompt edit (ONE line) → suite 7-stale-only → battery:
G1 Intake zero-chunk = 0 → G2/G3/G4 hold → forensics_calls rows → bookings 0 upcoming →
STATUS update. Abort/rollback: the fix is ONE prompt line — revert the file (git
checkout the file in the worktree); lane re-boot unchanged; no config touched.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| FIND-9 sub-causes (1) scope dilution / (2) multi-intent single-vector / (3) no per-KB quota | structural redesigns; owner decides AFTER this plan's evidence |
| ConfirmSlots/contact_details empty-query zero-hits (FIND-4 family) | separate pattern; not the G1-Intake fix |
| S2L spike family (hysteretic window trim re-bill) | next latency surface; own analysis session |
| happy turn-1 lite 1,957 ms single sample | drill in T3; separate surface if real |
| iter87 merge + WARM_AWAIT_DEST_MS default promotion | owner calls, independent of this plan |
