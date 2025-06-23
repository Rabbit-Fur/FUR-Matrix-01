import asyncio
import types

from bot.cogs import reminder_autopilot as autopilot_mod


def test_run_reminder_check_skips(monkeypatch):
    send_called = False

    class FakeUser:
        async def send(self, msg):
            nonlocal send_called
            send_called = True

    class FakeBot:
        async def fetch_user(self, uid):
            return FakeUser()

    dummy = types.SimpleNamespace(bot=FakeBot(), get_user_language=lambda uid: "de")

    monkeypatch.setattr(autopilot_mod, "is_production", lambda: False)

    asyncio.run(autopilot_mod.ReminderAutopilot.run_reminder_check(dummy))

    assert send_called is False
