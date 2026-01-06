# Farm Vaidya Backend - Unified Deployment

Complete backend system with FastAPI and LightRAG knowledge graph running together.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Farm Vaidya Backend                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────┐    ┌─────────────────┐  │
│  │  FastAPI Backend │◄───┤ Shared .env     │  │
│  │  (Port 8000)     │    │ Configuration   │  │
│  └────────┬─────────┘    └─────────────────┘  │
│           │                      ▲              │
│           │ HTTP Requests        │              │
│           ▼                      │              │
│  ┌──────────────────┐           │              │
│  │  LightRAG Server │───────────┘              │
│  │  (Port 9621)     │                          │
│  └──────────────────┘                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
# Clone repository (if not already done)
git clone <your-repo-url>
cd farmvaidya-conversational-ai/backend

# Create .env from template
cp .env.example .env

# Edit .env with your credentials
notepad .env
```

### 2. Setup Virtual Environments

#### Backend
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

#### LightRAG
```powershell
cd lightrag\Lightrag_main

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"

# Sync dependencies
uv sync --extra api

# Install Bun and build WebUI
powershell -c "irm https://bun.sh/install.ps1 | iex"
$env:Path = "$env:USERPROFILE\.bun\bin;$env:Path"
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..\..\..\..
```

### 3. Start Services

**Single Command - Both services in one terminal:**
```powershell
# From backend/ directory
python start_services.py
```

You'll see combined output from both services:
```
[LightRAG] INFO: Uvicorn running on http://0.0.0.0:9621
[Backend] ✅ MongoDB connected successfully
[Backend] INFO: Uvicorn running on http://0.0.0.0:8000
```

**Alternative options:**
```powershell
# PowerShell (opens separate windows)
.\start_all_services.ps1

# Linux/Render
chmod +x start_render.sh
./start_render.sh
```

Access points:
- **Backend API**: http://localhost:8000/docs
- **LightRAG**: http://localhost:9621/docs

### 4. Stop Services

```powershell
.\stop_all_services.ps1
```

## 📁 Files Overview

### Configuration Files
- **`.env`** - Your actual environment variables (gitignored)
- **`.env.example`** - Template with all available variables
- **`requirements.txt`** - Backend Python dependencies

### Deployment Scripts
- **`start_services.py`** - Universal Python script (Windows/Linux/Render)
- **`start_all_services.ps1`** - Windows: Start both services
- **`stop_all_services.ps1`** - Windows: Stop both services
- **`start_render.sh`** - Linux: Start both services (for Render)

### Documentation
- **`README.md`** - This file (overview)
- **`SHARED_ENV_SETUP.md`** - Environment configuration explained
- **`DEPLOYMENT_GUIDE.md`** - Local development setup
- **`RENDER_DEPLOYMENT.md`** - Production deployment on Render

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory. Both services will use it!

### Required Variables

```env
# Backend
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/farmvaidya_chat?retryWrites=true&w=majority
JWT_SECRET=your_super_secret_jwt_key_change_this
LIGHTRAG_API_URL=http://localhost:9621

# LightRAG & Gemini
GEMINI_API_KEY=your_gemini_api_key_here
LLM_BINDING=gemini
LLM_MODEL=gemini-2.0-flash-lite
EMBEDDING_BINDING=gemini
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=768
```

See [.env.example](.env.example) for all available options.

## 🌐 API Endpoints

### Backend (Port 8000)

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI documentation |
| `/api/auth/login` | User authentication |
| `/api/chat/send` | Send chat message |
| `/api/sessions` | Manage chat sessions |

### LightRAG (Port 9621)

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI documentation |
| `/webui` | Web UI for knowledge graph |
| `/query` | Query knowledge graph |
| `/insert` | Insert documents |

## 📊 Directory Structure

```
backend/
├── .env                          # Shared configuration (gitignored)
├── .env.example                  # Configuration template
├── requirements.txt              # Python dependencies
├── start_all_services.ps1        # Start script (Windows)
├── stop_all_services.ps1         # Stop script (Windows)
├── start_render.sh               # Start script (Linux/Render)
├── README.md                     # This file
├── SHARED_ENV_SETUP.md          # Environment setup guide
├── DEPLOYMENT_GUIDE.md          # Local deployment guide
├── RENDER_DEPLOYMENT.md         # Production deployment guide
├── venv/                        # Backend virtual environment
├── app/                         # Backend source code
│   ├── main.py                  # FastAPI application
│   ├── routers/                 # API routes
│   ├── services/                # Business logic
│   ├── models/                  # Data models
│   └── ...
└── lightrag/
    └── Lightrag_main/
        ├── .env                 # Copied from backend/.env
        ├── .venv/               # LightRAG virtual environment
        ├── lightrag/            # LightRAG source
        ├── rag_storage/         # Knowledge graph storage
        └── inputs/              # Document input directory
```

## 🐳 Deployment Options

### Local Development (Windows)
```powershell
# Option 1: Python script (recommended)
python start_services.py

# Option 2: PowerShell script
.\start_all_services.ps1
```

### Production (Render)
See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete guide.

Quick steps:
1. Push code to GitHub
2. Create Web Service on Render
3. Set environment variables in dashboard
4. Deploy!

## 🔍 Troubleshooting

### Port Already in Use
```powershell
.\stop_all_services.ps1
# Or manually:
Get-NetTCPConnection -LocalPort 8000, 9621
Stop-Process -Id <PID> -Force
```

### Virtual Environment Issues
```powershell
# Recreate backend venv
Remove-Item -Recurse venv
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# Recreate LightRAG venv
cd lightrag\Lightrag_main
Remove-Item -Recurse .venv
uv sync --extra api
```

### Environment Variables Not Loading
- Ensure `.env` exists in `backend/` directory
- Check `.env` file syntax (no spaces around `=`)
- Restart services after changing `.env`

### LightRAG Embedding Mismatch
```powershell
cd lightrag\Lightrag_main
Remove-Item -Recurse -Force rag_storage
# Restart LightRAG server
```

## 📚 Additional Resources

- **Backend Framework**: [FastAPI Documentation](https://fastapi.tiangolo.com)
- **LightRAG**: [GitHub Repository](https://github.com/HKUDS/LightRAG)
- **Gemini API**: [Google AI Studio](https://ai.google.dev)
- **MongoDB Atlas**: [Documentation](https://docs.atlas.mongodb.com)
- **Render**: [Deployment Docs](https://render.com/docs)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test locally with `start_all_services.ps1`
4. Submit a pull request

## 📝 License

[Your License Here]

## 🆘 Support

For issues or questions:
1. Check documentation files in this directory
2. Review error logs in terminal windows
3. Verify `.env` configuration
4. Check MongoDB and Gemini API connectivity

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Production Ready ✅
