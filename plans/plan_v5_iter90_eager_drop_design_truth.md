# plan_v5_iter90_eager_drop_design_truth — READ-ONLY forensics: find the "drop any turn that does not make it to EOT" design in the ledger/code, determine why the iter90 A/B turns behave as if it never existed, and deliver a cited verdict. NO design changes, NO new plans, NO commits beyond this file and one memo.

## Meta
- Date: 2026-10-03
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland/MainVps. ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Scope: evidence preservation + ledger findings archaeology + code-path truth @ `30405ad` + switch-state diff vs the successful iter87 battery + log-to-code attribution of the B0/B250 multi-round turns → ONE verdict memo. Read-only forensics.
- Status: EXECUTED 2026-10-03 (T1-T6 complete). Verdict: research/surgeon/iter89-prompt-enhancements/94_eager_drop_design_truth.md — DROP DESIGN = eager_hold_audio_until_confirm (iter85 b97957f; old kill+refire DELETED @542d3e8); DORMANT in the A/B (env line absent); iter87 ran it ON (boot-script export, 23 silent discards in lane journals); A/B rounds 2/3 = designed FSM tool chain, not eager artifacts; 250/2500 unrelated (ack-await only); verdict = SWITCH DRIFT. Remediation = options in the memo, owner picks.
- OWNER DECISION 2026-10-03: options 1 (A/B re-run) and 4 (wire cache dump) DROPPED. Fix = ONE commit: scrub 250→2500 in both .envs + promote the full iter87 round-B pack to defaults (no lane boots without it). Verify = ONE GK stress persona. FIND-37 recorded (rowid 37, ledger backed up). iter91 skeleton: rewrite around this fix, do not execute as-is.
- DRIVER LAW (owner 2026-10-03, revised): verification test = ORIGINAL `llm_mic_caller.py` (vanilla — it drives calls fine; the A/B's bugs were evidence-capture: launcher reused one `--out`, journal redirected). b52 = barge-loop stress variant ONLY, stays on `engine/iter82-pause-nudge`, not needed. Rules: DISTINCT `--out` per run; ground truth = server log + Langfuse. NO A/B, NO b52 — the iter91 = flip the switches (250→2500 + promote pack defaults), run the GK, prove it worked. ENV-SWITCHES.md updated same day (250 corrected to 2500; driver law revised).

## Compaction Context (from the 2026-10-03 iter90 session — read this BEFORE forming any theory)

**Owner's claims (verbatim, to VERIFY not re-litigate):**
1. "We were doing eager EOT calls async — if one was launched and then another, we were not stupid enough to make a whole brand new call. We just killed it, used our pre-cached tokens and re-fired the llm input call."
2. "That async design was replaced by a 'drop any turn that does not make it to EOT' — made specifically to avoid this kind of disaster. We could fire 1000 eager EOTs and we would just pay the latency for the EOT one."
3. "We logged every battery, every iter and every commit on a SQLite DB" (the findings table in the call ledger — the fix's paper trail is THERE).
4. The EOT 250/2500 knob has NOTHING to do with this disease (owner: "that has nothing to do with the EOT 250 or 2500").
5. "Stop making plans that poison the design" — no new plans/commits without owner GO. The iter91 skeleton already on main is FROZEN-SUSPECT (see Errors).

**Verified facts this session (cited — these are NOT theories):**

*Runs:*
- B0 (knob 0): 2026-10-02 12:28, sid `c5aed8b0d1e4`, trace `eef77fed30a360e83cf36581c5681f07`, 12 caller turns / 18 llm rounds (7×1-round, 4×2-round, 1×3-round), full FSM chain, stop `turn_cap_goodbye`. Log: `/tmp/opencode/voice_server_8030.log` (final reports at lines 41/54/70/86/101/120/138/156/171/190/207/224). B0 raw json LOST (`--out` overwrite; launcher `/tmp/opencode/iter90_run_mic.sh` hardcodes `/tmp/opencode/iter90_mic_gk_boris.json` = now B250's).
- B250 (knob 250): 2026-10-03 05:59, sid `c866214c53fc`, trace `f97167e5f27308672085048ef6223fcf`, 12 reported turns (t4 barge-cancelled, log L76) / 15 rounds (10×1, 1×2, 1×3), never left Discovery. Log: `/tmp/opencode/voice_server_8030b.log`.
- iter87 successful battery (the owner's reference "everything worked"): `research/surgeon/iter87-prewarm-hold/sdk_happy_a4de3446.txt` era, lanes 8047/8048, `WARM_AWAIT_DEST_MS=2500` + "round-B knobs" (FULL KNOB LIST NOT YET PULLED — T2 must get it from `plans/plan_v5_iter87_prewarm_owner_design.md` + the iter87 surgeon folder). Langfuse: happy = prefix `a4de3446`, barge = prefix `e25675a5` (resolve full ids by scanning `/api/public/traces` pages). Rounds-per-turn: happy 28 turns/43 rounds (16×1, **12×2, 1×3**), barge 38/53 (24×1, 13×2, 1×3) — **multi-round turns ALWAYS existed at the same distribution as iter90**. Waits on landed warms 994–1605ms (the "waiting way too much" the owner remembers), 0 timeouts, cache-hit p50 4736. Merged to main @ `730dfdb` ("Real_MVP", owner say-so 2026-09-30).
- Driver difference: iter87 battery used `llm_mic_caller_b52.py`; iter90 A/B used `/tmp/opencode/wt-iter89/engine/scripts/llm_mic_caller.py --scenario happy --persona Boris --agent-idle-s 4` (gpt-4o-mini brain + TTS audio).

*B0 turn 8 (the 4519ms turn) exact sequence (log lines 110-158):*
- `12:30:57.669` StartOfTurn (caller starts) → `12:30:58.510` eager turn started (**840ms INTO the utterance**) → `12:30:58.540` eot adopted (no rerun) → `12:31:00.149` round 1 Discovery input=4476 cache=3712 ttft=663 output=98 → `12:31:00.154` await_warm cap=100 already_done → `12:31:01.899` round 2 Discovery input=4826 (**+350**) **cache DROPPED 3712→2688** ttft=1676 output=99 → `12:31:03.000` warm done Closer ms=1167 → `12:31:03.175` round 3 Closer input=4986 (+160) cache=3712 ttft=723. **NO StartOfTurn and NO eager marker between rounds** — rounds 2/3 trigger UNPROVEN (tool rounds vs caller continuation vs adoption path = T5's job). Turn report: `resumed_count=0`, `resume_pending=false`, `eager_final_match=true`, `barge_in=false`.
- B250 t8 mirrors it: 3 rounds Intake+Intake+Discovery, r1 **cache=0** (turn 8 = TRIM_STEP=8 first trim boundary — candidate: hysteretic history trim, same class as iter87's single cache-0 at turn 61), r2 cache 2688; await_warm Discovery `outcome=timeout waited_ms=250 cap_ms=250` @06:01:24.853 (the ONE paid hold — warm landed 06:01:25.775, AFTER r3's llm started 06:01:24.863).

*Code facts @ `30405ad` (wt-iter89):*
- `diallux/config.py:214` `prewarm_entry_wait_ms=100`; `:219` `prewarm_entry_wait_eot_ms=500`; `:226` `warm_await_dest_ms=0` (comment: "iter87 VERSION B (fire + hold), knob-gated as ONE unit... Lane/battery runs 2500 (> measured warm worst case 2059 ms)"); `:~228-233` **`eager_hold_audio_until_confirm: bool = False`** — comment: "FIX 1 (PORT 1): eager-think, confirmed-speak — hold the eager turn's AUDIO at the sentence gate until the confirmed EndOfTurn adopts it; TurnResumed discards silently (nothing was ever spoken). Default off = byte-exact today behavior; rollback = env off." ← **CANDIDATE for the owner's "drop" design: present, code-default OFF.**
- wt-iter89 `.env` (grep verified 2026-10-03): `WARM_AWAIT_DEST_MS=250`, `DEEPGRAM_EAGER_EOT=true`, `DEEPGRAM_EAGER_EOT_THRESHOLD=0.7`, `TTS_PROVIDER=elevenlabs` Sarah test voice, `TTS_GATE_FAST_FIRST_FLUSH=false`, `TTS_DEDUPE_SEMANTIC=false`, `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27`, `OPENAI_MODEL=gpt-5.4`. **NO `EAGER_HOLD_AUDIO_UNTIL_CONFIRM` line, NO `PREWARM_ENTRY_WAIT_*` lines.** Whether the iter87 battery lane env SET the eager-hold line = UNKNOWN, T2.
- `diallux/graph/builder.py`: `_await_warm` :633; entry holds :1841-1874; one-ahead fire :2575-2590; chain warms :2700-2760 (all three warm-plane extras gated `warm_await_dest_ms>0`).
- Langfuse spans observed in both A/B traces: `eager_hold:fire` (1:1 with turns), `await_warm`, `turn:N`/`turn:N:final`, `llm:<State>`, `tool:*`, `rag`/`rag:pin`, `tts_first_byte`, `eot_silence_wait`. **No span ever logged a resume/drop event** (consistent with resumed_count=0 — but ALSO consistent with the drop path being absent/uninstrumented — T3 decides).

**This session's ERRORS (on record, fresh agent must not repeat):**
1. On 2026-10-02 (prior session) I wrote `WARM_AWAIT_DEST_MS=250` when the owner said "turn it on" — the iter87-proven value is **2500** (config comment + iter87 battery). Wrong value, my error.
2. I reported "iter87 had ZERO multi-round turns" — **RETRACTED**: that was a span-occurrence miscount; proper attribution shows 12×2-round + 1×3-round in the successful run (same distribution as iter90).
3. I theorized about mechanisms (driver×eager artifact, SOT fire law) **before querying the ledger findings table** — the findings table was NEVER queried this session. The owner built that ledger exactly so this doesn't happen. LEDGER FIRST, ALWAYS.
4. I committed an iter91 skeleton + PT rows + ENV-SWITCHES edits (commits `79f8669`, `d9616c6`, `be7b934`, `35a9bd8` on main) as part of iter90-plan T3-T5. The owner has flagged unapproved plan-making. **`plans/plan_v5_iter91_defaults_and_warm_decouple.md` is FROZEN-SUSPECT: do NOT execute, do NOT extend; its rationale (SOT fire law, driver×eager artifact) came from the challenged analysis and must be re-validated against T6's verdict before ANY of it is used.**

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| LEDGER FIRST: query findings/sessions/runs tables BEFORE any code reading or theory | owner's explicit demand; the fix's paper trail is in the DB (every battery, iter, commit) |
| Read-only forensics; the ONLY writes = evidence archive + one memo (research/ zone) + this plan file | no code, no .env, no services, no new plans (owner: "stop making plans that poison the design") |
| Owner's design claims = hypotheses to verify with citations, never to re-litigate or "improve" | the design was ratified before; this session finds WHY it's not behaving as designed |
| 250 vs 2500 treated as SEPARATE question (ack-timing plane) — must not contaminate the drop-design verdict | owner: "nothing to do with the EOT 250 or 2500"; verify, don't assume |
| iter91 skeleton FROZEN-SUSPECT until this verdict lands | challenged analysis; nothing on it may be executed |
| Multi-round turns existed at the same distribution in the successful run (table above) | measured, retraction already issued; do not re-assert "re-rounds are new" |
| No merges, no branch cuts, no keyhound-relevant pushes in this plan | LAW 0 + read-only scope |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO on this plan | owner's word in-chat |
| Any remediation (env value writes, iter91 edits, code fixes) | owner AFTER T6 verdict — this plan ends at the verdict |
| Whether `/tmp` evidence logs still exist (reboot risk) | T1 preserves them FIRST; if already gone, reconstruct from Langfuse traces + this plan's Compaction Context |

## Environment & Dependencies
- OREGON ssh wrapper (Meta). No `sqlite3` CLI anywhere — always `.venv/bin/python -c "import sqlite3; …"` with the OREGON venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (copy-mirror venv — never bin/pip).
- Ledger (findings/runs/calls/rounds/rag/sessions): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db` — read `research/surgeon/iter48-rag-truth/SQL_ANALYSIS_SOP.md` FIRST (schema + query discipline).
- Branch/iteration registry: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db` (branches/commits).
- Code under test: `/tmp/opencode/wt-iter89/engine/diallux/` @ `30405ad` (branch `engine/iter89-prompt-enhancements`, pushed to GitHub).
- Evidence logs (PRESERVE IN T1): `/tmp/opencode/voice_server_8030.log` (B0), `/tmp/opencode/voice_server_8030b.log` (B250), `/tmp/opencode/iter90_mic_gk_boris.json` (B250 driver json; `journal_lines` field STALE — never cite), `/tmp/opencode/iter90_run_mic.sh` (launcher).
- Langfuse: env at `/tmp/opencode/wt-iter89/engine/.env` (`LANGFUSE_HOST/PUBLIC_KEY/SECRET_KEY`; host http://46.62.233.228:3001; Basic auth base64(pk:sk); `/api/public/traces?limit=100&page=N` — paginate client-side, `fromStartTime` param 400s on this build; `/api/public/observations?traceId=<id>&limit=100&page=N`). Trace ids: B0 `eef77fed30a360e83cf36581c5681f07`, B250 `f97167e5f27308672085048ef6223fcf`, iter87 happy/barge = resolve prefixes `a4de3446`/`e25675a5`.
- iter87 design/knob sources: `plans/plan_v5_iter87_prewarm_owner_design.md` (on main), `research/surgeon/iter87-prewarm-hold/{01_battery_verdict.md,02_latency_report.md,03_merge_validation_sop_audit.md,sdk_happy_a4de3446.txt,sdk_barge_e25675a5.txt}`, iter85 evidence = branch `engine/iter85-eager-hold` @ `542d3e8` (surgeon folder: locate via `ls /home/julio/projects/clean_diallux_SDR/research/surgeon/ | grep -i 'iter8[56]'`; also `git log --oneline engine/iter85-eager-hold -5`).
- Prior-session memos (context, may need correction after T6): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/{90_rag_zero_main_verdict,92_boris_ab_hold_verdict,93_deepgram_param_nativeness}.md`.

## Architecture (the eager turn lifecycle as currently UNDERSTOOD — UNKNOWNs marked, T3 replaces this with code truth)
```
caller audio → Deepgram flux (EagerEndOfTurn @ threshold 0.7)
  → eager turn starts (speculative llm round on partial utterance?)
  → [UNKNOWN A: what holds/kills this round when caller continues]
     · owner's design: drop any turn that does not make it to EOT
       (candidate: eager_hold_audio_until_confirm — config default False,
        NO env line in the A/B lane)
  → EOT adopt (eot adopted running eager turn, no rerun)
  → round chain within turn: [UNKNOWN B: what fires rounds 2/3 —
     tool rounds? continuation? adoption?] each round re-fires llm
     with prompt cache (cache_read column proves token reuse 2688-4736)
  → STATE BLOCK rewrite between rounds = cache drop (3712→2688) [UNKNOWN C: which write]
  → warm planes (fire-at-detection · post-execute · one-ahead gated by knob)
  → TTS → turn report (resumed_count=0 everywhere in both A/B runs)
```

## File Map
| File (absolute path) | What | New/Edit |
|---|---|---|
| /tmp/opencode/wt-main-docs/plans/plan_v5_iter90_eager_drop_design_truth.md | this plan (docs→main, the ONLY git write) | NEW |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/evidence_2026-10-03/ | T1 archive of both logs + driver json + launcher (untracked research/) | NEW (evidence) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/94_eager_drop_design_truth.md | T6 verdict memo (untracked research/) | NEW |

## Deploy Rules
- READ-ONLY: no code, no .env (agents NEVER edit .env — register law), no services, no branch cuts, no merges.
- Allowed writes: the evidence archive + the memo (research/ zone = append-only evidence) + this plan file on main via `/tmp/opencode/wt-main-docs` (push with `git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'`; the repo-level relative helper's "unable to open .git/gh-creds" fatals are known-harmless noise).
- NEVER touch: Oregon main checkout git state (`df23d37` = PROD), Finland main checkout's 3 dirty files (AGENTS.md, plans/NEXT_STEPS.md, plans/PENDING_TASKS.md), the frozen iter91 skeleton.
- The temp 8030 lane was already dead on 2026-10-03 (verified) — do not boot it for this plan; forensics runs on preserved logs.

## Tasks (in order)

### T1 — Preserve the evidence before anything else
Goal: /tmp is reboot-volatile; the A/B logs are the only ground truth for round triggers.
Commands: `ssh … "mkdir -p /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/evidence_2026-10-03 && cp -v /tmp/opencode/voice_server_8030.log /tmp/opencode/voice_server_8030b.log /tmp/opencode/iter90_mic_gk_boris.json /tmp/opencode/iter90_run_mic.sh /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/evidence_2026-10-03/ && md5sum /home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/evidence_2026-10-03/*"`
Verification: 4 files present, md5s recorded in the T6 memo header.

### T2 — Ledger findings archaeology (BEFORE reading any code — LEDGER FIRST)
Goal: the paper trail of the "drop any turn that does not make it to EOT" fix: which iter, which commit, which test, which verdict, which knob.
Commands:
- Read `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/SQL_ANALYSIS_SOP.md` first.
- Schema: `ssh … "cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -c \"import sqlite3; con=sqlite3.connect('../research/surgeon/iter48-rag-truth/ledger.db'); print(con.execute('SELECT name FROM sqlite_master WHERE type=\\\"table\\\"').fetchall())\""`
- Findings search (adapt terms): `… \"SELECT rowid,* FROM findings WHERE lower(coalesce(description,'')||coalesce(issue,'')||coalesce(notes,'')||coalesce(title,'')) LIKE '%eager%' OR … LIKE '%resume%' OR … LIKE '%drop%' OR … LIKE '%turn%' OR … LIKE '%hold%'\"` (inspect actual columns first).
- Cross-ref: branch registry `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter47-call-ledger/ledger.db` for `engine/iter85-eager-hold`, `engine/iter86-*`, `engine/iter87-prewarm-hold` + head commits; `git log --oneline` those branches; read their surgeon folders + `plans/plan_v5_iter87_prewarm_owner_design.md` for the FULL round-B knob list actually set on the 8047/8048 lanes (was `EAGER_HOLD_AUDIO_UNTIL_CONFIRM` set?).
Deliverable: T2 section of the memo — the fix's lineage table (iter → commit → findings row → test → knob → verdict).
Verification: every row cited by rowid/sha; explicitly state whether a findings row for the drop design EXISTS or NOT.

### T3 — Code truth @ 30405ad
Goal: replace UNKNOWNs A/B/C in the Architecture block with file:line facts.
Files: `/tmp/opencode/wt-iter89/engine/diallux/media/session.py` (turn loop), `diallux/graph/builder.py`, `diallux/config.py`.
Questions: (1) enumerate EVERY code path that starts an llm round within a turn (tool round, eager adopt, resume/refire, continuation, knot await) with file:line; (2) what exactly `eager_hold_audio_until_confirm=True` vs `False` changes end-to-end (fire → audio gate → adopt/TurnResumed); (3) does a "kill in-flight eager round + refire with cached prefix" path exist at all in this code, and under which flag; (4) what rewrites the STATE BLOCK between rounds (the 3712→2688 cache-drop writer).
Verification: each answer = file:line citation; no behavioral claims without one.

### T4 — Switch-state diff + lineage check
Goal: why is it biting us NOW — three candidates, pick with data.
Commands: diff table iter87-lane knobs (from T2) vs wt-iter89 `.env` (full grep, not just known keys); `ssh … "cd /home/julio/projects/clean_diallux_SDR && git merge-base --is-ancestor 730dfdb 30405ad && echo IN-LINEAGE || echo NOT-IN-LINEAGE"` (is the iter89 branch cut from the merged Real_MVP main, or an older tip?); also `git log --oneline 30405ad -15`.
Deliverable: the diff table + lineage verdict → which candidate holds: (a) switch drift (a safety line missing in the A/B env), (b) branch-base regression (fix not in 30405ad's lineage), (c) visibility-only (fix active, behavior same, we just never printed per-turn chains before).

### T5 — Log-to-code attribution of the A/B multi-round turns
Goal: with T3's path map, name the EXACT trigger of B0 t8 rounds 2/3 and B250 t8/t11 rounds 2/3.
Commands: parse the archived logs (T1 copies) + Langfuse observations (trace ids above; attribute GENERATIONs to turn spans by startTime) — for each round: trigger path, input delta source (tool result vs caller text — check tool:* obs timestamps and input growth), cache_read, and the STATE-BLOCK write that broke the prefix. The t8 window citations are in the Compaction Context (B0 lines 110-158; B250 lines 124-134 + await timeout 06:01:24.853).
Verification: each round's trigger = code path (T3 citation) + log line + obs id, all three agreeing.

### T6 — Verdict memo
Goal: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter89-prompt-enhancements/94_eager_drop_design_truth.md` answering, with citations only:
1. What is the "drop any turn that does not make it to EOT" mechanism (name, file:line, findings row, iter/commit)?
2. Is it present and ACTIVE in the A/B code+env? (If `eager_hold_audio_until_confirm` default-False + no env line = it was DORMANT in the A/B — say it plainly.)
3. Did the successful iter87 battery run it ON?
4. What fired rounds 2/3 in the A/B multi-round turns (per T5)?
5. Does the 250/2500 knob touch any of this? (Expected: no — confirm or refute.)
6. Why is the disease "back": drift / regression / visibility — which, with the T4 evidence?
7. Retractions/confirmations of this session's claims (Errors list above) and the frozen iter91 skeleton's fate (owner decides: rewrite, keep, or delete).
Verification: every claim traceable to ledger rowid / git sha / file:line / log line / obs id; remediation = OPTIONS ONLY, owner picks; no averages-only claims.

## Validation Plan (end-to-end)
T1 checksums → T2 findings lineage table → T3 code citations → T4 diff + lineage verdict → T5 triple-attributed rounds → T6 memo → owner reads verdict → (owner's call, NOT this plan) remediation.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Any remediation (env writes incl. the 250→2500 correction, iter91 edits/branch, code fixes) | owner decision AFTER the verdict; this plan ends at the memo |
| iter91 skeleton rewrite/delete | frozen-suspect until T6 |
| Sam first_name gate archaeology (PT-78) | separate session |
| iter89 merge decision | owner at close-out, unchanged |
| 5-persona mic battery reruns | only if owner orders repeats after the verdict |
