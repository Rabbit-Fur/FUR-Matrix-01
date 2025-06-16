# schemas/event_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class EventModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str
    description: Optional[str] = None
    date: str  # ISO Format
    participants: Optional[List[str]] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
