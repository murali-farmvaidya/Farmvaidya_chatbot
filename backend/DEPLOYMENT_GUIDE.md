# Farm Vaidya Backend + LightRAG Unified Deployment

This document explains how to run both the FastAPI backend and LightRAG server together as a single deployment.

## 🏗️ Architecture

This deployment runs two services:
1. **Backend API** (FastAPI) - Port 8000
2. **LightRAG Server** - Port 9621

Both services run independently but can be started/stopped together using the provided scripts.

## 📋 Prerequisites

### 1. Backend Virtual Environment
```powershell
# Create and activate backend venv
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. LightRAG Setup
```powershell
# Navigate to LightRAG directory
cd lightrag\Lightrag_main

# Install uv (if not already installed)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add uv to PATH for current session
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"

# Sync LightRAG dependencies
uv sync --extra api

# Install Bun (for WebUI)
powershell -c "irm https://bun.sh/install.ps1 | iex"
$env:Path = "$env:USERPROFILE\.bun\bin;$env:Path"

# Build WebUI
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..
```

### 3. Environment Configuration

**IMPORTANT**: Both Backend and LightRAG now use a **single shared `.env` file** located in `backend/` directory.

Create a `.env` file in the `backend/` directory by copying the example:
```powershell
# From the backend/ directory
cp .env.example .env
```

Then edit `.env` with your values:
```env
# Backend Configuration
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
LIGHTRAG_API_URL=http://localhost:9621

# LightRAG Configuration
GEMINI_API_KEY=your_gemini_api_key_here
LLM_BINDING=gemini
LLM_MODEL=gemini-2.0-flash-lite
EMBEDDING_BINDING=gemini
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=768

# ... (see .env.example for all available options)
```

The startup script automatically copies this `.env` file to the LightRAG directory, ensuring both services use the same configuration. This is **perfect for Render deployment** where you only need to set environment variables once.

## 🚀 Starting Services

### Quick Start
```powershell
# From the backend/ directory
.\start_all_services.ps1
```

This will:
- ✅ Check if virtual environments exist
- ✅ Check if ports are available
- ✅ Start Backend Server in a new window (port 8000)
- ✅ Start LightRAG Server in a new window (port 9621)
- ✅ Display access URLs

### Manual Start (Alternative)

#### Terminal 1 - Backend
```powershell
cd backend
.\venv\Scripts\Activate
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - LightRAG
```powershell
cd backend\lightrag\Lightrag_main
.\.venv\Scripts\Activate
lightrag-server
```

## 🛑 Stopping Services

### Quick Stop
```powershell
# From the backend/ directory
.\stop_all_services.ps1
```

This will:
- 🛑 Stop all processes on port 8000 (Backend)
- 🛑 Stop all processes on port 9621 (LightRAG)
- 🛑 Clean up any remaining uvicorn/lightrag processes

### Manual Stop
- Press `CTRL+C` in each terminal window
- Or close the PowerShell windows

## 🌐 Service URLs

Once started, you can access:

### Backend
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### LightRAG
- **API**: http://localhost:9621
- **WebUI**: http://localhost:9621/webui
- **Documentation**: http://localhost:9621/docs
- **Alternative Docs**: http://localhost:9621/redoc

## 🔍 Troubleshooting

### Port Already in Use
If you see "port already in use" errors:
```powershell
# Stop all services first
.\stop_all_services.ps1

# Check if ports are still occupied
Get-NetTCPConnection -LocalPort 8000, 9621

# Force kill if needed
Stop-Process -Id <PID> -Force
```

### Virtual Environment Not Found
```powershell
# Recreate backend venv
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# Recreate LightRAG venv
cd lightrag\Lightrag_main
uv sync --extra api
```

### LightRAG Embedding Dimension Mismatch
If you see "Embedding dim mismatch" error:
```powershell
cd lightrag\Lightrag_main
Remove-Item -Recurse -Force rag_storage
# Restart LightRAG server
```

### Check Service Status
```powershell
# Check if backend is running
curl http://localhost:8000/docs

# Check if LightRAG is running
curl http://localhost:9621/docs
```

## 📁 Directory Structure
```
backend/
├── start_all_services.ps1       # Start both services
├── stop_all_services.ps1        # Stop both services
├── requirements.txt             # Backend dependencies
├── venv/                        # Backend virtual environment
├── app/
│   ├── main.py                  # FastAPI application
│   ├── routers/
│   ├── services/
│   └── ...
└── lightrag/
    └── Lightrag_main/
        ├── .venv/               # LightRAG virtual environment
        ├── lightrag/            # LightRAG source
        ├── lightrag_webui/      # WebUI source
        └── rag_storage/         # LightRAG data storage
```

## 🔄 Development Workflow

### Daily Usage
```powershell
# Start everything
.\start_all_services.ps1

# Develop and test...

# Stop when done
.\stop_all_services.ps1
```

### Updating Dependencies

#### Backend
```powershell
.\venv\Scripts\Activate
pip install -r requirements.txt
```

#### LightRAG
```powershell
cd lightrag\Lightrag_main
.\.venv\Scripts\Activate
uv sync --extra api
```

## 🐳 Production Deployment Notes

### Render Deployment

For Render deployment, the shared `.env` approach is ideal:

1. **Create a Web Service** for your application
2. **Set Environment Variables** in Render Dashboard using the variables from `.env.example`
3. **Key Variables to Set**:
   ```
   MONGODB_URI=your_production_mongodb_uri
   JWT_SECRET=<generate with: openssl rand -hex 32>
   GEMINI_API_KEY=your_gemini_api_key
   LIGHTRAG_API_URL=http://localhost:9621
   LLM_BINDING=gemini
   EMBEDDING_BINDING=gemini
   PORT=9621
   HOST=0.0.0.0
   ```
4. **Build Command**: `cd backend && pip install -r requirements.txt && cd lightrag/Lightrag_main && uv sync --extra api`
5. **Start Command**: Create a startup script that runs both services

#### Render Startup Script Example
Create `start_render.sh` in `backend/`:
```bash
#!/bin/bash
# Start LightRAG in background
cd lightrag/Lightrag_main
.venv/bin/lightrag-server &
cd ../..

# Start Backend in foreground
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### General Production Considerations
1. Use a process manager like PM2 or Windows Service
2. Set up proper logging and log rotation
3. Use a reverse proxy (nginx/IIS) for SSL termination
4. Configure SSL/TLS certificates
5. Set up monitoring and health checks
6. Use production-grade databases (MongoDB Atlas, managed PostgreSQL)
7. Implement rate limiting and request throttling

## 📝 Notes

- Backend runs with `--reload` flag for development (auto-restart on code changes)
- LightRAG stores data in `rag_storage/` directory
- Both services use their own virtual environments
- Services can be accessed from other machines using your IP address instead of localhost

## 🆘 Support

If you encounter issues:
1. Check the terminal output for error messages
2. Verify all environment variables are set correctly
3. Ensure ports 8000 and 9621 are not blocked by firewall
4. Check that both virtual environments are properly set up
