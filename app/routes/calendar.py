from typing import List
from bson import ObjectId
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth import get_current_user


router = APIRouter()


