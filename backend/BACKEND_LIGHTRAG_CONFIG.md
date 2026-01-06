# ✅ Backend Configuration Updated for Local LightRAG

## What Was Changed

### Before
Your backend was calling an **external Render URL**:
```python
# backend/app/core/config.py
LIGHTRAG_URL = "https://convo-chatbot.onrender.com/query"  # ❌ External service
```

### After
Now it uses the **local LightRAG instance** running in the same deployment:
```python
# backend/app/core/config.py
LIGHTRAG_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:9621/query")  # ✅ Local service
```

## Architecture Flow

### Previous Architecture (Separate Deployments)
```
Frontend
   ↓
Backend (Render) ──HTTP──> LightRAG (External Render Service)
   ↓                           ↓
MongoDB                   Vector Storage
```

### New Architecture (Unified Deployment) ✅
```
Frontend
   ↓
Backend (Port 8000) ──localhost──> LightRAG (Port 9621)
   ↓                                    ↓
MongoDB                           Vector Storage
```

**Same Process, Faster Communication!**

## Benefits of Local LightRAG

1. **⚡ Faster Response Times** - No network latency between services
2. **💰 Cost Savings** - No need for separate Render deployment
3. **🔒 More Secure** - Internal communication, not exposed externally
4. **🎯 Simpler Management** - Single deployment to maintain
5. **📦 Unified Configuration** - One `.env` file for everything

## Configuration

### Local Development (.env)
```env
LIGHTRAG_API_URL=http://localhost:9621/query
```

### Render Deployment (Environment Variables)
```env
LIGHTRAG_API_URL=http://localhost:9621/query
```

**Note**: Even on Render, use `localhost` since both services run in the same container!

## How Requests Flow

### 1. User Sends Message
```
User → Frontend → POST /api/chat/send → Backend
```

### 2. Backend Queries LightRAG
```python
# backend/app/services/chat_service.py
answer = query_lightrag(user_message, history, language=detected_language)
```

### 3. LightRAG Service Makes Request
```python
# backend/app/services/lightrag_service.py
res = requests.post(LIGHTRAG_URL, json=payload, timeout=60)
# LIGHTRAG_URL = "http://localhost:9621/query"
```

### 4. Local LightRAG Responds
```
LightRAG (localhost:9621) → Response → Backend → Frontend → User
```

## Verification

### Check Configuration
```python
# backend/app/core/config.py
from app.core.config import LIGHTRAG_URL
print(LIGHTRAG_URL)  # Should print: http://localhost:9621/query
```

### Test the Connection
```powershell
# Start both services
python start_services.py

# Test backend
curl http://localhost:8000/docs

# Test LightRAG directly
curl -X POST http://localhost:9621/query -H "Content-Type: application/json" -d "{\"query\":\"test\",\"mode\":\"mix\"}"

# Test through backend
curl -X POST http://localhost:8000/api/chat/send -H "Content-Type: application/json" -d "{\"user_message\":\"hello\"}"
```

## Files Modified

1. **[backend/app/core/config.py](../app/core/config.py)**
   - Changed hardcoded URL to environment variable
   - Uses `LIGHTRAG_API_URL` from `.env`
   - Defaults to `http://localhost:9621/query`

2. **[backend/.env](../.env)**
   - Updated `LIGHTRAG_URL` → `LIGHTRAG_API_URL`
   - Set to `http://localhost:9621/query`
   - Added `GEMINI_API_KEY` for consistency

## Important Notes

### ✅ What Works Now
- Backend queries local LightRAG instance
- No external API calls needed
- Faster response times
- Single deployment handles everything

### ⚠️ What to Remember
- Both services must be running together
- Use `python start_services.py` to start both
- LightRAG must start before backend (handled by script)
- Port 9621 is internal only (not exposed externally on Render)

### 🚀 For Render Deployment
Set these environment variables:
```
LIGHTRAG_API_URL=http://localhost:9621/query
GEMINI_API_KEY=your_api_key_here
MONGO_URI=your_mongodb_uri
JWT_SECRET=your_secret
```

Then use start command:
```bash
python start_services.py
```

## Troubleshooting

### "Connection refused to localhost:9621"
**Problem**: LightRAG is not running

**Solution**:
```powershell
# Check if LightRAG is running
curl http://localhost:9621/docs

# Restart services
python start_services.py
```

### "Backend still calling external URL"
**Problem**: Old config cached or not restarted

**Solution**:
```powershell
# Stop all services
.\stop_all_services.ps1

# Clear Python cache
Remove-Item -Recurse -Force backend\app\__pycache__
Remove-Item -Recurse -Force backend\app\*\__pycache__

# Restart
python start_services.py
```

### "LightRAG responds but backend doesn't get it"
**Problem**: Network/firewall blocking localhost

**Solution**:
- Check Windows Firewall settings
- Ensure ports 8000 and 9621 are allowed
- Try using `127.0.0.1:9621` instead of `localhost:9621`

## Summary

✅ **Backend now uses local LightRAG** (`http://localhost:9621/query`)  
✅ **Configuration is environment-based** (`.env` file)  
✅ **Works for both local development and Render deployment**  
✅ **No more external API dependencies**  
✅ **Faster, cheaper, simpler!**

---

**Last Updated**: January 6, 2026  
**Status**: ✅ Configured and Ready
