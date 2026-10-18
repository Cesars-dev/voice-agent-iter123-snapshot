# plan_iter77-twilio-iter70_2026-09-24 — ONE branch (iter70 fixes + Helsinki fixes + Twilio deploy + EL Hannah + py-side playback accel) → browser mic test :8025 → then Twilio

## Meta
- Date: 2026-09-24 (supersedes `plan_iter70-mic-lane_2026-09-24.md` — same day, owner redirected mid-session)
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE branch `engine/iter77-twilio-iter70` carrying iter70 speech fixes + Helsinki-proven
  engine fixes + iter67 Twilio deploy code, served on **OREGON** lane `127.0.0.1:8025` with
  **ElevenLabs Hannah** (owner voice choice) + the browser playback-rate knob; owner
  ear-tests the iter70 behaviors via the mic page (SSH tunnel); then (phase 2) Twilio live call.
- Status: **PARTIALLY EXECUTED this session (T0-T2 done, see Progress Log) — REMAINING WORK = NEXT
  SESSION** (owner: "lets go on another session"). Everything below `NEXT SESSION` is PLAN ONLY.
- Branch: `engine/iter77-twilio-iter70` @ `8c5f72f` — worktree Helsinki `/tmp/opencode/wt-iter77`
  AND worktree Oregon `/tmp/opencode/wt-iter77` (branch pushed to GitHub `origin`, owner ordered
  2026-09-25: "push this to git, pull on OR, lets switch to OR"). **WORK LOCATION FROM NOW ON = OREGON
  5.78.83.174** (`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`, repo
  `/home/julio/projects/clean_diallux_SDR`). Helsinki stays as reference/rollback.
- Work location: the worktree `/tmp/opencode/wt-iter77`; MAIN checkout untouched
  (`engine/iter76-harness-firesim` @ `c1f2f1b`); ONE branch intended for BOTH Helsinki and Oregon ("one branch for OR and we take it from here").

## Compaction Context
(condensed session record — a fresh agent continues from this block alone)

**Project:** Dialux SDR v5 voice engine (LangGraph + STT/LLM/TTS) in
`/home/julio/projects/clean_diallux_SDR/engine`. Boxes: **Helsinki 46.62.233.228** (this work) +
**Oregon 5.78.83.174** (owner's other box; do NOT connect unless owner says so). Original repo
`Retell_AI_MCP_connection` serves live :8000-8003 — never disturbed.

**The 4 OWNER-WANTED behaviors (iter70 speech fixes, branch `engine/iter70-speech-fixes` @ `dc62fb9`):**
65f3567 pause re-prompt (10s silence → ONE rephrased re-ask w/ context, one-shot per turn) ·
94f5164 deterministic transition beat (ack keeps context, routes to destination continuation) ·
02b4bef same-turn near-duplicate dedupe (jaccard ≥0.80, no embedder) · 87a0ce5 speech_filter
observability lines + mic_events CUT/REASK · dc62fb9 prompt edits (NEVER-repeat rule + 7 ack fillers).

**Owner questions answered this session (settled):**
- "Cartesia on the engine or the env?" → CODE default is `tts_provider: str = "elevenlabs"`
  (`/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py:376`); today's :8020 lane ran
  Cartesia only because the lane's `.env` said `TTS_PROVIDER=cartesia`. **OWNER WANTS ELEVENLABS**
  with the owner's tuned EL config (see env below) — env flipped in the branch worktree.
- "The browser acceleration that makes it sound a lil faster" = iter73 T1 `1a8e04a` — browser-side
  `?rate=` param on the mic page, `src.playbackRate` clamp 0.80–1.15, playhead scaled by RATE.
  **Already cherry-picked into the branch** (`8c5f72f`) and de-shadowed to byte-match main's proven
  file (`git diff c1f2f1b -- engine/diallux/static/mic/index.html` = empty). It is PROVIDER-AGNOSTIC
  (works for EL audio too; TTS-side speed pin stays authoritative in env).
- EL vs Cartesia conflict check: none — `diallux/media/tts_factory.py` switches on
  `settings.tts_provider`; both adapters exist and merged (iter66); the `?rate=` knob is browser-side.
  The one test that pinned the OLD env state (`test_factory_switches_provider`) now PASSES with the
  EL env.

**Progress Log — DONE this session (do NOT redo):**
1. Worktree + branch created: `git worktree add /tmp/opencode/wt-iter77 -b engine/iter77-twilio-iter70 dc62fb9`.
2. Cherry-picked onto it (ALL clean, zero conflicts):
   `9ccdccf` (mic page RATE scope fix) → `858543c` (LLM pool keepalive 600s, Helsinki latency fix)
   → `6cc6a72` (Twilio: /media transport=twilio pin + /twiml X-Twilio-Signature fail-closed gate)
   → `6b53d5a` (deploy artifacts: Caddy calls.diallux-ai.site → 127.0.0.1:8026, systemd unit)
   → `e5a87f6` (Caddy multi-line handle blocks + fastembed pin) → `0394a3b` (fastembed pin +
   hostname twilio.diallux-ai.site) → `1a8e04a` (playback-rate knob, re-picked + de-shadowed = `8c5f72f`).
   Branch tip after amend: `8c5f72f`.
3. Audit done: the RAG/Langfuse "pooling" plumbing the owner remembered IS in the branch ancestry
   (iter61 `6c986e8` pool staleness, iter65 `fc45536` prewarm/pool) and the env re-pointing is baked
   into both `.env`s: `LANGFUSE_HOST=http://localhost:3001` (self-hosted Langfuse v3.172.1, VERIFIED
   UP on Helsinki: `curl http://127.0.0.1:3001/api/public/health` → `{"status":"OK","version":"3.172.1"}`)
   and `DATABASE_URL=postgresql://diallux:<redacted>@localhost:5434/diallux` (5434 listening).
4. Env for the branch worktree: `/tmp/opencode/wt-iter77/engine/.env` (copied from
   `/tmp/opencode/wt-iter70/engine/.env`) — keys: `TTS_PROVIDER=elevenlabs` (FLIPPED 2026-09-24 per
   owner; rollback `TTS_PROVIDER=cartesia`), `ELEVENLABS_MODEL_ID=eleven_turbo_v2_5`,
   `ELEVENLABS_VOICE_ID=ZSNL4hPqCnqoMPaI4jGX` (**Hannah "All-American" — owner's CURRENT tuned voice,
   synced 2026-09-24 from the main checkout `.env` = the state the iter73 `?rate=` playback-accel
   calls were tuned against; NOT Sarah — owner corrected: "it was not sarah, I added a new voice"**),
   `ELEVENLABS_SPEED=1.0`, `ELEVENLABS_STABILITY=0.7`, `ELEVENLABS_STYLE=1.0` (TTS speed stays 1.0 —
   EL API hard-caps speed at 1.2 on turbo_v2_5 with HTTP 400; the owner's accel is NOT on the TTS
   side: **the accel lives on the ENGINE/browser py side — the mic page `?rate=` playback knob
   (iter73 T1, `src.playbackRate` clamp 0.80–1.15)**, so Hannah 1.0 TTS × `?rate=1.06..1.15` =
   the "lil faster" feel beyond EL's cap),
   `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` (kept intact per VOICE LAW rollback rule),
   `LANGFUSE_ENABLED=true`, `VOICE_TEST_TOKEN`, `OPENAI_API_KEY`, `OPENAI_MODEL` (=gpt-5.4, MODEL LAW),
   `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`, `CARTESIA_VOICE_ID`. NEVER print values.
   Other owner-discovered EL voices on the account (from iter72/73 voice-lab sessions): Eryn
   `kdnRe2koJdOK4Ovxn2DI` (0.4/1.2), Sarah A&I `Nhs7eitvQWFTQBsf0yiT`, Vanessa
   `8DzKSPdgEQPaK5vKG0Rs`, prod-Sarah `uG1JFy6xppqckhHCs2KG` (Casual & Modern, 1.06/0.5/1.0).
5. Suite on the branch (from `/tmp/opencode/wt-iter77/engine`, main venv):
   `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q` →
   4 failures with cartesia env; after the EL flip `test_factory_switches_provider` PASSES, so expect
   exactly the 3 KNOWN pre-existing env-knob failures (`test_iter46_latency_floor.py::test_fast_first_flush_before_stream_end`,
   `test_iter59_dedupe_semantic.py::test_semantic_threshold_config_defaults`,
   `test_iter60_audit_fixes.py::test_turn_opening_reask_dropped_when_window_nonempty`) — these are the
   iter67-VOICE-LAW env overrides vs old code-default pins; iter74 T5 fixes this class on ITS branch.
   Full suite after EL flip NOT yet re-run — next session T1 must re-run and confirm exactly those 3.
6. TRAPS DISCOVERED (already handled in this session, listed so they are not re-tripped):
   - `scripts/serve_voice.sh` hardcodes PORT=8020 and `.venv/bin/python`; the worktree's own `.venv`
     is a BROKEN system-symlink venv (python → /usr/bin/python3, no packages). Launch the lane with
     the MAIN venv python from the worktree cwd (exact command in T1).
   - The playback-rate knob needs `?rate=` on the MIC PAGE URL (default 1.0 = no accel).
   - ports busy on Helsinki: 8000, 8001, 8002, 8020 (baseline lane, pid 3824992), 8022, 8023,
     8024 (SHARED mic lane, pid 1196492 — UNTOUCHABLE), 8026 (prod, pid 2333450). **:8025 is FREE.** On OREGON busy = 8026 prod, 8090 mic (0.0.0.0 public), 8001-8003, 5434
     — :8025 free there too (verified 2026-09-25).
   - **OR MAIN CHECKOUT = PROD WORKING TREE** (verified 2026-09-25): `diallux.service` (:8026) and
     `diallux-mic.service` (:8090) BOTH run from `/home/julio/projects/clean_diallux_SDR/engine`,
     currently on `engine/iter73-oregon-wip-20260924` @ `df23d37` — NEVER checkout/switch/reset/pull
     in the OR main checkout; all branch work stays in `/tmp/opencode/wt-iter77`.
   - /tmp worktrees + lane logs are reboot-volatile on both boxes (accepted pattern).
   - Helsinki Langfuse binds `0.0.0.0:3001` — internet-exposed (that is why OR reaches it cross-box);
     owner security note, out of scope here.
   - endpoints conflict audit: Langfuse localhost:3001 OK; DB 5434 OK; 8001/8002/8003 are the
     ORIGINAL live services (read-only); no localhost hardpoints broken for this branch.

**Context from earlier in the day (background, do not redo):** iter76 fake-caller driver
(`/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_mic_caller.py`, branch
`engine/iter76-llm-mic-caller` @ `24991b8`, worktree `/tmp/opencode/wt-iter76`) built + 5 happy runs
against :8020 baseline (9ccdccf code): real STT→LLM→TTS loop works, 33 LLM rounds all in Intake,
no bookings created. Owner decided fake tests not needed now — ear tests instead. iter74 speech
fixes (`engine/iter74-speech-production` @ `5ffcc67`) remain NOT merged / NOT deployed (separate A/B later).

7. **T0 OREGON endpoint audit — DONE 2026-09-25 (all green):**
   - **Langfuse:** OR `.env` `LANGFUSE_HOST=http://46.62.233.228:3001` = cross-box to Helsinki's
     self-hosted instance; `/api/public/health` from OR → **HTTP 200** (v3.172.1). Works; every trace
     travels OR→Helsinki (fire-and-forget, acceptable). NO langfuse server runs on OR itself.
   - **Postgres:** OR has its OWN postgres on `localhost:5434` (diallux db); RAG data present:
     `kb_chunks_v2` = **210 rows**, `kb_chunks` = 233, plus `kb_chunks_emb_staging*` tables. RAG is
     served from OR-local data (no cross-box DB dependency).
   - **Live endpoints on OR:** `:8001` cal_slots, `:8002` time, `:8003` validator all **HTTP 200**;
     `diallux.service` (:8026 prod) + `diallux-mic.service` (:8090, listens on 0.0.0.0) active.
   - **Engine venv on OR:** REAL working venv (`/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python`,
     `import diallux` OK — unlike Helsinki's broken worktree symlinks). Use `.venv/bin/python` directly.
   - **Voice state OR == Helsinki branch env:** `TTS_PROVIDER=elevenlabs`, turbo_v2_5, Hannah
     `ZSNL4hPqCnqoMPaI4jGX` 1.0/0.7/1.0, `OPENAI_MODEL=gpt-5.4`, `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` intact.
   - **Env copied into OR worktree:** `cp /home/julio/projects/clean_diallux_SDR/engine/.env
     /tmp/opencode/wt-iter77/engine/.env` (owner-root owned, mode 640).
   - **Free port on OR: :8025** (busy: 8026 prod, 8090 mic 0.0.0.0, 8001-8003, 5434).
   - Keyhound before push: 258 hits ALL pre-existing docs/legacy placeholders; the 7-branch diff has
     ZERO secret-pattern matches (verified) → push clean.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| ONE branch `engine/iter77-twilio-iter70` = iter70 fixes + Helsinki fixes (9ccdccf, 858543c) + iter67 Twilio code + playback-rate knob | Owner: "don't merge, create our own branch… take the engine fixes + the Twilio deployment… one branch for OR and we take it from here" |
| **All work from now on = OREGON** (branch pushed to origin, worktree pulled there 2026-09-25) | Owner: "push this to git, pull on OR, lets switch to OR… we are going to be working on OR from now on" |
| T0 OR endpoint audit DONE (2026-09-25, results in Progress Log item 7) | Owner: "T0 must be to audit langfuse and every endpoint" |
| ElevenLabs Hannah on the lane (`TTS_PROVIDER=elevenlabs` + Hannah block @ TTS speed 1.0), Cartesia kept as rollback keys | Owner: "I want eleven labs… a particular voice and a config"; the tuned voice is Hannah (owner corrected: "it was not sarah, I added a new voice"); accel = py/browser side, not TTS |
| Playback-rate accel = `?rate=` mic-page param, ALREADY in the branch | Owner's remembered "browser acceleration" = iter73 T1; provider-agnostic; env TTS speed stays authoritative |
| Test order: browser mic WS FIRST, Twilio ONLY after owner satisfied | Owner: "first let's test it via the websocket. If everything goes well, then we test it via Twilio" |
| Port :8025 on OREGON | Only free lane port on both boxes (OR busy: 8026/8090/8001-8003/5434) |
| NO fake-caller runs | Owner: "no fake tests… we already proved that it works" |
| Ear test verification backed by journal lines (speech_filter/CUT/REASK/pause_reask/transition) | "no journal line for a probe = FAIL, not UNKNOWN" (from prior plan, kept) |
| No merges into main; branch NOT for merging until owner satisfied | LAW 0 + owner "don't merge anything" |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Owner GO for next session (serve :8025 + ear test) | owner (this is the standing plan) |
| Owner's rate value for the ear test (baseline `?rate=1.0` first, then `1.06`/`1.1`/`1.15` steps — accel is py/browser-side on top of TTS speed 1.0) | owner at mic-page open |
| Twilio phase: which Caddy hostname to repoint (`twilio.diallux-ai.site` vs `calls.diallux-ai.site`) + whether a NEW Twilio number is needed | owner, phase 2 |
| Full suite re-run after the EL flip (expect exactly the 3 known fails) | next session T1 |

## Environment & Dependencies
- Branch/worktree: `/tmp/opencode/wt-iter77` (branch `engine/iter77-twilio-iter70` @ `8c5f72f`) — code under test.
- Launch venv (the ONLY working one): `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (NEVER `bin/pip`).
- Env file: `/tmp/opencode/wt-iter77/engine/.env` — OREGON worktree is the OPERATIVE env (verified
  2026-09-25: full EL Hannah block + `ELEVENLABS_API_KEY` + `VOICE_TEST_TOKEN` + Langfuse PK/SK +
  `AUDIO_TRANSPORT=browser` + `DATABASE_URL=…@localhost:5434/diallux`; root:root 0640). See Progress
  Log item 4 for the Helsinki-era key list.
- Services on Helsinki: Langfuse `http://localhost:3001` (self-hosted v3.172.1), Postgres `127.0.0.1:5434`,
  Redis `127.0.0.1:6379`, original live `:8001/:8002/:8003` (read-only). Twilio phase adds
  Caddy `twilio.diallux-ai.site` → lane port (deploy artifacts already in the branch).
- Lane log `/tmp/opencode/voice_server_8025.log`, pid file `/tmp/opencode/voice_8025.pid`.
- Secrets: read from the env file, NEVER print. `scripts/keyhound` before any push.

## Architecture (block diagram)

```
OWNER BROWSER (SSH tunnel) -> http://127.0.0.1:8025/mic?rate=1.0|1.06..1.15&k=$VOICE_TEST_TOKEN
   |  WS /mic/ws (linear16 16k, 640B/20ms frames)
   v
lane :8025 = engine/iter77-twilio-iter70 @ 8c5f72f
  cwd /tmp/opencode/wt-iter77/engine, env ./.env
  ├─ STT  Deepgram flux (external)
  ├─ LLM  gpt-5.4 (OpenAI)         <- iter70 fixes: pause re-prompt 10s, transition beat, dedupe
  ├─ TTS  ElevenLabs Hannah "All-American" (eleven_turbo_v2_5, speed 1.0, stability 0.7, style 1.0)
  │        (rollback: TTS_PROVIDER=cartesia -> sonic-3.6-2026-08-27 Linda)
  ├─ browser ?rate= playback accel 0.80-1.15 (iter73 T1, provider-agnostic)
  ├─ Langfuse http://localhost:3001 (VERIFIED UP Helsinki)
  ├─ Postgres 127.0.0.1:5434 (checkpoint)
  └─ Twilio phase 2: /twiml signature gate + /media transport=twilio (iter67 code IN the branch)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/plans/plan_iter77-twilio-iter70_2026-09-24.md` | this plan | New (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter77-twilio-iter70/01_report.md` | ear-test verdicts, journal slices, latency table, Twilio evidence | New (gitignored) |
| `/tmp/opencode/wt-iter77/engine/.env` | already set (EL Hannah 1.0/0.7/1.0, synced from main `.env`); next session may only flip `TTS_PROVIDER` back if owner says | Edit (env only, gitignored) |
| NO other code changes planned next session | testing + Twilio pointing only | — |

## Deploy Rules
- Serve the lane ON OREGON (exact; OR venv is real, run it from the worktree so the branch package wins):
  ```bash
  ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'cd /tmp/opencode/wt-iter77/engine && set -a && . ./.env && set +a && setsid nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8025 >> /tmp/opencode/voice_server_8025.log 2>&1 & echo $! > /tmp/opencode/voice_8025.pid'
  ```
  then preflight (same gate serve_voice.sh uses):
  ```bash
  ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'cd /tmp/opencode/wt-iter77/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/voice_preflight.py --url http://127.0.0.1:8025'
  ```
- Stop the lane: `ssh … 'kill $(cat /tmp/opencode/voice_8025.pid)'`.
- Browser access from Julio's laptop to OR lane = SSH tunnel (OR has no Caddy route for :8025 until Twilio phase).
- NEVER touch: `diallux.service` (:8026 prod on OR), `diallux-mic.service` (:8090 mic on OR — listens
  on 0.0.0.0, public-ish: treat as live), `:8000-8003` live services (both boxes), Helsinki's
  `:8024` shared mic lane + `:8020` baseline lane, production Retell agents,
  `/opt/diallux-production/.env`, `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` in any env edit
  (rollback survival law).
- Twilio phase 2 deploy = owner-gated: the branch's Caddy/systemd artifacts (`engine/deploy/`
  per iter67 commits) are TEMPLATES ONLY — on OR both collide with prod (:8026 / unit name
  `diallux.service`) and `caddy-apply` does not exist on OR; see the T6 gap register (audit
  2026-09-25) before any phase-2 work.

## Tasks (in order)

### T1 — Re-verify branch state + suite (NEXT SESSION — on OREGON)
Goal: prove nothing drifted since this session; suite = 3 known env-knob fails only.
Files: none.
Commands (full) — run ON OREGON (`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`):
```bash
git -C /tmp/opencode/wt-iter77 log --oneline -8
git -C /tmp/opencode/wt-iter77 status --short
cd /tmp/opencode/wt-iter77/engine && set -a && . ./.env && set +a && \
/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q 2>&1 | grep -E "^FAILED|[0-9]+ passed"
```
Verification: tip = `8c5f72f` on top of the cherry-pick chain; status FULLY clean (the OR worktree is
fresh — the `eval/llm2llm_report.json`-class dirt was Helsinki-worktree-only); failures = EXACTLY the 3 known
(iter46 fast_first_flush, iter59 dedupe_semantic, iter60 reask) — anything else = STOP and report.

### T2 — Preflight + endpoint audit re-check (fast, ON OREGON)
Goal: confirm the audit results still hold at session start.
Files: none.
Commands (full) — via ssh to OR:
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '
curl -sf http://46.62.233.228:3001/api/public/health
ss -tln | grep -E "127\.0\.0\.1:(5434)"
ss -tln | grep -q "127.0.0.1:8025 " && echo BUSY || echo FREE
grep -nE "^(TTS_PROVIDER|ELEVENLABS_VOICE_ID|ELEVENLABS_MODEL_ID|ELEVENLABS_SPEED|LANGFUSE_HOST|CARTESIA_MODEL_ID)" /tmp/opencode/wt-iter77/engine/.env | sed "s/\(KEY=\).*/\1<set>/"
'
```
Verification: Langfuse 200 v3.172.1 (cross-box); 5434 listening; :8025 FREE; env shows
`TTS_PROVIDER=elevenlabs`, Hannah voice, `CARTESIA_MODEL_ID` still pinned.

### T3 — Serve :8025 ON OREGON and prove iter70 + EL are live
Goal: lane up; knobs live; EL adapter selected.
Files: none.
Commands (full): Deploy Rules "Serve the lane" + :
```bash
curl -sf http://127.0.0.1:8025/health | head -c 300
cd /tmp/opencode/wt-iter77/engine && set -a && . ./.env && set +a && \
/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -c "
from diallux.config import get_settings
s = get_settings()
print('provider', s.tts_provider, 'el_voice', s.elevenlabs_voice_id, 'speed', s.elevenlabs_speed)
print('pause_reask', s.pause_reask, s.pause_reask_ms)
print('dedupe_similar', s.tts_dedupe_similar, s.tts_dedupe_similar_overlap)
print('model', s.openai_model)
"
```
Verification: `/health` `"ok":true, "tts":"elevenlabs/..."`, `"llm":"gpt-5.4"`; prints
`provider elevenlabs` + Hannah id `ZSNL4hPqCnqoMPaI4jGX` + `pause_reask True 10000` + `dedupe_similar True 0.8`.
If TTS init fails (EL key/rate limits) → record error, offer cartesia rollback (env flip), STOP.

### T4 — OWNER EAR TEST via browser mic ON OREGON (the real test)
Goal: owner hears the 4 behaviors with EL Hannah + optional `?rate=`; browser reaches the lane via SSH tunnel to OR :8025.
Files: none.
Procedure — owner tunnel from laptop first (`ssh -i <owner-key> -N -L 8025:127.0.0.1:8025 root@5.78.83.174`), then
owner at `http://127.0.0.1:8025/mic?rate=1.0&k=<VOICE_TEST_TOKEN>` — `k=` is MANDATORY (`/mic/ws` is
fail-closed, close 4401 on missing/mismatched token, app.py:241-250). Baseline `rate=1.0` first, then
`?rate=1.06` / `1.1` / `1.15` steps:
1. Silence re-prompt: answer, then stay silent >10s → ONE rephrased re-ask with context.
2. Smart ack: short "yeah/sure" answers → ack keeps context, next question flows.
3. Repeat cut: provoke similar replies → no near-duplicate twice.
4. Latency: owner's ear vs the :8020 baseline lane tab.
Agent-side verification per probe (on OR) — evidence channels (audited 2026-09-25):
probe 1 = `pause re-ask firing` (session.py:754; grep word `pause_reask` does NOT match it);
probe 2 = owner ear ONLY (transition beat has NO log line and NO span — 94f5164 added none);
probe 3 = `speech_filter stage=similar` (builder.py:2390/2502, the jaccard dedupe sites);
probe 4 = ear + `mic page stats` line. `CUT`/`REASK` are regex tags inside scripts/mic_events.py,
not log lines — use the script or the corrected grep:
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'cd /tmp/opencode/wt-iter77/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/mic_events.py --tag CUT,REASK,WS-GATE,STT-ERR,TTS-ERR,TURN'
# fallback: grep -E "speech_filter|re-ask firing|mic ws rejected" /tmp/opencode/voice_server_8025.log | tail -40
```
"no journal line for a probe = FAIL" applies ONLY to probes 1 and 3 (lines exist); probe 2 verdict is ear-only.
Record PASS/FAIL/UNCLEAR per probe in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter77-twilio-iter70/01_report.md`.

### T5 — Langfuse proof + cleanup (trace lands on Helsinki's :3001 even when the lane is on OR)
Goal: trace reached Langfuse (cross-box OR→Helsinki); bookings cancelled; lane stopped if owner wants.
Commands (full):
```bash
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'tail -n 50 /tmp/opencode/voice_server_8025.log | grep -iE "langfuse|trace"'
# HELSINKI-local command (traces land on Helsinki's Langfuse; do NOT run this on OR):
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python scripts/lf.py health
```
Verification: lane `/health` `"langfuse":true`; `lf.py health` OK — NOTE: it may print "ingest
pipeline: NO RECENT TRACES (worker/clickhouse down?)" — quiet-period heuristic only (traces from
2026-09-24 ARE queryable). PASS criterion = the :8025 session's trace appears in `lf.py traces`.
(they land in Helsinki's Langfuse because OR points at `http://46.62.233.228:3001`).
Cleanup: cancel every test booking (Cal.com event 3801235 is REAL); stop lane only if owner wants
the port freed.

### T6 — PHASE 2: Twilio (ONLY after owner says browser test is good)
Goal: live Twilio call through the same branch.
Files: Caddy + systemd artifacts already in the branch (from iter67 commits).
Outline (full plan rewrite required before executing — this is the stub):
1. Owner picks port + hostname (`twilio.diallux-ai.site` per `0394a3b` or `calls.diallux-ai.site`
   per `6b53d5a` — DECIDE before touching Caddy).
2. Serve the branch lane on the chosen port (uvicorn command like T3, different port).
3. ~~Apply Caddy route via caddy-apply~~ — `sudo /usr/local/bin/caddy-apply` DOES NOT EXIST on OR
   (verified 2026-09-25; Helsinki-only wrapper). Gap register the T6 rewrite MUST resolve (all
   owner-gated, audit 2026-09-25): (1) OR Caddy has NO public :80/:443 (loopback :8080 utility proxy
   + :2019 admin only) → build the edge on OR (Hetzner cloud firewall open, owner console) or run
   phase 2 on Helsinki (public Caddy + caddy-apply already there); (2) DNS `twilio.diallux-ai.site`
   → 46.62.233.228 (HELSINKI), `calls.diallux-ai.site` → no A record → repoint to the chosen box;
   (3) if OR: edit `/etc/caddy/Caddyfile` directly + `systemctl reload caddy`; (4) branch
   `deploy/Caddyfile` hardcodes `127.0.0.1:8026` = OR PROD — block must target the chosen LANE port;
   (5) branch `deploy/diallux.service` would OVERWRITE the OR prod unit (same name, port 8026,
   /opt path) — use a NEW unit name (e.g. `diallux-twilio.service`) + worktree path + lane port, or
   manual uvicorn per T3; (6) lane env needs `TWILIO_AUTH_TOKEN` + `TWILIO_ACCOUNT_SID` +
   `PUBLIC_BASE_URL=https://<chosen hostname>` (present on OR only in `/opt/diallux-production/.env`;
   never print values) — without the token `/twiml` 403s everything (fail-closed, app.py:141-142),
   without PUBLIC_BASE_URL the TwiML Stream URL is a placeholder (config.py:421).
4. Twilio number webhook → `https://<hostname>/twiml` (X-Twilio-Signature gate will validate);
   `/media` pins transport=twilio (mulaw 8k) automatically.
5. Owner makes a REAL call; capture journal + Langfuse; cancel any test booking.
Dependencies: T4 verdict PASS + owner GO.

## Validation Plan (end-to-end)
1. T1 suite = 3 known fails only, tip `8c5f72f`, chain intact, OR worktree FULLY clean.
2. T2 all endpoints green on OREGON (Langfuse 3001 cross-box, PG 5434, :8025 free).
3. T3 lane up: EL Hannah + iter70 knobs + gpt-5.4 + RAG preflight PASS.
4. T4 owner ear verdict per behavior + journal evidence per the corrected channels (probe 2 ear-only).
5. T5 Langfuse trace + bookings cancelled.
6. Zero merges; branch stays local until owner satisfied; then owner decides merge OR/ORIGIN push.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter74 speech fixes A/B (`engine/iter74-speech-production` @ `5ffcc67`) | separate later A/B, owner-gated; NOT merged/deployed anywhere |
| iter76 fake-caller runs | already proven (5 happy runs vs :8020 baseline); owner said no fake tests this phase |
| Merging ANYTHING into main | LAW 0 — owner say-so only |
| Oregon lane serve | after Helsinki ear-test passes, same branch, owner picks the box/port |
| EL matrix voice battery (iter72 voice lab Eryn/Sarah/Vanessa) | separate voice-lab plan `078f06d`; not this branch's job |
