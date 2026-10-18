# Wave plan PT-3 — transition beat (PARKED; re-decide after PT-1 + PT-2 + one real call)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: status record ONLY — nothing is built, nothing is cut. The task: transition acks carry the next question in the same turn ("Perfect — so how many calls a week are you missing?").
- Status: **PARKED (owner 2026-10-10)** — decide AFTER PT-1 verifies and PT-2 lands + one real call.
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-3 specific: the win exists ONLY on the parked `engine/iter68-speech-flow` branch (`turn_asked` flag @ that branch's builder.py:2403/2516/2562/2588) — never re-landed on main; the iter68 chain is the owner-condemned hot zone (total-failure post-mortem 2026-09-23; NEVER cherry-pick). Oct-6 evidence: 3 stacked question-turns around the Discovery→Closer transition (09:26:00/09:26:04/09:26:22) on iter95-era code.

## Why parked (the collision, spelled out)
- PT-2's ask-chop makes "one question per round then yield" a HARD code rule. PT-3's beat wants the TRANSITION ack round to ask the next question — i.e. exactly one question, carried by the ack. The two must not fight over the transition round: the state-transition write must guarantee the beat round (an `entry_lite` ack) is EXEMPT from the continuation-silence gate (it speaks by design) while still subject to the one-question chop.
- The re-decide gate (owner): PT-1 verified (echo dead) + PT-2 landed + ONE real call listened. If the real call's transitions already flow (PT-2's chop + the existing entry_lite acks asking naturally), PT-3 dies as redundant; if transitions still waste a round, PT-3 revives as a SMALL fresh build (a `turn_asked`-style one-trip flag, re-coded on the then-current main, never ported).

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| The re-decide input: PT-1 verified + PT-2 merged + one real call on the lane | the wave chain (master plan) |

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| — | nothing, by owner order | — |

## Tasks
- NONE. This file exists so the master plan's index has a row for PT-3 and nobody re-opens it out of context.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| The beat itself | parked — see above |
