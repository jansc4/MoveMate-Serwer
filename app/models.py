from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional, Literal

class UserInDB(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    password: str
    role: Literal["admin", "user"] = "user"  # domyślnie każdy nowy użytkownik to user

    class Config:
        json_encoders = {
            ObjectId: str
        }
