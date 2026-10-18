# iter102 wave roadmap — per-PT eval (branches/commits/size/risk) + tiered apply (quick wins first)

## Meta
- Date: 2026-10-10 (EOD of the 2026-10-09 PT-triage session; executes as its OWN session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE session = PENDING_TASKS **PT-0**: (a) produce the per-PT eval table (branches, expected commits, files, pins, risk tier, data gate, owner-review columns) for the live backlog PT-1..PT-11; (b) propose + confirm the tier ordering (owner: "quick wins first, then heavier"); (c) on owner GO, cut the tier-1 quick-win branches and run them to the pre-merge ASK. Heavier tiers queue behind the owner's manual review.
- Status: PLAN ONLY (awaits owner GO)
- **EXECUTED + SUPERSEDED as the wave's operating doc (2026-10-10, iter102b session):** the eval (T1/T2) ran and the owner ratified the branch structure — see `research/surgeon/iter102-fix-wave/01_wave_eval.md`. From 2026-10-10 the wave lives in the master plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md` with ONE detailed plan file per iteration in `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/` (PT-1, PT-2, PT-4, PT-5, PT-6, PT-8, PT-9, PT-10, PT-11 + PT-3 PARKED + PT-7 FOLDED). Read the master plan first; this roadmap remains as the PT-0 session record.

## Compaction Context (verbatim session state as of 2026-10-09 EOD)

### What happened in the 2026-10-09 session (all committed to main through `a32a928`)
- The backlog `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` was reconciled, consolidated, renumbered per owner: **LIVE BACKLOG** section = PT-0 (this roadmap session) + PT-1..PT-9 (the wave, full-detail rows with code line refs) + PT-10/PT-11 (owner additions). Every old PT-NN row lives verbatim in the file's ARCHIVE section (traceable to old reports/commits). `/home/julio/projects/clean_diallux_SDR/AGENTS.md` NEXT-UP block points agents at the live backlog; `/home/julio/projects/clean_diallux_SDR/plans/NEXT_STEPS.md` carries the pinned pointer.
- Owner's corrections landed on record: prompts = SUGGESTIONS, never hard gates; hard gates = code in `engine/diallux/`. Iter68 code = trap, never cherry-picked (PT-3 transition beat and the old "chain-link yield" stay parked; PT-2 below re-owns the purpose cleanly).
- Owner added two new items: PT-10 (dv-failure-gated recovery tool on the Verify Data state — boolean CLOSED by default, code-gated) and PT-11 (caller's number must reach the engine — last real calls never delivered it).
- Analysis-only work produced (zero code changes all session): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/00_pt_deepdive.md` (PT verdict tables + FIND anatomy + the PT-2 stacking analysis §D).
- The found plan: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design.md` — AMENDED with the owner addendum (speak call binds `LITE_NOOP_TOOL` ALONE, never bare `tools=[]`; speak-stream tool_calls discarded at the gather merge; executor swallows `memory_note` at `engine/diallux/graph/tools.py:304`). Design READY, build pending.
- Boxes synced: origin/main = `a32a928` = FI (`/tmp/opencode/wt-main-docs-fi`) = OR (`/tmp/opencode/wt-main-docs`, clean fast-forward). OR prod checkout untouched (protected branch). FI's dirt (doc drafts, wt-audit probe patch, parked-worktree artifacts) = owner-ruled "stay dirty, no harm", DO NOT clean anything.

### The wave it evaluates (as ratified by the owner 2026-10-09)
- PT-1 echo inserts (P0) · PT-2 ask-chop (+continuation-silence + spoken-only history, in code) · PT-3 transition beat (PARKED) · PT-4 gate cap 500 ("a cap, not a rule") · PT-5 RAG query memo (byte-identical skip, no sqlite) · PT-6 numerals · PT-7 Intake refer-tag shape (under evaluation — may fold) · PT-8 pre-LLM gap stopwatch (approved, observability) · PT-9 SPEAK-FIRST split-round (big lever, spec ready) · PT-10 dv-gated recovery tool · PT-11 caller-number pass-through.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| The session applies in TIERS: safe quick wins first, heavier later | Owner 2026-10-09: "I am going to review everything manually. Probably would do first the safe quick wins, and then we go heavier on everything." |
| ONE branch per PT, smallest change, prompt-first/env-knob-first — NO grabbing fixes from parked/hot-zone branches, NO cherry-picks from iter60-78 era | Owner post-mortem law (old PT-73, standing) + the iter68 trap evidence (527-line entangled iter68 delta) |
| Every merge = LAW 0 owner say-so; every code change = branch `engine/iterNN-<slug>` → suite → pin → battery → ASK | `/home/julio/projects/clean_diallux_SDR/AGENTS.md` hard rules; no exceptions |
| No new iter numbers for anything outside `engine/diallux/` | Owner's zero-code rule ("no fucking iters that dont touch code") |
| PT-2's three rules live in CODE, not prompts: (1) never stay silent (chop removes only the post-question tail; the PT-68/iter94 ladder covers caller silence); (2) never stack questions in one turn; (3) the model's history always equals what was SPOKEN (chopped text never enters history) | Owner 2026-10-09 (replaces the earlier rejected idea; the "transition round stays silent" idea is dead) |
| PT-4 = flush at natural sentence boundaries; `_FLUSH_LEN` hard cap 500 chars only as a runaway valve ("a cap, not a rule") | Owner verdict — the model decides its output; FIND-38's 11 mid-clause cuts at exactly char 140 were the disease |
| PT-5 = per-call dict `{normalized query → results}` on the graph agent; BYTE-IDENTICAL query hits reuse; no sqlite; pin = seeded special case | Owner brainstorm ratified: "a chunk retrieved (byte identical or chunk identical) should not be retrieved again" |
| PT-9 speak stream binds `LITE_NOOP_TOOL` ALONE (owner's silent-tool design), tools stream carries the full real array | Owner question answered by code verification (`llm.py:84`, `builder.py:2207/569-571`, `tools.py:304`); the spec addendum records it |
| OR = official dialing place; FI = develop/test | Workspace AGENTS.md + the validation plan's endpoint map |

## BLOCKED / NEEDS INPUT (owner decides at session GO)
| Item | Where to get it |
|---|---|
| Cut base: does the wave cut from CURRENT main (`a32a928`) or wait for the 97 dial + merge (`/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_98_validation_merge.md` T1-T7 preconditions, still pending owner dial) — the original fix-wave plan assumed post-97-merge base | Owner says so; both options are valid for tier 1 (the tier-1 hunks touch disjoint files from 97's) |
| Canonical `/home/julio/projects/clean_diallux_SDR/engine/.env` line 37 `AUDIO_TRANSPORT=twilio` ratification | Owner edits (agents NEVER edit canonicals) — needed before any REAL dial; unit-level work is not blocked |
| Tier markings: owner reviews the T1 eval table and confirms/edits the tiers | `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/01_wave_eval.md` |
| PT-6 numeral wording (e.g. "$1,250" → "twelve fifty dollars" vs "one thousand two hundred fifty") | Owner ear pick during verification, not before |
| PT-10 design dictation: exact state name ("Verify Data" = `ConfirmSlots`?), the dv-failure boolean's trigger list, the recovery action set (candidate: caller-ID fallback riding PT-11's wire) | HITL with owner at session (same pattern as the iter87 prewarm-design dictation) |
| Live-call double-check of the wave (the two Oct-6/8 transcripts cannot be regenerated; pins REPLAY their shapes at unit level) | Owner dial on the lane after merges, per the validation endpoint map |

## Environment & Dependencies
- venv (canonical, FI): `/home/julio/projects/clean_diallux_SDR/engine/.venv` (python 3.12; pip via `-m pip` only).
- Suite: `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1` — record TODAY's red set as the baseline (post-97-merge it is expected `5 failed, 517 passed, 1 skipped`; if the 97 merge has NOT landed, the count is whatever main carries — the gate = byte-identical to the baseline you measured, growing ONLY by each PT's own pins).
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db` (rag rows carry the PT-5/PT-7 evidence; read via `.venv/bin/python -c "import sqlite3; ..."` — no sqlite3 CLI on the box).
- Tracking SDK v2: `lf.py pair` + `costs` live ONLY on session branch `engine/iter97-research-adaptation` @ `c877e51` (commit, clean, UNMERGED; main lacks both subcommands — verified 2026-10-09). Merge/cherry-pick to main = owner say-so; the wave's echo gates literally run on `pair`.
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/`.
- Lane opener (on OR): `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <NN> <base> <slug>`; provisional ports 102→:8071, 103→:8072, 104→:8073, 105→:8074, 106→:8075 (never-touch list unchanged: :8000-8003, :8020/21, :8024, :8025, :8026, :8049/50, :8063/65/66/67/68/69, :8070). PT-9's own lane = OR :8068 per the 100_design §8 (FI dry-run :8083).
- OR box: `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`. FI = this box.
- Evidence inputs: the two real-call transcripts regenerate anytime via `engine/scripts/lf.py gens 152d98c0c8d73f27680d950f2914e1bb` / `gens be7bb8e7404b76d2c0b50ddc9636e4d2`; current copies at `/tmp/opencode/oct6_transcript.txt`, `/tmp/opencode/call_cf047_transcript.txt`.

## Architecture
```
main (a32a928 — or post-97-merge main if owner chooses to wait)
   |- engine/104-gate-cap-500        (PT-4, TIER 1 QUICK WIN)
   |- engine/105-rag-query-memo      (PT-5, TIER 1 QUICK WIN)
   |- engine/108-gap-stopwatch       (PT-8, TIER 1, observability-only)  [numbers at cut time, next free = 107+]
   |- engine/102-echo-accounting     (PT-1, TIER 2)
   |- engine/110-caller-number-wire  (PT-11, TIER 2: zero-code trace -> one-arg wire)
   |- engine/2-ask-chop              (PT-2, TIER 3 HEAVY)
   |- engine/100-split-round         (PT-9, TIER 3 HEAVY — cut from engine/98-service-tier tip per the amended 100_design)
   |- engine/NN-dv-recovery-tool     (PT-10, TIER 3, after the owner's design dictation)
   PT-3 = parked (not cut). PT-6 = plan-approved, tier = owner's call (tiny; likely TIER 1-2). PT-7 = fold-or-drop decision inside the eval.
   Serial merges per LAW 0: branch -> suite -> pin -> battery -> ASK -> merge --no-ff -> tag engine/iterNN -> scripts/git-tree.sh -> ITERATIONS line.
```

## File Map (THIS session's outputs)
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/01_wave_eval.md` | T1 deliverable: the per-PT eval table (11 rows) + tiering + owner-review marks | NEW (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-0 status → evaluated/executing per owner marks; PT rows gain their tier tags only if the owner edits them | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/plans/NEXT_STEPS.md` | queue refresh to the roadmap state (PT-0 flowing; next = tier-1 apply or the PT-9 build) | EDIT (docs → main) |
| Tier-1 branches' engine files (ON GO only): `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` (PT-4), `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (PT-5 fire sites + PT-8 report) | the smallest change each | EDIT (branches) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` (PT-4 Settings promotion per SWITCH LAW rule 4) | `_FLUSH_LEN` constant → `gate_flush_len` field default 500 | EDIT (branch) |
| `engine/tests/test_iter104_gate_cap.py` … one pin file per tier-1 branch (names at cut time) | replay pins | NEW (branches) |

## Deploy Rules
- Every tier-1 branch: cut via `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh` on OR → push to origin → FI worktree add → develop/test on FI (FI venv) → suite gate (byte-identical baseline + own pins) → battery on the OR lane (or mic transport per PT) → report to `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter<N>-<slug>/` → **ASK Julio → merge only on say-so** (`--no-ff`, tag, `scripts/git-tree.sh`, ITERATIONS line).
- CHANGE POLICY on `.env`: agents NEVER edit canonical envs; new knobs must have code defaults matching the tested value (SWITCH LAW rule 4).
- What is NEVER touched: the hot-zone branches (`engine/iter65-*` chain, `engine/iter68-speech-flow`, `engine/iter68-speech-lite`, `engine/iter70-speech-fixes`), the OR protected checkout `engine/iter73-oregon-wip-20260924`, FI prod `/opt/diallux-production`, live agents `agent_16985b5d087e56c35141983396` / `agent_87e4d5f08475e5bc558b2f390f`, the FI services (:8001-8003), the OR prod-checkout dirty files (owner-ruled 2026-10-09: LIVE AS-IS, stay uncommitted).
- FI's locally-dirty worktrees stay dirty (owner 2026-10-09: "no harm") — nobody resets/stash-cleans anything.

## Tasks (in order)
### T1 — Per-PT eval table (zero-code, THE deliverable)
- Goal: for each of PT-1..PT-11 (PT-3 = parked, one line for it too): expect 1 branch? ~how many commits? files (abs paths) touched; suite pins (names); risk tier; its data gate from the Oct-6/8 calls; and the SHORTEST owner-review note. Add the two owner questions per PT where they exist (PT-6 wording, PT-7 fold, PT-10 dictation).
- Commands: fulfill every claim with line refs already gathered 2026-10-09 (all in this file + `00_pt_deepdive.md`); NO new exploration needed except confirming today's file line numbers shifted if any merge landed overnight.
- Deliverable: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/01_wave_eval.md`.
- Verification: every row cites at least one abs path + one verified fact; no row says "TBD".
### T2 — Tier proposal + owner queue refresh
- Goal: apply the TIER divider (1 SAFE QUICK WIN / 2 MEDIUM / 3 HEAVY) per the owner's stated intent (proposed below in T6 preamble, opinion: tier 1 = PT-4, PT-5, PT-8, (+PT-6 if owner keeps it — call it SMALL); tier 2 = PT-1, PT-11; tier 3 = PT-2, PT-9, PT-10) and present it for manual review. Update `/home/julio/projects/clean_diallux_SDR/plans/NEXT_STEPS.md` + PT-0 status (docs → main, ONE commit).
- Verification: owner has the eval file path + the tier marks in chat; no branch cut without the GO.
### T3 — (ON OWNER GO) tier-1 apply = cut lanes per LANE LAW
- Goal: serial cut of tier-1 branches. Per-branch recipe (identical DO: branch → suite → pin → battery → ASK):
- T3a (PT-4): OR: `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <next-free-iter> main gate-cap-500` (ports per Env). FI: `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/<worktree> <branch>` (origin pushed from OR first). Edit: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` `_FLUSH_LEN = 140` → flush purely on sentence boundaries + idle flush; hard cap becomes `settings.gate_flush_len` (default 500, `engine/diallux/config.py` field + ENV-SWITCHES registration). Pins: replay the Oct-8 233-char single-sentence shape → batch boundaries at sentence ends only, zero mid-clause cuts; flag-off byte parity: pin the CURRENT flush behavior under `settings.gate_flush_len=140` snapshot test. Suite: baseline byte-identical + pins green.
- T3b (PT-5): same recipe, branch `<next-free-iter>-rag-query-memo`. Edit: `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` fire sites (`:595-600`, `:788-793`, `:920`) — one dict on the CallRuntime: `self._rag_query_memo: dict[str, list]`; at fire: normalize query, hit → reuse `_live_consumed_res` chunks, `return` before embed; miss → fire + store. NO sqlite; store dies with the call. Pins: `test_<N>_rag_query_memo.py` — scripted 3-caller-fast shape: 3 identical queries → 1 embed, 2 memo hits; a delta query → new fire; byte-identical reuse; call-end purge correctness (fresh runtime = empty dict).
- T3c (PT-8): same recipe, observability-only. Edit: `engine/diallux/media/session.py` final-report assembly (near the iter93 `rag_consume` stamp at `session.py:923-925`) — add per-round `pre_llm_ms` breakdown fields from the existing round-clock stamps (no new spans, no behavior change). Pin: field presence + zero-change of every existing key.
### T4 — Gate checks + ASK
- Commands: per branch, `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1`; battery on the OR lane (or scripted mic-caller for the memo gate); ledger import `scripts/live_sql.py import --window "HH:MM-HH:MM" --run <name> --commit <sha>`; `scripts/keyhound` before every push.
- Verification: ASK text lists every gate number (suite diff, pins, battery, gate-vs-data) — the owner reads them and says merge/hold.
### T5 — heavier tiers: parked behind the owner's manual review of `01_wave_eval.md`
- TIER 3 (PT-2, PT-9, PT-10) gets its own mini-plan(s) after the review (PT-9 = the SPEC is the plan; PT-10 = HITL dictation first (design-first, like iter87 T0)); no branch is cut in this session for tier 3.
### T6 — Session close
- Status files: PT-0 verdict + tier marks into `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` rows (docs → main, one commit); ITERATIONS.md ledger line "iter102 roadmap session (no code)"; commit registry refresh ritual from the MAIN checkout's engine dir (backup `ledger.db` first per the standing law); `scripts/keyhound` before every push; evidence under `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/`.

## Validation Plan (end-to-end)
1. Every tier-1 branch: the suite's baseline red set byte-identical, growing only by its own pins.
2. PT-4 gate: on the Oct-8 cf047 shapes replayed at unit level (`/tmp/opencode/call_cf047_transcript.txt` regenerated anytime via `lf.py gens`) — 11 mid-clause cuts → 0; first-flush latency unchanged.
3. PT-5 gate: the cf047 rag rows (34 fires, 25 identical canned) replayed scripted → 1 embed + 24 memo hits; identical queue reuse; latency unchanged counter-style.
4. PT-8 gate: report keys gain `pre_llm_ms` breakdown fields; NOT ONE existing key changes; a live mic run stamps them non-negative.
5. No prompt or KB file changes on ANY tier-1 branch. No merges at all without owner say-so.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| PT-2 / PT-9 / PT-10 (tier 3 heavy) | owner's manual review of the eval table first; PT-10 needs the design dictation done as a HITL first |
| PT-3 transition beat | PARKED by owner (re-decide after PT-2 + one real call) |
| The 97 dial + merge sequencing (and the canonical `.env` ratification) | owner decisions standing in BLOCKED; either path lets tier 1 proceed |
| Deepgram EOT knob tuning | owner-deferred keeper (biggest lever, interacts with FIND-39) |
| Heating items (old PT-01..08) | other agent's lane |
| Fast-tier pricing truth | owner/OpenAI page |
| Cleaning ANY of FI's dirty worktrees | owner-ruled 2026-10-09: stay as-is |
