# plan_v5_iter88_chat_leak_drill_and_intake_fix — chat-lane leak-reveal drill (ZERO TTS spend) + the PT-74 KB-less fix + lockstep discipline

## Meta
- Date: 2026-09-30 (written at the Real_MVP merge-validation session close).
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Scope: ONE session. (a) Chat-lane drill of the leak-reveal skip pattern (PT-77) —
  graph transport, text only, ZERO TTS/STT spend; (b) the ONE-LINE Intake.md:35
  refer-tag fix (PT-74) + the llm.json Intake mirror sync; (c) the 9-state
  byte-parity pin (PT-76, test-only); (d) the md↔llm.json lockstep doc (PT-75, docs-only).
- Status: PARKED 2026-10-02 by owner — superseded by /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter89_prompt_enhancements.md (the 00_master_plan prompt package: PT-74 anchor rewrites absorbed by its Phase 1, PT-75 doc rides iter89 T6, PT-76 pin lands in iter89 Edit A; PT-77 drill stays OPEN in PENDING_TASKS).
- SUPERSEDES: /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter88_intake_refer_drill.md
  (absorbed 100% — its T3 one-line fix, battery intent and FIND-9 drill evidence carry here).

## Compaction Context (merge-validation session close 2026-09-30 — carried verbatim)

**Real_MVP merge landed LOCALLY (FROZEN BOX).** Merge commit `730dfdb` in worktree
/tmp/opencode/wt-merge87 (detached): main line = origin/main 50ecbaa + engine/iter87-prewarm-hold
02eb2ac chain (21 commits: iter80 EL-mic-flip+driver → iter82 pause-nudge → iter83 stt-liveness
→ iter84 backoff → iter85 eager-hold+deletes → iter86 forensics SDK → iter87 deterministic-hold).
Conflicts ×4 (llm.py, session.py, test_iter65_dv_carryover, test_tts_providers) resolved
--theirs (chain side = iter80-audited, battery-proven). Main-side keeps: speech_replay.py
(+294), test_delivery.py current pins (+22/−15), test_iter66_elevenlabs_cutover.py (+334).

**FROZEN BOX LAW (owner order 2026-09-30):** GitHub PAT DELETED from both boxes
(/home/julio/projects/clean_diallux_SDR/.git/gh-creds removed on OREGON + FINLAND;
credential.helper now fails closed; old token must be REVOKED by owner on github.com).
NO pushes, NO pulls. Oregon local = source of truth. Finland = untouched backup
(last sync: origin/main 5ad4e22 = STALE by design). Docs commits land on the LOCAL
main line (wt-merge87) and wait for the owner's token rotation to push.

**Merge validation PASSED (evidence report
/home/julio/projects/clean_diallux_SDR/research/surgeon/iter87-prewarm-hold/03_merge_validation_sop_audit.md,
40 sops rows in ledger runs merge87-validation + iter87-hold-battery):**
- Suite on 730dfdb: 3 stale reds ONLY (iter46 fast-first-flush, iter59 semantic-threshold,
  iter60 turn-opening-reask) — was 7 on the chain; main's iter66 test pins healed
  test_delivery ×4 (15/15 PASS). Zero new. NOTE: pytest on this box hard-exits after the
  summary WITHOUT printing the final "N failed/M passed" line — count the FAILED lines.
- Live mic validation call (merged tree, frozen driver, Danny happy, EL Sarah verified
  journalctl, gpt-5.4): micbridge-cede46476d35 / Langfuse 7b3f940bfd4107ca5745307c362960c8,
  44 rounds. Latency BETTER: uperm p50 1,005 (vs 1,176 iter87 row 13), E2Eresp p50 1,196
  (vs 1,385), turn-1 682, round ttft p50 795, cache-0 rounds 0, eager match 100%, 0 cold
  destination rounds (await_warm: 53 already_done / 4 landed). NO booking (caller-turn cap
  31 hit mid-VerifyLead) → nothing to cancel. p90 ~4.0s = the KNOWN pre-existing S2L spike
  surface (hysteretic trim) — unchanged, not a merge regression.

**THE LEAK-REVEAL SKIP (PT-77 — THE pattern question this plan drills first):**
Trace forensics (GEN15-17, Closer state): GEN15 asks permission ("Has anyone ever shown
you the math…?"); caller NEVER answers (repeats "$450" fragments — driver re-ingestion
artifact, caller utterances processed 2-4× as separate rounds on BOTH trees); GEN16 fires
extract_leak_inputs(missed_calls_weekly 15, close_rate_pct 60, avg_job_value 450) +
calculate_monthly_leak → tool OK: weekly_leak 4,050 / monthly_leak 17,500 — WITH EMPTY
TEXT; GEN17 EMPTY TEXT again, writes monthly_leak via extract_closer_details (it READ the
$17,500) + closer_completed + transition_to_Offer. The weekly-first reveal was NEVER
spoken; caller NEVER declined. Two prompt rules violated: "Call the tool in the SAME
response as your reply text — never empty text with tools" (×2) + "Reveal WEEKLY FIRST …
then STOP and wait" (skipped). iter87-happy (same driver) DID reveal at t25 ("$17,500 a
month", in Offer state — late but spoken). SALES D4: merge call 1/2, iter87 2/2.

**Chat-lane compatibility audit (DONE, read-only):** harness.py delta 2a36c94→730dfdb
= 2 lines; builder delta 02eb2ac→730dfdb = EMPTY — the chat lane runs the EXACT
battery-proven builder. Media-layer changes (EOT/STT/TTS params, eager hold, backoff,
ladder) never touch graph transport. The chat harness parses refer tags + does RAG
(--rag) — the KB-less disease (PT-74) is testable on chat at ZERO TTS cost.

**THE KB-LESS BUG (PT-74, unchanged from the absorbed plan):**
Intake.md:35 `#[refer pain-points-kb for the empathic mirror — {{pain_frame}}]` — the
delivery instruction leaked INTO the refer anchor (parser rag.py:589 takes the text
between "for" and "—" as the retrieval query; builder.py:1088 refer_query embeds it).
16/17 Intake retrievals 0-chunk (iter87 battery G1 FAIL). Origin: b94dad4 (2026-09-08
restructure), carried 22 days. llm.json Intake state_prompt ALREADY lacks the tag
(mirror drift exists) — the fix MUST sync the mirror (PT-76 pins it forever after).

**Session infrastructure:**
- Two-box law: session on Finland (MainVps); ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`.
  Worktrees on Oregon: /tmp/opencode/wt-merge87 (730dfdb — THE base), wt-iter87 (02eb2ac),
  wt-iter86 (d158b4c — forensics SDK + .env source), wt-iter82 (frozen driver).
- Registry DB refreshed 2026-09-30: /home/julio/projects/clean_diallux_SDR/research/surgeon/
  iter47-call-ledger/ledger.db (branches 188 / commits 6411 / iter_docs 422 rows; backup
  ledger.db.iter47-stale-20260930.bak).
- Call ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (NO sqlite3 CLI — venv python + sqlite3 module only).
- Chat harness: `/tmp/opencode/wt-merge87/engine/tests/llm2llm/harness.py`
  `--transport graph --personas <Name> --slots mock --langfuse --caller-model <m> --agent-model gpt-5.4`.
  Personas (REAL names only): Maria, Susan, Danny, Marcus, Carlos, Pedro, Sofia, Jorge,
  Daniel, Brenda, Gene, Frank, Ray + 12 adversarial; Larry gated.
- SDK: /tmp/opencode/wt-iter86/engine/scripts/call_forensics.py (--trace <langfuse-id-prefix>;
  --journal crashed on these traces = None-ts render bug, trace-only works).
- Lane boot (for the optional single mic check): /tmp/opencode/boot_lane_merge87.sh <port>
  (8047 proven free; round-B knobs + WARM_AWAIT_DEST_MS=2500 baked in; systemd-run --user
  --collect --unit=diallux-<port>.service; kill at close + ss verify).
- MODEL LAW: agent gpt-5.4 everywhere. VOICE LAW: tests = EL Sarah (uG1JFy6xppqckhHCs2KG) —
  journalctl `connected` before any mic call.
- Cancel every test booking (event 3801235 REAL). This plan's chat battery uses MOCK slots
  → normally nothing to cancel; if real slots ever touched, cancel via the iter87 recipe.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Merge 730dfdb = LANDED locally; Real_MVP; suite 3 stale reds; validation call PASS | owner: "iter87 is a real MVP"; no push possible (frozen box) |
| FROZEN BOX: no push/pull; token deleted both boxes; docs commit locally on wt-merge87 | owner order 2026-09-30; GitHub + Finland = backups |
| Master ladder = as good as it gets; ONE pending = PT-74 + discovered prompt issues | owner 2026-09-30 |
| Chat lane = the instrument for the leak-reveal drill (zero TTS spend) | owner: "not waste text-to-speech tokens since we're only checking logic" |
| PT-74 fix = ONE line in Intake.md + llm.json Intake mirror sync (same commit) | mirror drift already exists; owner: heavy md iterations must LAND in llm.json |
| 9-state byte-parity pin (PT-76) = test-only, rides this session | owner: "sync the 9 states (we only have 2 right now)" |
| Lockstep discipline doc (PT-75) = docs-only | owner: "md-llm.json riddle to be documented properly" |
| Heavy prompt engineering = owner has his own plan — DEFERRED, not this session | owner 2026-09-30 |
| R5.5 in-generation dupes + re-ask loops = PRE-EXISTING (both trees), tracked not fixed here | SOP audit evidence; separate owner design call |
| Keep git discipline; boxes stay on separate commits | owner 2026-09-30 |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO: chat drill scope + exact Intake.md:35 wording (default below) | T0; default = `#[refer pain-points-kb — missed calls, lost bookings — {{pain_frame}}]` |
| Whether the drill needs a NEW fragmented-caller persona (owner dictates script) | T0; default = existing personas first, no new persona without owner |
| GitHub token rotation (owner-only, github.com) | whenever owner wants pushes back; until then FROZEN BOX |

## Environment & Dependencies
- OREGON venv (shared): /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python
  (never <venv>/bin/pip — copy-mirror trap; use <venv>/bin/python -m pip).
- Branch base law: cut `engine/iter88-chat-leak-drill` FROM the LOCAL main line `730dfdb`
  (NOT origin/main — frozen box): `git -C /tmp/opencode/wt-merge87 worktree add
  /tmp/opencode/wt-iter88 -b engine/iter88-chat-leak-drill 730dfdb && cp
  /tmp/opencode/wt-iter87/engine/.env /tmp/opencode/wt-iter88/engine/.env`
  (ENV LAW: .env carries the rotated OpenAI key + all round-B knobs).
- Chat battery needs NO ports, NO TTS keys (graph transport; --slots mock).
- pytest count law: count FAILED lines, the final count line may be missing (hard-exit quirk).
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db.

## Architecture (one block)
```
T1 chat-lane drill: fragmented-caller rounds → Closer rounds census (reveal spoken?
   empty-text-with-tools?) across existing personas, ZERO TTS → pattern vs fluke
   → T2 PT-74 one-line fix + llm.json Intake sync → T3 9-state parity pin (test-only)
   → T4 chat battery (mock slots): reveal discipline + Intake rag chunks > 0 + suite
   → T5 PT-75 lockstep doc + ledger rows + report → HITL
```

## File Map
| File (absolute path) | Role | Touch? |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter81_master_ladder.md | THE ladder (STATUS = resume point) | status only |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter88_chat_leak_drill_and_intake_fix.md | THIS plan | itself |
| /tmp/opencode/wt-merge87 (730dfdb) | the LOCAL main line + base for the branch cut | read/base |
| /tmp/opencode/wt-iter88 (cut at T1) | the build | build here |
| /home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/Intake.md | PT-74: line 35 refer tag | T2 — ONE line |
| /home/julio/projects/clean_diallux_SDR/engine/agent/llm.json | Intake state_prompt mirror sync | T2 — same commit |
| /home/julio/projects/clean_diallux_SDR/engine/tests/test_iter43_prompts.py | parity pin lives here (Offer+contact) → widen to 9 states | T3 — test only |
| /home/julio/projects/clean_diallux_SDR/docs/ (new file) | PT-75 lockstep doc | T5 |
| /tmp/opencode/wt-iter86 (d158b4c) | forensics SDK + .env source | SDK use |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db | call/findings ledger (sops/rag/runs) | append |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter88-chat-leak-drill/ | reports (NN_*.md) | append |
| /home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md | PT-74/75/76/77 rows | close on done |

## Deploy Rules
- FROZEN BOX: NO git push, NO git pull, NO fetch that changes working trees. Docs
  commits on the LOCAL main line (wt-merge87). Push returns ONLY after the owner
  rotates the GitHub token and says so.
- NEVER touch the OREGON prod checkout git state (df23d37) / diallux.service /
  :8026/:8000-8003/:8090.
- ENV LAW: copy wt-iter87 engine/.env into every new worktree before ANY run.
- Cancel every test booking if real slots touched (event 3801235 REAL).
- Docs (md) straight to main (LOCAL); CODE waits on engine/iter88-* branch per LAW 0.

## Tasks (in order)
### T0 — HITL: scope + wording (10 min)
1. Present: chat-drill scope (personas list), the ONE-LINE rewrite (old vs new),
   the 9-state pin, the lockstep doc. Owner approves / dictates.
Verification: owner says GO; wording pinned in this plan's margin.
Unblocks: T1.

### T1 — branch cut + worktree (5 min)
Goal: /tmp/opencode/wt-iter88 on engine/iter88-chat-leak-drill @ 730dfdb.
Commands: exactly as in Environment & Dependencies (branch cut line).
Verification: worktree exists; `.env` has OPENAI_API_KEY (never print the value).
Unblocks: T2.

### T2 — chat-lane leak-reveal drill (PT-77, 45 min, NO code, ZERO TTS)
Goal: pattern vs fluke. Census across existing personas (chat battery = mock slots,
graph transport): per call, Closer-state rounds — (a) does the weekly reveal get SPOKEN
(extract from Langfuse gen outputs: text containing "a week"/"a month" + $ figure after
calculate_monthly_leak ok); (b) empty-text-with-tools count; (c) reveal-timing (Closer
vs late/Offer). Compare merge-lane Danny mic call as the known positive skip.
Commands: run harness per persona (one command each, full absolute paths); pull gen
outputs via the Langfuse REST recipe in Compaction Context; tabulate.
Output: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter88-chat-leak-drill/
00_reveal_drill.md (table: persona | rounds | reveal spoken Y/N | empty-tool-text count |
notes). Every claim = a trace row.
Verification: ≥6 personas run; every verdict = quote from a gen output.
Unblocks: T3 (and answers: user-side vs pattern).

### T3 — PT-74 refer-tag anchor rewrite + mirror sync (30 min; scope WIDENED by the 2026-09-30 chat round-sync census: 4 of 5 tags embed delivery instructions)
1. Edit /tmp/opencode/wt-iter88/engine/diallux/prompts/Intake.md line 35: replace
   `#[refer pain-points-kb for the empathic mirror — {{pain_frame}}]` with the
   T0-approved line (default:
   `#[refer pain-points-kb — missed calls, lost bookings — {{pain_frame}}]`).
   THEN the census-approved rewrites for the sibling tags (owner wordings at T0;
   defaults:
   - Discovery.md pain-points tag:
     `#[refer pain-points-kb - missed calls, lost bookings, conversion loss - {{pain_points}}]`
   - Discovery.md sales-language tag:
     `#[refer sales-language-kb - objection and deferral handling - {{pain_frame}}]`
   - Offer.md tag:
     `#[refer sales-psychology-kb - re-anchor pain and leak cost - {{pain_frame}} / {{monthly_leak}}]`
   - Closer.md tag:
     `#[refer sales-psychology-kb - the leak cost, lost revenue - {{weekly_leak}} / {{monthly_leak}}]`
   Scope = the refer-tag anchor texts ONLY, in both files.
2. SAME COMMIT: replace llm.json's Intake state_prompt with the EXACT full Intake.md
   content (byte-sync the mirror — closes the existing drift; json-escape properly).
3. pytest: `.venv/bin/python -m pytest tests -q` → 3 stale reds ONLY (count FAILED lines).
Verification: diff = 2 files exactly; suite 3 stale reds.
Unblocks: T4.

### T4 — 9-state parity pin (test-only, 20 min)
1. Widen test_iter43_prompts.py: parametrized test — for ALL 9 states
   (Intake, Discovery, Closer, Offer, contact_details, ConfirmSlots, VerifyLead,
   Booking, Closing): `states[].state_prompt == prompts/<Name>.md`.
2. If any state ≠ md (expected: NONE after T3's sync): STOP, report the drift, owner call.
Verification: new pin green; suite unchanged (3 stale reds).
Unblocks: T5.

### T5 — chat battery + PT-75 doc + ledger + report (45 min)
1. Chat battery: harness personas (the drill set + happy), --slots mock --rag --langfuse.
   Gates: (a) Intake rag chunks > 0 on refer-bearing rounds (the KB-less fix verified —
   pull the rag plane: ledger rag rows for the run); (b) reveal discipline per T2 census;
   (c) suite 3 stale reds.
2. Import run to ledger (live_sql.py import --run chat-iter88 ... --branch
   engine/iter88-chat-leak-drill --commit <sha>; micbridge import trap does NOT apply —
   chat lane = llm2llm-graph-* names).
3. PT-75: write /home/julio/projects/clean_diallux_SDR/docs/prompt_llm_json_lockstep.md
   (the riddle: md = runtime truth per-call; llm.json = fallback + Retell parity; edit
   rules; the iter64c dead-model-field lesson; the refer-tag parser reads md ONLY).
4. Report /home/julio/projects/clean_diallux_SDR/research/surgeon/iter88-chat-leak-drill/
   01_verdict.md; close PT-74/76 (+ PT-77 with the pattern verdict); update master ladder
   STATUS + NEXT_STEPS; commit docs to LOCAL main line.
Verification: rag chunks > 0 (SQL row), suite green-ish, PT rows closed.
Unblocks: HITL close.

## Validation Plan (end-to-end)
T0 GO → T1 worktree → T2 census (zero TTS) → T3 one-line + mirror sync → T4 9-state pin
→ T5 chat battery: Intake rag chunks > 0 + reveal census + suite 3-stale → ledger rows →
docs → HITL. Abort/rollback: T3/T4 are prompt+test only — `git checkout` the two files in
the worktree; no config touched; lanes not involved (chat = no ports).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Heavy prompt engineering (owner's own plan) | owner: separate session AFTER this one |
| Mic battery on the fixed prompts + owner ear A/B | after heavy prompting (avoid double spend) |
| R5.5 in-generation dupes + re-ask loops + contact_details dedupe-exemption tuning | pre-existing both trees; owner design call (PT-73 law: smallest fix) |
| S2L spike surface (hysteretic trim re-bill) | next latency surface, own session |
| GitHub push (merge 730dfdb + docs) | FROZEN BOX until owner rotates the PAT |
