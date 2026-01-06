# ✅ Single Terminal Deployment - Fixed!

## What Changed

### Before ❌
- Two separate console windows opened
- Hard to monitor both services
- Not suitable for Render deployment

### After ✅
- **Single terminal** for both services
- Combined output with color-coded prefixes
- Works on Windows, Linux, and Render
- Matches your Node.js workflow

## How to Start

```powershell
cd backend
python start_services.py
```

## Expected Output

```
==================================================
  Starting Farm Vaidya Services
==================================================

[INFO] Copying shared .env file to LightRAG directory...
  ✓ .env file synchronized
[INFO] Starting LightRAG Server (port 9621)...
[SUCCESS] LightRAG server started (PID: 12345)
[INFO] Waiting for LightRAG to initialize...
[INFO] Starting Backend API Server (port 8000)...
[SUCCESS] Backend server started (PID: 12346)

==================================================
  Services Started Successfully!
==================================================

Backend API:     http://localhost:8000
Backend Docs:    http://localhost:8000/docs
LightRAG API:    http://localhost:9621
LightRAG WebUI:  http://localhost:9621/webui
LightRAG Docs:   http://localhost:9621/docs

[INFO] Press Ctrl+C to stop all services

[LightRAG] INFO: Uvicorn running on http://0.0.0.0:9621
[Backend] ✅ MongoDB connected successfully
[Backend] INFO: Uvicorn running on http://0.0.0.0:8000
[LightRAG] INFO: 127.0.0.1:xxxxx - "POST /query HTTP/1.1" 200 OK
[Backend] INFO: 127.0.0.1:xxxxx - "GET /docs HTTP/1.1" 200 OK
```

## Color-Coded Output

- 🔵 **[LightRAG]** - Cyan colored output from LightRAG server
- 🟢 **[Backend]** - Green colored output from Backend API
- ℹ️ **[INFO]** - General information messages
- ✅ **[SUCCESS]** - Success messages
- ⚠️ **[WARNING]** - Warning messages
- ❌ **[ERROR]** - Error messages

## MongoDB Fix

### Issue
Your MongoDB URI was incomplete:
```
MONGO_URI=mongodb+srv://...@cluster0.hgzl3np.mongodb.net/
                                                        ^^^ Missing database name
```

### Fixed
```
MONGO_URI=mongodb+srv://...@cluster0.hgzl3np.mongodb.net/farmvaidya_chat?retryWrites=true&w=majority
```

Now includes:
- Database name: `farmvaidya_chat`
- Connection options: `retryWrites=true&w=majority`
- Connection validation on startup

## Stopping Services

Press `Ctrl+C` in the terminal - both services will stop gracefully:

```
^C[WARNING] Shutting down services...
[SUCCESS] All services stopped
```

## For Render Deployment

This same script works on Render! Just use:

**Start Command:**
```bash
python start_services.py
```

Both services run in the same container, with output going to Render logs.

## Comparison to Your Node.js Example

### Your Node.js (convo-companion)
```bash
npm start
→ node start-all.js
→ Single terminal with combined output ✅
```

### Your Python (farmvaidya - NOW)
```bash
python start_services.py
→ Single terminal with combined output ✅
```

**Same behavior!** 🎉

## Architecture

```
┌─────────────────────────────────────────┐
│         Single Terminal Window          │
├─────────────────────────────────────────┤
│                                         │
│  start_services.py (Parent Process)    │
│          │                              │
│          ├──> LightRAG (Background)    │
│          │    Port 9621                │
│          │    Output: [LightRAG]       │
│          │                              │
│          └──> Backend (Foreground)     │
│               Port 8000                │
│               Output: [Backend]        │
│                                         │
│  Combined Output in Same Terminal      │
│                                         │
└─────────────────────────────────────────┘
```

## Verification

### 1. Check Both Services Running
```powershell
# You should see output from both:
[LightRAG] Server is ready...
[Backend] ✅ MongoDB connected...
```

### 2. Test Backend
```powershell
curl http://localhost:8000/docs
```

### 3. Test LightRAG
```powershell
curl http://localhost:9621/docs
```

### 4. Test Backend → LightRAG Communication
```powershell
curl -X POST http://localhost:8000/api/chat/send -H "Content-Type: application/json" -d "{\"user_message\":\"hello\"}"
```

## Troubleshooting

### "MongoDB connection failed"
**Solution**: Check your MongoDB URI in `.env` file
```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/farmvaidya_chat?retryWrites=true&w=majority
```

### "Port already in use"
**Solution**: Stop existing services
```powershell
# Windows
Get-NetTCPConnection -LocalPort 8000, 9621
Stop-Process -Id <PID> -Force

# Or use the stop script
.\stop_all_services.ps1
```

### "Process died unexpectedly"
**Solution**: Check the error messages in the terminal output
- Look for `[ERROR]` messages
- Check if ports are available
- Verify virtual environments exist

### Can't see output
**Solution**: The script now shows output from both services in the same terminal with prefixes

## Benefits

✅ **Single Terminal** - Just like your Node.js project  
✅ **Combined Output** - See everything in one place  
✅ **Color-Coded** - Easy to distinguish services  
✅ **Render Ready** - Works for deployment  
✅ **Graceful Shutdown** - Ctrl+C stops both cleanly  
✅ **MongoDB Validation** - Errors shown immediately  
✅ **Process Monitoring** - Auto-detect if services die  

## Files Modified

1. **start_services.py** - Single terminal mode with combined output
2. **app/db/mongo.py** - Added connection validation
3. **app/core/config.py** - Validate all required env vars
4. **.env** - Fixed MongoDB URI with database name

---

**Status**: ✅ Ready for local development and Render deployment!
