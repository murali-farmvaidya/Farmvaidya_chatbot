# Shared Environment Configuration Summary

## ✅ What Changed

Your setup now uses a **single shared `.env` file** for both Backend and LightRAG services!

### Before
```
backend/
├── .env                    # Backend variables only
└── lightrag/
    └── Lightrag_main/
        └── .env            # LightRAG variables only (separate file)
```

### After
```
backend/
├── .env                    # All variables for BOTH services
├── .env.example            # Template with all variables
└── lightrag/
    └── Lightrag_main/
        └── .env            # Auto-copied from backend/.env
```

## 🎯 Benefits

1. **Single Source of Truth**: Manage all environment variables in one place
2. **Render-Ready**: Perfect for Render deployment where you set env vars once
3. **No Duplication**: Same API keys shared between services
4. **Easy Updates**: Change variables in one place, both services get updated
5. **Version Control**: Only track `.env.example`, never commit actual secrets

## 📝 How It Works

### Local Development

When you run `start_all_services.ps1`:
1. Script checks for `backend/.env`
2. Automatically copies it to `backend/lightrag/Lightrag_main/.env`
3. Starts both services with synchronized configuration

### Render Deployment

When deploying on Render:
1. Set environment variables once in Render Dashboard
2. Render automatically makes them available to both services
3. Both services read from the same environment variables

## 🔑 Key Environment Variables

### Shared Between Both Services
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Backend Specific
```env
MONGODB_URI=your_mongodb_uri
JWT_SECRET=your_jwt_secret
LIGHTRAG_API_URL=http://localhost:9621
```

### LightRAG Specific
```env
LLM_BINDING=gemini
LLM_MODEL=gemini-2.0-flash-lite
EMBEDDING_BINDING=gemini
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=768
```

## 📋 Setup Checklist

### First Time Setup

1. **Copy the template**
   ```powershell
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` with your values**
   - Add your MongoDB URI
   - Add your Gemini API key
   - Add your JWT secret
   - Configure other settings

3. **Start services**
   ```powershell
   .\start_all_services.ps1
   ```

### Render Deployment

1. **Push code to GitHub** (`.env` is gitignored)

2. **Set environment variables in Render Dashboard**
   - Copy from your local `.env` file
   - Or use variables from `.env.example`

3. **Deploy**
   - Render will make env vars available to both services
   - No need to manage separate configuration files

## 🔒 Security Notes

- ✅ `.env` is in `.gitignore` - never committed
- ✅ `.env.example` is tracked - serves as documentation
- ✅ Secrets are only in environment variables
- ✅ Same API keys can be shared (efficient, no duplication)

## 🚀 Quick Commands

```powershell
# Local Development
cd backend
.\start_all_services.ps1          # Start both services
.\stop_all_services.ps1           # Stop both services

# Environment Management
cp .env.example .env              # Create config from template
notepad .env                      # Edit configuration
```

## 📖 Documentation Files

- **[.env.example](./env.example)** - Template with all variables and comments
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Local development setup
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - Complete Render deployment guide

## ❓ FAQ

**Q: Do I need to set GEMINI_API_KEY twice?**  
A: No! Set it once in `backend/.env` and it's used by both services.

**Q: What if I change .env while services are running?**  
A: Restart services with `stop_all_services.ps1` then `start_all_services.ps1`

**Q: Can I still use separate .env files?**  
A: Yes, but not recommended. The startup script copies from `backend/.env` anyway.

**Q: Does this work on Linux/Mac?**  
A: Yes! Use `start_render.sh` for Unix-based systems.

**Q: What about production secrets?**  
A: Never commit `.env` to git. Use Render's environment variables dashboard or secrets management.

## ✅ Verification

To verify your setup is correct:

```powershell
# 1. Check .env exists
Test-Path backend\.env

# 2. Check it has required variables
Select-String -Path backend\.env -Pattern "GEMINI_API_KEY|MONGODB_URI|JWT_SECRET"

# 3. Start services and check logs
.\start_all_services.ps1

# 4. Test endpoints
curl http://localhost:8000/docs     # Backend
curl http://localhost:9621/docs     # LightRAG
```

## 🎉 Result

You now have a **unified deployment** where:
- ✅ Both services share configuration
- ✅ Perfect for Render deployment
- ✅ Easy to maintain and update
- ✅ No duplicate API keys or secrets
- ✅ Single source of truth for all settings
