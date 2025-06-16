from pydantic import BaseModel, Field, validator
from typing import Optional, List
from bson import ObjectId
from datetime import datetime


class ReminderModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    event_id: str
    message: str
    send_time: str  # ISO 8601 Zeit als Text
    lang: Optional[str] = "de"
    participants: Optional[List[str]] = []
    sent: Optional[bool] = False

    @validator("send_time")
    def validate_send_time(cls, v):
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Zeit muss im ISO-Format sein (z. B. 2025-06-25T19:00:00)")
        return v

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
