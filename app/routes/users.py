from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.models import UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated
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
async def register_user(user: UserCreate, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    """
    Registers a new user in the system.

    Args:
        user (UserCreate): The user data for registration.
        db (Database): The database connection.

    Returns:
        UserResponse: The response with the newly registered user's username and email.
    """
    await check_email(str(user.email), db)
    hashed_password = hash_password(user.password)
    new_user = UserInDB(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    await db.users.insert_one(new_user.model_dump())

    return UserResponse(username=user.username, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login_user(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logs a user in using OAuth2PasswordRequestForm and returns access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.
        db (Database): The database connection.

    Returns:
        TokenResponse: The response containing access and refresh tokens.
    """
    db_user = await db.users.find_one({"email": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_id = str(db_user["_id"])
    role = db_user.get("role", "user")  # Default to 'user' if no role is defined

    # Add scopes to tokens based on role
    access_token = create_access_token({
        "sub": user_id,
        "scopes": [role]  # Scopes must be a list
    })

    refresh_token = create_refresh_token({
        "sub": user_id
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    """
    Refreshes the access token using a valid refresh token.

    Args:
        refresh_token (str): The refresh token used to generate a new access token.
        db (Database): The database connection.

    Returns:
        TokenResponse: The response containing the new access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the refresh token
    payload = verify_token(refresh_token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # Find the user in the database
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception

    # Generate a new access token
    access_token = create_access_token(data={"sub": user_id, "scopes": user["role"]})

    return TokenResponse(
        access_token=access_token, token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """
    Retrieves the current user's username and email.

    Args:
        current_user (UserInDB): The current authenticated user.

    Returns:
        UserResponse: The response containing the current user's username and email.
    """
    return {
        "username": current_user.username,
        "email": current_user.email
    }


@router.get("/user_profile", response_model=List[UserProfileResponse])
async def user_profile(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user: dict = Depends(get_current_user)):
    """
    Retrieves a list of all user profiles in the system. Only accessible by admins.

    Args:
        current_user (dict): The current authenticated user.
        db (Database): The database connection.

    Returns:
        List[UserProfileResponse]: A list of user profiles.
    """
    check_role(current_user, "admin")

    # Fetch all users from the database
    users_cursor = db.users.find()
    users = await users_cursor.to_list(length=None)

    # Create a response with a list of UserProfileResponse instances
    user_profiles = [UserProfileResponse(username=user["username"], email=user["email"], id=str(user["_id"]),
                                         role=user["role"]) for user in users]

    return user_profiles


@router.get("/user_profile/{user_id}", response_model=UserProfileResponse)
async def user_profile_with_id(user_id: str,db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],  current_user: dict = Depends(get_current_user)):
    """
    Retrieves a user profile by ID. Only accessible by admins.

    Args:
        user_id (str): The ID of the user to fetch.
        current_user (dict): The current authenticated user.
        db (Database): The database connection.

    Returns:
        UserProfileResponse: The user's profile response.
    """
    check_role(current_user, "admin")

    # Fetch the user from the database by ID
    user = await check_id(str(user_id), db)

    # Create and return the user profile response
    user_profile = UserProfileResponse(
        username=user["username"],
        email=user["email"],
        id=str(user["_id"]),
        role=user["role"]
    )

    return user_profile


@router.get("/user_profile/email/{email}", response_model=UserProfileResponse)
async def user_profile_by_email(email: str,db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],  current_user: dict = Depends(get_current_user)):
    """
    Retrieves a user profile by email. Only accessible by admins.

    Args:
        email (str): The email of the user to fetch.
        current_user (dict): The current authenticated user.
        db (Database): The database connection.

    Returns:
        UserProfileResponse: The user's profile response.
    """
    check_role(current_user, "admin")

    # Fetch the user from the database by email
    user = await db.users.find_one({"email": email})

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Create and return the user profile response
    user_profile = UserProfileResponse(
        username=user["username"],
        email=user["email"],
        id=str(user["_id"]),
        role=user["role"]
    )

    return user_profile


@router.post("/user_profile", response_model=UserProfileResponse)
async def create_user_profile(user: UpdateUserProfile, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],  current_user: dict = Depends(get_current_user)):
    """
    Creates a new user profile. Only accessible by admins.

    Args:
        user (UpdateUserProfile): The data for the new user.
        current_user (dict): The current authenticated user.
        db (Database): The database connection.

    Returns:
        UserProfileResponse: The newly created user's profile response.
    """
    check_role(current_user, "admin")

    await check_email(str(user.email), db)

    # Create a new user with the provided data
    hashed_password = hash_password(user.password)
    new_user = UserInDB(username=user.username, email=user.email, password=hashed_password, role=user.role)

    result = await db.users.insert_one(new_user.model_dump())

    return UserProfileResponse(
        username=user.username,
        email=user.email,
        id=str(result.inserted_id),
        role=user.role
    )


@router.put("/user_profile/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, user: UpdateUserProfile, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],  current_user: dict = Depends(get_current_user)):
    """
    Updates a user's profile. Only accessible by admins.

    Args:
        user_id (str): The ID of the user to update.
        user (UpdateUserProfile): The updated user data.
        current_user (dict): The current authenticated user.
        db (Database): The database connection.

    Returns:
        UserProfileResponse: The updated user's profile response.
    """
    check_role(current_user, "admin")

    # Ensure the user exists
    existing_user = await check_id(str(user_id), db=db)

    updated_user = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role
    }

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_user})

    return UserProfileResponse(
        username=user.username,
        email=user.email,
        id=user_id,
        role=user.role
    )


@router.delete("/user_profile/{user_id}", response_model=UserProfileResponse)
async def delete_user_profile(user_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user: dict = Depends(get_current_user)):
    """
    Deletes a user's profile. Only accessible by admins.

    Args:
        user_id (str): The ID of the user to delete.
        current_user (dict): The current authenticated user.
        db (Database): The database connection.

    Returns:
        UserProfileResponse: The deleted user's profile response.
    """
    check_role(current_user, "admin")

    existing_user = await check_id(str(user_id), db)

    delete_result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    return UserProfileResponse(
        username=existing_user["username"],
        email=existing_user["email"],
        id=user_id,
        role=existing_user["role"]
    )
