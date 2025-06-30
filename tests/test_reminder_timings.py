import asyncio
import types
from datetime import datetime, timedelta

import pytest

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
    event = {
        "_id": 1,
        "title": "Ping",
        "event_time": now + timedelta(minutes=10, seconds=1),
        "google_event_id": "g1",
    }
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
    monkeypatch.setattr(autopilot_mod, "fetch_upcoming_events", lambda *a, **k: [{"id": "g1"}])
    monkeypatch.setattr(autopilot_mod, "get_calendar_service", lambda: object())
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
            "event_participants": participants_col,
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


class FileCaptureUser:
    def __init__(self):
        self.kwargs = None
        self.bot = False
        self.id = 1

    async def send(self, *args, **kwargs):
        self.kwargs = kwargs


@pytest.mark.asyncio
async def test_daily_poster_attachment(monkeypatch, tmp_path):
    member = FileCaptureUser()
    guild = types.SimpleNamespace(members=[member])
    bot = types.SimpleNamespace(get_guild=lambda gid: guild)

    def fake_get_collection(name):
        if name == "events":
            now = datetime.utcnow()
            return DummyCollection(
                [
                    {"title": "Event", "event_time": now.isoformat()},
                ]
            )
        return DummyCollection()

    poster_file = tmp_path / "poster.png"
    poster_file.write_bytes(b"img")

    monkeypatch.setattr(autopilot_mod.tasks.Loop, "start", lambda self: None)
    monkeypatch.setattr(autopilot_mod, "get_collection", fake_get_collection)
    monkeypatch.setattr(autopilot_mod.Config, "DISCORD_GUILD_ID", 1)
    monkeypatch.setattr(autopilot_mod, "is_opted_out", lambda uid: False)
    monkeypatch.setattr(
        autopilot_mod.poster_generator,
        "generate_text_poster",
        lambda *a, **k: str(poster_file),
    )
    monkeypatch.setattr(autopilot_mod.discord, "File", lambda p: {"path": p})

    cog = autopilot_mod.ReminderAutopilot(bot)
    await cog.send_daily_poster()

    assert member.kwargs["file"]["path"] == str(poster_file)
    assert not member.kwargs.get("content")
