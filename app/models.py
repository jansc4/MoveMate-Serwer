from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Optional, Literal
from app.utils.Enums import ExerciseType, Difficulty
from schemas import ExercisePerformanceBase

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
    video_url: str
    thumbnail_url: str
    exerciseType: ExerciseType
    difficulty: Difficulty

    class Config:
        json_encoders = {
            ObjectId: str
        }

class ExercisePerformanceInDB(ExercisePerformanceBase):
    id: Optional[str] = None
    exercise_id: ObjectId

    class Config:
        json_encoders = {ObjectId: str}