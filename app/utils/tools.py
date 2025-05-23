from app.database import get_db
from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

async def check_exercise(required_exercise: str, db: AsyncIOMotorDatabase):
    """
    Sprawdza, czy ćwiczenie jest już w bazie danych.

    Args:
        required_exercise (str): ćwiczenie, który ma zostać sprawdzone.
        db: Obiekt bazy danych.

    Raises:
        HTTPException: Jeśli ćwiczenie jest już w użyciu, zgłasza błąd 400 (Bad Request).
    """
    print(f"🔗 Połączono z bazą: {db}")  # Debug print, można usunąć w produkcji
    existing = await db.exercises.find_one({"name": required_exercise})
    if existing:
        raise HTTPException(status_code=400, detail=f"Exercise '{required_exercise}' already exists.")