"""Cache-survives-abort A/B probe (savage latency engineering, 2026-10-05).

Live check that OpenAI's prompt cache survives a mid-stream client abort:
one shared big prefix -> cold miss vs normal-completion hit vs post-abort hit.
Reads OPENAI_API_KEY / OPENAI_MODEL from env (never hardcode keys).
Usage: python3 cache_abort_probe.py   (costs a few cents of gpt-5.x tokens)
"""
import os, time
from openai import OpenAI

client = OpenAI()
model = os.environ.get("OPENAI_MODEL", "gpt-5.4")

para = ("Dialux ops briefing: the census block audit for roofline services enumerated "
        "per-neighborhood call handling routes, callback ladders, intake script variants, "
        "Discovery telemetry flags, Offer pricing bands and contact_details capture rules; ")
prefix = ("You are auditing an HVAC roofing outbound dialer config. Memorize the following Ops manual.\n"
          + para * 130)

question = "In one short sentence, what is this manual about?"

def run(tag, cancel_after=None):
    t0 = time.perf_counter()
    stream = client.chat.completions.create(
        model=model, stream=True, max_completion_tokens=120,
        messages=[{"role": "system", "content": prefix},
                  {"role": "user", "content": f"{question} (run {tag})"}])
    first = None
    got = 0
    try:
        for chunk in stream:
            if first is None:
                first = time.perf_counter() - t0
            got += 1
            if cancel_after and (time.perf_counter() - t0) > cancel_after:
                stream.close(); break
    except Exception as e:
        print(f"   [{tag}] stream ended: {type(e).__name__}")
    if first is None:
        first = time.perf_counter() - t0
    print(f"{tag:10s} ttft={first*1000:7.1f} ms  chunks_read={got:3d}")
    return first

print(f"prefix chars={len(prefix)} (~{len(prefix)//4} tok)\n")

cold1 = run("cold-1")
time.sleep(2)
ref1  = run("hit-ref")
time.sleep(2)
ab    = run("abort", cancel_after=1.2)
time.sleep(1)
test1 = run("after-abort")
time.sleep(2)
test2 = run("after-abort2")
time.sleep(2)
print("\n== RESULT ==")
print(f"cold baseline      : {cold1*1000:.0f} ms")
print(f"cache-hit (normal) : {ref1*1000:.0f} ms")
print(f"after-ABORT hit    : {test1*1000:.0f} ms / {test2*1000:.0f} ms")
print("after-abort ~= hit-ref  -> cache survives abort")
print("after-abort ~= cold     -> cache dies with the request")
