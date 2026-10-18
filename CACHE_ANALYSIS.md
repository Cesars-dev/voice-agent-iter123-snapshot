# iter92-CACHE-GROWTH AUTOPSY — verdict memo (2026-10-04)

## Question
Owner saw iter91 GK cache_read flat at two floors (2688/3712) while input grows and concluded
iter89's prompt changes broke prefix-cache growth (we went back to this). Reference belief:
iter87 (MVP-finally era @02eb2ac) had growing cache. Verify + isolate + find the breaker.

## Verdict
NO REGRESSION. The flat-floor shape with rare +1024 steps has been the behavior of the
engine AND of production Retell on the SAME model class since the ledger began (2026-09-18).
iter87's long heavy calls made it LOOK like growth; iter90/91's short light calls made it
LOOK like a new bug. Same mechanism, different call depth.

## Evidence chain
1. LEDGER (all runs, all drivers, pre- and post-iter87): the floors alphabet
   {1664, 2688, 3712, 4736, 5760, 6784, 7808, 8832} appears in EVERY run since iter56;
   growth events per call: 5-11 (positive), 8-74 flat, regardless of commit/model/config.
   - battery-iter56 (the 'cache climbs' T0 proof): +8 per call over 27-37 turns.
   - happy-iter78-or 93-turn call: +10 grow events over 93 turns. 10.
   - iter87 r13 (43 turns incl tool-heavy ConfirmSlots): +10; repaid climbs 308->2713.
   - iter90-mic-b0/b250 (30405ad) + iter91 (2b3e900): identical shape, shorter calls.
2. THE GRID: every observed cache_read in every run = 640 + 1024k exactly
   (1664, 2688, 3712, ..., 10643-side on Retell). Provider block quantization, not a cap.
3. CODE: builder.py and config.py are BYTE-IDENTICAL 02eb2ac..30405ad (iter89 changed only
   prompts/*.md + llm.json copy). iter91's 11 default flips touch no cache flags
   (state_in_delta=True, history_window=0 full append-only, tail_before_history inert).
4. REAL RUNTIME LOG (iter91 lane 8050): delta_tokens frozen at 1746 for 5 consecutive
   Intake rounds while history grew -> the non-delta bytes are stable, as designed.
5. SYNTHETIC (real builder, prod flags): consecutive-round message lists are append-only;
   LCP grows every round; only the post-history delta is replaced (by design, iter56).
6. PROVIDER CONTROL (RateIl production, deprecated key, 95-request call, 600 s):
   prompt 2648->10643 grows identically; LLM p50 911 ms; 11/60 rounds at 1.9-4.2 s,
   42/60 flat 700-1150 ms ACROSS THAT RANGE -> same quantized-cache regime, spikes when
   a miss lands (their per-turn substituted dv system prompt makes their miss slice bigger).
   Raw payload: research/surgeon/iter92-cache-growth/retell_call_b790bb6f_raw.json.

## The real cost (NOT a regression; the fix candidate)
- per-turn re-bill = post-history DELTA (replaced every round; state block grows with
  verbatim dv appends: 1746 -> 2763 -> 4326 in iter91) + user turn + sub-1024-block
  remainder. In iter87 that reached ~2700 tok/turn by ConfirmSlots.
- knob-effect on iter91 vs gk-iter89 in the ledger: same shape -> iter91 knobs not the cause.
- the ~+300 tok/turn Intake re-bill bump in iter89 vs 02eb2ac is REAL (1->3 refer tags) but small; not the disease.

## Fix candidates (iter92, code change ONLY, owner decides)
1. FREEZE the state block at state entry (append-only within state; re-freeze at
   transition) -> prefix becomes [tools][head][state-block][history] byte-stable,
   delta shrinks to per-round diff only. NOT the state_in_delta=False revert (older, worse).
2. SLIM the state block (drop verbatim caller words; pointer to live dvs) -> smaller
   replaced slice.
3. Do nothing (accept 2688-8832 floors + delta re-bill): Retell did the same on prod
   with the same model and it shipped.

## Key learnings to carry forward
- cache_read on this stack is BLOCK-QUANTIZED; never again read 'flat cache' as a bug
  without crossing a block boundary.
- call DEPTH is the confounder in every cache read: 12-turn GKs can never show the
  staircase; use 40+ turn calls or heavy tool rounds for cache battery tests.
- MCP client MUST read the file first (twice failed to); do not copy w-iter envs between
  lanes; keyhound BEFORE every push.

## iter92b quant check (2026-10-05)
FOUR GK stress-persona mic calls (Sam/Priya/Dave/Bianca) @ 2b3e900, lane wt-92 :8062 —
measured confirmation of the verdict above. 100 rounds: grid-fit 100% (only 2 off-grid
rows = turn-1 cold class), floors {2688,3712,4736,5760}, growth events 2-6/call (incl
+2048 crossings), hold alive (18-24 releases, 0 cancels). ttft p50 858 / steady 853 ==
iter87 reference. e2e_resp p50: Priya 1373 (gate-exact), Sam 1394, Dave 1421, Bianca
1777 — misses are STT/EOT-lag driven (Bianca Deepgram EOT spikes 4.3-6.5s on pause-heavy
persona), NOT cache. Findings: F-92b-1 WS handshake race vs teardown (prod concurrency
risk), F-92b-2 e2e gate marginal miss, F-92b-3 repaid model undercounts (uncached
history suffix + /3.3 tokenization), F-92b-4 new_lane.sh uncommitted, F-92b-5 (HIGH)
raw tool-call protocol text leaked into assistant turns on 2/4 calls (Dave A8, Bianca
A31, CJK mojibake; iter65 sanitizer covers brace sentences only; audio verify needed).
Evidence: research/surgeon/iter92b-4gk-quant/ (01 raw tables, 02 quant verdict, 03 SOP
report; ledger run iter92b-4gk-quant = 84 sops rows + 100 rounds + 153 rag spans).
SALES bands: Sam 10/14 solid, Priya 4/14 retrain (probe-loop stress caught), Dave 10/14
solid, Bianca 13/14 hire. NO code changes this session; iter93 decision = owner.
