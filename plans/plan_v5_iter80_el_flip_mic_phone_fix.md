# plan_v5_iter80_el_flip_mic_phone_fix — ground-zero = iter65 @ 031bb73; provider=ElevenLabs, HTML rate knob, mic phone-number re-ask fix

## Meta
- Date: 2026-09-26
- Project root (OREGON box): `/home/julio/projects/clean_diallux_SDR` ON `root@5.78.83.174` — ALL commands run through
  `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "cd /home/julio/projects/clean_diallux_SDR && <cmd>"`.
  Local Helsinki box is reference ONLY this iteration (owner: "work Oregon only").
- Scope: THREE surgical changes on ONE new branch, ground zero = merged stable `031bb73` (iter65 model-defaults):
  1. Provider flip to ElevenLabs (EL adapter already in the tree — env-level switch + prewarm protocol-match already present at this base).
  2. Port the browser rate knob (iter73 `8c5f72f` — one file, 2 lines, HTML only).
  3. Mic phone-number re-ask fix (chat lane has number fallback capture; mic lane does not).
- Status: PLAN ONLY (not started — awaits owner approval of T-file sketches)

## Compaction Context
(owner-approved session summary, 2026-09-25/26)

**Project:** Dialux SDR v5 voice engine (LangGraph + Deepgram STT + LLM + TTS), repo
`/home/julio/projects/clean_diallux_SDR`. Two boxes: Helsinki `46.62.233.228` (user julio; reference +
live services) and OREGON work box `5.78.83.174` (root, key `~/.ssh/id_ed25519_hetznor`; prod working
tree — NEVER git checkout/switch/reset/pull on its main checkout; hostname `ubuntu-4gb-hil-1`).

**Merge history (main code-merges ONLY, verified via first-parent merges):** exactly 4 —
`4559a33` MVP-Finally (2026-09-16), `40b3b40` iter52→64c ladder, `84fd1ce` iter66 ElevenLabs cutover,
`50a453f` iter65 model-defaults (2026-09-22 23:58). Main tip docs chain ends `5410303` (NUMBERING LAW:
iterNN increments ONLY on main-pipeline engine code; docs/plans ride current NN).

**iter65 @ `031bb73` facts (verified on OREGON):** suite 451 pass / 0 fail; battery 4/4 BOOK; TTS default
**cartesia** (`diallux/config.py:356` `tts_provider="cartesia"`, sonic-3.6, Linda `829ccd10-...`);
ElevenLabs adapter FULLY in tree (`engine/diallux/media/elevenlabs_tts.py`, `tts_factory.py`,
`config.py` + `.env.example` EL block with owner-pinned prod voice Sarah `uG1JFy6xppqckhHCs2KG`
turbo_v2_5 speed 1.06 stability 0.5 style 1.0) — merge ≠ flip (T7 owner-gated, never flipped);
media prewarm has EL branch (`media/prewarm.py:101` at this tree). Keepalive landmine present
(httpx default 5s; one-variable fix = iter75 `858543c` `keepalive_expiry=600`).
`rac/retrieval` on the 4 chat batteries = hybrid, healthy (served 98%, await p50 0ms, query_empty 0%,
pin 89%; land/degraded flag FAIL = PT-59 ledger-import artifact only — RAG needs NO work).

**Bugs (evidence ledger `research/surgeon/iter48-rag-truth/ledger.db`, mic run `mic-20260923-ccacb090`,
40 turns, trace `fb08761939f0d6f11e6eaa33b697d831`, branch iter65-model-defaults @ `fc45536`):**
mic lane re-ask loop: "best number" asked 6 turns verbatim, last name 3 turns, history grows 8349→9472
chars with zero capture; later root-caused (iter79 T1 @ `8b88bb6`) = checkpointed `pause_reask` bool
leaks turn-to-turn. Chat lane does NOT have this bug — chat has number fallback capture mic lacks.
`05_mic_call_report.md` was never synced; RECONSTRUCTED 2026-09-26 on OREGON from ledger (done).

**Winner-branch decision (owner):** fix from stable iter65 base, no iter66+ speech-flow architecture;
cadence = edit → smoke test → next edit; cheap model during mic smoke tests (deep lane windowed).

**Never changed in this plan (untouched):** RAG (`rag.py`, `kbs/`), state machine graph, PROMPTS (prompts/*.md
are source of truth — 05be69e trimmed state-prompt directives at LATER commits, not in 031bb73), production
agents `agent_16985b5d087e56c35141983396` / `agent_87e4d5f08475e5bc558b2f390f`, validator `:8003`,
cal_slots `:8001`, time `:8002`, Caddy, Cal.com event 3801235 (real — mock slots ONLY),
Cal.com `Z` time format (use `+00:00`).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Base branch ref = `031bb73` (iter65 model-defaults) | stable: suite 451 green, battery 4/4, all changes single-knob rollback; prewarm EL branch already present |
| Branch name = `engine/iter80-el-flip-mic-phone-fix` | next main-pipeline iterNN = 80 (last pipeline change = 79) |
| Branch is CUT by creating a ref, NOT by checking out | OREGON main checkout is prod — `git branch <name> 031bb73` + worktree under `/tmp/opencode/wt-iter80` |
| Rate knob = PORT `8c5f72f` diff (2 lines into `engine/diallux/static/mic/index.html`), not cherry-pick commit | HTML-only; port survives even if context lines drift; TTS-side speed pin stays authoritative |
| Keepalive 600s port (iter75 `858543c`, one variable in `engine/diallux/graph/llm.py`) rides this branch | removes iter65's carry-in turn-1 TLS landmine before smoke tests measure EL turn-1 |
| EL flip via lane `.env` `TTS_PROVIDER=elevenlabs` + EL block uncommented; code default stays `cartesia` in `config.py` | merge ≠ flip law kept intact in git; prod rollout remains owner-gated |
| Cheap model for smoke tests: `OPENAI_MODEL=gpt52-mini-equivalent CHEAP UNKNOWN — must be obtained from .env candidates` (see BLOCKED table) | mic smokes must not burn deep-window tokens during end-to-end test loops |
| Smoke = iterate on :8026 lane (new worktree uvicorn, `127.0.0.1` bind, foreground) | does not touch lanes :8000/:8021/8022/8024/:8025; no systemd, no Caddy |
| One commit per change (provider-flip-commit, rate-knob-commit, mic-fix-commit) after its smoke gate | edit→test→commit→next, per owner cadence |

## BLOCKED / NEEDS INPUT
| Item | Where to get it |
|---|---|
| Exact cheap-model id for smoke lane | owner (candidates seen in repo: `gpt-5.2`; iter65 sweep used gpt-5.2→5.4; confirm id string for proxy) |
| Chat-lane number fallback capture location (function name) | grep `engine/diallux/builder.py` + `engine/diallux/media/normalize.py` + llm.json `response_variables` on branch — audit in T1 and pin result in T3 before coding |
| EL `ELEVENLABS_API_KEY` value | OREGON lane `.env` (gitignored — never print) |
| Whether OREGON lane :8026 is free | check `ss -ltnp | grep :8026` before first smoke |

## Environment & Dependencies
- OREGON: host `root@5.78.83.174`, ssh key `/home/julio/.ssh/id_ed25519_hetznor` (from Helsinki box).
- Repo french on OREGON: `/home/julio/projects/clean_diallux_SDR`; worktree for this iteration:
  `/tmp/opencode/wt-iter80` (created ON OREGON via `git worktree add`).
- Python/venv on OREGON: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python` (suite 451 = pytest, pinned requirements in `engine/requirements.txt`; fastembed==0.8.0 pinned).
- Ports on OREGON lane: cal_slots `:8001`, time `:8002`, validator `:8003` (systemd, untouched); engine lane for THIS branch = `:8026` fresh uvicorn run from worktree.
- Langfuse on OREGON: runs `http://46.62.233.228:3001` (set in `.env`, fail-safe if unreachable).
- Bedrock for mic smoke: mic WS path `/ws/mic` on :8026 (browser page = `engine/diallux/static/mic/index.html`).

## Architecture (one block diagram)
```
caller (mic WS :8026) ──► builder.py graph rounds (state machine UNTOUCHED)
                                 │
                                 ├─ STT: Deepgram flux (pool prewarm unchanged)
                                 ├─ LLM: OpenAI gpt-5.4 / SMOKE=CHEAP_MODEL (graph/llm.py, shared pool, keepalive 600 after T-port)
                                 └─ TTS: tts_factory → elevenlabs_tts.py (EL AT THIS BASE)  [TTS_PROVIDER=elevenlabs]
browser page static/mic/index.html  [rate knob ?rate= 0.80–1.15 — HTML only]
```

## File Map
| File (absolute path) | What changes | New/Edit/Delete |
|---|---|---|
| OREGON `/home/julio/projects/clean_diallux_SDR` + `/tmp/opencode/wt-iter80` (worktree on OREGON) | branch ref + worktree from `031bb73` | New |
| `/tmp/opencode/wt-iter80/engine/diallux/static/mic/index.html` | insert RATE read + 2-line port of `8c5f72f` (`src.playbackRate.value = RATE`, `playhead = at + buf.duration / RATE`) | Edit |
| `/tmp/opencode/wt-iter80/engine/diallux/graph/llm.py` | port iter75 `858543c`: `keepalive_expiry=600` into `httpx.Limits` of `_SHARED_HTTP` | Edit |
| `/tmp/opencode/wt-iter80/engine/.env` (LANE ONLY, gitignored) | `TTS_PROVIDER=elevenlabs`, EL block uncommented (Sarah pin), `OPENAI_MODEL=<CHEAP>` for smokes | Edit |
| OREGON `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter80-el-flip-mic-phone-fix/` smoke evidence | transcripts + SOP rows per change | New |
| `/tmp/opencode/wt-iter80/engine/diallux/<file located in T1 audit>` | mic phone-number fallback capture (SINGLE file expected — pin location from T1 before editing) | Edit (after T1 audit) |
| OREGON `/home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter80_el_flip_mic_phone_fix.md` | THIS plan | New |

## Deploy Rules
- NEVER `git checkout`/`switch`/`reset`/`pull` inside `/home/julio/projects/clean_diallux_SDR` on OREGON (prod working tree). The branch exists as ref; all code edits happen in the worktree `/tmp/opencode/wt-iter80`.
- Run lane: foreground uvicorn from worktree venv, `127.0.0.1:8026`, `--port 8026`, kill pid per session; NEVER systemd / Caddy / existing lanes.
- LLM edits: NEVER modify an existing production LLM; cheap model = temporary `.env` override on the lane only, reverted after T4.
- Push/merge: NOT in this plan (LAW 0 — owner say-so at the end only).

## Tasks (in order)

### T1 — cut branch + worktree + audit
Goal: branch exists as OREGON ref; worktree checked out; chat-lane number-capture location identified and pinned in the plan margin.
Files: branch ref `engine/iter80-el-flip-mic-phone-fix`; worktree `/tmp/opencode/wt-iter80`.
Commands (full):
1. `ssh -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "cd /home/julio/projects/clean_diallux_SDR && git branch engine/iter80-el-flip-mic-phone-fix 031bb73"`
2. Same ssh: `git worktree add /tmp/opencode/wt-iter80 engine/iter80-el-flip-mic-phone-fix`
3. Same ssh: `grep -n -A6 'pause_reask\\|best number\\|best_number' /tmp/opencode/wt-iter80/engine/diallux/builder.py /tmp/opencode/wt-iter80/engine/diallux/media/normalize.py | head -60`
Dependencies: none.
Verification: `git -C /home/julio/projects/clean_diallux_SDR rev-parse engine/iter80-el-flip-mic-phone-fix` == `031bb73...`; worktree `git -C /tmp/opencode/wt-iter80 log -1 --oneline` == `031bb73`; audit grep output pasted into this plan's margin before T3 starts.

### T2 — keepalive 600 port (one variable)
Goal: `engine/diallux/graph/llm.py` `_SHARED_HTTP` uses `keepalive_expiry=600`.
Files: `/tmp/opencode/wt-iter80/engine/diallux/graph/llm.py`.
Commands (full): edit in worktree: `_SHARED_HTTP = httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=600.0, write=600.0, pool=600.0), limits=httpx.Limits(keepalive_expiry=600.0))`; commit message `iter80 T2: shared pool keepalive_expiry=600 (iter75 858543c port — iter65 T1 carried httpx default 5s; turn-1 paid fresh TLS)`.
Dependencies: T1.
Verification: `grep -n keepalive_expiry` shows 600; T2 smoke: boot lane without T2-`/health` gate change — hit `curl -s 127.0.0.1:8026/health | jq .llm_prewarm` → `true`; TTFT observed in evidence, no failure permitted.

### T3 — ElevenLabs flip (lane env, adapter preflight)
Goal: lane speaks EL with Sarah pin; prewarm matches provider branch.
Files: OREGON worktree `/tmp/opencode/wt-iter80/engine/.env` (+ `llm.json` NOT touched; config default untouched in git).
Commands (full): edit `.env` keys: `TTS_PROVIDER=elevenlabs`, `ELEVENLABS_API_KEY=<from .env>`, `ELEVENLABS_VOICE_ID=uG1JFy6xppqckhHCs2KG`, `ELEVENLABS_MODEL_ID=eleven_turbo_v2_5`, `ELEVENLABS_INACTIVITY_TIMEOUT=180`, `ELEVENLABS_STABILITY=0.5`, `ELEVENLABS_SIMILARITY_BOOST=0.75`, `ELEVENLABS_STYLE=1.0`, `ELEVENLABS_SPEED=1.06`; run `cd /tmp/opencode/wt-iter80/engine && .venv/bin/python -m pytest tests/test_iter66_elevenlabs_cutover.py -x -q` (MERGED pins expected green on this base).
Dependencies: T2. Run suite whole: `.venv/bin/python -m pytest -q` → status ?? UNKNOWN — must be obtained from worktree run evidence; doc gate should equal suite 451+12 EL pins base behavior.
Verification: EL smoke page — mic smoke 10 agent turns all voiced by EL (Sara ear check by owner) on :8026 with `TTS_PROVIDER=elevenlabs`; log shows `tts_provider` resolved EL; no stray Cartesia socket in `prewarm` logs; operator may ask live ear test after.

### T4 — HTML rate knob (2-line port; commit even before pea)
Goal: browser playback-rate knob present on :8026 mic page.
Files: `/tmp/opencode/wt-iter80/engine/diallux/static/mic/index.html`.
Commands (full): apply exactly 2-line port of diff from `8c5f72f` via `git show 8c5f72f -- engine/diallux/static/mic/index.html` as reference, then edit lines (insert at bufferSource creation site around the `for (let i...` block); ALSO add the `?rate=` clamp block (reads `RATE` 0.80–1.15) verbatim from `git show 8c5f72f:engine/diallux/static/mic/index.html | grep -n -B3 -A3 'RATE'`.
Dependencies: T3 (lane live on :8026), owner optional ear test.
Verification: page GET `http://127.0.0.1:8026/diallux/static/mic/index.html?rate=0.93` and console prints `RATE 0.93`; audio plays at roughly 0.93× with playhead math consistent (no double-speed drift; multiple buffers keep gapless per 8c5f72f note).
Commit: `iter80 T4: browser rate knob port (iter73 8c5f72f 2-line HTML-only port; TTS-side speed pin authoritative; zero added latency)`.

### T5 — mic phone-number re-ask fix (THE bug)
Goal: on mic lane, when caller says a number that is NOT the best one ("that's my landline / not the best number"), engine captures fallback number like chat lane does; re-ask loop gone (≤2 asks).
Files: file Pinned in T1 margin; worktree copy.
Commands (full): FIRST run T1 step 3 grep verbatim and paste; then implement the MINIMAL port: copy the exact fallback mechanism that chat lane has (grep ORT in ledger that chat battery captured Danny/Susan number fine while mic did not — evidence = `chat-iter65-happy` t33-40 clean vs ledger mic `mic-20260923-ccacb090` 6-turn loop) — expected location per compaction: `engine/diallux/builder.py` post-history delta logic + (Possibly) `pause_reask` flag turn-scoping from iter79 `8b88bb6` (port ONLY the turn-scope bool reset + ingest-clear-on-caller-text, NOT the speech-flow cushion).
Dependencies: T1 (audit), T3/T4 lane live.
Verification (Event): smoke script ON OREGON: intent-say capture: run micbridge fake caller (Cartesia voice harness pattern from iter76 `engine/tools/mic_caller.py`, UNKNOWN exact path — shall grep `find engine -name '*caller*'` in T1) speaking "That's my old office number; better cell is +1 512 555 0142" — expected ≤2 asks total for phone and single confirmation round, NO verbatim x6 repetition; paste mic_events + rounds from ledger; then run the builder-level pin (port from iter79 regression pin named test in `8b88bb6` if imported cleanly; else write a new pin asserting one-turn reset of the re-ask flag).
Commit: ONE commit — `iter80 T5: mic phone-number fallback capture + turn-scope re-ask flag (chat parity; kcal from iter79 8b88bb6 minimal port)`.

### T6 — smoke battery + evidence pack + plan next
Goal: full smoke battery after all changes land; evidence written; report-card for owner; NOTE the ASYNC proposal (owner "ritu/async element call" idea — retrieve asynchronously to shave await: hold for NEXT plan).
Files: OREGON `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter80-el-flip-mic-phone-fix/*`.
Commands (full): rerun smoke battery on :8026 (happy 3 personas from `chat-iter65-happy` list + 1 mic live loop capture) → `.venv/bin/python -m pytest -q` in worktree → expect green ≥ 451+12 pins; update PENDING_TASKS on OREGON main? NO — only write evidence + commit nothing to main (LAW 0).
Dependencies: T5.
Verification: ALL batteries PASS; EL flip holds across states (no cogitation in Closing/ConfirmSlots); rate knob no-playhead drift across 20 buffers; keepalive stable (no turn-1 fresh-TLS ms spike); mic re-ask ≤2.

## Validation Plan (end-to-end)
1. Worktree suite green: `.venv/bin/python -m pytest -q` at `/tmp/opencode/wt-iter80/engine` (whole suite; expected ≥463 pins like merge 50a453f era comment).
2. EL smoke: 10 agent turns all EL (Sara ear check by owner) on :8026 with `TTS_PROVIDER=elevenlabs`.
3. Rate knob: `?rate=0.93` audible slowdown, no drift.
4. Mic re-ask: ≤2 asks, fallback number captured and carried into ConfirmSlots.
5. All evidence in the evidence folder; owner reviews; owner say-so ONLY then consider push (NOT in this plan).

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter79 speech-flow cushions beyond the turn-scope bool | owner said fix-from-stable; speech-flow line (74/78/79) is the burned-down branch we are NOT rebuilding |
| Async RAG retrieval (owner "ritu/async element call") | needs own design round; goes into the NEXT major-plan after T6 audit |
| Model downgrade persistence | temporary `.env` smoke-only; prod stays gpt-5.4 (MODEL LAW) until owner flips |
| Merge/push of `engine/iter80-el-flip-mic-phone-fix` | LAW 0 — owner say-so after T6 evidence |

PLAN FILE: /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter80_el_flip_mic_phone_fix.md
