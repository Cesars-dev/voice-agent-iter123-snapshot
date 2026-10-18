# plan_v5_iter102b_wave_master_plan_authoring — THE wave master plan (per-iteration plans authored + indexed)

## Meta
- Date: 2026-10-10 (the iter102b master-plan authoring session — the session the roadmap's ledger line named: "next = iter102b master-plan authoring (code-heavy-ness analysis -> 02_edit_specs -> THE wave master plan per iter81 style)")
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE master file for the whole iter102 fix wave. Every iteration has its OWN detailed plan file in `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/` (code-analyzed, edit-spec'd, pinned, gated). This file carries: the plan INDEX, the shared laws, the branch chain, the run order, the session-close invariants. It supersedes nothing — it organizes `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102_wave_roadmap.md` (the PT-0 eval session plan, EXECUTED) and consumes `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/01_wave_eval.md` (the owner-ratified eval + branching directives).
- Style: the iter81 master-ladder pattern (`/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md`) — one living file, STATUS at top, session log at bottom.
- Status: PLAN ONLY — the wave awaits owner GO per branch (LAW 0). Zero wave code has been cut. All line references in the per-iteration plans were verified 2026-10-10 against `origin/main` @ `10aebad` (engine content = `3daf11c`).
- Landing note (2026-10-10): this file ABSORBS the original authoring session plan (T1/T2/T3 — recoverable in git history; that session EXECUTED: the 11 per-iteration plans + edit-spec closures below, and `lf.py pair` cherry-picked to main by owner order). Two artifacts landed today: the SDK (cherry-pick commit) and the docs (this file + folder + pointer edits).
- Landing note II (2026-10-10, later): WORKFLOW LAW amended into Resolved Decisions (one iter number per branch / fixes = more commits on the SAME number until proven / data-driven fixes, no guessing / owner-instructed cadence / this file updated at every session close). Numbering re-bound: the wave keeps `iter102` (docs phase; docs fix-commits = `102c`, `102d`, …); the FIRST code branch = **iter103**; subsequent designed branches take the next number at launch (iter104 = PT-1, iter105 = PT-2, iter106 = PT-10, iter107 = PT-9). The old reserved-slot list is VOID as numbers; the per-iteration files' suggested branch names are PROVISIONAL.

## STATUS — read this first (update at EVERY session close)
- NOTHING EXECUTED yet. Next action on owner GO: **iter103** — cut `engine/103-wave-stack` from the CURRENT main (docs drift landed main @ `d8cacdf`; engine bytes unchanged since `3daf11c`) and run its five commits in order (PT-11 trace FIRST, zero-code; then PT-8 → PT-5 → PT-6 → PT-4 → PT-11-wire).
- **THE WORKFLOW (owner 2026-10-10, amended):** one iter number per branch → edit → test → analyze DATA → fix with data (MORE COMMITS ON THE SAME NUMBER, never a new one) → re-test → **STOP AT A CHECKPOINT** when proven → next branch (iter104 = PT-1) on the owner's instruction. Cadence per session = owner-instructed (default 1; owner may say 2/N). NO GUESSING. This master plan is the design — updated at EVERY session close.
- **FINLAND-ONLY (owner 2026-10-10):** this wave touches NO OREGON box — no ssh, no OR lanes, no OR dials. Branch cut + lane open = `scripts/new_lane.sh` run locally on FI (verified box-agnostic); tests = FI-local suite + FI-local lanes. OR wakes only on owner order (latency era / real dials). (This commit = **iter102d**.)
- The 97 dial + merge remains the standing owner BLOCKED (either path lets the wave proceed — cut base = current main `3daf11c` per owner directive 10, 2026-10-10).
- PT-10 remains BLOCKED on the owner's design dictation. PT-3 remains PARKED (decided after PT-1+PT-2+one real call). PT-7 FOLDED. PT-9 LAST, from the 98 tip.
- Session log: see bottom. This session = authoring only (this file + the 11 per-iteration files + the roadmap pointer edit; docs lane).

## Compaction Context (what a fresh agent must know)

**The project:** Dialux SDR v5 voice engine (Twilio media WS → Deepgram flux STT → LangGraph graph → gpt-5.4 → SentenceGate → ElevenLabs), repo `/home/julio/projects/clean_diallux_SDR`. Boxes: **FINLAND** (Helsinki `46.62.233.228`, user julio) does EVERYTHING — lanes, branch cuts, develop, test; NO ssh to anywhere during the wave (owner: no SSH mess, it drags). **OREGON = LATENCY-ONLY, DORMANT** (owner 2026-10-10: the wave only checks that the edits WORK — latency and real-call stuff belongs to a later owner-ordered era, likely OR). Origin (GitHub) pushes from FI remain the sync + backup mechanism.

**The wave's evidence base:** two REAL calls on the OR :8050 test-merge (`06bdd97`) — Oct-6 `CA93823104f61c20d6` (trace `152d98c0c8d73f27680d950f2914e1bb`): the "worked okay-ish, 1,882 ms p50" call, self-answering continuation rounds + fast-number complaint ON TAPE; Oct-8 `CAcf047fe3fd9075` (trace `be7bb8e7404b76d2c0b50ddc9636e4d2`): 140-char mid-clause cuts ×11 (FIND-38), user-echo inserts (FIND-37), canned RAG re-fires (FIND-35). Transcripts regenerable via `engine/scripts/lf.py gens <trace_id>`.

**What the 2026-10-10 roadmap session already did (committed to main through `10aebad`):** the per-PT eval (`research/surgeon/iter102-fix-wave/01_wave_eval.md`), the tier + branch-structure decisions (owner), the backlog renumber (`plans/PENDING_TASKS.md` LIVE BACKLOG PT-1..PT-11). **This session** authored the per-iteration plans (the folder below) — including the two edit-spec closures the eval deferred to "the 02 file" (PT-5's normalize rule + dict init; PT-8's field names + source stamps — both closed inside their plan files, NOT a separate 02 file).

**Repo law (short form):** LAW 0 — code = branch `engine/iterNN-<slug>` per approved plan → suite → battery → report → ASK Julio → merge `--no-ff` → tag → `scripts/git-tree.sh` → ITERATIONS line. Docs = straight to main. Prompt-layer (prompts/*.md, KBs, llm.json) = CODE, full LAW 0. LANE LAW (`scripts/new_lane.sh`), SWITCH LAW (ENV-SWITCHES register; code default = tested value), MODEL LAW (gpt-5.4 everywhere), VOICE LAW (EL default). Read `/home/julio/projects/clean_diallux_SDR/AGENTS.md` before touching anything.

## THE PLAN INDEX (every MD plan this wave has — read the master, work the child)

| # | Iteration (one line) | Plan file (absolute path) | Vehicle | Run position |
|---|---|---|---|---|
| PT-8 | Pre-LLM gap stopwatch — per-round `pre_llm_ms` breakdown, observability-only | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` | THE STACK BRANCH, commit 1 | FIRST (owner run order) |
| PT-5 | RAG query memo — byte-identical per-call query-set cache, no sqlite | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-5_rag_query_memo.md` | THE STACK BRANCH, commit 2 | 2nd |
| PT-6 | Numeral expansion before TTS — $ / dates / times, owner-worded | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-6_numeral_expansion.md` | THE STACK BRANCH, commit 3 | 3rd |
| PT-4 | Gate cap 500 — "a cap, not a rule"; `_FLUSH_LEN` → `Settings.gate_flush_len` | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-4_gate_cap_500.md` | THE STACK BRANCH, commit 4 | 4th |
| PT-11 | Caller number must reach the engine — trace first, then the 1-2-line wire | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-11_caller_number_wire.md` | THE STACK BRANCH, commit 5 (trace = zero-code, top of session) | LAST in the stack |
| PT-1 | Echo inserts (FIND-37, P0) — one user entry per utterance, replace semantics | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-1_echo_inserts.md` | OWN branch `engine/102-echo-accounting` (reserved; number ratifies at cut) off the STACK TIP | after the stack is green; PT-3's fate decided at its ASK |
| PT-2 | Ask-chop — the owner's 3 rules in code (chop / continuation-silence / spoken-only history) | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-2_ask_chop.md` | OWN branch `engine/103-turn-segregation` (reserved) off PT-1's tip | after PT-1 verifies |
| PT-10 | dv-failure-gated recovery tool on VerifyLead — CLOSED by default, code-gated | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-10_dv_recovery_tool.md` | OWN branch (post-dictation) after PT-11's wire | BLOCKED on the owner dictation |
| PT-9 | SPEAK-FIRST split-round — speak stream (`LITE_NOOP_TOOL` alone) ∥ tools stream | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-9_speak_first_split_round.md` | `engine/100-split-round` from the `engine/98-service-tier` tip | LAST (owner) |
| PT-3 | Transition beat — carry the next question in the ack | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-3_transition_beat_PARKED.md` | — | PARKED (re-decide after PT-1+PT-2+one real call) |
| PT-7 | Intake refer-tag shape — keep/shorten the WHAT anchors | `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-7_intake_refer_tag_FOLDED.md` | — | FOLDED (PT-5's memo kills the cost; anchor tune = prompt ride on say-so) |

Companion documents (not plans, but part of the wave's paper): the roadmap session plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102_wave_roadmap.md` (EXECUTED), the earlier wave plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102_fix_wave_and_pt_deepdive.md` (superseded in structure by the owner's stack/chain directives — its per-FIND analyses remain valid evidence), the eval `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/01_wave_eval.md`, the deepdive `…/00_pt_deepdive.md`, the PT-9 spec `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design.md` (amended).

## Resolved Decisions (owner, verbatim-intent — DO NOT revisit)
| Decision | Rationale / source |
|---|---|
| **THE BRANCH CHAIN:** stack branch (PT-8/5/6/4/11, ONE branch, per-PT clean commits, owner run order) → PT-1 branch off the stack tip → PT-2 branch off PT-1's tip → PT-10 own branch (post-dictation) → PT-9 LAST from the 98 tip. NEVER branch from main mid-chain. Every link TESTED (suite baseline + own pins) before the next cut. Serial merge-back at the END — merge back, merge back, merge back — each merge = LAW 0 owner say-so. NO squash (per-PT commits stay readable as one unit) | Owner branching directives 2026-10-10 (recorded in `01_wave_eval.md` §Owner branching directives) |
| Cut base of the chain's first branch = the CURRENT main at cut time (= `d8cacdf` as of 2026-10-10 — docs drift only; engine bytes unchanged since `3daf11c`, so the per-iteration files' `3daf11c` refs remain valid) | Owner directive 10 (the 97 dial/merge stays a separate standing decision) + the docs landing |
| PT-1 FIRST in the heavier group; PT-3's fate decided after PT-1 verifies (the transition write must not collide with PT-2's chop) | Owner directive 7 |
| PT-7 = folded ("if it's not worth its own branch, it's not a task") | Owner directive 8 |
| PT-9 = cut from `engine/98-service-tier` tip per the amended spec; explained to owner | Owner directive 9 |
| PT-2's three rules live in CODE, never prompts (never-silent via the PT-68/iter94 ladder; never stack questions; spoken-only history with the model told what was chopped) | Owner 2026-10-09, on record |
| PT-4 = "a cap, not a rule" — sentence boundaries flush; 500 = runaway valve only | Owner verdict on FIND-38 |
| PT-5 = byte-identical reuse, per-call dict, NO sqlite | Owner brainstorm ratified 2026-09/10 |
| PT-9 speak stream binds `LITE_NOOP_TOOL` ALONE; tool_calls discarded at the gather; executor swallows `memory_note` | Owner addendum 2026-10-09 (spec-amended) |
| **WORKFLOW LAW (owner 2026-10-10 — ONE NUMBER PER BRANCH):** ONE iter number per branch — the branch IS the iteration. Fixes during a branch = MORE COMMITS ON THE SAME NUMBER (never a new one) until the code is PROVEN (suite + pins + its data gate); the suffix system covers the era's non-engine artifacts (`iter<NN>b/…`, `iter<NN>c/…`). The wave identifier stays `iter102` (docs/plan phase — tolerated retroactively; docs fix-commits = `102c`, `102d`, …). The FIRST code branch = **`engine/103-<slug>`**; numbers advance strictly in LAUNCH ORDER at each branch's cut: `104` = PT-1, `105` = PT-2, `106` = PT-10, `107` = PT-9. The per-iteration plan files' suggested branch names are PROVISIONAL; the old reserved-slot list (100-split-round, 102-echo, 103-turn-segregation, 104-gate, 105-rag, 106-numerals, 108-stopwatch, 110-wire) is VOID as numbers | Owner: "we stay on the iter number that we're working on until that code is proven to work. Then we launch the next iteration — 103"; "I don't want a new iter name unless we touch code"; "if we have to fix and re-commit, it's gonna be 102C or whatever" |
| **DATA LAW (owner 2026-10-10 — NO GUESSING):** edit → test → analyze DATA → fix with data → re-test — as many cycles as needed, same branch, same number. Every fix carries evidence (ledger row / gate number / pin). A goal not achieved = the loop repeats; nothing is "close enough". | Owner: "we edit, we analyze data, and we fix with data. We don't guess." |
| **CADENCE LAW (owner 2026-10-10):** default ONE branch-iteration per session; the owner instructs the count ("do 1", "do 2", "do 6" — whatever he says). STOP AT A CHECKPOINT after every branch. Each session close = update THIS master plan (it is the design). | Owner: "one per session or maybe two per session, depending on whether I give you the instruction"; "every time we check out a session, we basically edit the master plan, which is the design" |
| **FINLAND-ONLY LAW (owner 2026-10-10 — NO OREGON):** every wave operation runs LOCALLY on FI — no ssh to OR at all during the wave. Branch cut + lane open = ONE command: `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <NN> <base> <slug>` (box-agnostic — verified 2026-10-10: no ssh inside, `REPO=/home/julio/projects/clean_diallux_SDR`, worktree at `/tmp/opencode/wt-<NN>`, symlinks the FI canonical venv, generates `.env` from the FI canonical, audit-gates it; `--list` = inventory). Suite/tests on FI worktrees; scripted mic/browser batteries on FI LOCAL lanes. No OR lanes/batteries/dials — OREGON wakes ONLY on owner order (latency era / real Twilio dials). Any OR reference inside the per-iteration plan files (ports, lanes, the OR-dial phases) defers to this law — substitute the FI-local equivalent, and the REAL-dial phases stay owner-gated. | Owner: "we don't work in Oregon at all. We do everything in Finland... we avoid any SSH mess"; "Oregon box is for latency purposes... we're only checking the edits work... we can do that here"; "we're gonna use the bash script that exists in Finland for every new branch" |
| Order is code-safe as listed (dependency check done at the eval): the stack's five PTs are mutually independent; real edges = PT-11→PT-10, PT-1→PT-2, PT-2→PT-3-decision; watch-points = PT-2 writes against PT-4's new flush (chain supplies it), PT-9 reconciles the round loop it shares with PT-2 (PT-9 last, off the 98 tip) | `01_wave_eval.md` §Dependency check |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO: cut the stack branch + run order | this file (the ASK) |
| The 97 dial + merge sequencing (either path lets the wave proceed) | `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_98_validation_merge.md` T1-T7 |
| PT-6 owner wording pick ($ / date / time styles) | ear pick at the stack session or verification |
| PT-10 design dictation (state name / trigger list / action set / flag lifetime) | HITL (the PT-10 plan's 4-question agenda) |
| PT-2 "decisive tool data" list + delta-note wording | HITL at the PT-2 design checkpoint (T0 of its plan) |
| Canonical `engine/.env` `AUDIO_TRANSPORT=twilio` ratification | owner edits (agents never edit canonicals) — needed before REAL dials only |
| PT-11 phase-A needs ONE real Twilio call on the lane | owner dials after the stack's early commits are lane-booted |

## Environment & Dependencies (shared — each child plan inherits)
- venv (canonical, symlinked into every lane): `/home/julio/projects/clean_diallux_SDR/engine/.venv` (python 3.12; pip via `-m pip` only — the pip-script shebang trap).
- Suite gate (every branch, every commit): `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1` — measure the baseline at cut; red set byte-identical, growing ONLY by the branch's own pins (post-97-merge expectation `5 failed, 517 passed, 1 skipped`; the 98 base expects `526/1/5` for PT-9).
- Lane opener (LOCALLY on FI — no ssh): `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <NN> <base> <slug>` (exit 0 = lane READY, exit 1 = DOA — fix env first); `--list` = inventory. FI-local lane ports = next free (:8071+ shape); never-touch list unchanged (:8000-8003, :8020/21, :8024, :8025, :8026, :8049/50, :8063-:8070).
- OREGON (DORMANT — owner 2026-10-10): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — ONLY on owner order (latency era / real Twilio dials). The wave runs on FI = this box.
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db` (runs/calls/rounds/rag/findings; read via `.venv/bin/python -c "import sqlite3; …"` — no sqlite3 CLI). Import: `scripts/live_sql.py import --window "HH:MM-HH:MM" --run <name> --commit <sha>`.
- Echo accounting SDK: `lf.py pair` — **ON MAIN** (cherry-picked 2026-10-10 by owner order from `engine/iter97-research-adaptation` @ `c877e51`; zero-conflict — main's `lf.py` was byte-identical to the commit's parent `37260fd`).
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/` (00 deepdive, 01 eval, 03 = PT-11 trace (to come), 04 = PT-10 dictation (to come)).
- Cal.com event 3801235 is REAL — cancel EVERY test booking after any battery.

## Architecture (the branch chain — one diagram, the law)
```
main d8cacdf (docs landing; engine bytes unchanged since 3daf11c)
  └─ engine/103-wave-stack    (iter103; ONE branch, FIVE clean commits + the PT-11 trace at session top)
        ① PT-8  gap stopwatch      (observability-only)
        ② PT-5  rag query memo     (byte-identical per-call cache)
        ③ PT-6  numeral expansion  ($ / dates / times, owner-worded)
        ④ PT-4  gate cap 500       (Settings.gate_flush_len, boundary flush)
        ⑤ PT-11 caller-number wire (trace → the 1-2-line fix)
         [suite gate: baseline + every PT's pins green]
         ├─ engine/104-echo-accounting      (iter104, PT-1: replace semantics, one user entry/utterance)
         │     [suite gate; ASK — PT-3's fate decided HERE]
         │     └─ engine/105-turn-segregation  (iter105, PT-2: the 3 rules in code)
         │           [suite gate; battery; ASK]
         └─ engine/106-dv-recovery (iter106, PT-10 own branch, post-dictation, after ⑤'s wire — base = owner's call at dictation)
  └─ engine/98-service-tier tip ── engine/107-split-round (iter107, PT-9: LAST, independent of the chain — the "100-split-round" name was pre-law)
  MERGE-BACK: only at the END, serial, each merge = LAW 0 owner say-so, --no-ff, tag engine/iterNN, git-tree.sh, ITERATIONS line.
  ANY gate failure inside a branch = more commits on THAT branch's number, data-driven, until proven (WORKFLOW LAW).
```

## File Map (this session's outputs — docs lane, straight to main)
| File (absolute path) | What | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md` | THIS file — the wave master plan | NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-1_echo_inserts.md` … `plan_wave_PT-11_caller_number_wire.md` | the 11 per-iteration plans (index above) | NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102_wave_roadmap.md` | pointer block added: this master plan + the folder own the wave from here | EDIT (one block) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | LIVE BACKLOG rows gain their plan-file pointers at the commit session (docs → main) | EDIT (at commit time) |

## Deploy Rules (shared by every child plan)
- Every branch: cut LOCALLY on FI — `scripts/new_lane.sh` (LANE LAW, FI-local; one command, audited) → develop/test in the FI worktree (FI canonical venv symlinked) → suite gate (baseline byte-identical + own pins) → scripted mic/browser battery on a FI LOCAL lane when the child plan calls for one (the child plans' OR-lane/OR-dial entries are DEFERRED under the FINLAND-ONLY LAW — only the FI-local gates are mandatory while OREGON is dormant) → report under `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/` (or the PT's own surgeon folder) → ledger import per SOP → **ASK JULIO** → on say-so: serial merge-back at chain end (`--no-ff`, tag `engine/iterNN`, `scripts/git-tree.sh`, ITERATIONS line). `scripts/keyhound` before EVERY push (pushes to origin remain the backup/sync lane — that is not "working in Oregon").
- Merge-backs happen ONLY at the end of the chain, serially, owner say-so each (the chain law).
- CHANGE POLICY: agents NEVER edit canonical `.env`s; new knobs carry code defaults matching the tested value (SWITCH LAW rule 4) + ENV-SWITCHES registration.
- What is NEVER touched: the hot-zone branches (`engine/iter65-*`, `engine/iter68-*`, `engine/iter70-*`), the OR protected checkout `engine/iter73-oregon-wip-20260924` (prod endpoints config — branch-guarded), FI prod `/opt/diallux-production`, live agents `agent_16985b5d087e56c35141983396` / `agent_87e4d5f08475e5bc558b2f390f`, FI services :8001-8003, FI's dirty worktrees (owner: stay as-is, no harm).
- After every battery: cancel ALL test bookings (Cal.com 3801235 REAL).

## Tasks (the wave's run order — each task = "open the child plan, execute it, gate it, ASK"; CADENCE LAW: one branch-iteration per session unless the owner instructs more)
### W1 — iter103: cut `engine/103-wave-stack` off current main + its five commits (PT-11 trace FIRST → PT-8 → PT-5 → PT-6 → PT-4 → PT-11-wire)
- On owner GO. PT-11's phase-A trace runs at the TOP of this session (zero-code, needs the lane + one owner dial); its phase-B wire is the stack's last commit. Gate: suite baseline + all five PTs' pins green + the PT-11 real-call dvs check.
- ANY gate failure here = more commits on iter103 (same number, data-driven) until proven — then CHECKPOINT (ASK). Next session = iter104 (W2).
- Child plans: PT-8 / PT-5 / PT-6 / PT-4 / PT-11 files.
### W2 — iter104: PT-1 branch off the stack tip
- Gate: suite + 6 pins + echo replay (3 shapes → 0 inserts). The ASK carries the PT-3 fate question.
- Child plan: PT-1 file.
### W3 — iter105: PT-2 branch off PT-1's tip
- T0 HITL (decisive-tool list + note wording) → build → gate: suite + 10 pins + the Oct-6 window replays + a scripted battery on the OR lane.
- Child plan: PT-2 file.
### W4 — iter106: PT-10 (whenever the dictation lands; after PT-11's wire)
- Child plan: PT-10 file (T0 = the dictation).
### W5 — iter107: PT-9 from the 98 tip (LAST)
- Child plan: PT-9 file (the spec is the design; the plan is the wrapper).
### W6 — Serial merge-back + close-out
- Merge each chain link in order (owner say-so each): iter103 stack → iter104 → iter105 → (iter106) → (iter107 independently); tags `engine/iter103..107`, git-tree, ITERATIONS lines, commit-registry refresh ritual (backup `ledger.db` first, run from the MAIN checkout's engine dir), PENDING_TASKS row statuses, keyhound, this file's STATUS + session log updated.

## Validation Plan (chain-level, end-to-end)
1. Every branch's own gates (per child plan) green before the next link cuts — the chain never advances on a red link.
2. Cross-branch pins hold at each cut: PT-2's pins run on a tree that contains PT-4's flush + PT-1's history semantics (chain supplies the watch-point dependencies by construction).
3. One REAL call after the chain merges (owner dial, per the endpoint map) re-verifies live: zero echo inserts, zero mid-clause cuts, canned RAG fires memoized, numerals worded, `callback_number` populated — the five FIND diseases, dead on tape.
4. No prompt/KB file changes anywhere in the chain except the PT-10 dictated surface (if the dictation requires it) — everything else is engine code + docs.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| The 97 dial + merge + canonical env ratification | owner standing decisions (BLOCKED table) |
| Deepgram EOT knob tuning (FIND-39 micro-turn plunge) | owner-deferred biggest latency lever — NOT a wave PT |
| ~~`lf.py pair` SDK merge to main~~ | **DONE 2026-10-10** (cherry-picked to main @ `a842dce`, owner order) |
| Fast-tier pricing truth | owner/OpenAI page |
| Heating items | other agent's lane |
| GK stress battery | end-of-queue after the owner blesses a lane |

## Session Log (append ONE row per session, newest at TOP)
| Date | Task touched | Outcome | Evidence | Next |
|---|---|---|---|---|
| 2026-10-10 (even later) | FINLAND-ONLY LAW amendment (this commit = **iter102d**) | Compaction/Resolved/Environment/Deploy Rules/STATUS rewritten to FI-only: no ssh to OR during the wave; lane open = `scripts/new_lane.sh` run LOCALLY on FI (box-agnostic, VERIFIED: no ssh, same REPO path, /tmp/opencode worktrees, FI canonical venv+env, audit gate); OR = latency-only dormant (wake = owner order); child plans' OR refs defer to the law; chain law re-confirmed on the plan (BRANCH CHAIN row + Architecture diagram + W6: branch-off-branch from each tip, serial merge-back at the end, no squash — per-PT clean commits read as one unit per PT) | this file | Owner GO → **iter103** = W1 (FI-local cut; PT-11 trace curl-diff part runs FI-local; its real-dial phase stays owner-gated) |
| 2026-10-10 (later) | WORKFLOW LAW amendment (this commit = **iter102c** per the new law) | Three laws added to Resolved Decisions (WORKFLOW: one number per branch, fixes stay on the number until proven; DATA: no guessing; CADENCE: owner-instructed, checkpoint per branch, master plan updated every close) + STATUS/Architecture/Tasks re-bound to iter103..107; old reserved slots void as numbers; Deferred: pair row closed (DONE on main) | this file | Owner GO → **iter103** = W1 stack cut (PT-11 trace first) |
| 2026-10-10 | iter102b authoring + landing session (zero wave code, zero cuts) | Master plan + 11 per-iteration plans authored (code analysis vs origin/main `10aebad`/engine `3daf11c`; edit-specs closed for PT-5 + PT-8; PT-11 root-cause hypothesis identified: `/twiml` reads `From` from query params while Twilio POSTs it form-encoded — trace to confirm); `lf.py pair` SDK cherry-picked to main (owner order, zero-conflict); docs landed via the docs worktree (this file + folder + roadmap/NEXT_STEPS/PENDING_TASKS/ITERATIONS pointers); the FI checkout's twin-sim-proven dust cleaned — no dirty state left | this file + `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/` (11 files) + the cherry-pick commit | Owner GO → W1: cut the stack branch, run PT-8 → PT-5 → PT-6 → PT-4 → PT-11 |
