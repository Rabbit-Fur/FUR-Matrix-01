from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fur_mongo import db
from schemas.event_schema import EventModel

log = logging.getLogger(__name__)

COLLECTION_NAME = "calendar_events"
collection = db[COLLECTION_NAME]


async def create_event(
    event: EventModel,
    *,
    col=None,
) -> EventModel:
    """Insert a new event document."""
    col = col or collection
    data = event.model_dump(by_alias=True)
    result = await asyncio.to_thread(col.insert_one, data)
    event.id = result.inserted_id
    return event


async def get_event_by_id(
    event_id: str | ObjectId,
    *,
    col=None,
) -> Optional[EventModel]:
    """Return a single event by ObjectId."""
    col = col or collection
    if not isinstance(event_id, ObjectId):
        event_id = ObjectId(event_id)
    doc = await asyncio.to_thread(col.find_one, {"_id": event_id})
    return EventModel(**doc) if doc else None


async def delete_event_by_id(
    event_id: str | ObjectId,
    *,
    col=None,
) -> int:
    """Delete an event by its ObjectId. Returns number of deleted docs."""
    col = col or collection
    if not isinstance(event_id, ObjectId):
        event_id = ObjectId(event_id)
    res = await asyncio.to_thread(col.delete_one, {"_id": event_id})
    return res.deleted_count


async def get_events_by_guild(
    guild_id: str,
    *,
    col=None,
) -> List[EventModel]:
    """Return all events for a Discord guild."""
    col = col or collection
    docs = await asyncio.to_thread(lambda: list(col.find({"guild_id": guild_id})))
    return [EventModel(**d) for d in docs]


async def get_events_in_range(
    start: datetime,
    end: datetime,
    *,
    col=None,
) -> List[EventModel]:
    """Return events between ``start`` and ``end`` sorted by time."""
    col = col or collection
    docs = await asyncio.to_thread(
        lambda: list(col.find({"event_time": {"$gte": start, "$lt": end}}).sort("event_time", 1))
    )
    return [EventModel(**d) for d in docs]


async def upsert_event(
    data: dict,
    *,
    col=None,
) -> None:
    """Upsert an event document by ``google_id`` field."""
    col = col or collection
    await asyncio.to_thread(
        col.update_one,
        {"google_id": data["google_id"]},
        {"$set": data},
        upsert=True,
    )
