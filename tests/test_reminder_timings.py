import asyncio
import types
from datetime import datetime, timedelta

from bot.cogs import reminder_autopilot as autopilot_mod
from bot.cogs import reminder_cog as cog_mod
from config import Config
from utils import event_helpers


class DummyCollection(list):
    def find(self, *args, **kwargs):
        return self

    def sort(self, *args, **kwargs):
        return self

    def find_one(self, query):
        for doc in self:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def insert_one(self, doc):
        self.append(doc)


class DummyUser:
    def __init__(self):
        self.sent = None

    async def send(self, msg):
        self.sent = msg


def test_autopilot_sends_with_role_mention(monkeypatch):
    user = DummyUser()

    async def fetch_user(uid):
        return user

    bot = types.SimpleNamespace(fetch_user=fetch_user)
    cog = autopilot_mod.ReminderAutopilot.__new__(autopilot_mod.ReminderAutopilot)
    cog.bot = bot

    async def fake_lang(uid):
        return "en"

    cog.get_user_language = fake_lang

    now = datetime.utcnow()
    event = {"_id": 1, "title": "Ping", "event_time": now + timedelta(minutes=10, seconds=1)}
    monkeypatch.setattr(autopilot_mod, "datetime", types.SimpleNamespace(utcnow=lambda: now))
    events_col = DummyCollection([event])
    participants_col = DummyCollection([{"user_id": "1", "event_id": 1}])
    sent_col = DummyCollection()
    optout_col = DummyCollection()
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
    monkeypatch.setattr(event_helpers, "get_collection", get_coll)
    monkeypatch.setattr(autopilot_mod, "is_production", lambda: True)
    monkeypatch.setattr(Config, "REMINDER_ROLE_ID", 99)

    asyncio.run(autopilot_mod.ReminderAutopilot.run_reminder_check(cog))

    assert user.sent.startswith("<@&99>")
    assert len(sent_col) == 1


def test_reminder_cog_sends_60min(monkeypatch):
    user = DummyUser()

    async def fetch_user(uid):
        return user

    bot = types.SimpleNamespace(get_user=lambda uid: user, fetch_user=fetch_user)
    cog = cog_mod.ReminderCog.__new__(cog_mod.ReminderCog)
    cog.bot = bot
    cog.get_user_language = lambda uid: "en"

    now = datetime.utcnow()
    event = {"_id": 2, "title": "Test", "event_time": now + timedelta(minutes=60, seconds=1)}
    monkeypatch.setattr(cog_mod, "datetime", types.SimpleNamespace(utcnow=lambda: now))
    events_col = DummyCollection([event])
    participants_col = DummyCollection([{"user_id": "1", "event_id": 2}])
    sent_col = DummyCollection()
    optout_col = DummyCollection()
    user_settings_col = DummyCollection()

    def get_coll(name):
        return {
            "events": events_col,
            "participants": participants_col,
            "reminders_sent": sent_col,
            "reminder_optout": optout_col,
            "user_settings": user_settings_col,
        }[name]

    monkeypatch.setattr(cog_mod, "get_collection", get_coll)
    monkeypatch.setattr(event_helpers, "get_collection", get_coll)
    monkeypatch.setattr(Config, "REMINDER_ROLE_ID", None)

    asyncio.run(cog_mod.ReminderCog.check_reminders(cog))

    assert user.sent and "<@&" not in user.sent
    assert len(sent_col) == 1
