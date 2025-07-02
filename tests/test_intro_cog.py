import asyncio
import json
import types

import pytest

from bot.cogs import intro_cog as mod


class FakeUser:
    def __init__(self):
        self.sent = False

    async def send(self, *, embed=None, file=None):
        self.sent = True


@pytest.mark.asyncio
async def test_maybe_send_intro(monkeypatch, tmp_path):
    intro_json = tmp_path / "intro.json"
    intro_json.write_text(json.dumps({"embeds": [{"title": "T"}]}))
    intro_img = tmp_path / "img.png"
    intro_img.write_text("img")
    monkeypatch.setattr(mod, "INTRO_JSON", intro_json)
    monkeypatch.setattr(mod, "INTRO_IMAGE", intro_img)

    flags = {}

    class FakeCollection:
        def find_one(self, q):
            return flags.get("flag")

        def update_one(self, q, u, upsert=False):
            flags["flag"] = u["$set"]

    monkeypatch.setattr(mod, "get_collection", lambda name: FakeCollection())
    monkeypatch.setattr(mod, "get_dm_users", lambda: [1])

    user = FakeUser()

    async def dummy_wait() -> None:
        pass

    async def dummy_fetch(uid):
        return user

    fake_bot = types.SimpleNamespace(
        fetch_user=dummy_fetch,
        wait_until_ready=dummy_wait,
        loop=asyncio.get_event_loop(),
    )

    cog = mod.IntroCog.__new__(mod.IntroCog)
    cog.bot = fake_bot
    await mod.IntroCog._maybe_send_intro(cog)

    assert user.sent
    assert flags["flag"]["value"] is True
