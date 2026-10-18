"""iter120 — Sales-Intuition prompt law + Closer leak-capture enforcement.

plan_v5_iter120_sales_intuition.md (owner 2026-10-16). Four surfaces:
  1-2. Intake.md: four-beat Question Craft (COMPASS -> NEED -> PROJECT -> ASK)
       + completion requires the challenge behind each var understood.
  3.   Closer.md: "next needed question or a commitment check" beat.
  4.   general_prompt.md: opener cap (never same opener twice in a row;
       no single opener >3x per call).
  5.   agent/llm.json lockstep carries the new rules.
  6-7. engine enforcement (builder._deterministic_node): when the 5.4 brain
       missed `extract_leak_inputs` in a Closer round with the inputs present,
       the ENGINE fires the capture + hands the model the reveal note;
       never outside Closer; never double-fires when the model called it.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.graph.builder import CallRuntime
from tests.fake_llm import FakeLLM, tool_call
from tests.mock_webhooks import mock_client

ROOT = Path(__file__).resolve().parents[1]
LLM_JSON = json.loads((ROOT / "agent" / "llm.json").read_text())

LEAK_PERSONA = {"missed_calls_weekly": 30, "close_rate_pct": 40,
                "avg_job_value": 1800}


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


def _make_rt(settings: Settings, fake) -> CallRuntime:
    return CallRuntime(settings, LLM_JSON, tracer=None, llm=fake,
                       http_client=mock_client())


async def _run_turn(rt: CallRuntime, call_id: str, text: str,
                    first: bool = False, persona: dict | None = None,
                    state: str | None = None):
    config = {"configurable": {"thread_id": call_id}}
    payload: dict = {"user_text": text}
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


def _run(rt: CallRuntime, call_id: str, text: str, persona: dict | None = None,
         state: str | None = None):
    async def go():
        return await _run_turn(rt, call_id, text, first=True, persona=persona,
                               state=state)
    return asyncio.run(go())


def _run_turns(rt: CallRuntime, call_id: str, texts: list[str],
               persona: dict | None = None, state: str | None = None):
    async def go():
        out = []
        for i, t in enumerate(texts):
            out.append(await _run_turn(rt, call_id, t, first=(i == 0),
                                       persona=persona,
                                       state=state if i == 0 else None))
        return out
    return asyncio.run(go())


class SpeakFirstFakeLLM:
    """Minimal mirror of test_iter112's split-router fake: speak calls pop
    `speak_rounds`, tools calls pop `tools_rounds`; `delay` holds a round's
    first yield — the tools land after the round close (M2/tail path: the
    tools execute at the NEXT turn's ingest, never via the state node)."""

    def __init__(self, speak_rounds, tools_rounds):
        self.speak_rounds = list(speak_rounds)
        self.tools_rounds = list(tools_rounds)
        self.calls: list[dict] = []

    async def astream(self, messages, tools, verbosity="", speak=False,
                      speak_model: str = "", max_completion_tokens: int = 0):
        queue = self.speak_rounds if speak else self.tools_rounds
        script = queue.pop(0) if queue else {"tokens": [], "tool_calls": []}
        self.calls.append({"speak": speak, "messages": list(messages)})
        delay = float(script.get("delay") or 0.0)
        if delay:
            await asyncio.sleep(delay)
        for tok in script.get("tokens", []):
            yield {"type": "token", "text": tok}
        for tc in script.get("tool_calls", []):
            yield {"type": "tool_call_start", "name": tc["name"]}
        yield {"type": "final", "content": "".join(script.get("tokens", [])),
               "tool_calls": script.get("tool_calls", []),
               "usage": {"input_tokens": 100, "output_tokens": 20,
                         "total_tokens": 120}}


def _trace_names(rt: CallRuntime) -> list[str]:
    return [e["tool"] for e in rt.executor.trace]


def _intake_md() -> str:
    return (ROOT / "diallux" / "prompts" / "Intake.md").read_text()


# --------------------------------------------------------------------------- #
# 1-2 — Intake four-beat Question Craft + completion law
# --------------------------------------------------------------------------- #
def test_intake_four_beat_loop_present():
    md = _intake_md()
    for anchor in ("COMPASS —", "NEED —", "PROJECT —", "ASK —",
                   "new emotional frame or sales angle",
                   "Rewording the same ask is not a new question",
                   "the conversation is the ledger"):
        assert anchor in md, anchor


def test_intake_completion_requires_understanding():
    md = _intake_md()
    assert "understood in their own words — never assumed" in md
    assert "including the challenge behind each, in their words" in md


def test_discovery_question_craft_law_present():
    md = (ROOT / "diallux" / "prompts" / "Discovery.md").read_text()
    for anchor in ("COMPASS —", "NEED —", "PROJECT —", "ASK —",
                   "A number they've already spoken (calls, close rate, ticket) "
                   "is known — never ask for it again",
                   "Rewording the same ask is not a new question",
                   "the conversation is the ledger"):
        assert anchor in md, anchor


# --------------------------------------------------------------------------- #
# 3 — Closer next-needed-question beat
# --------------------------------------------------------------------------- #
def test_closer_next_question_beat():
    md = (ROOT / "diallux" / "prompts" / "Closer.md").read_text()
    assert "NEXT needed question or a commitment check" in md
    assert "Always end your turn with a question." not in md


# --------------------------------------------------------------------------- #
# 4 — general opener cap
# --------------------------------------------------------------------------- #
def test_general_opener_cap():
    md = (ROOT / "diallux" / "prompts" / "general_prompt.md").read_text()
    assert "never the same opener twice in a row" in md
    assert "no single opener more than 3 times in one call" in md


# --------------------------------------------------------------------------- #
# 5 — llm.json lockstep carries the new rules
# --------------------------------------------------------------------------- #
def test_llm_json_carries_new_rules():
    states = {s["name"]: s for s in LLM_JSON["states"]}
    assert "the conversation is the ledger" in states["Intake"]["state_prompt"]
    assert "understood in their own words — never assumed" in \
        states["Intake"]["state_prompt"]
    assert "never ask for it again" in states["Discovery"]["state_prompt"]
    assert "NEXT needed question or a commitment check" in \
        states["Closer"]["state_prompt"]
    assert "no single opener more than 3 times in one call" in \
        LLM_JSON["general_prompt"]


# --------------------------------------------------------------------------- #
# 6 — engine enforces the leak capture when the brain missed it
# --------------------------------------------------------------------------- #
def test_leak_capture_enforced_when_brain_missed():
    fake = FakeLLM([
        {"tokens": ["Got it."],
         "tool_calls": [tool_call("extract_closer_details",
                                  {"pain_points": "missed calls"})]},
        {"tokens": ["so the gap is real"], "tool_calls": []},
    ])
    rt = _make_rt(_settings(), fake)
    _custom, values = _run(rt, "s-120-leak-1", "sure", persona=LEAK_PERSONA,
                           state="Closer")
    assert rt._leak_capture_forced is True
    assert "extract_leak_inputs" in _trace_names(rt)      # engine-fired capture
    facts = " ".join(values.get("held_facts") or [])
    assert "$21,600" in facts and "$93,500" in facts      # reveal note figures
    assert str(values["dvs"].get("weekly_leak")) == "21,600"


def test_leak_capture_no_double_fire_when_model_called():
    fake = FakeLLM([
        {"tokens": ["Let me run those numbers."],
         "tool_calls": [tool_call("extract_leak_inputs",
                                  {"missed_calls_weekly": "30",
                                   "close_rate_pct": "40",
                                   "avg_job_value": "1800"})]},
        {"tokens": ["ok"], "tool_calls": []},
    ])
    rt = _make_rt(_settings(), fake)
    _custom, values = _run(rt, "s-120-leak-2", "sure", persona=LEAK_PERSONA,
                           state="Closer")
    assert _trace_names(rt).count("extract_leak_inputs") == 1   # model's call only
    assert rt._leak_capture_forced is False
    assert "reveal the weekly figure" not in \
        " ".join(values.get("held_facts") or [])


# --------------------------------------------------------------------------- #
# 7 — enforcement never fires outside Closer
# --------------------------------------------------------------------------- #
def test_leak_capture_not_outside_closer():
    fake = FakeLLM([
        {"tokens": ["Got it."],
         "tool_calls": [tool_call("extract_discovery_details",
                                  {"industry": "roofing"})]},
        {"tokens": ["ok"], "tool_calls": []},
    ])
    rt = _make_rt(_settings(), fake)
    _custom, values = _run(rt, "s-120-leak-3", "sure", persona=LEAK_PERSONA,
                           state="Discovery")
    assert rt._leak_capture_forced is False
    assert "extract_leak_inputs" not in _trace_names(rt)
    assert "reveal the weekly figure" not in \
        " ".join(values.get("held_facts") or [])


# --------------------------------------------------------------------------- #
# 8 — M2/tail path: the Closer round's tools land at the NEXT turn's ingest
#     (the harness reality — the Sam run's trio tailed past the deterministic
#     node); the ingest hook must still enforce the capture + deliver the note.
# --------------------------------------------------------------------------- #
def test_leak_capture_enforced_on_m2_path():
    fake = SpeakFirstFakeLLM(
        speak_rounds=[{"tokens": ["Got it."]},
                      {"tokens": ["Sure."]}],
        tools_rounds=[{"tool_calls": [tool_call("extract_closer_details",
                                                {"pain_points": "missed calls"})],
                       "delay": 0.3},             # outlives the round -> M2
                      {"tool_calls": []}],
    )
    rt = _make_rt(_settings(speak_first_pipeline=True), fake)
    _run_turns(rt, "s-120-leak-m2", ["hello?", "sure"],
               persona=LEAK_PERSONA, state="Closer")
    assert rt._leak_capture_forced is True
    assert "extract_leak_inputs" in _trace_names(rt)
    # turn-1 calls (pre-fire) carry no note …
    t1_msgs = " ".join(str(m.get("content") or "") for m in fake.calls[0]["messages"])
    assert "reveal the weekly figure" not in t1_msgs
    # … the post-ingest (turn-2) payload carries the ENGINE note with figures
    t2_msgs = " ".join(str(m.get("content") or "") for m in fake.calls[2]["messages"])
    assert "reveal the weekly figure" in t2_msgs
    assert "$21,600" in t2_msgs and "$93,500" in t2_msgs
