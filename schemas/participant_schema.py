from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from models.models_mongo import PyObjectId


class ParticipantModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    event_id: str
    user_id: str
    joined_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat()},
    )
