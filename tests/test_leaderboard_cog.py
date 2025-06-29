import asyncio
import types

import bot.cogs.leaderboard as lb_mod
from fur_lang import i18n


class DummyCollection:
    def __init__(self):
        self.find_calls = 0
        self.distinct_calls = 0

    def distinct(self, field):
        self.distinct_calls += 1
        return ["raids"]

    def find(self, query):
        self.find_calls += 1
        assert query["category"] == "raids"
        return self

    def sort(self, *args, **kwargs):
        return self

    def limit(self, n):
        return [{"username": "Alice", "score": 5, "category": "raids"}]


class DummyUsers:
    def find_one(self, flt):
        return None


class DummyInteraction:
    def __init__(self):
        self.user = types.SimpleNamespace(id=1, display_name="Tester")
        self.response = types.SimpleNamespace()

        async def send_message(msg, ephemeral=False):
            self.sent = msg
            self.ephemeral = ephemeral

        self.response.send_message = send_message


def test_leaderboard_cache(monkeypatch):
    monkeypatch.setattr(
        i18n,
        "translations",
        {
            "en": {
                "leaderboard_message": "{header}\n{content}",
                "leaderboard_header": "LB",
                "leaderboard_unknown_category": "bad",
                "leaderboard_error": "err",
            },
            "de": {
                "leaderboard_message": "{header}\n{content}",
                "leaderboard_header": "LB",
                "leaderboard_unknown_category": "bad",
                "leaderboard_error": "err",
            },
        },
    )
    dummy = DummyCollection()
    monkeypatch.setattr(
        lb_mod, "get_collection", lambda name: dummy if name == "leaderboard" else DummyUsers()
    )
    monkeypatch.setattr(lb_mod.tasks.Loop, "start", lambda self, *a, **k: None)

    bot = types.SimpleNamespace()

    async def wait_until_ready():
        return None

    bot.wait_until_ready = wait_until_ready
    cog = lb_mod.Leaderboard(bot)
    asyncio.run(cog._update_all_categories())
    assert dummy.find_calls == 1

    interaction = DummyInteraction()
    asyncio.run(cog.top_players.callback(cog, interaction, "raids"))
    assert dummy.find_calls == 1
    assert "Alice" in interaction.sent


def test_cog_unload_cancels(monkeypatch):
    monkeypatch.setattr(
        i18n,
        "translations",
        {
            "en": {
                "leaderboard_message": "{header}\n{content}",
                "leaderboard_header": "LB",
                "leaderboard_unknown_category": "bad",
                "leaderboard_error": "err",
            },
            "de": {
                "leaderboard_message": "{header}\n{content}",
                "leaderboard_header": "LB",
                "leaderboard_unknown_category": "bad",
                "leaderboard_error": "err",
            },
        },
    )
    bot = types.SimpleNamespace()

    monkeypatch.setattr(lb_mod.tasks.Loop, "start", lambda self, *a, **k: None)

    async def wait_until_ready():
        return None

    bot.wait_until_ready = wait_until_ready
    cog = lb_mod.Leaderboard(bot)
    called = False

    def fake_cancel():
        nonlocal called
        called = True

    cog.update_leaderboards.cancel = fake_cancel
    cog.cog_unload()
    assert called
