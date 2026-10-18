"""iter122 — call-start luna prewarm (plan_v5_iter122_luna_callstart_prewarm.md).

At call start (session.start, BEFORE begin_message) the SPEAK (luna) twin gets
a ONE-TOKEN socket warm — it opens the twin's TCP/TLS + pays the provider's
first-token latency while Linda's opener plays, AHEAD of the heavy payload
warms (order is the runway; turn-1 lite TTFT target 500-800 ms). The four
existing warms (full, lite, speak, speak-lite) are unchanged; the new warm is
additive and gated on a dedicated speak twin resolving.

Pins:
  1. session.start() fires the luna socket warm BEFORE the greeting
     (begin_message -> self.tts.speak); the warm rides the luna twin.
  2. session.start() still fires the lite speak warm for the starting state.
  3. the lite speak warm bytes mirror the turn-1 lite speak view bytes.
  4. E1 (speak_model unset) / legacy "" / a non-speak state fires no socket warm.
  5. the eager-hold / EOT deferred-tool path is untouched by the new warm.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diallux.config import Settings
from diallux.graph import builder as B
from diallux import rag as ragmod
from tests.mock_webhooks import mock_client

ROOT = Path(__file__).resolve().parents[1]
LLM_JSON = json.loads((ROOT / "agent" / "llm.json").read_text())
LUNA = "gpt-5.6-luna"
SOCKET_MSG = [{"role": "user", "content": "ok"}]


def _settings(**kw) -> Settings:
    base = dict(openai_api_key="test", retell_api_key="test",
                langfuse_enabled=False, first_turn_lite=True)
    base.update(kw)
    return Settings(**base)


class _SpyLLM:
    """Records every warm-style request:
      - brain warms:  warm(messages, tools)
      - speak-twin:   speak_llm(model).bind(...).ainvoke(messages)
    """

    def __init__(self):
        self.warm_calls: list[dict] = []
        self.speak_calls: list[dict] = []

    async def warm(self, messages, tools):
        self.warm_calls.append(
            {"messages": list(messages),
             "tools": [t["function"]["name"] for t in tools]})

    def speak_llm(self, model=None):
        outer = self

        class _Twin:
            def bind(self, **kw):
                return self

            async def ainvoke(self, messages):
                outer.speak_calls.append({"model": model,
                                          "messages": list(messages)})
                return None

        return _Twin()


def _rt(spy, settings) -> B.CallRuntime:
    return B.CallRuntime(settings, LLM_JSON, tracer=None, llm=spy,
                         http_client=mock_client())


def _mk_session(CallSession, settings, runtime):
    sess = object.__new__(CallSession)
    sess.settings = settings
    sess.call_sid = "c122"
    sess.stream_sid = "s122"
    sess.transport = "browser"
    sess.tracer = None
    sess.llm_json = LLM_JSON
    sess.custom_parameters = {}
    sess.runtime = runtime
    sess._outbox = asyncio.Queue()
    sess._initial_payload = {
        "history": [{"role": "assistant", "content": "Hello!"}],
        "dvs": {}, "state_name": "Intake"}
    sess._turn_state = "Intake"
    return sess


def _install_media_fakes(monkeypatch, order=None):
    from diallux.media import session as session_mod

    class FakeSTT:
        async def connect(self, ws=None):
            pass

    class FakeTTS:
        async def connect(self, ws=None):
            pass

        def new_context_id(self):
            return "ctx-1"

        async def speak(self, ctx, text, continue_=False, overrides=None):
            if order is not None:
                order.append(("greet", text))

    monkeypatch.setattr(session_mod, "DeepgramSTT", lambda *a, **k: FakeSTT())
    monkeypatch.setattr(session_mod, "create_tts", lambda *a, **k: FakeTTS())


async def _no_store(settings):
    return None


# --------------------------------------------------------------------------- #
# 1 — socket warm fires BEFORE the greeting, on the luna twin
# --------------------------------------------------------------------------- #
def test_start_fires_luna_socket_warm_before_greeting(monkeypatch):
    from diallux.media.session import CallSession
    from diallux.media import session as session_mod

    monkeypatch.setattr(ragmod, "get_kb_store", _no_store)
    order: list[tuple] = []
    _install_media_fakes(monkeypatch, order)

    spy = _SpyLLM()
    settings = _settings(speak_first_pipeline=True, speak_model=LUNA)
    rt = _rt(spy, settings)
    # session.start() builds its OWN runtime at line 216 — pin ours in place.
    monkeypatch.setattr(session_mod, "CallRuntime", lambda *a, **k: rt)
    real = rt.warm_speak_socket
    rt.warm_speak_socket = lambda state: (order.append(("socket", state)),
                                          real(state))

    sess = _mk_session(CallSession, settings, rt)

    async def go():
        await sess.start()
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())

    # call-site order: socket warm is fired BEFORE the greeting playback
    kinds = [o[0] for o in order]
    assert kinds[0] == "socket"
    assert "greet" in kinds and kinds.index("socket") < kinds.index("greet")
    assert order[0][1] == "Intake"

    # and the warm itself rode the luna twin (the one-token message)
    sock = [c for c in spy.speak_calls if c["messages"] == SOCKET_MSG]
    assert sock, "no one-token socket warm reached the speak twin"
    assert sock[0]["model"] == LUNA

    # source order too: the fire precedes begin_message in session.start()
    src = (ROOT / "diallux" / "media" / "session.py").read_text()
    assert src.index("warm_speak_socket") < src.index("await self.tts.speak(")


# --------------------------------------------------------------------------- #
# 2 — the lite speak warm still fires for the starting state
# --------------------------------------------------------------------------- #
def test_start_fires_lite_speak_warm(monkeypatch):
    from diallux.media.session import CallSession
    from diallux.media import session as session_mod

    monkeypatch.setattr(ragmod, "get_kb_store", _no_store)
    _install_media_fakes(monkeypatch)

    spy = _SpyLLM()
    settings = _settings(speak_first_pipeline=True, speak_model=LUNA)
    rt = _rt(spy, settings)
    monkeypatch.setattr(session_mod, "CallRuntime", lambda *a, **k: rt)
    sess = _mk_session(CallSession, settings, rt)

    async def go():
        await sess.start()
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())

    assert "speak-lite:Intake" in rt._prewarmed
    lite = [c for c in spy.speak_calls
            if c["messages"] and c["messages"][0]["content"] == rt._lite_head()]
    assert lite, "lite speak warm did not fire for the starting state"
    assert lite[0]["model"] == LUNA
    # the initial greeting history is in the warmed prefix
    greet = (sess._initial_payload.get("history") or [{}])[0].get("content", "")
    assert greet and any(m.get("content") == greet for m in lite[0]["messages"])


# --------------------------------------------------------------------------- #
# 3 — lite speak warm bytes mirror the turn-1 lite speak view
# --------------------------------------------------------------------------- #
def test_lite_speak_warm_bytes_match_turn1():
    spy = _SpyLLM()
    settings = _settings(speak_first_pipeline=True, speak_model=LUNA)
    rt = _rt(spy, settings)
    history = [{"role": "assistant", "content": "Hello!"},
               {"role": "user", "content": "hi"}]
    dvs = dict(rt.initial_state("c3").get("dvs") or {})
    dvs_norm = B.DynamicVariables.from_flat(dvs or {}).to_flat()

    async def go():
        rt.warm_speak_cache("Intake", history, dvs, lite=True)
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())

    expected = rt._speak_view(rt._lite_head(), history,
                              rt._speak_delta("Intake", dvs_norm,
                                              history, ""))
    assert len(spy.speak_calls) == 1
    assert spy.speak_calls[0]["messages"] == expected


# --------------------------------------------------------------------------- #
# 4 — no socket warm under E1 / legacy "" / a non-speak state
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("state", ["Intake", "Booking"])
def test_no_luna_warm_when_speak_model_unset(state):
    spy = _SpyLLM()
    settings = _settings(speak_first_pipeline=True, speak_model="")
    rt = _rt(spy, settings)

    async def go():
        rt.warm_speak_socket(state)
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())
    assert spy.speak_calls == []
    assert not any(k.startswith("socket:") for k in rt._prewarmed)


def test_no_socket_warm_for_non_speak_state():
    spy = _SpyLLM()
    settings = _settings(speak_first_pipeline=True, speak_model=LUNA)
    rt = _rt(spy, settings)

    async def go():
        rt.warm_speak_socket("Booking")          # tool-heavy -> gpt-5.4
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())
    assert spy.speak_calls == []
    assert not any(k.startswith("socket:") for k in rt._prewarmed)


def test_socket_warm_latched_once():
    spy = _SpyLLM()
    settings = _settings(speak_first_pipeline=True, speak_model=LUNA)
    rt = _rt(spy, settings)

    async def go():
        rt.warm_speak_socket("Intake")
        rt.warm_speak_socket("Intake")           # latched -> no re-fire
        await asyncio.gather(*list(rt._warm_tasks), return_exceptions=True)

    asyncio.run(go())
    sock = [c for c in spy.speak_calls if c["messages"] == SOCKET_MSG]
    assert len(sock) == 1
    assert f"socket:{LUNA}" in rt._prewarmed


# --------------------------------------------------------------------------- #
# 5 — the eager-hold / EOT deferred-tool path is untouched
# --------------------------------------------------------------------------- #
def test_eager_hold_path_untouched():
    src = (ROOT / "diallux" / "graph" / "builder.py").read_text()
    i = src.index("def warm_speak_socket")
    j = src.index("async def _warm(", i)
    seg = src[i:j]
    for sym in ("_fire_split_tools", "_stage_split_tools",
                "_execute_deferred_tools", "_apply_deferred_merge",
                "_await_warm"):
        assert sym not in seg, f"new warm must not touch {sym}"

    sess_src = (ROOT / "diallux" / "media" / "session.py").read_text()
    # additive: the existing four warms all still fire at call start
    for call in ("warm_rag", "warm_prompt_cache", "warm_speak_cache",
                 "warm_speak_socket"):
        assert call in sess_src, call
