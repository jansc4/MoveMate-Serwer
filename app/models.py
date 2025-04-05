from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class UserInDB(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    password: str

    class Config:
        # Dodajemy, by Pydantic poprawnie obsługiwało ID MongoDB
        json_encoders = {
            ObjectId: str
        }