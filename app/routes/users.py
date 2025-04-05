from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.models import UserInDB
from app.utils.security import check_role, check_email, check_id
from app.schemas import UserCreate, UserResponse, TokenResponse, UserProfileResponse, UpdateUserProfile
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user
)



router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db=Depends(get_db)):
    """Rejestracja nowego użytkownika"""
    await  check_email(str(user.email))
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
    role = db_user.get("role", "user")  # domyślnie 'user' jeśli nie ma pola

    # Dodajemy 'scopes' do tokenów na podstawie roli
    access_token = create_access_token({
        "sub": user_id,
        "scopes": [role]  # scopes muszą być listą
    })

    refresh_token = create_refresh_token({
        "sub": user_id
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def refresh_token(refresh_token: str, db=Depends(get_db)):
    """Odświeżanie access tokena za pomocą refresh tokena"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Weryfikacja refresh tokena
    payload = verify_token(refresh_token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # Znajdź użytkownika w bazie
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception

    # Generowanie nowego access tokena
    access_token = create_access_token(data={"sub": user_id, "scopes": user["role"]})

    return TokenResponse(
        access_token=access_token,token_type="bearer")



@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"]
    }


@router.get("/user_profile", response_model=List[UserProfileResponse])
async def user_profile(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Tylko administratorzy mają dostęp
    check_role(current_user, "admin")

    # Pobieramy wszystkich użytkowników z bazy danych
    users_cursor = db.users.find()
    users = await users_cursor.to_list(length=None)  # Pobiera całą kolekcję użytkowników

    # Tworzymy odpowiedź w formie listy instancji UserProfileResponse
    user_profiles = [UserProfileResponse(username=user["username"], email=user["email"], id=user["_id"],
                                         role=user["role"]) for user in users]

    return user_profiles

@router.get("/user_profile/{user_id}", response_model=UserProfileResponse)
async def user_profile_with_id(user_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Sprawdzamy, czy użytkownik ma rolę "admin"
    check_role(current_user, "admin")

    # Pobieramy użytkownika z bazy danych na podstawie ID
    user = await check_id(str(user_id), db=db)

    # Tworzymy odpowiedź w formie instancji UserProfileResponse
    user_profile = UserProfileResponse(
        username=user["username"],
        email=user["email"],
        id=str(user["_id"]),  # Konwertujemy ObjectId na string
        role=user["role"]
    )

    return user_profile

@router.get("/user_profile/email/{email}", response_model=UserProfileResponse)
async def user_profile_by_email(email: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Sprawdzamy, czy użytkownik ma rolę "admin"
    check_role(current_user, "admin")

    # Pobieramy użytkownika z bazy danych na podstawie emaila
    user = await db.users.find_one({"email": email})

    # Jeśli użytkownik nie został znaleziony, rzucamy wyjątek
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Tworzymy odpowiedź w formie instancji UserProfileResponse
    user_profile = UserProfileResponse(
        username=user["username"],
        email=user["email"],
        id=str(user["_id"]),  # Konwertujemy ObjectId na string
        role=user["role"]
    )

    return user_profile


@router.post("/user_profile", response_model=UserProfileResponse)
async def create_user_profile(user: UpdateUserProfile, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Sprawdzamy, czy użytkownik ma rolę "admin"
    check_role(current_user, "admin")

    # Sprawdzamy, czy użytkownik o podanym emailu już istnieje

    await check_email(str(user.email))

    # Tworzymy nowego użytkownika
    hashed_password = hash_password(user.password)  # Haszujemy hasło
    new_user = UserInDB(username=user.username, email=user.email, password=hashed_password, role=user.role)

    # Zapisujemy użytkownika w bazie
    result = await db.users.insert_one(new_user.model_dump())

    # Tworzymy odpowiedź
    return UserProfileResponse(
        username=user.username,
        email=user.email,
        id=str(result.inserted_id),  # Zwracamy ID nowego użytkownika
        role=user.role
    )


@router.put("/user_profile/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, user: UpdateUserProfile, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Sprawdzamy, czy użytkownik ma rolę "admin"
    check_role(current_user, "admin")

    # Sprawdzamy, czy użytkownik o danym ID istnieje
    existing_user = await check_id(str(user_id), db=db)

    # Aktualizujemy dane użytkownika
    updated_user = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),  # Haszujemy hasło
        "role": user.role
    }

    # Zaktualizowanie użytkownika w bazie
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_user})

    # Tworzymy odpowiedź
    return UserProfileResponse(
        username=user.username,
        email=user.email,
        id=user_id,
        role=user.role
    )


@router.delete("/user_profile/{user_id}", response_model=UserProfileResponse)
async def delete_user_profile(user_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Sprawdzamy, czy użytkownik ma rolę "admin"
    check_role(current_user, "admin")

    # Sprawdzamy, czy użytkownik o danym ID istnieje
    existing_user = await check_id(str(user_id), db=db)

    # Usuwamy użytkownika z bazy
    delete_result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    # Tworzymy odpowiedź
    return UserProfileResponse(
        username=existing_user["username"],
        email=existing_user["email"],
        id=user_id,
        role=existing_user["role"]
    )

