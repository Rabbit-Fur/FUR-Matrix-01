import importlib
import pathlib
import sys
import types

import pytest
from flask import current_app

services_pkg = types.ModuleType("services")
services_pkg.__path__ = [str(pathlib.Path(__file__).resolve().parents[1] / "services")]
sys.modules["services"] = services_pkg

autopilot_mod = importlib.import_module("bot.cogs.reminder_autopilot")


class DummyUser:
    def __init__(self) -> None:
        self.sent: str | None = None

    async def send(self, msg: str) -> None:
        self.sent = msg


@pytest.mark.asyncio
async def test_reminder_autopilot_sends_with_app_context(monkeypatch):
    monkeypatch.setattr(autopilot_mod.tasks.Loop, "start", lambda self, *a, **k: None)

    user = DummyUser()

    async def fetch_user(uid: int):
        return user

    bot = types.SimpleNamespace(fetch_user=fetch_user)
    cog = autopilot_mod.ReminderAutopilot(bot)

    monkeypatch.setattr(autopilot_mod, "is_production", lambda: True)
    monkeypatch.setattr(autopilot_mod, "is_opted_out", lambda _uid: False)
    monkeypatch.setattr(
        autopilot_mod.ReminderAutopilot, "get_user_language", lambda self, uid: "en"
    )
    monkeypatch.setattr(autopilot_mod.Config, "REMINDER_ROLE_ID", 0, raising=False)

    class EventsCol:
        def find_one(self, query):  # pragma: no cover - simple stub
            return {"_id": "1", "google_id": "abc", "title": "Test Event"}

    class ParticipantsCol:
        def find(self, query):  # pragma: no cover - simple stub
            return [{"user_id": "123"}]

    class RemindersSentCol:
        def find_one(self, query):  # pragma: no cover - simple stub
            return None

        def insert_one(self, doc):  # pragma: no cover - simple stub
            self.inserted = doc

    def fake_get_collection(name):  # pragma: no cover - simple stub
        mapping = {
            "events": EventsCol(),
            "event_participants": ParticipantsCol(),
            "reminders_sent": RemindersSentCol(),
        }
        return mapping.get(name, types.SimpleNamespace(find_one=lambda q: None))

    monkeypatch.setattr(autopilot_mod, "get_collection", fake_get_collection)

    def fake_list_upcoming_events(service, **kwargs):
        current_app.name  # will raise if context missing
        return [{"id": "abc", "title": "Test Event"}]

    monkeypatch.setattr(autopilot_mod, "get_service", lambda settings: object())
    monkeypatch.setattr(autopilot_mod, "list_upcoming_events", fake_list_upcoming_events)
    monkeypatch.setattr(autopilot_mod, "t", lambda key, title, lang: f"Reminder: {title}")

    await cog.run_reminder_check()
    assert user.sent == "Reminder: Test Event"
