# 01_audit — iter97 implementation (loop hygiene T1–T3 + T4-eval; iter98 service_tier)

Procedure: `tasks/surgeon/iter97-implementation/` · Date: 2026-10-08
Code base: **main @ `61bfc7e`** (FI and OR synced, verified this session) — the exact base the branch will be cut from.
Owner plan source: `/home/julio/projects/vps-inbox/IDE_AGENT_PROMPT_latency_fixes_1_3 2.md` (verbatim copy: `/tmp/opencode/iter97_owner_plan_source.md`, archived at `tasks/surgeon/iter97-implementation/archive/`).
Baseline report evaluated against: `/home/julio/projects/clean_diallux_SDR/research/surgeon/iter97-research-adaptation/97_analysis.md` (session-1, six verdicts).

Owner verdicts locked (2026-10-08, this session):
- Fix 1 (loop hygiene): RUN T1–T3, then MEASURE. T4 (raw SDK speak path) NOT built — only evaluated for worthiness from T1 data.
- Fix 2 (service_tier): APPROVED. env knob + kwargs plumbing. Measured case: 97_analysis #3 (300–500ms mean TTFT + variance collapse, cross-tier cache read preserved).
- Fix 3 (TTS bake-off): REJECTED by owner ("dumb, not a gain"). iter99 = stale, never cut.
- Branching: ONE cut per fix. iter97 lane/branch first; iter98 cut FROM THE TIP of iter97 (owner overrides the LAW 0 v2.1 no-stacking clause — owner directive on record).

---

## A. What EXISTS (verified at `61bfc7e`, all file:line real)

### Turn clock + reports
| Thing | Anchor | State |
|---|---|---|
| `TurnClock` dataclass | `/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/latency.py:17` | fields: `t_user_end`, `t_llm_first`, `t_tts_first`, `t_audio_out`, `t_turn_done`, `t_barge_in`, `extra`; marks at `:28–32` |
| `report()` keys | `latency.py:34–51` | `stt_eot_to_llm_first_ms`, `llm_first_to_tts_first_ms`, `tts_first_to_audio_out_ms`, `e2e_response_ms`, `e2e_turn_ms`, `barge_in[_at_ms]`, `**extra` — **NO dispatch decomposition** |
| Late report extras | `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:904–931` | `resumed_count` `:912`, `held_swallow` `:915–922`, `rag_consume` `:923–926` — **no `bench_aliases`** |

### Round loop (builder)
| Thing | Anchor |
|---|---|
| `t0 = time.perf_counter()` | `/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/builder.py:2287` (just above `tracer.start_llm` `:2288`) |
| LLM stream open | `builder.py:2317` (`async for ev in runtime.llm.astream(...)`) |
| ttft anchor (first delta of ANY type, iter87 T1.4) | `builder.py:2322` (`if ttft_s is None`) |
| `writer = get_stream_writer()` | `builder.py:1801` (round loop head; second writer at `:2718`) |
| existing custom events | `writer({"tts_token": ...})` at `:2326, :2407, :2427, :2494, :2565, :2758` |
| round-usage log line (`ttft=%s`) | `builder.py:2453` |

### Session media path
| Thing | Anchor | State |
|---|---|---|
| `_run_turn` custom-event branch | `/home/julio/projects/clean_diallux_SDR/engine/diallux/media/session.py:877–880` | condition `mode == "custom" and "tts_token" in data`; first-only `mark_llm_first` at `:878–879`; gate.add epoch-tagged `:880` |
| `on_media` | `session.py:345–353` | inline `await self.stt.send_audio(_b64decode(...))` |
| `start()` task spawn | `session.py:214–218` | `_writer_task` `:214`; `_liveness_task` `:215–218` (gated on `stt_rx_zombie_ms`) |
| `stop()` cancellation | `session.py:298–304` | cancels `_liveness_task` |
| class-level task-default pattern | `session.py:368–369` (`_ladder_task`/`_ladder_step` class attrs) — the pattern to copy for `_media_queue` |
| `__init__` | `session.py:90–158` | no media queue today |

### WS readers (app)
| Thing | Anchor | State |
|---|---|---|
| Twilio `/media` reader | `/home/julio/projects/clean_diallux_SDR/engine/diallux/app.py:144–185` | inline `json.loads` `:153`, `await session.on_media(payload)` `:170` — **no queue, no interarrival stamp** |
| `/mic/ws` reader | `app.py:196–244` | `MIC_CHUNK_INTERARRIVAL_MS` stamped receive-side `:220–223`; `await session.on_media(b64)` `:225`; VOICE_TEST_TOKEN gate `:200–206` |
| `/health` | `app.py:88–112` | no `event_loop` field, no `service_tier` field |
| `_lifespan` | `app.py:36–58` | no loop-type logging |

### Metrics
`/home/julio/projects/clean_diallux_SDR/engine/diallux/observability/metrics.py`: 6 latency histograms `:21–38`, `MIC_CHUNK_INTERARRIVAL_MS` `:40–42` (buckets 20/35/50/65/80/100/150/200/300/500), counters `:44–48`, `observe_turn_report` `:51–61`. **Missing**: dispatch/first-event histograms, Twilio interarrival, media-lane drop counter.

### Config
`/home/julio/projects/clean_diallux_SDR/engine/diallux/config.py`: LLM section `:37–49` (`openai_model="gpt-5.4"` `:42`, `openai_temperature` `:43`, `openai_verbosity="medium"` `:45`); section style `# ---- name ----`; **two** "V2 production" sections `:447` + `:463` (the known duplication — new flags go in their OWN section, never either copy); `tts_gate_fast_first_flush: bool = False` `:207` (PT-71 — untouched). **Missing**: iter97 section, `media_frame_lane`, `openai_service_tier`.

### LLM construction (llm.py)
`/home/julio/projects/clean_diallux_SDR/engine/diallux/graph/llm.py`:
| Site | Anchor | Notes |
|---|---|---|
| `_REASONING_MODEL_RE` | `:30` | gpt-5* / o1/3/4 |
| `shared_llm_http_client()` | `:40–47` | the ONE warmed httpx pool |
| `llm_boot_prewarm()` | `:50–76` | own ChatOpenAI + own mk (`:59–69`), `max_completion_tokens=16` — a THIRD construction site |
| `StreamingLLM.__init__` | `:216–263` | **mk built ONLY inside `if _REASONING_MODEL_RE.match()` `:231–238`; attached only when non-empty `:237–238`**; `self._llm` `:244` (`stream_usage=True`); `_warm_llm` `:257–263` inherits `**kwargs` |
| `llm_for_verbosity` lazy twins | `:265–286` | SECOND mk site `:279–283` |
| `warm()` | `:288+` | uses `_warm_llm` (bind_tools) |
| `service_tier` | grep: **zero hits repo-wide** | confirmed absent |

### Launch surfaces (uvloop)
- `/home/julio/projects/clean_diallux_SDR/engine/deploy/diallux.service` ExecStart: `uvicorn diallux.app:app --host 127.0.0.1 --port 8000` (no `--loop`).
- `/home/julio/projects/clean_diallux_SDR/engine/Dockerfile:17` CMD uvicorn (no `--loop`).
- `requirements.txt`: `uvicorn[standard]>=0.32` — **uvloop NOT pinned explicitly**; the `[standard]` extra installs it, so uvicorn may ALREADY auto-select it.
- OR lanes boot as bare background `uvicorn diallux.app:app --host 127.0.0.1 --port NNNN` (live ps evidence: 8049/8026/8090).

### Tooling
- `/home/julio/projects/clean_diallux_SDR/scripts/fast_suite.sh` — whitelist-lane tool; `--touched` auto-selects touched test files + importers of changed diallux modules; a `diallux/config.py` change forces the FULL suite; no named pin groups.
- `/home/julio/projects/clean_diallux_SDR/scripts/new_lane.sh` — `new_lane.sh <numeric-iterNN> <base-sha-or-branch> <slug>` → worktree `/tmp/opencode/wt-<NN>` + branch `engine/<NN>-<slug>` + venv symlink + canonical `.env` + audit gate. **Numeric guard refuses "iter97"** (must pass `97`). Precedent: iter96 lane branch = `engine/96-delta-cache-layout` @ `/tmp/opencode/wt-96`.
- Suite baseline: **516 passed / 1 skipped / 5 failed** (pre-existing reds, identical on main tip). `tests/conftest.py:15–19` pins `env_file=None` (hermetic).
- Probes exist: `/home/julio/projects/clean_diallux_SDR/engine/scripts/llm_mic_caller.py` (`--ws-url`, `--scenario happy`, `--max-caller-turns`, `--journal-log`) and `/home/julio/projects/clean_diallux_SDR/engine/scripts/latency.py` (`--hours`, `--name`, `--json`).

## B. What's MISSING (the gaps the fix fills)
1. `stt_eot→llm_dispatch` and `llm_dispatch→first_event` decomposition: TurnClock fields/marks, report keys, builder writer events, metrics histograms. (Today only the merged `stt_eot_to_llm_first_ms` exists — the 250–350ms adder is invisible.)
2. Twilio-path media interarrival observability (mic path has it; phone path does not).
3. Media frame lane: inbound frames are parsed/decoded inline in the WS-reader coroutine (head-of-line risk under LLM/TTS load).
4. uvloop pin + `/health` proof (today: unpinned, unproven — may already be active via `uvicorn[standard]`).
5. `openai_service_tier` knob + hoisted mk (absent repo-wide).
6. fast_suite named pin groups for the new iteration tests.

## C. Risks / bugs found (each is addressed in 02)
- **R1 — byte-parity trap (iter98):** `model_kwargs` is attached only when non-empty (`llm.py:237–238`). Hoisting mk so `service_tier` applies to ALL models must keep the flag-off serialization byte-identical (attach-only-when-non-empty preserved) or the prompt cache prefix breaks (iter43 class). Pin with a byte-equality test.
- **R2 — third construction site:** `llm_boot_prewarm` builds its own client. Tier deliberately NOT applied there (16 throwaway tokens at 2x is waste; cross-tier cache read is preserved — 97_analysis measured 5,888/5,888).
- **R3 — eager-EOT anchoring:** `stt_eot_to_llm_first_ms` is EagerEOT-anchored when eager is on (`session.py:478` comment). The new dispatch metric inherits the same base; tests must not assume plain-EOT anchoring.
- **R4 — mic stamp order:** `/mic/ws` interarrival stamp must stay on the receive side, BEFORE any enqueue (else the queue's backpressure corrupts the measurement).
- **R5 — drop-oldest frame loss:** under sustained overload the lane drops frames by design — guarded by the dropped-frames counter, one WARNING per burst, and the A/B exit gate `dropped == 0`.
- **R6 — no-`__init__` test pattern:** some tests build sessions without `__init__`; all new session state must be class-level defaults (copy the `_ladder_task` pattern `session.py:368–369`).
- **R7 — uvloop may already be active** via `uvicorn[standard]`: T2's gate is honest proof (`/health` before/after); if already uvloop, record it and make NO latency claim for T2.
- **R8 — one-loop discipline:** the drain task is a NEW consumer on the same loop; law = ONE queue, ONE drain task, no other consumer touches `_media_queue`.
- **R9 — anchor drift in the owner plan:** it quotes an iter96-era snapshot (e.g. builder `:2403/:2439` → real `:2287/:2322`; "search `tts_token in data`" → real condition `session.py:877`). All anchors above are re-verified at `61bfc7e`; executing agents re-grep before editing.

## D. Known-bad ideas explicitly NOT in scope (owner + evidence)
- `tts_gate_fast_first_flush=true` — REJECT (PT-71 battery failure; 97_analysis #2).
- TTS bake-off / provider flip — owner-rejected 2026-10-08; Voice LAW (EL default) stands.
- Mouth/brain split (M1/M2/M3) — owner-deferred.
- Warm-knob tightening — REJECT-as-proposed (iter95 savage supersedes; 97_analysis #5).
- Deepgram EOT knob values — owner-set, out of agent hands.
