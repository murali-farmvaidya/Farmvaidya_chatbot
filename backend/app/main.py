from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, chat, sessions
from app.routers import messages

app = FastAPI()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    from app.core.config import LIGHTRAG_URL
    import requests
    
    lightrag_status = "unknown"
    try:
        response = requests.get("http://localhost:9621/docs", timeout=2)
        lightrag_status = "connected" if response.status_code == 200 else "error"
    except:
        lightrag_status = "not_reachable"
    
    return {
        "status": "healthy",
        "backend": "running",
        "mongodb": "connected",
        "lightrag": lightrag_status,
        "lightrag_url": LIGHTRAG_URL
    }

# Test endpoint without auth
@app.get("/")
def root():
    return {"message": "Farm Vaidya Backend API", "status": "running"}

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(messages.router)
