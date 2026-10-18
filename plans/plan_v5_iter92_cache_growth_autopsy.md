# plan_v5_iter92_cache_growth_autopsy — cache stops growing past the ack/heavy floors; pin the breaker, restore growth, prove with ONE GK

## Meta
- Date: 2026-10-04
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland/MainVps. ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Scope: (a) forensics on WHY prefix-cache growth stalls (owner-observed: cache_read flat at 2688/3712 while inputs grow), (b) isolate prompt-assembly change (iter87 `02eb2ac` → iter89 `30405ad`) vs pack-defaults effect, (c) ONE code fix on a new branch, (d) suite + ONE GK call proving cache GROWS + latency ≥ iter87 reference, (e) report + ASK.
- Status: PLAN ONLY (not started — awaits owner GO)

## Compaction Context (from the 2026-10-03/04 iter91 session — verbatim carry)

**Where iter91 stands (DONE, awaiting merge say-so):**
- Branch `engine/iter91-promote-pack-defaults` @ **2b3e900** (base `30405ad`, owner option B). Commits: `87730db` (T2: 11 config.py default flips — the proven iter87 round-B pack promoted to CODE defaults), `2f94eea` (T3 tooling: `scripts/new_lane.sh` + hermetic `engine/tests/conftest.py`), `2b3e900` (T3: 9 test adaptations + dead-store hermeticity). Docs on main: `a9ee061` (LANE LAW + COMMIT REGISTRY + COMMIT DISCIPLINE laws = AGENTS.md rules 8-9).
- Suite: **493 collected / 0 failed / 3 skipped (RC=0)** — red set proven identical ±env.
- T4 env scrub DONE ×4 files (md5-verified, backups in /tmp/opencode/env_backup_T4/): `WARM_AWAIT_DEST_MS 250→2500` + `DEEPGRAM_EAGER_EOT_THRESHOLD 0.7→0.35` in /opt/diallux-production/.env, OREGON main engine/.env, wt-iter89/engine/.env, wt-iter91/engine/.env. Cartesia pin intact. NO restarts (/opt restart = owner timing).
- T5 GK PASSED: Boris/happy, vanilla driver, lane 8050 → 12 agent turns, turn_cap_goodbye, no booking. Report: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter91-promote-pack/01_verify_report.md + 02_call_audit.md (4-SOP audit, 20 rows persisted to ledger `sops`).
- OPEN owner calls from iter91: merge say-so (iter89+91 together), /opt prod restart timing. iter92 does NOT answer these — separate.

**THE NEW ISSUE (owner-spotted pattern, 2026-10-04):** in the iter91 GK per-turn table, `cache_read` is FLAT — t1=0, t2-t7=2688, t9-t13=3712, t16-t19=2688 — while `input` GROWS every turn (1656→3238→3505→3558→3618→4069p50). Cache is supposed to GROW with the conversation (each turn should re-read the FULL prior prompt + pay only the delta). The observed shape = TWO STATIC FLOORS (the ack's byte-identical prefix floor 2688 ↔ the heavy/Discovery floor 3712) that oscillate instead of growing. Owner reading: "agent is lobotomized from the call" — every turn re-pays the whole growing tail; latency LOOKS okay (e2e p50 1120 < iter87 row-13 1376) but the cache economics are broken. Owner hypothesis: **iter89's prompt-enhancement changes broke prefix-cache growth** ("we change the prompt and we made a mess, all of a sudden we are missing cache"); iter87 (the MVP-finally-era proven config @ `02eb2ac`) had growing cache + great latency.

**Per-turn data ALREADY captured (iter91 GK, lane 8050 log /tmp/opencode/voice_server_8050.log):**
```
t1  stt->llm 1185 e2e 1345 cache 0    input 1656 Intake (first-turn class)
t2  1415 e2e 1606 cache 2688 input 3238 Intake
t3   934 e2e 1120 cache 2688 input 3505 Intake
t4  1292 e2e 1489 cache 2688 input 3558 Intake
t6  1426 e2e 1626 cache 2688 input 3618 Intake
t7  2303 e2e 2524 cache 2688 (extract+transition turn — the max)
t9   828 e2e 1002 cache 3712 Discovery ack (fastest turn)
t10  836 e2e 1105 cache 3712 Discovery
t13  900 barged cache 3712
t16  806 e2e 1119 cache 2688 barged
t18  959 barged cache 2688
t19  787 e2e 1102 cache 2688 barged
```

**Ledger facts (ground truth for next session):** ledger at /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db. Runs table HAS: `iter87-hold-battery` (window 05:00-06:00, imported 2026-09-30 — the iter87 battery with rounds+cache_read in the `rounds` plane!), `gk-iter89` (5 calls @ 30405ad), `iter90-mic-b0`, `iter90-mic-b250`, `chat-iter88-*`, `iter91-gk-verify` (calls=1, commit 2b3e900). Forensics_calls row 13 = iter87_hold_happy (trace a4de3446dffa91d7c3b0884cdda47cf3, 28 turns, e2e p50 1376/p90 3778, hold_releases 31, await already_done 46/no_task 0, cache0-dest 0, commit 02eb2ac, driver=llm_mic_caller_b52 FROZEN from wt-iter82); row 14 = iter87_hold_bargeloop (trace e25675a56211…, 38 turns). Row 13 params = FULL round-B pack: EAGER_HOLD_AUDIO_UNTIL_CONFIRM=true, DEEPGRAM_EAGER_EOT_THRESHOLD=0.35, DEEPGRAM_EOT_THRESHOLD=0.65, DEEPGRAM_EOT_TIMEOUT_MS=3000, WARM_AWAIT_DEST_MS=2500, POST_INTERRUPT_BACKOFF_MS=500 (lane value then; owner standard now 1000), PAUSE_LADDER reminder/8000/1, STT_RX_ZOMBIE_MS=15000, STT_ADOPT_MAX_AGE_S=120 — i.e. **config-identical to iter91 defaults except backoff 500 vs 1000 (no cache impact) → any cache-sequence difference iter87 vs iter91 = CODE (prompt assembly), not knobs.**

**Langfuse facts:** host http://46.62.233.228:3001 (Helsinki), keys in wt-iter91/engine/.env (LANGFUSE_PUBLIC_KEY/SECRET_KEY). Generation obs carry usage {unit,input,output,total} + metadata {state, latency_s, ttft_s, state_in_delta, delta_tokens, scope} — **usage has NO cached-token field; cache_read came from the engine's server-log "round usage" lines.** iter87's lane log (/tmp/opencode/voice_server_8047.log) is GONE — cache sequence for iter87 must come from the LEDGER `rounds` plane (imported 2026-09-30) — that's why the SDK-first path is mandatory.

**Session errors on record (do not repeat):** copying envs between worktrees (the wrong-250 disease — now LAW: envs are GENERATED from canonical by scripts/new_lane.sh); engine/scripts/live_sql.py predates the micbridge filter fix `537e53c` — for mic runs use the ROOT script /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py; battery_forensics.py in /tmp/opencode is a stale iter86 one-off (hardcoded RUNS) — do not reuse; call_forensics.py lives at /tmp/opencode/wt-iter86/engine/scripts/ (NOT in wt-iter91); pytest must NOT be run with ambient exports (`set -a; . ./.env` before pytest = forbidden — conftest blocks env_file but ambient os.environ still leaks); single-L "clean_diallux_SDR" misspelling creates phantom dirs (ALWAYS double-L diallux).

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| SDK-FIRST: use the proven SDKs, never hand-roll | owner 2026-10-04: "we have an sdk, actually many for this purposes, use them" |
| Reference = ledger run `iter87-hold-battery` + forensics rows 13/14 @ `02eb2ac` | the proven-CONFIG reference (owner: great latency, cache grew) |
| Isolation point = ledger run `gk-iter89` @ `30405ad` | same prompts as iter91's base, PRE-promoted-defaults → separates prompt-assembly change from knob effect |
| iter91 branch stays OPEN, unmerged | owner merge say-so pending; iter92 fix may stack on iter91 tip or cut fresh from 30405ad — decide after T1-T3 evidence |
| The fix = a CODE change to prompt assembly | cache growth is structural (prompt ordering/stability), not a knob |
| ONE GK call to prove the fix | repo law (verify = one stress persona, no A/B unless owner orders) |
| No merges without owner say-so | LAW 0 |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO on this plan | owner's word in-chat |
| iter92 branch base decision (iter91 tip 2b3e900 vs 30405ad) | decide AFTER T1-T3 (if breaker predates iter91, cut from 30405ad) |
| iter89+91 merge say-so | owner, unchanged from iter91 close-out |

## Environment & Dependencies
- OREGON ssh wrapper (Meta). Repo: /home/julio/projects/clean_diallux_SDR (double-L).
- venv (canonical, symlinked into lanes): /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python — NEVER bin/pip; always `python -m pip`.
- Ledger: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db (gitignored). NO sqlite3 CLI — use python sqlite3.
- SDKs (USE THESE): /home/julio/projects/clean_diallux_SDR/scripts/live_sql.py (ROOT copy — has micbridge filter), /home/julio/projects/clean_diallux_SDR/scripts/latency_pull.py, /home/julio/projects/clean_diallux_SDR/scripts/rag_pull.py (all main, stdlib `python3`); engine worktree SDKs: /tmp/opencode/wt-iter91/engine/scripts/{call.py, lf.py, lf_quick.py, mic_events.py}; forensics helper: /tmp/opencode/wt-iter86/engine/scripts/call_forensics.py (importable via sys.path).
- Langfuse: keys in /tmp/opencode/wt-iter91/engine/.env; host http://46.62.233.228:3001.
- iter87 lane journal: GONE (8047 log deleted). Its data = ledger `rounds` plane only.
- Iteration lanes that exist: wt-iter91 (branch @ 2b3e900), wt-iter89 (30405ad), wt-iter87 (02eb2ac), wt-iter86 (d158b4c), wt-iter85 (542d3e8) — all under /tmp/opencode/.
- Cal.com event 3801235 REAL — cancel any booking the GK creates (POST /v2/bookings/{uid}/cancel with cancellationReason body).
- Voice LAW: ElevenLabs prod Hannah ZSNL4hPqCnqoMPaI4jGX; tests Sarah uG1JFy6xppqckhHCs2KG (already in lane envs).

## Architecture (what the investigation changes)
```
ledger rounds plane (iter87-hold-battery / gk-iter89 / iter91-gk-verify)
  → cache-growth sequences (turn · input · cache_read · ttft) per run
  → isolation: iter87@02eb2ac vs gk-iter89@30405ad (pure prompt delta)
               gk-iter89 vs iter91 (knob-promotion delta, same prompts)
  → diff prompt assembly 02eb2ac..30405ad (builder.py render + agent prompt files)
  → pin the cache-breaker with line numbers + a minimal repro
  → iter92 branch: ONE fix (stable/append-only prompt ordering; floors must merge into ONE growing prefix)
  → suite (493/0/3 gate) → ONE GK on a fresh lane (new_lane.sh) → cache GROWS + latency ≥ reference
  → report research/surgeon/iter92-cache-growth/ → ASK JULIO
```

## File Map
| File (absolute path) | What | New/Edit |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter92_cache_growth_autopsy.md | THIS plan (docs→main) | NEW |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92-cache-growth/ | evidence + report | NEW (gitignored) |
| /tmp/opencode/wt-iter92/ (via scripts/new_lane.sh) | the fix branch engine/iter92-<slug> | NEW |
| /tmp/opencode/wt-iter92/engine/diallux/graph/builder.py (+ prompt files) | the ONE cache fix | EDIT (on branch) |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db | iter92-gk-verify run import | APPEND |

## Deploy Rules
- **SYNC LAW (owner, 2026-10-04): the session sits in FINLAND (Helsinki 46.62.233.228); ALL editing/commits/pushes happen ON OREGON (5.78.83.174) ssh-wrapped. After every push from OREGON, Finland PULLS (`git -C <finland-checkout> fetch origin && … ` on the docs worktree only — the dirty Helsinki main checkout stays untouched, engine work flows through fresh Finland worktrees off origin/main). That is the only sanctioned way the boxes stay synced. NEVER edit files from Finland directly onto OREGON's tree except via the ssh-wrapped commands above.**
- Lane ops ONLY via `scripts/new_lane.sh <iterNN> <base> <slug>` (LANE LAW, AGENTS.md 2026-10-04); audit gate must print READY before boot.
- NEVER checkout/switch/reset/pull on the OREGON main checkout; NEVER merge without owner say-so; keyhound before any push.
- NEVER run pytest with exported secrets. NEVER touch live agent IDs, :8001-8003, Caddy.
- Foreground test uvicorns: 127.0.0.1 bind on a free port, kill after (pid file /tmp/opencode/voice_<port>.pid).

## Tasks (in order)

### T1 — Reference cache sequences from the ledger (SDK-only)
Goal: the iter87 reference + the iter89 isolation point, as per-round tables.
Commands:
- `ssh … "cd /home/julio/projects/clean_diallux_SDR && python3 scripts/latency_pull.py --run iter87-hold-battery"` and `… --run gk-iter89` and `… --run iter91-gk-verify`.
- Rounds detail via SQL: `/home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -c "import sqlite3; con=sqlite3.connect('/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db'); …"` — SELECT trace_id, turn/ord, state, input, cache_read, ttft_ms FROM rounds WHERE run_id IN ('iter87-hold-battery','gk-iter89','iter91-gk-verify') ORDER BY trace_id, ord — print the sequences side by side.
Verification: each sequence prints; compute per-turn: `delta_repaid = input - cache_read` and `growth = cache_read[i] - cache_read[i-1]`.
Expected signal: iter87 = growth > 0 most turns (cache_read approaches prior input); iter91 = growth ≈ 0 (two static floors).

### T2 — Isolate: prompt-assembly change vs knob change
Goal: attribute the growth break.
Commands: compare T1 sequences — iter87@02eb2ac vs gk-iter89@30405ad (BOTH ran pack-ish env lines via their lane envs; both have cache sequences in the ledger) → if growth breaks at 30405ad = PROMPT ASSEMBLY (iter89). If gk-iter89 grows and only iter91 flattens = the promoted knobs (then check warm/eager paths' effect on prompt shape).
Verification: a one-line verdict with the run names as evidence; save table to /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92-cache-growth/01_sequences.md.

### T3 — Pin the breaker in the prompt assembly
Goal: line-numbered mechanism. Diff the prompt assembly between `02eb2ac` and `30405ad`:
- `ssh … "cd /home/julio/projects/clean_diallux_SDR && git diff 02eb2ac 30405ad --stat -- engine/diallux/ | tail -15"` → target: builder.py render/assembly + agent prompt md files + llm.json.
- Read the CURRENT assembly in /tmp/opencode/wt-iter91/engine/diallux/graph/builder.py (history block, lanes block, tools block, state head — ORDER + stability). Cache grows only if the byte-prefix of every turn's prompt is the previous turn's prompt (append-only history, stable state head, lanes/tools in FIXED slots, identical system blocks).
Verification: name the block whose bytes shift per turn (the cache breaker) with builder.py:LINE; minimal repro = render two consecutive synthetic prompts and diff them (throwaway script, or adapt the existing test helpers — do NOT add new SDK scripts).

### T4 — THE FIX (code, iter92 branch)
Goal: restore single growing prefix. ONE mechanism-level change: make the per-turn prompt = [fixed head][fixed state block][append-only history][stable lanes slot][stable tools slot] so every turn's prefix byte-matches the prior turn (the ack's FIND-5 floor and the heavy floor must CONVERGE into one growing prefix — keep the ack's cache-floor win AND the growth).
Commands: `ssh … "OR=/home/julio/projects/clean_diall* && git -C \$OR worktree add /tmp/opencode/wt-iter92 -b engine/iter92-<slug> <base-from-T2>"` (or new_lane.sh), edit builder.py (+ prompt files if needed), commit on branch.
Verification: (1) suite `cd /tmp/opencode/wt-iter92/engine && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m pytest tests -q` = 0 failed (the 9 adapted tests may need re-adaptation IF the fix changes await/round shapes — adapt per the iter91 precedent, provenance comments mandatory); (2) synthetic consecutive-prompt diff shows append-only growth.

### T5 — Prove with ONE GK
Goal: cache GROWS + latency ≥ iter87 reference.
Commands: `cd /tmp/opencode/wt-iter91 && ./scripts/new_lane.sh 92 <base> <slug>` (audit READY) → boot 127.0.0.1:<free port> → vanilla driver Boris/happy --agent-idle-s 4 → kill lane.
Verification (ground truth = server log + Langfuse): (1) `round usage` cache_read sequence GROWS turn over turn (growth > 0 for ≥70% of turns after turn 2); (2) e2e p50 ≤ 1376 (row 13) and no new cache0-dest class; (3) hold alive (releases ≥1, cancels 0); (4) import `iter92-gk-verify` via ROOT live_sql.py; (5) cancel any booking (event 3801235 law).

### T6 — Report + ASK
Goal: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter92-cache-growth/02_verify_report.md — sequences table, breaker mechanism, fix diff summary, GK numbers vs reference. Then ASK JULIO: merge say-so (iter92 + iter91 + iter89 stack), whether iter90's A/B verdict needs a re-read in cache-light (the "disease" may have been cache economics all along).

## Validation Plan (end-to-end)
T1 sequences from ledger → T2 one-line attribution → T3 breaker pinned → T4 suite 0 failed + append-only synthetic proof → T5 one GK: cache grows, e2e ≤ reference, ledger row → T6 report → owner merge call.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| iter91 merge + /opt restart | owner say-so, unchanged |
| A/B re-runs of backoff 500/1000 | FIND-38 stands on owner authority |
| Openener rotation / rephrase-simplify rules (02_call_audit polish items) | separate prompt iteration — do NOT bundle into the cache fix (ONE variable per iteration) |
| Turn-1 TTFT floor (1064) | known first-turn class; revisit only if the cache fix moves it |
