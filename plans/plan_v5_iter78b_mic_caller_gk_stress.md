# plan_v5_iter78b_mic_caller_gk_stress — cherry-pick iter76 Cartesia mic-caller + run the 5 GK stress personas live on the iter78 lane

## Meta
- Date: 2026-09-25
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Worktree: `/tmp/opencode/wt-iter78` (branch `engine/iter78-merged-turn-yield`, pushed tip `746fbd8`)
- Scope: cherry-pick `24991b8` (iter76 T2 LLM mic caller) onto the CURRENT branch (owner:
  "no branching, just cherry pick the code and add it here"), make the caller persona
  pluggable, smoke it, then run the 5 GK stress personas (Sam, Priya, Boris, Bianca, Dave)
  over the REAL mic WS with a Cartesia-synthesized caller voice — prove the iter78 fixes
  (yield + said-truth + entry_lite delta) hold on the real-audio path.
- Status: IN PROGRESS (owner directive received 2026-09-25 — "no branching, just cherry
  pick the code and add it here, lets use cartesia and run a fake test… run the 5GK's of
  the stress test… on a new session per new plan SOP")

## Compaction Context
**Project:** Dialux SDR v5 voice engine (LangGraph + STT/LLM/TTS), repo
`/home/julio/projects/clean_diallux_SDR`. Work box = **OREGON 5.78.83.174**
(`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`). Helsinki 46.62.233.228 =
reference + Langfuse :3001. **OR main checkout = prod working tree — never
checkout/switch/reset/pull there.** OR venv =
`/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` — run FROM the worktree cwd.

**iter78 branch state (all pushed to origin):** `05be69e` (T2: iter70-T3 transition/flat-ack
directive lines REMOVED from `Closer/Discovery/Offer/Intake.md` + `agent/llm.json` byte-parity
mirror; directive = owner wording, now ONLY in the entry_lite post-history delta
`builder.py` ~2260-2269) · `d4fe473` (T3: yield at the first spoken "?",
knob `TTS_YIELD_ON_QUESTION=true` default-on; said-truth = history content + `last_spoken`
:= spoken bytes when yield fires; `turn_asked` post-filter → iter70 T3 beat untouched) ·
`6001f53` (evidence json) · `746fbd8` (T4.1 owner directive: `--rag-fire-sim` default TRUE in
the harness, `--no-rag-fire-sim` opt-out). Suite = exactly 3 known env-knob fails + 8 iter78
pins green (`engine/tests/test_iter78_yield.py`). Lane :8025 serves iter78 (pid file
`/tmp/opencode/voice_8025.pid` = 63177, log `/tmp/opencode/voice_server_8025.log`, env
`/tmp/opencode/wt-iter78/engine/.env` — ElevenLabs Hannah agent voice, mic WS token-gated via
`VOICE_TEST_TOKEN`). **VOICE LAW: preserve `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` in any env
edit. MODEL LAW: gpt-5.4.**

**Proven this session (T4 live proof, run `happy-iter78-or`, ledger + 60 SOP rows persisted):**
4 chat-harness calls (Maria ×3 + Danny) ALL PASS, booked, 0 gate rejections, 0 same-round
post-"?" stacks; yield cut + said-truth PROVEN by repro; RAG firesim plane matches the
iter77 base ref (0 empty queries, ~85% served); TTFT in band; all bookings = mock UID
`qeTqHuZ1EDzH8bxEdhPQ6H` (fixture). Report:
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md`.

**The iter76 mic caller (source of the cherry-pick):** commit `24991b8` on branch
`engine/iter76-llm-mic-caller` — `engine/scripts/llm_mic_caller.py` (501 lines) +
`engine/tests/test_iter76_llm_mic_caller.py` (86 lines). Standalone (zero diallux imports):
Cartesia caller TTS (`CARTESIA_API_KEY`/`CARTESIA_MODEL_ID`/`CARTESIA_VOICE_ID`, raw
pcm_s16le 16k), driver-side Deepgram flux ear (`DEEPGRAM_API_KEY`) listening to AGENT audio,
caller brain = OpenAI (`OPENAI_API_KEY`, model `--caller-model` or env `OPENAI_MODEL`,
default gpt-5.4, `max_completion_tokens=200`), human pacing (agent-idle turn-end + 5-15s gaps
with NO frames during the wait), connects to `ws://…/mic/ws?k=<VOICE_TEST_TOKEN>` (token in
the ws URL query; evidence json redacts it). Scenarios: happy / barge-in-only / dump-only /
watchdog. The happy loop has Maria-v2-specific scripted beats (DUMP_QUESTIONS, REPEAT_PHRASE,
GOODBYE_PHRASE, BOOKED_HINTS early-goodbye) + hardcoded `PERSONA_PROMPT`.

**Owner directive (verbatim intent, 2026-09-25):** cherry-pick the driver onto iter78, run
fake calls with it (Cartesia caller voice) to SEE IF THE PROBLEMS ARE GONE, and run the
**5 GK stress personas** (gatekeepers: Sam, Priya, Boris, Bianca, Dave from
`engine/tests/llm2llm/personas.py`). New plan file per the new-plan SOP (this file).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Cherry-pick `24991b8` onto `engine/iter78-merged-turn-yield` (NO new branch) | Owner: "no branching, just cherry pick the code and add it here" (owner say-so overrides the branch-stacking default) |
| Extend the driver, NOT rewrite: add `--persona NAME` that loads the persona `system` from `engine/tests/llm2llm/personas.py` and appends the driver's generic PACING RULES block | The 5 GK personas exist as caller-LLM system prompts in that registry; pacing rules are audio-transport constraints, persona-agnostic |
| Under `--persona`, the Maria-v2 scripted beats (DUMP_QUESTIONS / REPEAT_PHRASE / GOODBYE_PHRASE text + BOOKED_HINTS early-goodbye) are DISABLED — brain-only replies, goodbye GENERATED by the brain at turn cap or when the persona's goal is complete | Those beats are Maria's hardcoded lines; a price-obsessed Priya or status-quo Dave must speak from their OWN prompt, not Maria's lines |
| Generic directive in persona mode: "reply in one short burst, pursue the goal stated in your persona, never invent outcomes, never mention being an AI or a test" | Keeps driver mechanics; persona system prompt carries the goal |
| `--voice-id` optional arg (default = env `CARTESIA_VOICE_ID`) | Lets the owner swap the caller voice later without an env edit; today caller voice = Linda = agent voice (accepted for stress runs; ear attribution handled by the driver's journal timing) |
| Scenario `happy` for all 5 GK runs (conversational loop, persona prompt steers behavior) | The GK behavior lives in their system prompts; audio-behavior scenarios (barge-in/dump/watchdog) are separate probes, not in scope |
| Every booking created by the GK runs on :8025 gets CANCELLED after the battery (Cal.com event 3801235 is REAL) | iter77 lesson — the lane hits real Cal.com |
| Smoke test FIRST (suite pins + one Maria-prompt happy run), THEN the GK battery | Owner: "smke testthe code and run it here" |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Distinct Cartesia CALLER voice id (optional — Linda default) | owner, or `engine/scripts/list_cartesia_voices.py`; run proceeds with env voice without it |

## Environment & Dependencies
- Box: OREGON `root@5.78.83.174` via `ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`.
- Worktree: `/tmp/opencode/wt-iter78` (branch `engine/iter78-merged-turn-yield` @ `746fbd8`).
- Python: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` FROM worktree cwd.
- Env: `/tmp/opencode/wt-iter78/engine/.env` — has `CARTESIA_API_KEY`, `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27`, `CARTESIA_VOICE_ID`, `DEEPGRAM_API_KEY`, `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-5.4`, `VOICE_TEST_TOKEN`.
- Driver deps: `websockets`, `openai`, `audioop` (3.12 stdlib), requests — all present in the venv (driver ran on iter76).
- Lane: :8025 mic WS `ws://127.0.0.1:8025/mic/ws?k=<VOICE_TEST_TOKEN>` (token at `/tmp/opencode/iter78_mic_token` on OR, root:600 — NEVER printed).
- Persona registry: `/tmp/opencode/wt-iter78/engine/tests/llm2llm/personas.py` — 5 GKs: `Sam`, `Priya`, `Boris`, `Bianca`, `Dave` (trace_name style: `(GK) Sam — scam-skeptic contractor` etc.; driver loads by matching the short name).
- Evidence (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/` — mic-caller jsons land as `gk_<name>.json`.

## Architecture (block diagram)
```
llm_mic_caller.py (--persona Sam --scenario happy)
  persona system (personas.py) + PACING RULES -> CallerBrain (gpt-5.4)
  brain text -> CartesiaCallerTTS synth (Cartesia, pcm_s16le 16k)
    -> MicDriver.stream_pcm -> WS /mic/ws?k=<token>  (16-bit PCM 16k mono, real mic path)
       -> engine :8025 (STT eager EOT -> graph rounds -> iter78 yield/said-truth)
          -> agent TTS audio back over WS
  AgentEar (Deepgram) transcribes AGENT audio -> agent_turns evidence json
  pacing: wait agent-idle 1.5s + human_gap 5-15s (no frames during gap)
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py` | cherry-picked, THEN extended: `--persona NAME` (registry load + pacing block), `--voice-id` override, persona-mode beats disabled | Edit |
| `/tmp/opencode/wt-iter78/engine/tests/test_iter76_llm_mic_caller.py` | cherry-picked verbatim (86 lines, suite pins) | New (via cherry-pick) |
| `/tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py` persona-registry import | `--persona` reads `tests/llm2llm/personas.py` via importlib from the engine root (driver stays standalone when `--persona` is unused) | Edit |
| `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter78b_mic_caller_gk_stress.md` | this plan | New |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/gk_*.json` | per-persona evidence | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-69 row + fire-sim lesson (docs → main at closeout) | Edit (T6) |

## Deploy Rules
- All work ON OREGON in `/tmp/opencode/wt-iter78`; suite via main venv from worktree cwd:
  `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q 2>&1 | tail -6` — expect exactly the 3 known env-knob fails.
- Lane :8025 already serves iter78 — if it is down: `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && setsid nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8025 </dev/null >> /tmp/opencode/voice_server_8025.log 2>&1 &` then `ss -tln | grep 8025`.
- Push trap: run `/home/julio/projects/clean_diallux_SDR/scripts/keyhound` from the MAIN checkout cwd, then `git push origin engine/iter78-merged-turn-yield` FROM the main checkout cwd (worktree `.git` is a file — credential helper breaks there).
- NEVER touch: OR prod `diallux.service` :8026 + `diallux-mic.service` :8090, OR :8001-8003, `/opt/diallux-production/.env`, Helsinki :8020/:8024, `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` in any env edit.

## Tasks (in order)

### T1 — Cherry-pick `24991b8`
Goal: driver + its test on the iter78 branch, no conflicts (new files only).
Commands:
```
ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 'cd /tmp/opencode/wt-iter78 && git cherry-pick 24991b8 && git log --oneline -1'
```
Verification: `ls /tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py /tmp/opencode/wt-iter78/engine/tests/test_iter76_llm_mic_caller.py` both exist; `pytest tests/test_iter76_llm_mic_caller.py -q` green.

### T2 — Persona extension (driver edit)
Goal: run ANY registry persona over the mic path.
Edits in `/tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py`:
1. `build_parser()`: add `--persona` (default "") + `--voice-id` (default "").
2. `main_async()`: if `--voice-id` non-empty, use it instead of env `CARTESIA_VOICE_ID` (model/key stay env — VOICE LAW pin preserved).
3. `--persona NAME`: import `tests/llm2llm/personas.py` (importlib from the engine root), find the persona whose name contains NAME (case-insensitive), build prompt = `persona["system"]` + "\n\n" + PACING_RULES (the generic pacing block only). Fail fast with the available GK names if not found.
4. `CallerBrain.reply()`: accept the prompt as a parameter (persona prompt in persona mode, PERSONA_PROMPT default).
5. In persona mode, `run_happy`: skip the DUMP/REPEAT scripted beats and the BOOKED_HINTS early-goodbye; directive = "Reply in one short burst (1-2 short sentences), pursuing the goal stated in your persona. Never invent outcomes. Never mention being an AI or a test."; at turn cap or when the persona prompt's goal is met, ask the brain for a natural goodbye (directive "wrap up and end the call naturally, one short sentence").
Verification: `pytest tests/test_iter76_llm_mic_caller.py -q` still green; `--help` shows both args; a 1-line dry check `--persona Priya` prints the persona found (no call).

### T3 — Smoke test (Cartesia, real mic path)
Goal: one full conversational fake call through the REAL mic WS.
Commands (worktree env, token substituted — value never printed):
```
TOKEN=$(cat /tmp/opencode/iter78_mic_token)
cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a
/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/llm_mic_caller.py \
  --ws-url "ws://127.0.0.1:8025/mic/ws?k=${TOKEN}" --scenario happy \
  --max-caller-turns 12 --out /home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/smoke_maria.json
```
Verification: evidence json has `agent_turns` ≥ 3, `caller_turns` ≥ 2, `stop_reason` in {booked_goodbye, turn_cap_goodbye}; agent transcript in `agent_turns` shows NO second sentence after a spoken "?" (manual read of the evidence turns + `grep -c "stage=yield" /tmp/opencode/voice_server_8025.log` for the window).

### T4 — The 5 GK stress personas (Cartesia, real mic path)
Goal: the owner's ask — gatekeeper resistance through the REAL audio path.
Personas: `Sam`, `Priya`, `Boris`, `Bianca`, `Dave` — one run each, sequential:
```
TOKEN=$(cat /tmp/opencode/iter78_mic_token)
cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a
for P in Sam Priya Boris Bianca Dave; do
  /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/llm_mic_caller.py \
    --ws-url "ws://127.0.0.1:8025/mic/ws?k=${TOKEN}" --scenario happy --persona "$P" \
    --max-caller-turns 14 \
    --out "/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/gk_${P}.json"
done
```
Verification per run: evidence json written, `agent_turns` ≥ 5, stop_reason present; lane log watched live (`tail -f /tmp/opencode/voice_server_8025.log | grep "speech_filter"`) for `stage=yield` when the model stacks.

### T5 — Audit + bookings cleanup
Goal: the problems are GONE on the real path.
1. For each `gk_*.json` + the smoke json: read `agent_turns` — assert no round has a second sentence after its first spoken "?" (yield-rule); note any `stage=yield` hits in the lane log window.
2. Ledger: `scripts/live_sql.py import --window <HH:MM-HH:MM> --run gk-iter78-mic --commit <sha>` (only if Langfuse traces landed for the mic lane rounds).
3. Bookings: check every GK run for a real booking (Cal.com event 3801235 REAL) — `scripts/voice_preflight.py` won't do it; use the slots endpoint `http://127.0.0.1:8001/` shape per `docs/api/` or the engine json — CANCEL every test booking and verify none remain.
Verification: zero post-"?" stacks across 6 runs; bookings cancelled; verdict per persona in the report.

### T6 — Closeout
1. Append results to `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md` (new section "T4b — mic-caller GK stress").
2. `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md`: PT-69 → CLOSED (iter78); new row: harness fire-sim default-on (done this branch); mic-caller GK evidence row.
3. Commit the driver extension + plan file on the branch; docs → main via a dedicated main worktree (NEVER `push origin HEAD:main` from an iteration branch); ASK owner before any merge (LAW 0).

## Validation Plan (end-to-end)
1. Cherry-pick clean; test_iter76 pins green on the branch.
2. Smoke run: agent turns transcribed by the Deepgram ear; conversation flows; no crash; `stop_reason` sane.
3. 5 GK runs: all personas heard and answered, resistance honored (Sam scam-probes ≥4 exchanges, Priya price pushback ≥3, Boris rushed, Bianca trust probes, Dave status-quo), zero post-"?" same-round stacks in the agent turns, `stage=yield` lines only when the model stacks.
4. No orphan test bookings on Cal.com event 3801235.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| barge-in / dump / watchdog audio scenarios on the GK personas | owner asked for the 5 GKs; audio scenarios are separate probes |
| Distinct caller voice (Cartesia voice id) | optional override arg exists; owner supplies id when wanted |
| iter76 branch merge into anything | separate branch — owner-gated (LAW 0); cherry-pick = code reuse, not merge |
| iter78 owner ear test (T5 of the main plan) | still pending owner; runs in parallel with this work on the same lane — NOT concurrent (lane is single-tenant) |
