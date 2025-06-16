# schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    discord_id: str = Field(..., example="123456789012345678")
    username: str
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    role_level: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserOut(UserModel):
    id: str

    class Config:
        orm_mode = True
