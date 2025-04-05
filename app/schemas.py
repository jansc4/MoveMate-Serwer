from typing import Optional, Literal

from pydantic import BaseModel, EmailStr

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