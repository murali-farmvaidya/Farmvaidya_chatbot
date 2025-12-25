from fastapi import Request, HTTPException
from app.core.security import verify_jwt

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth.split(" ")[1]
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload["sub"]
