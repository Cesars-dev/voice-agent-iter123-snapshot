"""iter119 — mouth-every-round (plan_v5_iter119_mouth_every_round.md).

The SPEAK stream routes to `speak_model` (luna) for EVERY round of the FIRST
4 states (Intake, Discovery, Closer, Offer): lite (t1), entry-lite acks,
heavy/steady. The 5 tool-heavy states (contact_details, ConfirmSlots,
VerifyLead, Booking, Closing) stay 100% gpt-5.4 — speech AND tools. The
tools-stream payload per round type stays byte-identical (lite:
[LITE_NOOP_TOOL]; entry: full array; heavy: full array). Channel-closed
(tools=[]) rounds of every state stay single-call.

Plus (T3, owner's un-cached-tokens catch): a luna LITE-shape speak warm
(`warm_speak_cache(..., lite=True)`, latch `speak-lite:<state>`, fired at
session start) — the only post-119 luna shape the existing warms do not
cover.

Pins:
  1. lite round (Intake t1): stagger fires; speak model == luna; background
     tools payload == [LITE_NOOP_TOOL] (byte-parity with today's single call).
  2. mouth entry-lite round (t2 back into Intake): speak model == luna;
     background tools payload == today's FULL array.
  3. non-mouth entry round (contact_details): NO stagger — single-call path,
     trace model == openai_model.
  4. entry-round tool execution parity (a tools-stream call executes with the
     SAME observables as the pre-change single call: executor trace +
     last_round_tool_calls + history).
  5. heavy round unchanged (iter112 contract) + channel-closed stays single.
  6. `speak_model_states` list untouched (mouth 4 -> luna, rest -> 5.4).
  7. luna lite warm: latch `speak-lite:<state>` + lite-head bytes; separate
     latch from the heavy `speak:<state>` warm; session start fires it.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.graph import builder as B
from tests.fake_llm import FakeLLM, tool_call
from tests.mock_webhooks import mock_client
from tests.test_iter112_speak_first import (
    PERSONA, SpeakFirstFakeLLM, LLM_JSON, _make_rt, _run, _run_turns,
    _tts_tokens,
)
from tests.test_iter114_speech_auth import _TracerStub

ROOT = Path(__file__).resolve().parents[1]
LUNA = "gpt-5.6-luna"


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


def _rt_with_tracer(settings: Settings, fake):
    return B.CallRuntime(settings, LLM_JSON, tracer=_TracerStub(), llm=fake,
                         http_client=mock_client())


# --------------------------------------------------------------------------- #
# 1 — lite round (t1, Intake): stagger + luna mouth + LITE_NOOP_TOOL payload
# --------------------------------------------------------------------------- #
def test_lite_round_fires_speak_arm_luna():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Hi ", "there."], "delay": 0.01}],
        tools_rounds=[{"tokens": []}],
    )
    rt = _rt_with_tracer(
        _settings(speak_first_pipeline=True, speak_model=LUNA,
                  first_turn_lite=True), fake)
    custom, _ = _run(rt, "s119-lite", "hello?", persona=dict(PERSONA))

    kinds = [(c["kind"], c["speak_model"]) for c in fake.calls]
    assert kinds == [("speak", LUNA), ("tools", "")]     # stagger fired
    speak_call, tools_call = fake.calls[0], fake.calls[1]
    assert speak_call["tools"] == []                     # bare mouth
    assert speak_call["messages"][0]["content"] == rt._lite_head()
    # byte-parity: the background tools stream carries TODAY's single-call
    # lite payload — [LITE_NOOP_TOOL] (FIND-5) + the same messages.
    assert tools_call["tools"] == ["memory_note"]
    assert tools_call["messages"][0]["content"] == rt._lite_head()
    # the mouth really spoke (speak stream only)
    assert "".join(_tts_tokens(custom)) == "Hi there."
    # trace truth: the lite generation is labelled luna
    assert rt.tracer.starts[0]["model"] == LUNA


# --------------------------------------------------------------------------- #
# 2 — mouth entry-lite round (turn-2 entry into Intake): luna + FULL tools
# --------------------------------------------------------------------------- #
def test_mouth_entry_lite_round_fires_speak_arm_luna():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Hi there."], "delay": 0.01},
                      {"tokens": ["Of course."], "delay": 0.01}],
        tools_rounds=[{"tokens": []}, {"tokens": []}],
    )
    rt = _rt_with_tracer(
        _settings(speak_first_pipeline=True, speak_model=LUNA,
                  first_turn_lite=True), fake)
    _run_turns(rt, "s119-entry", ["hello?", "yes please"],
               persona=dict(PERSONA))

    kinds = [(c["kind"], c["speak_model"]) for c in fake.calls]
    assert kinds == [("speak", LUNA), ("tools", ""),
                     ("speak", LUNA), ("tools", "")]
    # t1 lite tools = noop; t2 entry tools = TODAY's full array (FIND-5 port)
    assert fake.calls[1]["tools"] == ["memory_note"]
    assert "extract_intake_details" in fake.calls[3]["tools"]
    assert fake.calls[2]["tools"] == []                  # entry mouth bare
    # trace truth: lite AND entry generations both labelled luna
    assert [s["model"] for s in rt.tracer.starts] == [LUNA, LUNA]


# --------------------------------------------------------------------------- #
# 3 — non-mouth entry round: single-call path unchanged
# --------------------------------------------------------------------------- #
def test_nonmouth_entry_round_stays_single_call():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[],                                  # no arm may fire
        tools_rounds=[{"tokens": ["Hi."]},
                      {"tokens": ["Got it, thanks."]}],
    )
    rt = _rt_with_tracer(
        _settings(speak_first_pipeline=True, speak_model=LUNA,
                  first_turn_lite=True), fake)
    _run_turns(rt, "s119-nonmouth", ["hello?", "ok"],
               persona=dict(PERSONA), state="contact_details")

    assert [c["kind"] for c in fake.calls] == ["tools", "tools"]
    assert all(c["speak"] is False and c["speak_model"] == ""
               for c in fake.calls)
    # trace truth: both rounds (lite + entry) labelled the hot model
    assert [s["model"] for s in rt.tracer.starts] == ["gpt-5.4", "gpt-5.4"]


# --------------------------------------------------------------------------- #
# 4 — entry-round tool execution parity (pre-change observables)
# --------------------------------------------------------------------------- #
def test_entry_round_tool_execution_parity():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Hi."], "delay": 0.02},
                      {"tokens": ["Let me note that."], "delay": 0.02}],
        tools_rounds=[{"tokens": []},
                      {"tool_calls": [tool_call("extract_intake_details",
                                                {"caller_name": "Kim"})]}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model=LUNA,
                            first_turn_lite=True), fake)
    _, (_, values) = _run_turns(rt, "s119-parity", ["hello?", "this is Kim"],
                                persona=dict(PERSONA))

    # the entry-round tool call executed (M1 adoption == the single-call path):
    # executor trace + assistant tool_calls frame + tool result in history.
    assert "extract_intake_details" in [e["tool"] for e in rt.executor.trace]
    hist = values.get("history") or []
    parked = [tc["function"]["name"]
              for m in hist
              if m.get("role") == "assistant" and m.get("tool_calls")
              for tc in m["tool_calls"]]
    assert "extract_intake_details" in parked
    assert any(m.get("role") == "tool" for m in hist)


# --------------------------------------------------------------------------- #
# 5 — heavy round unchanged + channel-closed stays single-call
# --------------------------------------------------------------------------- #
def test_heavy_round_unchanged():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Hi there."], "delay": 0.01}],
        tools_rounds=[{"tokens": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model=LUNA),
                  fake)
    _run(rt, "s119-heavy", "hello", persona=dict(PERSONA))
    assert [(c["kind"], c["speak_model"]) for c in fake.calls] == \
        [("speak", LUNA), ("tools", "")]
    assert fake.calls[0]["tools"] == []
    assert "extract_intake_details" in fake.calls[1]["tools"]


def test_channel_closed_stays_single_call():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": [], "delay": 0.01}],     # silent mouth
        tools_rounds=[{"tool_calls": [tool_call("extract_intake_details",
                                                {"caller_name": "Kim"})]},
                      {"tokens": ["Okay, got it."]}],     # forced-speech rd
    )
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model=LUNA,
                            force_speech_keep_tools=False), fake)
    custom, _ = _run(rt, "s119-cc", "this is Kim", persona=dict(PERSONA))
    assert [c["kind"] for c in fake.calls] == ["speak", "tools", "tools"]
    assert fake.calls[2]["tools"] == []          # tools=[] -> never armed
    assert fake.calls[2]["speak"] is False
    assert "Okay, got it." in "".join(_tts_tokens(custom))


# --------------------------------------------------------------------------- #
# 6 — the speak list stays the mouth 4 (no widening)
# --------------------------------------------------------------------------- #
def test_speak_model_states_list_unchanged():
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model=LUNA),
                  FakeLLM([]))
    for s in ("Intake", "Discovery", "Closer", "Offer"):
        assert rt._speak_model_for(s) == LUNA, s
    for s in ("contact_details", "ConfirmSlots", "VerifyLead", "Booking",
              "Closing"):
        assert rt._speak_model_for(s) == "gpt-5.4", s


# --------------------------------------------------------------------------- #
# 7 — T3: luna lite-shape speak warm
# --------------------------------------------------------------------------- #
class _WarmSpyLLM:
    """Records speak-twin warm requests (speak_llm(model) -> bind ->
    ainvoke)."""

    def __init__(self):
        self.calls: list[dict] = []

    def speak_llm(self, model=None):
        outer = self

        class _Twin:
            def bind(self, **kw):
                return self

            async def ainvoke(self, messages):
                outer.calls.append({"model": model,
                                    "messages": list(messages)})
                return None

        return _Twin()


def test_luna_lite_warm_fires_and_uses_lite_head():
    llm = _WarmSpyLLM()
    rt = B.CallRuntime(_settings(speak_first_pipeline=True, speak_model=LUNA),
                       LLM_JSON, tracer=None, llm=llm, http_client=mock_client())

    async def go():
        rt.warm_speak_cache("Intake", [], {}, lite=True)
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())
    assert "speak-lite:Intake" in rt._prewarmed
    assert llm.calls and llm.calls[0]["model"] == LUNA
    # the lite warm mirrors the HOT lite speak construction: lite-head bytes
    assert llm.calls[0]["messages"][0]["content"] == rt._lite_head()


def test_luna_lite_warm_latch_separate_from_heavy():
    llm = _WarmSpyLLM()
    rt = B.CallRuntime(_settings(speak_first_pipeline=True, speak_model=LUNA),
                       LLM_JSON, tracer=None, llm=llm, http_client=mock_client())

    async def go():
        rt.warm_speak_cache("Intake", [], {}, lite=True)
        rt.warm_speak_cache("Intake", [], {})          # heavy shape
        rt.warm_speak_cache("Intake", [], {}, lite=True)   # latched -> no-op
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())
    assert "speak-lite:Intake" in rt._prewarmed
    assert "speak:Intake" in rt._prewarmed
    assert len(llm.calls) == 2                         # one per shape, no re-fire
    heavy = next(c for c in llm.calls
                 if c["messages"][0]["content"] != rt._lite_head())
    assert heavy["messages"][0]["content"] == rt._head_for("Intake", None)[0]


def test_session_start_fires_luna_lite_warm():
    src = (ROOT / "diallux" / "media" / "session.py").read_text()
    i = src.index("warm_speak_cache", src.index("warm_speak_cache") + 1)
    seg = src[i:i + 400]
    assert "lite=True" in seg
