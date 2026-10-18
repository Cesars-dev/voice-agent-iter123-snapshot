# iter99 — speak-first: prompt-rule test + engine-driven split-round design (session also executes the parked iter98 plan verbatim)

## Meta
- Date: 2026-10-08
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: (T0) execute `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter98_service_tier_synthesis.md` AS IS (all its tasks T1→T7), (T1) prove the tool-first attribution from existing data, then cut `engine/99-speak-first` and A/B the speak-first prompt rule, (T2) write the iter100 split-round design spec (engine-enforced speak-first — NO build this session), (T3) close-out.
- Status: EXECUTED (same day, long-session GO): T0 = iter98 executed verbatim (B1/B2/B3 — keep gate PASSED, tier=fast kept, see research/surgeon/iter98-service-tier/98_report.md); T1a attribution PROVEN (tool-first 1931 vs text-first 389 ms, STOP NOT fired, 99_attribution.md); T1b + T1c executed — A/B ALL GATES MISSED (branch gap p50 460.5, e2e +247.7 worse, compliance 2.4%) → prompt rule VERDICT: DEAD on this data, branch `engine/99-speak-first` stays unmerged, rule owner-gated (99_report.md); T2 iter100 split-round SPEC READY (research/surgeon/iter100-split-round/100_design.md) — build = next session, own branch engine/100-split-round from 98 tip.

## Compaction Context

### Mission
Dialux SDR v5 engine (LangGraph voice agent: Twilio/mic mulaw WS → Deepgram flux STT → 9-state graph → gpt-5.4 via langchain ChatOpenAI → SentenceGate → ElevenLabs → transport). Owner goal: **e2e_turn p50 ≤ 1,200 ms on real telephony** (last real call 1,882 ms p50).

### Where iter97 ended (2026-10-08, all verified this session)
- Branch `engine/97-implementation` @ `6044b9f` on FI = `61bfc7e` (base) → `2943d88` (D1: mic-caller survives server-side end_call close) → `68e5f3c` (T1: clock truth — TurnClock `t_llm_dispatch`/`t_llm_first_event` + 3 report keys; writer events at `engine/diallux/graph/builder.py:2290` `llm_dispatch` and `:2332` `llm_first_event`) → `6044b9f` (D2: call-end Langfuse tail-confirm moved off the event loop).
- **T0/T1 verified APPLIED and LIVE**: all 27 T1-era turn reports in `/tmp/opencode/lane-8021.log` carry the new keys. Baseline tsv: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-implementation/baseline_mic/t0_final_reports.tsv` (n=73).
- **Checkpoint verdict (measured, n=27 deep persona arcs)**: `stt_eot_to_llm_dispatch` p50 **70 ms** (loop-adder thesis dead pre-dispatch); `llm_dispatch_to_first_event` p50 **1,208 ms** (≈ same-day raw cURL 1.18–1.81 s on same payload shape ⇒ SDK/astream/endpoint add ~0–50 ms — endpoint plumbing EXONERATED); `llm_first_event_to_llm_first` p50 **538 ms / p95 2,370 ms** (first SDK event, often a tool_call delta, → first SPOKEN token); `llm_first_to_tts_first` p50 174 ms; `e2e_response` p50 1,901 ms.
- T2 (uvloop) skipped — lanes already run uvloop. T3 (media frame lane) skipped — premise measured dead. T4-eval DEAD (lane 1,208 ≈ raw default-tier TTFT). iter97 merge = owner say-so, pending.
- **OR IS BEHIND**: `engine/97-implementation` on OREGON = `61bfc7e` (missing D1/T1/D2). OR lane `:8065` runs pre-T1 code. The tip MUST be pushed FI→OR before any OR lane work (T0 step 0 below).
- Chat-vs-mic resolution (settled this session): the 96b "250–350 ms mic overhead" was largely **era-mix** (chat-728 = median of Sep 24–Oct 3 traces; mic-1,208 = Oct 8, same day raw cURL also read 1.18–1.81 s) + the two mic-only segments the chat clock never crosses: **tool-first opening gap** (538 ms p50) and the **EOT anchor** (Deepgram's decision — owner-deferred knobs, the biggest unmeasured toll). Payload fat (mic re-ships state delta + ~3 fresh KB chunks per round via eager laneB RAG, `rag_fire_sim=False` in the chat harness — `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/harness.py:148`) is worth only ~15–40 ms at the measured 8–22 ms/1k-token prefill slope. 96b report: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-delta-cache-layout/96b_ttft_forensics.md`.

### Where iter98 stands
- Plan `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter98_service_tier_synthesis.md` committed to main (`6bd1028`, 2026-10-08 11:28), status PLAN ONLY. **ZERO of its tasks executed** (this session verified: no `engine/98-service-tier` branch on either box, no worktree, no probe, no report dir, master plan `plan_v5_iter97_implementation.md` on main still falsely says "PLAN ONLY"). It is fully ratified and self-contained — T0 below executes it verbatim.
- Suite baseline on `engine/97-implementation` tip: FI **517 passed / 1 skipped / 5 failed** (510 pre-existing + 7 T1 pins). The 5 reds: `tests/test_iter48_rag_truth.py::test_eot_and_midturn_entry_awaits_split_caps`, `::test_lite_round_awaits_lite_warm`, `::test_await_warm_none_uses_midturn_flag_and_shield`, `tests/test_iter55_observability.py::test_await_warm_timeout_keeps_warm_alive`, `tests/test_iter65_dv_carryover.py::test_validator_parity_daily_case`.

### The speak-first thesis (what T1 tests)
Tool-first rounds make TTS wait while the model emits tool_call arguments before any spoken word — 538 ms p50 of dead air. **Proven**: the gap exists (T1 data) and turns are tool-heavy (iter87 T1.4 exists because tool-only rounds logged ttft=None; the T1-era trace `1bfaf5cdcf81` shows 13 tool calls in 18 gens). **NOT proven**: (a) per-round attribution (no one split the 27 turns into tool-first vs text-first groups), (b) the fix (no speak-first prompt variant has been run). T1 below proves (a) from existing data, then tests the prompt rule; T2 designs the engine-enforced version (owner: "let's not play roulette with the model").

### Engine-driven design decision (owner session 2026-10-08, ratified shape)
**In-node parallel split-round, NOT LangGraph topology fan-out.** LangGraph's parallel branches (`Send`/fan-out nodes) would work but force a refactor of the state_node walk, reducers, and the iter46 T4a prewarm wiring. The same guarantee is achievable inside the round loop (`engine/diallux/graph/builder.py` ~:2287 area) with `asyncio.gather` over two astreams on the shared warmed httpx pool (`llm_boot_prewarm`, iter65 T1):
- **Speak call**: `astream(messages, tools=[])` — tools unbound ⇒ the model CANNOT open with tool args; text starts at TTFT and streams to SentenceGate/TTS immediately.
- **Tools call**: `astream(messages, tools)` — same messages, natural tool choice, no speech consumed; results merge into state updates when the gather completes.
TurnClock continuity: `llm_dispatch` stamps once; `llm_first_event` stamps on the SPEAK call's first event. Parity proof = `llm_first_event_to_llm_first` collapsing to ~0–50 ms structurally. Cost: 2× input tokens/round (mostly cache-read-discounted). Risk: speech/action divergence (speak call says "booking you in" while the tools call returns nothing) — monitored as `findings` rows. NO `tool_choice="required"` forcing in v1. Full spec = T2 deliverable; build = NEXT session, own plan, cut as `engine/100-split-round`.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| T0 = execute the iter98 plan VERBATIM (its T1→T7, no edits) | Owner directive this session ("the iter98 plan as is"). Its own Resolved Decisions table stands. |
| Push `engine/97-implementation` `6044b9f` FI→OR BEFORE any OR lane work | OR is behind (`61bfc7e`); iter98's B3 keep-gate metric only exists on `6044b9f`. |
| Attribution analysis BEFORE the prompt edit, with a STOP checkpoint | If tool-first does not explain the 538 ms gap (gap uniform across text-first and tool-first rounds), the speak-first lever is dead and iter99 is not cut — do not build on an unproven thesis. |
| iter99 = `engine/99-speak-first`, cut as a SIBLING from `engine/97-implementation` tip (`6044b9f`) — NOT atop `engine/98-service-tier` | Owner re-affirmed 2026-10-08: every code change = its own branch, never stacked, so a bad fix can be dropped alone. Sibling cuts maximize rollback: drop 98 or 99 independently. Touch-sets are disjoint (98 = knob code: config.py/llm.py/app.py; 99 = prompts/general_prompt.md + one test file) ⇒ independent merge order, no conflicts, no confounds. Numeric name: `scripts/new_lane.sh` numeric guard. |
| **Long-session authority: this plan IS the owner GO for T0→T1→T2 in sequence — no return to owner between iterations.** The session runs until each idea is either (a) made to work (gates met) or (b) proven wrong (measured miss, STOP checkpoint verdict), everything documented. The only hard stops that DO return to owner: any merge say-so (LAW 0), any verdict that kills a planned idea (attribution miss / probe 400 / A/B miss → record verdict, cut the NEXT idea), and the GK stress battery. | Owner directive this session: "long session with iterations approved until we a) make it work b) prove it wrong — everything documented." |
| **Per-idea branch discipline (owner, this session):** T0 = iter98 idea (its lane work + bugfixes + test pins all stay ON `engine/98-service-tier`), T1 = iter99 idea (all on `engine/99-speak-first`), T2 = design only (spec, no branch cut). Bugs discovered while measuring an idea = fixed ON THAT IDEA'S BRANCH with recorded commits (the D1/D2 precedent); tests for the idea = same branch. Proven (gates met) or proven-wrong (measured) → cut the NEXT idea's branch; never carry the next idea's work onto a proven branch. | Owner: "T0 T1 and T2 are branch cuts essentially, with one pickle: iters of the same idea — bugs and tests stay on that branch; once we prove/measure we cut the next and move on." |
| **Box roles sync (owner, this session): tests stay on Finland.** FI = authoring + suite + dry-run lanes; OR = battery runs (`:8066`/`:8067` A/B pulls). OR is lighter/idle-box so any FI-measured gain trans reflects there in the future; FI `:8021` stays parked as the comparison lane. Rollback safety: sibling branches from `6044b9f` mean dropping 98 or 99 alone never touches the other. | Owner: "we sync, but we keep tests in Finland — OR will be lighter, so any gain here will be reflected there in the future." |
| Prompt rule lands in `engine/diallux/prompts/general_prompt.md` (shared head) only | `static_head(state_name)` composes general + state text (builder.py:842/1107) — one insertion covers all 9 states; expand per-state ONLY if compliance is measurably state-specific. |
| iter99 A/B base = `engine/98-service-tier` tip with IDENTICAL lane `.env` on both sides (same `OPENAI_SERVICE_TIER` state, whatever iter98-B3 concluded) | SWITCH LAW #3: a behavioral-switch diff between runs VOIDS the comparison. |
| iter100 = split-round, DESIGN ONLY this session | Owner: engine-driven, no model roulette. Build gets its own plan/session after the iter99 verdict; if prompt compliance proves ≥90% and holds across SOPs, iter100 downgrades to guarantee-layer — owner call at that checkpoint. |
| No LangGraph topology change (no `Send`/parallel nodes) | In-node `asyncio.gather` achieves the same concurrency with a smaller blast radius; state reducers, prewarm wiring, and the state_node walk stay intact. |
| Preserve `/tmp/opencode/lane-8021.log` BEFORE any lane reboot | It holds the 27 T1-era turn reports; reboots REWRITE it (known trap from the iter98 plan). Copy to the iter99 evidence dir first. |
| Ports: iter99 OR lane `:8067`, FI dry-run `:8082` | Avoids the iter98 reservations (`:8066`/`:8081`) and every never-touch port. |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO on this plan | owner reads this file |
| Exact gpt-5.4 fast-tier pricing | rides the iter98 plan's BLOCKED table (its T5/T7 record the `lf.py costs` delta) |
| iter97/iter98 merge say-so | owner — LAW 0; iter99 rides the branch chain meanwhile |

## Environment & Dependencies
- FI repo: `/home/julio/projects/clean_diallux_SDR` (checkout parked on `engine/iter97-research-adaptation` @ `37260fd`, clean). Python: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (3.12). Suite: `cd <worktree>/engine && .venv/bin/python -m pytest tests -q` → expect **517/1/5** on the 97-tip (identical red set, names above).
- OR (work box): `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — repo `/home/julio/projects/clean_diallux_SDR`; lanes in `/tmp/opencode/wt-*`. Transport FI↔OR = git push/pull ONLY (never rsync).
- Lane opener (repo root, works both boxes): `bash scripts/new_lane.sh <NN> <base-branch> <slug>`; `bash scripts/new_lane.sh --list` = inventory; exit 1 = DOA.
- Fast suite: `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` (cwd MUST be a repo engine dir): node-ids | `--touched` | `--full`.
- Mic driver: `scripts/llm_mic_caller.py` (D1-fixed; `--journal-log` is a dead flag — never pass it; evidence = lane journal `turn N final report:` lines + `--out` json).
- Langfuse: FI self-hosted; CLI `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python scripts/lf.py traces --name micbridge --hours 8` / `lf.py show <trace_id>`. T1-era traces for attribution: `110fe70fdccd` (22 gens), `1bfaf5cdcf81` (18 gens); persona-era: `88e33dae89a4` (31 gens), `75219a7a5e52` (34 gens). Caller jsons on disk: `/tmp/opencode/iter97_t1_run1.json`, `/tmp/opencode/iter97_t1_run2.json`, `/tmp/opencode/iter97_persona_run1.json`, `/tmp/opencode/iter97_persona_run3.json`. Join rule: json `started_wall` ↔ trace start time; sid from json `events` ↔ trace name `micbridge-<sid>`.
- Key code anchors (on `engine/97-implementation`): round loop + writer events `engine/diallux/graph/builder.py:2290`/`:2332`; astream wrapper `engine/diallux/graph/llm.py:297`; mk per-model gating `engine/diallux/graph/llm.py:~237`; prompts `engine/diallux/prompts/*.md` (general head composed via `static_head`, builder.py:842/1107); config `engine/diallux/config.py`.
- NEVER touch ports: FI `:8000–8003`, `:8020`, `:8021` (iter97 lane stays parked), `:8080` Caddy; OR `:8049`/`:8050`, `:8063`, `:8065`. Protected branch `engine/iter73-oregon-wip-20260924` — never touch/rebase/reset.
- Secrets: workspace `.env` files (gitignored). `VOICE_TEST_TOKEN` sits in each lane `.env`. `.env` values are owner-set only (the iter98 B3 flip is the owner order on record via that plan).

## Architecture
```
main (docs: this plan + iter98 plan)
engine/97-implementation @ 6044b9f            (done, awaits merge say-so)
  ├─ engine/98-service-tier  (T0 = iter98 idea — knob+probe+A/B; bugs+tests STAY HERE)
  ├─ engine/99-speak-first   (T1 = sibling cut from 6044b9f; bugs+tests STAY HERE)
  └─ engine/100-split-round  (T2 = DESIGN SPEC ONLY — in-node gather:
        speak astream(tools=[]) ∥ tools astream(tools) → no roulette)
FI = authoring + suite + dry-run lanes · OR = batteries (lighter box, gains reflect there)
Long-session authority: run T0→T1→T2 until each idea is MADE TO WORK or PROVEN WRONG.
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter99_speak_first.md` | this plan (commit to main now) | NEW (docs → main) |
| everything in the iter98 plan's File Map | T0 executes it verbatim — see `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter98_service_tier_synthesis.md` | per that plan |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter99-speak-first/99_attribution.md` | tool-first vs text-first gap split over the existing 27 turns + traces | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/engine/diallux/prompts/general_prompt.md` | +OUTPUT ORDER LAW paragraph (exact text in T1-below) | EDIT (on `engine/99-speak-first`) |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter99_speak_first.py` | pin: general head carries the rule; prompt loads byte-clean | NEW (on branch) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter99-speak-first/99_report.md` | attribution + A/B + compliance + verdict | NEW (evidence, gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design.md` | the split-round spec (T2 deliverable — full design, no code) | NEW (evidence, gitignored) |

## Deploy Rules
- T0 deploys = the iter98 plan's Deploy Rules, verbatim (OR lane `:8066`, FI dry-run `:8081`), PLUS step 0: `git -C /home/julio/projects/clean_diallux_SDR push origin engine/97-implementation` then on OR `git -C /home/julio/projects/clean_diallux_SDR fetch origin && git branch -f engine/97-implementation origin/engine/97-implementation` (the OR worktree `/tmp/opencode/wt-97` is checked out on it — pull INSIDE the worktree instead: `git -C /tmp/opencode/wt-97 pull --ff-only origin engine/97-implementation`; the parked `:8065` uvicorn keeps running old code until rebooted — do NOT reboot it, it is a comparison lane).
- iter99 lane (OR, after T0): `bash scripts/new_lane.sh 99 engine/98-service-tier speak-first` → boot `/tmp/opencode/wt-99/engine` on `:8067`: `cd /tmp/opencode/wt-99/engine && set -a && . ./.env && set +a && (setsid .venv/bin/uvicorn diallux.app:app --host 127.0.0.1 --port 8067 > /tmp/opencode/lane-8067.log 2>&1 < /dev/null &)` → `curl -s localhost:8067/health`.
- FI dry-run lane for iter99 authoring checks: port `:8082`, same boot pattern from a FI worktree of `engine/99-speak-first`.
- Before ANY reboot of anything touching `/tmp/opencode/lane-8021.log`: `cp /tmp/opencode/lane-8021.log /home/julio/projects/clean_diallux_SDR/research/surgeon/iter99-speak-first/lane-8021.t1era.preserved.log`.
- No merges without owner say-so (LAW 0). `scripts/keyhound` before every push. Commit registry refresh from the MAIN checkout's `engine/` dir at session end (backup `research/surgeon/iter47-call-ledger/ledger.db` first).

## Tasks (in order)

### T0 — Execute the iter98 plan AS IS
Goal: land `engine/98-service-tier` end-to-end exactly as ratified.
Step 0 (NEW, this plan): push the 97 tip FI→OR (Deploy Rules above).
Steps 1–7: open `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter98_service_tier_synthesis.md` and execute its Tasks T1→T7 in order, verifying each against its own Verification lines.
Verification: that plan's Validation Plan 1–4 all satisfied; `98_report.md` exists with probe + A/B + costs + verdict; master plan `plan_v5_iter97_implementation.md` on main tells the executed truth.
**STOP CHECKPOINT:** if its B3 keep-gate misses (p50 −100 ms not achieved), execute its own STOP (delete the tier line, report) — then CONTINUE to T1 below regardless (T1's lever is independent).

### T1 — Speak-first: attribution proof, prompt rule, A/B
Goal: prove (or kill) the tool-first thesis, then test the prompt fix on `engine/99-speak-first`.
**T1a — Attribution (zero-code, STOP checkpoint).** Copy `/tmp/opencode/lane-8021.log` to the evidence dir (preservation rule above). Parse the 27 `turn N final report:` lines (keys `llm_first_event_to_llm_first_ms`). For each turn, determine tool-first vs text-first from Langfuse: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python scripts/lf.py show <trace_id>` for `110fe70fdccd` and `1bfaf5cdcf81` — a gen whose window contains tool spans / whose output carries `tool_calls` = tool-first round; join turn↔gen by wall-time window (json `started_wall` + journal timestamps). If `lf.py show` does not expose per-gen `tool_calls`, query the Langfuse API directly with a small stdlib+`langfuse` script in the evidence dir (do NOT modify `scripts/lf.py`). Compute gap p50/p95 per group. Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter99-speak-first/99_attribution.md`.
Verification: two-group table with n, p50, p95.
**⟙ STOP CHECKPOINT:** if text-first-group gap p50 ≈ tool-first-group gap p50 (difference < 100 ms — the gap is NOT tool-ordering), the speak-first lever is DEAD: write the verdict, do NOT cut iter99, jump to T2 with the revised thesis recorded. Else continue.
**T1b — Cut + prompt rule.** Sibling cut (NOT atop iter98): FI `git -C /home/julio/projects/clean_diallux_SDR worktree add /tmp/opencode/wt-99 -b engine/99-speak-first 6044b9f` (fetch/push it to OR first: `git -C /home/julio/projects/clean_diallux_SDR push origin 6044b9f:refs/heads/engine/99-speak-first` if authoring on FI)... alternatively on OR: `bash scripts/new_lane.sh 99 6044b9f speak-first`; author on FI worktree (zeropull: FI author → push → OR pull). Edit `.../engine/diallux/prompts/general_prompt.md` — append to the head section, exact text:
`OUTPUT ORDER LAW: In every turn, write your complete spoken reply (natural sentences for the caller) BEFORE invoking any tool. Never open a turn with a tool call. If a tool is needed this turn, speak first, then call it.`
Verify composition first: `git -C /tmp/opencode/wt-99 show engine/99-speak-first:engine/diallux/graph/builder.py | sed -n '840,845p;1105,1112p'` (confirm `static_head` composes general_prompt.md into every state's system head — if NOT, add the same paragraph to each of the 9 state files instead). New pin `engine/tests/test_iter99_speak_first.py`: general head contains the rule verbatim; every `engine/diallux/prompts/*.md` still loads (utf-8, non-empty).
Verification: `bash /home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh tests/test_iter99_speak_first.py` green; full suite identical red set (517/1/5 shape + new pin). If a pre-existing prompt-content pin breaks, fix that pin ON THE BRANCH and record it in the report.
**T1c — A/B (suite on FI, batteries on OR).** Two OR lanes, IDENTICAL `.env` (same `OPENAI_SERVICE_TIER` state — whatever T0's B3 concluded; record which): base = `engine/97-implementation` tip (`6044b9f`) lane on `:8066` fresh boot; branch = `engine/99-speak-first` lane `:8067`. Suite/pins run on FI (per box-roles decision); the OR lanes run ONLY the battery pulls:
```bash
ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'cd /tmp/opencode/wt-99/engine && set -a && . ./.env && set +a && .venv/bin/python scripts/llm_mic_caller.py --ws-url "ws://127.0.0.1:8067/mic/ws?k=$VOICE_TEST_TOKEN" --scenario happy --persona Maria --max-caller-turns 21 --max-run-s 420 --out /tmp/opencode/iter99_speak_run1.json'
```
(same for `:8066` base with `--out /tmp/opencode/iter99_base_run1.json`; repeat for a second persona, e.g. `--persona Jorge`).
Keep gate: `llm_first_event_to_llm_first_ms` p50 **≤ 200 ms** on the branch (from 538) AND `e2e_response_ms` p50 **−150 ms minimum** vs base AND compliance ≥ 80% of branch turns with gap < 100 ms AND no new `findings`-class behavior (SOP battery light: happy-gate first, never stress a broken flow). Record compliance per state.
Verification: numbers into `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter99-speak-first/99_report.md`; cancel ALL test bookings (`/tmp/opencode/cancel_test_booking.py` pattern, cal.com v2, `cal-api-version: 2024-08-13`); miss → record, keep branch unmerged, report to owner (the prompt rule stays on the branch either way — owner decides).

### T2 — iter100 split-round design spec (NO build)
Goal: the engine-enforced, no-roulette design, fully specified for a future session.
Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter100-split-round/100_design.md` containing, at minimum: the in-node `asyncio.gather` shape (speak `astream(messages, tools=[])` ∥ tools `astream(messages, tools)`); Settings flag `round_split_speak_tools: bool = False` (`engine/diallux/config.py`, new `# ---- iter100 ----` section; SWITCH LAW: code default equals tested-on value at merge decision); TurnClock stamp policy (`llm_dispatch` once; `llm_first_event` from the speak call); iter46 T4a prewarm rewiring (tool_call_start signal moves to the tools call's stream); state-merge semantics (tool results apply at gather completion, before next round's `_build_messages`); cost model (2× input/round, cache-read mostly; record via `lf.py costs`); divergence risk + monitoring (speak-says-X / tools-return-Y as `findings` rows); byte-parity flag-off pin; A/B gates (gap p50 ≤ 50 ms structural + e2e_response −300 ms target + zero divergence in happy-gate); ports (`:8068` OR / `:8083` FI, provisional).
Verification: a fresh agent reading only the spec + this plan could cut `engine/100-split-round` without asking a design question (the lobotomized-agent test).

### T3 — Close-out
Docs to main (LAW 0 docs lane, `wt-main-docs-fi` pattern): ENV-SWITCHES register lines for anything T0/T1 added; `ITERATIONS.md` entries ON THE BRANCHES; commit registry refresh (backup first); `scripts/keyhound` before every push; ASK JULIO for all merges (LAW 0). Note the iter99 verdict's implication for iter100 priority in the report.

## Validation Plan (end-to-end)
1. T0's own validation (the iter98 plan's Validation Plan 1–4) fully green before T1b cuts anything.
2. Attribution table exists BEFORE any prompt edit; STOP checkpoint honored on a miss.
3. iter99 A/B: same-box, same-driver, identical lane `.env` both sides (SWITCH LAW #3), ≥50 turns total, gates as written in T1c, evidence + trace ids in `99_report.md`, bookings cancelled.
4. Suite red set byte-identical (the 5 named reds) at every commit gate; new pins green via fast_suite node list.
5. All evidence under `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter99-speak-first/` and `.../iter100-split-round/` (gitignored); nothing evidence-shaped inside `engine/`.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter100 split-round BUILD | design-only this session; own plan + session after the iter99 verdict |
| EOT knob values (Deepgram) | owner-owned, deferred — biggest unmeasured lever, outside this session's scope |
| iter97/98/99 merges to main | owner say-so only (LAW 0) |
| GK stress battery | AFTER a lane the owner blesses (ritual: book → capture validator uid → cancel) |
| Payload slimming (strip RAG from hot states) | worth ~15–40 ms at measured slopes — hygiene, re-rank after iter99/100 land |
| fast-tier pricing lookups beyond the iter98 plan's own T5/T7 | rides the iter98 plan |
