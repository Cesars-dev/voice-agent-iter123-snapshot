"""iter121 — TransitionGate M3 (transition-ride guard) pins.

Cosmetic feature name: "TransitionGate M3". Env knobs keep their names:
  m2_mouth_watch_states  (default "Intake,Discovery,Closer,Offer")
  m2_mouth_watch_fence_ms (default 600)

Group 1 (builder, graph fake harness — mirrors test_iter112_speak_first):
  1  knob defaults
  2  blank watch-state arms the watch (not the tail): arm signal + registry
  2b the watch list is honored per state (default arms Discovery; narrowed tails)
  3  transition fires -> verdict "discard" emitted at the boundary
  4  packet lands without a transition -> verdict "release"
  5  empty watch list -> byte-exact legacy tail
  6  a value/transition-flagged batch still AWAITS (door 2)
  7  iter112 static pin: no wait_for/timeout in the merge paths

Group 2 (session/gate muzzle — real SentenceGate + a recording sink):
  8  candidate muted, ACK (same epoch) speaks
  9  no-signal release speaks the candidate
  10 at-most-once: a late discard after release is a no-op
  11 fence releases a held line; a later discard is a no-op
  12 cross-turn ticket: discard(N) drops the candidate, ticket N+1 flows
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.media.sentence_gate import SentenceGate

# --------------------------------------------------------------------------- #
# Group 1 helpers (mirror test_iter112)
# --------------------------------------------------------------------------- #
import json

from diallux.graph.builder import CallRuntime
from diallux.observability.latency import TurnClock
from diallux.graph.llm import StreamingLLM
from tests.fake_llm import FakeLLM, tool_call
from tests.mock_webhooks import mock_client

ROOT = Path(__file__).resolve().parents[1]
LLM_JSON = json.loads((ROOT / "agent" / "llm.json").read_text())
PERSONA = {"first_name": "Maria", "last_name": "Gonzales",
           "company_name": "Bright Smile Dental",
           "prospect_timezone": "America/Chicago",
           "callback_number": "+13124001234"}


def _settings(first_turn_lite=False, **kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=first_turn_lite)
    base.update(kw)
    return Settings(**base)


class SpeakFirstFakeLLM:
    def __init__(self, speak_rounds, tools_rounds):
        self.speak_rounds = list(speak_rounds)
        self.tools_rounds = list(tools_rounds)
        self.calls: list[dict] = []

    async def astream(self, messages, tools, verbosity="", speak=False,
                      speak_model: str = "", max_completion_tokens: int = 0):
        kind = "speak" if speak else "tools"
        queue = self.speak_rounds if speak else self.tools_rounds
        script = queue.pop(0) if queue else {"tokens": [], "tool_calls": []}
        self.calls.append({"kind": kind, "speak": speak,
                           "speak_model": speak_model,
                           "tools": [t["function"]["name"] for t in tools],
                           "messages": list(messages)})
        delay = float(script.get("delay") or 0.0)
        if delay:
            await asyncio.sleep(delay)
        for tok in script.get("tokens", []):
            yield {"type": "token", "text": tok}
        for tc in script.get("tool_calls", []):
            yield {"type": "tool_call_start", "name": tc["name"]}
        usage = script.get("usage") or {"input_tokens": 100, "output_tokens": 20,
                                        "total_tokens": 120}
        yield {"type": "final", "content": "".join(script.get("tokens", [])),
               "tool_calls": script.get("tool_calls", []), "usage": usage}


async def _run_turn(rt, call_id, text, first=False, persona=None, state=None):
    config = {"configurable": {"thread_id": call_id}}
    payload = {"user_text": text}
    if first:
        payload.update(rt.initial_state(call_id, persona))
    if state:
        payload["state_name"] = state
    custom: list[dict] = []
    async for mode, data in rt.graph.astream(payload, config=config,
                                             stream_mode=["custom", "updates"]):
        if mode == "custom" and isinstance(data, dict):
            custom.append(data)
    values = (await rt.graph.aget_state(config)).values
    return custom, values


def _run_turns(rt, call_id, texts, persona=None, state=None, settle=0.0):
    async def go():
        out = []
        for i, t in enumerate(texts):
            out.append(await _run_turn(rt, call_id, t, first=(i == 0),
                                       persona=persona,
                                       state=state if i == 0 else None))
        if settle:
            await asyncio.sleep(settle)
        return out
    return asyncio.run(go())


def _make_rt(settings, fake):
    return CallRuntime(settings, LLM_JSON, tracer=None, llm=fake,
                       http_client=mock_client())


def _watch_events(custom_events_flat):
    return [e for e in custom_events_flat if "mouth_watch" in e]


# --------------------------------------------------------------------------- #
# Group 1 — builder
# --------------------------------------------------------------------------- #
def test_m3_knob_defaults():
    s = Settings(openai_api_key="test", retell_api_key="test", langfuse_enabled=False)
    assert s.m2_mouth_watch_states == "Intake,Discovery,Closer,Offer"
    assert int(s.m2_mouth_watch_fence_ms) == 600


def _blank_closer_two_turn_rt(watch_states=None):
    """Turn 1 in Closer fires a tools stream that stays BLANK past turn 2's
    ingest, then lands a stage packet (transition_to_Offer)."""
    kw = dict(speak_first_pipeline=True, speak_model="gpt-4.1")
    if watch_states is not None:
        kw["m2_mouth_watch_states"] = watch_states
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["one moment."]},
                      {"tokens": ["Let me pull that up."]}],
        tools_rounds=[{"tool_calls": [tool_call("transition_to_Offer", {}, "t1")],
                       "delay": 0.25},     # blank at turn-2 ingest, lands later
                      {"tool_calls": []}],
    )
    rt = _make_rt(_settings(**kw), fake)
    return rt, fake


def test_m3_blank_watch_state_arms_not_tails(caplog):
    rt, fake = _blank_closer_two_turn_rt()
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        (c1, _), (c2, _) = _run_turns(
            rt, "s-121-a", ["hi there", "go on"], persona=PERSONA,
            state="Closer", settle=0.4)
    evs = _watch_events(c1 + c2)
    assert {"mouth_watch": "arm"} in evs or any(
        e.get("mouth_watch") == "arm" for e in evs)
    assert rt._tail_pending == []                       # not tailed
    assert any("how=watched" in r.getMessage() for r in caplog.records)


def test_m3_watch_list_is_honored(caplog):
    # narrowed to Closer -> a Discovery blank tails
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["ok."]}, {"tokens": ["right."]}],
        tools_rounds=[{"tool_calls": [tool_call("transition_to_Closer", {}, "t")],
                       "delay": 0.25}, {"tool_calls": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model="gpt-4.1",
                            m2_mouth_watch_states="Closer"), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "s-121-b", ["hi", "go"], persona=PERSONA,
                   state="Discovery", settle=0.4)
    assert any("how=tailed" in r.getMessage() for r in caplog.records)


def test_m3_fired_discard_verdict():
    # Intake->Discovery passes the transition hard gate with intake_completed.
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["one moment."]}, {"tokens": ["got it."]}],
        tools_rounds=[{"tool_calls": [tool_call("transition_to_Discovery", {}, "t1")],
                       "delay": 0.25}, {"tool_calls": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model="gpt-4.1"), fake)
    persona = {**PERSONA, "inbound_channel": "Facebook/Meta ad",
               "interest_topic": "missed calls", "pain_frame": "losing callers",
               "intake_completed": True}

    async def go():
        out = []
        out.append(await _run_turn(rt, "s-121-c", "hi", first=True,
                                   persona=persona, state="Intake"))
        out.append(await _run_turn(rt, "s-121-c", "go"))
        await asyncio.sleep(0.4)                  # packet lands -> verdict set
        out.append(await _run_turn(rt, "s-121-c", "and then"))  # boundary emits
        return out

    runs = asyncio.run(go())
    evs = [e.get("mouth_watch") for (c, _) in runs for e in _watch_events(c)]
    assert "arm" in evs
    assert "discard" in evs


def test_m3_no_signal_release_verdict():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["ok."]}, {"tokens": ["sure."]}],
        tools_rounds=[{"tool_calls": [], "delay": 0.25},   # blank then empty
                      {"tool_calls": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model="gpt-4.1"), fake)

    async def go():
        out = []
        out.append(await _run_turn(rt, "s-121-d", "hi", first=True,
                                   persona=PERSONA, state="Closer"))
        out.append(await _run_turn(rt, "s-121-d", "go"))
        await asyncio.sleep(0.4)
        out.append(await _run_turn(rt, "s-121-d", "and then"))
        return out

    runs = asyncio.run(go())
    evs = [e.get("mouth_watch") for (c, _) in runs for e in _watch_events(c)]
    assert "arm" in evs
    assert "release" in evs


def test_m3_empty_list_is_legacy_tail(caplog):
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["ok."]}, {"tokens": ["sure."]}],
        tools_rounds=[{"tool_calls": [tool_call("transition_to_Offer", {}, "t")],
                       "delay": 0.25}, {"tool_calls": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model="gpt-4.1",
                            m2_mouth_watch_states=""), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "s-121-e", ["hi", "go"], persona=PERSONA,
                   state="Closer", settle=0.4)
    assert any("how=tailed" in r.getMessage() for r in caplog.records)


def test_m3_flagged_batch_still_awaits(caplog):
    # tools stream emits the transition BEFORE turn-2 ingest (short delay) ->
    # saw_transition True -> door 2 await (not watched, not tailed).
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["ok."], "delay": 0.2}, {"tokens": ["got it."]}],
        tools_rounds=[{"tool_calls": [tool_call("transition_to_Offer", {}, "t")],
                       "delay": 0.0}, {"tool_calls": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model="gpt-4.1"), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "s-121-f", ["hi", "go"], persona=PERSONA,
                   state="Closer", settle=0.2)
    assert not any("how=watched" in r.getMessage() for r in caplog.records)


def test_m3_no_wait_for_in_merge_paths_still_holds():
    import inspect
    from diallux.graph import builder as B
    for fn in (B.CallRuntime._fire_split_tools,
               B.CallRuntime._execute_deferred_tools,
               B.CallRuntime._split_close_pending):
        src = inspect.getsource(fn)
        assert "wait_for" not in src, fn.__name__
        assert "timeout" not in src, fn.__name__


# --------------------------------------------------------------------------- #
# Group 2 — session/gate muzzle (real SentenceGate + recording sink)
# --------------------------------------------------------------------------- #
class _Sink:
    def __init__(self):
        self.spoken: list[str] = []

    async def __call__(self, text: str, continue_: bool):
        if text:
            self.spoken.append(text)


def _gate():
    sink = _Sink()
    g = SentenceGate(sink, managed=False, flush_len=500)
    return g, sink


def test_m3_candidate_muted_ack_speaks():
    async def go():
        g, sink = _gate()
        g.watch_arm(epoch=1, fence_ms=0)
        g.add("This is the old state line.", epoch=1)      # candidate (buffered)
        await g.watch_resolve("discard")
        g.add("Great, moving on now.", epoch=1)            # ACK (same epoch)
        await g.end_of_turn()
        return sink.spoken
    spoken = asyncio.run(go())
    assert any("moving on" in s for s in spoken)
    assert not any("old state" in s for s in spoken)


def test_m3_no_signal_release_speaks_candidate():
    async def go():
        g, sink = _gate()
        g.watch_arm(epoch=1, fence_ms=0)
        g.add("This is the old state line.", epoch=1)
        await g.watch_resolve("release")
        await g.end_of_turn()
        return sink.spoken
    spoken = asyncio.run(go())
    assert any("old state" in s for s in spoken)


def test_m3_ack_never_muzzled_at_most_once():
    async def go():
        g, sink = _gate()
        g.watch_arm(epoch=1, fence_ms=0)
        g.add("candidate line here.", epoch=1)
        await g.watch_resolve("release")                   # resolved once
        g.add("the ack line is safe.", epoch=1)            # ACK buffer
        r = await g.watch_resolve("discard")               # late -> ignored
        await g.end_of_turn()
        return sink.spoken, r
    spoken, r = asyncio.run(go())
    assert any("ack line is safe" in s for s in spoken)
    assert r == "ignored"


def test_m3_fence_releases():
    async def go():
        g, sink = _gate()

        async def on_fence(ep):
            await g.watch_resolve("release")

        g.watch_arm(epoch=1, fence_ms=30, on_fence=on_fence)
        g.add("a held line that wants out.", epoch=1)       # readiness -> fence
        await asyncio.sleep(0.1)                            # fence fires
        r = await g.watch_resolve("discard")                # late -> ignored
        await g.end_of_turn()
        return sink.spoken, r
    spoken, r = asyncio.run(go())
    assert any("wants out" in s for s in spoken)
    assert r == "ignored"


def test_m3_cross_turn_ticket():
    async def go():
        g, sink = _gate()
        g.watch_arm(epoch=1, fence_ms=0)
        g.add("stale candidate text.", epoch=1)
        await g.end_of_turn()                               # turn 1 ends held
        g.advance(2)
        await g.watch_resolve("discard")                    # drops epoch 1
        g.add("fresh ack text on turn two.", epoch=2)
        await g.end_of_turn()
        return sink.spoken
    spoken = asyncio.run(go())
    assert any("fresh ack" in s for s in spoken)
    assert not any("stale candidate" in s for s in spoken)


# --------------------------------------------------------------------------- #
# T5b — the TransitionGate M3 tracking span is LIVE (flush_before_arm)
# --------------------------------------------------------------------------- #
def test_m3_arm_span_records_flush_before_arm():
    from unittest.mock import MagicMock
    from diallux.media.session import CallSession

    sess = CallSession.__new__(CallSession)
    g, sink = _gate()
    sess.gate = g
    sess.settings = _settings(m2_mouth_watch_fence_ms=600)
    sess.tracer = MagicMock()
    sess._watch_hold_epoch = None

    async def go():
        # epoch 2 already flushed a sentence to TTS before the arm
        g.add("an already flushed sentence here.", epoch=2)
        await sess._on_mouth_watch({"mouth_watch": "arm", "state": "Closer"}, 2)
        await g.close()

    asyncio.run(go())
    names = [c.args[0] for c in sess.tracer.span.call_args_list]
    assert "iter121:transitiongate-m3" in names
    meta = sess.tracer.span.call_args_list[0].kwargs["metadata"]
    assert meta["phase"] == "arm"
    assert meta["state"] == "Closer"
    assert meta["flush_before_arm"] is True        # the tracked metric


def test_m3_arm_span_flush_false_when_clean():
    from unittest.mock import MagicMock
    from diallux.media.session import CallSession

    sess = CallSession.__new__(CallSession)
    g, sink = _gate()
    sess.gate = g
    sess.settings = _settings(m2_mouth_watch_fence_ms=600)
    sess.tracer = MagicMock()
    sess._watch_hold_epoch = None

    async def go():
        await sess._on_mouth_watch({"mouth_watch": "arm", "state": "Closer"}, 1)
        await g.close()

    asyncio.run(go())
    meta = sess.tracer.span.call_args_list[0].kwargs["metadata"]
    assert meta["flush_before_arm"] is False        # expected 0 on the battery
