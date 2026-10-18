# plan_v5_iter92c — Worktree & branch audit @ b572cb9: what to merge, what to keep branched (analysis, ZERO code changes)

## Meta
- Date: 2026-10-05
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland (this box, `julio` @ 46.62.233.228). ALL repo ops ssh-wrapped to OREGON:
  ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'
- Numbering law: NO new engine number. This is an ANALYSIS session riding the iter92 line
  (suffix c). ZERO code changes, ZERO merges executed — this session produces the
  merge/keep verdict TABLE; every merge/delete decision belongs to the owner.
- Scope: inventory ALL worktrees + engine branches on BOTH boxes, diff each against
  main, classify merge-now / keep-branched / stale-cleanup, write the verdict, ASK JULIO.
- Status: **EXECUTED 2026-10-05** — S1+S2+S3 landed on main (execution record at the end of the "Verdict + MERGE PLAN" section). Owner said GO in-session; every gate ran.

## Compaction Context (from the 2026-10-05 iter92b session — carry verbatim)
- iter92b EXECUTED COMPLETE (plan /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter92b_4gk_cache_quant.md):
  lane /tmp/opencode/wt-92 on OREGON (branch engine/92-92b-4gk-quant @ 2b3e900, created by
  scripts/new_lane.sh 92 2b3e900 92b-4gk-quant — numeric-law: iter arg must be numeric), 4 GK mic
  calls (Sam/Priya/Dave/Bianca, 100 rounds), ledger run `iter92b-4gk-quant` (84 sops rows +
  100 rounds + 153 rag spans in /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db),
  evidence /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92b-4gk-quant/{01_raw_tables,02_quant_report,03_sop_report}.md.
  Verdict: CONFIRMS iter92 cache verdict; e2e gate marginal miss (STT/EOT-driven); findings F-92b-1..5.
- Findings NOT yet filed (discussed in-chat only, must land in iter92c evidence or PENDING_TASKS):
  F-92b-6 = iter87 reference ran on HELSINKI lanes (ports 8047/8048 not on OR) = cross-box gate;
  F-92b-7 = promoted warm/dest-cap tier (b250-class via iter91 pack) costs ~+90–115 ms vs b0
  (iter90 ledger: iter90-mic-b0 p50 765 vs iter90-mic-b250 p50 880); F-92b-7b = iter92b repaid-model
  gap refinements (uncached-history suffix term, /3.3 tokenization).
- SAVAGE LATENCY committed to main @ b572cb9: /home/julio/projects/clean_diallux_SDR/scripts/savage_latency/
  {README.md,cache_abort_probe.py,warm_race_audit.py} — "cancel, don't wait" playbox, adoption PARKED
  by owner ("we will adopt a bit later, I want to test what we have first").
- CACHE_ANALYSIS.md iter92b quant section committed @ 057635f (pushed by this agent from OR wt-main-docs,
  pulled+ff-merged FI). Owner committed the iter92b plan @ 77387ed (FI→main).
- main tip on BOTH boxes after this session: b572cb9 (git -C ... log --oneline -1 to verify).
- open merge decision ALREADY on record: iter89 (30405ad) + iter91 (2b3e900) MERGE still pending
  owner say-so (carried from iter91 session files).
- Known parked merge candidate from AGENTS.md: engine/iter77-twilio-iter70 @ 0394a3b (parked merge-ready).
- wt-92 branch engine/92-92b-4gk-quant has ZERO commits on it (lane created but no code changes);
  its only artifacts are gitignored research files → candidate for worktree-removal AFTER verdict.
- Session errors on record (do not repeat): pytest with exported env secrets = FORBIDDEN; envs are
  GENERATED per lane (scripts/new_lane.sh), never copied between lanes; live_sql.py import must use
  the ROOT copy /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py (has the micbridge trace
  filter) — the engine worktree copy does NOT; OREGON main checkout NEVER checkout/switch/reset/pull;
  all edits/commits/pushes via /tmp/opencode/wt-main-docs (OR), push with
  -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'; Finland
  fetch must go through the MAIN checkout path (worktree fetch hits gh-creds 'Not a directory') then
  ff-merge wt-main-docs: git -C /home/julio/projects/clean_diallux_SDR fetch origin
  'refs/heads/main:refs/remotes/origin/main' && git -C /tmp/opencode/wt-main-docs merge --ff-only origin/main.
- NO sqlite3 CLI on either box — read ledger via .venv python: /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -c "import sqlite3; ..."
- Numbers that matter for the assessment (all already in git or ledger, no re-computation needed):
  493 collected / 0 failed / 3 skipped suite state at 2b3e900; gk-iter89 (f7a37c3) and chat-iter88-live
  never judged by SOP rows (iter92b 03_sop_report is the FIRST GK judgment audit).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Analysis session, ZERO merges/cleanups executed | merge/delete = owner trigger words under LAW 0; this session produces ONLY the verdict table |
| Rides iter92 suffix c (no new engine number) | numbering law: no engine/diallux code change here |
| Inventory BOTH boxes' /tmp/opencode/wt-* + all engine/* branch heads | worktrees drift per box; GitHub refs are the merge truth |
| Use scripts/git-tree.sh (OR main checkout, run-only) | existing tool builds the branch topology safely; never hand-edit GIT_TREE.md |
| Merge-conflict dry-run via `git merge-tree` per candidate branch | no checkout, no mutation, predicts conflicts before owner says go |
| Verdict = one table, 3 labels: MERGE-NOW / KEEP-BRANCHED / CLEANUP | keeps the owner decision binary-able |
| Evidence lands in /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92c-worktree-merge/ (gitignored), verdict summary committed INTO this plan file | one plan = one session; plan file = durable record |
| Ends with ASK JULIO (merge list approval + cleanup list approval) | LAW 0 |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| iter87 merge state (wt-merge87 purpose/completeness) | T0 inspects /tmp/opencode/wt-merge87 (OR) + /home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-prewarm-hold/03_merge_validation_sop_audit.md |
| Whether any engine branch carries unpushed (local-only) commits | T1 `git log --oneline origin/<branch>..<branch>` equivalent per ref |
| NextSteps/ledger pointers for verdict | confirmed paths pinned in Compaction Context; no unknowns remain |

## Environment & Dependencies
- Boxes: OREGON 5.78.83.174 (root, key /home/julio/.ssh/id_ed25519_hetznor — ssh from FI) = source of truth; FI 46.62.233.228 (this session) = reads/analysis.
- Repo main checkouts: FI /home/julio/projects/clean_diallux_SDR · OR same path (read-only by law).
- Docs worktrees: FI /tmp/opencode/wt-main-docs · OR /tmp/opencode/wt-main-docs.
- venv for any python: /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python (NEVER bin/pip).
- Tools used: git (both boxes), scripts/git-tree.sh (OR), scripts/keyhound (both). No new deps.
- Ports/services: NONE needed (no lanes, no calls this session).

## Architecture (what this session changes)


## File Map
| File (absolute path) | What | New/Edit |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter92c_worktree_merge_assess.md | THIS plan + verdict summary appended at end (status→EXECUTED) | NEW (docs→main) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92c-worktree-merge/01_inventory.md | raw inventory both boxes | NEW (gitignored) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92c-worktree-merge/02_branch_analysis.md | per-branch diff/conflict tables | NEW (gitignored) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92c-worktree-merge/03_verdict.md | MERGE/KEEP/CLEANUP verdict + F-92b-6/7 filing | NEW (gitignored) |
| /home/julio/projects/clean_diallux_SDR/GIT_TREE.md | regenerated by scripts/git-tree.sh if owner approves any branch tag change | NO EDIT this session |

## Deploy Rules
- NO code changes, NO merges, NO worktree removals, NO branch deletes — those are owner words.
- OR main checkout: NEVER checkout/switch/reset/pull. All git writes via /tmp/opencode/wt-main-docs.
- scripts/git-tree.sh: run ONLY, for the topology picture (it regenerates GIT_TREE.md — commit it
  ONLY IF the topology changed due to an OWNER-approved action; in this session: run for picture,
  DO NOT commit unless changed by owner action).
- keyhound before any push; FI sync = fetch via main path + ff-merge wt-main-docs (exact commands
  in Compaction Context).
-Lane discipline: no lane this session; if a lane were needed, scripts/new_lane.sh only (enum: numeric iter, slug carries suffix).

## Tasks (in order)

### T0 — Inventory (both boxes)
Goal: full census of worktrees + engine branches with heads, dates, dirty state.
Commands (FI, local):
- git -C /home/julio/projects/clean_diallux_SDR log --oneline -1
- git -C /home/julio/projects/clean_diallux_SDR worktree list
- ls /tmp/opencode/ | grep wt- ; for w in /tmp/opencode/wt-*; do echo == $w; git -C $w status --short | head -5; git -C $w log --oneline -1; done
Commands (OR, ssh-wrapped): same two loops + scripts/git-tree.sh run for the topology picture
- ssh … 'cd /home/julio/projects/clean_diallux_SDR && bash scripts/git-tree.sh' (output captured into 01_inventory.md; do NOT commit GIT_TREE.md unless it reflects an owner-approved change)
Verification: 01_inventory.md contains both boxes' worktree tables + branch → head SHA → last-commit-date
mapping for every engine/* ref (git -C /home/julio/projects/clean_diallux_SDR for-each-ref 'refs/heads/engine/*' --format='%(refname) %(objectname) %(creatordate)').

### T1 — Branch analysis (merge candidates vs main)
Goal: per engine branch: commits ahead of main, files touched, conflict forecast, freshness.
Commands (OR, ssh-wrapped; for B in each engine/* ref found in T0):
- git -C /home/julio/projects/clean_diallux_SDR log --oneline main..$B | head -20
- git -C /home/julio/projects/clean_diallux_SDR diff --stat $(git -C /home/julio/projects/clean_diallux_SDR merge-base main $B)..$B | tail -5
- git -C /home/julio/projects/clean_diallux_SDR merge-tree --write-tree main $B 2>&1 | head -5   # conflict forecast, no mutation
- stale-check: git -C /home/julio/projects/clean_diallux_SDR branch --merged main | grep $B   (no unique commits → CLEANUP candidate)
Special focus: engine/iter89 (expect 30405ad), engine/iter91 (expect 2b3e900), engine/iter77-twilio-iter70
(0394a3b), iter87 merge state via /tmp/opencode/wt-merge87 + research/surgeon/iter87-prewarm-hold/03_merge_validation_sop_audit.md,
engine/92-92b-4gk-quant (expect ZERO unique commits → cleanup candidate).
Verification: 02_branch_analysis.md has one block per branch with the 4 command outputs + a 1-line read.

### T2 — Verdict (merge / keep / cleanup)
Goal: the owner decision table.
- Classify every branch+worktree: MERGE-NOW (owner pre-authorized pending, e.g. iter89+iter91),
  KEEP-BRANCHED (unique value, not approved, or awaiting merge pairing), CLEANUP (no unique commits,
  dead worktree, superseded).
- Cross-check research/surgeon/iter92c-worktree-merge/03_verdict.md against:
  - iter91 files (iter89+91 merge pending say-so)
  - iter78 yield/iter85 fix branches (engine/iter85-eager-hold @ 542d3e8 per AGENTS.md NEXT-UP context)
  - the deep-clean law: worktree removal list goes to owner, agent NEVER removes.
- File the two unfiled findings (F-92b-6 cross-box reference, F-92b-7 warm tier cost) in 03_verdict.md
  appendix so they survive the session.
Verification: every known branch appears exactly once in the verdict table with a label + evidence line.

### T3 — Commit + sync + ASK
Goal: durable, readable-for-a-fresh-agent record; owner asked.
- Append verdict summary (the table + the two findings + the ASK items) to THIS plan file
  (section '## Verdict (iter92c, filled 2026-10-05)'), status→ EXECUTED.
- Commit via OR: ssh … 'cd /tmp/opencode/wt-main-docs && cp <FI plan contents — scp from FI> …' (scp FI→OR plan file first, then commit+push with the gh-creds helper; keyhound first).
- FI sync back: fetch via MAIN checkout path + ff-merge wt-main-docs (commands in Compaction Context).
- scp evidence 01/02/03 BOTH ways + md5sum checksum both sides.
- ASK JULIO (1) approve MERGE-NOW list (2) approve CLEANUP list incl. wt-92 removal (3) count iter89+91
  pair authorization still open (4) confirm iter93 agenda = savage adoption A/B first or merges first.
Verification: main has the plan commit with inline verdict; boxes checksum-equal; owner answered in-chat.

## Validation Plan (end-to-end)
T0 census complete (both boxes) → T1 per-branch blocks + conflict forecasts → T2 verdict table with
zero unknowns left in BLOCKED → T3 plan committed with inline verdict + boxes synced + owner asked.
ZERO code/merge/cleanup actions executed anywhere.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Actual merges (incl iter89+91 pair) | owner say-so = the trigger; iter93 planning follows the verdict |
| savage_latency adoption A/B (warm cap, spec abort, RAG placement) | owner: "adopt later, test what we have first" — iter93 candidate queue |
| /opt restart, /opt cutover work | unchanged pending backlog |
| PENDING_TASKS.md PT-rows for F-92b-1..7 | only AFTER owner accepts the findings (folded into T3's ASK) |

## savage_latency carry (committed main @ b572cb9 — reference for the merge/keep assessment)
- What it is: /home/julio/projects/clean_diallux_SDR/scripts/savage_latency/{README.md,cache_abort_probe.py,warm_race_audit.py} — the
  "cancel, don't wait" playbox (savage latency engineering): one OpenAI stream per key per moment;
  abort completes, keep the prefill cache; never queue behind a warm/spec zombie.
- Proof on record (README carries it): live A/B cache_abort_probe — cold 1421 ms vs hit 914 vs
  post-abort 857 = cache survives a mid-stream kill; warm_race_audit on the iter92b log:
  169 awaits = 163 already_done + 6 lost races (1,218–2,324 ms of the 2,500 cap);
  slow-TTFT rounds proved NOT cache misses (multi-stream collisions instead).
- Files under assessment in iter92c: scripts/ root — residence on main decided @ b572cb9, KEEP.
- Adoption: PARKED by owner — iter93 candidate queue order pinned in the README's adoption gate:
  (1) warm cancel-not-wait cap ~300–400 ms, (2) eager spec client-abort (evaluate harder:
  iter78b re-ask edge cases, provider abort semantics, resume_pending interplay),
  (3) RAG off hot path, (4) process split (skipped: ~50–100 ms benefit, rewrite-grade risk).
- Findings feeding it (file at T2): F-92b-7 warm/dest-cap tier ~+90–115 ms vs b0 (iter90 ledger
  iter90-mic-b0 765 / iter90-mic-b250 880); only 4 slow-TTFT rounds in 100 all Bianca-collision-class;
  spec-concurrency tax +17–111 ms on dup rounds.

## Verdict + MERGE PLAN (iter92c, appended live 2026-10-05, owner-approved in-chat)

> **Status: SAVED — nothing executed. All git writes still need owner trigger words (LAW 0).**
> Facts verified in-session: fold 730dfdb = merge(50ecbaa ← main, 02eb2ac ← iter87) done ON THE
> BRANCH side 2026-09-30 as the owner-say-so'd REHEARSAL ("Real_MVP"); it is NOT in main.
> main's drift since 50ecbaa = docs/savage_latency only → forecasts clean (old-style merge-tree,
> 0 conflicts). iter86 (d158b4c) is a SIBLING leaf cut from 85's tip: its ONLY content is
> engine/scripts/call_forensics.py (analysis SDK, no engine code) and it is NOT inside iter91's
> tree despite the fold's message claiming it. Parentage: 85→{86 sibling, 87→fold→89→91}.
> Ledger cross-check result: the adopt-after-false-start race NEVER had a fix (ledger scan
> before F-92c-1/F-92c-2 landed: no prior fix row; fix = pending branch below). Deep scan:
> the ONLY commit to touch the hold/adopt region in the whole 85→91 stack is iter85's own
> 542d3e8 ("adopt now unconditional — hold makes rerun moot") — the release stayed GUARDED
> (`if _eager_held and gate`), so the race exists since iter85's first implementation.
> The deprecated iter86 plan itself flagged "FIX-1's single gate hold" as fragile
> (plan_v5_iter86 line 130/136). Batteries never hit it (driver speaks in clean gaps;
> no mid-utterance resume). Every fix collaborator lives in the iter92c lane evidence.

### The staged landing (S1 → S2 → S3, one gate each, all on OREGON via wt-main-docs)

| Stage | Action | Verified forecast | Gate |
|---|---|---|---|
| S1 | `git merge --no-ff 730dfdb` → main (lands iter80-87 chain + fold-resolved conflicts) | 0 conflicts vs live main | engine suite on main; red → STOP |
| S2 | `git cherry-pick d158b4c` → main (86's forensics SDK, 1 file) | 0 conflicts (base 542d3e8) | suite still green |
| S3 | `git merge --no-ff 2b3e900` → main (89 prompt edits + 91 pack; ~4 new commits post-S1) | 0 conflicts (same base 50ecbaa) | suite; then tag `engine/iter91`, `scripts/git-tree.sh`, ITERATIONS + registry line (law 8), keyhound, push, FI fetch+ff sync |

- NEVER executed mid-session: no rebase/squash/force (owner: "no squashing"), no /opt edits,
  prod deploy untouched; /opt needs `TTS_DELIVERY_PROFILES=false` ONLY at cutover (owner word).
- Cleanup AFTER S3 (separate owner say-so, one by one): `wt-92` + `engine/92-92b-4gk-quant`
  (pointer twin of 91, zero own commits), `wt-merge87` (detached staging), wt-91 rebuilt lane.
- SEPARATE asks kept out of scope: `engine/iter77-twilio-iter70` @ 8c5f72f (parked merge-ready,
  its own decision), EL/GitHub key rotation review.

### Fix branch AFTER the landing (owner ordered: fix-before-Twilio)
- Race = `_eager_held` cleared by false-start discard ⇒ adopt skips `gate.release()` ⇒ reply
  never spoken (FIND-35, trace a6f7c585a68f, lane sid 3f8773ff173b; headphones ⇒ FIND-32 echo
  ruled OUT). Same machinery serves Twilio — production callers pause mid-sentence = it WILL bite.
- Plan: cut `engine/iter92-fix-held-adopt` (name per owner) off the landed tip: adopt path
  delivers even when `_eager_held` was cleared (or held-state derives from the gate; force flush
  on adopt) + pin test + live lane replay of the fragment-interrupted pattern. Optional same
  branch (owner pick): F-92c-2 STT-confidence repair reply ("can you repeat that?").
- verdict table for branch census T2 → labels replaced by THIS plan (supersedes).

### GitHub exposure closure (executed 2026-10-05, owner-ordered)
+ Private NOW (owner PATCH call, HTTP 200 ×6): diallux-sdr-iter89, diallux-voice-engine-iter86,
  diallux_sdr_almost_there, dialux-sdr-langgraph-v5, state_machine_voice, scope-test-nonexistent.
  Still PUBLIC by choice (deploy pipelines may rely): diallux_sitio_espanol, leasing-tenant-scorer,
  MLOs_scrape, PDF-parser-for-property-radar, site-scan-project, Video_repurpose, bajio-relocate,
  clean-template-site-scan, despacho-contable-mx. Rotation review of OpenAI/Deepgram/EL tokens
  queued (full repos sat public Sep-25 → Oct-05).

### EXECUTION RECORD (filled 2026-10-05, after owner GO — all four gates ran)
| Step | Commit | Content | Gate result |
|---|---|---|---|
| S1 | `a10eec4` | `--no-ff 730dfdb` — iter80-87 chain incl. pre-resolved fold | suite: 1 fail = test_iter44 dead-store 401 (known S1-era hermeticity gap; its cure rides S3 — verified on 2b3e900 tip) |
| S2 | `a546454` | cherry-pick `d158b4c` — call_forensics.py (498 lines, single file) | (no separate gate — SDK-only, 0-conflict forecast held) |
| S3 | `6d9f277` | `--no-ff 2b3e900` — iter89+91 tail; PENDING_TASKS.md doc-union conflict resolved (PT-74 widened row kept, main's 10-03 section kept) | tree proof: `git diff main 2b3e900 -- engine/` = ONLY .env.example truth-fix + call_forensics.py; suite: **490 passed / 3 skipped / 0 failed** (88s) |
| close-out | `f20bcc1` / `1739e69` / `9369f39` | env audit → ONE mangle found+fixed (.env.example TTS_DELIVERY_PROFILES true→false; the 58fe765 insert had been a silent no-op); env values verified vs register on ALL planes (code defaults ALL MATCH, canonical env clean, lane clean); tag `engine/iter91` @ `6d9f277`; GIT_TREE regenerated; ITERATIONS S1-S3 line; PT-80 → DONE @ 87730db; registry rebuilt (6883 commits, main @ 9369f39) | keyhound: push-diff scan 0 key-shaped strings (259 standing hits = legacy services/* contamination, pre-existing state); pushed main + tag; FI synced (tags + ff to 9369f39) |

- NOT executed (unchanged, owner words pending): cleanup deletions (wt-92, 92-92b pointer, wt-merge87, wt-91 lane), iter77 merge, /opt changes, fix branch `engine/92-fix-held-adopt` (cut AFTER cleanup decisions or immediately on word).
