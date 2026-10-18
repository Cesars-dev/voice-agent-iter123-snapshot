# plan_v5_iter91_promote_pack_defaults_gk_verify — flip the proven switches into code defaults, scrub the wrong 250, run ONE GK to prove it

## Meta
- Date: 2026-10-03
- Project root (OREGON, source of truth): /home/julio/projects/clean_diallux_SDR
- Session box: Finland/MainVps. ALL repo ops ssh-wrapped to OREGON:
  `ssh -o ConnectTimeout=10 -o BatchMode=yes -i /home/julio/.ssh/id_ed25519_hetznor root@5.78.83.174 "<cmd>"`
- Scope: ONE branch (engine/iter91-promote-pack-defaults) that (a) promotes the MVP-proven round-B switch pack to config.py defaults, (b) suite green, (c) ONE GK verification call on the vanilla driver, (d) report + ASK. Plus docs: this plan replaces the FROZEN-SUSPECT skeleton; ENV-SWITCHES already corrected.
- Status: PLAN ONLY (not started — awaits owner GO)

## Compaction Context (from the 2026-10-03 iter90 verdict session)

**The verdict (memo 94, cited):** the iter90 Boris A/B "disease" = SWITCH DRIFT, not a design or code failure. The drop design (`eager_hold_audio_until_confirm`, iter85 FIX 1 @ b97957f) was DORMANT in the A/B (no env line, code default False); the successful iter87 battery ran it ON (boot-script exports; lane journals: 31+37 confirmed releases, 23 silent discards, 0 legacy cancels). The A/B multi-round turns = the DESIGNED FSM tool chain (extract → complete+transition → entry-lite ack), same distribution as iter87. 250/2500 unrelated to rounds (ack-await only). The old kill+refire design was DELETED in 542d3e8 by design (double-append disaster class) — do NOT restore it.

**Owner decisions 2026-10-03 (verbatim intent):**
1. NO A/B re-run — values already pinned; "0 vs 250" tested nothing.
2. Fix = "promote the pack": make the production env config the one that works — promote the full iter87 round-B pack to DEFAULTS so no lane can boot without it.
3. Verification = ONE GK persona (stress set) after the fix commit. NO b52 needed (b52 = barge stress variant only, stays on engine/iter82-pause-nudge); the verification runs the ORIGINAL vanilla `llm_mic_caller.py` (owner revised the first driver law same day).
4. POST_INTERRUPT_BACKOFF promoted value = **1000** (owner standard; the 500 lane value "added more problems than it solved"; 500-vs-1000 was never A/B'd — FIND-38).
5. iter91 frozen skeleton (`plans/plan_v5_iter91_defaults_and_warm_decouple.md`, commits d9616c6/35a9bd8) = INVALIDATED by the verdict (its "driver×eager artifact / SOT fire law" rationale was refuted: rounds were tool rounds). This plan REPLACES it.

**Ledger state:** FIND-37 (switch drift, rowid 37) + FIND-38 (backoff never compared, rowid 38) in `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db`; forensics_calls rows 13/14 = the PROVEN-CONFIG reference (params carry the full knob list + driver identity, commit 02eb2ac, traces a4de3446…/e25675a5…). Backup: ledger.db.bak-iter90-verdict-20261003.

**The wrong 250 (scrub target):** `WARM_AWAIT_DEST_MS=250` sits in wt-iter89/engine/.env:56, OREGON main engine/.env:54, and /opt prod. Ratified value = 2500 (iter87: worst warm 2059 ms, zero timeouts). ENV-SWITCHES.md corrected 2026-10-03 (docs commits 15a624f→a3a4878 on main).

**Session errors on record (do not repeat):** 250-for-2500 transcription error (prior session); "iter87 had zero multi-round turns" retracted; single-L "clean_dialux_SDR" path misspelling created a phantom dir (cleaned up; ALWAYS type double-L diallux or use glob `clean_diall*`); findings table must be queried FIRST in any analysis session.

## Resolved Decisions (DO NOT revisit)
| Decision | Rationale |
|---|---|
| Promote pack to config.py defaults (not env-only) | owner: no lane may boot without the tested design "by construction"; kills drift recurrence |
| Backoff promoted value = 1000 | owner standard; 500 proven only pre-hold (FIND-38) |
| Warm await promoted value = 2500 | iter87 battery spec (worst warm 2059 ms) |
| NO A/B re-run of warm-await | values pinned; 0-vs-250 test was vacuous |
| Verification driver = vanilla llm_mic_caller.py | owner revised driver law; vanilla drives calls fine; b52 = barge stress only |
| Verification persona = Boris, scenario happy, --agent-idle-s 4 | apples-to-apples vs the iter90 A/B (same persona/scene/driver, ONLY the switches differ) |
| Suite gate = same stale-red set unchanged | repo law: 7 failed / 472 passed / 2 skipped (test_delivery ×4, iter46, iter59, iter60) |
| Branch base = 30405ad (engine tip), NOT main | owner option B 2026-10-03: main untouched until iter89/91 land; apples-to-apples with A/B prompts; iter87 precedent (cut from unmerged iter85 tip) |
| Branch via OREGON worktree add, NEVER checkout on the OREGON main checkout | OREGON main checkout = prod working tree, git state frozen (df23d37-era + iter73 branch HEAD) |

## BLOCKED / NEEDS INPUT
| Item | Where / how to unblock |
|---|---|
| Owner GO on this plan | owner's word in-chat |
| Verify port 8050 free before boot | `ss -ltnp | grep 8050` on OREGON; pick next free if taken |
| /opt prod restart after env scrub | owner's call, AFTER the branch verdict (services read env at boot; no restart inside this plan) |

## Environment & Dependencies
- OREGON ssh wrapper (Meta). Repo: /home/julio/projects/clean_diallux_SDR (double-L diallux ALWAYS).
- venv: /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python (copy-mirror; never bin/pip, use `python -m pip`).
- Worktree to create: /tmp/opencode/wt-iter91, branch engine/iter91-promote-pack-defaults, cut from **the current ENGINE tip 30405ad** (branch engine/iter89-prompt-enhancements, wt-iter89) — OWNER DECISION 2026-10-03 option B: stay on the engine branch stack, do NOT touch main; base 30405ad keeps the iter89 prompts = apples-to-apples with the iter90 A/B. Documented deviation: iter91 rides an awaiting-merge branch (same precedent as iter87 cutting from the unmerged iter85 tip 542d3e8); iter89 + iter91 merge together at owner say-so. Note: config.py is byte-identical between 730dfdb and 30405ad — the flips are the same either way.
- .env for the lane: cp /tmp/opencode/wt-iter89/engine/.env /tmp/opencode/wt-iter91/engine/.env (ENV LAW), then scrub WARM_AWAIT_DEST_MS 250→2500 in the COPY (the branch defaults make it belt-and-suspenders).
- Driver: /tmp/opencode/wt-iter89/engine/scripts/llm_mic_caller.py (vanilla). Scenario happy, persona Boris (loads from engine/tests/llm2llm/personas.py mic_personas), caller model gpt-4o-mini, agent gpt-5.4 (OPENAI_MODEL in .env).
- Voice: ElevenLabs Sarah (test voice, per VOICE LAW) — already in the wt-iter89 .env.
- Langfuse: /tmp/opencode/wt-iter91/engine/.env keys; host http://46.62.233.228:3001; traces paginate /api/public/traces?limit=100&page=N.
- Ledger import: cd /tmp/opencode/wt-iter91/engine && . ./.env && .venv/bin/python scripts/live_sql.py import --window "HH:MM-HH:MM" --run iter91-gk-verify --commit <sha>.
- Suite: cd /tmp/opencode/wt-iter91/engine && .venv/bin/python -m pytest tests -q.
- Push: git -c credential.helper='store --file=/home/julio/projects/clean_diallux_SDR/.git/gh-creds' push (lock warning = benign noise); keyhound before push.
- Cal.com: event 3801235 REAL — cancel any booking the GK creates (POST /v2/bookings/{uid}/cancel with cancellationReason body).

## Architecture (what changes, one block)
```
config.py defaults flip (9 values) + ENV scrub (250→2500 ×3 files)
  → fresh worktree branch (base 30405ad, engine stack) → suite green
  → lane 127.0.0.1:8050 boots with BARE-DEFAULT behavior (env only overrides voice/test keys)
  → vanilla driver, Boris/happy, agent-idle-s 4 (same shape as iter90 A/B)
  → ground truth: server log (hold releases, await outcomes, round usage cache reads) + Langfuse trace
  → import to ledger (iter91-gk-verify) → compare vs rows 13/14 profile + iter90 A/B
  → report in research/surgeon/iter91-promote-pack/ → ASK JULIO (merge = owner only)
```

## File Map
| File (absolute path) | What | New/Edit |
|---|---|---|
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter91_promote_pack_defaults_gk_verify.md | THIS plan (docs→main) | NEW |
| /home/julio/projects/clean_diallux_SDR/plans/plan_v5_iter91_defaults_and_warm_decouple.md | frozen skeleton → SUPERSEDED | git mv to plans/archive/ |
| /tmp/opencode/wt-iter91/engine/diallux/config.py | the 9 default flips | EDIT (on branch) |
| /tmp/opencode/wt-iter89/engine/.env | scrub 250→2500 (owner-authorized) | EDIT |
| /home/julio/projects/clean_diallux_SDR/engine/.env | scrub 250→2500 (owner-authorized) | EDIT |
| /opt prod .env (path per iter90 memo: /opt prod) | scrub 250→2500 (owner-authorized; no restart in-plan) | EDIT |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter91-promote-pack/ | report + evidence | NEW |
| /home/julio/projects/clean_diallux_SDR/research/surgeon/iter48-rag-truth/ledger.db | import iter91-gk-verify run | APPEND |

## Deploy Rules
- Branch cut ONLY via `git worktree add` on OREGON: base = **30405ad** (engine/iter89-prompt-enhancements tip, OWNER option B 2026-10-03 — stay on the branch stack, main untouched). NEVER checkout/switch/reset/pull on the OREGON main checkout.
- NEVER touch: live agent IDs, services :8001-8003, Caddy, prod voice lane restarts, the OREGON main checkout's git state, Helsinki local repo working tree (dirty, on engine/iter76-harness-firesim).
- ENV scrub is owner-authorized by this plan's scope ("literally flip the switches"); do NOT touch any other .env key. Preserve CARTESIA_MODEL_ID pin (2026-09-23 lesson) — the scrub edits ONLY the WARM_AWAIT_DEST_MS line.
- No merges without owner say-so (LAW 0). keyhound before any push.

## Tasks (in order)

### T1 — Docs: replace the skeleton (main)
Goal: this plan on main; skeleton archived.
Commands: write this file into /tmp/opencode/wt-main-docs/plans/; `git -C /tmp/opencode/wt-main-docs mv plans/plan_v5_iter91_defaults_and_warm_decouple.md plans/archive/` (or delete if git says path missing on that worktree — the skeleton commit d9616c6 IS on main); commit both; push origin main.
Verification: `git -C /tmp/opencode/wt-main-docs log --oneline -2` shows the docs commit; origin/main advanced.

### T2 — Branch + the 9 flips (code)
Goal: engine/iter91-promote-pack-defaults with the proven pack as defaults.
Commands:
- Create worktree: `ssh … "OR=\$(ls -d /home/julio/projects/clean_diall*) && git -C \$OR worktree add /tmp/opencode/wt-iter91 -b engine/iter91-promote-pack-defaults 30405ad"` (base = engine tip; OWNER option B).
- Edit /tmp/opencode/wt-iter91/engine/diallux/config.py EXACTLY:
  - :206 `tts_gate_fast_first_flush: bool = True` → `False`
  - :226 `warm_await_dest_ms: int = 0` → `2500`
  - :233 `eager_hold_audio_until_confirm: bool = False` → `True`
  - :318 `tts_dedupe_semantic: bool = True` → `False`
  - :352 `deepgram_eot_threshold: float = 0.7` → `0.65`
  - :353 `deepgram_eot_timeout_ms: int = 2500` → `3000`
  - :354 `deepgram_eager_eot_threshold: float | None = None` → `0.35`
  - :356 `deepgram_eager_eot: bool = False` → `True`
  - :484 `post_interrupt_backoff_ms: int = 0` → `1000`
  - :467 `pause_ladder_mode: str = "off"` → `"reminder"`
  - :468 `pause_reask_ms: int = 15000` → `8000`
  - (:469 pause_ladder_max stays 1; :478/:479 stt values already 120/15000 — no change)
- Update the comments on those lines to cite the provenance (iter87 battery / rows 13/14 / FIND-37/38) per repo style.
- Commit on the branch.
Verification: `git -C /tmp/opencode/wt-iter91 diff origin/main -- engine/diallux/config.py` shows EXACTLY those value flips, nothing else.

### T3 — Suite green
Commands: `ssh … "cd /tmp/opencode/wt-iter91/engine && .venv/bin/python -m pytest tests -q"`.
Verification: 7 failed / 472 passed / 2 skipped = the stale-red set UNCHANGED (test_delivery ×4, iter46 fast-first-flush, iter59, iter60). NOTE: test_iter46 fast-first-flush and test_delivery assert the OLD defaults (True/True) — if they now fail as NEW reds, adapt the TESTS to the promoted defaults (tests follow the owner-ratified defaults; document in the report). Any OTHER new red = STOP, autopsy, ASK.

### T4 — ENV scrub (owner-authorized)
Commands (exact, each file ONE line edit only):
- `ssh … "sed -i 's/^WARM_AWAIT_DEST_MS=250$/WARM_AWAIT_DEST_MS=2500/' /tmp/opencode/wt-iter89/engine/.env"` then grep-verify.
- Same for /home/julio/projects/clean_diallux_SDR/engine/.env (OREGON main checkout env) — VERIFY the line is exactly `WARM_AWAIT_DEST_MS=250` first (grep), and re-grep CARTESIA_MODEL_ID after (pin intact).
- /opt prod .env: locate via the iter90 memo (memo 92/ENV-SWITCHES §4 named /opt prod; exact path: grep WARM_AWAIT_DEST_MS in /opt — `grep -rln 'WARM_AWAIT_DEST_MS=250' /opt 2>/dev/null | head -3`); edit the single line; NO service restart.
Verification: all three files show 2500; no other line changed (`git` does not track .env — use md5 before/after and diff against a cp).

### T5 — THE verification run (one GK)
Goal: prove the promoted defaults produce the iter87 profile.
Commands:
- Verify port: `ssh … "ss -ltnp | grep 8050"` (must be empty; else pick 8051+).
- Boot lane: `ssh … "cd /tmp/opencode/wt-iter91/engine && set -a && . ./.env && set +a && nohup /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python -m uvicorn diallux.app:app --host 127.0.0.1 --port 8050 > /tmp/opencode/voice_server_8050.log 2>&1 & echo \$! > /tmp/opencode/voice_8050.pid"`.
- Wait for start; verify journal line "elevenlabs connected" in the log.
- Run driver: `ssh … "cd /tmp/opencode/wt-iter89/engine && set -a && . ./.env && set +a && /home/julio/projects/clean_diallux_SDR/engine/.venv/bin/python scripts/llm_mic_caller.py --ws-url 'ws://127.0.0.1:8050/mic/ws?k='\$VOICE_TEST_TOKEN --scenario happy --persona Boris --agent-idle-s 4 --journal-log /tmp/opencode/voice_server_8050.log --out /tmp/opencode/iter91_gk_boris.json"`.
- Kill lane after: `kill \$(cat /tmp/opencode/voice_8050.pid)`; verify port free.
Verification (ground truth = server log + Langfuse, NEVER journal_lines):
  1. Server log shows "eager turn audio released at confirmed EOT" ≥1 (the hold is ALIVE) and ZERO "eager turn cancelled (user resumed)".
  2. await_warm outcomes: zero no_task; dest-entry holds ≤2500, no pathological waits.
  3. round usage lines: cache_read values in the iter87 profile (no NEW cache-0 rounds beyond the known pre-existing class).
  4. Langfuse trace: pull obs, confirm turns/rounds structure ≈ iter87 distribution.
  5. Import run: `live_sql.py import --window <HH:MM-HH:MM of run> --run iter91-gk-verify --commit <branch sha>`; verify row exists.
  6. If the GK books: cancel the booking (Cal event 3801235 law) and record it.

### T6 — Report + ASK
Goal: /home/julio/projects/clean_diallux_SDR/research/surgeon/iter91-promote-pack/01_verify_report.md — per-call table, hold/await/cache numbers vs forensics_calls 13/14 reference, verdict + any test adaptations made in T3. Then ASK JULIO: merge say-so (LAW 0), /opt prod restart timing, iter89 merge decision unchanged.
Verification: report exists; ledger row imported; owner asked in-chat.

## Validation Plan (end-to-end)
T1 docs on main → T2 diff = exactly the 9 flips → T3 stale-red set unchanged (or documented test adaptations) → T4 three envs scrubbed to 2500 (pin intact) → T5 one GK call with hold ALIVE + healthy await/cache profile → ledger row → T6 report → owner merge call.

## Deferred / Not In This Plan
| Item | Why |
|---|---|
| /opt prod service restarts | owner timing, after verdict |
| 500-vs-1000 backoff re-measure (b52 barge pass) | optional; FIND-38 stands on owner authority |
| iter89 merge decision | owner at close-out, unchanged |
| b52 driver improvements / vanilla journal_lines fix | separate; b52 not needed in-plan |
| Sam first_name gate (PT-78) | separate session |
| iter91 skeleton's "one-ahead decouple" idea | INVALIDATED by verdict (rounds were tool rounds); dead unless owner revives |
