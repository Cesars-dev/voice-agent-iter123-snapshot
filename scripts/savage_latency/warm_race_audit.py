"""warm_race_audit.py — prewarm/eager race auditor for a diallux voice-server log (savage latency engineering).

Answers, from raw log lines, the three questions that decide adopt-or-not:
  1. how many prewarm awaits won (already_done) vs lost the race (landed late / cap waits)?
  2. was the caller-visible cost of a lost race a TTFT problem or an S->L (EOT->LLM) problem?
  3. are the high-TTFT rounds cache MISSES (nothing cached) or provider/concurrency spikes
     (cache present and on-grid)?

Usage: python3 warm_race_audit.py /tmp/opencode/voice_server_8062.log [--bounds name,lo,hi]
With --bounds only a line-number window is analyzed; default = whole log.
"""
import re, sys
from collections import Counter

LOG = sys.argv[1]
bounds = None
if len(sys.argv) > 3 and sys.argv[2] == "--bounds":
    name, lo, hi = sys.argv[3].split(",")
    bounds = (name, int(lo), int(hi))

lines = open(LOG, errors="replace").readlines()
if bounds:
    lines = lines[bounds[1] - 1 : bounds[2]]

ts_pat = re.compile(r"^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}),(\d{3})")
aw_pat = re.compile(r"await_warm key=(\S+) outcome=(\S+) waited_ms=(\d+) cap_ms=(\d+)")
wd_pat = re.compile(r"warm done key=(\S+) shape=(\S+) outcome=(\S+) degraded=(\S+) ms=(\d+)")
ru_pat = re.compile(r"round usage: turn=(\d+) state=(\w+) input=(\d+) cache_read=(\d+) output=(\d+) ttft=(\d+)ms")

def tsec(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

events = []
for i, raw in enumerate(lines):
    m = ts_pat.match(raw)
    if not m:
        continue
    t = tsec(m.group(4), m.group(5), m.group(6), m.group(7))
    aw = aw_pat.search(raw)
    wd = wd_pat.search(raw)
    ru = ru_pat.search(raw)
    if aw:
        events.append(("aw", t, dict(key=aw.group(1), outcome=aw.group(2), wait=int(aw.group(3)), cap=int(aw.group(4)), line=i)))
    elif wd:
        events.append(("wd", t, dict(key=wd.group(1), shape=wd.group(2), wout=wd.group(3), ms=int(wd.group(5)), line=i)))
    elif ru:
        events.append(("ru", t, dict(turn=int(ru.group(1)), state=ru.group(2), input=int(ru.group(3)),
                                     cache=int(ru.group(4)), output=int(ru.group(5)), ttft=int(ru.group(6)), line=i)))

rounds = [e for e in events if e[0] == "ru"]
aws    = [e for e in events if e[0] == "aw"]
wds    = [e for e in events if e[0] == "wd"]
label = bounds[0] if bounds else "full log"

print(f"== {label} ==  await_warm={len(aws)}  warm_done={len(wds)}  rounds={len(rounds)}\n")
print("await_warm outcomes:", Counter(e[2]["outcome"] for e in aws))
lost = [e for e in aws if e[2]["outcome"] != "already_done"]
print(f"lost races (outcome != already_done): {len(lost)}")
for e in sorted(lost, key=lambda x: x[2]['wait'], reverse=True):
    print(f"   wait={e[2]['wait']:5d}ms / cap={e[2]['cap']}  key={e[2]['key']}  @line {e[2]['line']}")
print()

def next_round_after(t, maxdt=6.0):
    for e in rounds:
        if e[1] >= t and e[1] - t <= maxdt:
            return e
    return None

print(f"{'time_s':>9} {'key':16} {'outcome':13} {'wait':>5} -> next round: turn state cache uncached ttft")
for e in aws:
    nr = next_round_after(e[1])
    if not nr:
        continue
    r = nr[2]
    unc = r["input"] - r["cache"]
    print(f"{e[1] % 3600:9.2f} {e[2]['key']:16} {e[2]['outcome']:13} {e[2]['wait']:5d} -> t{r['turn']:2d} {r['state']:16} {r['cache']:5d} {unc:5d} {r['ttft']:5d}ms")

print("\n== high-TTFT rounds (>=1800ms): cache state + preceding await/warm context ==")
for e in rounds:
    t, r = e[1], e[2]
    if r["ttft"] < 1800:
        continue
    unc = r["input"] - r["cache"]
    ongrid = r["cache"] and (r["cache"] - 640) % 1024 == 0
    before = [x for x in aws + wds if t - 6 <= x[1] <= t]
    after  = [x for x in aws + wds if t < x[1] <= t + 6]
    print(f"\nround turn={r['turn']} {r['state']} ttft={r['ttft']}ms input={r['input']} cache={r['cache']} uncached={unc} ongrid={'YES' if ongrid else ('COLD' if r['cache']==0 else 'no')}")
    for kind, tt, d in before:
        tag = f"await({d['outcome']},wait={d['wait']})" if kind == "aw" else f"warm-done(shape={d['shape']},ms={d['ms']})"
        print(f"   BEFORE {tag} {d['key']}")
    for kind, tt, d in after[:1]:
        tag = f"await({d['outcome']},wait={d['wait']})" if kind == "aw" else f"warm-done(shape={d['shape']},ms={d['ms']})"
        print(f"   AFTER  {tag} {d['key']}")

print("\n== CLAIM TEST: slow rounds vs cache presence ==")
hi = [(r["input"] - r["cache"], r["cache"]) for e in rounds for r in [e[2]] if e[2]["ttft"] >= 1800]
lo = [(r["input"] - r["cache"], r["cache"]) for e in rounds for r in [e[2]] if e[2]["ttft"] < 800]
for lbl, grp in (("ttft>=1800", hi), ("ttft<  800", lo)):
    if not grp:
        continue
    avg_unc = sum(g[0] for g in grp) / len(grp)
    ongrid = sum(1 for g in grp if g[1] and (g[1] - 640) % 1024 == 0)
    print(f"{lbl}: n={len(grp):3d}  avg_uncached={avg_unc:6.0f} tok  cache on-grid={ongrid}/{len(grp)}")
