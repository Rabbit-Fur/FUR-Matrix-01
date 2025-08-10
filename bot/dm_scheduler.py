from __future__ import annotations

import logging
from typing import Awaitable, Callable

from services.calendar_service import CalendarService

log = logging.getLogger(__name__)

SendDMCallback = Callable[[int, str], Awaitable[None]]


class DMReminderScheduler:
    """Trigger DM reminders for upcoming calendar events."""

    def __init__(self, service: CalendarService, send_dm_callback: SendDMCallback) -> None:
        self.service = service
        self.send_dm_callback = send_dm_callback
        self._sent: set[tuple[int, int]] = set()

    async def tick(self) -> None:
        """Check for upcoming events and send DMs via callback."""
        events = await self.service.list_upcoming_events()
        for ev in events:
            participants = self.service.events.database["event_participants"].find(
                {"event_id": ev.get("_id")}
            )
            for part in await participants.to_list(length=None):
                user_id = int(part.get("user_id", 0))
                if not user_id:
                    continue
                key = (ev.get("_id"), user_id)
                if key in self._sent:
                    continue
                message = f"Reminder: {ev['title']} at {ev['event_time'].strftime('%H:%M UTC')}"
                try:
                    await self.send_dm_callback(user_id, message)
                except Exception:  # noqa: BLE001
                    log.warning(
                        "Failed to send reminder to %s for event %s",
                        user_id,
                        ev.get("title"),
                        exc_info=True,
                    )
                    continue
                self._sent.add(key)
                log.info("Sent reminder DM to %s for event %s", user_id, ev["title"])


__all__ = ["DMReminderScheduler", "SendDMCallback"]
