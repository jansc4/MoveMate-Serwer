from typing import List
from bson import ObjectId
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth import get_current_user
from app.schemas import CalendarCreate, CalendarResponse, StepsResponse, StepsCreate
from app.models import CalendarInDB, ExercisePerformanceInDB
from datetime import datetime
from fastapi import Path
from bson import ObjectId
from app.utils.tools import today

router = APIRouter()


@router.post("/calendar", response_model=CalendarResponse)
async def create_calendar_entry(
        calendar_data: CalendarCreate,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    calendar_inDB = CalendarInDB(**calendar_data.model_dump())
    calendar_inDB.user_id = current_user.id
    check = await db.calendar.find_one({"date": calendar_data.date})
    if check is None:
        raise HTTPException(status_code=404, detail="Calendar entry already exist")
    result = await db.calendar.insert_one(calendar_inDB.model_dump(exclude={"id"}))

    return CalendarResponse(id=str(result.inserted_id), **calendar_inDB.model_dump())

@router.get("/calendar", response_model=List[CalendarResponse])
async def get_all_calendar_entries(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),
):
    # Pobierz wszystkie wpisy kalendarza użytkownika
    entries = []
    cursor = db.calendar.find({"user_id": current_user.id})
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        entries.append(CalendarResponse(**doc))
    return entries


@router.get("/calendar/{calendar_id}", response_model=CalendarResponse)
async def get_calendar_entry(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    calendar_id: str = Path(..., description="ID wpisu kalendarza"),
    current_user=Depends(get_current_user),
):
    doc = await db.calendar.find_one({"_id": ObjectId(calendar_id), "user_id": current_user.id})
    if not doc:
        raise HTTPException(status_code=404, detail="Calendar entry not found")
    doc["id"] = str(doc["_id"])
    return CalendarResponse(**doc)


@router.put("/calendar/{calendar_id}", response_model=CalendarResponse)
async def update_calendar_entry(
    calendar_id: str,
    calendar_data: CalendarCreate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),
):
    updated_data = {k: v for k, v in calendar_data.model_dump().items() if v is not None}
    result = await db.calendar.update_one(
        {"_id": ObjectId(calendar_id), "user_id": current_user.id},
        {"$set": updated_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Calendar entry not found")

    # Pobierz zaktualizowany wpis
    doc = await db.calendar.find_one({"_id": ObjectId(calendar_id)})
    doc["id"] = str(doc["_id"])
    return CalendarResponse(**doc)


@router.delete("/calendar/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_entry(
    calendar_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),
):
    result = await db.calendar.delete_one({"_id": ObjectId(calendar_id), "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Calendar entry not found")


@router.get("/calendar/date/date}", response_model=CalendarResponse)
async def get_calendar_entry(
        date: datetime,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user)
):
    day = date

    # Pobierz dokument
    result = await db.calendar.find_one(
        {"date": day, "user_id": current_user.id}
    )
    if not result:
        raise HTTPException(status_code=404, detail="Calendar entry not found")

    # Przygotuj odpowiedź
    result["id"] = str(result["_id"])
    return CalendarResponse(**result)

@router.get("/steps/today", response_model=StepsResponse)
async def get_steps_today(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),):
    date = today()
    result = await db.calendar.find_one({"date": date, "user_id": current_user.id})
    if not result:
        raise HTTPException(status_code=404, detail="Brak danych dla dzisiejszego dnia")
    return StepsResponse(steps=result["steps"], maxSteps=result["maxSteps"])

###########
@router.put("/steps/today", response_model=StepsResponse)
async def get_steps_today(steps: StepsCreate, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),):
    date = today()
    result = await db.calendar.find_one({"date": date, "user_id": current_user.id})
    if not result:
        raise HTTPException(status_code=404, detail="Nie znaleziono daty")
    return StepsResponse(steps=result["steps"], maxSteps=result["maxSteps"])

@router.get("/steps", response_model=StepsResponse)
async def get_steps_today(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),):
    date = today()
    result = await db.calendar.find_one({"date": date, "user_id": current_user.id})
    if not result:
        raise HTTPException(status_code=404, detail="Brak danych dla dzisiejszego dnia")
    return StepsResponse(steps=result["steps"], maxSteps=result["maxSteps"])
