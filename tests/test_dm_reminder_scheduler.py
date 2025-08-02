from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_avoids_duplicate_dms(monkeypatch):
    from services import calendar_service as mod

    # prevent background task from starting
    monkeypatch.setattr(mod.tasks.Loop, "start", lambda self, *a, **k: None)

    class FakeUser:
        def __init__(self, uid, recorder):
            self.id = uid
            self.recorder = recorder

        async def send(self, msg):
            self.recorder.append((self.id, msg))

    class FakeBot:
        def __init__(self):
            self.sent = []

        async def wait_until_ready(self):
            return None

        async def fetch_user(self, uid):
            return FakeUser(uid, self.sent)

    class FakeParticipants:
        def __init__(self):
            self.docs = [{"user_id": "1"}]

        def find(self, query):
            return self

        async def to_list(self, length=None):
            return self.docs

    class FakeEventsCollection:
        def __init__(self):
            self.database = {"event_participants": FakeParticipants()}

    class FakeService:
        def __init__(self):
            self.events = FakeEventsCollection()

        async def _get_range(self, start, end):
            return [
                {
                    "_id": 99,
                    "title": "Test Event",
                    "event_time": datetime.utcnow().replace(tzinfo=timezone.utc),
                }
            ]

    bot = FakeBot()
    service = FakeService()

    scheduler = mod.DMReminderScheduler(bot, service)

    # run twice; second should be skipped due to cache
    await scheduler.reminder_loop()
    await scheduler.reminder_loop()

    assert len(bot.sent) == 1
