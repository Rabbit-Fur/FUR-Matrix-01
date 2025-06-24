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
    event = {"_id": 1, "title": "Test", "event_time": now + timedelta(minutes=5)}
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
