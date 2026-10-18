# AGENTS.md — Operating manual for AI agents working in this repo

> **Read this before touching anything.** One repo, one tree, zero nested repos.
> The law: DOCTRINE.md · the map: GIT_TREE.md · the why: STRUCTURE.md · the queue: plans/NEXT_STEPS.md.
> Fork of Retell_AI_MCP_connection (2026-09-08). The ORIGINAL still serves :8000–8003;
> **never run services from this repo until cutover** (DOCTRINE §6).

## NEXT UP (owner 2026-10-09)

> **THE BACKLOG = `plans/PENDING_TASKS.md` -> "LIVE BACKLOG" (queue head = PT-0, the next session; everything older = the ARCHIVE section below it in that file).**
> NEXT SESSION = eval branches/commits per wave PT (PT-1..PT-9) -> execution plan -> apply. PT-9 = the SPEAK-FIRST split-round (big latency lever, spec ready).
> **THE GOAL unchanged: e2e_turn p50 <= 1,200 ms on real telephony** (1,882 baseline).
> **WORKFLOW (owner-ratified): develop/test on Finland, push-pull via git to OREGON** for lanes/batteries — no rsync, ever.
> Deferred to owner: Deepgram EOT knob values (biggest latency lever). Parked: iter77-twilio @ 8c5f72f.
**Context (owner post-mortem 2026-09-23):** iter68/68-lite = PARKED, total failure ("our solutions caused more problems than they solved"). The overengineering — semantic cos dedupe, scripted-pass registries, 2-strike ladders, chain-link buffering — muted/truncated REAL speech. We fix small, on main, prompt-first, env-knob-first. **Do NOT cherry-pick or merge from `engine/iter68-speech-flow` / `engine/iter68-speech-lite`.** Reference plans (all on main): `plans/plan_v5_iter68_speech_flow.md` (v1, the good one) + v2 + v3; post-mortem rows PT-68..PT-73 in `plans/PENDING_TASKS.md`.
**Parked merge-ready:** `engine/iter67-twilio-live-lane` @ `0394a3b` (collision-free verified; merge = owner only).
**PROTECTED BRANCH (owner, 2026-10-07):** `engine/iter73-oregon-wip-20260924` = the owner's **prod endpoints config** (llm.json validator URLs → 127.0.0.1:8080 oregon latency workaround + run ledgers). **DO NOT touch / rebase / reset / force-push it — ever.** Guard stack: tip marker `61a88ff` (`BRANCH_GUARD.md`); pre-push hook on both boxes (blocks delete + non-ff for this ref); local backup branch `guard/iter73-prod-endpoints` on both boxes; append-only mirror repo `Cesars-dev/clean-dialux-sdr-guard` (holds the branch — GitHub rulesets/branch-protection unavailable: account is on FREE plan for a private repo). Force-pushing or rewriting this branch = revert on sight (hard rule 0 class).
**Voice LAW current (2026-09-28):** ElevenLabs is DEFAULT (prod = Hannah `ZSNL4hPqCnqoMPaI4jGX` speed 1.0/stability 0.6/style 1.0 + py playback accel 1.08–1.15; tests = Sarah `uG1JFy6xppqckhHCs2KG`); Cartesia ONLY for HIPAA or lower-quality deployments/tests — see the VOICE LAW section below. `TTS_GATE_FAST_FIRST_FLUSH=false` + `TTS_DEDUPE_SEMANTIC=false` stay (PT-71 class lessons: chopped clauses / muted real speech); same-turn dup guard + sanitizer stay ON (main defaults).

## Zones and what they mean

| Zone | What it is | You may | You may NOT |
|---|---|---|---|
| `engine/` | The LangGraph voice pipeline (diallux brain, prompts, tests, harness) | iterate on `engine/iterNN-*` branches | commit evidence into it; create folder copies |
| `retell/sdr/` | Deployed Retell chat agent, config-as-code (`current/` = V7.9 slot-lock) + versions ladder | read; new version = new folder + MANIFEST + tag | patch a version in place; deploy without plan |
| `retell/heating-uk/` | UK HVAC voice agent line (V3.1 near-prod) | same discipline as sdr | same |
| `services/` | time :8002 / cal_slots :8001 / validator :8003 + proxy_guard — LIVE infra (original still serving) | read code, write docs | **start/stop/bind ports**; run uvicorn here |
| `docs/` | SOPs (BUILD, DEPLOYMENT, Testing_guidelines 3-SOP audit, api, legacy) | read first; update on drift | — |
| `plans/` | NEXT_STEPS.md (live queue) + SOP_NEW_PLAN.md + archive/ of every past plan | write plans per SOP | park active work anywhere else |
| `research/` | EVIDENCE: surgeon reports, transcripts (engine+chat+heating), batteries, dumps, salvage manifests | append; read for forensics | track in git (gitignored); put source there |
| `_cold_archive/` | tarballs of every dead folder (snapshots, stale twin, state_machine, 6.1 era, mcp server) | nothing | resurrect without explicit plan + owner OK |

**Git history is Julio's crystal ball. What matters is WHAT you're changing:**

> **ITERATION NUMBERING LAW (owner, 2026-09-25):** "iter" = a CODE change to the MAIN
> pipeline (`engine/diallux/` + its prompts). The iter number increments ONLY when a new
> code branch modifying the main pipeline is cut. EVERYTHING else rides the CURRENT
> iteration number with a suffix naming what it was — docs, plans, analyses, surgeon
> reports, string/script edits, SDK changes, lang updates, anything outside
> `engine/diallux/` → same N, e.g. `iter78/plan_x`, `iter78/audit_stt`,
> `iter78/sdk_y`. Code that lands straight to main (not engine code) also keeps the
> same iter number. This keeps iter + its non-code artifacts traceable as one unit.
>
> **ZERO-CODE RULE (owner, 2026-10-05, hardening after the iter90/92 drift):** a
> session that changes no `engine/diallux/` code NEVER takes the next bare number as
> its own mission name. It carries the last CUT CODE iter with a suffix —
> `iter<NN>/verdict`, `iter<NN>b/quant`, `iter<NN>c/audit` — in the plan filename,
> the lane/branch name, the report folder, and every evidence pointer. Docs and
> verdicts of a zero-code run land straight to main (rule 0 docs law); nothing
> engine-shaped is created for them. (Drift on record: iter90/92/92b took bare
> numbers as owner-ordered mission names with zero code — tolerated once, do not
> repeat; retroactive renames NOT required.)
```
plan (plans/plan_*_iterNN_*.md) → branch engine/iterNN-<slug> → ONE variable
→ suite green (pytest engine/tests) → battery (first-13 + stress per SOPs)
→ report (research/surgeon/iterNN-slug/NN_*.md) → commits on the branch
→ ASK JULIO (LAW 0) → [on owner say-so: merge --no-ff → tag engine/iterNN
→ scripts/git-tree.sh → ITERATIONS.md ledger line]
```

- Happy-path gate first: never stress a broken flow (`--no-happy-gate` only on purpose).
- After every battery: cancel ALL test bookings (Cal.com event 3801235 is REAL).
- Abandoning an iteration? Leave the branch + one-line verdict in ITERATIONS.md.

## Hard rules (violations = revert on sight)

0. **⚖️ LAW 0 — THE GIT CRYSTAL BALL (v2):** **CODE = full discipline:** any code,
   prompt, agent-config, KB or services change → branch `engine/iterNN-<slug>` per
   approved plan → commit on branch → test → report → ASK. **NO merges of code branches
   without Julio's explicit say-so. Ever.** **DOCS = straight to main:** md files
   (README/AGENTS/DOCTRINE/GIT_TREE/STRUCTURE/MIGRATION_MAP/plans/notes/ITERATIONS)
   commit + push directly to main, no ceremony — nothing harmful in them (no secrets,
   no evidence bulk). **Always say-so:** rebase, force, branch delete/rename, history
   rewrite; tags only with owner-approved merges.
   **"Branch" is an owner trigger word (v2.1, 2026-09-22):** when Julio says
   "branch (it)", a NEW branch `engine/iterNN-<slug>` is cut from the current
   tip for that work — NEVER stack onto an existing iteration branch (lesson
   2026-09-22: the iter64c llm.json MODEL LAW bump rode the already-complete
   iter64 branch and merged with it), NEVER commit code/agent-config changes
   to main, and never do the new work on a branch that is awaiting merge.
      **Test-infra whitelist lane (v2.3, 2026-10-06, owner-approved iter95/sdk Mode A):** `scripts/fast_suite.sh`, `engine/tests/**` test files, and pytest config may commit STRAIGHT to main (gated per-commit by `scripts/fast_suite.sh --touched` passing BEFORE the commit lands). The full merge gate (one full-suite run per branch/session) and the NEVER-lane (`engine/diallux/**`, prompts, retell, services) are untouched.

**Prompt-layer is CODE, not docs (v2.2, 2026-10-02):** `engine/diallux/prompts/*.md`, `engine/agent/knowledge_bases/*.md`, and `engine/agent/llm.json` are prompt-layer changes under full LAW 0 discipline — branch `engine/iterNN-<slug>`, commit on branch, ASK before merge — even though they are md files. The "docs straight to main" lane NEVER covers them.
1. **No repo inside a repo.** Nested histories live as refs (`engine/*`, `history/*`) — that's where they stay.
2. **No folder snapshots.** iter state = branches. Snap-era (`engine/snap-*`) is read-only archaeology.
3. **No tokens in URLs, no .env in git.** Run `scripts/keyhound` before any push. Rotate the exposed V7.9 PAT (known contamination — see MIGRATION_MAP).
4. **Evidence goes to `research/`** — transcripts, reports, dumps. Never inside engine/ or retell/.
5. **`scripts/git-tree.sh` after every merge** — GIT_TREE.md must never be >1 iteration stale.
6. **Never touch live agent IDs** (`agent_f305…` sdr, `agent_1698…` heating voice, `agent_87e4…` chat) without an explicit plan + owner instruction.
7. **KB policy stands**: reuse/upsert via `kb_registry.json` — never hand-create KBs (~$250 lesson).
8. **COMMIT REGISTRY LAW (owner, 2026-10-04): every commit lands in the SQLite commit registry.** The registry (`research/surgeon/iter47-call-ledger/ledger.db`, generated by `scripts/call_ledger.py`) tracks every commit WITH the columns that say WHY it was made (purpose, plan, verdict). A commit that is not registered = a commit that did not happen. Refresh ritual: re-run the registry build from the MAIN checkout's `engine/` dir at the END of every session that made commits (backup `ledger.db` first) — the registry is a derived view of git and goes stale otherwise. Reading: `<venv>/bin/python -c "import sqlite3; …"` (no sqlite3 CLI on the box).
9. **COMMIT DISCIPLINE LAW (owner, 2026-10-04): commits only happen as part of active, planned work.** No drive-by commits, no commits outside the current lane/plan, no "while I'm here" commits. The paper trail IS the point: **plans and docs are committed straight to main** (rule 0 docs law), so every code commit on a branch can be traced to a plan commit on main — clear doc for every single commit. If work is not worth a plan line or a registry row, it is not worth a commit.

## LANE LAW — worktrees, venv, .env (owner, 2026-10-04, iter91)

**The disease (paid for repeatedly):** git worktrees are code-only — gitignored `.venv`/`.env` do NOT follow. Every new lane was hand-dressed: envs copied from whatever worktree was nearby (carrying stale values — the wrong `WARM_AWAIT_DEST_MS=250` rode into iter91's lane from a sibling worktree and pytest silently tested against it), venvs "borrowed" by remembered absolute paths, tests reading ambient `.env` from CWD. Same class of bug, rediscovered every iteration.

**The law:**

1. **ONE command to open a lane — `scripts/new_lane.sh <iterNN> <base-sha-or-branch> <slug>`** (from the repo root, on OREGON). It does the whole dance: `git worktree add /tmp/opencode/wt-<iterNN> -b engine/<iterNN>-<slug> <base>` → venv symlink → `.env` generated from the canonical → **audit gate** against known-bad values (`WARM_AWAIT_DEST_MS=250`, missing `CARTESIA_MODEL_ID` dated pin, `DEEPGRAM_EAGER_EOT_THRESHOLD > DEEPGRAM_EOT_THRESHOLD` → Deepgram rejects with HTTP 400, probed 2026-10-03) → verdict line in `/tmp/opencode/lane_manifest.txt`. Exit 0 = lane READY; exit 1 = lane **DOA — do not boot it**, fix the env first. `scripts/new_lane.sh --list` = lane inventory. The script only ever CREATES new lane folders — it never touches the OREGON main checkout, existing worktrees, or running services.
2. **ONE venv per box — never copied, only symlinked.** Canonical: `clean_diallux_SDR/engine/.venv`. Every lane symlinks it read-only (`ln -s`, the script does it) and RUNS from it; nothing installs into it during normal work. The old copy-mirror venvs (and their broken `bin/pip` shebangs — see Eval SOP pip trap) are the anti-pattern. Exception: an iteration that genuinely needs a NEW package gets a lane-PRIVATE venv (`python -m venv` + `python -m pip install -r requirements.txt`) recorded in the lane manifest; the canonical venv changes only via owner-approved dependency bumps.
3. **ONE canonical `.env` — generated, never hand-copied.** `clean_diallux_SDR/engine/.env` (OREGON main checkout) is the ONLY source lane envs are generated from; values are ratified in `docs/Testing_guidelines/ENV-SWITCHES.md`. NEVER copy an `.env` from another worktree — that is how the wrong 250 traveled.
4. **Tests are environment-hermetic.** `engine/tests/conftest.py` (autouse) blocks `.env` discovery during pytest — the suite result must not depend on what env file happens to sit in the worktree. Tests pin their own Settings explicitly (most already do via `_settings()`). Suite-safe by evidence: iter91 audit ran the full suite with and without `.env` — identical red set. A test that "passes only with ambient env/network/keys" is a bug in the test (paid lesson: `test_iter44_dead_store` was making REAL Deepgram websocket connects).

## Where the history is (the thing agents always ask)

- Engine iterations iter21→iter31: branches `engine/iter*` (+`engine/main` = iter28 merge)
- Photocopy era iter7→iter20 + iter22-abort: branches `engine/snap-*` (chained chronologically; `git diff engine/snap-v1.3-iter7 engine/snap-v1.3-iter8` shows what iter8 changed)
- Stash: `refs/stashes/engine-phaseB` (phaseB WIP) + `engine/phaseB-wip-stash`
- Nested repos of the past: `history/v79-simulator/*`, `history/state-machine-voice/*`, `history/retellai-mcp-server/*`
- Folder-era archives: `_cold_archive/*.tar` (stale twin, 9 snapshots, state_machine, 6.1 era, mcp server, old webhooks)
- Old-path → new-path: MIGRATION_MAP.md

## Run & test (engine only; services are read-only here until cutover)

```bash
cd engine
.venv/bin/python -m pytest tests -q                    # suite (expect current count from ITERATIONS.md)
set -a; . ./.env; set +a                                 # secrets (gitignored)
.venv/bin/python tests/llm2llm/harness.py --personas Maria --rag --langfuse --max-turns 48   # single persona
.venv/bin/python scripts/lf_eval.py ladder               # full SOP ladder (skips Larry the assassin)
```

Langfuse SDK: `scripts/lf.py` (health/traces/costs), `scripts/lf_eval.py status`.
Personas: 25 in `tests/llm2llm/personas.py` — 13 original + 12 adversarial; Larry is gated.
Reports of past batteries: `research/surgeon/v5-pgvector-gpt52-argfix/` and siblings.

## Eval SOP — SQLite call ledger (iter48+, MANDATORY for every engine iteration)

Every engine iteration MUST leave its call evidence in the SQLite ledger —
Langfuse is the source, SQLite is the workspace. **No run is "done" until it is
imported and verified by SQL.** Read
`research/surgeon/iter48-rag-truth/SQL_ANALYSIS_SOP.md` FIRST (exact design:
tables, import, bug-coverage queries, Langfuse cross-check, percentile fields).

- Ledger: `research/surgeon/iter48-rag-truth/ledger.db` (runs/calls/rounds/rag/findings).
- Import: `scripts/live_sql.py import --window "HH:MM-HH:MM" --run <name> --commit <sha>`.
- Quick pulls: `scripts/lf_quick.py runs|bugs|table|rounds|scaffold`.
- Gates are named SQL queries (`live_sql.py gates --a <a> --b <b>`), never "feels okay".

**SWITCH LAW (mandatory, 2026-10-02 — the iter87/iter90 lesson):** every engine
behavior switch is a `diallux/config.py` Settings field whose code default is
silently overridden by the gitignored `engine/.env` — which does not travel with
worktrees and has no git diff, so config drift is invisible and has bitten three
iterations of tests (the deterministic hold shipped default-0, nothing turned it
on, fresh boots ran a different engine than the battery that passed). Therefore:
1. The register of all switches + what they do + current resolved values lives in
   `docs/Testing_guidelines/ENV-SWITCHES.md` — read it before trusting any comparison.
2. EVERY run/battery/live call snapshots its RESOLVED switch set next to the
   evidence (the command in ENV-SWITCHES.md §2) and diffs it vs prod and vs the
   previous passing run.
3. A behavioral-switch diff between two runs = the comparison is VOID until the
   verdict explains it.
4. Load-bearing design switches must have their CODE DEFAULT equal the tested-on
   value; default-off for a tested design was the bug.
5. `.env` values are owner-set only (LAW 0). Agents never edit them.

**TWO ledgers (different jobs):**
1. **Call/findings ledger** — `research/surgeon/iter48-rag-truth/ledger.db` (runs/calls/rounds/rag/findings): per-call evidence + the `findings` bug log. Schema + gates: `SQL_ANALYSIS_SOP.md` in the same folder.
2. **Branch/iteration registry** — `research/surgeon/iter47-call-ledger/ledger.db` (branches/commits/runs/calls): one queryable view of ALL `engine/*` branches + head commits. Generator: `scripts/call_ledger.py` — lives on branch `engine/iter47-call-ledger` (NOT on main; extract via `git show engine/iter47-call-ledger:scripts/call_ledger.py` — no merge needed to RUN it, commit to main = owner call). **Refresh ritual: re-run the build from the MAIN checkout's `engine/` dir at the END of every battery session** (the registry is a derived view of git; it goes stale otherwise) — backup `ledger.db` to `ledger.db.<tag>.bak` first. TRAP: run it from the MAIN `engine/` checkout — `json_logs` live there (a fresh worktree has none and the glob silently returns nothing = empty calls table), and the script reads `json_logs`/`.env` from `__file__`-derived ROOT, not cwd.
3. Reading either DB: NO `sqlite3` CLI on this box — `.venv/bin/python -c "import sqlite3; …"` from the engine worktree.
4. **pip trap:** `engine/.venv` is a copy-mirror venv — `bin/pip`'s shebang points at the ORIGINAL live venv. Always `<venv>/bin/python -m pip …`, never the pip script.

**REVISION LOGGING (mandatory):** every harness/battery/live run gets its own
imported `run_id` tagged with the commit sha it ran on (naming: `smoke-a`,
`happy-a`, `happy-b`, `battery-iter48` — letter = commit snapshot). Re-run the
bug-coverage check (`lf_quick.py bugs --run <name>`) after EVERY change: fixes
break other things, so the SAME queries must be re-verified after each revision.

**AUTOPSY REPORT (mandatory on any failure):** when a call/persona crashes,
loops, regresses vs the previous run, or fails a gate — write an autopsy to
`research/surgeon/iterNN-slug/` (per-call: transcript turns, rag/round rows from
the ledger, root cause with line numbers, whether it is NEW vs a known `findings`
row). Record the finding in the ledger `findings` table + `plans/PENDING_TASKS.md`
(as PT-NN) so branch/commit evidence survives the session.

## MODEL LAW (owner, 2026-09-22)

- **Agent LLM = `gpt-5.4` EVERYWHERE** — chat harness, voice/mic, every deploy, every test. No exceptions without an explicit plan + owner say-so.
- Runtime switch = `OPENAI_MODEL` in the engine `.env` (this OVERRIDES code defaults — pydantic Settings env wins). `agent/llm.json`'s `"model"` field is DISPLAY-ONLY dead metadata the engine never reads — do not trust it, do not "fix" the model by editing llm.json alone.
- `config.py:openai_model` default flip to `gpt-5.4` = next engine branch (LAW 0).
- Retell-HOSTED agents (live V7.9 etc.) are separate surfaces — model changes there need explicit owner instruction (LAW 6).
- Paid lesson (2026-09-22): `agent/llm.json` said `gpt-5.2` while the .env ran `gpt-5.4` — an agent misreported the test model from the dead field. Langfuse trace `observations[].model` is the ground truth for "what model ran".

## VOICE LAW — ELEVENLABS DEFAULT (owner, 2026-09-28)

**Default = ElevenLabs.** Cartesia is ONLY for HIPAA-related stuff or lower-quality deployments (and tests).

**PRODUCTION voice = Hannah** ("All-American" `ZSNL4hPqCnqoMPaI4jGX`, EL account):
```
TTS_PROVIDER=elevenlabs
ELEVENLABS_MODEL_ID=eleven_turbo_v2_5
ELEVENLABS_VOICE_ID=ZSNL4hPqCnqoMPaI4jGX
ELEVENLABS_SPEED=1.0
ELEVENLABS_STABILITY=0.6
ELEVENLABS_STYLE=1.0
```
plus a PLAYBACK-SIDE accelerator on the browser / voice streaming socket — a py
accelerator (time-stretch on the audio out path) pushing effective speed to
**1.08–1.15** (EL API hard-rejects generation speed >1.2 on turbo_v2_5, so the
accel lives on playback, not in voice_settings). Generation-side per-state
speeds already exist and are tested: `engine/diallux/media/delivery.py`
(per-state speed/stability/style table + documented provider ranges) and
`engine/tests/test_delivery.py`. The py playback accelerator = planned prod
work; do not lose the 1.08–1.15 target.

**TEST voices = Sarah** (`uG1JFy6xppqckhHCs2KG`, turbo_v2_5, speed 1.06/stability 0.5/style 1.0/similarity 0.75) — what every T4 battery runs today. Keep for tests.

**Cartesia rollback config (kept for HIPAA / low-quality deployments/tests):**
```
TTS_PROVIDER=cartesia
CARTESIA_MODEL_ID=sonic-3.6-2026-08-27     # ← THE pin. Dated snapshot, NOT the rolling alias
CARTESIA_VOICE_ID=829ccd10-f8b3-43cd-b8a0-4aeaa81f3b30   # Linda (public stock, "Conversational Guide", en-US feminine)
CARTESIA_SPEED=1.12
```
Ear verdict corrected (owner 2026-09-28): the old "much better than EL" call was made against `sonic-3.6`, NOT the actual model in use (sonic-3.6-2026-08-27) — on the real current model that voice is acceptable, BUT **EL blows it out of the water every time**.

- **Paid lesson (2026-09-23, still standing):** the iter66 EL cutover env rebuild DROPPED `CARTESIA_MODEL_ID` from `engine/.env` → code default fell back to the rolling `sonic-3.6` alias → different model build, different delivery on every call. ANY env-file edit that touches TTS keys MUST preserve the dated `CARTESIA_MODEL_ID` pin.
- Per-state delivery profiles (`engine/diallux/media/delivery.py`: speed/stability/style per state) are part of the sound — unchanged, do not "simplify" them.
- Verify what a lane actually runs: `journalctl --user -u diallux-<port>.service | grep "connected"` — prints `elevenlabs connected (model=… voice=…)` or `cartesia connected (model=…)`. Ground truth for the voice, same as Langfuse for the model.

## Naming traps (paid for in blood)

- `engine/` IS the old typo dir `dialux-langgraph-production-v5` (the live one). The
  correctly-spelled dir was the STALE twin — now `_cold_archive/diallux-twin-stale-correct-spelling.tar`.
- `retell/` here = Retell config lines, NOT the Retell company. `retell/sdr/current/` = V7.9.
- Old `Dialux_SDR/` path no longer exists — MIGRATION_MAP.md translates every legacy path.
