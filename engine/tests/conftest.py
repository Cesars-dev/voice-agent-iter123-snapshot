"""Shared test configuration — tests are hermetic to ambient environment.

iter91 (2026-10-03): pydantic Settings reads `.env` from CWD, so a worktree's
LANE .env (real keys, possibly stale values) silently changed suite behavior
(the "which .env am I testing against" disease). Evidence that blocking is
suite-safe: iter91 audit ran the full suite with and without a .env present —
identical red set (10) in both conditions. Tests pin their own Settings
explicitly; anything needing real credentials must opt in deliberately.
"""

import pytest


def pytest_configure(config):
    """iter123b: collection-time hermeticity.

    Test modules build module-level `Settings(...)` (e.g. test_iter30's
    SETTINGS) at IMPORT/collection time — BEFORE the per-test fixture below
    can neutralize env_file. Those objects therefore read the lane's .env:
    observed `speak_first_pipeline=True`, `speak_model=gpt-5.6-luna`,
    `max_call_turns=128` on a lane .env with SPEAK_FIRST_PIPELINE=1, which
    drifted ~25 suite results (the split arm firing inside pre-split fakes:
    `TypeError: astream() got an unexpected keyword argument 'speak'`, and
    `fake_llm.py:41 pop from empty` when the split consumed extra rounds).

    Neutralize env_file for the WHOLE session from configuration time
    (runs before any test module is imported), so module-level Settings are
    as hermetic as per-test ones. Env VARS still apply (deliberate opt-in).
    """
    from diallux.config import Settings, get_settings

    Settings.model_config = {**Settings.model_config, "env_file": None}
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _no_ambient_env_file(monkeypatch):
    from diallux.config import Settings, get_settings

    monkeypatch.setattr(
        Settings, "model_config", {**Settings.model_config, "env_file": None}
    )
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
