from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from models.models_mongo import PyObjectId


class ParticipantModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    event_id: str
    user_id: str
    joined_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
