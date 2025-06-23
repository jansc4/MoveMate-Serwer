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
    exerciseType: ExerciseType
    difficulty: Difficulty

class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    exerciseType: ExerciseType
    difficulty: Difficulty

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    exerciseType: Optional[ExerciseType] = None
    difficulty: Optional[Difficulty] = None



class ExercisePerformanceBase(BaseModel):
    exercise_id: str
    duration_min: Optional[int] = None
    numberOfSets: Optional[int] = None
    numberOfRepetitions: Optional[int] = None
    weight: Optional[float] = None
    intervalBetween_days: Optional[int] = None
    done: Optional[bool] = False
    notes: Optional[str] = None

class ExercisePerformanceCreate(ExercisePerformanceBase):
    pass

class ExercisePerformanceResponse(ExercisePerformanceBase):
    id: str

class CalendarBase(BaseModel):
    date: datetime
    steps: Optional[int] = None
    maxSteps: Optional[int] = None
    exercises: Optional[List[ExercisePerformanceCreate]] = []

class CalendarCreate(CalendarBase):
    #user_id: str
    pass

class CalendarResponse(CalendarBase):
    id: str
    user_id: str
    exercises: Optional[List[ExercisePerformanceResponse]] = []

class StepsBase(BaseModel):
    steps: Optional[int] = None

class StepsGoalUpdate(BaseModel):
    maxSteps: int

class StepsCreate(StepsBase):
    maxSteps: Optional[int] = None

class StepsUpdate(StepsBase):
    pass
class StepsResponse(StepsBase):
    maxSteps: Optional[int] = None

class StepsHistoryResponse(BaseModel):
    steps: Optional[int] = 0
    date: datetime
