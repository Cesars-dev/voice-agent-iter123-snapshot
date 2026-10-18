# savage_latency — the "cancel, don't wait" latency ledger

Owner call (2026-10-05): PARKED for adoption — "we will adopt this a bit later,
I want to test what we have first." Nothing here touches the engine.

## The principle (proven in-session on real calls)

Savage engineering of the prewarm/eager stack, one rule:

> **At most one OpenAI stream per key, per moment. Cancel; never queue; never wait.**

Three states for a not-yet-done prewarm (`warm b` of the a/b/c cache design) when
the real turn c) fires:

| warm b state at transition | old behavior (promoted b250 tier) | savage behavior |
|---|---|---|
| completed | adopt (~100 ms) — unchanged | adopt (~100 ms) — unchanged |
| mid-completion (prefill done) | **wait 1,218–2,324 ms** (measured 6 losses in the iter92b battery) | **abort the completion**; the prefix cache it wrote stays on OpenAI's side (proven below); fire c) against that cache — TTFT ~ hit-class |
| pre-inflight (prefill not done) | wait | abort; fire c) as a normal uncached round (bounded downside = today's baseline) |

Aborting a completion does NOT delete the prompt cache: OpenAI writes the prefix
cache **at prefill time, server-side, keyed to the prompt prefix** (the same
mechanism the iter92 verdict found quantizing cache_read on 1024-block floors).
The completion is only decoding; the thinking is already paid for and stored.

## Proof 1 — cache survives a mid-stream abort (`cache_abort_probe.py`)

Live A/B against gpt-5.4, one shared ~7,823-token prefix, one key (2026-10-05,
OREGON lane env):

```
cold-1      ttft= 1421.0 ms   (nothing cached — baseline)
hit-ref     ttft=  913.7 ms   (normal completion -> cache hit)
abort       ttft=  853.6 ms   (stream killed at ~1.2 s, mid-completion)
after-abort ttft= 1089.7 / 857.2 ms  <-- same prefix, right after the kill
```

after-abort = **hit-class** (857 ≈ 914), nowhere near cold (1,421). The cache the
aborted request wrote during its prefill survived and the next full-payload request
read it. Caveats: n=1 per condition (second sample dead-on, first within provider
noise), same key as the live lanes.

## Proof 2 — the lost races are WAITING, not cache loss (`warm_race_audit.py`)

Full audit of the iter92b battery server log (`/tmp/opencode/voice_server_8062.log`,
run `iter92b-4gk-quant@2b3e900`): 169 `await_warm` events —

- **163 × `already_done, waited 0 ms`** — the saver worked (96%)
- **6 × `landed` after waiting 1,218 / 1,244 / 1,440 / 1,446 / 1,651 / 2,324 ms of the
  2,500 cap** — the 4% lost races. The 2,324 ms one is the owner's remembered
  "~2400 ms we lost the race" (Bianca t23 contact_details).
- Every round that followed a lost race ran at **710–957 ms TTFT with on-grid
  cache_read** — the wait is NOT in TTFT; it sits in the S→L window (caller's ear).
- The genuinely slow TTFT rounds (≥1,800 ms, 4 of 100) were **NOT cache misses**
  (cache on-grid in 3/4; they are multi-stream collisions: spec + real + one-ahead
  warm on one key — 3 concurrent streams; the same class your Retell prod control
  showed at 11/60 rounds, 1.9–4.2 s).
- Cold turn-1 (cache=0 possible) = the only true no-cache class, bounded by startup.

## Re-billing / garbage analysis (why "failure" branches are safe)

- An aborted warm writes NOTHING to state/history — adoption only accepts
  completed warm runs. No "garbage carried into the next turn".
- Cost of an abort = the input tokens of the warm's prompt (already billed at
  prefire) — output of the aborted stream is never billed.
- The saver is untouched: completed warms are adopted regardless of any cap; the
  cap only governs the still-streaming case.

## Where the ms are (measured, this stack)

| Component | Cost | Where measured |
|---|---|---|
| dest-cap wait tier (b250-class promoted by iter91 pack) | ~+90–115 ms vs b0 | iter90 A/B: `iter90-mic-b0` 765 vs `iter90-mic-b250` 880 (ledger) |
| lost-race waits | 1.2–2.4 s each, 4% of awaits | this folder audit + ledger run `iter92b-4gk-quant` |
| spec+real+warm collisions | +17–111 ms (dup-round ttft); spikes to 2–2.7 s | iter92b rounds; Retell control call_b790bb6f (11/60 spikes) |
| RAG on hot path | 85–131 ms/round (S→L plane, not TTFT) | iter92b rag spans vs iter87 round-B "RAG ms p50 0" |
| provider drift | ±50 ms | 6-day non-monotonic ttft history (iter48 ledger) |

Reference contamination note (F-92b-6): the iter87 reference battery (853/1376)
ran on **Helsinki** lanes (8047/8048) — cross-box vs today's OREGON numbers.

## Files

| File | What |
|---|---|
| `cache_abort_probe.py` | live A/B probe: cold vs hit vs after-abort, single shared prefix; reads OPENAI_* from env (no secrets in-file) |
| `warm_race_audit.py` | server-log auditor: parses await_warm / warm done / round usage, prints per-await → next-round table (outcome, wait, cache state, ttft), flags lost races and slow rounds, runs the slow-round-vs-cache claim test |

Run the audit on any lane log:
`python3 scripts/savage_latency/warm_race_audit.py /tmp/opencode/voice_server_8062.log`

## Real-data pointers (all committed or checksum-synced boxes)

- Engine evidence: `research/surgeon/iter92b-4gk-quant/{01_raw_tables,02_quant_report,03_sop_report}.md`
- Ledger: `research/surgeon/iter48-rag-truth/ledger.db` — runs `iter92b-4gk-quant` (session `iter92b-4gk-quant@2b3e900`), `iter90-mic-b0`/`iter90-mic-b250` (the tier A/B), `iter87-hold-battery` (reference, Helsinki)
- Cache mechanics: `CACHE_ANALYSIS.md` (root) — iter92 verdict + iter92b quant check section
- Retell prod control: `research/surgeon/iter92-cache-growth/retell_call_b790bb6f_raw.json` (both boxes)

## Adoption gate (owner, 2026-10-05)

PARKED. Before any adopt: re-verify under owner's current test stack, then the
candidate order is (1) warm cancel-not-wait cap (~300–400 ms), (2) eager spec
client-abort on resume (parked as "good idea — evaluate harder": iter78b re-ask
edge cases, provider abort semantics, resume_pending interplay), (3) RAG off
hot path, (4) process split (skipped — ~50–100 ms benefit, rewrite-grade risk).
