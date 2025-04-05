from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.models import UserInDB
from app.schemas import UserCreate, UserResponse, TokenResponse
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from bson import ObjectId

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db=Depends(get_db)):
    """Rejestracja nowego użytkownika"""
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    hashed_password = hash_password(user.password)
    new_user = UserInDB(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    await db.users.insert_one(new_user.model_dump())

    return UserResponse(username=user.username, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """
    Logowanie z użyciem OAuth2PasswordRequestForm, który oczekuje:
    - application/x-www-form-urlencoded
    - pola: username i password
    Dla nas: username == email
    """
    db_user = await db.users.find_one({"email": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_id = str(db_user["_id"])
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"]
    }
