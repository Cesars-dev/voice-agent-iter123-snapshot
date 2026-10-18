# 03 CROSS-REFERENCE — audit (01) vs action plan (02)

Method: every flaw/risk from 01 checked for coverage in 02; every 02 element checked for support in 01. Contradictions, gaps, redundancies hunted.

## A. Flaw coverage matrix

| Audit flaw | Covered in 02? | Where / note |
|---|---|---|
| F1 wrong ITERATIONS.md path | ✅ | T5.1 names `engine/ITERATIONS.md` |
| F2 stale suspect list | ✅ | T3 works ONLY from the T1-measured list (≥5s cumulative); F2 files explicitly not assumed |
| F3 mischaracterized iter95 pattern | ✅ | T3.1 names the iter94 `_clocked` template as THE pattern; iter95's small-real-sleep style not treated as a template |
| F4 unproven 20–25 min premise | ✅ | T1 decision gate: ≤3 min → T3 cancelled, report to owner. This is the biggest single change vs the original plan |
| F5 hidden verdict line (-qq) | ✅ | T1 command + fast_suite.sh both drop the extra `-q`; T2.3 verification explicitly asserts the verdict line is visible |
| F6 broken invocation path | ✅ | T2 verified via absolute path `…/scripts/fast_suite.sh` from lane `engine/` cwd; usage header documents cwd contract |
| F7 empty-selection full-suite fallthrough | ✅ | `run()` exits 0 on empty; T2.5 verifies |
| F8 new_lane.sh numeric gate | ✅ | Mode B spec: numeric workaround + branch rename (9494 precedent). **Gap check:** 02 T0/T2 do not restate the exact Mode B command — see resolution R-a below |
| F9 moved iter95 state / base commit | ✅ | T0.3 asks the owner to confirm base post-merge-decision; pre-flight check for concurrent sessions (R1) added |
| F10 plan not on main | ✅ | New pre-step T-1 (docs law landing) |
| F11 wt-main-docs cannot run pytest | ✅ | fast_suite.sh uses the canonical venv by absolute path; no worktree mutation needed |
| F12 monotonic patch surface | ✅ | T3.1 requires per-file clock check + same-virtual-time extension for monotonic paths |
| F13 config.py import explosion | ✅ | `--touched` short-circuits to `--full` with a notice when `diallux/config.py` is in the diff |
| F14 transient ENOENT | ✅ (partial) | Pre-flight `ps`/`worktree list` sanity; T1 gate file written with absolute paths. Residual risk accepted + on record |
| R1 concurrency (lane 9494) | ✅ | T0 pre-flight check |
| R2 xdist on 2 vCPU | ✅ | T4 opt-in, count-identity, uninstall-on-mismatch |
| R3 T3 ROI | ✅ | T1 gate + T3.2 do-not-touch list |
| R4 Mode A = law change | ✅ | T0.4 AGENTS.md one-line amendment owner-approved |

## B. Does the audit support every action-plan change?

| 02 element | Audit support |
|---|---|
| T-1 landing the plan | F10; LAW 0 docs law (AGENTS.md) |
| T0 four-part ask | F9, R1, R4; plan's own BLOCKED table |
| T1 command shape (no extra -q, `time`, exit code) | F5 (verified live both ways); §3 (no durations log exists anywhere) |
| T1 decision gate ≤3 min | §3 evidence: 88s ledger at same engine code, ≈30–45s sleep budget, fast spot-runs |
| T2 script draft | F5/F6/F7/F11/F13 + verified pytest.ini/conftest/venv facts §1; canonical-venv path verified working from wt-95 |
| T3 pattern choice + do-not-touch list | §5 pattern catalog (iter94 committed template; iter84 style); §6 clock map; §3 sleep census (cancel targets, settle-yields) |
| T4 pip discipline | AGENTS.md pip trap; LANE LAW 2 |
| T5 paths + registry ritual | F1; AGENTS.md rules 3/8 |

## C. Contradictions found

1. **Original plan T1 vs its own premise:** the plan says "profile FIRST, no guessing" but pre-commits to a suspect list and a T3 conversion workload. The audit shows the suspects are seconds-fast (F2) and the premise itself is doubtful (F4). 02 resolves by making T1 binding (gate), not decorative. **Resolved.**
2. **Original plan T2 spec (`pytest "$@" -q`) vs F5:** the specced script would hide verdicts — the exact disease the SDK exists to cure. 02's draft drops the `-q`. **Resolved.**
3. **Original plan Mode B command (`new_lane.sh 95sdk …`) vs the script's numeric gate (F8):** impossible as written. 02 fixes via numeric workaround + rename. **Resolved (R-a).**

## D. Gaps found & resolutions

- **R-a (from F8):** 02 didn't spell out the Mode B lane command. Resolution (folded into the master plan): `bash /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh 9595 <base> sdk` → branch auto-named `engine/9595-sdk` → `git branch -m engine/9595-sdk engine/iter95-sdk` pre-commit (the same rename move used for iter94/95, per the worktree list). Numeric doubling precedent: lane 9494, manifest 07:19:51 today.
- **R-b:** 02 T2.4 asserts wt-95's diallux diff is empty post-commit — true at audit time (`git diff --name-only HEAD -- engine/diallux` = clean after 63e013c); the 2 dirty TEST files are the selection. Verified.
- **R-c:** T3 "one file per commit" + mode A straight-to-main means each conversion lands on main individually — bounded by the per-file before/after proof + `--touched` gate; acceptable per the plan's own landing-mode analysis. No change.
- **R-d:** the `--touched` grep mapping is heuristic (untracked NEW diallux modules are invisible to `git diff HEAD`). Accepted: heuristic + `--full` fallbacks documented; the merge gate remains the full suite once per branch/session.

## E. Redundancies

- The original plan's T3 suspect pre-list is now redundant (T1 decides) — kept only as a falsified reference in the audit, not as a work list.
- Nothing else redundant; T4 remains correctly optional.

## F. Verdict of the cross-reference

Every audit flaw has an owner in 02; every 02 change is audit-supported; the three contradictions and four gaps are resolved (R-a..R-d). The plan's architecture (three-mode script, profile-first, opt-in xdist, docs close) survives; its premise, its evidence commands, its file map, and its Mode B mechanics needed surgery — done in 02, finalized in 04.
