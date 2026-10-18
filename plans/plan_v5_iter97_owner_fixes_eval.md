# iter97 session-2 — owner's own iteration plan: soundness evaluation vs the 97 report, adapt/reject discussion (analysis only; no cuts; code-if-cut STILL rides iter97)

## Meta
- Date: 2026-10-08
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ANALYSIS + DISCUSSION. The owner brings his OWN plan of iterations (doc to be pasted in-session — T1 gate). The agent evaluates every proposed fix in it against the already-written 97 analysis report (`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_analysis.md`), classifies each as SOUND / UNSOUND / NEEDS-DATA with file:line + measurement evidence, then runs a structured adapt/not-adapt discussion round with the owner. ZERO engine code changes, ZERO branch cuts in this session. Numbering: EVERYTHING rides iter97 — including the eventual code cut (owner directive 2026-10-08: "STILL iter97 even when we cut") — superseding the earlier "next bare number = iter98" expectation.
- Status: PLAN ONLY (not started — awaits owner pasting his iteration plan)

## Compaction Context (session state carried verbatim, 2026-10-08)

### Where iter97 stands
- FI = `/home/julio/projects/clean_diallux_SDR` (this box, checkout parked on branch `engine/iter97-research-adaptation` @ `04562e7`, 1 docs commit behind main — code-identical to main). OR = `5.78.83.174` (work box; ssh: `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`; root checkout parked on PROTECTED `engine/iter73-oregon-wip-20260924` @ `61a88ff` — never touch).
- main = origin/main = `4ced81a` on BOTH boxes (the extra commit is the iter97 plan doc only).
- iter97 session-1 (analysis) is DONE: the owner's deep-research doc was ingested, audited against the working code, and cURL-benchmarked from OR. Deliverable written: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_analysis.md` (research/ = gitignored). Research source preserved: `/tmp/opencode/iter97_research_source.md` (verbatim copy of `diallux_v6_next_level_engineering_decisions.md`, originally at `/home/julio/projects/vps-inbox/diallux_v6_next_level_engineering_decisions.md`).

### The six verdicts already on record (97_analysis.md)
| # | Research fix | Verdict | Anchor evidence |
|---|---|---|---|
| 1 | TTS swap EL turbo→Flash (latency 100–150ms) | ADAPT (ear test only) | Measured warm TTFA wash: turbo ~255–270ms vs flash ~275–315ms (OR, n=4); flash wins cold-start 0.28s vs 0.60s; ~6× cheaper/char. Code default is ALREADY `eleven_flash_v2_5` (`/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py` ~411); OR prod `.env` pins `eleven_turbo_v2_5` |
| 2 | `tts_gate_fast_first_flush=true` | REJECT | Our own invention (iter46 T5, `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py:207`); re-argues PT-71 (recorded battery failure: chopped clauses / muted speech) without engaging the evidence; Voice LAW pins `false` (confirmed OR `.env`) |
| 3 | `service_tier="priority"` on brain | ADOPT-AS-IS | Absent from `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py` (confirmed). Measured OR: TTFT 1.18–1.94s → 0.72–0.97s uncached; 0.78s vs 1.18–1.81s on 5,888-tok cached prefix; **cross-tier cache read preserved (5,888/5,888 `cached_tokens`)**. Cost 2× tokens. Injection sites: `graph/llm.py` main `mk` dict (~232–238) + lazy verbosity twins (~278–284); warm twin (`:257`) inherits via `**kwargs` |
| 4 | Verify US box region | NO-OP (solved) | OR ↔ api.openai.com RTT 0.6ms avg, TLS 13ms — in-DC; 0ms to recover |
| 5 | Warm knobs 2500→700 / 500→300 | REJECT-as-proposed (superseded) | iter95 `prewarm_abort_cap_ms=400` (`config.py:~227`) already IS cancel-don't-wait with iter92b cache-survival proof; 2500 ratified on data (iter87: worst warm 2059ms, ZERO timeouts). No-op unless OR forensics show live 2500ms timeout events |
| 6 | Loop-contention fix (stream consumption + Twilio frame parse off media loop, ~250–350ms) | OPEN (owner scoping) | Surface verified: `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py:147–171` (inline parse/decode in WS receive), `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:871–880` (inline graph.astream consumption). Overlaps parked iter96c probe (`/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter96c_loop_lag_probe.md`) — do not stack |

### Owner directives locked this session (2026-10-08)
- "No fast mouth heavy brain for now" — doc §5–7 (M1 mouth-shadow / M2 / M3 split) DEFERRED. Not in any active plan.
- fast_first_flush = OUT (owner concurred "we gain nothing").
- EL Flash ear A/B = IN as an optional (no-code, owner-ear) task wherever the next ratified plan lives.
- Warm knobs = don't touch optimized values; forensics-gate only (default outcome: no change).
- **Numbering: everything stays iter97. No cuts until code time; when code is cut it STILL carries 97** (owner directive — supersedes iter98 minting; the Zero-Code-Rule hardening "mint at branch-cut" remains a queued proposal, not yet ratified).
- Ops note: `ELEVENLABS_API_KEY` value leaked into session log during the OR `.env` audit (redaction pattern missed it) — rotation recommended, owner call.

### Standing repo facts (unchanged)
- Engine suite baseline: **516 passed / 1 skipped / 5 failed** (pre-existing reds, identical on main tip). Command: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q`.
- OR lanes: `wt-9494` = `test/iter93-94-95` @ `9eb341c` on `:8049`+`:8050` (owner voicetests — never touch); `wt-96` = `engine/96-delta-cache` @ `b81b382` on `:8063` (PARKED, PT-85 owner verdict pending). FI `:8000–8003` = ORIGINAL live services (read-only law). FI `:8020` idle-ish iter96 lane; `:8021` reserved iter96c.
- Transport FI↔OR = git push/pull ONLY (no rsync/scp). `.env` values owner-set only. Switch register = `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md`.
- Goal on record: e2e_turn p50 ≤ 1,200ms real telephony (today ≈ 1,882ms).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Everything rides iter97, including any future code cut (branch will be `engine/iter97-<code-slug>` cut from main tip `4ced81a` when owner ratifies) | Owner directive 2026-10-08; kills the numbering-drift debate by owner law |
| No branch cuts and no engine code changes in THIS session | Owner: "no cuts until we touch code"; evaluation + discussion first |
| The six 97_analysis verdicts are the baseline of comparison for the owner's plan | They are the session-1 deliverable, owner-read |
| Mouth/brain split (M1/M2/M3) stays deferred | Owner directive 2026-10-08 |
| Analysis artifacts continue in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/` (gitignored); plans/docs → main straight | Docs law + evidence law (unchanged from session-1 plan) |
| cURL-before-edit remains the method for any latency claim | Owner mandate this session ("so we don't guess"); already produced the session-1 numbers |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| **Owner's own iteration-plan doc** (the input this whole session evaluates) | OWNER pastes it in-session or names its path (vps-inbox pattern like session-1's research doc). T1 GATE — nothing runs until it lands |
| Exact gpt-5.4 priority-tier pricing (2× figure verification) | OpenAI pricing page at implementation time — not needed for evaluation |
| Rank-6 scoping (in the 97 code cut vs separate lane) | Owner decides during T4 discussion |
| Key rotation execution (ElevenLabs) | Owner call; agent never edits `.env` values |

## Environment & Dependencies
- FI engine venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (Python 3.12; suite via `python -m pytest`).
- OR access (read-only git + read-only queries): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — log/branch/rev-parse/status/diff/grep + forensics reads only. NO checkout/switch/pull on OR.
- Secrets: keys ride `.env` files (gitignored). NEVER print values (session-1 incident on record). `scripts/keyhound` before any push.
- Evidence paths this session: `/tmp/opencode/iter97_owner_plan_source.md` (owner plan verbatim copy), `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_analysis.md` (baseline report), `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_owner_fixes_eval.md` (this session's deliverable).

## Architecture (what this session produces)
```
owner's iteration plan (pasted, T1)
        │
        ▼
   fix inventory (every proposed fix numbered, restated in engine terms)
        │
        ▼ per fix:
   [read 97_analysis verdict + working code @ 04562e7 + session-1 measurements]
        ─▶ SOUND (evidence supports) / UNSOUND (contradicts recorded evidence
           or measurement) / NEEDS-DATA (no evidence either way → name the
           exact measurement that would decide it)
        ─▶ file:line anchors + effort/surface/risk tag
        │
        ▼
   adapt / not-adapt DISCUSSION round with owner (one round, structured:
   agent recommendation per fix → owner verdict per fix, recorded verbatim)
        │
        ▼
   97_owner_fixes_eval.md (research/, gitignored) + ratified-fix shortlist
   ready for the future code cut (which, per owner law, will ride iter97)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/tmp/opencode/iter97_owner_plan_source.md` | verbatim copy of the owner's pasted iteration plan | NEW (tmp only) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_owner_fixes_eval.md` | per-fix soundness evaluation + adapt/not-adapt verdict table + owner's recorded answers | NEW (research/, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_owner_fixes_eval.md` | THIS plan (docs → main straight) | NEW (committed to main) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | +PT row ONLY if evaluation finds a live bug | EDIT (docs → main) |
| engine code / branches | NOTHING — analysis only, no cuts | — |

## Deploy Rules
- No deploys, no lane boots, no services touched, no branch cuts (FI or OR).
- Commits: THIS plan file → MAIN straight (docs law) from the FI checkout (temporary `git switch main` → commit → push → `git switch engine/iter97-research-adaptation` back). `scripts/keyhound` before push.
- NEVER touch: protected `engine/iter73-oregon-wip-20260924`, parked wt-96/`:8063`, voicetest lanes `:8049`/`:8050`, ORIGINAL services `:8000–8003`, prod agents (`agent_16985b5d087e56c35141983396`, `agent_87e4d5f08475e5bc558b2f390f`), `.env` values, `validator_endpoint/` live code.

## Tasks (in order)
### T1 — Ingest the owner's iteration plan (GATE)
Goal: capture the owner's own plan-of-iterations verbatim.
Commands:
```
cp <owner-pasted-path> /tmp/opencode/iter97_owner_plan_source.md
```
(if pasted inline, save the content to that path first). If the owner has not pasted it: STOP — nothing else in this plan runs.
Verification: file exists, non-empty; fix/iteration entries are extractable.
Dependencies: owner input.

### T2 — Inventory + cross-reference
Goal: number EVERY proposed fix/iteration in the owner's plan; restate each in engine terms; mark which of the six 97_analysis verdicts it touches (or "new" if it doesn't).
Files: working notes only (deliverable assembled in T3/T5).
Verification: inventory row count = recount twice; every row cites the owner-plan section it came from.

### T3 — Soundness evaluation (the core)
Goal: for every inventory row, evaluate against 97_analysis.md + working code @ `04562e7` + session-1 measurements; classify SOUND / UNSOUND / NEEDS-DATA with at least one file:line or measurement anchor. Where NEEDS-DATA: name the exact measurement (e.g. "OR warm-span forensics p50/p95", "cURL TTFT with <exact payload>") and its cost.
Commands (read-only, FI):
```
cd /home/julio/projects/clean_diallux_SDR && sed -n '<range>p' <file>
cd /home/julio/projects/clean_diallux_SDR && git grep -n "<term>" engine/diallux/
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q   # once at session end, drift proof
```
Optional read-only cURL (only if the owner's plan asserts an unmeasured latency number; same method as session-1, keys from OR `.env` via remote shell vars, never printed).
Files: `97_owner_fixes_eval.md` (draft).
Verification: every row classified with ≥1 anchor; any UNSOUND row names the recorded evidence it contradicts (post-mortem row, Voice LAW, battery record, or session-1 measurement).

### T4 — Adapt / not-adapt discussion round (owner in the loop)
Goal: present the evaluation as a compact per-fix recommendation table (RECOMMEND ADAPT / REJECT / MEASURE-FIRST + one-line reason); get the owner's verdict per fix; record answers verbatim (including any owner overrides).
Verification: every inventory fix has an owner verdict line; disagreements with 97_analysis are explicitly marked as owner-overrides with rationale.

### T5 — Deliverable + drift check
Goal: finalize `97_owner_fixes_eval.md` (verdict line at top: "N owner fixes: X sound, Y unsound, Z needs-data; ratified shortlist = …"); commit THIS plan to main if not already committed; prove zero code drift.
Commands:
```
cd /home/julio/projects/clean_diallux_SDR && git status -s engine/   # must be empty
cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q   # 516 passed / 1 skipped / 5 failed
```
Verification: suite count identical to baseline; `git status -s engine/` empty; shortlist ready for the (owner-gated) code cut that will ride iter97.

## Validation Plan (end-to-end)
- Suite count identical to baseline (516/1/5) at session end — zero code drift.
- Every fix in the owner's plan has: inventory row → soundness classification with anchors → owner verdict.
- No engine/ file modified; no branch cut on either box (check: `git branch --show-current` unchanged on FI; OR root checkout still `engine/iter73-oregon-wip-20260924`).
- The ratified shortlist is executable by a fresh agent: each fix carries exact files/commands/verification for the future iter97 code cut.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| The code cut itself (carrying iter97, per owner law) | Owner gates it until evaluation + discussion conclude; will be cut from main tip `4ced81a` |
| Mouth/brain split M1/M2/M3 | Owner-deferred 2026-10-08 ("no fast mouth heavy brain for now") |
| iter96 merge verdict (PT-85) | Owner-gated until the `:8063` Twilio forensics verdict |
| iter96c loop-lag probe | Separate plan-only lane, branch NOT cut; merges with rank-6 question later |
| Deepgram EOT knob values | Owner-set, out of agent hands |
| Zero-Code-Rule hardening ("mint the number at branch-cut") | Queued proposal for owner approval — one-line docs edit |
| ElevenLabs key rotation | Owner call (session-1 leak on record) |
