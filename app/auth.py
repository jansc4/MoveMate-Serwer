from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from app.database import get_db
from bson import ObjectId
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# Ustawiamy scope'y tutaj
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scopes={
    "user": "Standard user",
    "admin": "Administrator access"
})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashuje hasło przy użyciu algorytmu bcrypt.

    Args:
        password (str): Hasło do zahaszowania.

    Returns:
        str: Zahaszowane hasło.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Weryfikuje, czy podane hasło pasuje do zahaszowanego.

    Args:
        plain_password (str): Hasło wprowadzone przez użytkownika.
        hashed_password (str): Zahaszowane hasło w bazie danych.

    Returns:
        bool: True, jeśli hasło jest poprawne, w przeciwnym razie False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Tworzy access token z danymi użytkownika i czasem wygaśnięcia.

    Args:
        data (dict): Dane użytkownika, które mają być zapisane w tokenie.
        expires_delta (timedelta, optional): Czas, po którym token wygaśnie.

    Returns:
        str: Wygenerowany access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """
    Tworzy refresh token z danymi użytkownika i czasem wygaśnięcia.

    Args:
        data (dict): Dane użytkownika, które mają być zapisane w tokenie.

    Returns:
        str: Wygenerowany refresh token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """
    Weryfikuje i dekoduje token.

    Args:
        token (str): Token do weryfikacji.

    Returns:
        dict: Dekodowane dane tokenu lub None w przypadku błędu.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """
    Pobiera aktualnego użytkownika na podstawie tokenu i sprawdza jego uprawnienia.

    Args:
        security_scopes (SecurityScopes): Scopes wymagane do dostępu do zasobów.
        token (str): Token użytkownika.
        db: Obiekt bazy danych.

    Raises:
        HTTPException: Jeśli token jest nieprawidłowy, użytkownik nie istnieje lub brakuje uprawnień.

    Returns:
        dict: Dane użytkownika.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": f"Bearer scope='{security_scopes.scope_str}'"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    return user
