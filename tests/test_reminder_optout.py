import asyncio
import types
from datetime import datetime, timedelta

import pytest

from bot.cogs import reminder_autopilot as autopilot_mod


class DummyCollection(list):
    def find(self, *args, **kwargs):
        return self

    def find_one(self, query):
        for doc in self:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    def insert_one(self, doc):
        self.append(doc)


class DummyUser:
    def __init__(self):
        self.sent = False

    async def send(self, msg):
        self.sent = True


def test_autopilot_ignores_opted_out_user(monkeypatch):
    user = DummyUser()
    bot = types.SimpleNamespace(fetch_user=lambda uid: user)
    cog = autopilot_mod.ReminderAutopilot.__new__(autopilot_mod.ReminderAutopilot)
    cog.bot = bot

    async def fake_lang(uid):
        return "en"

    cog.get_user_language = fake_lang

    now = datetime.utcnow()
    event = {"_id": 1, "title": "Test", "event_time": now + timedelta(minutes=10)}
    events_col = DummyCollection([event])
    participants_col = DummyCollection([{"user_id": "123", "event_id": 1}])
    sent_col = DummyCollection()
    optout_col = DummyCollection([{"discord_id": "123"}])
    user_settings_col = DummyCollection()

    def get_coll(name):
        return {
            "events": events_col,
            "event_participants": participants_col,
            "reminders_sent": sent_col,
            "reminder_optout": optout_col,
            "user_settings": user_settings_col,
        }[name]

    monkeypatch.setattr(autopilot_mod, "get_collection", get_coll)

    asyncio.run(autopilot_mod.ReminderAutopilot.run_reminder_check(cog))

    assert not user.sent
    assert sent_col == []


@pytest.mark.asyncio
async def test_send_poster_skips_opted_out(monkeypatch):
    called = {"sent": False}

    async def fake_send(file=None):
        called["sent"] = True

    member = types.SimpleNamespace(id=1, bot=False, send=fake_send)
    guild = types.SimpleNamespace(members=[member])
    bot = types.SimpleNamespace(get_guild=lambda gid: guild)

    monkeypatch.setattr(autopilot_mod, "is_opted_out", lambda uid: True)
    monkeypatch.setattr(autopilot_mod.discord, "File", lambda p: p)
    monkeypatch.setattr(asyncio, "sleep", lambda d: None)

    cog = autopilot_mod.ReminderAutopilot.__new__(autopilot_mod.ReminderAutopilot)
    cog.bot = bot
    cog.delay = 0

    await autopilot_mod.ReminderAutopilot._send_poster_to_members(cog, "poster", "daily")
