# NEXT_STEPS — the live queue (one item at a time)

> Updated: 2026-09-17 (later) — iter54-assessment session.
> Previous queue (HVAC V3 polish, 2026-08-01) → `plans/archive/NEXT_STEPS_hvac-2026-08-01.md`.

> **NAMING CONVENTION (owner decision 2026-09-17 — applies going forward):**
> `iter<N>` = a CODE iteration (branch + commits + battery). A PLAN is a plan — it does
> not own an iter number. Historical drift to keep straight when reading old docs:
> iter43 = real branch, ABANDONED (`engine/iter43-eot-cache-askgate`, tag `iter43-failed`);
> iter44 = real branch (`engine/iter44-cache-floor`); plan FILES named `plan_iter43_*` /
> `plan_iter44_*` are their plans (missing the `v5_` prefix — cosmetic). `mvp-finally`
> was deliberately NOT iterNN-numbered ("iterations = commits"). iter55 follows the
> convention: one iter = one plan = one branch. (Formal note rides
> `engine/ITERATIONS.md` on the next branch closeout — do not hand-edit it on main,
> the iter52 branch carries its newest version.)

> **NEXT UP (owner 2026-10-09): the live queue = `plans/PENDING_TASKS.md` -> LIVE BACKLOG (head = PT-0, the next-session wave eval; branches/commits per PT typed, plan written, then applied). The items below are the 2026-10-08 queue — historical.**

## NOW

> Updated: 2026-10-10 (later) — iter102b session EXECUTED + LANDED (THE wave master plan + 11 per-iteration plans; `lf.py pair` SDK cherry-picked to main); next = owner GO → stack-branch cut.

0. **DONE 2026-10-10 (iter102b session): `plans/plan_v5_iter102b_wave_master_plan_authoring.md` EXECUTED + LANDED** — 11 per-iteration plans in `plans/iter102_plus_wave_edits/` + THE wave master plan (iter81 style, absorbed this session plan); edit-specs closed inside the PT-5/PT-8 plans; `lf.py pair` SDK cherry-picked to main (owner order, zero-conflict). **NEXT: owner GO → W1 = cut THE STACK BRANCH from main; PT-11 trace runs first (zero-code), then per-PT commits PT-8 → PT-5 → PT-6 → PT-4 → PT-11-wire; chain per the master plan (PT-1 next, PT-2 after, PT-9 LAST from the 98 tip).**

0. **DONE 2026-10-08: `plans/plan_v5_iter97_implementation.md` executed** — branch `engine/97-implementation` @ `6044b9f` (D1 `2943d88`, D2 `6044b9f`): T1 clock truth landed; STOP CHECKPOINT FIRED (dispatch p50 70 ms — loop thesis DEAD, T3 skipped); T2 honest-skip (already uvloop); T4-eval DEAD. Master plan updated to executed truth (`414fed2`). UNMERGED — LAW 0 owner say-so.
1. **DONE 2026-10-08: `plans/plan_v5_iter98_service_tier_synthesis.md` executed** — branch `engine/98-service-tier` @ `abbd9d8`: B1 knob + byte-parity pins (suite 526/1/5), B2 `"fast"` ACCEPTED (paired p50 1124→856.5), B3 same-lane A/B n=42+42: dispatch→first p50 **−378.5 ms = KEEP GATE PASSED 3.8×** (`fast` kept on lane env, code default `""`). Report `research/surgeon/iter98-service-tier/98_report.md`. UNMERGED — owner say-so + pricing-page lookup BLOCKED.
2. **DONE+VERDICT 2026-10-08: `plans/plan_v5_iter99_speak_first.md` T1a-T1c executed** — branch `engine/99-speak-first` @ `e3a3fb2` (sibling, NOT atop 98): attribution PROVEN (tool-first n=10 gap p50 1,931 vs text-first n=17 p50 388.8 — mapping in `99_attribution.md`); prompt rule A/B (default tier both sides since sibling cut lacks the knob) **ALL GATES MISSED** (branch gap p50 460.5 vs base 117.3, e2e +247.7 WORSE, compliance 2.4%) → prompt-rule route DEAD on this data. Rule stays on branch, owner decides. Report `research/surgeon/iter99-speak-first/99_report.md`. UNMERGED.
3. **NEXT: BUILD iter100 split-round OFF the spec** — `research/surgeon/iter100-split-round/100_design.md` (in-node asyncio.gather: speak astream(tools=[]) ∥ tools astream(tools)); cut `engine/100-split-round` from `engine/98-service-tier` tip; new Settings flag `round_split_speak_tools` (default False → flip at merge decision); pins per §9 of the spec; A/B on OR :8068 / FI :8083; gates p50 ≤50 ms structural + e2e −300 + compliance ≥80% + zero new findings.
4. **PARKED (agreement 2026-10-07): iter96 merge = PT-85** — owner fires a real Twilio call at OR lane :8063 (`wt-96` @ `b81b382`, live) → forensics vs baseline trace `152d98c0` → PASS = merge on cost merits (token-cost/wire-bytes win; latency gain honest ≈ −0…20 ms) on owner say-so. 96b forensics: research/surgeon/iter96-delta-cache-layout/96b_ttft_forensics.md.
5. **PROTECTED: `engine/iter73-oregon-wip-20260924` = owner prod endpoints config — DO NOT TOUCH** (marker `61a88ff`, pre-push hooks both boxes, mirror repo `Cesars-dev/clean-dialux-sdr-guard`; AGENTS.md PROTECTED BRANCH).
6. Merge-candidate triage queue: PT-86 (iter79 fix-verify), PT-87 (iter82/iter86 instruments) — owner-gated, low priority.

Previous queue (2026-09-23 iter67 era) follows; historical entries kept for traceability.

0. **RESUME `plans/plan_v5_iter67_twilio_resume_t6_t7.md` — iter67 Twilio lane is LIVE on the VPS** (`https://twilio.diallux-ai.site`, systemd :8026, signature gate on, suite 434). Next: T6 repoint `+18885958927` → the engine (owner say-so: "repoint") → T7 owner-ears call + ledger + report. Branch `engine/iter67-twilio-live-lane` @ `0394a3b` pending merge (T8, after iter66 merges first).
1. **EXECUTE `plans/plan_v5_iter55_tts_era_turn1_ammo.md`** (owner GO pending):
   production-era truth + turn-1 "ammo locked" landing. Finds in one session:
   (a) the live :8000 engine runs **iter40-era code — the cache machine never
   shipped** (verified: zero `prompt_prewarm`/`first_turn_lite` in the deployed
   config); (b) warm-completion time is measured NOWHERE (zero spans) — T0 adds
   warm + greeting spans; (c) owner gates are HARD: first 3-4 turns TTFT ≤900 ms,
   worst case TTFT ≤1,100 / hear ≤1,400 ms; (d) sequence: T0 spans → warm p90
   table → O5 (tail shrink) → turn-1 full-round probe (`FIRST_TURN_LITE=false`)
   → fallback "one moment, taking notes" ONLY if misses remain (default OFF).
   Supersedes `plan_v5_iter54_turn1_cache_landing.md` (its O1-O5 menu collapsed:
   O3/O4 dead under the 1,100/1,400 gates; O1 direction owner-confirmed, gated on T0).
2. **Julio — merge ASK: `engine/iter52-industry-pin` @ `a36bdd7`** (ONE clean commit:
   iter52 feature + docs + LAW 0 v3 + Mike Rourke persona; suite 333 green ×2 modes;
   battery-iter52 4/4 + plumber A/B PASS). Branch verified conflict-free vs main
   (`merge-tree` exit 0). Standing ASK since 2026-09-16. (iter55 cuts from this branch's
   HEAD `054af7b` regardless — merge order is owner's call.)
3. **HITL — owner decisions iter55 needs (no agent answer exists):**
   - Real-path test level: browser mic-bridge battery only, or + one REAL Twilio test
     call (test number + webhook change; production agents untouched).
   - "One moment, taking notes" filler copy approval (T6, only if misses remain).
   - Turn-1 EOT wait ceiling: keep 500 ms or raise (decide AFTER T0 warm numbers).
   - warm_rag / KB-resolve keep-drop-reorder at call start (owner directive: NO KB
     loads before/at the lite turn; physics check: warm_rag is async but feeds the
     turn-2 first heavy round's embed — measure with T1 greeting span, then decide).
   - **Cutover authorization** — the endgame ASK: the deployed :8000 has never run the
     cache machine; the lab evidence is meaningless to production until it ships.
4. *Previous top item:* ~~Julio — Phase B engine-owned state machine~~ (still parked,
   `phaseB-wip` stash — superseded in priority by the ASKs above).

## NEXT (owner-gated — nothing happens without Julio's word)

- **Services cutover to the fork's engine** — the item behind ALL the latency work:
  the deployed engine is iter40-era, so every lab gain (lite head, warms, await split,
  RAG lanes, industry pin) is invisible to real callers until cutover.
  MIGRATION_MAP.md checklist; real-path validation rides iter55 T2.
- ~~**Merge iter29 → iter30 → iter31-c3d stack into `engine/main`**~~ STALE
  (superseded 2026-09-16: main @ `4559a33` = the MVP merge of `engine/mvp-finally`
  cut from `engine/iter49c-engine-finish` — that stack is already in main).
- ~~**Cut iter32**~~ STALE (superseded by iters 33-52; the "gen-p50 ≤1.2s prefix work"
  it carried landed via the iter43-48 cache work; Pedro over-book guard + Phase B
  remain parked, re-triaged on their own merits).
- **iter53 hygiene plan** (`plans/plan_v5_iter53_git_hygiene_rag_next.md`, parked at
  ref label `engine/docs-archive/fec12dd-plan53`) — docs-only, T1–T7 unexecuted,
  independent of iter55; schedule = owner's call.

## OWNER GitHub actions (agent cannot)

- [ ] Delete stray repo `Cesars-dev/scope-test-nonexistent` (empty; token lacks delete scope)
- [ ] Rotate the V7.9 PAT burned in the ORIGINAL repo's `.git/config` (see PENDING_TASKS security ledger)
- **NICE-TO-HAVE (iter87 follow-up): per-state prewarm on/off switch** — a dedicated
  toggle for warming ONLY specific chain destinations (e.g. `prewarm_chain_off: str = ""`
  comma-list knob in the same style as `state_entry_lite_off`, one `if` around the iter87
  chain-fire loop). Today the new fire sites are gated only by the `PROMPT_PREWARM`
  master switch + `WARM_AWAIT_DEST_MS` hold knob. Owner deprioritized for this build.
