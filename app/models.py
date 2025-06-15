from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Optional, Literal, List
from app.utils.Enums import ExerciseType, Difficulty
from app.schemas import ExercisePerformanceBase
from app.schemas import CalendarBase

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

class ExerciseInDB(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    exerciseType: ExerciseType
    difficulty: Difficulty

    class Config:
        json_encoders = {
            ObjectId: str
        }

class ExercisePerformanceInDB(ExercisePerformanceBase):
    id: Optional[str] = None
    exercise_id: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}


class CalendarInDB(CalendarBase):
    user_id: Optional[str] = None
    exercises: Optional[List["ExercisePerformanceInDB"]] = []

    class Config:
        json_encoders = {ObjectId: str}

