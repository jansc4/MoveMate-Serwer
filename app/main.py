from fastapi import FastAPI
from app.routes import users
from contextlib import asynccontextmanager
from app.database import connect_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()  # Połączenie z bazą danych przy starcie
    yield
    # Tu możesz dodać cleanup, np. zamknięcie połączeń

app = FastAPI(lifespan=lifespan)

# Rejestrowanie endpointów użytkowników
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the User API"}
