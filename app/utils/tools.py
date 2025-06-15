from app.database import get_db
from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, date, time

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

async def check_day(required_day: datetime, db: AsyncIOMotorDatabase):
    """
    Sprawdza, czy dzień jest już w bazie danych.

    Args:
        required_day (str): dzień, który ma zostać sprawdzony.
        db: Obiekt bazy danych.

    Raises:
        HTTPException: Jeśli dzień jest już w kalendarzu, zgłasza błąd 400 (Bad Request).
    """
    print(f"🔗 Połączono z bazą: {db}")  # Debug print, można usunąć w produkcji
    existing = await db.calendar.find_one({"date": required_day})
    if existing:
        raise HTTPException(status_code=400, detail=f"Day '{required_day}' already exists.")

def today():
    today_date = date.today()
    datetime_with_zero_time = datetime.combine(today_date, time.min)
    return datetime_with_zero_time
