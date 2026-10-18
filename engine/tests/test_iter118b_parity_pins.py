"""iter118b A6 — history byte-parity + token-order fuzz (offline, hermetic).

1) identical mocked streams: flag OFF vs ON -> persisted history signature
   identical (cache / wire-format protection, iter43 class).
2) the first gate-flush stamp depends ONLY on the SPEAK stream — a tools
   stream in any order/pace can never move it (fails if anyone re-merges).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from tests.fake_llm import FakeLLM, tool_call
from tests.test_iter112_speak_first import (
    PERSONA, SpeakFirstFakeLLM, _make_rt, _run,
)


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


def _hist_sig(values) -> str:
    h = [(m.get("role"), m.get("content")) for m in (values.get("history") or [])]
    return hashlib.sha256(json.dumps(h, sort_keys=True).encode()).hexdigest()


def _flushes(custom) -> list[str]:
    return [e["gate_flush"] for e in custom if "gate_flush" in e]


def test_history_parity_flag_off_vs_on():
    # same spoken TEXT in both arms (tools text discarded) -> the persisted
    # history (role, content) sequence must be identical.
    off = FakeLLM([{"tokens": ["Got it."], "tool_calls": []}])
    rt_off = _make_rt(_settings(), off)
    _, v_off = _run(rt_off, "par-off", "this is Kim", persona=PERSONA)

    on = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Got it."]}],
        tools_rounds=[{"tokens": ["Got it."], "tool_calls": []}])
    rt_on = _make_rt(_settings(speak_first_pipeline=True, speak_diet=True,
                               speak_model="gpt-5.6-luna"), on)
    _, v_on = _run(rt_on, "par-on", "this is Kim", persona=PERSONA)

    assert _hist_sig(v_off) == _hist_sig(v_on)


def test_first_flush_depends_only_on_speak_stream():
    scripts = [
        {"tokens": ["T"] * 80, "tool_calls": []},                     # long tools text first
        {"tokens": ["T."], "tool_calls": [
            tool_call("extract_intake_details", {"inbound_channel": "ad"}, "t1")]},
        {"tokens": [], "tool_calls": []},                             # tool-only
    ]
    for i, tools_script in enumerate(scripts):
        fake = SpeakFirstFakeLLM(
            speak_rounds=[{"tokens": ["Got it."]}],
            tools_rounds=[tools_script])
        rt = _make_rt(_settings(speak_first_pipeline=True, speak_diet=True,
                                speak_model="gpt-5.6-luna"), fake)
        custom, _ = _run(rt, f"fuzz-{i}", "this is Kim", persona=PERSONA)
        assert _flushes(custom) == ["sentence"], (i, tools_script)
