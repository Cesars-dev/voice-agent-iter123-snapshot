# 04_master_plan — iter97 implementation (AIRTIGHT)

Procedure: `tasks/surgeon/iter97-implementation/` · Date: 2026-10-08 · Status: **AWAITS OWNER GO** (framework step 5)

## Execution document (single source of truth)

**`/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md`** (committed to main per docs law)

This file does not duplicate it. The surgeon chain that produced it:
`01_audit.md` (code state @ `61bfc7e`, all anchors verified) → `02_action_plan.md` (design) → `03_cross_reference.md` (C1–C8 resolved, G1–G5 closed) → **this preflight**.

## Preflight verification (framework step 4 — traced against actual code)

| Claim | Verified at | Result |
|---|---|---|
| `t0` sits at `builder.py:2287`, anchor `ttft_s is None` at `:2322`, writer available from `:1801` | read this session | ✓ events can be fired exactly as specified |
| Custom events with new keys reach `session.py:877` and currently fall through | read `:874–880` | ✓ stamping insertion point is real |
| `model_kwargs` attach-only-when-non-empty at `llm.py:237–238` | read `:216–263` | ✓ hoist design preserves flag-off bytes |
| `llm_for_verbosity` twins rebuild kwargs separately at `:271–284` | read | ✓ second injection site confirmed |
| `service_tier` absent repo-wide | grep | ✓ zero hits |
| `_writer_task` spawn `:214`, `_liveness_task` `:215–218`, stop-cancel `:302–304` | read | ✓ drain-task placement beside them works |
| Class-level task-default pattern exists (`_ladder_task` `:368–369`) | read | ✓ pattern to copy |
| `/media` inline on_media at `app.py:170`; `/mic/ws` at `:225` with stamp at `:220–223` | read | ✓ branch points exact |
| Launch surfaces: `engine/deploy/diallux.service` ExecStart, `engine/Dockerfile:17` CMD, bare-uvicorn lane boots | read + live ps on OR | ✓ all three carry no `--loop` today |
| `new_lane.sh` numeric guard + base-arg accepts branch names | read `:41–55` | ✓ `97 61bfc7e implementation` and `98 engine/97-implementation service-tier` are valid invocations |
| fast_suite `--touched` behavior + config.py full-suite trigger | read script | ✓ pin groups additive, no conflict |
| Suite baseline 516/1/5 | on record (session plans, both boxes) | ✓ T0 re-verifies on the lane |
| Mic probe CLI exists (`--scenario happy`, `--journal-log`) | read argparse | ✓ commands in plan are runnable |
| Ports `:8021` (FI) / `:8065` (OR) free-reserved | iter96c plan reserved them; iter96c superseded by this plan | ✓ reused; lanes `:8049/:8050/:8063`, services `:8000–8003`, `:8080` untouched |

## Flaw-resolution log (from 03)

- FLAW-1 (`t_tts_req` missing) → T1.4 ships partial `bench_aliases`, omission recorded. CLOSED.
- C1 numbering/branch conflict → owner's latest directive encoded (one cut per fix; `engine/97-implementation` → `engine/98-service-tier` from its tip; no iter99). CLOSED.
- C2 suite gate → identical-red-set gate, T0 snapshots red names. CLOSED.
- C3 T4 scope → eval-only with a numeric decision rule (≥150ms sustained p50 delta vs raw probe = candidate; within ~50ms = dead). CLOSED.
- C4 iter96c overlap → superseded by T1; recorded in plan + NEXT_STEPS. CLOSED.
- C5 wrong deploy path → corrected to `engine/deploy/` + `engine/Dockerfile`. CLOSED.

Open items that are OWNER-gated by design (not flaws): phone-path Twilio verdict, prod `.env` flips, fast-tier pricing check, final merges (LAW 0).

## GO gate

Framework step 5: **no code is touched until the owner reads `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter97_implementation.md` and says GO.** On GO, execution order is T0 → T1 → (checkpoint) → T2 → T3 → A/B → T4-eval → report → ASK; iter98 only after the iter97 report is read.
