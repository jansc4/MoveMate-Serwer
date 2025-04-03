from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from bson import ObjectId
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: User, db=Depends(get_db)):
    """Rejestracja nowego użytkownika"""

    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password=password)
    result = await db.users.insert_one(new_user.dict())

    return UserResponse(username=user.username, email=user.email)

@router.post("/login")
async def login_user(user: UserCreate, db=Depends(get_db)):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}
