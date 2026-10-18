# plan_iter70-mic-lane_2026-09-24 — test the iter70 speech fixes on THIS server (Helsinki) via browser mic :8025

## Meta
- Date: 2026-09-24
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: serve the ALREADY-EXISTING iter70 worktree (`/tmp/opencode/wt-iter70` @ `dc62fb9`) on a new
  local lane `127.0.0.1:8025` on THIS box (Hetzner Helsinki `46.62.233.228`), verify Langfuse +
  every downstream endpoint resolves HERE, and let the OWNER test the iter70 speech fixes BY EAR
  through the browser mic WS. NO new branch, NO commits, NO merges, NO engine code changes.
- Status: **SUPERSEDED same-day** by `/home/julio/projects/clean_diallux_SDR/plans/plan_iter77-twilio-iter70_2026-09-24.md` (owner redirected: branch wanted, EL Sarah, playback-rate, Twilio phase). Read that file instead.
- Work location: existing worktree `/tmp/opencode/wt-iter70` (branch `engine/iter70-speech-fixes` @ `dc62fb9`).
  The MAIN checkout `/home/julio/projects/clean_diallux_SDR` stays untouched on
  `engine/iter76-harness-firesim` @ `c1f2f1b`.

## Compaction Context
(condensed session record — a fresh agent continues from this block alone)

**What this project is:** Dialux SDR v5 voice engine (LangGraph states + STT/LLM/TTS loop) in
`/home/julio/projects/clean_diallux_SDR/engine`. Two VPS boxes exist: **Helsinki 46.62.233.228**
(THIS box — where this session's work happens, lower latency proven) and **Oregon 5.78.83.174**
(`ubuntu-4gb-hil-1`, owner's other test box; original repo features iterate there first). The
original repo `Retell_AI_MCP_connection` serves live services :8000-8003 — never disturbed.

**Code under test = iter70 SPEECH FIXES** (branch `engine/iter70-speech-fixes`, tip `dc62fb9`):
65f3567 pause re-prompt (10s silence -> one rephrased re-ask, one-shot per turn) ·
94f5164 deterministic transition beat ("ok" ack one-trips only when turn_asked; flat ack routes to
the destination's continuation round) · 02b4bef same-turn near-duplicate dedupe (jaccard>=0.80,
no embedder) · 87a0ce5 speech_filter observability (INFO line per filter drop/split + mic_events
CUT/REASK tags) · dc62fb9 owner prompt edits (NEVER-repeat-yourself rule + 7 ack filler samples).
These are the behaviors the owner wants to hear with his own ear: silence re-prompt, smart ack with
context, question repeats cut.

**Same session, earlier work (context only, NOT part of this plan):** iter76 built
`/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_mic_caller.py` — a standalone fake-caller
driver (Cartesia caller voice + driver-side Deepgram ear + human 5-15s pacing) committed `24991b8` on
branch `engine/iter76-llm-mic-caller` from worktree `/tmp/opencode/wt-iter76`. Owner decided for THIS
plan: **no fake-caller runs — already proven; owner tests by ear via browser mic.**

**Owner decisions this session (settled):**
- Test iter70 on THIS server (Helsinki), not Oregon/Finland-box versions of these paths.
- Do NOT branch, do NOT merge, do NOT commit — a worktree already IS the test vehicle.
- First browser/WS only. Twilio is a LATER phase (separate session) that WILL need a clean branch
  combining iter70 fixes + iter67 Twilio deploy code (see Deferred).
- Audit Langfuse + any endpoint that could conflict on this different server, BEFORE testing.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Serve `/tmp/opencode/wt-iter70` (branch `engine/iter70-speech-fixes` @ `dc62fb9`) on `127.0.0.1:8025` | Owner: "test iter70 on this server via browser". No new branch/commit needed — worktree already owns the code |
| Lane launcher = main checkout's copy-mirror venv python invoked from the worktree dir: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app` with cwd `/tmp/opencode/wt-iter70/engine` | `scripts/serve_voice.sh` hardcodes PORT=8020 AND `.venv/bin/python`; the worktree's own `.venv` is a BROKEN system symlink venv (python -> /usr/bin/python3, no packages, `import diallux` fails). Using main venv + worktree cwd puts the worktree package first on sys.path (verified: `import diallux.app` OK) |
| Port `8025` | Verified free. Busy on this box: 8000, 8001, 8002, 8020 (today's baseline lane, pid 3824992), 8022, 8023, 8024 (SHARED mic lane — untouchable, pid 1196492), 8026 (prod, pid 2333450) |
| Langfuse = `http://localhost:3001`, self-hosted v3.172.1, ALREADY CORRECT on this box | `.env` line `LANGFUSE_HOST=http://localhost:3001`; this box listens 0.0.0.0:3001 and `/api/public/health` returns `{"status":"OK","version":"3.172.1"}` (verified 2026-09-24). NOT the cloud endpoint |
| Owner tests BY EAR at `http://127.0.0.1:8025/mic` (browser mic WS `/mic/ws?k=$VOICE_TEST_TOKEN`) | Owner decision: no fake-caller runs this session |
| Every test booking cancelled immediately (Cal.com event 3801235 is REAL) | Repo law |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO to occupy :8025 and open the browser mic page | owner (PLAN ONLY) |
| Whether to keep the baseline lane :8020 alive during the test (YES recommended = live A/B by switching tabs) | owner; if NO, :8020 lane must be stopped via its pid file |
| Which Twilio number/Caddy hostname to use in the LATER Twilio phase (`twilio.diallux-ai.site` exists per `/tmp/opencode/wt-iter67` deploy artifacts; `calls.diallux-ai.site` per commit `6b53d5a`) | owner — needed only in the deferred phase |

## Environment & Dependencies
- Worktree (code under test): `/tmp/opencode/wt-iter70` — `git -C /tmp/opencode/wt-iter70 log --oneline -1` MUST print `dc62fb9`.
  It already has its own gitignored `.env` (`/tmp/opencode/wt-iter70/engine/.env`, mode 660, owner julio:julio).
- Venv used to LAUNCH (copy-mirror, the only working one): `/home/julio/projects/clean_diallux_SDR/engine/.venv`
  (`bin/python`; NEVER `bin/pip`).
- Preflight script that must pass before calling the lane healthy:
  `/tmp/opencode/wt-iter70/engine/scripts/voice_preflight.py`
- Secrets are read from `/tmp/opencode/wt-iter70/engine/.env` keys: `VOICE_TEST_TOKEN`, `DATABASE_URL`
  (`postgresql://diallux:<redacted>@localhost:5434/diallux`), `LANGFUSE_PUBLIC_KEY`,
  `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`, `OPENAI_API_KEY`, `OPENAI_MODEL` (MODEL LAW = `gpt-5.4`),
  `CARTESIA_API_KEY`, `CARTESIA_MODEL_ID` (`sonic-3.6-2026-08-27` — VOICE LAW pin, survives ANY env edit),
  `CARTESIA_VOICE_ID`, `DEEPGRAM_API_KEY`. NEVER print values.
- Local services this lane depends on (this box):
  - Langfuse self-hosted `http://localhost:3001` (0.0.0.0:3001 listening, health 200, v3.172.1)
  - Postgres `127.0.0.1:5434` (listening, used by `DATABASE_URL` — checkpoint memory)
  - Redis `127.0.0.1:6379`, PG clusters 5432/5433 (listening)
  - `:8001` cal_slots / `:8002` time / `:8003` validator — LIVE ORIGINAL infra, read-only, never started from the fork
- Lane log: `/tmp/opencode/voice_server_8025.log` · pid file: `/tmp/opencode/voice_8025.pid`

## Architecture (block diagram)

```
BROWSER (owner's machine, via SSH tunnel)  ->  http://127.0.0.1:8025/mic
   |
   v  WS /mic/ws?k=$VOICE_TEST_TOKEN
 lane process 127.0.0.1:8025
   launched: /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app
   cwd:      /tmp/opencode/wt-iter70/engine   (iter70 code @ dc62fb9)
   env:      /tmp/opencode/wt-iter70/engine/.env
   |
   +-- Deepgram flux STT  (external)
   +-- OpenAI gpt-5.4 LLM (external)  <-- iter70 fixes live here (pause re-prompt / transition beat / dedupe)
   +-- Cartesia TTS sonic-3.6-2026-08-27 (external)
   +-- Langfuse http://localhost:3001      <- VERIFIED UP on this box
   +-- Postgres 127.0.0.1:5434             <- VERIFIED UP (checkpoint)
   +-- :8001 cal_slots / :8002 time / :8003 validator  <- live original, read-only
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_iter70-mic-lane_2026-09-24.md` | this plan | New (docs -> main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter70-mic-lane/01_report.md` | ear-test notes, journal slices proving each fix landed, latency table | New (gitignored) |
| NO engine file changes | this plan tests existing code only | — |

## Deploy Rules
- START the lane (exact command, from the worktree engine dir so the worktree package wins on sys.path):
  ```bash
  cd /tmp/opencode/wt-iter70/engine && set -a && . ./.env && set +a && \
  setsid nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app \
    --host 127.0.0.1 --port 8025 >> /tmp/opencode/voice_server_8025.log 2>&1 &
  echo $! > /tmp/opencode/voice_8025.pid
  ```
  (NOT `scripts/serve_voice.sh` — it hardcodes PORT=8020 and the broken worktree `.venv`. After launch,
  run the SAME preflight serve_voice.sh uses: `cd /tmp/opencode/wt-iter70/engine && set -a && . ./.env &&
  set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/voice_preflight.py --url http://127.0.0.1:8025`)
- STOP the lane: `kill $(cat /tmp/opencode/voice_8025.pid)`.
- NEVER touch: lane `127.0.0.1:8024` (SHARED mic lane, pid 1196492), `127.0.0.1:8026` (prod),
  `127.0.0.1:8020` (today's baseline lane, pid 3824992 — only owner may stop it),
  `:8000-8003` original live services, production Retell agents, any `.env` voice pin
  (`CARTESIA_MODEL_ID=sonic-3.6-2026-08-27`), Oregon's `diallux.service` / `diallux-mic.service`.
- NO commits, NO merges, NO branch creation in this plan. Evidence goes to `research/` only.

## Tasks (in order)

### T0 — Preflight + endpoint audit (no code)
Goal: prove every dependency resolves on THIS box before the owner spends an ear-test on it.
Files: none.
Commands (full):
```bash
git -C /tmp/opencode/wt-iter70 log --oneline -1
curl -sf http://127.0.0.1:3001/api/public/health
curl -sf -o /dev/null -w "8001=%{http_code}\n" http://127.0.0.1:8001/health
curl -sf -o /dev/null -w "8002=%{http_code}\n" http://127.0.0.1:8002/health
curl -sf -o /dev/null -w "8003=%{http_code}\n" http://127.0.0.1:8003/health
ss -tln | grep -E "127\.0\.0\.1:(5434|6379|8025)"
grep -nE "LANGFUSE_HOST|LANGFUSE_ENABLED|DATABASE_URL|OPENAI_MODEL|CARTESIA_MODEL_ID" /tmp/opencode/wt-iter70/engine/.env | sed 's/=.*/=<set>/'
```
Dependencies: none.
Verification: `git` prints `dc62fb9`; Langfuse `/api/public/health` returns `{"status":"OK","version":"3.172.1"}`;
`:5434` / `:6379` listening; **`:8025` must be FREE**; `.env` lines present. Record any MISS in the report.
NOTE: 8001/8002/8003 may not answer `/health` — record the actual code, do not assume broken.

### T1 — Serve the iter70 lane on :8025
Goal: iter70 code live on this box, RAG proven by preflight.
Files: none (new lane only).
Commands (full): see "START the lane" in Deploy Rules, then:
```bash
curl -sf http://127.0.0.1:8025/health | head -c 300
```
Dependencies: T0 green.
Verification: `/health` returns `"ok":true`, `"llm":"gpt-5.4"`, `"tts":"cartesia/sonic-3.6"`,
`"rag_mode":"rag"`; preflight PASSES (RAG PROVEN). If preflight red -> kill the lane, read
`/tmp/opencode/voice_server_8025.log`, fix nothing in code — report and stop.

### T2 — Prove the iter70 knobs are live in THIS process
Goal: before the owner tests by ear, prove the lane is really running the iter70 settings.
Files: none.
Commands (full):
```bash
cd /tmp/opencode/wt-iter70/engine && set -a && . ./.env && set +a && \
/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -c "
from diallux.config import get_settings
s = get_settings()
print('pause_reask', s.pause_reask, s.pause_reask_ms)
print('dedupe_similar', s.tts_dedupe_similar, s.tts_dedupe_similar_overlap)
print('openai_model', s.openai_model)
print('checkpoint', s.checkpoint_backend)
"
```
Dependencies: T1.
Verification: prints `pause_reask True 10000` and `dedupe_similar True 0.8` (iter70 defaults from
`/tmp/opencode/wt-iter70/engine/diallux/config.py` lines ~178-189). If not -> the lane is NOT iter70; stop and report.

### T3 — Owner EAR TEST via browser mic (the actual test)
Goal: owner hears whether the fixes landed.
Files: none. Then owner opens `http://127.0.0.1:8025/mic` (token in
`/tmp/opencode/wt-iter70/engine/.env` key `VOICE_TEST_TOKEN`) and runs these probes IN ORDER,
one behavior per call, taking notes:
1. **Silence re-prompt (65f3567)** — answer normally, then stay SILENT >10s -> agent must re-ask ONCE,
   REPHRASED, with conversation context (not restart, not repeat the same words).
2. **Smart ack / transition beat (94f5164)** — give a short partial answer ("yeah", "sure") mid-flow ->
   ack must carry NEXT question / keep context, not go mute, not restart.
3. **Repeat cut (02b4bef + dc62fb9)** — provoke two similar replies -> no near-duplicate sentence twice.
4. **Latency** — owner's ear, compared with the :8020 baseline lane tab he already used today.
Dependencies: T2 green.
Verification: per probe, the agent journal must show the matching signature:
```bash
tail -n 200 /tmp/opencode/voice_server_8025.log | grep -E "speech_filter|pause_reask|CUT|REASK|transition|dedupe"
```
Record which of the 4 behaviors PASSED / FAILED / UNCLEAR in the report — a "no journal line" for a
probe is a FAIL, not an UNKNOWN.

### T4 — Langfuse wiring proof + cleanup
Goal: prove the call reached Langfuse on THIS box, then clean up.
Files: none.
Commands (full):
```bash
grep -c "turn .* final report" /tmp/opencode/voice_server_8025.log
tail -n 50 /tmp/opencode/voice_server_8025.log | grep -iE "langfuse|trace"
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && \
  .venv/bin/python scripts/lf.py health
```
Verification: `/health` of the lane reported `"langfuse":true`; `scripts/lf.py health` OK; at least ONE
trace appears for the session from :8025. If ZERO traces -> the fixes are unobservable externally;
say so loudly in the report (that is a finding, not a pass).
Dependencies: T3.
Cleanup (AFTER owner is done): cancel every test booking (Cal.com event 3801235 is REAL), then
`kill $(cat /tmp/opencode/voice_8025.pid)` — only if the owner wants the port freed.

## Validation Plan (end-to-end)
1. T0: all endpoints resolve on THIS box (Langfuse 3001 is the Helsinki self-hosted instance, not cloud).
2. T1: iter70 lane live on :8025, `/health` ok, preflight RAG PROVEN.
3. T2: `pause_reask_ms=10000` + `tts_dedupe_similar` live = we are testing iter70, not something else.
4. T3: owner ear-test verdict per behavior, backed by journal signatature lines.
5. T4: Langfuse received the trace; bookings cancelled; lane stopped.
6. Zero code changed anywhere this session — if any file under `/tmp/opencode/wt-iter70/engine/` is dirty
   outside `eval/llm2llm_report.json` (already dirty before this session), STOP and report.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Twilio live call test | Owner: phase AFTER browser. Needs a NEW clean branch from iter70 tip carrying iter67's Twilio deploy logic (cherry-pick, NOT merge): `6cc6a72` (`/media` transport=twilio pin + `/twiml` X-Twilio-Signature fail-closed gate), `6b53d5a` (deploy artifacts: Caddy `calls.diallux-ai.site` -> 127.0.0.1:8026, systemd unit), `e5a87f6` (Caddy multi-line handle blocks + fastembed pin), `0394a3b` (fastembed pin + hostname -> twilio.diallux-ai.site). Collision pre-check: iter67 touched ~30 files (app.py, config.py, deploy artifacts + its own tests `test_twilio_signature.py`); iter70 touched speech_filter/ingest/prompts + its own tests. Own plan, own branch, owner-gated |
| Fake-caller (iter76 driver) runs | Owner decided: already proven, not needed this session |
| Testing iter74 speech fixes (`engine/iter74-speech-production` @ `5ffcc67`) | Separate later A/B — iter74 is NOT merged and NOT deployed anywhere |
| Any merge of anything into main | LAW 0 — owner say-so only; never this session |
