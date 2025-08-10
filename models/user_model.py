from datetime import datetime
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, ConfigDict, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        return ObjectId(str(v))


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    discord_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class UserRepository:
    """Async helper for CRUD operations on the users collection."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def create(self, user: "UserModel") -> "UserModel":
        data = user.model_dump(by_alias=True)
        result = await self.collection.insert_one(data)
        user.id = result.inserted_id
        return user

    async def get_by_discord_id(self, discord_id: str) -> Optional["UserModel"]:
        raw = await self.collection.find_one({"discord_id": discord_id})
        return UserModel(**raw) if raw else None

    async def update_tokens(
        self, discord_id: str, *, access_token: str, refresh_token: str, token_expiry: datetime
    ) -> bool:
        result = await self.collection.update_one(
            {"discord_id": discord_id},
            {
                "$set": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_expiry": token_expiry,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return result.modified_count > 0
