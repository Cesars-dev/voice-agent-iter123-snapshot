# plan_v5_iter90_assess_rag_zero_and_first_name — the owner's 2-point main assessment (NO git actions): (1) why "last test on main" showed ZERO Intake RAG retrievals, (2) find the lost first_name attendee-fallback design (when was it allowed / did the iter89 prompt restructure miss it)

## Meta
- Date: 2026-10-02
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland/MainVps. ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Scope: ASSESSMENT ONLY (read the tree, the SQLite ledger, git history, plans/reports;
  NO code edits, NO config edits, NO branches, NO pushes/pulls of code). Docifacts
  (this plan, the verdict memo, PT rows) commit to LOCAL main per LAW 0 docs rule.
- Status: PLAN ONLY (not started — awaits approval)

## Compaction Context (iter89 session 2026-10-02 — carried verbatim)

**What iter89 landed (branch `engine/iter89-prompt-enhancements`, tip `30405ad`, pushed
to GitHub; NOT merged — awaiting owner say-so):**
- `697b3a0` Edit A: Phase 1 (Intake rework I-1..I-9 — mission, small-talk gate, THREE
  pain-points refer lanes: `surface pain recognition and opening discovery questions`
  / {{inbound_channel}}, `probing questions below the surface symptom` / {{interest_topic}},
  `emotional anchoring and empathic response` / {{pain_frame}}; Question Craft; Critical
  Rules rework), general G-A/G-B, K-1 call-context General Inbound rework, K-2 pain-points
  Trigger Questions insert, Discovery D-A/D-B + llm.json 9-state lockstep (6 synced) +
  test pins (iter43 widened to 9 states; iter25 ×3, iter48 ×2, iter49/59/60/63 wording pins
  — the plan-sanctioned class only).
- `5c4f94f` Edit B: general_prompt.md wholesale ← 01_general_prompt_FINAL.md (6,053 B,
  deployed 1,284 tokens exact, 9 markers ×1, zero {{var}}) + llm.json general mirror +
  _GENERAL_KBS order pin + 4 `## KNOWLEDGE` prose-collision wording pins.
- `a02192c` Edit C: Phase 2 [APPLY] (D-1..D-4, C-1..C-7, O-1..O-4, CT-1..CT-4,
  CS-1/CS-2, V-1/V-2, B-1/B-2, CL-1/CL-2, CL-3 SMS-safe: `<Thanks, {{first_name}}! You'll
  get a text with all the details — the day and the time.>`, I-10, C-8a strip amplification
  samples; V-3 SKIPPED, C-8b KEPT) + llm.json 9-state re-sync.
- `f7a37c3` CHERRY-PICK of iter76's `c1f2f1b`: harness auto-enables `--rag-fire-sim`
  under `--rag` when fire mode is hybrid (owner approved; harness-only, +20/−2 in
  `/tmp/opencode/wt-iter89/engine/tests/llm2llm/harness.py`; opt-out `--no-rag-fire-sim`).
- `30405ad` battery evidence report refresh.
- Suite on the branch: EXACTLY 3 stale reds —
  `tests/test_iter46_latency_floor.py::test_fast_first_flush_before_stream_end`;
  `tests/test_iter59_dedupe_semantic.py::test_semantic_threshold_config_defaults`;
  `tests/test_iter60_audit_fixes.py::test_turn_opening_reask_dropped_when_window_nonempty`.
  All three = old pins of behavior newer owner orders reversed (TTS_GATE_FAST_FIRST_FLUSH=false;
  TTS_DEDUPE_SEMANTIC=false; turn-opening change). Verified red on un-edited main line too

**GK battery evidence (run `gk-iter89` @ f7a37c3, ledger gk-iter89, 185 rounds, 147 rag spans):**
- Method: 5 sequential harness runs (async parallel caused silent zero-RAG — root cause
  below), graph transport, mock slots, --rag --langfuse, gpt-5.4 caller+agent, max-turns 48.
- First batch (parallel, NO --rag-fire-sim) showed rag_turns=0 on ALL 5 calls. The embedder
  race theory was DISPROVEN by a solo rerun (still 0). TRUE root cause: `--transport graph`
  never fires the session-layer lanes; `--rag-fire-sim` is that emulation (iter63). The
  iter76 auto-enable fix (`c1f2f1b` 2026-09-24) was parked on `engine/iter76-harness-firesim`
  and NEVER merged to main → every fresh battery from the main line re-discovers this
  ("last test on main proved ZERO rag retrievals on intake" = THE SAME artifact). With the
  cherry-pick + firesim, Boris proof: rag_turns=22, 18,883 chars; full 5-batch: Sam 42/32,960,
  Priya 21/23,137, Boris 22/18,883, Bianca 23/23,903, Dave 26/19,775 — zero-hit-free (PT-74
  fix verified on the branch).
- Results: Sam FAIL no-book (48-turn budget death), Priya 13/14 hire (1 pricing-leak RED:
  quoted "$697 a month" at Closer t10), Boris 13 (fast close, anti-promise held), Bianca 12,
  Dave 13 (cleanest). 4/5 booked. Per-turn chunk replay fragment:
  `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/` chunk tables.
- Sam autopsy (root cause): contact_details→ConfirmSlots edge in `agent/llm.json` requires
  TRUTHY `first_name` (edge `required` list). Sam declined a personal name; the agent stored
  "Ortiz Roofing" only as `company_name` (first_name absent from final dvs). Engine gate
  (`diallux/graph/tools.py` `_gate_check_edge`) blocked the transition ("first_name is empty"),
  while the prompt rule says "Never re-ask for a name, never loop the read-back" → prompt-vs-gate
  deadlock → 16 turns of "anything else to note?" loop → max-turns death, `ended=False`.
  OWNER's position: first_name-required was DESIGNED by him. The open question is whether the
  attendee-fallback design ("Capture whatever they answer as {{first_name}}" / declined-name
  handling) existed before, when, and whether the big prompt ressructure (iter89 Phase 3
  wholesale + Phase 1) lost it — REVISION: that fallback line lives in
  `/tmp/opencode/wt-iter89/engine/diallux/prompts/contact_details.md` §1 First name TODAY
  (verified present post-Edit-C) — so the prompt half survives; the SUSPECT half is the
  agent's actual behavior (stored company only) and whether an older mechanic (e.g.
  name→first_name coercion or a `[name_declined]` convention) ever existed in the gate/tools.

**Two-box state:** Finland main @ `50ecbaa` (pulled); GitHub has branch tip `30405ad`;
Oregon wt-iter89 tip `30405ad`; wt-merge89… wt-merge87 detached at the docs line. GitHub PAT
(rotated 2026-10-02) written to:芬兰 `/home/julio/projects/.env` GITHUB_TOKEN; Oregon
`/home/julio/projects/clean_diallux_SDR/.env` GITHUB_TOKEN; both repos' `.git/gh-creds`
credential stores (0600). Git from /tmp worktrees needs
`git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'`
(the relative-path helper breaks in worktrees — paid lesson this session).

**LLM.json schema note:** the contact_details→ConfirmSlots edge `required` = contact_details_
completed, first_name, company_name, prospect_timezone, callback_number, phone_confirmed
(+ `presence_required: [is_calling_best_number]`). GATE_FAIL_MESSAGES table in
`diallux/graph/tools.py:66`. Prompts md = runtime truth; llm.json = tools/fallback/Retell
parity (PT-75 law; doc still owed at T6 close).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| iter89 branch = A+B+C edits + cherry-pick, suite 3 stale reds, NO merge | LAW 0; owner HITL pending |
| Firesim auto-enable cherry-picked INTO iter89 branch (not main) | owner approved 2026-10-02; bigger fix = the eventually-merge lands it on main |
| first_name-required gate is owner-designed; deadlock is a DESIGN BUG to fix, not a gate to remove | owner's words 2026-10-02; keep the gate, find the lost fallback mechanic |
| GK batteries run SEQUENTIAL from now on | async-parallel caused silent zero-RAG reporting confusion; embedder race disproven but sequential is now SOP for evidence runs |
| 3 stale reds are NORM — never "fix" from a prompt branch | engine behavior obeys newer owner env orders |
| Sam-class failure = engine/gate fix candidate → new engine branch NEXT (none cut yet) | iter numbering law: gate touch = new iter |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO to run this assessment | owner's word |
| Owner decision on the eventual first_name fix approach (presence-based gate + [name_declined] vs agent-layer coercion) | after T2 archaeology gives the timeline |
| iter89 merge decision | owner at T4 (post-assessment) |

## Environment & Dependencies
- OREGON ssh wrapper (above). venv: /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python (always `-m pip`).
- No sqlite3 CLI — `.venv/bin/python -c "import sqlite3; …"` only.
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (runs/calls/rounds/rag/findings/sops/sessions). Run `gk-iter89` imported (5 calls, f7a37c3).
- SOP: /home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/full_call_analysys.md
- Harness json_logs (branch evidence): /tmp/opencode/wt-iter89/engine/tests/llm2llm/json_logs/GK*_l2l-*.json
- Main checkout (PROD; NEVER touch git state): /home/julio/projects/clean_diallux_SDR @ df23d37 (engine/iter73-oregon-wip line).
- Local main line (docs): /tmp/opencode/wt-main-docs (branch main @ 50ecbaa) on FINLAND directly;
  on OREGON /tmp/opencode/wt-merge87 detached at that docs line.
- Iter89 worktree: /tmp/opencode/wt-iter89 @ 30405ad.

## File Map (this plan's writes)
| File (absolute path) | What | |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter90_assess_rag_zero_and_first_name.md | this plan | new (docs→main, this session) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/90_rag_zero_main_verdict.md | T1 deliverable | new |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/91_first_name_archaeology.md | T2 deliverable | new |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/89_sam_autopsy.md | Sam gate deadlock autopsy | new |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/89_sop_rows_{call,sales,humanized}.json + import | iter89 SOP rows → ledger | persist |
| /home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md | PT-78 Sam-gate row; leaves PT-77 open | edit (docs) |

## Deploy Rules
- NO code branches, NO config edits, NO service touches. NO push/pull of code.
  Docs commits only (this plan, memos, PT rows) on the LOCAL main line (wt-main-docs
  on Finland; push there), then mirror to Oregon if owner asks.
- NEVER touch prod checkout git state (df23d37), services, ports, TTS/STT.

## Tasks (in order)

### T1 — Assess "ZERO rag retrievals on Intake" on the last main test (read-only)
Goal: verdict memo distinguishing MAIN's true behavior from the harness artifact.
Commands:
- Read main's harness: `ssh … "grep -n 'rag_fire_sim' /home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/harness.py | head"` (expect NO auto-enable block — the cherry-pick only lives on the branch).
- Confirm from the ledger which runs produced the "ZERO rag" Sheriff data:
  `python3 /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py --db /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db runs` + `python3 … sops --run …` cross-check.
- Classify: main→zero-RAG = TEST HARNESS artifact (missing auto-enable), NOT a live-call regression; the branch's f7a37c3 proves the fix. State in
  /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/90_rag_zero_main_verdict.md
  (with the three pieces of evidence + the merge implication: merging iter89 lands the guardrail on main).
Verification: memo exists; cites file grep + ledger run rows + branch diff `git -C /tmp/opencode/wt-iter89 diff 38f63e5..f7a37c3 -- tests/llm2llm/harness.py`.

### T2 — first_name attendee-fallback archaeology (find if the design was lost / when allowed)
Goal: timeline of the first_name gate + declined-name handling; verdict: (a) mechanic exists somewhere we misplaced, (b) mechanic never existed and iter89's restructure only exposed the deadlock, (c) mechanic existed and iter89 DELETED it (must be reverted/absorbed).
Commands:
- Git archaeology on the gate: `git -C /tmp/opencode/wt-iter89 log --oneline -S 'first_name' -- agent/llm.json | head -20` and `git -C /tmp/opencode/wt-iter89 log -p -S 'attendee name' -- diallux/prompts/contact_details.md | head -60`.
- Prompt fallback history: `git -C /tmp/opencode/wt-iter89 log --oneline -S 'Never re-ask for a name' -- diallux/prompts/contact_details.md`; and for the extraction side: `grep -n 'attendee name\|first_name' /tmp/opencode/wt-iter89/engine/diallux/graph/tools.py | head` (is there any name→first_name coercion? presence/truthy?).
- Ledger findings: findings table rows mentioning name/booking; `select * from findings;` via `.venv/bin/python -c "import sqlite3…"`.
- Plans/reports sweep: `grep -rn 'attendee name\|name declined\|Ortiz\|surname_not_provided' /home/julio/projects/clean_diallux_SDR/plans/ /home/julio/projects/clean_diallux_SDR/research/surgeon/ 2>/dev/null | head -40`.
- Deliverable: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/91_first_name_archaeology.md — dated timeline (iter + commit + what each side said), verdict a/b/c, and the minimal fix candidates (preserve the gate; e.g. presence_required + stored marker vs agent-layer attendee-name coercion).
Verification: memo timeline has commit SHAs for every row; no invented data.

### T3 — Sam autopsy + iter89 SOP judgment rows persisted (same session, no git moves for code)
Commands (per full_call_analysys.md): write rows files, then
- `cd /home/julio/projects/clean_diallux_SDR && python3 scripts/live_sql.py --db research/surgeon/iter48-rag-truth/ledger.db sop-import --run gk-iter89 --sop CALL --branch engine/iter89-prompt-enhancements --commit f7a37c3 --file research/surgeon/iter89-prompt-enhancements/89_sop_rows_call.json` (repeat SALES, HUMANIZED).
- Verify: `python3 … sops --run gk-iter89 | head -30`.
Verification: rows present (verify counts); Sam autopsy written at 89_sam_autopsy.md root-cause section as in Compaction Context.

### T4 — Close-out memo + owner decision pack
Goal: one page per owner: T1 verdict, T2 verdict + fix options, iter89 merge rec (notes: 4/5 booked, sales band hire on 4 calls, pricing-leak Priya red, Sam gate bug), and remaining T6 items (PT-75 lockstep doc, PT rows). Deliver in chat + save
research/surgeon/iter89-prompt-enhancements/92_closeout_memo.md. NO merge executed without owner say-so.
Dependencies: T1, T2.

## Validation Plan (end-to-end)
T1 memo (grep + ledger evidence) → T2 timeline (SHAs verified) → T3 rows in ledger (SELECT count) →
T4 memo → owner verdicts → (next session, separate engine branch per LAW 0): gate fix design.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Engine fix branch (first_name gate + [name_declined] or agent-layer coercion) | LAW 0: new code = new iter; design choices need T2 evidence + owner pick |
| Priya pricing-leak prompt patch | prompt branch closed; owner decides whether prompt tweak rides the next engine branch instead |
| iter89 merge + tag + git-tree.sh + REAL KB re-ingest | owner say-so at T4 |
| PT-77 leak drill | stays open |
| Mic battery / ear A/B on new prompts | post-merge |
