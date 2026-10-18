# 03 — CROSS-REFERENCE — audit (01) vs action plan (02) vs merged plan (plans/plan_v5_iter70_speech_fixes_merged.md)

Method: every audit finding (A1-A22) checked for plan coverage; every planned change checked for audit support; every contradiction/gap/redundancy recorded. Verdict per item: COVERED / GAP / CONFLICT.

---

## 1. Audit findings → action-plan coverage

| Audit # | Finding | Action plan coverage | Verdict |
|---|---|---|---|
| A1 | Reference directive lost when all dvs empty (`if state_delta_block:` nesting) | 2.4.3 — directive appends to delta independent of state-block emptiness | COVERED (fixed) |
| A2 | llm.json not byte-parity for Intake/Discovery/Closer; only Offer is | 3.4 — same-lines-into-own-base mirror; Offer stays identical; lockstep test green; refer=36 verified | COVERED |
| A3 | 4 legacy tests pin the flat-ack one-trip | 3.5 — exact token updates (same as 22e6f88) | COVERED |
| A4 | T4p target ambiguity (VOICE_OUTPUT_RULES vs per-state .md) | T4p HITL — owner picks target + wording | COVERED (owner gate) |
| A5 | `_run_turn` lacks `extra_payload` | 2.3.5 | COVERED |
| A6 | GraphState missing `turn_asked`/`pause_reask` | 2.2 + 3.1 | COVERED |
| A7 | 22e6f88 extras (fast-flush flip, min_chars knob, letter-spelling line) | T3 header EXCLUDES them; PT-71 env carries fast-flush | COVERED (excluded by design) |
| A8 | c6159ce extras (cancel-safe gen spans, observability knob) | 5.1 — no knob, unconditional INFO; gen spans out | COVERED (excluded by design) |
| A9 | Arm timing = end of `_late_turn_report` (~3s drain wait) | Accepted in audit; unchanged in 02 | COVERED (accepted) |
| A10 | Greeting never arms timer | Accepted (matches reference + ear-check scenario) | COVERED (accepted) |
| A11 | Re-ask counts toward turn/time caps | Accepted (safety) | COVERED (accepted) |
| A12 | `_cap_hit()` at arm AND fire | Present in 2.3.6/2.3.7 code | COVERED |
| A13 | Re-ask turn RAG: no laneB fire; laneA dvs-driven | Accepted | COVERED (accepted) |
| A14 | config.py duplicated blocks | Out of scope, not fixed | COVERED (documented, untouched) |
| A15 | Env LAW knobs must stay (cartesia pin, semantic=false, sentences=on) | Never-touch list carried; T4' adds NEW knobs only | COVERED |
| A16 | entry_lite speech-only directive coexists with T3 prompt directive | Accepted (reference shipped this; escape hatch exists) | COVERED (accepted) |
| A17 | Engine one-trip change covers ALL 9 states' transitions but only 4 prompts carry the directive | **02 does NOT mention it** | **GAP G-1** → resolve in master plan: flag at T3 HITL stop + report |
| A18 | Deploy copies all prompts (no-op for unedited ones) | Accepted | COVERED |
| A19 | Suite expectations (476+1 env fail+1 flake) | Verification sections | COVERED |
| A20 | HITL gates inside task order (T4' thresholds, T4p lines, merge) | Preserved (02 header + T4'/T4p/T7) | COVERED |
| A21 | Docs→main on MAIN checkout; pre-existing dirty SOP file never staged | T7 | COVERED |
| A22 | Class-level `_pause_reask_task` default for no-init tests | 2.3.1 | COVERED |

## 2. Planned changes → audit support

| Plan item | Audit support | Verdict |
|---|---|---|
| T2 timer mechanics (session.py ~52 lines) | 651e567 read in full; anchors verified (L278, 598, 638, 645, 676-717) | SUPPORTED |
| T2 ingest guard shape | builder.py:2737-2742 verified; empty-append flaw confirmed | SUPPORTED |
| T2 knobs 10000ms | Owner law in plan; config layout verified | SUPPORTED |
| T3 route change | 22e6f88 diff verified against main's L2793-2799; behavior delta isolated to flat-ack case | SUPPORTED |
| T3 turn_asked flag plumbing | Sites verified: seed (L2267 region), mid-stream append (L2354-2361), stream-end append (L2440-2447), updates (L2469), ingest (L2722) | SUPPORTED |
| T3 directive lines | 22e6f88 verbatim; current prompt files read — lines absent today | SUPPORTED |
| T4' helper + insertion points | Flush sites verified (L2323-2324, L2419-2420); window key format verified (normalized strings) | SUPPORTED |
| T4' replay mirror | speech_replay.py structure verified (L27-33 imports, L107-182 replay) | SUPPORTED |
| T5 log helper + sites | c6159ce shape verified; mic_events RULES/_CALL_TAGS verified | SUPPORTED |
| T6/T7 blocks | Copied verbatim from the merged plan's Deploy Rules | SUPPORTED |

## 3. Contradictions found

| # | Contradiction | Resolution |
|---|---|---|
| C-1 | Merged plan T2 directive paraphrase ("the caller has gone quiet — re-ask ONCE, shorter, differently worded, then stop") vs reference verbatim text ("has gone SILENT … shorter, warmer, differently worded … Do not call any tool this round.") | Plan law = VERBATIM carry from iter68 surgeon plans → use the reference text (02 does). Master plan pins the exact string. |
| C-2 | Merged plan T5 stage list omits `semantic`; reference c6159ce logged it | Correct omission — the semantic branch is env-dead (`TTS_DEDUPE_SEMANTIC=false`); logging a dead branch is noise. Keep omitted. |
| C-3 | 02 says T5 "(6 total)" log call sites but the site list enumerates 7 (4 mid-stream: ff_cut/sanitize/exact/similar + 3 stream-end: sanitize/exact/similar) | Counting error in 02 — master plan fixes to 7 sites (~12 lines, still within "~10 log lines" tiny scope; ff_cut never fires on the lane because fast-flush is env-off). |
| C-4 | 02 T5 says stream-end exact drop logs inside the current `if not (...)` gate — but the exact hit is the gate's FALSE branch; logging it needs a companion branch (the reference restructured the block) | Master plan specifies the minimal +3-line companion-branch shape (double-evaluate the condition, zero behavior change). |
| C-5 | 02 commit map: T2 ~75 lines / T3 ~60 lines vs PT-73 "≤60 lines, >50 needs owner sign-off" | Not a true conflict — the merged plan is owner-approved and mandates HITL at every T; master plan makes explicit: each HITL stop shows the owner the EXACT diff before the commit is made (sign-off = the stop itself). |
| C-6 | Merged plan File Map puts `speech_replay.py` under T4' AND T5; 02 splits (jaccard mirror in T4', CUT-print parity in T5) | Consistent with the plan's own task text (T4' says "log via T5 line", T5 says "speech_replay mirrors the jaccard rule"). Keep 02's split; both land before the ear test. |

## 4. Gaps found

| # | Gap | Resolution in master plan |
|---|---|---|
| G-1 | A17 (engine one-trip change is global; prompt directives only in 4 states) not surfaced in 02 | T3 HITL stop includes the one-line owner flag: "engine guarantee applies to ALL transitions incl. contact_details→ConfirmSlots etc.; the scripted-question directive ships only in Intake/Discovery/Closer/Offer (reference scope) — OK?" |
| G-2 | Battery harness cannot exercise T2 (session-layer timer; harness drives CallRuntime directly) | Master plan T6 notes: T2 is proven on the mic lane ONLY (ear checklist item 1); battery proves T3/T4'/T5 speech behavior + booking flow. |
| G-3 | 02 does not state where the T4' stream-end similar check sits relative to the (dormant) semantic block | Master plan pins the order: exact → similar → semantic (similar BEFORE semantic so the env-dead branch never masks the live one). |
| G-4 | No pin in 02 for "turn_asked carries across rounds of the same turn" (round 1 asks, round 2 flat-transitions → finalize) | Master plan adds pin 5 to test_iter70_transition_beat.py. |
| G-5 | 02 does not restate that the T2/T3 worktree commits happen on the BRANCH (never main) and PENDING_TASKS updates on MAIN | Master plan execution rules section (LAW 0). |

## 5. Redundancies found

| # | Redundancy | Disposition |
|---|---|---|
| R-1 | 22e6f88's `elif not any(transition ok): return "finalize"` branch is unreachable in practice (covered by the first branch's `or not any(...)`) | Keep verbatim anyway (reference parity; dead branch is harmless and self-documenting). |
| R-2 | T5's fast_flush log site can never fire on the lane (`TTS_GATE_FAST_FIRST_FLUSH=false`) | Keep (forensics tool must mirror code truth; costs 2 lines). |

## 6. Open items carried into PREFLIGHT (must verify against live code before master plan)

1. Re-verify every anchor line number in 02 against the worktree (files unchanged since audit — expected pass).
2. Compile-check the T4' stream-end insertion shape against the actual block structure (C-4).
3. Verify `re` import availability for `_WORD_RE` (builder.py imports re — L38) and that no name `_similar_dup`/`_log_filter`/`_WORD_RE`/`_SIMILAR_FILLERS`/`_similar_tokens` already exists in builder.py (collision check).
4. Verify `speech_replay.py` import list extension compiles (names exist post-T4').
5. Verify test helper `run_turns`-style pin harness compiles against `tests/fake_llm.py` (FakeLLM, tool_call) and `tests/mock_webhooks.py` (mock_client) — both exist (audit §0).
6. Confirm the 4 legacy test token lines match 02's replacements exactly.
7. Confirm llm.json JSON edit surface (state_prompt strings) — mirror lines contain no double quotes/backslashes that break JSON escaping (they contain " — " em-dashes and `?` — safe; verify with a json.load after edit spec).
8. Confirm `pytest` subset command set for each task commit.

Cross-reference verdict: **one GAP (G-1) and four master-plan resolutions (C-3, C-4, G-2..G-4) carried forward; no unresolved contradictions.** The action plan is fully supported by the audit; the audit is fully addressed except G-1 (resolved in the master plan).
