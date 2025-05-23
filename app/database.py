from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URL


client = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["fitness_app"]
    print(f"🔗 Połączono z bazą: {db}")  # Debugging
    try:
        if "users" not in await db.list_collection_names():
            await db.create_collection("users")
        if "calendar" not in await db.list_collection_names():
            await db.create_collection("calendar")
        if "exercises" not in await db.list_collection_names():
            await db.create_collection("exercises")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

async def get_db():
    """Zwraca instancję bazy danych"""
    global db
    if db is None:
        raise RuntimeError("🚨 Brak połączenia z bazą!")
    return db