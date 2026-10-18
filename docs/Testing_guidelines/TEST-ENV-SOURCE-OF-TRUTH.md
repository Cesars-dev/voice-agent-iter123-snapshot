# TEST + ENV — SINGLE SOURCE OF TRUTH (v1)

> Created 2026-10-18 (iter123). Purpose: **one absolute path** for "what passes, what doesn't,
> and WHY" — so nobody has to infer a red count from a stale log again.
> Owned by the test-infra lane. Regenerate with the commands in §5.

---

## 1. THE ONLY VALID WAY TO MEASURE (law)

A red count is meaningless unless it is measured against the **untouched base commit, today**:

```bash
# base (the commit the branch is cut from), in its own lane/worktree:
cd <repo>/engine && <repo>/scripts/fast_suite.sh --full      # background + tail every 30s
# branch: same command in the branch lane
# DIFF the two FAILED sets. "N red" claims in plans/logs are NOT evidence.
```

**Why:** on 2026-10-18 the plan claimed "exactly the carried 7 red"; the untouched baseline actually
read **48**. Root cause: `conftest.py` killed `.env` only via a per-test fixture, so module-level
`Settings(...)` (built at import/collection time, e.g. `test_iter30_fast.py:27`) still read the lane
`.env` (`speak_first_pipeline=True`, `speak_model=gpt-5.6-luna`, `max_call_turns=128`) → the split arm
fired inside pre-split fakes (`TypeError: astream() got 'speak'`, `fake_llm.py:41 pop from empty`).
Fixed at collection time via `pytest_configure` (`c4a287a`). Baseline then read **7** — the claim was
right, the measurement was broken.

## 2. HERMETICITY LAW (standing)

- The suite result MUST NOT depend on which `.env` sits in the worktree.
- `conftest.pytest_configure` neutralizes `Settings.env_file` for the WHOLE session (collection-time).
- A test that needs real creds/network opts in explicitly.
- A test that "passes only with ambient env" is a **bug in the test** (paid lesson: iter44_dead_store).

## 3. CURRENT NUMBERS (2026-10-18, iter123 branch `engine/123-merge-slots-retrieval`)

| | collected | red | passed |
|---|---|---|---|
| Base `6cad81a` (+ hermeticity fix) | ~719 | **7** | 711 |
| iter123 branch | ~719 | **7** | 711 |

**Zero net regressions.** The iter123 design pins (6) were updated to the new contract in `68818f7`.

## 4. THE GENUINE 7 (pre-existing, carried) — verdicts

| Test | Failure | Verdict |
|---|---|---|
| `iter48::test_eot_and_midturn_entry_awaits_split_caps` | expects a ≥0.5s warm-await, gets ~0 | STALE PIN — awaits are config-gated (default-off knobs); pins a disabled mode |
| `iter48::test_lite_round_awaits_lite_warm` | same | STALE PIN |
| `iter48::test_await_warm_none_uses_midturn_flag_and_shield` | expects 60ms mid-turn await, gets ~0 | STALE PIN |
| `iter55::test_await_warm_timeout_keeps_warm_alive` | span outcome `aborted` ≠ `timeout` | STALE PIN |
| `iter114d::test_speak_warm_parallel_with_full_warm` | warm-parallel shape | STALE PIN |
| `iter31::test_head_byte_stable_across_calls_and_dvs_literal` | head prefix ≠ constant | LAYOUT PIN — head build changed across iters |
| `iter65::test_validator_parity_daily_case` | `weekly_leak` None ≠ `$6,500` | MOCK PARITY — mock validator's daily-case math |

None indicate production behaviour breakage; all are candidates for the pin-retirement pass (§6).

## 5. ENV VALUES — one register, one ritual

- **The register:** `docs/Testing_guidelines/ENV-SWITCHES.md` (every switch: field, code default,
  resolved-today, what it owns, trip-wire). iter123 added `LINEAR_STATES`, `RAG_RENDER_CHAR_BUDGET`,
  and the `SLOTS_PREFETCH` flip.
- **The ritual (SWITCH LAW):** every run/battery snapshots its RESOLVED switch set next to the evidence
  and diffs vs prod + the previous passing run. A behavioural-switch diff between two runs = the
  comparison is VOID until explained.
- **Code default == tested value** for load-bearing switches (default-off for a tested design = the bug).
- `.env` values are owner-set only; agents never edit them.

Regenerate the register's "resolved today" column:
`cd <repo>/engine && .venv/bin/python -c "from diallux.config import Settings;print(Settings().model_dump_json(indent=1))"`

## 6. PIN LIFECYCLE RULE (proposed — needs owner ratification)

1. **A design change updates or deletes its pins in the SAME commit.** A pin is a contract; changing
   the contract changes the pin.
2. **A pin whose contract no longer exists is DELETED, never "fixed".**
3. **Stale pins found later are retired in a dedicated pin-audit commit** on the test-infra lane —
   measured (§1), classified, one verdict per pin.
4. **Every pin names its contract and owning iteration** in the docstring (the good pattern already in
   `test_iter112`/`test_iter118`).
5. **A "carried red" claim must cite a base-vs-branch diff from the same day** — never a log file.

### Regeneration (authoritative commands)
```bash
cd <repo>/engine
.venv/bin/python -m pytest tests -q > /tmp/suite.log 2>&1      # or scripts/fast_suite.sh --full
grep "^FAILED" /tmp/suite.log | sed 's/ - .*//' | sort          # the red set, for a base-vs-branch diff
```
