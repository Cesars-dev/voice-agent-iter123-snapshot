# iter96b — TTFT floor forensics: explain why killing the 1,746-char uncached delta only moved TTFT −20…−78 ms

## Meta
- Date: 2026-10-07
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ANALYSIS ONLY (zero engine-code changes). Import everything the iter96 session measured/mattered, decompose per-round TTFT into its real components on the existing artifacts, and either (a) locate the lever that gets phone-path TTFT p50 962 → ≤750 as promised, or (b) rewrite the promise with evidence. Ends with the real-Twilio verdict run on the parked OREGON lane.
- Status: PLAN ONLY (not started — awaits owner go)

## Compaction Context (everything that matters, imported)

### Where the work already is
- Repo: `/home/julio/projects/clean_diallux_SDR` (FINLAND box). Branch **`engine/iter96-delta-cache-layout` @ `b81b382`** — pushed to GitHub, **NOT merged to main**. Branch parent: main @ `8078ad0`. Plan doc committed to main: `d09aa10` (`plans/plan_v5_iter96_delta_cache_layout.md`).
- What iter96 shipped (already verified by suite + A/B): the per-round trailing delta previously re-shipped a byte-identical-per-state block (~1,746 chars Intake / 3,422–4,500 chars Closer, `builder.py` `delta_tokens` = CHARS) as fresh uncached bytes every round. iter96 promotes the static-per-state frame into the cacheable prefix (`[tools][head][stage][history][delta]`, switch `STATE_DELTA_STAGE_STATIC` / code default `delta_stage_static=True`, gated by `state_in_delta=True`); trailing keeps only changed dvs lines + fresh RAG arrivals + directive. One real bug fixed in-branch (turn-1 lite round minted an empty poisoned stage frame — excluded via `not lite` gate).
- New telemetry keys: `delta_static_chars`, `delta_trailing_chars` (beside unchanged `delta_tokens` = chars). Registry: `/home/julio/projects/clean_diallux_SDR/docs/Testing_guidelines/ENV-SWITCHES.md`.
- Suite: `cd /home/julio/projects/clean_diallux_SDR/engine && .venv/bin/python -m pytest tests -q` → **516 passed / 1 skipped / 5 failed** — all 5 fail identically on pristine main tip (iter95 abort-cap clamp vs old await pins + 1 validator case). Zero new reds from iter96. Fast runner: `scripts/fast_suite.sh --full` (~90 s for the 496-pin era suite).
- Existing report (read, do not duplicate): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-delta-cache-layout/96_report.md`.

### The measured numbers (A/B, all logged in round-usage journal lines "turn=N state=X … ttft=Yms delta=Z")
- OREGON same-box A/B (mic-ws driver, Danny persona, full arc Intake→Discovery→Closer→Offer→contact_details):
  - baseline `8078ad0` lane :8064 → journal `/tmp/opencode/iter96_base_or_danny.json` (ON OREGON): **n=23, TTFT p50=918 / p90=1097 / max=1217**, delta_chars p50 1,746 every round (Intake), 4,000+ on late states.
  - iter96 `b81b382` lane :8063 → `/tmp/opencode/iter96_or_danny1.json` (ON OREGON): **n=22, TTFT p50=898 / p90=1166 / max=1523**, trailing collapsed to 0–231 steady / 109 ack frames; RAG-fluctuation rounds still re-ship 3–3.5k (correctness-preserving).
  - Earlier session report cited p50 879 from a different post-change file; **recomputed 898** — reconcile in T1.
- FINLAND lane :8020 scripted llm_mic happy path (artifacts in `/tmp/opencode/` HERE): `iter96_baseline_happy.json` + `iter96_baseline_server_log.snapshot` (14 rounds, TTFT p50 1059) vs `iter96_postchange3_happy.json` (20 rounds, TTFT p50 981, Intake static 1748/trailing 0, Discovery static 2014/trailing fluctuating 2.4–3.7k).
- Cache behavior on the wire (proven): iter96 rounds cached PAST the promoted frame when OpenAI cooperates (`cache_read` 4736/5760/6784 tokens across successive states); far too many rounds still stuck at `cache_read=2688` (tools+head only) — **OpenAI stochastic cache misses** (1,024-block cache); baseline bounced 2688↔3712 the same way.
- Reference trace (real Twilio, NOT from the iter96 session — older voicetest 06:21/09:21 UTC 2026-10-06, session_id `diallux-call-7a17bcd1`, call_sid `CA93823104f61c20d6ff12300f46b2ef7f`, stream_sid `MZ535215e12bb6c7c19cdd1489681c6175`, transport=twilio, stt=flux, eager_eot=True, tts eleven_turbo_v2_5): `/home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5` Langfuse FI, trace `152d98c0c8d73f27680d950f2914e1bb`, 37 gens, per-gen span p50 1810 / p90 3797 ms (span = prompt+full streaming, NOT TTFT; tracer does NOT emit completionStartTime per gen — TTFT must come from engine round-usage logs, not Langfuse).
- Owner's goal (unchanged): **e2e_turn p50 ≤ 1,200 ms on real telephony**; iter96 plan promised TTFT p50 962 → ~750 on phone (= −200…300 ms claim).
- **THE YARDSTICK — chat-path TTFT p50 floor (what we measure against):** iter78-era `llm2llm` chat runs on the SAME engine+model (gpt-5.4, Finland) measured in the prior session from Langfuse FI: **27 runs, Sep-24..Oct-2, median-of-trace-p50 TTFT ≈ 714–753 ms** (range shown ~690–740). Phone path = chat + ~250 ms; the delta was convicted for exactly that gap. Reference "good" chat trace (delta p50 1,261 chars): `e3bea8da71d7366d38bd81dcdaa12` — **treat id as UNCERTAIN, re-resolve via `lf.py traces` before quoting** (verbatim source: the compaction context of `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter96_delta_cache_layout.md`, commit `d09aa10`). Fresh re-derivation today FAILED via a quick `lf.py` page-scan (no `llm2llm*` traces with `timeToFirstToken` found from 2026-09-24 48h-pages → ingest/index/paging quirk to be resolved in T0, exactly per lf.py skill gotchas). The per-run artifacts also exist as json files at `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/json_logs/*.json` (434 files, key `p50_ms` = per-turn e2e ms — NOT ttft; those show graph happy-path turn p50 ~1,368–2,076 in the Sep-24 files — second yardstick for e2e).
- Iter95-era measured phone baseline: TTFT p50 962 / p90 1,252; e2e_turn p50 1,882; chat-path TTFT p50 ~714–753 (27 llm2llm runs Sep-24..Oct-2) — delta convicted as lever.

### The open puzzle (WHY THIS PLAN EXISTS)
Trailing-delta kill worked exactly as designed (1,746→0 chars) but measured TTFT gain was only **−20 ms (OR) / −78 ms (FI mic)** — nowhere near −200…300. Candidate causes, all testable on existing data:
1. **METHOD ERROR, PARTIALLY CONFIRMED**: several "TTFT numbers" quoted in chat were full LLM span (prompt+stream, up to 323 out tok, p50 1810 in trace `152d98c0`) — not TTFT. Engine `ttft=` metric in round-usage lines is the real one; definition/fraction breakdown must be pinned from engine source (`ttft=` printed by the round-usage logger).
2. **Cache-miss dilution**: if only ~a fraction of rounds actually cache the new frame (2688-stuck rounds ≈ 50%+), expected TTFT saving = hit_rate × (~437 tok × ~0.10 ms/tok prefill) ≈ tens of ms, not 300.
3. **TTFT floor is dominated by non-prefill sources**: gpt-5.4 is a REASONING model (engine log: "temperature=0.30 ignored for reasoning model gpt-5.4"; `reasoning_effort` passed via model_kwargs) — hidden thinking time before the first visible token may be the dominant fixed cost (~600–800 ms), immunizing TTFT against prefill cuts.
4. Prefill tok→ms conversion assumption (~0.1 ms/tok) may be wrong for this model/endpoint.

### Resolved decisions (carried from iter96, DO NOT revisit)
- One-variable law; branch ceremony; GitHub push/pull as the only OREGON transport (never rsync); `delta_tokens` meaning unchanged; model stays gpt-5.4; voices = Sarah for batteries; `delta_stage_static=True` is live code default on the branch; nothing merges without owner say-so.

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner say-so to merge `engine/iter96-delta-cache-layout` → main | owner (LAW 0) |
| Real Twilio voicetest fired at parked OREGON lane :8063 (`AUDIO_TRANSPORT=twilio`, number +1 888 595 8927 → Caddy voicetest route) | owner fires the call; we pull the trace + round log |
| iter95b restatement of the 5 pre-existing red pins | owner authorization (separate, zero-code) |

## Environment & Dependencies
- FINLAND = this box; repo `/home/julio/projects/clean_diallux_SDR`; engine venv `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`.
- OREGON: `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` — journals under `/tmp/opencode/` there (`iter96_base_or_danny.json`, `iter96_or_danny1.json`, `iter96_or_happy1.json`, lane logs).
- Langfuse FI: helper `python3 scripts/lf.py` run from `/home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5` (keys in its `.env`; `lf.py traces/show/gens/usage`; ingest pipeline health check `lf.py health` — currently reports "NO RECENT TRACES" over 24 h: verify before treating new-trace absence as absence of calls).
- Engine round-usage log line format: `round usage: turn=N state=S input=I cache_read=C output=O ttft=Tms state_in_delta=True delta_tokens=D` (ttft in ms; delta_tokens = chars of trailing delta; on the branch also printed via new telemetry keys).
- Ports never to touch: 8001–8003 (live ORIGINAL), OREGON fixed ports; lanes are foreground uvicorn with pid files in OREGON `/tmp/opencode/` (`voice_8063.pid`, `voice_server_8064.log`).

## Architecture (what TTFT decomposes into — the diagram to fill with numbers)
```
last_caller_byte → [STT flux finalize] → [EOT eager-hold release] → [graph dispatch] → [LLM prefill (cache_read C / uncached U tok)] → [hidden reasoning (gpt-5.4)] → FIRST TOKEN (this = ttft) → streaming out (0–323 tok) → TTS first byte (separate metric)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                 everything left of the arrow is what iter96 could and could not move; fill p50 per component
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-delta-cache-layout/96b_ttft_forensics.md` | NEW forensic doc: TTFT decomposition tables, cache hit-rate stats, verdict on each hypothesis, corrected A/B math | NEW |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter96-delta-cache-layout/96_report.md` | APPEND: corrected numbers + pointer to 96b forensics (never rewrite prior text) | EDIT (append-only) |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_iter96b_ttft_floor_forensics_2026-10-07.md` | this plan (docs → straight main per repo law) | NEW |
| engine code | NOTHING — zero code changes | — |

## Deploy Rules
- Nothing deploys. OREGON/PROD working tree stays untouched; read-only. If the Twilio verdict needs the lane restarted, lane bootstrap already documented (`/tmp/opencode/lane-8049.log` pattern, `scripts/new_lane.sh iterNN base-sha slug`) — REUSE, don't reinvent; notify owner before touching :8063 state.

## Tasks (in order)
### T0 — Re-anchor the chat TTFT yardstick (must run first — everything is measured against it)
Goal: re-derive the chat-path TTFT p50 floor freshly, because the −300ms promise was "phone 962 → chat ~750". Method (from the same session chain that produced 714–753): list Langfuse FI traces with `sessionId` starting `llm2llm` (LF UI/SQL-level filter, NOT the up-link query param), Sep-24..Oct-2 window, per trace read GENERATION `timeToFirstToken`, per-trace p50, then median-of-p50 across runs. If quick `lf.py` pages keep returning none (today's scan failed that way), fall back to raw SQL on the self-hosted Postgres/ClickHouse or the LF UI export; verify with one known-good trace id first.
Files: no repo files touched; output table goes straight into `96b_ttft_forensics.md`.
Commands: `cd /home/julio/projects/Retell_AI_MCP_connection/Dialux_SDR/diallux-langgraph-production-v5 && python3 scripts/lf.py traces --hours 336 --limit 100` (and `lf.py show <id>`); escalation path: docker exec into the Langfuse compose stack (host `http://localhost:3001`) for a direct DB query.
Verification: forensics doc opens with the yardstick: chat TTFT p50 median-of-p50 = X (n runs), trace ids listed; if X turns out NOT ~714–753, this rewrites the whole iter96 acceptance bar.
### T1 — Reconcile the numbers (single source of truth)
Goal: one table, one definition. Pin the exact engine-side definition of `ttft=` (grep the round-usage logger in `/home/julio/projects/clean_diallux_SDR/engine/diallux/…`), then recompute p50/p90 from ALL THREE artifacts (`/tmp/opencode/iter96_base_or_danny.json`, `/tmp/opencode/iter96_or_danny1.json` on OREGON via ssh; `/tmp/opencode/iter96_baseline_server_log.snapshot` local). Reconcile 879 vs 898; state which file produced each.
Commands: the ssh command above; `grep -rn "round usage" /home/julio/projects/clean_diallux_SDR/engine/diallux/ | head`.
Verification: table in the forensics doc with file → n → p50 → p90 → delta_chars p50 per run; contradictions explained.

### T2 — Hypothesis 2: quantify cache hit-rate vs TTFT
Goal: from the journals, per round split by `cache_read` level (1664=tools+head-only cold, 2688/3712/4736/5760/6784=deeper caches) and correlate `ttft` vs `cache_read` AND vs `delta_tokens` within same cache level. Compute: median TTFT at cache 2688 across baseline vs iter96 (same cache level ⇒ same prefill ⇒ isolates reasoning/other floors). Output: expected-vs-observed saving math.
Verification: table "cache level × state → median ttft (baseline) vs median ttft (iter96)" proves/refutes the dilution factor; hit-rate % stated.

### T3 — Hypothesis 3: reasoning floor
Goal: prove/refute that gpt-5.4 hidden reasoning dominates TTFT. Read `reasoning_effort`/model_kwargs in `/home/julio/projects/clean_diallux_SDR/engine/diallux/` (session warning in journal shows both knobs injected). Compare Intake round-1 (cold) ttft across runs; check whether ttft variance correlates with output reasoning indicia; optionally cite the chat-path llm2llm numbers (p50 ~714–753 with tiny payloads) already in the iter96 plan as the chat floor.
Verification: forensics doc states EITHER "reasoning floor > X ms ⇒ prefill cuts can never reach −300" with the evidence, OR convicts prefill with the measured tok→ms slope from T2.

### T4 — Hypothesis 4: tok→ms slope calibration brief note + memo
Goal: derive the actual prefill ms/1k tok for gpt-5.4 from pairs of rounds differing only in input size at equal cache level (baseline data has plenty: 1,662→10,714 in_tok). Fold into T2/T3 verdicts.
Verification: slope stated with data provenance.

### T5 — OREGON phone-path verdict (the real prize, AFTER owner fires the call)
Goal: real Twilio voicetest into the parked `b81b382` lane :8063; pull round-log TTFT + delta + Langfuse trace; same forensics vs baseline trace `152d98c0c8d73f27680d950f2914e1bb` (target per plan: phone delta_chars p50 ≤ ~1500, TTFT p50 ≤ ~800). First run `lf.py health` and confirm the trace ingested (or read `voice_server_8063.log`-equivalent round lines on OREGON).
Verification: verdict section in 96b doc: PASS/FAIL vs target with numbers; report 96_report.md appended.

### T6 — Write up + LAW 0 closeout
Goal: 96b_ttft_forensics.md final (decomposition table: STT/EOT vs dispatch vs prefill vs reasoning; where is the next −200 ms REALLY); append to 96_report.md; commit docs to main; ASK JULIO with the 3 carried asks.
Verification: PLAN FILE line below; git log shows the docs commit on main.

## Validation Plan (end-to-end)
- forensics doc exists with T1–T4 tables all populated from real artifacts (no quoted-from-memory numbers);
- each hypothesis gets verdict: CONFIRMED / REFUTED / PARTIAL, with the exact figure;
- if owner fires the Twilio call: phone verdict numbers included;
- suite state unchanged (516/1/5) — nothing code-side to re-run.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Merging iter96 to main | owner say-so (LAW 0), separate ask |
| iter95b 5-pin restatement | separate zero-code batch |
| ElevenLabs V4-turbo TTFB lane test | owner optional add-on, not this analysis |
| Mini-model (point 2) switch | owner later decision |
| EOT knob values | owner call |
