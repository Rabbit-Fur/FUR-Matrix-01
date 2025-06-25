import asyncio
import importlib
import warnings


def test_create_bot_no_runtime_warning(monkeypatch):
    monkeypatch.setenv("ENABLE_DISCORD_BOT", "true")
    from bot import bot_main

    mod = importlib.reload(bot_main)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", RuntimeWarning)
        asyncio.run(mod.create_bot())
    assert not any(issubclass(w_.category, RuntimeWarning) for w_ in w)
