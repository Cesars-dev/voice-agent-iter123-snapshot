# PLAN — iter75 T2: validate keepalive fix on a non-Maria happy path (hil-1 mic lane)

## Meta
- Date: 2026-09-24
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: Prove the iter75 `keepalive_expiry=600` fix delivers first-answer latency at steady-state cost on a happy-path persona OTHER than Maria, on the hil-1 (Oregon) mic lane, using the llm2llm harness + OTEL/Langfuse evidence.
- Status: PLAN ONLY (not started — branch already cut, owner GO received to run the test)

## Compaction Context
(verbatim condensed session state)

**Migration state.** The full stack was cloned 2026-09-24 to NEW Hetzner box hil-1
(`5.78.83.174`, cpx21 3vCPU/4GB/75GB, Ubuntu 26.04, dc `hil-1` Hillsboro OR) per
`/home/julio/projects/clean_diallux_SDR/plans/plan_iter69_server-migration_2026-09-23.md`
(T2-T8 executed out of order by owner request: full rsync clone incl. .git @
`9ccdccf` (engine/iter73-playback-rate), all 140 refs restored, pgvector restored
210/233, endpoints :8001-8003 live via systemd, engine :8026 via `diallux.service`,
mic lane :8090 via `diallux-mic.service` (0.0.0.0, token-gated `VOICE_TEST_TOKEN`).
Nothing points at hil-1 publicly yet — DNS `twilio-usa.diallux-ai.site` NOT cut over;
browser mic works via SSH tunnel localhost:8090 or direct IP (mic perms need HTTPS →
tunnel is the working path). Langfuse stays on the OLD box (`46.62.233.228:3001`);
hil-1 envs point at it (`LANGFUSE_HOST` fixed in `/opt/diallux-production/.env` line
19 + engine `.env` + root `.env`). TTS on hil-1 = **ElevenLabs prod pin** (iter66
`e91af1a`): Sarah `uG1JFy6xppqckhHCs2KG`, turbo_v2_5, speed 1.06, stability 0.5,
boost 0.75, style 1.0, `ELEVENLABS_INACTIVITY_TIMEOUT=180` — owner-ordered EL
("place EL as the voice provider"). `DEEPGRAM_EAGER_EOT=true @ 0.7` (owner pick,
was 0.6). `CALL_PREWARM=true` was tried and REVERTED (adopted pooled flux sockets
never fired transcripts — dead-socket bug; known-good = false).

**iter75 (owner-approved, cut from `9ccdccf`):** branch `engine/iter75-llm-keepalive`
@ `858543c` — ONE change in `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py`:
`shared_llm_http_client()` gains `limits=httpx.Limits(keepalive_expiry=600.0)`
(httpx 0.28 removed the AsyncClient kwarg; the 5s default let the greeting-time
lite/full prewarm connection die before turn-1 → turn-1 TTFT 1,120 vs steady
664-935). Suite: 3 pre-existing fails (iter46/59/60 — same on main), 459+ passed,
0 new. Deployed to hil-1 by scp of `llm.py` + restart at 14:11:20 UTC; both lanes
active. NOT merged to main (LAW 0 — merge = owner say-so).

**Evidence baseline (hil-1 mic session 13:36, PRE-fix):** turn-1 e2e 1,358ms
(TTFT 1,120, cache 1664 lite floor); steady turns 4-7 e2e 1,050-1,100 (TTFT
754-935); prewarms fire at call open and complete 8s before turn-1
(`warm done lite:Intake 2,669ms` @ 13:36:08). Finland baseline (same path, this
morning, 21 turns): e2e p50 ~1,550, 8/21 turns > 2s jitter; TTFT p50 ~854.

**Verified tooling on hil-1:** harness `.venv/bin/python tests/llm2llm/harness.py
--personas <X> --rag [--langfuse] --slots mock|live` (mock = no real bookings;
live = REAL Cal.com event 3801235 — cancel after); ledger import
`python3 scripts/live_sql.py import --window "HH:MM-HH:MM" --run <name> --commit <sha>`
(needs root `/home/julio/projects/clean_diallux_SDR/.env` `LANGFUSE_HOST` →
`http://46.62.233.228:3001` — FIXED on hil-1 13:41); percentiles
`python3 scripts/latency_pull.py --run <name>`; trace gens via
`/api/public/traces` (Langfuse REST, keys from engine `.env`).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Test persona = **Susan** (happy-path, expect book) | Owner: "happy path, not Maria, another" — Maria already has 5 runs today (2 old-box PASS + 3 hil-1) |
| Run on hil-1, mic lane NOT required — harness `--slots mock` | Validates keepalive turn-1 claim without touching real Cal.com; latency claim is LLM-plane |
| `--langfuse` ON | Need OTEL traces for per-turn TTFT evidence; run names trace as `llm2llm-graph-<slug>` |
| `--max-turns 48`, `--rag` | Standard happy-path battery shape (SOP) |
| One run, then import as `hil1-susan-lf` | One variable (keepalive), one comparison run |
| Old-box reference = existing `oldbox-maria-lf` ledger run + new `oldbox-susan-lf` if wanted | Same-commit same-shape comparison; Maria already imported |
| iter75 stays branch-only until owner merges | LAW 0 |
| hil-1 tree stays at `9ccdccf` + deployed `llm.py` | Working tree is the operational clone; branch on old box carries the change |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| None | — |

## Environment & Dependencies
- hil-1: `ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174` (Mac: `ssh -i ~/.ssh/id_rsa root@5.78.83.174`)
- Engine venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv` (py3.12.14, deps pinned == old box freeze)
- Env source: `cd /home/julio/projects/clean_diallux_SDR/engine && set -a; . ./.env; set +a` (as user `julio` on hil-1 via `sudo -u julio bash -c`)
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db` (copied to hil-1, import writes there)
- Langfuse: old box `:3001`, keys `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` in engine `.env`
- TTS on hil-1: EL Sarah (iter66 pin) — irrelevant to harness (text-native)
- Harness callers: `--slots mock` (default) — NO real booking; no cancellation needed
- NOT touched: old box services, live agent IDs, `/opt/diallux-production` on old box

## Architecture
```
hil-1 harness (graph transport, gpt-5.4 agent, gpt-4o caller, mock webhooks)
  → shared httpx pool (keepalive_expiry=600 — THE FIX)
  → OpenAI gpt-5.4  · Langfuse trace `llm2llm-graph-book Susan` → old box :3001
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter75_llm_keepalive.md` | this plan | NEW (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter75-llm-keepalive/` | run receipts + turn tables | NEW (gitignored) |
| No code changes | iter75 already cut+deployed (`858543c`) | — |

## Deploy Rules
- Old box: untouched (this plan runs harness on hil-1 and reads journals locally on old box only if old-box comparison needed).
- hil-1: only harness runs + ledger import; NO service restarts; NO env edits.
- Mock bookings only; `--slots live` is FORBIDDEN in this plan (no cancel burden).
- Never print secret values; `.env` sourcing via `set -a/.env/set +a` only.

## Tasks (in order)

### T1 — Susan happy path on hil-1 (traced)
Goal: one happy-path run, non-Maria persona, with Langfuse tracing, to measure turn-1 TTFT/e2e under iter75 keepalive.
Files: run logs under `/tmp/maria…` style path `/tmp/susan-lf.log`; json log auto-written to `/home/julio/projects/clean_diallux_SDR/engine/tests/llm2llm/json_logs/`.
Commands (full, on hil-1):
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 \
  'cd /home/julio/projects/clean_diallux_SDR/engine && sudo -u julio bash -c "cd /home/julio/projects/clean_diallux_SDR/engine; set -a; . ./.env; set +a; nohup .venv/bin/python tests/llm2llm/harness.py --personas Susan --rag --langfuse --max-turns 48 --slots mock > /tmp/susan-lf.log 2>&1 & echo started"'
```
Dependencies: none (services already running iter75).
Verification: after ≤5 min, `/tmp/susan-lf.log` tail shows `[PASS] (BOOK) Susan — … book` and `ALL PASS`; a Langfuse trace named `llm2llm-graph-book Susan`-slug exists (timestamp ≈ now).

### T2 — Import + per-turn table
Goal: ledger row + full per-turn metric table (TTFT/cache/tokens + STT→LLM/TTS/e2e per turn).
Commands (full, on hil-1):
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 \
  'cd /home/julio/projects/clean_diallux_SDR && sudo -u julio python3 scripts/live_sql.py import --window "<HH:MM>-<HH:MM>" --run hil1-susan-lf --commit 858543c --branch engine/iter75-llm-keepalive'
```
(Use the actual UTC window of the run; widen if the trace missed the window — check with the traces API first.)
Verification: import prints `imported run=hil1-susan-lf … calls=1`.

### T3 — Latency pull + turn-1 verdict
Goal: percentiles + per-turn TTFT from the ledger; compare turn-1 vs steady.
Commands (full, on hil-1):
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 \
  'cd /home/julio/projects/clean_diallux_SDR && sudo -u julio python3 scripts/latency_pull.py --run hil1-susan-lf'
```
Plus trace-gens table (the same inline python used for `micbridge-35407ac5a1bb`).
Verification: turn-1 TTFT printed; PASS if turn-1 TTFT ≤ ~900ms (steady band 660-935) — i.e. the keepalive removed the cold-connection penalty; FAIL if turn-1 ≥ 1,050ms (cold path persists → re-diagnose; do NOT iterate blindly).
Write receipt: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter75-llm-keepalive/t2_susan_turn_table.md` (turn table + verdict line).

### T4 — (owner-optional) old-box Susan comparison
Goal: apples-to-apples oldbox-vs-hil1 turn tables for Susan.
Commands (full, on OLD box /home/julio/projects/clean_diallux_SDR):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a; . ./.env; set +a
nohup .venv/bin/python tests/llm2llm/harness.py --personas Susan --rag --langfuse --max-turns 48 > /tmp/opencode/susan-old-lf.log 2>&1 &
```
Then import as `oldbox-susan-lf` (window = actual run time, commit `9ccdccf` — old box runs pre-keepalive code).
Dependencies: T1-T3 done. Cost note: paid LLM run (~$1-2).
Verification: same table shape as T2/T3; `latency_pull.py --run oldbox-susan-lf hil1-susan-lf`.

## Validation Plan (end-to-end)
1. T1 Susan PASS on hil-1 (mock).
2. T2 ledger import 1 call.
3. T3 turn-1 TTFT ≤ ~950ms + steady parity (660-935) → iter75 verified for first-answer.
4. T4 optional old-box Susan table for the report.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Merging iter75 to main | LAW 0 — owner say-so after evidence |
| Live-slots Susan (real booking) | Avoids another cancel cycle; keepalive claim is LLM-plane, mock proves it |
| Mic-lane turn-1 re-test by owner | Already proven shape; owner may re-test manually on `http://localhost:8090/mic` |
| Twilio PSTN e2e | BLOCKED on DNS `twilio-usa.diallux-ai.site` + number repoint (owner) |
