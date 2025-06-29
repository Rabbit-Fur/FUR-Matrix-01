import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional

from discord.ext import tasks
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from config import Config
from google_auth import load_credentials

log = logging.getLogger(__name__)


class SyncTokenExpired(Exception):
    """Raised when a stored sync token is no longer valid."""


def _parse_datetime(info: Optional[dict]) -> Optional[datetime]:
    if not info:
        return None
    value = info.get("dateTime") or info.get("date")
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class CalendarService:
    """Synchronize Google Calendar events into MongoDB via Motor."""

    def __init__(
        self,
        *,
        calendar_id: Optional[str] = None,
        mongo_uri: Optional[str] = None,
        events_collection: Optional[AsyncIOMotorCollection] = None,
        tokens_collection: Optional[AsyncIOMotorCollection] = None,
    ) -> None:
        self.calendar_id = calendar_id or Config.GOOGLE_CALENDAR_ID
        uri = mongo_uri or Config.MONGODB_URI or "mongodb://localhost:27017/furdb"
        if events_collection and tokens_collection:
            self.client = None
            self.events = events_collection
            self.tokens = tokens_collection
        else:
            self.client = AsyncIOMotorClient(uri)
            db = self.client.get_default_database()
            self.events = db["events"]
            self.tokens = db["calendar_tokens"]

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _build_service() -> Any | None:
        creds = load_credentials()
        if not creds:
            log.warning("Google credentials missing – cannot sync")
            return None
        return build("calendar", "v3", credentials=creds, cache_discovery=False)

    async def _api_list(self, params: dict) -> dict:
        service = self._build_service()
        if not service:
            return {}
        return await asyncio.to_thread(service.events().list(**params).execute)

    # ------------------------------------------------------------------
    # Sync logic
    # ------------------------------------------------------------------
    async def _get_token(self) -> Optional[str]:
        doc = await self.tokens.find_one({"_id": "google"})
        return doc.get("token") if doc else None

    async def _store_token(self, token: str) -> None:
        await self.tokens.update_one({"_id": "google"}, {"$set": {"token": token}}, upsert=True)

    @staticmethod
    def _build_doc(event: dict) -> dict:
        start_dt = _parse_datetime(event.get("start"))
        end_dt = _parse_datetime(event.get("end"))
        event_time = start_dt
        if event_time:
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)
            else:
                event_time = event_time.astimezone(timezone.utc)
        return {
            "google_id": event.get("id"),
            "title": event.get("summary", "No Title"),
            "description": event.get("description"),
            "location": event.get("location"),
            "updated": event.get("updated"),
            "start": start_dt,
            "end": end_dt,
            "event_time": event_time,
            "source": "google",
            "status": event.get("status"),
        }

    async def _store_events(self, events: Iterable[dict]) -> None:
        for ev in events:
            doc = self._build_doc(ev)
            if not doc["google_id"]:
                continue
            await self.events.update_one(
                {"google_id": doc["google_id"]}, {"$set": doc}, upsert=True
            )

    async def sync(self) -> int:
        token = await self._get_token()
        params = {
            "calendarId": self.calendar_id,
            "singleEvents": True,
            "showDeleted": True,
            "maxResults": 2500,
        }
        if token:
            params["syncToken"] = token
        else:
            params["timeMin"] = datetime.utcnow().isoformat() + "Z"
        try:
            data = await self._api_list(params)
        except HttpError as exc:
            if exc.resp.status == 410:  # sync token expired
                token = None
                params.pop("syncToken", None)
                params["timeMin"] = datetime.utcnow().isoformat() + "Z"
                data = await self._api_list(params)
            else:
                raise
        events = data.get("items", [])
        await self._store_events(events)
        new_token = data.get("nextSyncToken")
        if new_token:
            await self._store_token(new_token)
        return len(events)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    async def _get_range(self, start: datetime, end: datetime) -> list[dict]:
        cursor = self.events.find({"event_time": {"$gte": start, "$lt": end}}).sort("event_time", 1)
        return await cursor.to_list(length=None)

    async def get_events_today(self) -> list[dict]:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return await self._get_range(start, end)

    async def get_events_week(self) -> list[dict]:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        return await self._get_range(start, end)


class DMReminderScheduler:
    """Send DM reminders for upcoming events."""

    def __init__(self, bot: Any, service: CalendarService) -> None:
        self.bot = bot
        self.service = service
        self.reminder_loop.start()

    def cog_unload(self) -> None:  # pragma: no cover - lifecycle
        self.reminder_loop.cancel()

    @tasks.loop(minutes=1)
    async def reminder_loop(self) -> None:
        await self.bot.wait_until_ready()
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        window_start = now + timedelta(minutes=10)
        window_end = now + timedelta(minutes=11)
        events = await self.service._get_range(window_start, window_end)
        for ev in events:
            participants = self.service.events.database["event_participants"].find(
                {"event_id": ev.get("_id")}
            )
            for part in await participants.to_list(length=None):
                try:
                    user = await self.bot.fetch_user(int(part["user_id"]))
                    await user.send(
                        f"Reminder: {ev['title']} at {ev['event_time'].strftime('%H:%M UTC')}"
                    )
                except Exception:  # pragma: no cover - network failures
                    log.warning("Failed to send reminder", exc_info=True)


__all__ = ["CalendarService", "DMReminderScheduler", "SyncTokenExpired"]
