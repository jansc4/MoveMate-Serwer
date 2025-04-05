from bson import ObjectId
from fastapi import HTTPException, status, Depends
from app.database import get_db

def check_role(current_user: dict, required_role: str):
    """
    Sprawdza, czy użytkownik posiada wymaganą rolę.

    Args:
        current_user (dict): Dane użytkownika, który jest aktualnie zalogowany.
        required_role (str): Rola, którą użytkownik musi posiadać.

    Raises:
        HTTPException: Jeśli użytkownik nie ma wymaganej roli, zgłasza błąd 403 (Forbidden).
    """
    if required_role not in current_user.get("role", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {required_role}",
        )

async def check_email(required_email: str, db=Depends(get_db)):
    """
    Sprawdza, czy email jest już używany przez innego użytkownika w bazie danych.

    Args:
        required_email (str): Email, który ma zostać sprawdzony.
        db: Obiekt bazy danych.

    Raises:
        HTTPException: Jeśli email jest już w użyciu, zgłasza błąd 400 (Bad Request).
    """
    print(f"🔗 Połączono z bazą: {db}")  # Debugging
    existing_user = await db.users.find_one({"email": required_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

async def check_id(required_id: str, db=Depends(get_db)):
    """
    Sprawdza, czy użytkownik o podanym identyfikatorze istnieje w bazie danych.

    Args:
        required_id (str): ID użytkownika, którego istnienie ma zostać zweryfikowane.
        db: Obiekt bazy danych.

    Returns:
        dict: Dane użytkownika, jeśli istnieje.

    Raises:
        HTTPException: Jeśli użytkownik o danym ID nie istnieje, zgłasza błąd 404 (Not Found).
    """
    existing_user = await db.users.find_one({"_id": ObjectId(required_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    return existing_user
