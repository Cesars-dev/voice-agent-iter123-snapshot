# plan_v5_iter91b — savage-cancel LADDER ASSESS (zero-code): owner research as truth + solution palette → one pick with FEWEST ITERATIONS → cross-ref vs `scripts/savage_latency/README.md`

## Meta
- Date: 2026-10-05
- Session box: **Finland** (julio @ 46.62.233.228). All repo git ops ssh-wrapped to OREGON:
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'`
- Project root (OREGON source of truth): `/home/julio/projects/clean_diallux_SDR`
- FI checkout: `/home/julio/projects/clean_diallux_SDR` (docs edits happen HERE when owner says so in-session; commits/pushes via OREGON `/tmp/opencode/wt-main-docs`)
- Scope: **ASSESS ONLY — ZERO engine code, ZERO lanes booted, ZERO batteries.** Produce: (1) the proposed-solutions palette, (2) a fresh READ of the owner's internet research as the main source of truth, (3) an adaptability matrix vs the CURRENT CODE (iter91 tip 2b3e900 / main 1c132e1) scored for FEWEST ITERATIONS, (4) a cross-reference against the savage-AI-engineering doc (`scripts/savage_latency/README.md` — releasing/canceling/suppressing LLM calls to gain latency and keep cache), (5) ONE verdict = the recommended execution ladder.
- Numbering/name law: assess-only, zero `engine/diallux/` code → ZERO-CODE RULE (AGENTS.md): carries the LAST CUT CODE iter = **iter91** (tag `engine/iter91` @ 6d9f277; the 92/92b/92c bare names were the tolerated-once drift, never repeated; **iter93** is minted for the pending FIX code branch — NOT this session). Suffix letter → **iter91b** (first ride after iter91 closed).
- Status: **EXECUTED (2026-10-05)** — verdict:
  `research/surgeon/iter91b-savage-cancel-assess/04_verdict.md` (gitignored evidence
  dir; ladder = iter93 B+ epoch discipline → savage warm abort cap → PT-81 same-state
  warm → PORT-list remainder). Owner research input: FIND35_TURN_ENGINE_RACE_DIAGNOSIS.md
  (Mac ~/vps-inbox, mutagen-synced FI copy /home/julio/projects/vps-inbox/) — folded in
  as the T1 truth refresh. PT-83 registered. Adoption parked at owner (LAW 0).

## Compaction Context (carry verbatim — the iter93 planning session, 2026-10-05, FI)

### Landed state
- main = origin/main = **1c132e1** (plan iter93 doc — docs-only). Tag `engine/iter91` @ **6d9f277**.
  Engine code byte-equal to `engine/iter91-promote-pack-defaults` @ **2b3e900** through merge S3.
  Both boxes synced. Suite on main: 490 passed / 3 skipped / 0 failed.
- **CRITICAL read-only gotcha:** the FROZEN OREGON main checkout
  (`/home/julio/projects/clean_diallux_SDR` on 5.78.83.174) is parked on branch
  `engine/iter73-oregon-wip-20260924` with a STALE working tree — its session.py has NO
  `_eager_held`. ALL code reads for real iter91-tip files come from OREGON
  `/tmp/opencode/wt-main-docs/engine/…` (or FI checkout, synced). Never trust the frozen
  checkout files; its refs are current, its FILES are not.
- Lane RUNNING: `wt-iter91` @ 2b3e900 on 127.0.0.1:8049, pid 1471973, log `/tmp/opencode/lane-8049.log`,
  Hannah EL pure-globals env, VOICE_TEST_TOKEN fail-closed gate.
- iter93 plan (`/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter93_held_adopt_race_fix.md`)
  is on main, awaits owner T0 HITL (variant A/B/C for FIND-35; F-92c-2 scope). This session
  FOLLOWS it (does not replace it): iter91b's verdict feeds the owner's T0 answers.

### FIND-35 race anatomy (VERIFIED against wt-main-docs code, exact lines)
- Hold: `session.py:794-799` `self._eager_held = bool(clock.extra.get("eager")) and bool(eager_hold_audio_until_confirm)` → `gate.hold()`.
- Adopt release GUARDED: `session.py:477-490` `if getattr(self,"_eager_held",False) and self.gate:` → `gate.release()`.
- Resume discard: `session.py:638-653` clears `_eager_held` + `gate.discard()`.
- Orphan path 1 (discard-cleared-flag): resume clears flag → EOT ADOPTS (task-not-done, eager flag still set — the awaited `discard()` yields between branches) → guard False → NO release → reply generated, never spoken (owner trace: 2× false-start discard held 1500/1300 ms + adopt at 48.947s without release log).
- Orphan path 2 (parked-final): LLM finishes before TurnResumed → `_run_turn`'s `end_of_turn()` wakes the final (`_held_final=True`) → resume guard `not task.done()` FAILS → no discard, audio stranded.
- Gate hold primitives: `/tmp/opencode/wt-main-docs/engine/diallux/media/sentence_gate.py:52-95` `hold()/release()/discard()`; add() buffers-only while held:66.
- Variants on the table: **A** = unconditional adopt flush only; **B** = A + turn-id-keyed gate ops (held-state lives in the gate keyed by turn_id); **C** = B + confidence-band repair (F-92c-2 = research FIX 3).

### The savage-AI-engineering doc (the cross-reference target)
- Path: `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/README.md` (landed main @ b572cb9 — "cancel-dont-wait playbox"; ADOPTION PARKED by owner 2026-10-05: "test what we have first"; a copy sits at `/tmp/opencode/savage_README.md`).
- Companion scripts: `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/cache_abort_probe.py`, `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/warm_race_audit.py`.
- Principle: **at most ONE OpenAI stream per key per moment. Cancel; never queue; never wait.** Mid-completion warm b → abort it; the prefix cache it wrote at PREFILL survives server-side (Proof 1: after-abort ttft 857 ≈ hit-class 914 vs cold 1421; n=1 per condition). Proof 2 (iter92b 4-GK battery audit): 169 awaits → 163 already_done (96%), 6 lost races waited 1,218-2,324 ms of the 2,500 cap; waits sit in the S→L window, NOT in TTFT (post-race rounds ran 710-957 ms on-grid cache). Slow TTFT rows (≥1,800 ms) = 3-stream collisions (spec+real+warm on one key), NOT cache misses.
- Measured cost table (in the README): dest-cap wait tier +90-115 ms (iter90 A/B mic-b0 765 vs mic-b250 880); lost races 1.2-2.4s × 4%; RAG on hot path 85-131 ms/round S→L; provider drift ±50 ms.
- Reference-contamination caveat (F-92b-6): the iter87 reference battery (853/1376) ran on HELSINKI lanes — cross-box vs OREGON numbers.

### Owner research = MAIN SOURCE OF TRUTH (fresh internet pull, z.ai big-gun)
- FI copy: `/home/julio/projects/chat_z_scraper/outputs/turn_taking_failure_mechanisms_analysis/turn_taking_failure_mechanisms_analysis_clean.md` (+ sibling `turn_taking_failure_mechanisms_analysis_full.json`; mac copy: `/Users/Cesar_1/Desktop/Dialux Lang graph/ma-transcripts/` via sshfs `/home/julio/mac_root/Desktop/Dialux Lang graph/ma-transcripts/`).
- Pull date: 2026-10-05 08:39. It contains: the PLATFORM MECHANISM MATRIX F1-F6 × (Vapi | Retell | our seam | knobs) (clean.md ~line 3668); the 10-mechanism dossiers + turn-ownership map (Q6) + PORT LIST "smallest-change-first, env-knob-first, one variable each" + "what we could NOT verify" (~line 3777-3795); Implementation-grade FIX 1-8 with knob registry + per-fix acceptance criteria + Appendix C "what we deliberately did NOT port" (~line 4581+).
- Known FIX-landed overlap (do NOT re-derive): FIX 2 reminder-ladder → landed iter91 (ladder reminder/8000/1); FIX 5 post-interrupt-backoff → landed (1000 ms); FIX 1 = the iter85/held feature itself (the disease container); FIX 3 = F-92c-2 candidate (confidence bands, STT_CONFIDENCE_FLOOR/CEIL, default OFF, log-first).
- Public repo on record: `github.com/Cesars-dev/dialux-mic-bridge` (README has the race spec).

### Other on-record (do not redo)
- iter92 verdict: cache floors = provider 1024-block quantization, NO regression; cost = replaced-delta re-bill.
- findable PTs: PT-74/75/76/77/79/81 open; PT-80 DONE; **PT-82 is reserved for the iter93 fix landing** — this session registers PT-83 (and only PT-83).
- Both boxes have NO sqlite3 CLI — read DBs via engine venv python. Ledger (findings): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Assess-only; ZERO code/lanes/batteries this session | owner: "this will be an assess only plan" |
| Name = iter91b (suffix ride on last CUT CODE iter 91; NOT iter94, NOT iter93-suffixed) | zero-code rule; iter93 name belongs to the pending FIX branch; 92-series drift "tolerated once, do not repeat" |
| Owner research file = main source of truth for mechanism claims | owner: "fresh pulled data from the internet" — agents must re-read it fresh, cite section headers, never argue from memory |
| Current-code truth = wt-main-docs @ 2b3e900 (NOT the frozen checkout files) | FIRST-REP Fly session proved the frozen checkout files are stale at the 73-wip tree |
| Scoring axis = FEWEST ITERATIONS to a merged fix (count of code branches + batteries) | owner: "pick whatever adapts best with my code with less iterations" |
| Cross-reference target = `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/README.md` (cancel/abort/suppress prewarm streams; cache survives abort) | owner: "we are releasing/canceling/suppressing llm calls to gain latency and keep cache" |
| Output = ONE verdict ladder proposal; iter93 stays the code vehicle; adoption = owner say-so | LAW 0; nothing merges/adopts without owner |
| savage README adoption stays PARKED inside this assessment (assess, not flip) | owner 2026-10-05 parking call stands until verdict |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Any NEW research beyond the 2026-10-05 08:39 pull (did the owner fetch more since?) | T1 HITL ask: "is the pull still the whole truth, or is there a newer export?" |
| Confidence-field semantics on FLUX mode (needed to grade FIX 3 feasibility) | UNKNOWN until the iter93 T1 raw TurnInfo dump — iter91b grades FIX 3 as "feasible per research, semantics unverified" |
| Savage abort-topology wiring truth (where abort hooks into llm.py warm paths) | code read at T2 on wt-main-docs; the README already names the states (completed/mid-completion/pre-inflight) |
| Final ladder pick | T4 — ASK JULIO (HITL); agent may mark a recommended pick but never starts it |

## Environment & Dependencies
- Python venv (any engine-side run): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (NO bin/pip).
- Git (FI): `/home/julio/projects/clean_diallux_SDR` direct for read; writes to main only via OREGON `/tmp/opencode/wt-main-docs` (push with `-c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'`; keyhound + diff-scoped scan of the to-be-pushed content before every push — the standing 259-hit noise is legacy `services/*`; only the NEW diff must be 0 key-shaped strings).
- Docs to read (all absolute, FI-local synced copies):
  1. `/home/julio/projects/chat_z_scraper/outputs/turn_taking_failure_mechanisms_analysis/turn_taking_failure_mechanisms_analysis_clean.md` — owner research (TRUTH SOURCE), target sections: lines ~3668 (F1-F6 matrix), ~3677 (PORT LIST), ~3777-3795 (mechanism dossiers + not-verified), ~4581-4659 (FIX 1-8 + knob registry + acceptance criteria + Appendix C not-ported).
  2. `/home/julio/projects/clean_diallux_SDR/scripts/savage_latency/README.md` — savage cross-reference (fetch via OREGON: `git show main:scripts/savage_latency/README.md` or read from `/tmp/opencode/wt-main-docs/scripts/savage_latency/README.md`).
  3. `/tmp/opencode/wt-main-docs/engine/diallux/media/session.py` + `sentence_gate.py` + `/tmp/opencode/wt-main-docs/engine/diallux/config.py` — the code truth for fit-scoring.
  4. `/tmp/opencode/wt-main-docs/engine/diallux/llm.py` (warm/prewarm paths) — savage-abort fit read.
  5. `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter93_held_adopt_race_fix.md` — the standing code-fix plan this verdict feeds.
  6. `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` — PT ledger (next free = PT-83).
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter91b-savage-cancel-assess/`
- Langfuse/ledger/registry imports: NOT required this session (no runs). Findings-table updates: allowed, additivity-only.

## Architecture (what this assessment produces — decision flow, not code)

```
 owner research (truth) ──► FIX-1..8 + F1-F6 + PORT LIST re-read
                                   │
 proposed solutions palette ───────┤
   S-1 race fix A/B/C (iter93)     │   adaptability matrix per candidate:
   S-2 savage cancel-dont-wait     ├──►  code-fit @ 2b3e900 · branches needed ·
   S-3 research PORT LIST rest     │      batteries needed · risk · savage-2-candidate
   S-4 harness-side (keepalive,    │      cross-ref verdict
        room tone, PT-79 probe)    │
   S-5 PT-81 same-state re-round   │
                                   ▼
                       FEWEST-ITERATIONS LADDER (ordered, costed)
                                   ▼
                        ASK JULIO (adoption/GO/shape)
```

## File Map
| File (absolute path) | What changes | New/Edit |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter91b_savage_cancel_assess.md` | THIS plan; status + verdict appended at end | NEW (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter91b-savage-cancel-assess/01_solutions_palette.md` | S-1..S-5 inventory: what each changes, exact files/lines, landing cost (steps+batteries), current status (landed/planned/parked) | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter91b-savage-cancel-assess/02_research_recheck.md` | Fresh read of the research pull: per-candidate section citations (F-row / FIX-n / acceptance criteria), deltas vs code-on-record, "could NOT verify" items listed | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter91b-savage-cancel-assess/03_matrix.md` | The adaptability matrix (candidate × branches × batteries × risk × savage-cross-ref × fewest-iterations score) | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter91b-savage-cancel-assess/04_verdict.md` | ONE recommended ladder + rejected orders + the HITL questions | NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-83 row (assessment verdict pending adoption) — PT-82 stays iter93's | EDIT (docs → main) |

## Deploy Rules
- NO service starts/stops; NO lane boots; NO git checkout/reset/pull on OREGON; NO /opt; NO booking-touching anything (no batteries).
- Docs commits (this plan + PT-83) land straight to main via OREGON wt-main-docs; evidence dir stays gitignored.
- Everything is read-only or md-file writes. Suite not needed (no code), but if any code file is mis-cited, re-cite from `git show` before believing the matrix.

## Tasks (in order)

### T1 — Research re-read (TRUTH REFRESH) + HITL freshness check
Goal: re-read the owner pull FRESH (sections listed in Environment §5) and produce `02_research_recheck.md`: for EVERY palette candidate, the exact supporting research row (F1-F6 matrix entry, FIX-n mechanism + acceptance criteria, "could NOT verify" caveats, Appendix-C not-ported) — quoting section + line number. Note every place the research ALREADY matched what we shipped (FIX 2/5 landed; FIX 1 = iter85 container) and every contradiction.
Ask owner (HITL, single question): "is the 08:39 pull still the whole truth, or is there a newer/side export to fold in?"
Verification: recheck file cites ≥1 research section per candidate; zero citations from memory (every claim has a line pointer and a short verbatim quote).
### T2 — Code-fit truth read (palette grounding)
Goal: for each candidate, exact fit vs wt-main-docs code @ 2b3e900: files/lines touched, knobs already present, tests to adapt. Verify savage abort-topology claims by reading `engine/diallux/llm.py` warm paths (are warms separate asyncio tasks on ONE OpenAI client/key? is abort a `.cancel()` on the task? does anything else await the warm beyond the saver?) — record REAL answers with line numbers, not the README's prose.
Verification: sources grounded on real files; every "the code does X in file.py:NN" verified by a direct read in the same session (frozen-checkout files FORBIDDEN as sources).
### T3 — Matrix (the deliverable)
Goal: `03_matrix.md` — one row per candidate: (a) research citation (T1), (b) code-fit cost: lines/files + new knobs + tests adapted (T2), (c) iteration cost: # code branches + # batteries to MERGED, (d) risk class (regression surface: gate/state machine = HIGH; knob-only = LOW), (e) savage cross-ref: does it cancel/abort/suppress a stream? does it respect one-stream-per-key? does it protect cache? honest YES/NO/PARTIAL with README line cites, (f) fewest-iterations score.
Rank into an ordered ladder; mark dependencies (e.g. C needs FIX-3 dump evidence from iter93 T1; S-5 needs PT-81 design).
Verification: matrix complete for S-1..S-5; every row has all 6 columns filled (UNKNOWN allowed but flagged in BLOCKED).
### T4 — Verdict + ASK JULIO
Goal: `04_verdict.md`: THE recommended ladder (fewest-iterations pick) + runner-up + rejected orders with reasons. Then present in-chat and ASK: (1) adopt the ladder as-is or reorder? (2) confirm iter93 T0 answers this verdict implies (A vs B; C in-scope?). NO code starts on any answer short of explicit owner GO.
Verification: verdict file exists; answer questions are ≤3, each with a default proposal so a one-word owner reply unblocks it.
### T5 — Land the docs (plan + PT-83) + close-out
Goal: commit plan + PT-83 row to main via OREGON wt-main-docs (docs law). Plan file gets "status → EXECUTED + verdict pointer" appended. Final state: assessment DONE, adoption parked at owner.
Commands (OREGON): `cd /tmp/opencode/wt-main-docs && git add plans/plan_v5_iter91b_savage_cancel_assess.md plans/PENDING_TASKS.md && git commit -m "plan iter91b: savage-cancel ladder assess EXECUTED - verdict-pointer + PT-83"` then keyhound + push + FI sync: `cd /home/julio/projects/clean_diallux_SDR && git fetch && git merge --ff-only origin/main` (FI side = pull from origin only, fast-forward).
Verification: main contains the plan commit; FI synced; no engine paths touched.

## Validation Plan (end-to-end)
T1 recheck cited-from-file → T2 code-truth grounded → T3 matrix complete → T4 verdict + ASK → T5 docs landed + FI/OR synced. Terminal state: owner holds a costed ladder and answers 2-3 one-liners; NOTHING merged, nothing adopted.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| IMPLEMENTING any position of the ladder (incl. iter93 branch cut) | code = its own session under LAW 0; this assess only ranks |
| Savage README adoption A/B battery | owner parked it; assess records the costs only |
| The diag/skill worktree-session stuff (worktree-diagram skill) | landed as a skill, not part of this plan |
| Langfuse/ledger imports, registry refresh | no runs this session; only findings-table additivity allowed |
| Findings corrections for F-92b-* rows | separate hygiene task, owner-ordered |
