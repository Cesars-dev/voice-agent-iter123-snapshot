"""iter118b — guard replay corpus (tests-only; NO guard behavior change).

Hermetic tuples (sentence, dvs, history, expected_cut):
  - the FIND-116C fabricated-money class must CUT;
  - an engine-authorized (dvs) figure must pass;
  - the 1029 five-percent pair: CUT while dvs still carries the stale
    80%-era figure; ALLOW once dvs carries the corrected value.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.graph.builder import _speak_guard_cut
from tests.fake_llm import FakeLLM
from tests.test_iter112_speak_first import _make_rt


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


def _auth(rt, dvs, history):
    tool_text, toks, nums = rt._speak_auth_sets(dvs, history)
    return tool_text, toks, nums


CASES = [
    # (label, sentence, dvs, history, expect_cut)
    ("fabricated_money_cuts",
     "If even eighty percent of those booked, that's about $3,750 a week.",
     {"missed_calls_weekly": 15, "close_rate_pct": 80, "avg_job_value": 450,
      "weekly_leak": "5,400"},
     [], True),
    ("authorized_dvs_figure_allows",
     "That's about $5,400 a week in missed revenue.",
     {"weekly_leak": "5,400"},
     [], False),
    ("stale_close_rate_corrected_figure_cuts_1029",
     "With 5% closing, that's about $160,000 a week.",
     {"missed_calls_weekly": 20, "close_rate_pct": 80, "avg_job_value": 10000,
      "weekly_leak": "160,000", "monthly_leak": "692,800"},
     [], True),
    ("corrected_figure_allows_1029",
     "With 5% closing, that's about $10,000 a week.",
     {"missed_calls_weekly": 20, "close_rate_pct": 5, "avg_job_value": 10000,
      "weekly_leak": "10,000", "monthly_leak": "43,300"},
     [], False),
]


@pytest.mark.parametrize("label,sent,dvs,history,expect_cut", CASES,
                         ids=[c[0] for c in CASES])
def test_guard_replay(label, sent, dvs, history, expect_cut):
    rt = _make_rt(_settings(), FakeLLM([]))
    tool_text, toks, nums = _auth(rt, dvs, history)
    reason = _speak_guard_cut(sent, toks, nums, dvs, tool_text)
    assert (reason is not None) == expect_cut, (label, reason)
