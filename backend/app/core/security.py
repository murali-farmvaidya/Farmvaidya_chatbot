from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import JWT_SECRET

ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24

def create_jwt(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def verify_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None
