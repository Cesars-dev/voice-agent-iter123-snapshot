# plan_v5_iter76_llm_mic_caller — Maria-v2: conversational LLM caller through the REAL mic path (Cartesia voice, LOCAL test lane)

## Meta
- Date: 2026-09-24
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Scope: ONE tool — a conversational LLM-caller driver (`llm_mic_caller.py`) that drives the REAL mic
  WebSocket path (Deepgram STT → engine → TTS → agent audio-out) with a Cartesia-voiced caller LLM
  that PACES like a human: waits for the agent to finish every turn, waits 5-15s between turns,
  reacts to what the agent actually said. Plus 4 scenario pins (barge-in, question-dump, forced
  repeat, silence/watchdog). Runs ENTIRELY on the local Hetzner VPS (46.62.233.228) against the
  LOCAL test voice lane on `127.0.0.1:8020` — never Oregon's lanes, never the shared mic lane :8024.
- Status: PLAN ONLY (not started — awaits owner approval)
- Branch: `engine/iter76-llm-mic-caller` (cut from `9ccdccf` = `engine/iter73-playback-rate` tip;
  NOT from iter74 — the target lane may serve any branch, the driver imports NO engine code)
- Work location: MAIN checkout `/home/julio/projects/clean_diallux_SDR`; runs are LOCAL (this box)

## Compaction Context
(condensed session record — a fresh agent continues from this block alone)

**What this project is:** Dialux SDR v5 voice engine (LangGraph 9-state + STT/LLM/TTS loop) in
`/home/julio/projects/clean_diallux_SDR/engine`. Local box = Hetzner VPS `46.62.233.228`
(Helsinki). Mic lane for SHARED tests = `diallux-8024.service` on `127.0.0.1:8024` (NEVER disturbed).
Test voice lanes spin via `/home/julio/projects/clean_diallux_SDR/engine/scripts/serve_voice.sh`
(PORT=8020, refuses prod ports 8000-8003, refuses busy port, loads `.env`, starts detached with
setsid, polls /health, runs the RAG preflight gate; log
`/tmp/opencode/voice_server_8020.log`, pid `/tmp/opencode/voice_8020.pid`). As of 2026-09-24
a test lane IS live on `127.0.0.1:8020` (pid 3824992, /health 200).

**OREGON box (context only — NOT a target for this plan):** Hetzner `ubuntu-4gb-hil-1` (Hillsboro,
Oregon) `5.78.83.174`, SSH `ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`, repo
`/home/julio/projects/clean_diallux_SDR` @ `9ccdccf`, system units `diallux.service` (:8026) +
`diallux-mic.service` (:8090). The owner runs tests there — DO NOT connect to it in this plan.
A fake-mic rig already ran there 2026-09-24 13:36-13:38 (ONE pre-recorded "Maria from Bright Smile
Dental" wav via `/tmp/gen_caller.py` Cartesia / `/tmp/gen_caller_el_pcm.py` ElevenLabs → streamed
through the real `/mic/ws`; session `35407ac5a1bb`, 7 turns, all eager-adopted, TTFT 754-1144ms).
Proven facts reused: mic WS shape works with a scripted driver; Cartesia REST TTS body shape.

**Owner decisions this session (2026-09-24, settled):**
- Conversational caller LLM ("prompt Maria v2 to act"): WAIT for the agent to speak each turn,
  WAIT ~10s (5-15s) before replying — like a real caller.
- Caller voice = CARTESIA (owner: "use cartesia, cheaper tokens"), NOT ElevenLabs.
- "lets do on a new session" → write the plan per the new-plan SOP; execution = next session.
- Runs on the LOCAL Hetzner VPS 46.62.233.228 against the LOCAL test lane :8020 ("so no collision"
  with Oregon :8090 tests). NOT port 8090 anywhere.

**Same session, iter74 (already implemented on Helsinki, branch `engine/iter74-speech-production`
@ `5ffcc67`, suite 481 green, Maria chat PASS BOOK — NOT merged, NOT deployed):** SpeechLedger (one
flush owner for all speech cuts), question clamp (1/round + 2/turn, knobs `tts_max_questions_*`),
never-mute REVIVE, cancel-reconcile notes (barge-in/eager-cancel → next turn continues from what
the caller HEARD), STT zombie watchdog (`stt_watchdog_ms=3000`). The driver in THIS plan is the
vehicle that will exercise all of it ONCE iter74 is deployed to a lane — and the same driver runs
against `9ccdccf` (today's lane) as the A/B baseline.

**Proven local-lane facts:**
- Local mic page/lane convention: `ws://127.0.0.1:<port>/mic/ws?k=$VOICE_TEST_TOKEN` (token in
  `/home/julio/projects/clean_diallux_SDR/engine/.env` key `VOICE_TEST_TOKEN` — NEVER print it).
- Browser transport = linear16 PCM 16k (`diallux/media/deepgram_stt.py`: `transport="browser"` →
  `linear16` @ `settings.browser_sample_rate`), 20ms frames = 640 bytes (2B × 16000 × 0.02).
- Cartesia REST TTS (proven by the Oregon rig `gen_caller.py`): `POST https://api.cartesia.ai/tts/bytes`,
  headers `Authorization: Bearer $CARTESIA_API_KEY` + `Cartesia-Version: 2025-04-16`; body
  `{"model_id": "sonic-3.6-2026-08-27", "transcript": "...", "voice_id": "$CARTESIA_VOICE_ID",
  "output_format": {...}}`. Raw 16k shape to be confirmed in T1 probe.
- MODEL LAW: caller LLM = `gpt-5.4` via `OPENAI_MODEL` / `OPENAI_API_KEY` in the engine `.env`.
- Secrets live in `/home/julio/projects/clean_diallux_SDR/engine/.env`; never print values.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Runs on the LOCAL box against the LOCAL test lane `127.0.0.1:8020` (fallback spin :8021) — NEVER Oregon :8090, NEVER :8024 | Owner: "not on port 8090, will kill my tests"; "we run on local hetzner vps 46 — so no collision". :8024 is the shared mic lane (untouchable); :8020 is the designated test lane |
| Caller voice = Cartesia `sonic-3.6-2026-08-27` + Linda `CARTESIA_VOICE_ID` | Owner: cheaper tokens; proven endpoint + pin from the Oregon rig |
| Driver = standalone script, stdlib + `websockets` + `openai` + `requests` ONLY, zero `diallux.*` imports | Runs against ANY engine branch/box without version skew |
| Caller LLM = `gpt-5.4` | MODEL LAW |
| Turn-end detection = agent audio-out idle (no new agent audio ≥ `--agent-idle-s` 1.5s after audio started, max `--max-turn-wait` 30s) | WS audio is the honest caller experience; journal `turn N final report` is the cross-check |
| Caller hears the agent via a SECOND Deepgram flux WS in the driver (feeds the agent PCM it receives, reads transcripts back) | No engine endpoint exposes turn text; audio-path truth; reuses `DEEPGRAM_API_KEY` |
| Pacing wait = uniform(5,15)s AFTER agent idle; during the wait the driver sends NO frames | Real caller behavior; no frames = no watchdog trigger (the watchdog requires flowing audio); silence-frames is a SEPARATE scenario |
| One scripted BARGE-IN (speak mid-agent-speech), one FORCED REPEAT ("sorry I didn't catch that"), one QUESTION DUMP (4 questions in one breath) | These are the iter74 behaviors the driver exists to exercise (reconcile note, similar dedupe, clamp) — A/B-able vs `9ccdccf` |
| `--scenario happy\|barge-in-only\|dump-only\|watchdog` | one variable per run |
| Evidence JSON + journal slice → `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter76-llm-mic-caller/` | repo law: evidence to research/, gitignored |
| Suite stays green after the driver lands | LAW 0; the driver is `engine/scripts/` content |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Exact Cartesia `output_format` body for raw pcm_s16le @16000 (proven shape is wav/44100) | T1 probe; on 4xx the error JSON lists valid values — adjust and re-probe once |
| Whether the :8020 lane's `browser_sample_rate` is 16000 | `/home/julio/projects/clean_diallux_SDR/engine/.env` key `BROWSER_SAMPLE_RATE` (or code default in `/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py`) — pin in T0 |
| Owner GO to cut the branch + use the :8020 lane | owner (PLAN ONLY) |
| Does the happy scenario book on the REAL Cal.com? (the test lane loads the engine `.env` → REAL webhooks) | owner yes/no; if yes → cancel every test booking immediately after each run (event 3801235 is REAL) |

## Environment & Dependencies
- Repo: `/home/julio/projects/clean_diallux_SDR` (branch `engine/iter76-llm-mic-caller`, cut from `9ccdccf`)
- Engine venv: `/home/julio/projects/clean_diallux_SDR/engine/.venv` (pytest: `.venv/bin/python -m pytest tests -q`; NEVER bin/pip — copy-mirror venv)
- Secrets: `/home/julio/projects/clean_diallux_SDR/engine/.env` — keys used: `CARTESIA_API_KEY`,
  `CARTESIA_VOICE_ID`, `CARTESIA_MODEL_ID`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `DEEPGRAM_API_KEY`,
  `VOICE_TEST_TOKEN`. Source: `cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a`
- Test lane: `127.0.0.1:8020` (live) or start with
  `/home/julio/projects/clean_diallux_SDR/engine/scripts/serve_voice.sh` (log
  `/tmp/opencode/voice_server_8020.log`). Lane serves branch state of the MAIN checkout —
  currently `9ccdccf`-class prod code (NOTE: main checkout is on `engine/iter75-llm-keepalive` @
  `9ccdccf` — someone else's branch, DO NOT switch branches on the MAIN checkout; the driver does
  not care).
- NO new packages (all four deps already in the engine venv).
- Deepgram flux WS for the driver-side agent-audio transcription: `wss://api.deepgram.com/v2/listen?model=flux-general-en&encoding=linear16&sample_rate=16000` (same shape as `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/deepgram_stt.py:74-89`, key `Token $DEEPGRAM_API_KEY`).

## Architecture (block diagram)

```
llm_mic_caller.py (LOCAL box 46.62.233.228)
  ├─ CallerBrain: OpenAI gpt-5.4 — persona Maria-v2 + pacing rules
  │     (1-2 sentence bursts, human pauses, on-signal dump/barge; no tools, plain text)
  ├─ CartesiaCallerTTS: POST https://api.cartesia.ai/tts/bytes
  │     model sonic-3.6-2026-08-27, Linda voice, raw pcm_s16le 16k (T1-probed)
  ├─ WS ws://127.0.0.1:8020/mic/ws?k=$VOICE_TEST_TOKEN
  │     ├─ SEND: caller PCM in 20ms frames (640B), real-time pacing (0.02s sleep)
  │     │        pacing wait = NO frames at all
  │     └─ RECV: agent audio-out bytes → agent_ring buffer + JSON events
  ├─ AgentEar: second WS → wss://api.deepgram.com/v2/listen (flux) fed the agent audio →
  │     agent transcript = what the caller actually HEARD
  ├─ pacing loop: agent_spoke → idle 1.5s → wait 5-15s → CallerBrain → CartesiaCallerTTS → stream
  └─ scenarios: happy (full arc) | barge-in-only | dump-only | watchdog (silence frames 12s)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_mic_caller.py` | NEW driver (~300 lines): MicDriver WS client, Cartesia caller TTS, AgentEar (driver-side Deepgram), CallerBrain, pacing loop, scenario flags, evidence writer | New |
| `/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter76_llm_mic_caller.py` | pins: 20ms framing math (640B), agent-idle turn-end detector on a synthetic byte stream, persona prompt contains the pacing rules, watchdog scenario emits zero-energy frames, no engine imports | New |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter76_llm_mic_caller.md` | this plan | New (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter76-llm-mic-caller/01_report.md` | run evidence, transcripts, journal slices, A/B notes vs iter74 | New (gitignored) |

## Deploy Rules
- Test lane lifecycle: PREFER the already-running `127.0.0.1:8020` lane (health-check first). If
  down: `/home/julio/projects/clean_diallux_SDR/engine/scripts/serve_voice.sh` (it refuses prod
  ports and busy ports; log `/tmp/opencode/voice_server_8020.log`).
- NEVER touch: `diallux-8024.service` (shared mic lane), Oregon's `diallux.service` /
  `diallux-mic.service` (:8026/:8090), `services/` ports 8001-8003, production Retell agents,
  `/opt/diallux-production/.env`, any `.env` voice pin
  (`CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` survives ANY env edit).
- The driver writes only to `/tmp/opencode/` + `research/surgeon/iter76-llm-mic-caller/`.
- Helsinki suite: `cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python -m pytest tests -q`

## Tasks (in order)

### T0 — Preflight (no code)
Goal: pin the WS protocol + sample rate; confirm the :8020 lane is up.
Files: none.
Commands (full):
```bash
curl -sf http://127.0.0.1:8020/health | head -c 300
grep -nE "mic/ws|mic_page|sample_rate|linear16" /home/julio/projects/clean_diallux_SDR/engine/diallux/app.py
grep -n "browser_sample_rate" /home/julio/projects/clean_diallux_SDR/engine/diallux/config.py
grep -E "VOICE_TEST_TOKEN|BROWSER_SAMPLE_RATE" /home/julio/projects/clean_diallux_SDR/engine/.env | sed 's/=.*/=<set>/'
```
Dependencies: none.
Verification: /health 200; exact `browser_sample_rate` + WS URL + frame format recorded in the plan
Architecture section (edit the plan if they differ); lane :8024 untouched throughout.

### T1 — Cartesia raw-PCM probe (1 request, local)
Goal: prove `output_format={"container":"raw","format":"pcm_s16le","sample_rate":16000}` returns raw 16k PCM.
Files: temp only (`/tmp/opencode/probe_cartesia_raw.py` — not committed).
Commands (full):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python - <<'PYEOF'
import os, requests
r = requests.post("https://api.cartesia.ai/tts/bytes",
    headers={"Authorization": f"Bearer {os.environ['CARTESIA_API_KEY']}",
             "Cartesia-Version": "2025-04-16", "Content-Type": "application/json"},
    json={"model_id": os.environ["CARTESIA_MODEL_ID"],
          "transcript": "Testing raw pcm sixteen kilohertz output.",
          "voice_id": os.environ["CARTESIA_VOICE_ID"],
          "output_format": {"container": "raw", "format": "pcm_s16le", "sample_rate": 16000}},
    timeout=30)
print("status:", r.status_code, "bytes:", len(r.content), "ctype:", r.headers.get("content-type"))
if r.status_code != 200: print(r.text[:400])
PYEOF
```
Dependencies: none.
Verification: 200 + bytes ≈ duration×32000 (1.5s speech ≈ 48k); else read the error JSON's valid
values and re-probe ONCE with the corrected shape.

### T2 — Driver implementation (commit 1)
Goal: the full driver + unit pins, on branch `engine/iter76-llm-mic-caller`.
Files: `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_mic_caller.py` +
`/home/julio/projects/clean_diallux_SDR/engine/tests/test_iter76_llm_mic_caller.py`.
Interface (pin — the ONLY entry point):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a
.venv/bin/python scripts/llm_mic_caller.py \
  --ws-url "ws://127.0.0.1:8020/mic/ws?k=$VOICE_TEST_TOKEN" \
  --scenario happy \
  --min-gap 5 --max-gap 15 --agent-idle-s 1.5 --max-turn-wait 30 \
  --caller-model "$OPENAI_MODEL" \
  --out /tmp/opencode/llm_mic_caller_<ts>.json
```
Components (ONE file, ~300 lines, no comments per repo style):
1. `MicDriver` — WS: binary OUT = caller audio frames; binary IN = agent audio (append to
   `agent_ring`); text IN = JSON events (append). On engine close → end call, flush evidence.
2. `CartesiaCallerTTS` — T1's endpoint/body verbatim; 3 retries with 0.5s backoff; returns bytes.
3. `AgentEar` — second Deepgram flux WS (linear16 16k), fed the agent PCM as it arrives; final
   transcripts = the agent's words the caller heard.
4. `CallerBrain` — one completion per turn; system prompt = Maria-v2 persona (Bright Smile Dental
   office manager, happy path, wants the walkthrough booked) + PACING RULES: reply in a short 1-2
   sentence human burst; after the DUMP signal ask 4 questions in one breath; on the BARGE signal
   produce exactly one short sentence (the driver cuts the agent off with it); never invent tool
   outcomes; conversation so far = agent transcript pairs.
5. Pacing loop: agent spoke (audio arriving) → idle `--agent-idle-s` → uniform gap → generate →
   TTS → stream 20ms frames in real time. `happy` = greeting wait 2s → normal flow until
   ConfirmSlots/booking → goodbye → exit; includes the FORCED REPEAT turn ("sorry I didn't catch
   that, say it again") right after the pricing reveal.
6. Scenarios: `barge-in-only` (ONE turn: stream mid-agent-speech), `dump-only` (ONE turn: the
   4-question dump), `watchdog` (after agent idle: stream zero-energy frames for 12s — with the
   iter74 watchdog deployed expect ONE `stt watchdog` reconnect journal line; on `9ccdccf` it
   exercises plain silence handling instead — that IS the A/B).
7. Evidence writer — JSON: config, events (WS lifecycle + per-turn spans), agent/caller transcript
   pairs, and the `journalctl -u diallux-*:8020 pid` turn-report lines captured during the run
   (subprocess tail on this box; the :8020 lane logs to `/tmp/opencode/voice_server_8020.log`).
Verification (Helsinki):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a && .venv/bin/python -m pytest tests/test_iter76_llm_mic_caller.py tests/test_units.py -q
```
Dependencies: T0 + T1. Commit on the branch.

### T3 — Happy run (the real proof)
Goal: one full `--scenario happy` call against :8020.
Commands (full):
```bash
cd /home/julio/projects/clean_diallux_SDR/engine && set -a && . ./.env && set +a
setsid nohup .venv/bin/python scripts/llm_mic_caller.py \
  --ws-url "ws://127.0.0.1:8020/mic/ws?k=$VOICE_TEST_TOKEN" \
  --scenario happy --min-gap 5 --max-gap 15 \
  > /tmp/opencode/iter76_happy.log 2>&1 < /dev/null &
```
Verification: evidence JSON written; `tail /tmp/opencode/voice_server_8020.log` shows ≥6 turns
(each with a final report); transcript coherent; the caller WAITED between turns (gaps visible in
the JSON timeline); if a booking got created → CANCEL it immediately (Cal.com event 3801235 is
REAL). Copy evidence to `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter76-llm-mic-caller/`.
Dependencies: T2.

### T4 — Scenario pins + report + ASK
Goal: run `barge-in-only` + `dump-only` + `watchdog`; write the report; ASK Julio.
Verification: barge-in → journal `barge_in: true` (+ TurnResumed/cancel if present) and the NEXT
turn does not re-ask answered things; dump-only → clamp behavior A/B (iter74 lane: `speech_filter
stage=clamp` lines; `9ccdccf` lane: the full dump spoken — either result is the evidence);
watchdog → exactly one reconnect (iter74 lane) or silent-but-alive (9ccdccf). CANCEL any test
booking. Report to
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter76-llm-mic-caller/01_report.md`.

## Validation Plan (end-to-end)
1. T1 probe 200/16k; T2 suite green; T3 happy call 6+ turns, waited gaps in the evidence timeline;
   T4 scenario pins recorded.
2. ZERO engine behavior code touched — the only engine-repo additions are the driver script + its
   tests, both non-invasive (suite green proves it).
3. The lane :8024 and everything Oregon stays untouched all session.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| Driving the OREGON :8090 lane | owner runs tests there — only if owner asks, same driver, different `--ws-url` |
| iter74-deployed lane A/B (clamp/similar/watchdog pins) | iter74 merge + lane deploy = owner-gated separately (branch ready @ `5ffcc67` on Helsinki) |
| Multi-persona voice battery (25 personas) | after Maria-v2 proves the shape |
| Oregon `agent/llm.json` TEMP-URL consolidation (127.0.0.1:8080) | pre-existing owner experiment; untouched |
