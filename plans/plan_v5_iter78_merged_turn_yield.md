# plan_v5_iter78_merged_turn_yield — PT-69 yield + entry_lite delta directive (complete the iter70 intended design)

## Meta
- Date: 2026-09-25
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: TWO tight commits on ONE branch, both completing speech-flow design, no reverts:
  1. **Prompt-pollution cleanup + entry_lite delta directive** — remove the transition/flat-ack
     directive lines from the state prompts (`Closer.md`, `Discovery.md`, `Offer.md` + Intake's
     variant) and inject that guidance into the EXISTING entry_lite round delta
     (`builder.py:2251-2265`) so only the flat-ack continuation round sees it. Completes the
     iter70 T3 intended design (verified in the code comments — see Compaction Context).
  2. **Yield at the first spoken "?" + said-truth alignment** (PT-69) — the spoken turn ends at
     the first "?"; history + `last_spoken` align to the SPOKEN text.
- Status: PLAN ONLY (rev 2 — owner re-directed 2026-09-25: keep iter70 T3; no "restore" of any
  old flow; the fix = placement, not architecture)
- Owner direction (verbatim intent, 2026-09-25): "We want to keep the changes, but instead of
  blasting it everywhere on the state prompts, we just put it on the flat ack so the entry lite
  has context… the entry lite delta directive will say, continue the call from where it stands
  or pick your next scripted question… the pre-warm doesn't have this directive, they won't
  collide, so next turn will not have this instruction."

## Compaction Context
(fresh-agent continuation block)

**Project:** Dialux SDR v5 voice engine (LangGraph + STT/LLM/TTS), repo
`/home/julio/projects/clean_diallux_SDR`. Work box = **OREGON 5.78.83.174**
(`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`; repo
`/home/julio/projects/clean_diallux_SDR`; **OR main checkout = prod working tree — never
checkout/switch/reset/pull there**). Helsinki 46.62.233.228 = reference. Lane :8025 on OR serves
`engine/iter77-twilio-iter70` @ `8c5f72f` (uvicorn pid `/tmp/opencode/voice_8025.pid` = 57628, log
`/tmp/opencode/voice_server_8025.log`, env `/tmp/opencode/wt-iter77/engine/.env`:
TTS_PROVIDER=elevenlabs Hannah `ZSNL4hPqCnqoMPaI4jGX` speed 1.0, browser `?rate=` knob, mic WS
token-gated). OR venv = `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` — run it
FROM the worktree cwd (branch package wins, verified). pytest 9.1.1. Suite baseline on the branch =
EXACTLY 3 known env-knob fails (test_iter46_latency_floor.py::test_fast_first_flush_before_stream_end,
test_iter59_dedupe_semantic.py::test_semantic_threshold_config_defaults,
test_iter60_audit_fixes.py::test_turn_opening_reask_dropped_when_window_nonempty).
Langfuse = Helsinki :3001 cross-box from OR. Voice LAW: preserve
`CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` in any env edit. MODEL LAW: gpt-5.4. LAW 0: no merges
without owner say-so; docs → main.

**The bug being fixed (smoke evidence, ledger session `smoke-iter77-or@8c5f72f`, report
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter77-twilio-iter70/02_callsop_report.md`):**
t9 = `"Would you be open to a live walkthrough with Jay to see how it'd fit your practice? Absolutely —
and based on what you shared, that's about $4,875 a week in missed revenue.Is that about what it
feels like on your side?"` — ack filler + second behavior stacked after the agent's own question.
t16 same class ("…is that all correct? Perfect.Would you prefer later today or tomorrow…?").

**Code facts verified 2026-09-25 (the design constraint):**
1. iter70 T3 (`94f5164`) INTENDED: flat-ack transition rounds route into the destination state and
   "the EXISTING entry_lite ack renders exactly ONE speech-only continuation round (destination's
   first scripted question if it fits, else one contextual question — prompt rule)"
   (`builder.py:2894-2905`). The same-turn beat STAYS — owner: "we don't want to go back".
2. The entry_lite round ALREADY rides a post-history delta (`builder.py:2251-2265`):
   `"THIS ROUND: SPEECH ONLY — do not call any tool. Reply to the caller in one or two short
   sentences, then stop."` (+ state block first when `state_in_delta`). **The continuation
   directive is NOT in that delta** — the missing half of the intended design.
3. The directive instead sits as a PERMANENT prompt line in the state .md files — added by the
   SAME commit: `engine/diallux/prompts/Closer.md:104`, `Discovery.md:57`, `Offer.md:59`
   ("When a stage transition just moved you here, your ack ends with EITHER the next scripted
   question (if it fits the live conversation) OR one short contextual question that keeps the
   flow — never a flat ack.") + "Every turn ends with a question to the caller — never a flat
   statement." in the same files (Intake.md got the shorter variant). Since the state .md is
   every round's system head, EVERY round sees the transition rule → the model (which must NOT
   know it is a state machine) reads it as a standing "my ack always carries a question" license
   → the stacking. OWNER: trim it from the state prompts; the rule belongs ONLY on the flat-ack
   entry_lite delta.
4. Delta mechanics (`builder.py:895-917`): delta = post-history system block, "fresh bytes every
   round, zero cached-prefix cost", "Never mutate mid-prompt". The pause-re-ask directive already
   rides this rail (`builder.py:2274-2280`). The pre-warm builds the head WITHOUT any delta →
   head stays clean → warm bytes = heavy-round bytes = no collision (owner's cache argument).
5. Said-truth exposure: assistant history entry = model's FULL generation
   (`builder.py:2620`, no-tools path 2663); `last_spoken` = `content` (2582); the speech filter
   touches ONLY the spoken stream (`_log_filter` docstring, builder.py:250-257 — "Model
   output/history/final content are NEVER touched; only the spoken stream"). Today consistent
   (nothing is cut); once yield cuts speech, history would claim unspoken text was said — hence
   the alignment requirement.
6. `turn_asked` = post-filter "caller-heard '?'" truth (builder.py:2319, set at 2428/2530, gated
   at 2894) — the iter70 said-truth gate the yield extends. The "?" sentence itself is always
   spoken (yield only cuts text AFTER it) → turn_asked unaffected.
7. Cross-turn near-verbatim re-ask guard exists (builder.py:2421) — gated by `tts_dedupe_semantic`
   (env-false in the OR lane, voice-law state — stays false).
8. iter71 (`plan_v5_iter71_intake_samples_ack_latency.md`) was NEVER executed (no branch) — its
   subject (same-turn continuation cold cache-0 rounds, ~700-1200ms warm can't land in the 100ms
   await) REMAINS OPEN and is NOT this plan (Deferred). iter70 baseline latency on OR:
   TTFT p50=654ms p90=968ms, turn-1 968ms (`smoke-iter77-or`, 28 rounds).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| KEEP iter70 T3 same-turn beat — NO revert, NO "restore the lite flow" | Owner: "neither of what you're describing is what we fixed. That iter70 fixed all of this… we don't want to go back. We want to keep the changes" |
| Remove the transition directive + "Every turn ends with a question" lines from the state prompts (`Closer.md`, `Discovery.md`, `Offer.md`, `Intake.md` variant) + llm.json mirror | Owner: "clean the pollution… I don't want this bullshit on the state prompts. We've got to trim that" — the model must not know it's a state machine |
| The directive moves to the entry_lite round DELTA (extend `builder.py:2251-2265`), wording ≈ owner's: "Continue the call from where it stands — pick up with your next scripted question (if it fits the live conversation) or one short contextual question that keeps the flow. Never a flat ack." | Owner: "we just put it on the flat ack so the entry lite has context. It understands that it should continue the conversation, and that's it" |
| No cache collision: pre-warm head = clean head (no directive) → warm bytes = heavy-round bytes; delta re-bills per round (fresh bytes, zero prefix cost, by design `builder.py:895-917`) | Owner: "that pre-warm doesn't have this directive, they won't collide, so next turn will not have this instruction" |
| Yield at the first spoken "?" (cut the same round's tail after the first spoken "?") stays IN scope as the backstop | Owner approved: "ok lets implement that 'yield at the end of a question'" — needed for non-transition stacking (t9 had no transition) |
| Said-truth alignment: when a yield fires, history `content` + `last_spoken` := SPOKEN text | Owner: "make sure the agent understands what was said and what was not said… sometimes the agent will send a 2nd turn and its context will understand that was 'said' when in reason it wasn't" |
| New branch `engine/iter78-merged-turn-yield` cut FROM `engine/iter77-twilio-iter70` @ `8c5f72f`; TWO commits (commit 1 = prompt cleanup + delta injection; commit 2 = yield hook), each with its own pins | LAW 0 v2.1 (branch = owner trigger word, never stack on a completed branch); two tightly-coupled speech-flow variables, separately revertable |
| Env knob `TTS_YIELD_ON_QUESTION=true` default ON (rollback = false); delta directive is NOT knobbed (it replaces a prompt line 1:1 — the rollback is `git revert` of commit 1) | VOICE LAW knob-first for the behavioral hook; prompt placement is a clean revert |
| Cut tail is DROPPED, not stashed; `turn_asked` stays post-filter | The caller's answer is the continuation; the "?" sentence always speaks (yield cuts only text AFTER it); cross-turn guard at 2421 prevents verbatim re-speak |
| Executor `spoken_text` (builder.py:2610) input = VERIFY in T2; if `validate_lead`/`record_booking_uid` parse it, keep full content for tools (data truth ≠ speech truth) | Tool calls act on data, not speech — confirm during T2 read, report any dependency |
| NO semantic/embedder machinery, NO history-window tricks, NO chain-link port | PT-69 second row + iter68 overengineering post-mortem |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner approval of the EXACT delta wording + the trimmed state-prompt diffs (HITL paste before edit) | owner at T3 start |
| Owner GO (T0) | owner |

## Environment & Dependencies
- Worktree ON OREGON: `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter78 -b engine/iter78-merged-turn-yield 8c5f72f` (run ON OR; NEVER in the OR main checkout).
- Python: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (main venv, run from the worktree cwd — NEVER the worktree's own broken `.venv`).
- Env file: copy `/tmp/opencode/wt-iter77/engine/.env` → `/tmp/opencode/wt-iter78/engine/.env` (root:root 640; append `TTS_YIELD_ON_QUESTION=true`).
- Ports: :8025 holds the iter77 lane (pid 57628) — stop before serving iter78.
- Langfuse: `http://46.62.233.228:3001` from OR (health `{"status":"OK","version":"3.172.1"}`).
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`; main-repo SDKs `scripts/live_sql.py` / `latency_pull.py` / `rag_pull.py`; worktree SDKs `scripts/call.py`, `scripts/lf.py`, `scripts/mic_events.py`, `scripts/voice_preflight.py`.
- Cal.com event 3801235 is REAL — cancel every test booking.
- Deploy-time cache note: trimming the state prompts changes head bytes → ONE-TIME turn-1 cache cold per state on the first live run (same G3 note as iter71's mid-battery case, but this is a clean deploy: warm and heavy bytes stay consistent). Plan the ear test knowing turn-1 may be ~968ms once.

## Architecture (block diagram)

```
caller audio -> WS /mic/ws -> STT -> graph round (builder.py)
  transition round fires ok transition_to_* + spoke, no "?" heard?
    -> beat (builder.py:2894-2905) routes to destination state
       -> round 2 = entry_lite (builder.py:1843-1873: light head kb=False, no RAG, no warm await)
            delta (2251-2265) NOW = state block + "SPEECH ONLY" + NEW:
            "Continue the call from where it stands — pick up with your next
             scripted question (if it fits) or one short contextual question.
             Never a flat ack."           ← the ONLY place this text exists
  state prompts (Closer/Discovery/Offer/Intake): transition lines REMOVED
    -> heavy head = clean (state + general prompt, no state-machine talk)
    -> pre-warm head bytes == heavy-round head bytes -> cache holds
  token stream -> sentence flush sites (2368-2390 mid-stream, 2484-2502 stream-end)
    NEW yield gate (TTS_YIELD_ON_QUESTION): sentence ends "?" ->
      speak it; CUT every later sentence of this round; log `_log_filter(stage="yield")`;
      history content + last_spoken := SPOKEN text (said-truth)
  turn_asked stays post-filter (2428/2530) -> transition beat unchanged
TTS ElevenLabs Hannah -> browser playback (?rate=)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter78_merged_turn_yield.md` | this plan | New (docs → main) |
| `/tmp/opencode/wt-iter78/engine/diallux/prompts/Closer.md` | REMOVE the 2 iter70 T3 lines (L104 area: "Every turn ends with a question…" + "When a stage transition just moved you here…") | Edit (commit 1) |
| `/tmp/opencode/wt-iter78/engine/diallux/prompts/Discovery.md` | same (L57 area) | Edit (commit 1) |
| `/tmp/opencode/wt-iter78/engine/diallux/prompts/Offer.md` | same (L59 area) | Edit (commit 1) |
| `/tmp/opencode/wt-iter78/engine/diallux/prompts/Intake.md` | same (shorter variant line) | Edit (commit 1) |
| `/tmp/opencode/wt-iter78/engine/agent/llm.json` | byte-parity mirror of every prompt edit (llm.json general_prompt + per-state mirrors as they exist) | Edit (commit 1) |
| `/tmp/opencode/wt-iter78/engine/diallux/graph/builder.py` | commit 1: extend the entry_lite delta (2251-2265) with the continuation directive (after the state block, before/merged with the SPEECH ONLY imperative — final ordering decided at T3 paste). commit 2: yield hook at both flush sites (~10-15 lines) + said-truth alignment | Edit |
| `/tmp/opencode/wt-iter78/engine/diallux/config.py` | knob `tts_yield_on_question: bool = True` (near tts_dedupe_* ~L187) | Edit (commit 2) |
| `/tmp/opencode/wt-iter78/engine/tests/test_iter78_yield.py` | pins for BOTH commits (see T3) | New |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md` | verdict + evidence | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-69 → CLOSED; add row: entry_lite delta directive (iter70 design completion) | Edit (docs → main) |

## Deploy Rules
- All code work ON OREGON, worktree `/tmp/opencode/wt-iter78`, main venv python from worktree cwd.
- Suite: `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q 2>&1 | tail -8` — expect the 3 known fails + all new pins green.
- Lane swap for the ear test: `kill $(cat /tmp/opencode/voice_8025.pid)` (fallback: pid from `ss -tlnp | grep 8025`), then
  `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && setsid nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8025 </dev/null >> /tmp/opencode/voice_server_8025.log 2>&1 &`
  then `ss -tln | grep "127.0.0.1:8025 "` (the `</dev/null` kills the wrapper-bash pid trap seen 2026-09-25) + `scripts/voice_preflight.py --url http://127.0.0.1:8025`.
- Push: `scripts/keyhound` from the MAIN checkout cwd (`.git/gh-creds` resolves from cwd — the worktree push trap 2026-09-25).
- NEVER touch: OR prod `diallux.service` :8026 + `diallux-mic.service` :8090 (they run FROM the OR main checkout — never checkout/switch/reset/pull there), OR :8001-8003, `/opt/diallux-production/.env`, Helsinki :8020/:8024, `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` in any env edit.

## Tasks (in order)

### T0 — HITL ASK
Owner GO on this rev-2 plan. Verification: owner says GO.

### T1 — Worktree + env (ON OREGON)
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'git -C /home/julio/projects/clean_diallux_SDR fetch origin && git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-iter78 -b engine/iter78-merged-turn-yield 8c5f72f && cp /tmp/opencode/wt-iter77/engine/.env /tmp/opencode/wt-iter78/engine/.env && echo "TTS_YIELD_ON_QUESTION=true" >> /tmp/opencode/wt-iter78/engine/.env && git -C /tmp/opencode/wt-iter78 log --oneline -1'
```
Verification: tip `8c5f72f`; knob present; worktree clean.

### T2 — HITL prompt diffs (commit 1, prompt + delta placement)
Goal: trim the pollution; complete the intended design.
1. Paste for owner approval: before/after of the 4 state .md files (remove the 2 added lines each in Closer/Discovery/Offer; the Intake shorter variant; llm.json mirror) + the exact entry_lite delta text (owner's wording: "Continue the call from where it stands — pick up with your next scripted question (if it fits the live conversation) or one short contextual question that keeps the flow. Never a flat ack." — final wording owner-approved).
2. Edit `builder.py:2251-2265`: extend the entry_lite `rag_delta` with that directive AFTER the SPEECH ONLY sentence (imperatives last, iter56 F-09 rule), keeping the state-block-first order.
3. Mirror llm.json byte-parity; run `python3 -c "import json; json.load(open('/tmp/opencode/wt-iter78/engine/agent/llm.json'))"` + the prompt lockstep tests (`tests/test_iter43_prompts.py tests/test_iter31_c3_prefix.py`).
Verification: `grep -rn "stage transition just moved\|Every turn ends with a question" /tmp/opencode/wt-iter78/engine/diallux/prompts/` → EMPTY; delta text present ONLY in builder.py's entry_lite branch; lockstep tests green; ONE commit `git commit`.

### T3 — Yield hook + said-truth (commit 2)
Goal: PT-69 backstop + the owner's said/not-said requirement.
Design (exact, from the verified code):
1. `config.py`: `tts_yield_on_question: bool = True`.
2. `builder.py` round scope (near 2310): `yielded = False`; track `spoken_content` (concat of flushed sentences).
3. Flush sites (2368-2390 mid-stream + 2484-2502 stream-end): when `runtime.settings.tts_yield_on_question` and the sentence ends "?": flush it, set `yielded = True`; every later sentence of the round goes to `_log_filter(runtime.settings, "yield", cut_text, state_name, state)` instead of TTS; stream-end pending while `yielded` → logged + dropped.
4. Said-truth: at history append, `content_history = spoken_content if (yielded and spoken_content.strip()) else content`; assistant history entry + `updates["last_spoken"]` use it. `turn_asked` post-filter logic UNTOUCHED (2428/2530).
5. T2 open-item check: `executor.execute(..., spoken_text=content)` (2610) — if `validate_lead`/`record_booking_uid` parse `spoken_text`, keep their input = full `content` (tools act on data); document the decision in the report.
6. Pins (`tests/test_iter78_yield.py`): stack ("…practice? Absolutely — and $4,875… Is that about right?") → spoken ends at first "?"; tail logged stage=yield; history content == spoken; last_spoken == spoken; knob-off → byte-identical full text; >2 questions → only first speaks; transition round with "?" → beat still fires; no-"?" round unchanged; entry_lite delta carries the directive, heavy head does NOT.
Verification: suite = 3 known fails + all pins green; `git -C /tmp/opencode/wt-iter78 diff --stat` = only the planned files.

### T4 — Live proof (ON OREGON)
Goal: prove the stacking is gone, live.
1. Stop iter77 lane → serve iter78 on :8025 (Deploy Rules) → preflight GREEN.
2. Chat happy-path (mock slots — no real booking): `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python tests/llm2llm/harness.py --personas Maria --rag --langfuse --max-turns 48`.
3. Full 5-SOP audit per `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/full_call_analysys.md` — SDK pipeline: `sop_mechanicals.py` → `call.py sop` → `live_sql.py import` (latency write) + `sop-import` CALL/SALES/HUMANIZED → `latency_pull.py` (latency read) → `rag_pull.py --run <run> --gates` (RAG plane — drill with `--rounds --zero --pin` if a gate fails), compare vs `smoke-iter77-or`.
Verification: NO agent turn contains a second sentence after a spoken "?" (json_log check); entry_lite continuation rounds still speak the destination question (the directive works — t13-t16 flow intact); `speech_filter stage=yield` lines when the model stacks; latency TTFT p50 within ±100ms of 654ms; CALL redundancy + HUMANIZED R5 seam rows → PASS; SALES band ≥12/14. Any booking → cancel (Cal.com 3801235 REAL).

### T5 — Owner ear test (mic page, iter78 lane)
Same Telegram flow (tunnel + `?rate=1.0&k=<token>` from the NEW worktree env; stage the token, never print). Probes: iter77's 4 + NEW: transition seams gone ("? Perfect." / "? Absolutely —" glue gone) and acks stay flat-only when they should.
Verification: PASS/FAIL/UNCLEAR per probe → `research/surgeon/iter78-merged-turn-yield/01_report.md`.

### T6 — Closeout (docs + ledger)
Persist SOP rows + latency to the ledger under the new run id; update `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` (PT-69 CLOSED + new row for the delta placement, docs → main via a dedicated main worktree — NEVER `push origin HEAD:main` from an iteration branch). ASK owner before any merge (LAW 0).

## Validation Plan (end-to-end)
1. Prompt grep clean: no transition/flat-ack directive in ANY state .md; delta text present ONLY in the entry_lite branch.
2. Suite: 3 known fails + all iter78 pins.
3. Harness Maria on iter78: booked, 0 gate rejections, zero post-"?" second sentences, `stage=yield` observability present, latency within ±100ms of the 654ms baseline.
4. 5-SOP audit delta vs `smoke-iter77-or`: CALL redundancy + tool_calls → PASS, HUMANIZED R5 seams gone, SALES ≥12/14, RAG plane gates PASS (`rag_pull.py --gates`: zero-chunk state-entries + no are-you-ai redirect, matching the iter77 baseline G1/G2 PASS).
5. Owner ear PASS on the mic page; PT-69 closed; iter70 T3 behavior intact (continuation question still asked — from the delta, not the standing prompt).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter71 T2 ack-latency options (A deterministic filler / B warm re-fire / C prompt-only) for the same-turn continuation cold cache-0 rounds | Owner keeps T3 (no revert); the latency gap stays open — iter71 remains the queued fix, owner picks the option later. NOT this plan's variable |
| iter71 T3 (Intake samples → generation seeds) | separate prompt work, owner-pointed |
| Merging iter77/iter78 into main | LAW 0 — owner say-so only |
| iter74 speech fixes A/B | separate owner-gated A/B (still NOT merged anywhere) |
| Twilio phase 2 | gap register in `plans/plan_iter77-twilio-iter70_2026-09-24.md` (audited); owner-gated |
| `_live_merged_turn` stash cleanup (builder.py:464/1605/1691 — dead iter68 machinery) | separate micro-cleanup |
| contact_details cross-turn re-ask (t14/t15) + DVS 20→15 drift | separate small iterations; owner queue |
