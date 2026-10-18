# SESSION 2026-10-06 — iter93/94/95 merged + live-validated: WORKING BUT NOT GREAT

> Read AGENTS.md FIRST (repo law). This file is the pinned session state for the NEXT session.
> Chain: plans/plan_v5_iter94_95_validation_close.md (parent of this save) → parent plan
> plans/plan_v5_iter94_ladder_silence_savage_warm.md.

## 1. Outcome (what is DONE and on main)

- **Merged into main (owner say-so in-chat 2026-10-06), tags created, zero conflicts:**
  - `engine/iter93` @ 2f7644f ← e57d2b2 (held-adopt race + observability pins)
  - `engine/iter94` @ 5681513 ← 3ac544a (silence ladder stretch guard)
  - `engine/iter95` @ eb54217 ← 63e013c (warm cancel-not-wait, `prewarm_abort_cap_ms=400` CEILING)
  - GIT_TREE.md regenerated; engine/ITERATIONS.md line appended; PT-84 → DONE.
- **Suite state:** 496 passed / 3 skipped / 0 failed (measured by the parallel iter95/sdk session @ 90.75s).
- **Live validation evidence (all on test/iter93-94-95 content == merged main content):**
  - Scripted Maria happy-path BOOKED for real (validator uid `r3F7uGWKd4M7baLatzPczi`, 08:39:42) — **cancelled + verified after test**.
  - Owner's REAL Twilio call (+1 888 595 8927 → voicetest.diallux-ai.site, OREGON): trace
    `152d98c0c8d73f27680d950f2914e1bb` (Langfuse FI server, project pk-lf-bba5…):
    TTFT p50 962 / p90 1224 · e2e_turn p50 1882 / p90 4031 · iter95 `outcome=aborted` ×12
    waited_ms=0 · ladder idle · 0 held_swallow · 0 degraded RAG · 0 errors · full flow to
    contact_details (turn_cap end, no booking → nothing to cancel).
  - Lane logs preserved: OREGON /tmp/opencode/lane-8049.log + lane-8050.log.

## 2. THE GOAL for the next session (owner, hard requirement)

**e2e_turn p50 ≤ 1,200 ms on REAL telephony.** Owner's words: people will die. As of today it is
1,882 ms. Everything below is in service of that number.

## 3. Latency ideas (the decomposition that justifies each lever)

e2e_turn p50 ≈ 1,882 breaks into four stacked tolls (owner's live call):

| Segment | p50 | Lever | Expected saving |
|---|---|---|---|
| STT EOT → LLM first | ~1,326 | **OWNER-SET Deepgram EOT knobs** (`DEEPGRAM_EOT_THRESHOLD`, `DEEPGRAM_EOT_TIMEOUT_MS` — still deferred by the owner; biggest single lever) | 200–400 ms |
| LLM TTFT | ~962 | prompt-layer branch: strip RAG context from hot-path states; mini-model for mechanical states (contact_details 8 gens @ ~1.2k dur needs no gpt-5.4); smaller state blocks = faster prefill | 100–250 ms |
| LLM → TTS first byte | ~250–300 | sentence-gate: flush first CLAUSE not first sentence | 100–150 ms |
| TTS/streaming tail + marks | ~250 | mostly floor; tighten mark-timeout only | small |

Realistic landing with levers 1+2: **~1,150–1,300**. Below 1,200 needs the prompt-layer lever done aggressively.

**Fastest experiment first (zero code):** boot phone lane with candidate EOT values as BOOT-ENV
overrides (never edit .env), owner makes one call, re-pull trace, A/B against today's numbers.

## 4. Owner decision for the workflow (ratified 2026-10-06)

**Develop/test on Finland; push-pull via git to OREGON.** Finland = the working/authoring box
(repo at /home/julio/projects/clean_diallux_SDR), OREGON (5.78.83.174, ssh-wrapped,
id_ed25519_hetznor) = the lane/battery/validation box. Rules that still apply:
- NO rsync/scp of repo content — only git push/pull (LAW).
- OREGON lanes only via scripts/new_lane.sh; NEVER touch OREGON main checkout / ports
  8001-8003/8026/8090/8080; merges on wt-main-docs only.
- Next session should VERIFY Finland can run the unit suite locally (venv exists? engine/.venv
  on FI?) and wire the push-pull loop (FI branch → OREGON fetch → lane).

## 5. Findings carried (do NOT rediscover)

| ID | Severity | Finding |
|---|---|---|
| F-92b-5 | HIGH | Raw tool-protocol text leaks into SPOKEN content (`to=functions.…` chunks without braces — iter65 sanitizer gap). Persisted in state block → re-billed every round. |
| NEW (2026-10-06) | LOW | llm_mic_caller.py crashes with unhandled ConnectionClosedOK when the agent ends the call server-side (post-booking goodbye) → journal never written. Catch server close = normal end-of-call. |
| DEFERRED | — | Deepgram EOT knob values = OWNER-set, after he hears a call (this session: he heard one — next session he decides values). |
| PARKED | — | iter77-twilio-iter70 @ 8c5f72f parked merge (12 commits ahead of main, has the /twiml signature gate) — owner decision pending. NOTE: merged main /twiml has NO signature gate — that is why the voicetest webhook window must stay short. |
| Pending | — | T5 TTFT benchmark of the chain (05_ttft_benchmark.md + ledger run) never ran — fold into the 1200ms mission. |

## 6. Infrastructure left standing (state when session closed)

- OREGON: lane 8049 (mic/test, wt-9494 @ 9eb341c) + lane 8050 (phone, same checkout,
  boot-env `AUDIO_TRANSPORT=twilio PUBLIC_BASE_URL=wss://voicetest.diallux-ai.site`), both UP.
- OREGON /etc/caddy/Caddyfile: `voicetest.diallux-ai.site` block added (backup
  Caddyfile.bak.voicetest.*) — /mic* → 8049, /twiml+/media → 8050, /health → 8049, rest 404.
- Twilio number +1 888 595 8927: webhook was REPOINTED to voicetest.diallux-ai.site/twiml for the
  live test — **REVERTED to https://twilio.diallux-ai.site/twiml (FI prod lane) at session close**
  (verify: `sudo journalctl` creds in /opt/diallux-production/.env; repoint = one
  IncomingPhoneNumbers PUT, provision script --repoint also works).
- Worktrees: wt-94, wt-95, wt-9494 (cleanup deletions = owner trigger word only).

## 7. Next-session entry

1. Read AGENTS.md + this file + plans/plan_v5_iter94_95_validation_close.md (T5 benchmark pending).
2. Decide with owner: EOT knob values (his call) + prompt-layer branch scope.
3. Set up the Finland-first workflow (§4) before writing any code.
4. The mission name for the 1200ms work: it is prompt-layer CODE → full LAW 0 ceremony,
   new iter number (`engine/iter96-*` or as the numbering law dictates at that time).
