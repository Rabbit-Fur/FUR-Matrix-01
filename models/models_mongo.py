from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

# ➕ Custom ObjectId Type für Pydantic-Kompatibilität
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        try:
            return ObjectId(str(v))
        except Exception:
            raise ValueError("Ungültige ObjectId")

# 🧑 Benutzer-Mongo-Modell (für Flask & FastAPI kompatibel)
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    discord_id: str
    username: str
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    role_level: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "discord_id": "123456789012345678",
                "username": "FURUser",
                "avatar": "https://cdn.discordapp.com/avatars/123/avatar.png",
                "email": "user@example.com",
                "role_level": "R3"
            }
        }
