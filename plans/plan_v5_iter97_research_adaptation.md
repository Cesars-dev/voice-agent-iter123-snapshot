# iter97 — deep-research adaptation: compare the owner's research fixes against the working engine (analysis only, zero behavior change)

## Meta
- Date: 2026-10-07
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ANALYSIS ONLY. Cut branch `engine/iter97-research-adaptation` from main tip (DONE @ `04562e7`, owner say-so 2026-10-07). Read the owner's pasted deep-research md, diff every proposed fix against the working engine code line-by-line, produce a fix-by-fix verdict (ADOPT-AS-IS / ADAPT / REJECT) + the implementation plan draft. NO engine code changes in this session — the implementation rides follow-up branch work after owner ratification.
- Status: IN PROGRESS (T0 done; T1 BLOCKED on owner pasting the research md path)

## Compaction Context (everything that matters, imported)

### Repo state (2026-10-07, post sync+guard session)
- FI = `/home/julio/projects/clean_diallux_SDR` (this box); OR = `5.78.83.174` (work box, ssh: `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`, repo `/home/julio/projects/clean_diallux_SDR`).
- main = origin/main = `04562e7` on BOTH boxes (synced via GitHub only — no rsync/scp, ever).
- FI checkout sits ON `engine/iter97-research-adaptation` @ `04562e7` (pushed, tracking origin).
- OR checkout: root repo parked on PROTECTED `engine/iter73-oregon-wip-20260924` @ `61a88ff` (owner prod endpoints config — DO NOT touch/rebase/reset/force-push; marker commit + `BRANCH_GUARD.md` + pre-push hook both boxes + local refs `guard/iter73-prod-endpoints` + append-only mirror repo `Cesars-dev/clean-dialux-sdr-guard`; GitHub rulesets unavailable — free plan). OR main checkout = worktree `/tmp/opencode/wt-main-docs` @ main.
- OR lanes RUNNING (never touch): `wt-9494` = `test/iter93-94-95` @ `9eb341c` on ports `:8049` + `:8050` (owner's Twilio voicetest targets); `wt-96` = `engine/96-delta-cache` @ `b81b382` on `:8063` (iter96 PARKED, PT-85).
- iter96 merge decision = PARKED BY OWNER AGREEMENT (2026-10-07): leave unmerged until PT-85 (owner fires real Twilio call at `:8063` → forensics vs baseline trace `152d98c0...` → verdict). DO NOT stack anything on it.
- iter96c probe (loop-lag) = SEPARATE plan-only lane: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter96c_loop_lag_probe.md` (on main @ `b43cac5`). Branch NOT cut. This iter97 session does NOT cut or execute it.
- Engine suite baseline: **516 passed / 1 skipped / 5 failed** (pre-existing reds, identical on main tip). Command: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q`.
- Engine ttft anchor (pinned): t0 = `perf_counter()` before `runtime.llm.astream(...)` (`/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py:2403` on main; first-event anchor :2439; logged in round-usage line :2452 area). Yardsticks: chat-path TTFT p50 **728 ms**; mic-path engine ttft p50 **900–1,065 ms**; gap ≈ 250–350 ms, hypothesis = asyncio loop contention (NOT yet proven — iter96c's job, not this plan's).
- Owner's standing goal: **e2e_turn p50 ≤ 1,200 ms on real telephony** (today ≈ 1,882).

### The research (owner-supplied, this session)
- The owner ran a DEEP RESEARCH on a dual-model voice-agent architecture ("fast mouth" gpt-4.1 for conversational speech turns / "smart hands" gpt-5.4 for tool-heavy turns) — repo published for it: `https://github.com/Cesars-dev/diallux-sdr-v5-engine-research` (`RESEARCH_QUESTIONS.md` pushed there 2026-10-06; deep-research prompt also saved at `/tmp/opencode/iter96b/deep_research_prompt.md`).
- The owner will PASTE or NAME the research md file path during this session. Every claim in it gets compared against the working code; nothing is taken on faith.

### Resolved decisions (carried, DO NOT revisit)
- Branch = `engine/iter97-research-adaptation`, cut from main `04562e7` (owner said so; NOT a suffix of iter96 — the eventual adaptation is engine code = next bare number).
- MODEL LAW: agent LLM = `gpt-5.4` everywhere TODAY; any model split (gpt-4.1 mouth / gpt-5.4 hands) is EXACTLY what this analysis evaluates — no switch flips without owner say-so.
- Analysis artifacts → `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/` (gitignored); plans/docs → main straight (docs law).
- One-variable law per implementation change; suite green before any future code branch merges; nothing merges without owner say-so (LAW 0).
- OREGON transport = git push/pull only. `.env` values owner-set only. Switch register = `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md`.

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Research md file path | OWNER pastes it in-session (T1 gate — do nothing until it lands) |
| Any research claims that reference code lines | Resolve by reading the CURRENT working code on the branch, not the research's line numbers (research may quote older iter numbers) |

## Environment & Dependencies
- FI engine venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (Python 3.12; suite via `python -m pytest`).
- OR repo access: ssh command above; READ-ONLY git over ssh for this plan (log/branch/rev-parse/status/diff/grep) — NO checkout/switch/pull on OR outside an owner-approved lane op.
- Ports (NEVER touch): FI `:8000-8003` (ORIGINAL services), `:8501` (Streamlit), `:8020` (iter96 FI lane, idle-ish — shows LISTEN), `:8021` reserved for iter96c probe; OR `:8049`/`:8050` (voicetests), `:8063` (parked wt-96), `:8065` (reserved iter96c), `:8080` (Caddy), OR service ports.
- Langfuse FI CLI: `cd /home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5 && python3 scripts/lf.py health|traces|show|gens` (keys in its `.env`; ingest quirk: verify with 48h trace scan before trusting absence).
- Key files of the working engine (read targets for the comparison): `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/delivery.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py`, `/home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/*.md`, `/home/julio/projects/clean_diallux_SDR/engine/agent/llm.json` (DISPLAY-ONLY dead metadata — never trust it for model).

## Architecture (what this session produces)
```
owner research md ──▶ fix inventory table (every proposed fix, numbered)
        │
        ▼ per fix:
   [read working code @ branch tip 04562e7] ─▶ verdict ADOPT-AS-IS / ADAPT / REJECT
   ─▶ line-anchored rationale (file:line) ─▶ effort/surface/risk tag
        │
        ▼
   97_analysis.md (research/surgeon/, gitignored) + implementation-plan draft
        │
        ▼
   LAW 0: owner reads verdict → ratifies → REAL code branches get cut per fix (one variable at a time)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/tmp/opencode/iter97_research_source.md` | verbatim copy of the owner's pasted research md (working copy) | NEW (tmp only) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_fix_inventory.md` | every research fix numbered + restated in engine terms | NEW (research/, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_code_comparison.md` | per fix: current code state (file:line on `engine/iter97-research-adaptation`), delta, verdict ADOPT-AS-IS/ADAPT/REJECT, effort/surface/risk | NEW (research/, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_analysis.md` | final report: verdicts + recommended adaptation order + open HITL questions for owner | NEW (research/, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_research_adaptation.md` | THIS plan (docs → main straight) | NEW (committed to main) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | +PT row only if analysis finds a live bug | EDIT (docs → main) |
| engine behavior | NOTHING — analysis only | — |

## Deploy Rules
- No deploys, no lane boots, no services touched. This session is read-code + write-analysis.
- Commits: docs/analysis files → MAIN straight (docs law); anything engine-shaped = FORBIDDEN this session. `scripts/keyhound` before any push.
- NEVER touch: protected iter73 branch, parked wt-96/`:8063`, voicetest lanes `:8049`/`:8050`, ORIGINAL services `:8000-8003`, prod agents (LAW 6), `.env` values.

## Tasks (in order)
### T0 — Branch cut (DONE before this plan was finalized)
Goal: `engine/iter97-research-adaptation` from main tip.
Commands (already run, recorded for the record):
```
cd /home/julio/projects/clean_diallux_SDR && git switch -c engine/iter97-research-adaptation 04562e7
git merge-base --is-ancestor 04562e7 HEAD
git push -u origin engine/iter97-research-adaptation
```
Verification: HEAD = `04562e7`, merge-base check exit 0, origin tracking set. ✓ DONE 2026-10-07.

### T1 — Ingest the research
Goal: owner pastes/names the research md; capture verbatim.
Commands: `cp <pasted-path> /tmp/opencode/iter97_research_source.md` (if a path); else save the pasted content to that path.
Verification: file exists, non-empty; fix inventory can be extracted.
GATE: if the owner has not pasted it, STOP — nothing else in this plan runs.

### T2 — Fix inventory
Goal: extract EVERY proposed fix/change/architecture element from the research into a numbered table, restated in engine terms (no marketing prose).
Files: `97_fix_inventory.md`.
Verification: table row count = research's fix count (recount twice); every row cites the research section it came from.

### T3 — Code comparison (the analysis core)
Goal: for each inventory fix, read the CURRENT working code on the branch tip and classify:
- **ALREADY-PRESENT** (main has an equivalent — cite file:line; note any behavioral delta),
- **DIVERGENT** (research proposes something the code does differently — describe both),
- **MISSING** (research-proposed, absent from code — describe the insertion surface),
- **SUPERSEDED** (a later iter already solved the underlying problem differently — cite the iter).
Commands (read-only):
```
cd /home/julio/projects/clean_diallux_SDR && git grep -n "<term>" engine/diallux/
sed -n '<range>p' engine/diallux/graph/builder.py
cd engine && .venv/bin/python -m pytest tests -q   # once, to prove zero drift vs 516/1/5
```
Files: `97_code_comparison.md`.
Verification: every inventory fix has a verdict row; every verdict cites at least one file:line; suite count unchanged (516/1/5).

### T4 — Report + implementation-plan draft + LAW 0
Goal: `97_analysis.md` with (a) per-fix verdict table, (b) recommended adaptation ORDER (one variable at a time; cheapest-surface first; latency levers ordered vs the 1,200 ms goal), (c) open HITL questions; then draft the implementation plan file (`plan_v5_iterNN_*.md` — number minted per numbering law only if/when code is ratified).
Verification: verdict line at the top of `97_analysis.md` = "N fixes: X adopt-as-is, Y adapt, Z reject; recommended first branch = …". Then ASK JULIO (LAW 0) — nothing cuts until he reads it.

## Validation Plan (end-to-end)
- Suite count identical to baseline (516/1/5) at session end — proves zero code drift.
- Every research fix appears in the inventory; every inventory fix has a verdict with file:line anchors.
- No engine/ file modified (check: `git status -s engine/` empty at session end, apart from untracked research artifacts).
- Plan-to-implementation handoff is executable by a fresh agent: next-session plan carries exact paths/commands/ports/verification per this SOP.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Any engine code change (the adaptation itself) | Analysis-only session; implementation = ratified follow-up branches, one variable at a time |
| iter96 merge (PT-85) | Owner-gated, parked until the `:8063` Twilio verdict |
| iter96c loop-lag probe | Separate plan-only lane (`plan_v5_iter96c_loop_lag_probe.md`), branch NOT cut, NOT this session |
| Deepgram EOT knob values | Owner-set, out of agent hands |
| iter73 branch | PROTECTED prod endpoints config — never touched |
