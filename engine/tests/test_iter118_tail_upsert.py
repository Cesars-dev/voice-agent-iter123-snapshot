"""iter118 (Part A) — owner trio pins.

Fix 1  upsert law (prompts): Closer.md + llm.json byte-lockstep — a caller
       CORRECTION must re-capture (the 1029 call lost the 80%→5% correction).
Fix 2  derive recompute (PT-99 engine half): `_derive` recomputes on input
       change, patch-only-on-change (the freeze gate died).
Fix 3  M2 tail + value hold: on a luna-state c) turn a live brain future is
       tailed (dispatch never waits); value/transition futures keep the await.

Red-first discipline: each pin is written + run BEFORE its edit.
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings                        # noqa: E402
from diallux.graph.builder import _PendingTools, _VALUE_TOOLS  # noqa: E402
from tests.fake_llm import FakeLLM, tool_call              # noqa: E402
from tests.test_iter112_speak_first import (               # noqa: E402
    PERSONA, _make_rt, _run_turn, _run_turns,
)

ROOT = Path(__file__).resolve().parents[1]
CLOSER = (ROOT / "diallux" / "prompts" / "Closer.md").read_text()
LLM = json.loads((ROOT / "agent" / "llm.json").read_text())

LUNA = dict(speak_first_pipeline=True, speak_model="gpt-5.6-luna")


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


# --------------------------------------------------------------------------
# Fix 1 — the upsert law (prompt layer + byte-lockstep mirror)
# --------------------------------------------------------------------------

def test_upsert_law_strings_present():
    assert (
        "never re-ask a filled value, and never argue it: if the caller "
        "corrects or replaces one, THEIR new number is the truth"
    ) in CLOSER
    assert "And call it AGAIN any time the caller corrects or replaces any of them" in CLOSER
    assert "call it again on every caller correction or replacement" in CLOSER
    closer = [s for s in LLM["states"] if s["name"] == "Closer"][0]
    tool = [t for t in closer["tools"] if t["name"] == "extract_leak_inputs"][0]
    assert "call it again whenever the prospect corrects or replaces" in tool["description"]


# --------------------------------------------------------------------------
# Fix 2 — `_derive` recompute-on-change (PT-99 engine half)
# --------------------------------------------------------------------------

def test_derive_recomputes_when_input_changes():
    rt = _make_rt(_settings(), FakeLLM([]))
    rt.tracer = MagicMock()
    dvs = {"missed_calls_weekly": "20", "close_rate_pct": "5",
           "avg_job_value": "10000", "weekly_leak": "160,000",
           "monthly_leak": "692,800"}
    patch, fired = rt._derive(dvs)
    assert fired is True
    assert patch["weekly_leak"] == "10,000"
    assert patch["monthly_leak"] == "43,300"
    assert rt.tracer.span.called
    assert rt.tracer.span.call_args[0][0] == "derive:leak_math"


def test_derive_idempotent_when_inputs_unchanged():
    rt = _make_rt(_settings(), FakeLLM([]))
    dvs = {"missed_calls_weekly": "20", "close_rate_pct": "80",
           "avg_job_value": "10000", "weekly_leak": "160,000",
           "monthly_leak": "692,800"}
    patch, fired = rt._derive(dvs)
    assert patch == {} and fired is False


def test_derive_first_fire_unchanged():
    rt = _make_rt(_settings(), FakeLLM([]))
    dvs = {"missed_calls_weekly": "20", "close_rate_pct": "80",
           "avg_job_value": "10000"}
    patch, fired = rt._derive(dvs)
    assert fired is True
    assert patch == {"weekly_leak": "160,000", "monthly_leak": "692,800"}


# --------------------------------------------------------------------------
# Fix 3 — the M2 tail + value hold
# --------------------------------------------------------------------------

class _StallFake:
    """Speak = trivial; the FIRST tools round emits `tool_call_start`
    immediately, then STALLS, then final — the M2 decision sees a LIVE
    stream with the flags set. Later tools rounds are empty."""

    def __init__(self, tool_name, args=None, stall=0.6, emit_start=True):
        self.tool_name = tool_name
        self.args = args or {}
        self.stall = stall
        self.emit_start = emit_start
        self.n_tools = 0

    async def astream(self, messages, tools, verbosity="", speak=False,
                      speak_model: str = "", max_completion_tokens: int = 0):
        if speak:
            yield {"type": "token", "text": "Got it."}
            yield {"type": "final", "content": "Got it.", "tool_calls": [],
                   "usage": {"input_tokens": 10, "output_tokens": 2}}
            return
        self.n_tools += 1
        if self.n_tools > 1:
            yield {"type": "final", "content": "", "tool_calls": [],
                   "usage": {"input_tokens": 10, "output_tokens": 1}}
            return
        tc = tool_call(self.tool_name, self.args, "t1")
        if self.emit_start:
            yield {"type": "tool_call_start", "name": self.tool_name}
        await asyncio.sleep(self.stall)
        yield {"type": "final", "content": "", "tool_calls": [tc],
               "usage": {"input_tokens": 10, "output_tokens": 5}}


def _m2_lines(caplog):
    return [r.message for r in caplog.records if "split M2:" in r.message]


def test_tail_skips_await_on_mouth_state_live_future(caplog):
    # iter121: the watch (TransitionGate M3) now covers the mouth states by
    # default, so the LEGACY tail is exercised with the watch list emptied.
    fake = _StallFake("extract_intake_details", {"caller_name": "Kim"})
    rt = _make_rt(_settings(**LUNA, m2_mouth_watch_states=""), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "tail-1", ["this is Kim", "ok"], persona=PERSONA)
    lines = _m2_lines(caplog)
    assert any("how=tailed" in m for m in lines), lines
    assert not any("how=awaited" in m for m in lines), lines


def test_tail_not_taken_for_tool_heavy_state(caplog):
    """iter123 R1: contact_details is a SINGLE-LANE transaction state — the
    split never arms, so NO M2 packet (and no tail/await decision) is ever
    created for it. The tail vs await decisions stay pinned on the mouth
    states by the tests around this one."""
    fake = _StallFake("extract_person_details", {"first_name": "Kim"})
    rt = _make_rt(_settings(**LUNA), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "tail-2", ["Kim", "Central"],
                   persona=PERSONA, state="contact_details")
    lines = _m2_lines(caplog)
    assert not lines, lines              # no split → no M2 lines at all


def test_tail_not_taken_when_transition_seen(caplog):
    fake = _StallFake("transition_to_Discovery", {})
    rt = _make_rt(_settings(**LUNA), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "tail-3", ["this is Kim", "ok"], persona=PERSONA)
    lines = _m2_lines(caplog)
    assert any("how=awaited" in m for m in lines), lines
    assert not any("how=tailed" in m for m in lines), lines


def test_tail_not_taken_when_value_tool_seen(caplog):
    fake = _StallFake("extract_leak_inputs",
                      {"missed_calls_weekly": "20", "close_rate_pct": "80",
                       "avg_job_value": "10000"})
    rt = _make_rt(_settings(**LUNA), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "tail-4", ["go ahead", "yes"],
                   persona=PERSONA, state="Closer")
    lines = _m2_lines(caplog)
    assert any("how=awaited" in m for m in lines), lines
    assert not any("how=tailed" in m for m in lines), lines


def test_tail_not_taken_when_speak_model_unset(caplog):
    # E1: speak_model="" -> no tail
    fake = _StallFake("extract_intake_details", {"caller_name": "Kim"})
    rt = _make_rt(_settings(speak_first_pipeline=True, speak_model=""), fake)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt, "tail-5a", ["this is Kim", "ok"], persona=PERSONA)
    assert not any("how=tailed" in m for m in _m2_lines(caplog))
    # E7: speak_model_states="" -> no tail
    fake2 = _StallFake("extract_intake_details", {"caller_name": "Kim"})
    rt2 = _make_rt(_settings(speak_first_pipeline=True, speak_model="gpt-5.6-luna",
                             speak_model_states=""), fake2)
    with caplog.at_level(logging.INFO, logger="diallux.graph"):
        _run_turns(rt2, "tail-5b", ["this is Kim", "ok"], persona=PERSONA)
    assert not any("how=tailed" in m for m in _m2_lines(caplog))


def test_tail_merge_applies_exactly_once():
    async def go():
        fake = _StallFake("extract_intake_details", {"caller_name": "Kim"}, stall=1.0)
        # iter121: legacy tail path (watch list emptied -> no TransitionGate M3).
        rt = _make_rt(_settings(**LUNA, m2_mouth_watch_states=""), fake)
        spy: list[str] = []
        orig = rt.executor.execute

        async def spy_exec(name, *a, **k):
            spy.append(name)
            return await orig(name, *a, **k)

        rt.executor.execute = spy_exec
        await _run_turn(rt, "tail-6", "this is Kim", first=True, persona=PERSONA)
        assert rt._pending_tools is not None and not rt._pending_tools.task.done()
        # turn 2's ingest sees the live future in Intake -> TAIL (no await)
        await _run_turn(rt, "tail-6", "ok")
        # turn-1's future was TAILED (turn 2 fired its own empty tools round,
        # so _pending_tools is not None — that is a different, later future)
        assert len(rt._tail_pending) == 1
        pend = rt._tail_pending[0]
        await asyncio.sleep(1.2)                       # future lands -> callback
        assert pend not in rt._tail_pending            # removed by identity
        assert len(rt._tail_merge) == 1
        st = (await rt.graph.aget_state(
            {"configurable": {"thread_id": "tail-6"}})).values
        out: list = []
        rt._drain_tail_merges({}, st, out_msgs=out)
        assert len(out) >= 1                           # the merge's tool msgs applied
        assert rt._tail_merge == []
        rt._drain_tail_merges({}, st, out_msgs=[])     # idempotent second drain
        assert rt._tail_merge == []
        assert spy.count("extract_intake_details") == 1

    asyncio.run(go())


def test_tail_merge_derives_leak_correction():
    rt = _make_rt(_settings(**LUNA), FakeLLM([]))
    rt._tail_merge = [{
        "msgs": [],
        "dvs_patch": {"missed_calls_weekly": "20", "close_rate_pct": "5",
                      "avg_job_value": "10000"},
        "dvs_after": {}, "new_state": None, "ended": False}]
    state = {"dvs": {"missed_calls_weekly": "20", "close_rate_pct": "80",
                     "avg_job_value": "10000", "weekly_leak": "160,000",
                     "monthly_leak": "692,800"}}
    patch: dict = {}
    rt._drain_tail_merges(patch, state)
    assert patch["dvs"]["weekly_leak"] == "10,000"
    assert patch["dvs"]["monthly_leak"] == "43,300"


def test_tail_close_cancels_all_live_tails(caplog):
    async def go():
        rt = _make_rt(_settings(**LUNA), FakeLLM([]))
        loop = asyncio.get_running_loop()

        async def never():
            await asyncio.sleep(100)

        p1 = _PendingTools(state_name="Intake",
                           dispatched_at=time.perf_counter())
        p1.task = loop.create_task(never())
        p2 = _PendingTools(state_name="Discovery",
                           dispatched_at=time.perf_counter())
        p2.task = loop.create_task(never())
        rt._tail_pending[:] = [p1, p2]
        rt._tail_merge[:] = [{"msgs": [], "dvs_patch": {}, "dvs_after": {},
                              "new_state": None, "ended": False}]
        with caplog.at_level(logging.INFO, logger="diallux.graph"):
            rt._split_close_pending("test-close")
        await asyncio.sleep(0.02)               # let the loop process the cancels
        assert p1.task.cancelled() and p2.task.cancelled()
        assert rt._tail_pending == []
        assert rt._tail_merge == []
        msgs = [r.message for r in caplog.records]
        assert sum("tailed tools task cancelled" in m for m in msgs) == 2
        assert any("tailed merge(s) dropped" in m for m in msgs)

    asyncio.run(go())
