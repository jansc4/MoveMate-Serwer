import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
ALGORITHM = os.getenv("ALGORITHM", "HS256")
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))