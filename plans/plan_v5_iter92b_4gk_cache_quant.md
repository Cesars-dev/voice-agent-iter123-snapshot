# plan_v5_iter92b — 4 GK stress personas @ 2b3e900: QUANTIFY the real cache/latency outcome (no code changes)

## Meta
- Date: 2026-10-05
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland (Helsinki 46.62.233.228). ALL repo ops ssh-wrapped to OREGON:
  ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 '<cmd>'
- Numbering law: NO new engine number — this is a TEST/analysis session. It rides iter92
  (suffix b) because iter92 minted the cache autopsy thread. ZERO code changes here.
- Scope: run FOUR llm_mic GK calls (stress personas) at the iter91 build (2b3e900), scan
  their server logs + Langfuse, and QUANTIFY the real outcome against the iter92 verdict
  (CACHE_ANALYSIS.md on main, commit bf5fb1e): 1024-block cache floors, per-turn re-bill =
  replaced delta + user turn, e2e latency vs the iter87 row-13 reference (p50 1376).
- Status: PLAN ONLY (not started — awaits owner GO)

## Compaction Context (from the 2026-10-04/05 iter92 session — verbatim carry)
- VERDICT (committed): NO REGRESSION. Engine cache floors {1664,2688,3712,4736,5760,
  6784,7808,8832} = 640+1024k — provider (gpt-5.4) block quantization, identical across
  every ledger run since iter56 (battery-iter56 +8/flat24; happy-iter78-or 93 turns +10;
  iter87 r13 +10; iter90/91 same shape). iter87's 'growth' = deep call + heavy ConfirmSlots
  tool rounds crossing blocks every 2-3 turns; iter90/91 = short light calls never crossing.
- REAL COST per turn = replaced post-history delta (state block grows with verbatim dv
  appends; 1746->2763->4326 B in iter91) + new user turn + sub-block remainder (<1024 shaving,
  up to 1023 tok). NOT a code/env revert: builder.py+config.py byte-identical 02eb2ac..30405ad;
  iter91's 11 knobs touch no cache flags.
- PROVIDER CONTROL: real Retell prod call (deprecated-key account, call_b790bb6fd6a679bf967,
  95 requests) prompt 2648->10643 grows identically, llm p50 911 ms, 11/60 spikes 1.9-4.2 s.
  Raw: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92-cache-growth/retell_call_b790bb6f_raw.json
  (checksum-identical on BOTH boxes).
- DOCS on main: CACHE_ANALYSIS.md (root) @ bf5fb1e (pushed from OREGON wt-main-docs, pulled FI).
  Evidence (gitignored, checksum-synced): /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92-cache-growth/
  {01_sequences.md, retell_call_b790bb6f_raw.json}.
- CODE under test: engine/iter91-promote-pack-defaults @ 2b3e900 (worktree /tmp/opencode/wt-iter91
  on OREGON), pushed to GitHub. Suite state at 2b3e900: 493 collected / 0 failed / 3 skipped.
  iter89 (30405ad) + iter91 MERGE still pending owner say-so.
-Ledger ground truth: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db
  (rounds plane: trace_id, ts, state, input, cache_read, ttft_ms; runs plane commit_sha).
  Reference rows: iter87-hold-battery (2 calls, 02eb2ac) = the ONLY full-depth mic reference.
- GK mechanics (proven iter91): lane uvicorn 127.0.0.1:<port>, driver
  /tmp/opencode/wt-iter91/engine/scripts/llm_mic_caller.py --scenario happy --persona Boris
  --agent-idle-s 4 --ws-url 'ws://127.0.0.1:PORT/mic/ws?k=$VOICE_TEST_TOKEN' (token in
  wt-iter91/engine/.env). Server log carries 'round usage: turn=N state=S input=I cache_read=C
  ... delta_tokens=D' lines (delta_tokens = CHARS of the post-history delta).
- Session errors on record (do not repeat): pytest with exported env secrets = FORBIDDEN;
  envs are GENERATED per lane (never copy between lanes); Finland fetch must go through the
  MAIN checkout path (worktree fetch hits gh-creds 'Not a directory' — fetch from
  /home/julio/projects/clean_diallux_SDR then ff-merge in wt-main-docs); OREGON wt-main-docs
  push uses -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds'.
- Voice LAW: prod TTS Hannah (lane envs carry it); test voices Sarah. Cal.com event 3801235
  is REAL — cancel any GK booking: POST https://api.cal.com/v2/bookings/<uid>/cancel with
  JSON body {"cancellationReason": "test cleanup iter92b"}. Langfuse host
  http://46.62.233.228:3001, keys in /tmp/opencode/wt-iter91/engine/.env.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Branch under test = 2b3e900 as-is (NO code edits, NO suite) | hypothesis is behavioral (quantization economics), iter92 verdict is no-regression; code change = separate iteration with owner say-so |
| 4 GK calls, personas Sam / Priya / Dave / Bianca, scenario happy, vanilla llm_mic_caller | Boris already ran in iter91-gk-verify (compare against it); these 4 mirror gk-iter89's spread; owner ordered stress-test-persona spread |
| Metric = per-turn (input, cache_read, delta_tokens, state, ttft) -> grid-fit + growth events + repaid model | the only honest cache read on this stack is block-quantization stats, proven in iter92 |
| Reference gates: e2e p50 <= 1376 ms / turn, no new cache0-dest beyond turn-1 class, hold alive (releases >=1), growth events > 0 per call | iter87 hold battery row-13 = the latency reference; iter91 GK already passed these on Boris |
| Foreground lane, 127.0.0.1 bind, free port, kill after | repo law (voice lane discipline) |
| One plan = one session; report + ASK JULIO at end | LAW 0 (this session is DOCS+evidence only) |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO on this plan | owner word in-chat |
| exact persona slugs | pinned in T0 from /tmp/opencode/wt-iter91/engine/tests/llm2llm/personas.py — expected set {Sam, Priya, Dave, Bianca}; if slugs differ (e.g. '(GK) Priya'), use what the file says, log it in the report |
| live_sql.py import CLI flags | T4 starts with 'python3 scripts/live_sql.py --help' pinned into the report before import (NO guessing) |

## Environment & Dependencies
- ssh wrapper (see Meta). Repo on OREGON: /home/julio/projects/clean_diallux_SDR (double-L — NEVER clean_diallux single-L).
- venv (NEVER bin/pip, always python -m pip or direct python path):
  /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python
- Lane: create with /home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh — LAW: lane ops ONLY via
  new_lane.sh; audit gate must print READY before boot. Expected lane dir /tmp/opencode/wt-iter92b
  (T0 pins the real path into /tmp/opencode/iter92b_lane_path.txt and every later command reads it).
- Server boot port: 8062 (free; 8050 was iter91, 8061 killed already). pid file /tmp/opencode/voice_8062.pid.
- Server log: /tmp/opencode/voice_server_8062.log (driver --journal-log appends here too).
- Driver: <LANE>/engine/scripts/llm_mic_caller.py — args per iter90_run_mic.sh precedent.
- Persona registry: <LANE>/engine/tests/llm2llm/personas.py.
- Ledger import SDK: /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py (ROOT copy — has the
  micbridge filter; NEVER the pre-537e53c engine/scripts copy for mic runs).
- Langfuse: http://46.62.233.228:3001 (Helsinki), keys in <LANE>/engine/.env (LANGFUSE_PUBLIC_KEY/SECRET_KEY).
- Evidence dir (gitignored): /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92b-4gk-quant/
- Retell keys (NOT needed this session; recorded): /home/julio/projects/Retell_AI_MCP_connection/.env
  (original account, deprecated key — 50 calls; production calls live THERE, not under the /opt key).

## Architecture (what this session changes)


## File Map
| File (absolute path) | What | New/Edit |
|---|---|---|
| /tmp/opencode/wt-iter92b/ (via new_lane.sh) | test lane @ 2b3e900 | NEW (lane infra, no code edits) |
| /tmp/opencode/voice_server_8062.log | lane log incl. round usage lines | NEW (forge) |
| /tmp/opencode/iter92b_gk_<persona>.json + .journal | driver outs x4 | NEW |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92b-4gk-quant/01_raw_tables.md | per-call round tables | NEW (gitignored) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92b-4gk-quant/02_quant_report.md | quantified verdict vs reference | NEW (gitignored) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db | run iter92b-4gk-quant import | APPEND (gitignored) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92-cache-growth/ (BOTH boxes) | cross-pointer note only | NO EDIT |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter92b_4gk_cache_quant.md | THIS plan (docs->main) | NEW |

## Deploy Rules
- SYNC LAW: Finland reads/analyzes; ALL edits/commits/pushes ssh-wrapped ON OREGON; after every
  OR push, Finland fetches via the MAIN checkout path then ff-merges wt-main-docs (exact commands in T4).
- LANE via new_lane.sh only; NEVER checkout/switch/reset/pull on the OREGON main checkout;
  NEVER merge without owner say-so; keyhound before any push (lane scripts: keyhound exists in
  /tmp/opencode/wt-iter91/scripts/ — run it in wt-main-docs context before push).
- Foreground tests: 127.0.0.1 bind, port 8062, kill after (pid file /tmp/opencode/voice_8062.pid).
  NEVER touch :8001-8003, Caddy, live agent IDs.
- NEVER run pytest or uvicorn with.Make sure NO ambient exported .env secrets leak beyond the lane process (boot inside its own bash -c 'set -a; . ./.env; set +a; exec ...' exactly).
- Cal.com: cancel any booking created (event 3801235 law).
- NO code edits in wt-iter92b (any discovered bug = FINDING in report, not a fix commit).

## Tasks (in order)

### T0 — Lane boot + persona pin
Goal: a READY lane at 2b3e900 on port 8062 + pinned persona slugs.
Commands:
- ssh … 'cd /home/julio/projects/clean_diallux_SDR && bash scripts/new_lane.sh 92b 2b3e900 4gk-quant'
- ssh … 'ls -d /tmp/opencode/wt-iter92b && echo /tmp/opencode/wt-iter92b > /tmp/opencode/iter92b_lane_path.txt'
  (if the lane dir name differs, write the REAL path — verify 'git -C <LANE> rev-parse --short HEAD' = 2b3e900-ish)
- ssh … 'grep -n "name" /tmp/opencode/wt-iter92b/engine/tests/llm2llm/personas.py | head -40'
- Boot: ssh … 'cd /tmp/opencode/wt-iter92b/engine && nohup bash -c "set -a; . ./.env; set +a; exec /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8062" > /tmp/opencode/voice_server_8062.log 2>&1 & echo $! > /tmp/opencode/voice_8062.pid; sleep 8; tail -3 /tmp/opencode/voice_server_8062.log'
Verification: log shows 'Uvicorn running on http://127.0.0.1:8062'; lane audit printed READY; persona slugs logged into T0 notes (append to 01_raw_tables.md header).

### T1 — FOUR GK calls (one per persona)
Goal: 4 full mic calls captured raw.
For P in Sam Priya Dave Bianca (in this order), per call:
- ssh … 'cd /tmp/opencode/wt-iter92b/engine && set -a; . ./.env; set +a; timeout 600 /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/llm_mic_caller.py --ws-url "ws://127.0.0.1:8062/mic/ws?k=$VOICE_TEST_TOKEN" --scenario happy --persona $P --agent-idle-s 4 --max-caller-turns 20 --journal-log /tmp/opencode/voice_server_8062.log --out /tmp/opencode/iter92b_gk_$P.json && echo GK_$P_DONE'
- After EACH call: ssh … 'grep -c "round usage" /tmp/opencode/voice_server_8062.log' (expect >12) and
  copy logs: ssh … 'cp /tmp/opencode/voice_server_8062.log /tmp/opencode/iter92b_server_log_$P.snapshot'
Verification: four GK_$P_DONE lines, four --out JSONs exist, 48+ round usage lines total.
IF a call books: POST /v2/bookings/<uid-from-out-json>/cancel (Cal.com v2, body {"cancellationReason":"test cleanup iter92b"}).

### T2 — Quantification (Finland reads OR logs via ssh; tables into 01_raw_tables.md on OR)
Goal: per-call round table + the 4 iter92 metrics.
Commands:
- ssh … 'grep "round usage:" /tmp/opencode/voice_server_8062.log | tail -<N-per-call-from-T1-count>' -> parse
  (throwaway parser亦 OK: write /tmp/opencode/iter92b_parse.py on OREGON, run with the venv python —
  pattern: turn, state, input, cache_read, output, ttft, state_in_delta, delta_tokens; carry-over persona boundaries marked by 'GK_' markers in call outs).
Compute per call: (a) % of cache_read values where (cache_read-640) % 1024 == 0 (target ~100%;
  report any off-grid value as ANOMALY); (b) growth events (+1024/(+2048...) crossings) vs turns;
  (c) repaid-fit: observed input-cache vs predicted delta_tokens/4 + last-turn size (within ±128);
  (d) ttft p50/p90 + state ladder reached.
Verification: 4 tables printed; anomalies flagged; table saved into 01_raw_tables.md via ssh-wrapped append.

### T3 — Verdict vs reference (the real outcome, quantified)
Goal: CONFIRMS-or-DISCONFIRMS the iter92 verdict with numbers, in one doc.
- Compare vs iter87-hold-battery (rows 13/14 SQL) + iter91-gk-verify (Boris): same SQL via venv python sqlite3 as in iter92 T1.
- Compare vs gk-iter89 (5 graph-persona calls): mic-vs-graph delta on the same metric set.
- DISCONFIRM trigger (any of): an off-grid cache_read NOT explained by state-entry lite; a
  cache_read DROP >1024 without a state change (barges) occurring in >20% of rounds; e2e p50 > 1376;
  hold broken (releases 0 / cancels >0). Any trigger -> FOPEN finding row in the report (NOT a fix).
Verification: 02_quant_report.md written on OR with 4 tables + verdict + anomaly list.

### T4 — Ledger import + docs + sync + ASK
Goal: durable evidence, synced boxes, owner decision request.
- ssh … 'cd /home/julio/projects/clean_diallux_SDR && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pip list 2>/dev/null | grep -qi retell || true'
  (retell SDK NOT needed; live_sql.py uses stdlib) then:
  ssh … 'cd /home/julio/projects/clean_diallux_SDR && python3 scripts/live_sql.py --help | head -20' — PIN the flags
  into 02_quant_report.md BEFORE importing; import run id 'iter92b-4gk-quant' (commit recorded 2b3e900).
- ssh … 'cd /tmp/opencode/wt-main-docs && bash /tmp/opencode/wt-iter91/scripts/keyhound' (pre-push law)
- scp evidence FI<->OR both ways (01_raw_tables.md, 02_quant_report.md) + checksum (md5sum) both sides.
- Docs commit on OR: report pointer + one-paragraph verdict appended to CACHE_ANALYSIS.md
  (section '## iter92b quant check (2026-10-09)') -> git add/commit/push from wt-main-docs
  (push via -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds').
- FI pull: ssh from FI MAIN path: git -C /home/julio/projects/clean_diallux_SDR fetch origin
  'refs/heads/main:refs/remotes/origin/main'; git -C /tmp/opencode/wt-main-docs merge --ff-only origin/main.
- Kill lane: ssh … 'kill $(cat /tmp/opencode/voice_8062.pid)'
- ASK JULIO: (1) accept verdict / open findings? (2) authorize the state-block freeze/slim as iter93 code change? (3) iter89+91 merge say-so still pending?

## Validation Plan (end-to-end)
T0 lane READY -> T1 4 calls done (48+ rounds) -> T2 4 quant tables, grid-fit ~100% -> T3 verdict vs
reference (CONFIRMS or DISCONFIRMS with numbers) -> T4 ledger row + report on main + boxes synced +
owner asked. NO code changes anywhere in this session.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| State-block freeze / slimmed delta (THE fix) | iter93 code session ONLY on owner say-so with iter92b numbers in hand |
| iter89+iter91 merge, /opt restart | owner say-so (unchanged) |
| More Retell control calls | evidence sufficiency reached in iter92; re-open only if iter92b DISCONFIRMS |
| A/B eager-eot knobs | FIND-38 stands; no knob changes |
