from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

# Hilfsklasse zur Unterstützung von ObjectId in Pydantic
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

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Hauptmodell für Events
class EventModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    description: Optional[str] = None
    date: str  # ISO-8601 Datum als Text
    participants: Optional[List[str]] = []

    @validator("date")
    def validate_date(cls, v):
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Datum muss im ISO-Format sein (z. B. 2025-06-20T18:00:00)")
        return v

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
