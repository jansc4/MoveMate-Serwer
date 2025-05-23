from typing import List
from bson import ObjectId
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import ExerciseInDB
from app.utils import ExerciseType, Difficulty
from app.utils.tools import check_exercise
from app.schemas import (
    ExerciseCreate, ExerciseResponse, ExerciseUpdate
)
from app.auth import get_current_user

router = APIRouter()

@router.post("/exercise", response_model=ExerciseResponse)
async def add_exercise(exercise: ExerciseCreate, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user=Depends(get_current_user)):
    await check_exercise(exercise.name, db)
    new_exercise = ExerciseInDB(**exercise.model_dump())
    result = await db.exercises.insert_one(new_exercise.model_dump(exclude={"id"}))

    return ExerciseResponse(id=str(result.inserted_id), **exercise.model_dump())

@router.get("/exercises", response_model=List[ExerciseResponse])
async def list_exercises(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user=Depends(get_current_user)):
    exercises = await db.exercises.find().to_list(length=100)
    return [ExerciseResponse(id=str(ex["_id"]), **{k: ex[k] for k in ExerciseCreate.model_fields.keys()}) for ex in exercises]

@router.get("/exercises/types", response_model=List[str])
async def list_exercises_types(current_user=Depends(get_current_user)):
    exercises_types = [et.value for et in ExerciseType]
    return exercises_types

@router.get("/exercises/difficulties", response_model=List[str])
async def list_exercises_difficulties(current_user=Depends(get_current_user)):
    exercises_difficulties = [et.value for et in Difficulty]
    return exercises_difficulties

@router.get("/exercise/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: str,db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user=Depends(get_current_user)):
    exercise = await db.exercises.find_one({"_id": ObjectId(exercise_id)})
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return ExerciseResponse(id=str(exercise["_id"]), **{k: exercise[k] for k in ExerciseCreate.model_fields.keys()})

@router.put("/exercise/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(exercise_id: str, update: ExerciseCreate, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user=Depends(get_current_user)):
    existing = await db.exercises.find_one({"_id": ObjectId(exercise_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Exercise not found")

    await db.exercises.update_one({"_id": ObjectId(exercise_id)}, {"$set": update.model_dump()})
    updated = await db.exercises.find_one({"_id": ObjectId(exercise_id)})
    return ExerciseResponse(id=str(updated["_id"]), **{k: updated[k] for k in ExerciseCreate.model_fields.keys()})

@router.delete("/exercise/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_id: str,db: Annotated[AsyncIOMotorDatabase, Depends(get_db)], current_user=Depends(get_current_user)):
    result = await db.exercises.delete_one({"_id": ObjectId(exercise_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return None