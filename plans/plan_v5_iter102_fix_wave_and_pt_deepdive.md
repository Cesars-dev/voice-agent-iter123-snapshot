# iter102 fix wave — the real-call bug ledger closes (FIND-33..40) + pending-task deep-dive

## Meta
- Date: 2026-10-08 (written at the tail of the iter97/98 validation-close session; executes as its OWN session on owner GO)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: (T0) deep-dive the surviving pending tasks (are they applied? value? reference report? truly open?) → verdict table; (T1–T5) fix the five data-backed bugs found on the real Oct-6 + Oct-8 calls as ONE cleaner wave on branches 102–106 in the owner's priority order; (T6) test-infra smalls; (T7) close-out.
- Status: PLAN ONLY — awaits (a) the current session's T1 real-call dial + T2 merge of `engine/97-implementation` (precondition, see BLOCKED), (b) owner GO on this plan.

## Compaction Context (verbatim session state as of 2026-10-08 23:5x UTC)

### Where things stand
The Dialux SDR v5 engine (LangGraph voice: Twilio/media WS → Deepgram flux STT → graph → gpt-5.4 → SentenceGate → ElevenLabs) ran its first real-transport validation session and produced a data-backed bug wave. Two REAL calls carry the evidence:
- **Oct-6 09:21 call** CA93823104f61c20d6 (548 s, OR `:8050` @ `06bdd97`, the live-validated iter93/94/95 test-merge; Langfuse trace `152d98c0c8d73f27680d950f2914e1bb`) — the "worked okay-ish, ~1,882 ms p50" call. Proves: the tool-result continuation rounds SPEAK AGAIN in the caller's window (09:26:00→09:26:04 and 09:27:30→09:27:34 — the caller said ON TAPE "you asked and answered yourself" @09:28:01 while his complaint got echo-recorded 3×), and the fast-number complaint ON TAPE ("I didn't get the number. Can you slow down?" @09:26:38; agent conceded "I may have said too fast").
- **Oct-8 22:45 call** CAcf047fe3fd9075 (355 s, same lane, trace `be7bb8e7404b76d2c0b50ddc9636e4d2`) — the warmup call. Proves: SentenceGate `_FLUSH_LEN=140` hard-cuts MID-SENTENCE (52 speak() batches / 23 turns, avg 2.26; 11 turns cut at exactly char 140 mid-clause — FIND-38), user-echo inserts on the eager-adopt path (FIND-37: one utterance → 2–3 history variants at 22:48:43/22:48:57/22:50:53), canned RAG re-fire (FIND-35: 17 identical canned queries, same top-3 every turn, 15×, 6 empty-query ceremony fires), and STT micro-turn plunge (FIND-39's fragmentation arm: caller burst split into STT turns 6/7/8/9 → three full agent turns T05/T06/T07 in 13 s).
- Analysis errors made and CORRECTED this session (do NOT recommit them): the "eager speak/record divergence" exhibit was a mis-pairing — 22/22 spoken==recorded verified by `/home/julio/projects/clean_diallux_SDR/engine/scripts/lf.py pair` (committed `c877e51`, subcommand `pair <trace_id>`: machine spoken-vs-recorded pairing + second-batch detection + variant-aware user echo inserts). The final report key `eager_final_match` compares the eager turn's transcript basis vs confirmed EOT; audio is HELD until EOT (match → adopt == spoken == recorded; mismatch → rerun).

### Endpoint / infrastructure state (as left)
- Twilio webhook for +1 888 595 8927 (sid PNd8751d5abe7cf5f680700679a4df8a08): `https://voicetest.diallux-ai.site/twiml` (API-set; basic-auth creds at `/opt/diallux-production/.env` keys `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`; never print them). OWNER DECISION on record: Oregon is now the official dialing place; FI `twilio.diallux-ai.site` → `/opt/diallux-production` (:8026, 2026-09-22 snapshot) is the OLD standing endpoint (detour consumed the first test calls; documented in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/00_endpoint_map.md`).
- OR Caddy `/etc/caddy/Caddyfile` voicetest block routes `/twiml` + `/media` → `127.0.0.1:8069` (97-alone lane, live); backups: `Caddyfile.bak.iter97val.1791498124` (flip to 8069), `Caddyfile.bak.iter95restore.*` (flip to 8050). OR `/etc/caddy` is NOT git-tracked.
- OR `:8069` = `/tmp/opencode/wt-97/engine` @ 97 `6044b9f`, booted via `cd /tmp/opencode/wt-97/engine && set -a && . ./.env && set +a && (setsid .venv/bin/uvicorn diallux.app:app --host 127.0.0.1 --port 8069 > /tmp/opencode/lane-8069.log 2>&1 < /dev/null &)`. Lane `.env` received TWO agent-appended lines (gitignored, disclosed): `PUBLIC_BASE_URL=wss://voicetest.diallux-ai.site` (was missing → code default `wss://your-domain.example.com` → TwiML garbage → busy/no-answer) and `AUDIO_TRANSPORT=twilio` via sed (was `browser` → mulaw@8000 STT vs linear16→ deaf+silent calls). **OR canonical `/home/julio/projects/clean_diallux_SDR/engine/.env` line 37 still says `AUDIO_TRANSPORT=browser` — OWNER must ratify flipping the canonical to `twilio` (agents never edit the canonical), else every new lane regenerates the deaf-silent bug.**
- The T1 97-alone real-call dial is STILL PENDING (owner): lane is up, endpoint pointed; after the call → forensics → CHECKPOINT → merge 97 → squash carrier `engine/100-tier-squash` → call #2 → merge (the live plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_98_validation_merge.md` T1–T7).

### Findings (ledger `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`, table `findings` — 41 rows; OPEN actionable):
FIND-37 (P0 echo inserts, adopt path), FIND-39 (P1 tool-result continuation speaks + micro-turn plunge; PT-69 merged-turn trim + PT-70 acks NEVER BUILT — verified absent in `06bdd97`), FIND-38 (P1 140-char mid-clause cut), FIND-35 (P1 canned-query re-fire; historical NULL-id row = the original FIND-35 book-livecall phone-match bug, needs id normalization), FIND-40 (P1 numeral pacing, ear-confirmed), plus test-infra FIND-33 (stale `run_offline()` script) / FIND-34 (chat battery ran eot not hybrid — config default flip rides the iter65 branch, resolves at T2 merge) / FIND-36 (CHECK-ONLY — the divergence probe stays as a mandatory mechanical, run via `lf.py pair`).
- Pending-task sweep DONE this session in `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md`: 18 rows + 2 banners tagged `DEPRECATED 2026-10-08`, 16 rows tagged `SECONDARY 2026-10-08`, 4 rows (PT-61..64 iter65 era) tagged hot-zone-deprecated (owner: do NOT touch that era). Surviving core = PT-68, PT-69, PT-70, PT-74, PT-79, PT-81, PT-72, PT-75, PT-76, PT-73 (law row), PT-56.

### Resolved context facts
- Suite truth: 97 tip = `517 passed / 1 skipped / 5 failed` (identical red set); squash carrier = `526/1/5`. `engine/100-tier-squash` + `engine/101-split-round` numbers RESERVED by the live plan; this wave starts at 102.
- Tracking SDK (`engine/scripts/lf.py pair`, commit `c877e51` on session branch `engine/iter97-research-adaptation`) already reports spoken/recorded pairs, second-batch, echo inserts. Evidence dirs (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/`.
- Supported env for tests: FI checkout `/home/julio/projects/clean_diallux_SDR/engine/.venv` (py 3.12, stdlib scripts only for ledger). LANE LAW on OR: lanes via `bash scripts/new_lane.sh <NN> <base> <slug>`; `.env` = canonical-generated.
- OR box: `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`. FI box = this one.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Fix order = 37 → 39(+PT-69/70) → 38 → 35 → 40 | Owner P0 first (context pollution feeds everything), then the transition re-speak he confirmed twice on tape, then the mangle machine, then RAG efficiency, then pacing (ear-confirmed but least mechanical). |
| ONE new session, plan-first (this file), wave branches 102–106 | Owner: "We will carry the fixes… to a new plan/branch… then another session"; numbering 101 reserved to split-round. |
| Each FIND = ONE branch, ONE variable — no grab-based fixes from hot-zone branches | Owner post-mortem law (PT-73): smallest change, prompt-first, env-knob-first; branches 65-68 = polluted hot zone (do NOT cherry-pick). |
| The transition fix follows the owner's on-record design | "As long as we detect a question, we chop the rest of the TTS and confirm to the model what was spoken" — the model's view of history == what the caller heard. |
| PT deep-dive (T0) runs FIRST, analysis-only, zero-code | Owner: tasks may already be applied or dead; verdict table gates which extras ride the wave branches. |
| Test-infra items (FIND-33/34 + PT-75/76 adjacent) ride the whitelist lane | `scripts/fast_suite.sh --touched` gate, commit straight to main (v2.3 law). |
| Oregon = the official dialing endpoint going forward (stated owner) | The validation_close plan's Deploy Rules already honor it; the canonical env ratification is owner-set. |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| T1 dial + T2 merge of the current plan (97) must COMPLETED FIRST | owner dial + `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_98_validation_merge.md` checkpoints |
| OR canonical `AUDIO_TRANSPORT=twilio` ratification | owner edits `/home/julio/projects/clean_diallux_SDR/engine/.env` line 37 on OR (or orders it); agents never edit canonicals |
| GO on this plan (owner reads it) | this file |
| EL numeral word-old preference ("twelve fifty" vs "one thousand two hundred fifty") | owner ear pick during T5 verification |
| FIND-35 fix semantics (skip-same-query vs topic-shift refresh) | the plan proposes the skip-guard + delta-refresh; owner confirms at T4 gate |

## Environment & Dependencies
- venv (engine, canonical): `/home/julio/projects/clean_diallux_SDR/engine/.venv` (python 3.12; pip via `-m pip` only).
- Suite: `cd /tmp/opencode/<worktree>/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1` → expect `5 failed, 517 passed, 1 skipped` (the byte-identical red set) unchanged by all wave branches (each pin adds tests, suite count grows by its pin count).
- Langfuse: `/home/julio/projects/clean_diallux_SDR/engine/scripts/lf.py` (pair/gens/show), evidence in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/` (gitignored).
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db` (`python3 /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py --db <db> sops/findings`).
- Lane opener (on OR): `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh <NN> <base> <slug>`; ports: 102→:8071, 103→:8072 (provisional; never touch :8000-8003, :8020/21, :8024, :8025, :8026, :8049/50, :8063/65/66/67, :8068, :8069, :8070).
- LADLE of truth per fix = the two recordings' transcripts (compact: `/tmp/opencode/oct6_transcript.txt`, `/tmp/opencode/call_cf047_transcript.txt` — regenerate any time via `lf.py gens <trace>=152d98c0c8d73f27680d950f2914e1bb` / `=be7bb8e7404b76d2c0b50ddc9636e4d2`).

## Architecture
```
main (post-T2/T3: engine/97 + 100-tier-squash merged; tagged engine/iter97 / engine/iter98)
   ├─ engine/102-echo-accounting   (FIND-37 P0: adopt-path history write)
   ├─ engine/103-turn-segregation  (FIND-39 + PT-69 + PT-70: asked-question chop + spoken-aligned history)
   ├─ engine/104-gate-clause-cut   (FIND-38: SentenceGate clause-boundary cut)
   ├─ engine/105-rag-refire-guard  (FIND-35: same-query skip + delta refresh)
   └─ engine/106-numeral-normalize (FIND-40: normalize.py numerals)
 each cut from current main at ITS OWN turn (serial merges per LAW 0: branch → suite → pin → ASK → merge/tag iter102..106)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102_fix_wave_and_pt_deepdive.md` | this plan (commit to main NOW, docs lane) | NEW |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | already tagged this session; T0 appends verdict columns | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/plans/NEXT_STEPS.md` | queue refresh pointing at this plan (T7) | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/00_pt_deepdive.md` | T0 verdict table | NEW (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` | T1 adopt-path user-history write (FIND-37) + T2 hold/chop + spoken-aligned history (FIND-39/PT-69/70) | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` | T2 round-loop ask-chop helper + tool-continuation speak gate | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py` | T3 `_FLUSH_LEN` → clause-boundary cut | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/tests/test_iter102_*.py` … `test_iter106_*.py` | one pin file per branch (echo replay, ask-chop, clause cut, refire guard, numerals) | NEW (branches) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/normalize.py` | T5 numeral expansion ($ amounts, dates, times) | EDIT (branch) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/harness.py` | T6 FIND-33 `run_offline()` re-script | EDIT (whitelist) |

## Deploy Rules
- Every branch: cut per `scripts/new_lane.sh` on OR; test on FI worktree (FIA venv); suite gate pre-commit (`--touched` for whitelist items); battery = the `lf.py pair` + turn reports on the lane's real or mic transport; ASK Julio (LAW 0) before ANY merge; ONE `--no-ff` merge + tag `engine/iterNN` + `scripts/git-tree.sh` per landed branch.
- CHANGE POLICY on `.env`: agents NEVER edit canonical envs; new run knobs must have code defaults matching the tested value (SWITCH LAW rule 4).
- The T0 verdict table is ANALYSIS ONLY; any NEW prompt/row edit for PT items (e.g. PT-74 Intake.md refer-tag fix) rides its own numbers AFTER the wave (or ASK owner to fold into 103).
- What is NEVER touched: sessions/prompts outside the named hunks, `engine/diallux/prompts/** EXCEPT Intake.md via explicit owner say-so, `services/`, ports listed above, the OR protected root checkout (`engine/iter73-oregon-wip-20260924`), FI prod `/opt/diallux-production`, `agent_16985b5d087e56c35141983396`, `agent_87e4d5f08475e5bc558b2f390f`, the hot-zone branches (`engine/iter68-speech-flow`, `engine/iter68-speech-lite`, `engine/iter65-*` chain etc.).

## Tasks (in order)
### T0 — Pending-task deep-dive (analysis, zero-code)
Goal: for each surviving PT (68, 69, 70, 74, 79, 81, 72, 75, 76, 56, + SECONDARY on request: 31, 32, 50, 87, 01-08 heating): verify against current code whether ALREADY APPLIED (grep + line refs), what value it adds, best reference report, then verdict: `APPLIED | RIDE-<branch> | DEFER | DROP (redundant/hypothetical)`.
Commands: `git -C /home/julio/projects/clean_diallux_SDR log --oneline -S "pause_ladder" engine/diallux/media/session.py | head` etc per mechanism; floor: every verdict carries evidence (grep line, report path, or commit sha).
Deliverable: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/00_pt_deepdive.md` with the verdict table + which PTs fold into which branch (expected: PT-69/PT-70 fold into 103; PT-79 folds into the `pair` SDK followup; PT-81 rides 103 or its own later branch).
Verification: every OPEN row in the PT file gains a verdict comment (docs edit, straight to main).
### T1 — engine/102-echo-accounting (FIND-37, P0)
Goal: the confirmed-EOT final transcript REPLACES the eager-fragment user entry within the same turn — the model's history sees ONE user message per utterance.
Edit: the history/turn-state write on the EOT adopt path (current code: both variants appended — replicate the Oct-8 22:48:43 shape in a unit test first).
Pin: `test_iter102_echo_accounting.py` — two EOT snapshots (fragment `Yeah. Exactly. That I'm missing business` then final `Yeah. Exactly. That I'm missing business. So how much…`) → history holds exactly one user entry (the final).
Suite gate: red set unchanged; lane smoke via `lf.py pair` (echo count 0) on a scripted mic-caller run.
### T2 — engine/103-turn-segregation (FIND-39 + PT-69 + PT-70)
Goal: (a) a question released by the gate CHOPS the rest of the stream for that round (gate.hold + drop), (b) tool-result continuation rounds DO NOT SPEAK unless new caller input or decisive tool data exists — they transition silently, (c) history aligns to SPOKEN ONLY (the owner's verbatim design), (d) merged-turn trim: >2 questions in one turn → trim to one (prompt+builder hook).
Edit: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py` (writer/chop + history align) + `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (continuation-round speak gate + trim hook).
Pins: `test_iter103_ask_chop.py` (streamed round ends `?` mid-tail → spoken history stops at the question), `test_iter103_continuation_silent.py` (calculate_monthly_leak continuation speaks NOTHING when the turn already asked), `test_iter103_merged_turn_trim.py`.
Gate vs data: replay Oct-6 09:27:30→09:27:34 window shape — the second round must not add speech.
### T3 — engine/104-gate-clause-cut (FIND-38)
Goal: `_FLUSH_LEN=140` fires only at the LAST clause boundary (`,` `;` `—` or sentence-end) ≤140; hard mid-word cut only as a safety valve ≥170.
Edit: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/sentence_gate.py`.
Pin: `test_iter104_clause_cut.py` — T20's 233ch single-sentence replays: batch boundaries at clause ends, no cut inside a word/clause; latency unchanged (streaming preserved).
Gate vs data: gate simulation on ALL 23 spoken texts of CAcf047 → 11 mid-clause cuts → 0.
### T4 — engine/105-rag-refire-guard (FIND-35)
Goal: no per-turn re-embed of an unchanged canned query: if the normalized query for the lane == the last consumed query for that state and no NEW caller delta arrived → reuse the consumed set (skip the fire); fire on caller-text change (delta refresh).
Edit: `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py` (lane fire guard at the fire sites) — mirror the `_live_merged_turn` same-msg stash semantics.
Pin: `test_iter105_refire_guard.py` — three identical queries → 1 fire, 2 reuses; a content delta → new fire.
Gate vs data: the cf047 shape (17 identical) → 1 fire + 16 reuse; rag table rows shrink; dispatch→first p50 unchanged.
### T5 — engine/106-numeral-normalize (FIND-40)
Goal: deterministic expansion before TTS socket: `$1,250` → "twelve hundred fifty dollars" (owner picks the wording), dates `04/20/2026` → "April twentieth twenty twenty-six", times; phone-style rules unchanged.
Edit: `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/normalize.py` (+ pin).
Pin: `test_iter106_numeral.py` — the Oct-6 leak math line renders expanded.
Gate vs data: an EL-side A/B synthesis on the 102 lane for the owner's ear ("$1,250 a week" vs expanded) — owner verdict optional.
### T6 — whitelist smalls (FIND-33)
Goal: `run_offline()` re-scripted to current prompts so the offline smoke passes hermetically.
Edit: `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/harness.py`.
Gate: `scripts/fast_suite.sh --touched` pass; commit straight to main (whitelist law).
FIND-34 resolves automatically at the current plan's T2 merge (code default hybrid @ iter65 branch comes in).
### T7 — Close-out
Sequence: update PT statuses per T0 verdicts; `NEXT_STEPS.md` queue refresh (standing = 97+carrier merged; next = this wave order); ITERATIONS.md ledger lines on main post-merge; commit registry refresh (backup ledger.db first, `git show engine/iter47-call-ledger:scripts/call_ledger.py` ritual); plan Status → EXECUTED; keyhound before every push; all evidence under `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter102-fix-wave/`.

## Validation Plan (end-to-end)
1. Every branch: red set byte-identical (517/1/5 base growing only by its own pins).
2. Each fix carries a DATA gate stated from the two real calls (echo count, continuation speaking count, mid-clause cuts, rag re-fires, numeral render) — no fix accepted on feel.
3. The two real-call transcripts cannot be regenerated live — the pins REPLAY their shapes in unit tests; a final real dial per the endpoint plan (webhook → fresh lane) re-verifies live before the wave's final merge.
4. Merge discipline per LAW 0: branch → suite → pin → battery probe → ASK → merge --no-ff → tag → git-tree → ITERATIONS line.
5. No prompt or KB file changes on any branch except the EXPLICIT PT-74/PT-70 prompt hunks IF the owner folds them (say-so recorded first).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| `engine/101-split-round` build | reserved, gated by the 100_design addendum + owner research |
| PT-74/PT-70 prompt changes | only on owner say-so to fold into 103 |
| Heating items (PT-01..08) | other agent's lane; owner priorities there are separate |
| Deepgram EOT knob tuning | owner-deferred (biggest lever; interacts with FIND-39 fragmentation) |
| `engine/100-tier-squash` T4 carrier validation | belongs to the CURRENT plan's checkpoints, not this wave |
| Fast-tier pricing truth | owner/OpenAI page |
