from bson import ObjectId
from fastapi import HTTPException, status, Depends
from app.database import get_db

def check_role(current_user: dict, required_role: str):
    if required_role not in current_user.get("role", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {required_role}",
        )

async def check_email(required_email: str, db=Depends(get_db)):
    existing_user = await db.users.find_one({"email": required_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

async def check_id(required_id: str, db=Depends(get_db)):
    existing_user = await db.users.find_one({"_id": ObjectId(required_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    return existing_user