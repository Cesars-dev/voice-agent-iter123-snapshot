# plan_v5_iter89_prompt_enhancements — the owner's 00_master_plan prompt package (Phase 1 + Phase 3 now, Phase 2 owner-gated LAST) + 9-state llm.json lockstep + prompt-layer LAW 0

## Meta
- Date: 2026-10-02
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland/MainVps. ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Scope: ONE iteration on branch `engine/iter89-prompt-enhancements` (worktree
  /tmp/opencode/wt-iter89 on OREGON) implementing the owner's prompt-enhancement
  package: Phase 1 (owner-approved verbatim) + Phase 3 (wholesale general_prompt.md
  from 01_general_prompt_FINAL.md) + Phase 2 [APPLY] hunks (LAST, owner-gated),
  plus full 9-state llm.json lockstep + the widened byte-parity pin + test-pin
  updates. PROMPT LAYER ONLY: engine/diallux/prompts/*.md,
  engine/agent/knowledge_bases/*.md, engine/agent/llm.json, engine/tests pins.
  ZERO engine code, ZERO tool/dv/marker changes, ZERO services.
- Status: PLAN ONLY (branch cut at T1; edits await owner GO at T2).
- PARKS: /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter88_chat_leak_drill_and_intake_fix.md
  (PT-74's anchor rewrites are absorbed by Phase 1 I-4/I-5; PT-75 lockstep doc
  rides this iter's T6; PT-76 9-state pin lands in Edit A; PT-77 leak-reveal
  drill stays OPEN in plans/PENDING_TASKS.md — deferred, not cancelled).

## Compaction Context (assessment session 2026-10-02 — carried verbatim)

**Hunk authority = the owner's master plan**, byte-copied to
/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/00_master_plan.md
(source of truth: /home/julio/projects/vps-inbox/00_master_plan.md on the Finland
box, mutagen-synced from the Mac). Its ground rules §0 are BINDING: byte-exact
BEFORE/AFTER matching, STOP-the-file-on-mismatch (never fuzzy-match), no
reformatting, invariants §4 (tool names, {{dv}} names, refer-tag syntax, KB
markers, general_prompt section order, business numbers). Commit-per-file rule
§0.3 is SUPERSEDED by the owner's granularity law below (one commit per EDIT).

**Current tree state (verified 2026-10-02):** OREGON wt-merge87 detached HEAD
at ea8967a (merge 730dfdb + 3 docs commits, plans only). ALL master-plan BEFORE
blocks were verified byte-exact against the live files — Intake.md, general_prompt.md,
all 8 state prompts, both KBs. No drift. The master plan's own verification
commits (0ce798f/89b64d4, repo "diallux_sdr_almost_there") do NOT exist in this
repo — irrelevant, current tree is the anchor.

**Runtime mechanics (verified in code — why this is safe):**
- Prompts: md files are the runtime source of truth
  (engine/diallux/config.py:438 "editable source of truth";
  engine/diallux/graph/builder.py:1672 — llm.json state_prompt is ONLY a
  fallback when the md file is absent).
- llm.json IS load-bearing at runtime but NOT for prompts/transitions: it
  supplies starting_state + begin_message (engine/diallux/state.py:55/67), the
  states[] map (builder.py:352), and general_tools = TOOL DEFINITIONS
  (builder.py:579/2161/2199, engine/diallux/graph/tools.py:113/114). State
  transitions are engine code (transition_to_* in graph/tools.py). This plan
  touches ZERO tool names/flags/dv names → the llm.json tool layer is untouched;
  only state_prompt/general_prompt TEXT mirrors get synced.
- MODEL LAW trap: llm.json "model" field is DISPLAY-ONLY dead metadata — do NOT
  touch it while syncing.

**Mirror state TODAY (verified):** llm.json 6/9 state_prompts DRIFT from md
(Intake, Discovery, Closer, VerifyLead, Booking, Closing); Offer,
contact_details, ConfirmSlots MATCH. Top-level llm.json general_prompt (6503
chars) also drifted.

**RAG mechanics (verified):** rag_fire_mode default = "hybrid"
(config.py:293): lane A (engine intent = refer-tag queries + dv values) fires at
first flux Update; lane B (caller utterance) at EOT/EagerEOT (builder.py:1218-1221).
Per-state KB scopes are the hardcoded _STATE_KBS map (builder.py:1059): Intake/
Discovery = general 9 (+discovery-bridge), Closer = 5, Offer = 4, Closing = 2;
Booking/VerifyLead/ConfirmSlots/contact_details fall through to the general-9
union (slug order harvested from general_prompt.md doc order). _RETRIEVAL_OFF is
empty (iter59 KB-everywhere). The plan changes NO scopes — general keeps all 9
markers (Phase 3 keeps them on one line), state markers untouched.

**Phase 3 FINAL file (verified 2026-10-02):**
/home/julio/projects/vps-inbox/01_general_prompt_FINAL.md (6053 bytes, 979 words)
— byte-copied to the surgeon folder (see File Map). Machine-checked: all 9
##slug-kb## markers exactly once, zero {{var}}. Its one-line marker ORDER is
call-context, sales-language, pain-points, sales-psychology, industry,
voice-ai-capabilities, are-you-ai, hipaa, call-closing — are-you-ai/hipaa BEFORE
call-closing, which DIFFERS from the current test pin (test_iter49_rag_parity.py
_GENERAL_KBS = ..., voice-ai-capabilities, call-closing, are-you-ai, hipaa) →
Edit B updates _GENERAL_KBS to the FINAL file's order.

**Test collisions found (all resolved inside this plan):**
1. test_iter43_prompts.py test_llm_json_lockstep_byte_identical pins
   Offer + contact_details == llm.json → Edit A syncs ALL 9 states (owner
   approved full pin over releasing the 2).
2. test_iter49_rag_parity.py:263, test_iter63_rag_fire_sim.py:56,
   test_iter60_audit_fixes.py:115/120 pin Intake's SINGLE "the empathic mirror"
   refer tag and laneA count == 1 → Phase 1 gives Intake THREE tags
   (I-4 "surface pain recognition and opening discovery questions" — {{inbound_channel}};
   I-5a "probing questions below the surface symptom" — {{interest_topic}};
   I-5b "emotional anchoring and empathic response" — {{pain_frame}}) → laneA
   count 1→3 (at the <=3 lanes/side cap, OK) and queries change → Edit A
   updates these pins to the new reality (verify empirically via build_lanes).
3. test_iter49 _GENERAL_KBS order pin → Edit B update (above).

**KB re-ingest:** Phase 1 K-1/K-2 modify call-context-kb.md + pain-points-kb.md
→ pgvector chunks go stale → scripts/rag_ingest.py rebuild (~$0.02 whole
corpus). pgvector is SHARED infra → DRY-RUN only in-session; REAL ingest only at
owner-approved merge/deploy time.

**FROZEN BOX LAW (owner order 2026-09-30, still standing):** GitHub PAT deleted
both boxes; NO pushes, NO pulls. Oregon local = source of truth. Docs commits
land on the LOCAL main line (wt-merge87). Finland = untouched backup.

**Owner decisions this session (2026-10-02):**
- Commit granularity: ONE commit per EDIT (not per file). Three edits = three
  commits on the branch. "every commit per file adds overhead."
- Phase 2 (state-hunk dedupe/notation pass) moves LAST, gated on the owner
  evaluating whether it is worth testing apart from his own lines.
- Phase 3 is its own single edit ("we must test with general prompt").
- C-8 (Closer amplification + permission-to-math samples): KEEP as-is this iter
  (verdict = gambling); stripped-variant A/B = NEXT SESSION (2 sessions,
  2 commits).
- V-3 (VerifyLead mission reword): SKIP — "engine driven, it has been working,
  let it run."
- CL-3 (Closing recap): owner CONFIRMED the booking sends an SMS only → the
  "link to join" + "one-click calendar" promises are FALSE → apply the safe
  wording (below).
- llm.json: pin ALL 9 states (full lockstep + widened parity test), do not
  release the 2 existing pins.
- LAW 0 clarification (owner order): LAW 0 applies EXPLICITLY to prompts + KBs
  + llm.json — never "docs straight to main". One line added to AGENTS.md.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Branch engine/iter89-prompt-enhancements cut on OREGON from the docs head (post-ea8967a) | iter88 number burned by the parked plan's docs; LAW 0 branch discipline |
| ONE commit per EDIT: Edit A (Phase 1 + KBs + llm.json 9-state sync + test pins), Edit B (Phase 3 wholesale + general mirror + _GENERAL_KBS order), Edit C (Phase 2, last) | owner 2026-10-02: per-file commits add overhead |
| Phase order: A → B → (owner gate) → C | owner 2026-10-02: Phase 2 last, after he evaluates it |
| Phase 2 §3.1 G-1..G-4 SKIPPED (superseded by Phase 3 wholesale) | master plan §3A: identical result already in the FINAL file |
| C-8 KEEP (no hunk); stripped A/B next session | verdict = gambling (attribution + ear-tuned craft at the PT-77 failure point); owner rule: third option → next session, try both |
| V-3 SKIPPED entirely | owner: VerifyLead is engine-driven, working — let it run |
| CL-3 APPLY: Closing recap sample becomes `<Thanks, {{first_name}}! You'll get a text with all the details — the day and the time.>` (drop the link/calendar clause) | owner confirmed SMS-only; master plan CL-3 safe wording; "text" matches the confirmed fact (Booking.md already says "You'll get a text") |
| llm.json full 9-state sync + widened parity pin (PT-76 lands here) | owner: pin all 9; 6/9 already drift today; fallback must be safe |
| Edit B also syncs llm.json top-level general_prompt to the FINAL content | mirror hygiene; same rationale |
| Test-pin updates approved as in-scope (iter43/49/60/63) | owner approved the scope additions that keep the suite green |
| KB re-ingest: dry-run in-session, real ingest at merge time | shared pgvector; branch must not mutate prod retrieval |
| Master plan §0 ground rules BINDING (byte-exact, STOP-on-mismatch, §4 invariants) | hunk authority = the copied 00_master_plan.md |
| FROZEN BOX: no push/pull; docs on LOCAL main (wt-merge87) | owner order 2026-09-30, standing |
| AGENTS.md gets one LAW 0 clarification line (docs commit) | owner order: LAW 0 applies to prompts + KBs |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO for Edit A (T2 start) | T0 HITL; this plan's approval |
| Owner evaluation of Phase 2 "worth testing apart from my own lines" | T4 gate — owner eyeballs Edit A+B results first |
| Optional zero-TTS chat battery GO (T5) | owner at T5; default = yes (mock slots, graph transport) |
| GitHub token rotation | owner-only, github.com; until then FROZEN BOX |

## Environment & Dependencies
- OREGON ssh wrapper (ALL repo ops):
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Worktrees on OREGON: /tmp/opencode/wt-merge87 (LOCAL main line, docs head),
  /tmp/opencode/wt-iter89 (THE build, branch engine/iter89-prompt-enhancements),
  /tmp/opencode/wt-iter87 (.env source).
- ENV LAW: /tmp/opencode/wt-iter89/engine/.env copied from
  /tmp/opencode/wt-iter87/engine/.env BEFORE any run (carries rotated OpenAI
  key + round-B knobs). Never print its values.
- OREGON venv (shared): /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python
  (pip trap: always `<venv>/bin/python -m pip`, never bin/pip).
- pytest law: run from the worktree engine dir; count FAILED lines — the final
  "N failed/M passed" line may be missing (box quirk). Expected baseline: 3
  stale reds ONLY (iter46 fast-first-flush, iter59 semantic-threshold, iter60
  turn-opening-reask).
- Hunk authority: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/00_master_plan.md
  (gitignored evidence copy — NEVER edited; the owner's vps-inbox original is
  the source). Phase 3 source:
  /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/01_general_prompt_FINAL.md.
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (NO sqlite3 CLI — venv python + sqlite3 module only).
- MODEL LAW: agent gpt-5.4 everywhere. Chat battery = graph transport,
  --slots mock, ZERO TTS/STT spend.
- Cal.com event 3801235 is REAL — cancel every test booking if real slots are
  ever touched (chat battery uses mock slots → normally nothing to cancel).

## Architecture (one block)
```
T1 branch engine/iter89-prompt-enhancements (DONE at plan time)
→ T2 EDIT A (one commit): Phase 1 hunks I-1..I-9, G-A/G-B, K-1/K-2, D-A/D-B
  + llm.json ALL-9 state_prompt sync + test pins (iter43 widen-to-9, iter49/60/63
  new Intake anchors) → suite = 3 stale reds only
→ T3 EDIT B (one commit): general_prompt.md wholesale ← 01_general_prompt_FINAL.md
  + llm.json general_prompt sync + _GENERAL_KBS order pin → suite + Phase-3
  invariant checks
→ T4 HITL GATE (owner evaluates Phase 2) → EDIT C (one commit): Phase 2 [APPLY]
  hunks D-1..D-4, C-1..C-7, O-1..O-4, CT-1..CT-4, CS-1/CS-2, V-1/V-2, B-1/B-2,
  CL-1/CL-2/CL-3(safe wording), I-10 — minus V-3 (skip) minus C-8 (keep)
  + llm.json re-sync → suite
→ T5 full validation: master-plan §5 (refer-tag parse = 3 pain-points tags,
  Intake zero angle brackets, filtered pytest, KB ingest DRY-RUN) + optional
  zero-TTS chat battery (owner GO)
→ T6 report + ledger rows + PT rows + PT-75 lockstep doc + HITL merge decision
  (NOTHING lands on main without owner say-so)
```

## File Map
| File (absolute path, OREGON worktree) | Role | Touch? |
|---|---|---|
| /tmp/opencode/wt-iter89/engine/diallux/prompts/Intake.md | Phase 1 I-1..I-9 (Edit A); Phase 2 I-10 (Edit C) | Edit A + C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/general_prompt.md | G-A/G-B (Edit A, then overwritten); wholesale ← FINAL (Edit B) | Edit A + B |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/Discovery.md | D-A/D-B (Edit A); D-1..D-4 (Edit C) | Edit A + C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/Closer.md | C-1..C-7 (Edit C); C-8 NOT applied | Edit C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/Offer.md | O-1..O-4 (Edit C) | Edit C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/contact_details.md | CT-1..CT-4 (Edit C; CT-2 before CT-3) | Edit C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/ConfirmSlots.md | CS-1/CS-2 (Edit C) | Edit C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/VerifyLead.md | V-1/V-2 (Edit C); V-3 NOT applied | Edit C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/Booking.md | B-1/B-2 (Edit C) | Edit C |
| /tmp/opencode/wt-iter89/engine/diallux/prompts/Closing.md | CL-1/CL-2/CL-3 safe wording (Edit C) | Edit C |
| /tmp/opencode/wt-iter89/engine/agent/knowledge_bases/call-context-kb.md | K-1 General Inbound (Edit A) | Edit A |
| /tmp/opencode/wt-iter89/engine/agent/knowledge_bases/pain-points-kb.md | K-2 Trigger Questions insert (Edit A) | Edit A |
| /tmp/opencode/wt-iter89/engine/agent/llm.json | 9 state_prompts sync (A); general_prompt sync (B); re-sync (C). NEVER touch "model" field | A + B + C |
| /tmp/opencode/wt-iter89/engine/tests/test_iter43_prompts.py | widen lockstep pin Offer+contact → ALL 9 (PT-76) | Edit A |
| /tmp/opencode/wt-iter89/engine/tests/test_iter49_rag_parity.py | Intake laneA pins 1→3 tags (A); _GENERAL_KBS order ← FINAL (B) | A + B |
| /tmp/opencode/wt-iter89/engine/tests/test_iter60_audit_fixes.py | "the empathic mirror" → "emotional anchoring" substring | Edit A |
| /tmp/opencode/wt-iter89/engine/tests/test_iter63_rag_fire_sim.py | laneA count/query pins → 3 new anchors | Edit A |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/00_master_plan.md | hunk authority (evidence copy, gitignored, never edited) | read only |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/01_general_prompt_FINAL.md | Phase 3 wholesale source (evidence copy) | read only |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/ | reports 01_edit_log.md, 02_verdict.md | append |
| /home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md | PT-74 absorbed-note, PT-76 close, PT-75 doc, PT-77 stays open | T6 |
| /home/julio/projects/clean_diallux_SDR/docs/prompt_llm_json_lockstep.md | PT-75 lockstep doc (md = runtime truth; llm.json = tools + fallback + Retell parity) | T6 (docs) |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | STATUS update at close | T6 (docs) |

## Deploy Rules
- FROZEN BOX: NO git push, NO git pull. Docs commits on the LOCAL main line
  (/tmp/opencode/wt-merge87). Code/prompt commits ONLY on
  engine/iter89-prompt-enhancements. NOTHING merges to main without owner
  say-so (LAW 0).
- NEVER touch the OREGON prod checkout git state (df23d37) / diallux.service /
  :8026/:8000-8003/:8090. Prod retrieval untouched until merge + re-ingest.
- KB re-ingest (scripts/rag_ingest.py) = DRY-RUN only in-session; the REAL
  ingest happens at owner-approved merge/deploy time.
- No services, no ports, no TTS/STT spend. Chat battery (if GO) = graph
  transport + mock slots.
- llm.json "model" field is dead display metadata — never "fix" it (MODEL LAW).

## Tasks (in order)

### T1 — branch cut + env + evidence (DONE at plan time — verify only)
Goal: /tmp/opencode/wt-iter89 on engine/iter89-prompt-enhancements, .env in
place, evidence copies in the surgeon folder.
Commands (already run):
- `ssh …root@5.78.83.174 "git -C /tmp/opencode/wt-merge87 worktree add /tmp/opencode/wt-iter89 -b engine/iter89-prompt-enhancements <docs-head-sha> && cp /tmp/opencode/wt-iter87/engine/.env /tmp/opencode/wt-iter89/engine/.env"`
- evidence copies into research/surgeon/iter89-prompt-enhancements/ (00_master_plan.md,
  01_general_prompt_FINAL.md from the Finland vps-inbox mirror).
Verification: worktree exists at the branch; `test -f /tmp/opencode/wt-iter89/engine/.env`
(never print contents); both evidence files present.

### T2 — EDIT A: Phase 1 + KBs + 9-state llm.json lockstep + test pins (ONE commit)
Goal: owner-approved Phase 1 landed verbatim; mirror fully synced; suite green
(3 stale reds only).
Files: see File Map (Edit A rows).
Steps:
1. Apply Phase 1 hunks EXACTLY from the surgeon-folder 00_master_plan.md §2:
   Intake I-1..I-9, general G-A/G-B, K-1, K-2, Discovery D-A/D-B. Byte-exact
   BEFORE matching; STOP the file and report on ANY mismatch (§0 law).
2. Sync llm.json: for ALL 9 states set states[].state_prompt = the
   post-Phase-1 md content (json-escaped, preserve the file's existing json
   formatting style; do NOT touch any other field, especially "model").
   Do it with a small python script via the venv python, then verify by test.
3. Test pins:
   a. test_iter43_prompts.py — widen test_llm_json_lockstep_byte_identical to
      all 9 states (Intake, Discovery, Closer, Offer, contact_details,
      ConfirmSlots, VerifyLead, Booking, Closing).
   b. test_iter49_rag_parity.py test_build_lanes_lane_a_query_format_and_scope —
      post-Phase-1 Intake has 3 refer tags → laneA = 3 lanes. Verify the actual
      queries empirically (build_lanes with the test's dvs), then pin: the
      {{pain_frame}}-tagged lane query = "emotional anchoring and empathic
      response: missed calls"; the {{inbound_channel}}/{{interest_topic}} lanes
      = bare anchors (dvs empty in that test). Keep the laneB/scope asserts
      unchanged.
   c. test_iter60_audit_fixes.py — "the empathic mirror" substrings →
      "emotional anchoring" (verify against actual lane queries).
   d. test_iter63_rag_fire_sim.py — lane_a count 1→3 + query pins (verify
      empirically; the persona's dvs decide which lanes carry values).
4. Run the suite:
   `cd /tmp/opencode/wt-iter89/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q`
   Expect EXACTLY the 3 stale reds (count FAILED lines).
5. Master-plan §5 checks: refer-tag parse on Intake.md (must return exactly 3
   tags, all pain-points — script in 00_master_plan.md §5.1) + angle-bracket
   audit (zero `<` and zero `>` in Intake.md).
6. ONE commit:
   `iter89 edit A: prompting phase 1 (Intake rework + 3 refer anchors, G-A/G-B, K-1/K-2, D-A/D-B) + 9-state llm.json lockstep + parity/tag pin updates`
Verification: suite 3 stale reds; §5 checks pass; `git show --stat` = prompts
(4 md) + 2 KBs + llm.json + 4 test files.
Dependencies: owner GO.

### T3 — EDIT B: Phase 3 wholesale general_prompt + general mirror (ONE commit)
Goal: general_prompt.md = 01_general_prompt_FINAL.md byte-exact; llm.json
general_prompt synced; _GENERAL_KBS order pin updated.
Steps:
1. Replace the ENTIRE content of
   /tmp/opencode/wt-iter89/engine/diallux/prompts/general_prompt.md with the
   byte-exact content of the surgeon-folder 01_general_prompt_FINAL.md
   (overwrites Edit A's G-A/G-B — expected, master plan §3A).
2. Sync llm.json top-level "general_prompt" to the same content (no other
   fields).
3. test_iter49_rag_parity.py — _GENERAL_KBS order ← the FINAL file's marker
   order: ["call-context", "sales-language", "pain-points", "sales-psychology",
   "industry", "voice-ai-capabilities", "are-you-ai", "hipaa", "call-closing"]
   (update the trailing comment too). This is the union-fallback order for
   Booking/VerifyLead/ConfirmSlots/contact_details + MadeUpState.
4. Phase-3 invariant checks (master plan §3A): all 9 markers exactly once in
   the raw file; zero {{var}}; (optional) deployed token count 1,284
   (o200k_base, markers stripped).
5. Suite (expect 3 stale reds). If ANY other general-content pin fails
   (test_first_turn_lite, test_iter31_c3_prefix, test_iter25_tags, test_rag):
   update ONLY wording pins; a MECHANICS failure = STOP + report (do not
   "fix" engine behavior from a prompt branch).
6. ONE commit:
   `iter89 edit B: prompting phase 3 — general_prompt wholesale from 01_general_prompt_FINAL.md + general mirror sync + _GENERAL_KBS order pin`
Verification: diff(md, FINAL) empty; suite 3 stale reds; head-cache note —
expect exactly ONE re-prime on the next live call (placement change, not
per-turn cost).
Dependencies: T2.

### T4 — HITL GATE + EDIT C: Phase 2 [APPLY] hunks, LAST (ONE commit, owner-gated)
Goal: the dedupe/notation pass, only after the owner evaluates Edit A+B results
and says Phase 2 is worth testing.
GATE: owner reviews Edit A+B diffs (and optionally the T5 battery) and answers:
"Phase 2 worth testing apart from my own lines?" Default if no answer: DEFER
Phase 2 to its own session (the branch keeps Edit A+B only).
Steps (on GO):
1. Apply from 00_master_plan.md §3 (Phase-2 BEFORE blocks assume Phase 1
   landed — they do now): D-1..D-4, C-1..C-7, O-1..O-4, CT-1..CT-4 (CT-2 then
   CT-3), CS-1/CS-2, V-1/V-2, B-1/B-2, CL-1, CL-2, I-10.
   NOT applied: V-3 (owner: leave as-is), C-8 (keep samples — next-session A/B),
   §3.1 G-1..G-4 (superseded by Phase 3).
2. CL-3 (owner-approved safe wording) — Closing.md recap sample becomes:
   `<Thanks, {{first_name}}! You'll get a text with all the details — the day and the time.>`
   (the "link to join" + "one-click calendar" clause is DELETED — the booking
   sends an SMS only, owner-confirmed 2026-10-02).
3. Re-sync llm.json 9 state_prompts (Edit C changed 8 of them).
4. Suite (3 stale reds) + rerun §5.1 refer-tag parse (still 3 tags) +
   angle-bracket audit.
5. ONE commit:
   `iter89 edit C: prompting phase 2 [APPLY] (one-home dedupe, notation law, de-machine; V-3 skipped, C-8 kept, CL-3 SMS-safe) + llm.json re-sync`
Verification: suite 3 stale reds; parity pin green (9 states); every hunk's
BEFORE matched byte-exact.
Dependencies: T3 + owner GO at the gate.

### T5 — full validation (master plan §5 + optional zero-TTS battery)
1. §5.1 refer-tag parse: exactly 3 tags, all pain-points (Intake).
2. §5.2 angle-bracket audit: Intake.md zero `<` and zero `>`.
3. §5.3 filtered suite: `-k "subst or rag or refer or prompt"` (adapt) — no new
   failures; full suite = 3 stale reds.
4. §5.4 KB re-ingest DRY-RUN:
   `cd /tmp/opencode/wt-iter89/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/rag_ingest.py --dry-run`
   → expect +1 section in pain-points (Trigger Questions) and the call-context
   chunk set change. REAL ingest = merge-time only.
5. §5.5 retrieval anchor eval (recommended): golden query set → the 3 new
   Intake refer lanes land on Opening Questions / Probing / Emotional Anchoring /
   Trigger Questions chunks.
6. OPTIONAL (owner GO) zero-TTS chat battery (graph transport, mock slots):
   `cd /tmp/opencode/wt-iter89/engine && .venv-path python tests/llm2llm/harness.py --transport graph --personas Maria,Danny,Sofia --slots mock --rag --langfuse --caller-model gpt-5.4 --agent-model gpt-5.4`
   Gates: Intake rag chunks > 0 on refer-bearing rounds (the PT-74 KB-less fix
   verified — pull ledger rag rows); no empty-text-with-tools regressions.
   Import to ledger: `scripts/live_sql.py import --run chat-iter89 --branch engine/iter89-prompt-enhancements --commit <sha>`.
Verification: all checks recorded in the report with outputs.
Dependencies: T3 (or T4 if Phase 2 lands first).

### T6 — report + ledger + PT rows + lockstep doc + HITL close
1. Report: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/01_edit_log.md
   (per-hunk applied/skipped table with reasons) + 02_verdict.md.
2. PENDING_TASKS.md: PT-74 → ABSORBED (Phase 1 I-4/I-5 rewrote the anchors;
   residual: Discovery/Closer/Offer refer anchors still delivery-instruction
   style — new PT row if owner wants them reworded); PT-76 → CLOSED (9-state
   pin landed in Edit A); PT-75 → CLOSED (doc below); PT-77 stays OPEN.
3. PT-75 lockstep doc: /home/julio/projects/clean_diallux_SDR/docs/prompt_llm_json_lockstep.md
   (md = runtime truth per-call; llm.json = general_tools + starting_state +
   begin_message + state_prompt FALLBACK + Retell parity; edit law = every
   prompt edit syncs the mirror in the SAME commit; MODEL LAW dead-field lesson).
4. Master ladder STATUS + NEXT_STEPS update; docs commit on wt-merge87 (LOCAL).
5. HITL: owner reviews branch diffs → merge decision (LAW 0: owner say-so
   required; merge = --no-ff + tag engine/iter89 + scripts/git-tree.sh +
   ITERATIONS.md ledger line + REAL KB re-ingest at deploy).
Verification: report exists; PT rows updated; docs committed locally.
Dependencies: T5.

## Validation Plan (end-to-end)
T1 branch → Edit A (Phase 1 verbatim + 9-state lockstep + pins; suite 3 stale
reds) → Edit B (general = FINAL byte-exact + mirror + order pin; invariants) →
owner gate → Edit C (Phase 2 minus V-3/C-8 plus CL-3; re-sync) → §5 checks +
dry-run ingest (+ optional zero-TTS battery) → report/ledger/docs → HITL merge
decision. Abort/rollback: everything lives on the branch —
`git -C /tmp/opencode/wt-iter89 checkout -- <file>` per edit, or drop the
branch entirely; main line and prod untouched; no config, no services, no spend
(unless the optional battery is GO'd — mock slots, zero TTS).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| C-8 stripped-variant A/B (Closer samples out, rely on sales-psychology-kb) | owner rule: gambling verdict → NEXT SESSION, 2 sessions + 2 commits |
| PT-77 leak-reveal drill (chat census) | parked with iter88; can ride the optional T5 battery informally |
| Discovery/Closer/Offer refer-anchor rewording (residual PT-74) | not in master plan scope; owner call after iter89 evidence |
| Mic battery + owner ear A/B on the new prompts | after merge; avoids double spend |
| REAL KB re-ingest into pgvector | merge/deploy time only (shared infra) |
| GitHub push (branch + docs) | FROZEN BOX until owner rotates the PAT |
