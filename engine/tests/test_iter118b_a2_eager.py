"""iter118b A2 — eager round = speak-only (stage on speculative, fire on adopt).

A speculative (EagerEOT) round stages its tools (no API call); the confirmed
EOT adopt fires them; a discard pays zero tools; confirmed rounds are
byte-identical to today; the speculative marker never leaks across turns.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from tests.fake_llm import tool_call
from tests.test_iter112_speak_first import (
    PERSONA, SpeakFirstFakeLLM, _make_rt, _run,
)


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


async def _run_speculative(rt, call_id: str, text: str, persona=None):
    config = {"configurable": {"thread_id": call_id}}
    payload = {"user_text": text, "speculative_turn": True}
    payload.update(rt.initial_state(call_id, persona))
    custom: list = []
    async for mode, data in rt.graph.astream(payload, config=config,
                                             stream_mode=["custom", "updates"]):
        if mode == "custom" and isinstance(data, dict):
            custom.append(data)
    values = (await rt.graph.aget_state(config)).values
    return custom, values


def _kinds(fake) -> list[str]:
    return [c["kind"] for c in fake.calls]


def test_speculative_round_fires_speak_only():
    async def go():
        fake = SpeakFirstFakeLLM(
            speak_rounds=[{"tokens": ["Got it."]}],
            tools_rounds=[{"tool_calls": [
                tool_call("extract_intake_details", {"inbound_channel": "ad"},
                          "t1")]}])
        rt = _make_rt(_settings(speak_first_pipeline=True), fake)
        await _run_speculative(rt, "a2-1", "this is Kim", persona=PERSONA)
        assert _kinds(fake) == ["speak"]              # NO tools call paid
        assert rt._staged_tools is not None           # snapshot parked
        assert rt._pending_tools is None
    asyncio.run(go())


def test_adopt_fires_tools_at_confirmation():
    async def go():
        fake = SpeakFirstFakeLLM(
            speak_rounds=[{"tokens": ["Got it."]}],
            tools_rounds=[{"tool_calls": [
                tool_call("extract_intake_details", {"inbound_channel": "ad"},
                          "t1")]}])
        rt = _make_rt(_settings(speak_first_pipeline=True), fake)
        await _run_speculative(rt, "a2-2", "this is Kim", persona=PERSONA)
        task = rt._fire_staged_tools()                # the adopt call site
        assert task is not None
        await task
        assert _kinds(fake) == ["speak", "tools"]
        assert rt._staged_tools is None
        assert rt._pending_tools is not None          # registered for M1/M2/M3
    asyncio.run(go())


def test_discard_pays_no_tools():
    async def go():
        fake = SpeakFirstFakeLLM(
            speak_rounds=[{"tokens": ["Got it."]}],
            tools_rounds=[{"tool_calls": [
                tool_call("extract_intake_details", {}, "t1")]}])
        rt = _make_rt(_settings(speak_first_pipeline=True), fake)
        await _run_speculative(rt, "a2-3", "this is Kim", persona=PERSONA)
        assert rt._staged_tools is not None
        rt._staged_tools = None                       # the discard clear
        assert rt._fire_staged_tools() is None
        assert _kinds(fake) == ["speak"]              # zero tools paid
    asyncio.run(go())


def test_confirmed_round_unchanged():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Got it."]}],
        tools_rounds=[{"tool_calls": [
            tool_call("extract_intake_details", {"inbound_channel": "ad"}, "t1")]}])
    rt = _make_rt(_settings(speak_first_pipeline=True), fake)
    _run(rt, "a2-4", "this is Kim", persona=PERSONA)
    assert _kinds(fake) == ["speak", "tools"]         # both arms as today
    assert rt._staged_tools is None


def test_flag_off_is_legacy():
    async def go():
        fake = SpeakFirstFakeLLM(
            speak_rounds=[{"tokens": ["Got it."]}],
            tools_rounds=[{"tool_calls": [
                tool_call("extract_intake_details", {}, "t1")]}])
        rt = _make_rt(_settings(speak_first_pipeline=True,
                                eager_speak_only=False), fake)
        await _run_speculative(rt, "a2-5", "this is Kim", persona=PERSONA)
        assert _kinds(fake) == ["speak", "tools"]     # legacy: both arms
    asyncio.run(go())


def test_speculative_marker_never_leaks_across_turns():
    async def go():
        fake = SpeakFirstFakeLLM(
            speak_rounds=[{"tokens": ["Got it."]}, {"tokens": ["Ok."]}],
            tools_rounds=[{"tool_calls": [
                tool_call("extract_intake_details", {}, "t1")]},
                {"tool_calls": []}])
        rt = _make_rt(_settings(speak_first_pipeline=True), fake)
        cfg = {"configurable": {"thread_id": "a2-6"}}
        # turn 1: speculative (staged, tools not fired)
        payload = {"user_text": "this is Kim", "speculative_turn": True}
        payload.update(rt.initial_state("a2-6", PERSONA))
        async for _ in rt.graph.astream(payload, config=cfg,
                                        stream_mode=["custom", "updates"]):
            pass
        assert rt._staged_tools is not None
        rt._staged_tools = None                        # discard
        # turn 2: CONFIRMED — must fire both arms (no stale marker)
        from tests.test_iter112_speak_first import _run_turn
        await _run_turn(rt, "a2-6", "ok")
        assert _kinds(fake) == ["speak", "speak", "tools"]
    asyncio.run(go())
