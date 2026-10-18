"""iter118b T15 — brain output bound (tools lane only; 0 = off).

The bound binds max_completion_tokens on the TOOLS lane per call; a generation
cut by the bound ("length") drops only tool calls whose args fail to parse —
a call that parses still executes (executions are never dropped).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.graph.llm import StreamingLLM


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=False)
    base.update(kw)
    return Settings(**base)


class _Chunk:
    def __init__(self, content=None, tcc=None, finish=None):
        self.content = content
        self.tool_call_chunks = tcc or []
        self.response_metadata = {"finish_reason": finish} if finish else {}
        self.usage_metadata = None


class _Bound:
    def __init__(self, chunks):
        self._chunks = chunks

    def astream(self, messages):
        async def gen():
            for c in self._chunks:
                yield c
        return gen()


class _Hot:
    def __init__(self, chunks, rec):
        self._chunks = chunks
        self._rec = rec

    def bind(self, **kw):
        self._rec.append(("bind", dict(kw)))
        return self

    def bind_tools(self, tools):
        self._rec.append(("bind_tools", tools))
        return _Bound(self._chunks)


def _collect(chunks, max_n):
    llm = StreamingLLM(_settings())
    rec: list = []
    llm._llm = _Hot(chunks, rec)

    async def go():
        events = []
        async for ev in llm.astream(
                [{"role": "user", "content": "hi"}],
                [{"type": "function", "function": {"name": "f"}}],
                max_completion_tokens=max_n):
            events.append(ev)
        return events

    return asyncio.run(go()), rec


def test_bound_allows_full_tool_args():
    chunks = [_Chunk(tcc=[{"index": 0, "id": "c1", "name": "f",
                           "args": '{"a": 1}'}], finish="tool_calls")]
    events, rec = _collect(chunks, 512)
    finals = [e for e in events if e["type"] == "final"]
    assert finals and finals[0]["tool_calls"][0]["name"] == "f"
    assert any(r[0] == "bind" and r[1].get("max_completion_tokens") == 512
               for r in rec)


def test_bound_flag_zero_off():
    chunks = [_Chunk(tcc=[{"index": 0, "id": "c1", "name": "f",
                           "args": '{"a": 1}'}], finish="tool_calls")]
    _, rec = _collect(chunks, 0)
    assert not any(r[0] == "bind" for r in rec)      # no bind when 0


def test_truncated_args_never_reach_executor():
    chunks = [_Chunk(tcc=[{"index": 0, "id": "c1", "name": "f",
                           "args": '{"a":'}], finish="length")]
    events, _ = _collect(chunks, 512)
    finals = [e for e in events if e["type"] == "final"]
    assert finals and finals[0]["tool_calls"] == []  # truncated call dropped
