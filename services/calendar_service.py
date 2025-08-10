import asyncio
import logging
import os
from datetime import date as date_type, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo.errors import ConfigurationError

from crud import event_crud
from services.google.calendar_sync import CalendarSettings, load_credentials
from schemas.event_schema import EventModel
from utils.time_utils import parse_calendar_datetime

log = logging.getLogger(__name__)


class SyncTokenExpired(Exception):
    """Raised when a stored sync token is no longer valid."""


class CalendarService:
    """Synchronize Google Calendar events into MongoDB via Motor."""

    def __init__(
        self,
        *,
        calendar_id: Optional[str] = None,
        mongo_uri: Optional[str] = None,
        events_collection: Optional[AsyncIOMotorCollection] = None,
        tokens_collection: Optional[AsyncIOMotorCollection] = None,
        token_path: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ) -> None:
        self.calendar_id = calendar_id or os.getenv("GOOGLE_CALENDAR_ID")
        self.token_path = (
            token_path
            or os.getenv("GOOGLE_TOKEN_STORAGE_PATH")
            or os.getenv(
                "GOOGLE_CREDENTIALS_FILE",
                "/data/google_token.json",
            )
        )
        self.scopes = scopes or ["https://www.googleapis.com/auth/calendar.readonly"]
        self.service: Any | None = None
        uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/furdb")
        if events_collection is not None and tokens_collection is not None:
            self.client = None
            self.events = events_collection
            self.tokens = tokens_collection
        else:
            self.client = AsyncIOMotorClient(uri)
            try:
                db = self.client.get_default_database()
            except ConfigurationError:
                db_name = os.getenv("MONGO_DB", "furdb")
                db = self.client[db_name]
            self.events = db["events"]
            self.tokens = db["calendar_tokens"]

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------
    def _build_service(self) -> None:
        if self.service:
            return
        settings = CalendarSettings(
            token_path=Path(self.token_path),
            calendar_id=self.calendar_id,
            scopes=self.scopes,
        )
        creds = load_credentials(settings)
        if not creds:
            raise SyncTokenExpired
        self.service = build(
            "calendar",
            "v3",
            credentials=creds,
            cache_discovery=False,
        )

    async def _api_list(self, params: dict) -> dict:
        self._build_service()
        if not self.service:
            log.warning("Calendar service not initialized – skipping")
            return {}
        return await asyncio.to_thread(self.service.events().list(**params).execute)

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
        start_dt = parse_calendar_datetime(event.get("start"))
        end_dt = parse_calendar_datetime(event.get("end"))
        event_time = start_dt
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
            await event_crud.upsert_event(doc, col=self.events)

    async def sync(self) -> int:
        log.info("Starting calendar sync for %s", self.calendar_id)
        self._build_service()
        if not self.service:
            log.warning("Calendar service not initialized – skipping")
            return 0
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
                log.warning("Sync token expired; performing full sync")
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
        log.info("Calendar sync complete: %s events", len(events))
        return len(events)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    async def _get_range(self, start: datetime, end: datetime) -> list[dict]:
        events = await event_crud.get_events_in_range(start, end, col=self.events)
        return [e.model_dump(by_alias=True) if isinstance(e, EventModel) else e for e in events]

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

    async def get_next_event(self) -> Optional[dict]:
        """Return the next upcoming event or ``None`` if none found."""
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        window_end = now + timedelta(days=365)
        events = await self._get_range(now, window_end)
        return events[0] if events else None

    async def get_events_for_date(self, dt: datetime | date_type) -> list[dict]:
        """Return events for the given day in UTC."""
        if isinstance(dt, datetime):
            day = dt.date()
        else:
            day = dt
        start = datetime.combine(day, datetime.min.time(), timezone.utc)
        end = start + timedelta(days=1)
        return await self._get_range(start, end)

    async def list_upcoming_events(self) -> list[dict]:
        """Return events starting roughly 10 minutes from now."""
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        start = now + timedelta(minutes=10)
        end = start + timedelta(minutes=1)
        return await self._get_range(start, end)


__all__ = ["CalendarService", "SyncTokenExpired"]
