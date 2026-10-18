"""iter118b A1 — M0 gate-flush stamps + bench aliases (pure observability).

Pins the two (only) emit points, the never-stamp cases, first-only semantics,
and the bench aliases (added only when the source value exists). No behavior
change, no metric renames.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.media.session import _stamp_clock_event
from diallux.observability.latency import TurnClock
from tests.fake_llm import FakeLLM
from tests.test_iter112_speak_first import SpeakFirstFakeLLM, _make_rt, _run


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


def _gate_flushes(custom) -> list[str]:
    return [e["gate_flush"] for e in custom if "gate_flush" in e]


# --------------------------------------------------------------------------- #
# clock unit pins
# --------------------------------------------------------------------------- #
def test_bench_aliases_present_and_equal():
    c = TurnClock(turn_index=1, t_user_end=1.0, t_llm_dispatch=1.1,
                  t_llm_first_event=1.05, t_llm_first=1.2, t_gate_flush=1.3,
                  t_tts_first=1.4, t_audio_out=1.6, t_turn_done=2.0)
    r = c.report()
    assert r["eou_delay"] == r["stt_eot_to_llm_dispatch_ms"] == 100.0
    assert r["llm_ttft"] == r["stt_eot_to_llm_first_ms"] == 200.0
    assert r["tts_ttfb"] == r["tts_first_to_audio_out_ms"] == 200.0
    assert r["e2e_latency"] == r["e2e_response_ms"] == 600.0
    assert r["llm_first_to_gate_flush_ms"] == 100.0
    assert r["gate_flush_to_tts_first_ms"] == 100.0
    assert r["gate_flush_since_first_token_ms"] == 250.0


def test_aliases_absent_when_source_none():
    r = TurnClock(turn_index=1, t_user_end=1.0).report()
    for k in ("eou_delay", "llm_ttft", "tts_ttfb", "e2e_latency"):
        assert k not in r


def test_session_stamp_first_only_reason():
    c = TurnClock(turn_index=1)
    _stamp_clock_event(c, {"gate_flush": "tail"})
    first = c.t_gate_flush
    assert first is not None and c.extra["gate_flush_reason"] == "tail"
    _stamp_clock_event(c, {"gate_flush": "sentence"})       # first-only
    assert c.t_gate_flush == first
    assert c.extra["gate_flush_reason"] == "tail"


# --------------------------------------------------------------------------- #
# builder emit points (flag OFF single stream = still honest)
# --------------------------------------------------------------------------- #
def test_first_flush_sentence_reason():
    fake = FakeLLM([{"tokens": ["Hello", " there", "."], "tool_calls": []}])
    rt = _make_rt(_settings(), fake)
    custom, _ = _run(rt, "m0-sent", "hi")
    assert _gate_flushes(custom) == ["sentence"]


def test_first_flush_tail_reason():
    fake = FakeLLM([{"tokens": ["Hi", " there"], "tool_calls": []}])  # no sentence end
    rt = _make_rt(_settings(), fake)
    custom, _ = _run(rt, "m0-tail", "hi")
    assert _gate_flushes(custom) == ["tail"]


def test_empty_round_has_no_gate_flush():
    fake = FakeLLM([{"tokens": [], "tool_calls": []}])      # nothing spoken
    rt = _make_rt(_settings(), fake)
    custom, _ = _run(rt, "m0-empty", "hi")
    assert _gate_flushes(custom) == []


def test_flagon_split_path_stamps_from_speak_stream_only():
    # tools-stream text is discarded -> it must never stamp; the stamp is the
    # speak stream's first real sentence, exactly once.
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Got it."]}],
        tools_rounds=[{"tokens": ["TOOLTEXT-NEVER-SPOKEN"], "tool_calls": []}])
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_diet=True,
                            speak_model="gpt-5.6-luna"), fake)
    custom, _ = _run(rt, "m0-split", "hi")
    assert _gate_flushes(custom) == ["sentence"]
