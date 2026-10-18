# Wave plan PT-7 — Intake refer-tag shape (FOLDED into PT-5 + a prompt ride on say-so)

## Meta
- Date: 2026-10-10 (authored in the iter102b master-plan session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: status record ONLY — the task is FOLDED (owner 2026-10-10: "if it's not worth its own branch, it's not a task"). No branch, no build, no further analysis.
- Status: **FOLDED**.
- Master plan: `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter102b_wave_master_plan_authoring.md`

## Compaction Context
Shared wave context: see `/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-8_pre_llm_gap_stopwatch.md` §Compaction Context.

PT-7 specific — the analysis that closed it (owner verdict 2026-10-10, census DONE):
- The WHAT-anchor text inside laneA queries is a DELIBERATE iter48 design: `parse_refer_tags` (rag.py:593) + `refer_query` (builder.py:1118-1150) build query = WHATs + non-empty dv values + caller text. The Oct-8 canned queries were BY-DESIGN anchor fires with EMPTY dv values (the caller sat 6 minutes in Intake with values never captured — a model-behavior issue, not tag pollution); 9/34 zero-hits were model-misbehavior fires on fragments, not anchor defects.
- The repeat COST of those fires dies with PT-5's memo (`/home/julio/projects/clean_diallux_SDR/plans/iter102_plus_wave_edits/plan_wave_PT-5_rag_query_memo.md`).
- The remaining taste question — keep or shorten the WHAT anchors — is a PROMPT-layer ride (Intake.md is code-zone, LAW 0), on explicit owner say-so only, never a standalone task.

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| — | nothing, by owner order | — |

## Tasks
- NONE. Pointer only: the anchor tune, if ever wanted, rides a future engine branch's prompt hunk with its own ASK.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| WHAT-anchor shortening | folded: prompt ride on owner say-so only |
