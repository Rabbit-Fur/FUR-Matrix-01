from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Ungültige ObjectId")
        return ObjectId(v)


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    discord_id: str
    username: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    role_level: str  # z. B. "R3", "R4", "ADMIN"
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
