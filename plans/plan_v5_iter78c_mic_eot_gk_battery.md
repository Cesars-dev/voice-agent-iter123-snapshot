# plan_v5_iter78c_mic_eot_gk_battery — owner ear test + fake-caller room-tone fix + 5 GK mic battery

## Meta
- Date: 2026-09-25
- Project root: `/home/julio/projects/clean_diallux_SDR`
- Worktree: `/tmp/opencode/wt-iter78` on OREGON (branch `engine/iter78-merged-turn-yield`, tip `d8260c2`, pushed)
- Scope: ONE open question (is the mic-path re-ask loop an engine bug or a fake-caller artifact) +
  the 5-GK mic battery the owner asked for. Owner ear test = T0 discriminator. NO new branches —
  this work continues on `engine/iter78-merged-turn-yield` (owner-sanctioned).
- Status: PLAN ONLY (not started — T0 awaits owner)

## Compaction Context (fresh-agent handoff)
**Project:** Dialux SDR v5 voice engine (LangGraph + STT/LLM/TTS). Work box = **OREGON
5.78.83.174** (`ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`). Helsinki
46.62.233.228 = reference + Langfuse :3001. **OR main checkout = prod working tree — NEVER
checkout/switch/reset/pull there.** OR venv =
`/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` — run FROM the worktree cwd.
Worktree = `/tmp/opencode/wt-iter78` (branch `engine/iter78-merged-turn-yield` @ `d8260c2`,
pushed). pytest 9.1.1. Suite baseline = EXACTLY 3 known env-knob fails
(test_iter46_latency_floor, test_iter59_dedupe_semantic, test_iter60_audit_fixes) + all other
pins green. Lane :8025 = iter78 engine (pid `/tmp/opencode/voice_8025.pid` = 63177, log
`/tmp/opencode/voice_server_8025.log`, env `/tmp/opencode/wt-iter78/engine/.env`: ElevenLabs
Hannah agent voice, `TTS_YIELD_ON_QUESTION=true`, mic WS token-gated).
**VOICE LAW: preserve `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27` in any env edit. MODEL LAW:
gpt-5.4. LAW 0: no merges without owner say-so; docs → main.**

**iter78 main plan (DONE, chat plane):** commit 1 `05be69e` (iter70-T3 transition/flat-ack
directive lines REMOVED from the 4 state .md + llm.json byte-parity mirror; directive now ONLY
in the entry_lite post-history delta, owner wording) · commit 2 `d4fe473` (yield at the first
spoken "?", knob `TTS_YIELD_ON_QUESTION=true`; said-truth = history content + `last_spoken`
:= spoken bytes when yield fires; `turn_asked` post-filter → iter70 T3 beat intact) · `6001f53`
+ `746fbd8` (evidence json + owner-directed `--rag-fire-sim` default TRUE in the harness).
8 pins: `engine/tests/test_iter78_yield.py`. Live proof (chat harness, run `happy-iter78-or`):
4 calls ALL PASS, 0 gate rejections, 0 same-round post-"?" stacks, RAG matches iter77 base ref,
TTFT in band. Ledger + 60 SOP rows persisted. Report:
`/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md`.
**Owner ear test (main plan T5) = STILL PENDING — it is this plan's T0.**

**The open bug (this plan's reason to exist):** the iter76 fake-caller
`engine/scripts/llm_mic_caller.py` (cherry-picked `bf21983` + persona extension `d8260c2`)
smoke call NEVER left `state=Intake` — the agent re-asked "how many calls do you miss" ~10×
(turns 5-16) while the caller's Cartesia-synthesized answer ("Probably around 10 to 15 a
week…") streamed. Evidence in `/tmp/opencode/voice_server_8025.log` (2026-09-25 07:39-07:57
window): `eager turn started (speculative)` + `eot adopted running eager turn (no rerun)` +
`barge-in on call` + STT `StartOfTurn` churn. The UNMODIFIED iter76 driver reproduced the same
loop (first smoke, before any edit) → NOT caused by the iter78b edits. Hypothesis: the driver
sends **ZERO frames during its 5-15s human gaps** (real callers always send room-tone frames);
that digital silence + the engine's eager-EOT speculation (`DEEPGRAM_EAGER_EOT` machinery)
produce fragmentary `user_text` → re-ask loop. The chat harness (no audio) never hits it —
4 chat calls passed clean.

**Key paths/ids for the fresh agent:**
- Driver: `/tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py` — iter76 original +
  iter78b extension (`--persona NAME` loads `engine/tests/llm2llm/personas.py`,
  `--voice-id` caller-voice override, ear = driver-side Deepgram flux with idle-gap turn
  finalization + 3s silence-chunk keepalive + reconnect).
- Token staged at OR `/tmp/opencode/iter78_mic_token` (chmod 600; NEVER print it — read it
  into the shell: `TOKEN=$(cat /tmp/opencode/iter78_mic_token)`).
- Mic WS: `ws://127.0.0.1:8025/mic/ws?k=${TOKEN}` (token check at `diallux/app.py:245-250`).
- Personas: 5 GKs in `engine/tests/llm2llm/personas.py` — `Sam` (scam-skeptic, ≥4 exchange
  resistance), `Priya` (price-obsessed, ≥3), `Boris` (rushed), `Bianca` (burned-before, ≥3
  trust probes), `Dave` (status-quo, ≥3). All expect eventual BOOK.
- Smoke evidence: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/smoke_maria.json`
  (15 agent turns, stop=turn_cap_goodbye, Intake loop visible in the agent turns).
- iter78b plan (context): `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter78b_mic_caller_gk_stress.md`.
- PENDING_TASKS: `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` (PT-69 open →
  close at T4; PT rows for the mic-eot finding → add at T4).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| T0 = OWNER ear test on the mic page (real human, natural pauses) BEFORE any code change | The single discriminator: loop for a human = engine bug; clean = fake-caller artifact → room-tone fix path |
| If T0 CLEAN → engine innocent → T1 fixes the DRIVER (room-tone during gaps) | The engine's STT/EOT stack is the same one that works on the owner's real mic tests + prod :8026 |
| If T0 LOOPS → engine bug → env-knob FIRST: `DEEPGRAM_EAGER_EOT=false` in the worktree `.env`, lane restart, owner ear re-test | VOICE LAW knob-first; code change only if the knob fixes it |
| Driver fix = room-tone frames (not JSON keepalive) during `human_gap` | Zero-frame gaps are acoustically non-human; room-tone keeps the STT pipeline in its normal regime |
| GK battery runs ONLY after the loop is confirmed GONE (one clean smoke first) | Running GKs against a looping agent = garbage evidence |
| All work on `engine/iter78-merged-turn-yield`, commits + push via keyhound from the MAIN checkout cwd | Owner: "no branching, just cherry pick the code and add it here" (iter78b precedent) |
| Every booking created during GK runs gets CANCELLED + verified | Cal.com event 3801235 is REAL |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| T0 owner ear-test verdict (PASS/FAIL/UNCLEAR per probe) | owner, after the tunnel + mic page (probes in T0) |
| Optional distinct Cartesia CALLER voice id | owner (else env `CARTESIA_VOICE_ID` = Linda for both sides — accepted) |

## Environment & Dependencies
- Box: OREGON `root@5.78.83.174` via `ssh -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174`.
- Worktree: `/tmp/opencode/wt-iter78` @ `d8260c2`. Python:
  `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` from worktree cwd.
- Env: `/tmp/opencode/wt-iter78/engine/.env` (44 lines + `TTS_YIELD_ON_QUESTION=true`) — has
  `CARTESIA_API_KEY`, `CARTESIA_MODEL_ID`, `CARTESIA_VOICE_ID`, `DEEPGRAM_API_KEY`,
  `OPENAI_API_KEY`, `OPENAI_MODEL`, `VOICE_TEST_TOKEN`, `DEEPGRAM_EAGER_EOT`.
- Lane :8025 running (pid file `/tmp/opencode/voice_8025.pid`); restart command in Deploy Rules.
- Driver deps: `websockets`, `openai`, `audioop` (3.12 stdlib) — in the venv.
- Evidence dir (gitignored): `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/`.
- Ledger: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`
  via `/home/julio/projects/clean_diallux_SDR/scripts/live_sql.py` (+ `latency_pull.py`).

## Architecture (block diagram)
```
T0 owner ear test :8025 mic page  ──PASS──> driver guilty path
   │                                     T1: room-tone during human_gap
   └──LOOP──> engine path                  T2: clean smoke (no re-ask loop)
              (DEEPGRAM_EAGER_EOT knob)    T3: 5 GK battery (Sam,Priya,Boris,Bianca,Dave)
                                           T4: audit + bookings + closeout
fake caller: brain text -> Cartesia TTS (pcm_s16le 16k) -> WS /mic/ws -> engine
             engine agent TTS -> back over WS -> driver Deepgram ear -> evidence json
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| `/tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py` | T1 (driver path): `human_gap` + gap handling — stream low-amplitude room-tone (`zero_pcm` scaled) for the whole gap instead of sending nothing; keep the driver-side ear as-is | Edit |
| `/tmp/opencode/wt-iter78/engine/.env` | T0-FAIL path only: append `DEEPGRAM_EAGER_EOT=false` (preserve `CARTESIA_MODEL_ID=sonic-3.6-2026-08-27`) | Edit (conditional) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/02_mic_gk_report.md` | per-GK + smoke verdicts | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/gk_<P>.json` | per-GK evidence | New (gitignored) |
| `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md` | PT-69 → CLOSED; new PT row: mic eager-EOT ↔ fake-caller seam (verdict + fix) | Edit (docs → main) |
| `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/01_report.md` | append iter78c section | Edit (gitignored) |

## Deploy Rules
- Lane restart (only if needed / after an env change):
  `kill $(cat /tmp/opencode/voice_8025.pid); cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && setsid nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8025 </dev/null >> /tmp/opencode/voice_server_8025.log 2>&1 &` then `ss -tln | grep "127.0.0.1:8025 "` + `scripts/voice_preflight.py --url http://127.0.0.1:8025`.
- Suite gate: `cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q 2>&1 | tail -6` → exactly the 3 known env-knob fails.
- Push: `/home/julio/projects/clean_diallux_SDR/scripts/keyhound` from the MAIN checkout cwd,
  then `git push origin engine/iter78-merged-turn-yield` FROM the main checkout cwd (worktree
  `.git` is a file — credential helper breaks there).
- NEVER touch: OR prod `diallux.service` :8026 + `diallux-mic.service` :8090, OR :8001-8003,
  `/opt/diallux-production/.env`, Helsinki :8020/:8024, `CARTESIA_MODEL_ID` pin.

## Tasks (in order)

### T0 — OWNER EAR TEST (HITL gate)
Goal: discriminator — engine bug or fake-caller artifact.
1. Give the owner: tunnel command (`ssh -i <key> -N -L 8025:127.0.0.1:8025 root@5.78.83.174`)
   + URL `http://127.0.0.1:8025/mic?rate=1.0&k=<token>` (token from
   `/tmp/opencode/iter78_mic_token`, never print).
2. Probes (owner speaks as a REAL caller, natural pauses, mid-sentence pauses included):
   (a) answer the "how many calls" question with a deliberate mid-sentence pause — does the
   agent wait or re-ask/duplicate? (b) short ack ("yeah") — context kept? (c) any "? Perfect."
   / "? Absolutely —" glue after the agent's own question? (d) transition acks carry the next
   question naturally (iter70 T3 + iter78 delta)?
3. Verdict PASS = engine innocent → T1 (driver room-tone path). Verdict LOOP/FAIL = engine
   guilty → T1-knob path (`DEEPGRAM_EAGER_EOT=false`, lane restart, owner re-test).
Verification: owner's PASS/FAIL/UNCLEAR per probe recorded in `02_mic_gk_report.md`.

### T1 — Fix the confirmed guilty side
Goal: kill the re-ask loop.
- Driver path (T0 PASS): edit `/tmp/opencode/wt-iter78/engine/scripts/llm_mic_caller.py` —
  during `human_gap` (and before the goodbye wait), stream room-tone = `zero_pcm(gap_s)` scaled
  to a low amplitude (e.g. multiply samples by ~0.005, keep DC ≈ 0) via the SAME `MicDriver`
  stream loop, so the engine's STT sees a live-but-quiet line instead of a dead one. Keep the
  driver's other behavior unchanged.
- Engine path (T0 FAIL): append `DEEPGRAM_EAGER_EOT=false` to
  `/tmp/opencode/wt-iter78/engine/.env` (AFTER confirming `CARTESIA_MODEL_ID` intact), restart
  the lane, owner re-test. Code change ONLY if the knob proves it and the owner asks.
Verification: `pytest tests/test_iter76_llm_mic_caller.py -q` green (driver path); lane log
shows NO `barge-in` churn during gaps; the specific re-ask loop gone.

### T2 — Clean smoke (Maria prompt, real mic path)
Goal: one full conversational call with NO re-ask loop.
Commands:
```
TOKEN=$(cat /tmp/opencode/iter78_mic_token)
cd /tmp/opencode/wt-iter78/engine && set -a && . ./.env && set +a
/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/llm_mic_caller.py \
  --ws-url "ws://127.0.0.1:8025/mic/ws?k=${TOKEN}" --scenario happy \
  --max-caller-turns 12 --out /home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/smoke_maria2.json
```
Verification: `agent_turns` ≥ 8; the state chain in the lane log (`grep -o "turn=[0-9]* state=[A-Za-z]*" /tmp/opencode/voice_server_8025.log | tail -20`) PROGRESSES past Intake (Discovery/Closer/Offer/contact_details/ConfirmSlots appear); agent turns contain NO consecutive same-question re-asks; `stage=yield` lines only when the model actually stacks. THEN cancel any booking created.

### T3 — The 5 GK battery (owner's ask)
Goal: gatekeeper resistance through the REAL audio path, iter78 fixes proven live.
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
Verification per run: evidence json written, state chain progresses, agent turns clean of
same-question re-ask loops; watch `tail -f /tmp/opencode/voice_server_8025.log | grep speech_filter`
live; watch for `stage=yield` hits (the yield firing on a REAL path = proof it works as a backstop).

### T4 — Audit + bookings + closeout
1. Read all `gk_*.json` + `smoke_maria2.json`: per persona, note the conversation arc, whether
   the persona's resistance was honored, any yield cuts, any re-ask loops. Expect bookings from
   most GKs (they eventually book) → CANCEL EVERY test booking (Cal.com event 3801235 REAL)
   and verify none remain.
2. Ledger: `scripts/live_sql.py import --window "HH:MM-HH:MM" --run gk-iter78-mic --commit <sha>`
   (Langfuse traces from the :8025 lane) + `latency_pull.py --run gk-iter78-mic`.
3. Write `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter78-merged-turn-yield/02_mic_gk_report.md`
   (table first: per-GK verdict; then summary; then quotes). Append the iter78c section to `01_report.md`.
4. `/home/julio/projects/clean_diallux_SDR/plans/PENDING_TASKS.md`: PT-69 → CLOSED (iter78
   chat-plane + mic-plane evidence); add the mic-eot-seam PT row with the T0 verdict + fix.
5. Commit the driver fix (if changed) on the branch; push via keyhound from main checkout cwd;
   docs → main via a dedicated main worktree; ASK owner before any merge (LAW 0).

## Validation Plan (end-to-end)
1. T0 verdict recorded → the guilty side identified and fixed.
2. Clean smoke: state chain progresses past Intake; zero re-ask loops; no orphan booking.
3. 5 GK runs: personas honored, state chains progress, zero same-question loops, bookings
   cancelled; `stage=yield` fired only on real stacks.
4. Ledger rows persisted; PENDING_TASKS updated; branch pushed; owner briefed.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| barge-in / dump / watchdog audio scenarios on GK personas | owner asked for the 5 GKs; separate probes |
| iter76 branch merge | LAW 0 — owner-gated |
| iter78 main-plan merge to main | LAW 0 — owner say-so only |
| iter71 ack-latency options | queued separately (owner picks) |
