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

# Proxy all LightRAG requests (docs, static files, API endpoints)
from fastapi import Request, Response
from starlette.background import BackgroundTask

@app.api_route("/lightrag/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_lightrag(path: str, request: Request):
    """Proxy all requests to LightRAG server"""
    lightrag_base = "http://localhost:9621"
    url = f"{lightrag_base}/{path}"
    
    # Forward query parameters
    if request.url.query:
        url = f"{url}?{request.url.query}"
    
    try:
        # Forward the request
        if request.method == "GET":
            response = requests.get(url, timeout=10)
        elif request.method == "POST":
            body = await request.body()
            response = requests.post(url, data=body, headers={"Content-Type": request.headers.get("content-type", "application/json")}, timeout=10)
        else:
            return {"error": f"Method {request.method} not supported in proxy"}
        
        # Return the response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except Exception as e:
        return {"error": f"LightRAG proxy error: {str(e)}"}

# Proxy static files from LightRAG (for Swagger UI CSS, JS, etc.)
@app.get("/static/{path:path}")
async def proxy_static(path: str):
    """Proxy static files from LightRAG server"""
    try:
        response = requests.get(f"http://localhost:9621/static/{path}", timeout=10)
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except Exception as e:
        return {"error": f"Static file error: {str(e)}"}

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except Exception as e:
        return {"error": f"LightRAG proxy error: {str(e)}"}

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(messages.router)
