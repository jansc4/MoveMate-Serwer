from typing import Optional, Literal, List
from app.utils.Enums import ExerciseType, Difficulty
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = ""
    token_type: str

class UserProfileResponse(UserResponse):
    id: str
    role: Literal["admin", "user"]

class UpdateUserProfile(UserCreate):
    role: Literal["admin", "user"]

class ExerciseCreate(BaseModel):
    name: str
    description: str
    video_url: str
    thumbnail_url: str
    exerciseType: ExerciseType
    difficulty: Difficulty

class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: str
    video_url: str
    thumbnail_url: str
    exerciseType: ExerciseType
    difficulty: Difficulty

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    exerciseType: Optional[ExerciseType] = None
    difficulty: Optional[Difficulty] = None

class CalendarCreate(BaseModel):
    user_id: ObjectId = None
    date: datetime = None
    steps: int = None
    maxSteps: int = None
    exercises: Optional[List] = None    # List[ExercisePerformance]

class ExercisePerformanceBase(BaseModel):
    exercise_id: str
    duration_min: Optional[int] = None
    numberOfSets: Optional[int] = None
    numberOfRepetitions: Optional[int] = None
    weight: Optional[float] = None
    intervalBetween_days: Optional[int] = None
    done: Optional[bool] = None
    notes: Optional[str] = None

class ExercisePerformanceCreate(ExercisePerformanceBase):
    pass

class ExercisePerformanceResponse(ExercisePerformanceBase):
    id: str