# iter97/98 — validation-close: live-call gate for 97, cosmetic squash for 98, merges to main, iter100 evaluation (analysis)

## Meta
- Date: 2026-10-08 (written same day; executes in its own session on owner GO)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: (T0) find the owner's Twilio endpoint through FILES/CONFIGS only (no routing changes); (T1) run branch `engine/97-implementation` code ALONE on a real owner Twilio call and prove it did not damage the endpoint; (T2) merge 97 to main (one land, tag `engine/iter97`); (T3) cut `engine/100-tier-squash` from the new main with 98's knob+probe cherry-picked into ONE commit; (T4) real call #2 at that lane, then merge (tag `engine/iter98`); (T5) iter100 split-round design evaluation = ANALYSIS ONLY (owner's two-LLM caveat answered with data); (T6) tracking-completeness audit for iter100 measurement; (T7) close-out.
- Status: PLAN ONLY (not started — awaits owner GO / next session)

## Compaction Context (verbatim session state as of 2026-10-08 15:0x UTC)

### Mission + where things stand after the iter99 session
Dialux SDR v5 engine (LangGraph voice agent: Twilio/mic mulaw WS → Deepgram flux STT → 9-state graph → gpt-5.4 → SentenceGate → ElevenLabs → transport). Owner goal: **e2e_turn p50 ≤ 1,200 ms on real telephony** (last real call 1,882 ms p50, 2026-10-06).

- **`engine/97-implementation` @ `6044b9f`** (3 commits: D1 `2943d88` mic-caller crash fix (test-driver file `engine/scripts/llm_mic_caller.py` — ZERO live-call surface), T1 `68e5f3c` clock truth (TurnClock `t_llm_dispatch`/`t_llm_first_event` + first-only per-turn stamps; report keys `llm_dispatch_to_first_event_ms` / `llm_first_event_to_llm_first_ms`; 2 Prometheus histograms `diallux_llm_dispatch_to_first_event_seconds` + `diallux_llm_first_event_to_llm_first_seconds` + `diallux_media_lane_dropped_total` + `diallux_twilio_chunk_interarrival_ms`; writer events at `engine/diallux/graph/builder.py:2290` `llm_dispatch` + `:2332` `llm_first_event`; stamp handler `engine/diallux/media/session.py:49-58` `_stamp_clock_event`), D2 `6044b9f` call-end Langfuse tail-confirm moved OFF the event loop (`_finish_tracer_off_loop`, `asyncio.to_thread`; fixed up to ~60 s loop freeze at call end — the real 08:51–08:53 handshake hang on FI :8021). Program: STOP CHECKPOINT fired (dispatch p50 70 ms → loop-contention thesis dead; T3 media-frame-lane was NOT built; T2 uvloop honest-skip — lanes already uvloop; T4-eval DEAD). **Suite at tip: 517 passed / 1 skipped / 5 failed on FI; identical red set**: `tests/test_iter48_rag_truth.py::test_eot_and_midturn_entry_awaits_split_caps`, `::test_lite_round_awaits_lite_warm`, `::test_await_warm_none_uses_midturn_flag_and_shield`, `tests/test_iter55_observability.py::test_await_warm_timeout_keeps_warm_alive`, `tests/test_iter65_dv_carryover.py::test_validator_parity_daily_case`. **97 has NEVER taken a real Twilio call — that is exactly what this plan validates before merging.**
- **`engine/98-service-tier` @ `b06a8c0`** (descendant of the 97 chain; 3 top commits: B1 `c557dc5` `openai_service_tier` Settings knob default `""` wired through hoisted `mk` in `engine/diallux/graph/llm.py` (attach only when non-empty = byte-parity; `_warm_llm` + verbosity twins inherit; `llm_boot_prewarm` deliberately NOT tiered; `/health` carries `"service_tier"` in `engine/diallux/app.py`; 9 pins incl. byte-equality vs pre-98 bytes `engine/tests/test_iter98_service_tier.py`; suite 526/1/5 red-set identical), B2 `abbd9d8` standalone probe `engine/scripts/llm_tier_probe.py` (12 paired streaming TTFT default vs `service_tier="fast"` on gpt-5.4: fast ACCEPTED no-400, p50 1124→856.5 ms (+267.5), p95 1471→1076), ledger line `b06a8c0`. B3 same-lane A/B on OR `:8066` (84 turns, default→fast only switch): dispatch→first p50 **1185.7→807.2 = −378.5 ms (keep gate −100 PASSED 3.8×)**; e2e p50 −350 ms. **KEEP verdict: `OPENAI_SERVICE_TIER=fast` stays on lane `.env` files; code default stays `""`.** Costs: default 352k in / fast 263k in for the windows ≈ 1.49× proxy spend; exact fast-tier pricing = BLOCKED (owner pricing-page lookup).
- **`engine/99-speak-first` @ `41799af`** (sibling from `6044b9f`; prompt-rule experiment): OUTPUT ORDER LAW appended to `engine/diallux/prompts/general_prompt.md` + 3 pins `engine/tests/test_iter99_speak_first.py` (suite 520/1/5). T1a attribution PROVEN from 27 T1-era turns: tool-first n=10 gap p50 **1,931.0 ms** vs text-first n=17 gap p50 **388.8 ms** (Δ 1,542 ≫ 100; STOP not fired). T1c A/B (OR :8066 97-tip vs :8067 99-rule, default tier both sides — sibling cut resolves the tier state by construction, documented deviation): **ALL GATES MISSED** — branch gap p50 460.5 (gate ≤200), e2e +247.7 ms WORSE, compliance 2.4%. VERDICT: prompt-rule route DEAD on this data; branch parked UNMERGED, rule owner-gated. Mechanism: rule did end tool-first opens (raw probe `research/surgeon/iter99-speak-first/cadence_timeline.json`: base head tool-opens 3/6 raw, branch 0/6) but the first written sentence's `.!?` boundary lands late and SentenceGate releases only at completion.
- **Master plans truth-committed on main**: `plans/plan_v5_iter97_implementation.md` → EXECUTED THROUGH T1 + STOP CHECKPOINT…; `plans/plan_v5_iter98_service_tier_synthesis.md` → EXECUTED…, `plans/plan_v5_iter99_speak_first.md` → EXECUTED…, `plans/NEXT_STEPS.md` queue refreshed. Main = `origin/main` = `5edcbcc` (docs only — zero engine code). ENV-SWITCHES row for `OPENAI_SERVICE_TIER` on main docs copy + on the 98 branch.
- **iter100**: design spec EXISTS at `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design.md` (in-node `asyncio.gather`: SPEAK call `astream(messages, tools=[])` ∥ TOOLS call `astream(messages, tools)` inside the round loop `builder.py:2294-2497`; Settings flag `round_split_speak_tools=False`; TurnClock from speak stream; iter46 T4a prewarm moves to the tools stream; merge-at-gather; speak-call cold-cache cost quantified (~20–130 ms/round prefill re-bill, offset by killing the 1,931 ms tool-first subgroup); divergence WARN + findings rows; 8 pins listed; A/B gates p50 ≤50 ms structural + e2e −300 + compliance ≥80%; ports :8068 OR / :8083 FI provisional). **NO BUILD this round.**
- **Sync state (verified 2026-10-08, this session)**: FI pushed everything; OR fetched; OR worktrees updated: wt-97 @ `6044b9f`, wt-98 @ `b06a8c0`, wt-99 @ `41799af`; `origin/main = 5edcbcc` both boxes; OR root checkout UNTOUCHED (protected `engine/iter73-oregon-wip-20260924` @ `61a88ff`). FI working copies of the four plan docs = byte-identical to main's committed versions (cosmetic `git status` modified/untracked entries are expected and fine).

### Owner directives this session (verbatim intent, on record)
1. "Sync everything on both boxes via GitHub. Push from Finland, pull in Oregon, make sure everything is squeaky clean." — DONE (recorded above).
2. "Open up a fork in Oregon — that's where my endpoint of the Twilio number lives. This should just go through the files. Only after you go through the files and you understand where is my endpoint showing, then we check that Eater 97 indeed didn't fuck up the endpoint. And only then do we merge." — T0/T1/T2 below.
3. "We can squash 98 just for cosmetic purposes because I don't wanna see like a thousand commits I don't understand… merge 97 to main, and then we merge 98 to main… Then we test again." — T3/T4 below.
4. "Probably gonna be good, but okay" — merges remain gated on the call-checkpoint verdicts.
5. iter100 caveat (owner, verbatim intent): "Is this design not gonna act like two separate LLMs? … if we answer first but didn't fire the tools, then we're not gonna get the context from the tools. But in reality, I think that's from last turn, right? If we extract a DB and we are supposed to respond in that DB, we already have that data. So we're only creating the new question, 50–60 tokens. Then we execute everything else. I think that's the right call… Although I'm not sure if that's production grade or test grade. That might destroy the payload, conflict with the knobs, might do a mess. I'm gonna research about it because this is just a hunch." — T5 answers the hunch WITH DATA; owner keeps researching; no build.
6. "We have the tracking code, live tools… make sure that if we're not tracking every single piece of useful data — no redundant blob — then we add it so we track it. Then we can use that tracking to measure exactly what's going on with Eater 100." — T6 audit.
7. HARD RULES re-confirmed: prompts/KBs NEVER land on main by default (AGENTS.md v2.2 — prompt-layer = CODE discipline); 99's prompt rule stays on its parked branch, owner-gated. Nothing prompt-shaped merges without explicit owner say-so. `scripts/keyhound` before every push. Tests stay on FI; batteries on OR. Transport FI↔OR = git push/pull ONLY (never rsync).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Merge authority = the plan's own checkpoint mechanism | Owner prescribed the exact sequence twice; each real call's clean verdict is the gate; merges execute WITHOUT a second round-trip only at a PASSING checkpoint (long-session authority pattern, iter99 precedent). Any shaky verdict → STOP → owner. |
| 97 merges as ONE land `--no-ff` (absorbs D1/T1/D2 + the 3 commits as-is, tag `engine/iter97`) | Owner: "we don't merge 97 — cancel" applies to chunks, not to the land; the branch is internally coherent (instrument + 2 fixes), cherry-picking D1/D2 separately was REJECTED this session (D2-dropping leaves a known freeze-class bug on main). |
| 98 re-lands as a SQUASHED carrier branch `engine/100-tier-squash` cut from main AFTER 97 merges; knob+probe land as ONE commit; old `engine/98-service-tier` stays parked untouched as evidence | Owner: "squash Eater 98 into one commit for cosmetic purposes". Branch-from-branch lesson applied: rebuilt from the standing tip. Numbering: new code branch modifying `engine/diallux/` takes the next free number = 100; split-round moves to 101. Old 98 branch is never deleted (evidence). |
| iter100 design gets the number 101: `engine/101-split-round`, cut from `engine/100-tier-squash` tip when built | Direct consequence of the carrier taking 100. The spec file name stays `100_design.md` (historical); the plan updates its Branch header at T5. |
| The 99 branch + prompt rule: NOT merged, NOT deleted this session | Proven-dead on data; owner owns the kill/park call. Its pins reference a dead rule — worthless on main. |
| Real-call validation = the ONLY acceptable pre-merge test for the endpoint question | Owner: "you might have tested on fake calls, but that's not the same as a live call." |
| Endpoint discovery through FILES ONLY first (Twilio-console paste from owner allowed as confirmation) | Owner: "this should just go through the files." NO routing changes during discovery; routing changes only at T1 with the mechanism named. |
| No gain = nonsense posture for 98 ("we're paying double") | Owner's double-pay stance: if the live call #2 shows NO tier improvement p50, STOP and re-evaluate the flip before any merge of 100-tier-squash. |
| Tracking audit bias: ADD what's measurably missing for iter100 measurement, but NO redundant blob | Owner: "don't want any blob that is redundant, unnecessary". Missing stamps = recorded as spec addendum items carried by the 101 branch (NOT patched onto 97/98 in this session). |
| Bookings: cancel EVERY test booking after each real-call validation (Cal.com event 3801235 is REAL) | Repo rule; live SDR flow really books. |
| Tests stay FI, batteries/OR-lanes on OR; GitHub-only transport | Standing workflow (owner 2026-10-06 + this session). |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Confirmed Twilio webhook URL for +1 888 595 8927 (sid-level ground truth) | owner reads the Twilio console (ActiveNumbers → +1 888 595 8927 → Voice & Fax → "A call comes in" URL). T0's file map is the cross-check. |
| GO on this plan (surgeon step 5) | owner reads this file |
| Exact gpt-5.4 fast-tier pricing | owner/OpenAI pricing page (carried BLOCKED from iter98) |
| Merge say-so at checkpoints | the checkpoints PASSING = the say-so (Resolved Decisions); shaky verdict returns to owner |

## Environment & Dependencies
- FI repo: `/home/julio/projects/clean_diallux_SDR` (checkout parked on `engine/iter97-research-adaptation` @ `37260fd`, clean). Python: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (3.12). Suite: `cd /tmp/opencode/wt-97/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1` → expect `5 failed, 517 passed, 1 skipped` (5 named reds above), and on the squash carrier `5 failed, 526 passed, 1 skipped`.
- OR (work box): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — repo `/home/julio/projects/clean_diallux_SDR`, worktrees `/tmp/opencode/wt-{97,98,99}` @ the synced tips (see Compaction). Root checkout = PROTECTED `engine/iter73-oregon-wip-20260924` @ `61a88ff` — NEVER checkout/reset/pull there.
- Lane opener (OR repo root): `bash scripts/new_lane.sh <NN> <base> <slug>`; `bash scripts/new_lane.sh --list` inventory; exit 1 = DOA. Existing wt-97 already dressed (venv symlink + audited `.env` from OR canonical) — a :8069 boot REUSES wt-97 (its branch is checked out there; a second uvicorn process on another port does not conflict — port-scoped).
- Test-lane ports: OR `:8069` (97-alone lane), OR `:8070` (squash-carrier lane). NEVER touch: FI `:8000–8003` (original live), `:8020`, `:8021` (parked iter97 mic comparison), `:8080` Caddy; OR `:8049`/`:8050` (wt-9494 voicetest lanes, owner), `:8063` (wt-96 parked, PT-85), `:8065` (parked 97 comparison lane on OLD process — leave running old code), `:8066`/`:8067` (A/B lanes, stopped). `:8068` reserved for the future 101 build.
- Secrets: `.env` files only (gitignored). `VOICE_TEST_TOKEN` sits in each lane `.env`. Lane `.env` values are owner-set; this plan's only env touch = OPTIONAL single line append `OPENAI_SERVICE_TIER=fast` on the :8070 lane `.env` (owner order on record: iter98 KEPT verdict; this plan = the order once GO'd).
- Langfuse CLI (FI self-hosted, project `pk-lf-bba5…`): `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python scripts/lf.py traces --name micbridge --hours 4` / `lf.py show <trace_id>` / token ledger via `lf.py traces --hours 4` listing (`lf.py costs` 400s on OR tonight — fallback stays the traces listing).
- Ledger: `research/surgeon/iter48-rag-truth/ledger.db` (+ SQL SOP in the same dir). Commit registry: `research/surgeon/iter47-call-ledger/ledger.db` — refresh at session end via `git show engine/iter47-call-ledger:scripts/call_ledger.py > engine/scripts/_call_ledger_tmp.py; cd engine && .venv/bin/python scripts/_call_ledger_tmp.py build; rm engine/scripts/_call_ledger_tmp.py` (backup the db first).
- Key anchors (on `6044b9f`): round loop + writer events `engine/diallux/graph/builder.py:2290/:2332`; astream wrapper `engine/diallux/graph/llm.py:297`; prompts compose `engine/diallux/graph/builder.py:1700-1716` (static_head: `general_prompt.md` + state text for every state); knot-free 98 vs 97 touch-sets (from `git diff` this session): 98-only = `engine/diallux/config.py` +`engine/diallux/graph/llm.py` +`engine/diallux/app.py` +lines in `docs/Testing_guidelines/ENV-SWITCHES.md` + `engine/scripts/llm_tier_probe.py` + `engine/tests/test_iter98_service_tier.py`; 97-only = `engine/diallux/graph/builder.py`, `engine/diallux/media/session.py`, `engine/diallux/observability/latency.py`, `engine/diallux/observability/metrics.py`, `engine/scripts/llm_mic_caller.py`, 2 new test files.
- Voicetest prior art (2026-10-06 iter93/94/95 validation): "owner REAL Twilio call +1 888 595 8927 via voicetest.diallux-ai.site (trace `152d98c0c8d73f27680d950f2914e1bb`, lane :8049/:8050 @ 9eb341c)". FI Caddy has NO voicetest route (checked: `sudo /bin/cat /etc/caddy/* | grep voicetest` = empty) — the route terminates on OR (caddy there, a tunnel, OR direct webhook, or Vercel hop) — THAT is the T0 question.

## Architecture
```
main @ 5edcbcc (docs only, both boxes, GitHub-synced)
  │
  ├─ AFTER T2:  ──◆ merge engine/97-implementation --no-ff  (tag engine/iter97)   [one land]
  │                 = T1 clocks + D1 caller fix + D2 off-loop finish
  │
  ├─ AFTER T4:  ──◆ merge engine/100-tier-squash --no-ff   (tag engine/iter98, ONE commit)
  │                 = openai_service_tier knob + probe + pins (98 rebased cosmetics)
  │
  └─ NEXT (own plan, NOT this session): engine/101-split-round cut from 100-tier-squash
       (speak astream(tools=[]) ∥ tools astream(tools) — spec research/surgeon/iter100-split-round/100_design.md)
 engine/99-speak-first @ 41799af  = PARKED leaf, prompt rule DEAD on data, owner-gated
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_98_validation_merge.md` | this plan (commit to main NOW, docs lane) | NEW (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/00_endpoint_map.md` | the file-backed endpoint discovery (T0 deliverable) | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/t1_call97_forensics.md` | call #1 clocks/verdict (T1) | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/t4_call98_forensics.md` | call #2 clocks/verdict + tier number (T4) | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design_addendum_owner_caveat.md` | T5 answer: the "two LLMs / no-context" caveat + payload-grade checklist + branch rename note (101) | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/tracking_coverage_audit.md` | T6 tracking audit for iter100 measurement | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/NEXT_STEPS.md` | queue refresh at close (T7) | EDIT (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/engine/ITERATIONS.md` (carried on branches wt-97/wt-98 checkout copies; also refreshed on main after merges) | ledger lines for the 97 merge + the 98 squash-carrier merges | EDIT (on branches pre-merge; on main post-merge) |
| NOTHING inside `engine/diallux/**` | merges are git ops; squash carrier = cherry-pick of ALREADY-BUILT commits; no new engine code this session | — |

## Deploy Rules
- **T1 lane (97-alone, :8069)** — from the EXISTING wt-97 worktree (branch checked out at `6044b9f`):
```bash
ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 \
  'cd /tmp/opencode/wt-97/engine && set -a && . ./.env && set +a && (setsid .venv/bin/uvicorn diallux.app:app --host 127.0.0.1 --port 8069 > /tmp/opencode/lane-8069.log 2>&1 < /dev/null &) && sleep 6 && curl -s localhost:8069/health'
```
  — `/health` must NOT contain a `"service_tier"` key (97-alone shape: the knob does not exist on 97) and MUST contain `"llm": "gpt-5.4"`.
- **T4 lane (squash carrier, :8070)** — after T3 creates the carrier branch on origin, on OR: `bash scripts/new_lane.sh 100 origin/engine/100-tier-squash <slug>` → then boot same pattern with port `:8070`; `/health` MUST contain `"service_tier": ""` (knob present, code default) — and the lane `.env` gets `OPENAI_SERVICE_TIER=fast` appended per Resolved Decisions BEFORE the call, so the call tests the RATED shape.
- **Endpoint pointing (T1)**: T0 names the mechanism anchored in files. Only two authorized shapes:
  1. owner flips the Twilio webhook in the dashboard (I provide the exact URL to paste: `https://<OR-host>:<caddyport-or-tunnel>/…` from T0's map);
  2. OR-side caddy/systemd file edit via a registered caddy-apply-style change (never FI caddy).
  Whichever is used, a RETURN step restores the webhook to its standing target after the call (same mechanism, reversed) — endpoint must never linger on a test lane.
- NEVER touch: the protected OR root checkout, FI services `:8000–8003`, prod agents (`agent_16985b5d087e56c35141983396`, `agent_87e4d5f08475e5bc558b2f390f`), the 99 branch content, FI caddy, `.env` canonical values. `scripts/keyhound` before every push. No rsync. Tags only at owner-approved merges (the checkpoints ARE the approval).

## Tasks (in order)

### T0 — Endpoint discovery through files (NO routing changes)
Goal: map where the owner's +1 888 595 8927 webhook lands, from configs only.
Commands (OR, read-only):
```bash
ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '
  ls /etc/caddy/ 2>/dev/null; sudo /bin/cat /etc/caddy/* 2>/dev/null | grep -nE "voicetest|reverse_proxy|:80[0-9]{2}" | head -40
  systemctl list-units --type=service | grep -iE "diallux|caddy|tunnel|ngrok" | head -20
  grep -n "public_base_url\|WECOM\|webhook\|twilio" /tmp/opencode/wt-97/engine/.env | sed "s/=.*/=<value-present>/"
  grep -rn "inbound_call_webhook\|twilio" /tmp/opencode/wt-97/engine/agent/llm.json | head -5
  ss -tlnp | grep -E ":(443|80|80[0-9]{2})" | head -20
'
```
cross-check: FI nginx/caddy covers `.diallux-ai.site` (checked — no voicetest there); suspect chain: Twilio → `voicetest.diallux-ai.site` (DNS → OR or Vercel) → OR caddy/tunnel → OR lane. Deliverable: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/00_endpoint_map.md` — the chain, the exact target lane/port, the recommended paste-URL for T1, and the RETURN-step URL. Owner confirms with the Twilio console value.
Verification: map states the chain end-to-end with file evidence lines; NO config changed during this task.

### T1 — 97-alone live call (the endpoint-damage-check)
Goal: `engine/97-implementation` @ `6044b9f` answers a REAL call on :8069 and the endpoint behaves.
Steps: boot per Deploy Rules → suite sanity already known (517/1/5) → owner points the webhook per T0's paste-URL (owner dashboard click or the named file mechanism — owner's call which, recorded in evidence) → owner dials +1 888 595 8927 → let it play a natural arc (book or close; ≥8 turns) → owner hangs / call ends.
Forensics (from :8069 journal + Langfuse): `turn N final report:` lines carry the 3 clock keys (T1 alive on the REAL transport); zero Traceback/ERROR blocks; call-end completes (D2 exercised: NO freeze — next handshake must not starve; run a health curl within 10 s of hang-up); token ledger + `llm_dispatch_to_first_event_ms` / `llm_first_event_to_llm_first_ms` p50; compare vs the mic-shape numbers (dispatch→first ~1.2 s default-tier expectation); booking created → CANCEL it (event 3801235 REAL; cancel via Cal.com v2 `cal-api-version: 2024-08-13`, pattern `research/surgeon/` prior cancel scripts on OR /tmp/opencode/).
Verification: `t1_call97_forensics.md` with: call trace id, per-turn table, call-end clean evidence, booking-cancelled receipt, verdict CLEAN/DIRTY.
**⟙ CHECKPOINT: DIRTY verdict → STOP, return webhook, owner decides (nothing was on main). CLEAN → T2 executes the merge.**

### T2 — Merge 97 to main (one land)
Goal: `engine/97-implementation` → main as THE one land, tagged.
Commands (FI main-checkout OR docs worktree for the ops; the park branch stays). Merge executed from the FI repo root (gh-creds resolves there):
```bash
cd /home/julio/projects/clean_diallux_SDR
git checkout main --detach || git -C /tmp/opencode/wt-main-merge worktree main…
# canonical:
git worktree add /tmp/opencode/wt-merge-main main
cd /tmp/opencode/wt-merge-main
git merge --no-ff engine/97-implementation -m "merge: iter97 observability+fixes into main (owner say-so at CLEAN checkpoint — live call validated; tag engine/iter97)" 
bash /home/julio/projects/clean_diallux_SDR/scripts/keyhound --staged; git tag engine/iter97 && git push origin main --tags
cd /home/julio/projects/clean_diallux_SDR && bash /home/julio/projects/clean_diallux_SDR/scripts/git-tree.sh   # GIT_TREE refresh law
# suite on main from the merge worktree:
cd /tmp/opencode/wt-merge-main/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1   # expect 5 failed, 517 passed, 1 skipped
# OR sync:
ssh … 'cd /home/julio/projects/clean_diallux_SDR && git fetch origin && git -C /tmp/opencode/wt-97 merge --ff-only origin/main 2>/dev/null; true'
```
Verification: `origin/main` tip = merge commit; tag `engine/iter97` exists; suite=517/1/5 on main; registry refreshed at T7.
(WT note: if `wt-merge-main` already exists, reuse it with `git -C /tmp/opencode/wt-merge-main pull --ff-only origin main` first.)

### T3 — Squash carrier `engine/100-tier-squash` (ONE commit)
Goal: 98's knob+probe rebased as a single cosmetic commit on the new main.
Commands:
```bash
cd /home/julio/projects/clean_diallux_SDR
git worktree add /tmp/opencode/wt-100-tier -b engine/100-tier-squash main
cd /tmp/opencode/wt-100-tier
git cherry-pick --no-commit c557dc5 abbd9d8          # knob (code+tests+ENV row) + probe script
bash /home/julio/projects/clean_diallux_SDR/scripts/keyhound --staged
git commit -m "98-squash: openai_service_tier knob + standalone tier probe (one commit per owner cosmetic order; knob byte-parity pinned flag-off; B3 keep verdict -378.5ms on record)"
git push origin engine/100-tier-squash
cd /tmp/opencode/wt-100-tier/engine && .venv/bin/python -m pytest tests --tb=no -p no:warnings 2>&1 | tail -1   # expect 5 failed, 526 passed, 1 skipped
```
Verification: carrier branch = main + exactly ONE commit; suite red set identical + 9 pins green; old `engine/98-service-tier` untouched.
Detail: if cherry-pick conflicts appear in `app.py` or `config.py` (should not — 98-only files listed in Key anchors), STOP and report (do not improvise).

### T4 — Real call #2 at the carrier (the double-pay check)
Goal: the knob rides a REAL call; the −378 ms shows with the owner's own ears, no anomalies.
Steps: OR `bash scripts/new_lane.sh 100 origin/engine/100-tier-squash <slug>` → boot :8070 per Deploy Rules → VERIFY `/health` `"service_tier" == "fast"` after appending the env line + rebooting the :8070 process → owner repoints webhook to :8070's URL (same mechanism as T1) → call #2 → forensics: `llm_dispatch_to_first_event_ms` p50 ≤ ~850 (the fast-tier signature) AND no Traceback/ERROR/hang AND the flow completed naturally → CANCEL any booking → owner flips webhook BACK to its standing target (T0's RETURN URL).
Verification: `t4_call98_forensics.md` with numbers + receipt; verdict CLEAN+GAME (numbers improved) or CLEAN+NOGAME (STOP before merge — Resolved Decision).
**⟙ CHECKPOINT 2: CLEAN+GAME → merge carrier to main (`--no-ff`, tag `engine/iter98`), same merge pattern as T2, `git-tree.sh`, push+tags, OR sync, suite re-run. CLEAN+NOGAME → STOP → owner. DIRTY → STOP → owner + keep `engine/98-service-tier` evidence branch as the reference.**

### T5 — iter100 evaluation (ANALYSIS ONLY, no build, no branch cut)
Goal: answer the owner's two-LLM caveat with DATA; make the production-grade call explicit; prep the 101 rename.
Deliverable: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design_addendum_owner_caveat.md` answering, with evidence:
1. **"Answers use last turn's tool data"** — TRUE by payload shape: `engine/diallux/graph/builder.py:2584` (`dvs.update(outcome.dvs_patch)` same-round) → the NEXT round's `_build_messages` carries post-patch dvs + history; the current round's speech (50–60 tokens) does NOT require the SAME round's tool results — EXCEPT the one call-out the spec already flags: `query_livecall_slots` filler (`builder.py:2608` slots_filler) + ConfirmSlots speech that reads slots results live. Quantify how many of the A/B turns (T1-era + A/B journals) had a slots/schedule-dependent same-round speech (grep tool names `query_livecall_slots|reserve_slot|check_availability` in `last_round_tool_calls` + speech-in-same-round).
2. **"Two separate LLMs"** — one round = 2 concurrent REQUESTS of the SAME model from the same turn state; divergence class (speak-says-X/tools-return-Y) monitoring is already §7 of the spec; add the A/B-journal-derived estimate of same-round co-emission today (grep rounds where BOTH content and tool_calls non-empty — from the ab journals' per-round `output` tokens + trace gen outputs) as the base rate of the divergence risk.
3. **Production-grade vs test-grade checklist**: payload behavior (state_in_delta byte-layout unchanged — split adds NO delta change), knob conflicts (zero new knobs; flag default OFF; iter100 spec §2), prewarm rewiring risk (iter46 T4a → tools stream), rollback = 1 env line. Verdict line: what must be true before a build plan is cut.
4. Owner's "I'm gonna research" hunch: leave a numbered slot for owner findings to append; the build plan (`engine/101-split-round`) is cut FROM HIS green light + this addendum.
Rename note: spec file header updated to `engine/101-split-round` (doc edit inside research/ — evidence dir, NOT engine/).
Verification: addendum exists; references exact lines/numbers; the lobotimzed-agent test (a fresh agent can judge production-readiness from it alone).

### T6 — Tracking completeness audit (for iter100 measurement)
Goal: ensure the live-call observability surface measures everything iter100's gates need; add NOTHING unless a data-backed gap.
Audit surface (verify, don't assume, from the wt-97 tree):
- `engine/diallux/media/session.py:49-58` `_stamp_clock_event` is transport-agnostic (both `/twilio` and `/mic/ws` paths call the same TurnClock flow) — CONFIRM the :8069 journal `turn N final report:` lines on REAL Twilio input carry the 3 clock keys (T1 does this directly).
- Report keys present: `stt_eot_to_llm_first_ms`, `stt_eot_to_llm_dispatch_ms`, `llm_dispatch_to_first_event_ms`, `llm_first_event_to_llm_first_ms`, `llm_first_to_tts_first_ms`, `tts_first_to_audio_out_ms`, `e2e_response_ms`, `e2e_turn_ms`, barge_in/eager/held/readset fields (schema from `engine/diallux/observability/latency.py:35-60`).
- Prometheus: 2 new histograms + `diallux_media_lane_dropped_total` + `diallux_twilio_chunk_interarrival_ms` registered (`engine/diallux/observability/metrics.py`) and REACHABLE via `/metrics` on the :8069 lane.
- iter100-specific NEEDS named in `research/surgeon/iter100-split-round/100_design.md` §8: same-box dispatch→first + first_event→first (covered), per-round tool_call emission (Langfuse gens carry it), divergenceWARN (to be added by the 101 build itself), tier per health (covered by knob's /health field post-merge).
Deliverable: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/tracking_coverage_audit.md` — covered/missing table; missing items = NOTES for the 101 branch (NO engine edits in this session).
Verification: audit line per §8 gate metric of the spec = covered/missing/where.

### T7 — Close-out
Sequence: registry refresh (backup `research/surgeon/iter47-call-ledger/ledger.db` first; exact command in Environment) AFTER all merges; `scripts/keyhound` before every push; `plans/NEXT_STEPS.md` refresh (new queue: standing = merged 97+98 tip; next = 101 build plan on number 101, gated by T5 addendum + owner research; 99 = parked punished leaf); ITERATIONS.md ledger lines for iter97/iter98 merges (post-merge, on main copy at `engine/ITERATIONS.md`); plan Status line → EXECUTED (docs → main). Evidence dirs stay gitignored.

## Validation Plan (end-to-end)
1. T0 map exists BEFORE any routing change; the webhook pointer mechanism is named and reversed after each call.
2. Suite red set byte-identical at every gate: pre-merge 517/1/5 (97 shape) and 526/1/5 (carrier shape) — never "all green with new reds".
3. Every real call leaves: journal forensics + Langfuse trace id + booking-cancel receipt (event 3801235 = REAL).
4. Both merges = exactly one `--no-ff` land each with their tag; the squash carrier = ONE commit on top of main; old 98 branch untouched.
5. No prompt (`engine/diallux/prompts/**`) or KB (`engine/agent/knowledge_bases/**`) change lands anywhere in this session (99 stays parked; hard rule honored).
6. All evidence under `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-98-validation/` + `.../iter100-split-round/` (gitignored); nothing evidence-shaped inside `engine/`.
7. Final sync: FI pushed, OR fetched+worktrees updated, origin/main parity verified both boxes (the squeaky-clean standard of this plan's T0 predecessor step).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| `engine/101-split-round` BUILD | needs T5 addendum + owner research green light; own plan + session |
| 99 verdict (merge the dead prompt rule / delete the branch) | owner's call; parked |
| Tier flip on any PROD surface | owner-gated; test lanes only carry it here |
| Deepgram EOT knobs | owner-owned deferred (biggest unmeasured lever) |
| GK stress battery | after a lane the owner blesses (book → capture validator uid → cancel ritual) |
| Payload slimming (strip RAG from hot states) | hygiene; re-rank after the 101 build |
| exact fast-tier pricing | owner/OpenAI page; recorded when available |
