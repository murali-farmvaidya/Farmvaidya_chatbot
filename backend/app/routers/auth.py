from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext

from app.db.mongo import users
from app.core.security import create_jwt
from app.core.config import GOOGLE_CLIENT_ID

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

router = APIRouter(prefix="/auth")  # ✅ THIS WAS MISSING

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- MODELS ----------------

class LoginIn(BaseModel):
    email: str
    password: str

class GoogleToken(BaseModel):
    token: str

class SignupIn(BaseModel):
    email: str
    password: str

# ---------------- UTILS ----------------

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# ---------------- EMAIL LOGIN ----------------

@router.post("/login")
def login(data: LoginIn):
    user = users.find_one({"email": data.email})

    if not user or "password" not in user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({
        "sub": str(user["_id"]),
        "email": user["email"]
    })

    return {"access_token": token}

# ---------------- SIGNUP ----------------

@router.post("/signup")
def signup(data: SignupIn):
    if users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = pwd_context.hash(data.password)

    user = {
        "email": data.email,
        "password": hashed,
        "auth_provider": "local"
    }

    result = users.insert_one(user)

    token = create_jwt({
        "sub": str(result.inserted_id),
        "email": data.email
    })

    return {"access_token": token}

# ---------------- GOOGLE LOGIN ----------------

@router.post("/google")
def google_login(data: GoogleToken):
    try:
        info = id_token.verify_oauth2_token(
            data.token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info["email"]
    name = info.get("name")

    user = users.find_one({"email": email})

    if not user:
        user = {
            "email": email,
            "name": name,
            "auth_provider": "google",
            "google_id": info["sub"]
        }
        users.insert_one(user)

    token = create_jwt({
        "sub": str(user["_id"]),
        "email": email
    })

    return {"access_token": token}
