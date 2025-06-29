from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        return ObjectId(str(v))


class EventModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    google_id: str
    summary: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    sync_token: Optional[str] = None
    participants: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EventRepository:
    """Async helper for Google event documents."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def create(self, event: "EventModel") -> "EventModel":
        data = event.model_dump(by_alias=True)
        result = await self.collection.insert_one(data)
        event.id = result.inserted_id
        return event

    async def get_by_google_id(self, google_id: str) -> Optional["EventModel"]:
        raw = await self.collection.find_one({"google_id": google_id})
        return EventModel(**raw) if raw else None

    async def upsert_by_google_id(self, google_id: str, updates: dict) -> bool:
        updates["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"google_id": google_id},
            {"$set": updates},
            upsert=True,
        )
        return result.acknowledged
