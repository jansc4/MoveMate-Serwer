from typing import List
from bson import ObjectId
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth import get_current_user
from app.schemas import CalendarCreate, CalendarResponse, StepsResponse, StepsUpdate, StepsHistoryResponse, \
    ExercisePerformanceResponse, ExercisePerformanceCreate, StepsGoalUpdate
from app.models import CalendarInDB, ExercisePerformanceInDB
from datetime import datetime
from fastapi import Path
from bson import ObjectId
from app.utils.tools import today, check_day

router = APIRouter()


@router.post("/calendar", response_model=CalendarResponse)
async def create_calendar_entry(
        calendar_data: CalendarCreate,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    calendar_inDB = CalendarInDB(**calendar_data.model_dump())
    calendar_inDB.user_id = current_user.id
    await check_day(calendar_inDB.date, db) # czy już istnieje
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
async def put_steps_today(
        steps: StepsUpdate,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    date = today()
    result = await db.calendar.find_one({"date": date, "user_id": current_user.id})

    if not result:
        # Utworzenie nowego wpisu z zachowaniem domyślnego maxSteps
        calendar_data = CalendarCreate(
            date=date,
            steps=steps.steps,
            maxSteps=10000  # domyślna wartość
        )
        result = await create_calendar_entry(calendar_data, db, current_user)
        return StepsResponse(steps=result.steps, maxSteps=result.maxSteps)

    # Aktualizacja tylko kroków, zachowując istniejący maxSteps
    await db.calendar.update_one(
        {"date": date, "user_id": current_user.id},
        {"$set": {"steps": steps.steps}}
    )

    updated_result = await db.calendar.find_one({"date": date, "user_id": current_user.id})
    return StepsResponse(steps=updated_result["steps"], maxSteps=updated_result["maxSteps"])

@router.put("/steps/today/goal", response_model=StepsResponse)
async def put_steps_today(
        steps: StepsGoalUpdate,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    date = today()
    result = await db.calendar.find_one({"date": date, "user_id": current_user.id})

    if not result:
        # Utworzenie nowego wpisu z zachowaniem domyślnego maxSteps
        calendar_data = CalendarCreate(
            date=date,
            steps=0,    # domyślna wartość
            maxSteps=steps.maxSteps
        )
        result = await create_calendar_entry(calendar_data, db, current_user)
        return StepsResponse(steps=result.steps, maxSteps=result.maxSteps)

    # Aktualizacja tylko kroków, zachowując istniejący maxSteps
    await db.calendar.update_one(
        {"date": date, "user_id": current_user.id},
        {"$set": {"maxSteps": steps.maxSteps}}
    )

    updated_result = await db.calendar.find_one({"date": date, "user_id": current_user.id})
    return StepsResponse(steps=updated_result["steps"], maxSteps=updated_result["maxSteps"])

@router.get("/steps/history", response_model=List[StepsHistoryResponse])
async def get_steps_history(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user=Depends(get_current_user),):
    history = []
    cursor = db.calendar.find(
        {"user_id": current_user.id},
        {"date": 1, "steps": 1, "_id": 0}
    )

    async for doc in cursor:
        history.append(StepsHistoryResponse(**doc))
    return history


@router.post("/calendar/{calendar_id}/exercise", response_model=ExercisePerformanceResponse)
async def add_exercise_to_calendar(
        calendar_id: str,
        exercise: ExercisePerformanceCreate,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    # Sprawdź czy wpis kalendarza istnieje
    calendar = await db.calendar.find_one({"_id": ObjectId(calendar_id), "user_id": current_user.id})
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar entry not found")

    # Utwórz nowy obiekt ćwiczenia z ID
    exercise_id = str(ObjectId())
    exercise_with_id = {**exercise.model_dump(), "id": exercise_id}

    # Dodaj ćwiczenie do listy
    result = await db.calendar.update_one(
        {"_id": ObjectId(calendar_id)},
        {"$push": {"exercises": exercise_with_id}}
    )

    return ExercisePerformanceResponse(**exercise_with_id)


@router.put("/calendar/{calendar_id}/exercise/{exercise_id}", response_model=ExercisePerformanceResponse)
async def update_exercise_in_calendar(
        calendar_id: str,
        exercise_id: str,
        exercise: ExercisePerformanceCreate,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    # Sprawdź czy wpis kalendarza istnieje
    calendar = await db.calendar.find_one({
        "_id": ObjectId(calendar_id),
        "user_id": current_user.id,
        "exercises.id": exercise_id
    })
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar entry or exercise not found")

    # Aktualizuj ćwiczenie w tablicy
    update_data = {f"exercises.$.{k}": v for k, v in exercise.model_dump().items() if v is not None}
    result = await db.calendar.update_one(
        {
            "_id": ObjectId(calendar_id),
            "exercises.id": exercise_id
        },
        {"$set": update_data}
    )

    # Pobierz zaktualizowany dokument
    updated_calendar = await db.calendar.find_one({
        "_id": ObjectId(calendar_id),
        "exercises.id": exercise_id
    })
    updated_exercise = next(ex for ex in updated_calendar["exercises"] if ex["id"] == exercise_id)

    return ExercisePerformanceResponse(**updated_exercise)


@router.delete("/calendar/{calendar_id}/exercise/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_from_calendar(
        calendar_id: str,
        exercise_id: str,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        current_user=Depends(get_current_user),
):
    # Sprawdź czy wpis kalendarza istnieje
    calendar = await db.calendar.find_one({
        "_id": ObjectId(calendar_id),
        "user_id": current_user.id,
        "exercises.id": exercise_id
    })
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar entry or exercise not found")

    # Usuń ćwiczenie z tablicy
    result = await db.calendar.update_one(
        {"_id": ObjectId(calendar_id)},
        {"$pull": {"exercises": {"id": exercise_id}}}
    )

