from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.routers import auth, chat, sessions
from app.routers import messages
import requests

app = FastAPI()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://chatbot-frontend-4i6h.onrender.com",  # Production frontend
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

# Proxy to LightRAG docs (for accessing Swagger UI on Render)
@app.get("/lightrag/docs", response_class=HTMLResponse)
def lightrag_docs():
    """Proxy to LightRAG Swagger documentation"""
    try:
        response = requests.get("http://localhost:9621/docs", timeout=5)
        return response.text
    except Exception as e:
        return f"<html><body><h1>LightRAG Not Available</h1><p>Error: {str(e)}</p></body></html>"

@app.get("/lightrag/openapi.json")
def lightrag_openapi():
    """Proxy to LightRAG OpenAPI spec"""
    try:
        response = requests.get("http://localhost:9621/openapi.json", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(messages.router)
