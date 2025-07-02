import importlib
import sys
import types

import pytest
from bson import ObjectId


class DummyCursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs


class DummyCollection:
    def __init__(self, docs=None):
        self.docs = docs or []

    async def find_one(self, flt):
        for d in self.docs:
            if all(d.get(k) == v for k, v in flt.items()):
                return d
        return None

    def find(self, query):
        matched = [d for d in self.docs if all(d.get(k) == v for k, v in query.items())]
        return DummyCursor(matched)


class DummyUser:
    def __init__(self):
        self.sent = None

    async def send(self, msg):
        self.sent = msg


@pytest.mark.asyncio
async def test_send_reminder(monkeypatch):
    stub_bot_main = types.SimpleNamespace(bot=types.SimpleNamespace(fetch_user=lambda uid: None))
    monkeypatch.setitem(sys.modules, "bot.bot_main", stub_bot_main)
    monkeypatch.setitem(sys.modules, "discord_util", types.ModuleType("discord_util"))
    if "bot.reminder_system" in sys.modules:
        del sys.modules["bot.reminder_system"]
    mod = importlib.import_module("bot.reminder_system")

    rid = str(ObjectId())
    reminder = {"_id": ObjectId(rid), "message": "ping"}
    reminders = DummyCollection([reminder])
    participants = DummyCollection([{"discord_id": "1", "reminder_id": rid}])
    monkeypatch.setattr(mod, "reminders_col", reminders)
    monkeypatch.setattr(mod, "participants_col", participants)

    user = DummyUser()

    async def fetch_user(uid):
        assert uid == 1
        return user

    monkeypatch.setattr(mod.bot, "fetch_user", fetch_user)

    count = await mod._send_reminder(rid)
    assert count == 1
    assert user.sent == "ping"
