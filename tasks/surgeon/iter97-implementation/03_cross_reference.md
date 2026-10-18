# 03_cross_reference — iter97 implementation

Procedure: `tasks/surgeon/iter97-implementation/` · Date: 2026-10-08
Method: `01_audit.md` ↔ `02_action_plan.md` compared line by line; every contradiction/gap/redundancy resolved or escalated below.

## 1. Coverage matrix (audit issue → plan task)

| Audit item (01 §) | Addressed by (02 §) | Status |
|---|---|---|
| Missing dispatch decomposition (B1) | T1.1–T1.5 | ✓ full chain: fields → marks → writer events → session stamps → report keys → metrics |
| Builder anchors `:2287/:2322` (A) | T1.2 | ✓ exact anchors used |
| Session branch `:877` falls through new keys (A) | T1.3 | ✓ stamps BEFORE tts_token check, first-only |
| No `bench_aliases` (A) | T1.4 | ✓ with honest caveat: `t_tts_req` clock doesn't exist — partial alias set allowed, omission recorded (FLAW-1 resolved) |
| Twilio interarrival missing (B2) | T1.5 + T3.3 | ✓ metric declared in T1, stamped in T3's reader edit |
| Inline media parse/head-of-line (B3) | T3 | ✓ queue+drain, flag OFF default, drop-oldest + counter (R5) |
| No-`__init__` test pattern (R6) | T3.2 | ✓ class-level defaults, `_ladder_task` pattern cited |
| One-loop discipline (R8) | T3.2 | ✓ ONE queue/ONE drain law written |
| uvloop unpinned/unproven (B4, R7) | T2 | ✓ pin + launch args + `/health` proof + honest already-active clause |
| mk hoist byte-parity trap (R1) | iter98.2 + test spec | ✓ attach-only-when-non-empty + byte-equality pin test |
| Boot prewarm third site (R2) | iter98.2 | ✓ explicitly NOT tiered, reason recorded |
| Eager-EOT anchoring (R3) | T1.6 test spec | ✓ tests must not assume plain-EOT base |
| Mic stamp order (R4) | T3.4 | ✓ stamp before enqueue |
| Anchor drift in owner plan (R9) | 01 §A table | ✓ all anchors re-verified at `61bfc7e`; master plan instructs re-grep before edit |
| Tier name `fast` vs measured `priority` | iter98.4 probe | ✓ no-400 probe before any lane flip |
| fast_suite has no pin groups (B6) | fast_suite § | ✓ `--iter97` / `--iter98` groups |
| Suite baseline 516/1/5 (not 496/3) | T0.1 | ✓ exact-red-set gate, T0 records the 5 names |

## 2. Contradictions found & resolved

| # | Contradiction | Resolution |
|---|---|---|
| C1 | Owner plan mints iter97/iter98/iter99 as three sibling iterations; repo directive (2026-10-08) said "everything rides iter97"; owner's LATEST word (this session): one cut per fix, iter98 from iter97 tip, iter99 stale | Owner's latest directive wins (it supersedes his own earlier one — recorded verbatim in 01). Branch names: `engine/97-implementation`, `engine/98-service-tier` (new_lane numeric guard; iter96 precedent). NO iter99. |
| C2 | Owner plan: "full suite green (496+/3/0)" | Reality: 516/1/5 with 5 pre-existing reds. Gate redefined = identical red set + new tests green. T0 snapshots the red names. |
| C3 | Owner plan T4 = build raw-SDK speak path | Owner verdict: T1–T3 then measure; T4 = EVAL ONLY (raw-vs-lane TTFT delta rule). Build spec preserved in owner plan §T4 for the future owner-gated phase. |
| C4 | iter96c loop-lag probe (plan-only, never cut) overlaps T1 | T1 SUPERSEDES iter96c (decomposition > lag-overshoot). Master plan records the supersession line so nobody runs iter96c. Ports reserved for iter96c (`:8021` FI, `:8065` OR) are reused by iter97. |
| C5 | Owner plan phases reference `deploy/diallux.service` at repo root | Real file: `/home/julio/projects/clean_diallux_SDR/engine/deploy/diallux.service` (repo-root `deploy/` does not exist). Dockerfile = `engine/Dockerfile:17`. Corrected in 02 T2. |
| C6 | Owner plan: `warm()` routes through raw serializer when flag on (T4 warm parity) | Deferred with T4 (not built). iter98 warm twin inherits tier via `**kwargs` — no serializer change, cache bytes untouched by tier (97_analysis: cross-tier cache read preserved). |
| C7 | 97_analysis recommended `engine/iter98-quick-wins` cut from main | Superseded by owner's sequencing (heavy lifting first, tier second, from iter97 tip). The tier EVIDENCE from 97_analysis carries over unchanged. |
| C8 | Owner plan exit gate for T3 mentions phone-path metrics | Phone path needs a real Twilio call = owner action. Plan gates on mic-lane A/B; phone verdict = owner-gated follow-up (recorded as pending-owner). |

## 3. Gaps found & closed

| # | Gap | Closure |
|---|---|---|
| G1 | `bench_aliases.tts_ttfb` needs `t_tts_req`, which TurnClock lacks | T1.4 ships partial aliases (`llm_ttft`, `e2e_latency`); omission recorded in report; NO new TTS-side clock in T1 (scope discipline) |
| G2 | Where do lane-boot commands get `--loop uvloop`? | Lanes boot as bare background uvicorn — the master plan's lane-boot step embeds the arg in the command line (single place) |
| G3 | Who cuts the branch — FI or OR? | 02 §Branch: OR opens lane via new_lane (creates branch); FI tracks it (`git switch --track`). ONE branch, no duplicates. |
| G4 | fast_suite update on main or branch? | Rides the branch (whitelist permits either; traveling with the pins avoids a main/branch skew). |
| G5 | `config.py` edit forces full suite via fast_suite `--touched` | Intended behavior; noted in 02 so the executing agent doesn't think it's a bug. |

## 4. Redundancies
- None material. The owner plan's invariant list (§NON-NEGOTIABLES) is absorbed into the master plan's Deploy Rules rather than restated per-task.

## 5. Escalated to owner (BLOCKED items in master plan)
- Real-Twilio phone-path verification (owner fires the call — same class as PT-85).
- Lane flips `MEDIA_FRAME_LANE=1`, `OPENAI_SERVICE_TIER=fast` on any PROD surface (owner-gated; test lane first).
- Exact gpt-5.4 fast-tier pricing at implementation time (probe + pricing page; 2x figure is the working assumption).
