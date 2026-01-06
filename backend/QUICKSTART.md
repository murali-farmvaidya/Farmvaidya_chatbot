# 🚀 Quick Start Guide - Single Command Deployment

## Local Development (Windows)

### Option 1: Python Script (Recommended ✅)
```powershell
cd backend
python start_services.py
```

### Option 2: PowerShell Script
```powershell
cd backend
.\start_all_services.ps1
```

## Render Deployment

### Setup Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add unified deployment"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Configure:
     - **Name**: farmvaidya-backend
     - **Region**: Oregon (US West) or closest
     - **Branch**: main
     - **Root Directory**: backend
     - **Runtime**: Python 3

3. **Build Command**
   ```bash
   pip install -r requirements.txt && cd lightrag/Lightrag_main && pip install uv && uv sync --extra api && cd ../..
   ```

4. **Start Command**
   ```bash
   python start_services.py
   ```

5. **Environment Variables** (Set in Render Dashboard)

   **Essential Variables:**
   ```
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/farmvaidya
   JWT_SECRET=<use: openssl rand -hex 32>
   GEMINI_API_KEY=your_gemini_api_key_here
   
   LLM_BINDING=gemini
   LLM_MODEL=gemini-2.0-flash-lite
   LLM_BINDING_HOST=https://generativelanguage.googleapis.com
   LLM_BINDING_API_KEY=your_gemini_api_key_here
   
   EMBEDDING_BINDING=gemini
   EMBEDDING_MODEL=gemini-embedding-001
   EMBEDDING_BINDING_HOST=https://generativelanguage.googleapis.com
   EMBEDDING_BINDING_API_KEY=your_gemini_api_key_here
   EMBEDDING_DIM=768
   
   HOST=0.0.0.0
   PORT=9621
   LIGHTRAG_API_URL=http://localhost:9621
   
   ENABLE_LLM_CACHE=true
   ```

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build and deployment

## 🎯 What Happens

### Local (Windows)
```
start_services.py
    ├── Checks virtual environments ✓
    ├── Copies .env file ✓
    ├── Starts LightRAG (port 9621) in new window
    └── Starts Backend (port 8000) in new window
```

### Render (Linux)
```
start_services.py
    ├── Checks virtual environments ✓
    ├── Uses Render environment variables ✓
    ├── Starts LightRAG (port 9621) in background
    └── Starts Backend (port $PORT) in foreground
```

## 🌐 Access Your Services

### Local
- Backend: http://localhost:8000/docs
- LightRAG: http://localhost:9621/docs

### Render
- Backend: https://your-service.onrender.com/docs
- LightRAG: Internal at localhost:9621 (accessed by backend)

## 🛑 Stopping Services

### Windows
- **Close the console windows**, or
- **Press Ctrl+C** in the windows, or
- Run: `.\stop_all_services.ps1`

### Linux/Render
- Services stop when Render stops the container

## ✅ Verification

After starting locally:
```powershell
# Check if services are running
curl http://localhost:8000/docs
curl http://localhost:9621/docs
```

After Render deployment:
```bash
# Check your Render service
curl https://your-service.onrender.com/docs
```

## 🐛 Troubleshooting

### "Virtual environment not found"
```powershell
# Backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# LightRAG
cd lightrag\Lightrag_main
uv sync --extra api
```

### "Port already in use"
```powershell
.\stop_all_services.ps1
# Or find and kill the process
Get-NetTCPConnection -LocalPort 8000, 9621
Stop-Process -Id <PID> -Force
```

### Render Build Fails
1. Check build logs in Render dashboard
2. Verify all environment variables are set
3. Ensure Python version matches (use `.python-version` file)

### Render Runtime Errors
1. Check logs in Render dashboard
2. Verify GEMINI_API_KEY is set
3. Verify MONGODB_URI is accessible from Render IPs
4. Check MongoDB Atlas Network Access settings

## 💡 Pro Tips

### For Local Development
- Use the Python script (`python start_services.py`) - it's cross-platform
- Keep both windows visible to monitor logs
- Backend has `--reload` enabled (auto-restarts on code changes)

### For Render Deployment
- Use Render's environment variables (don't commit `.env`)
- Enable auto-deploy from GitHub
- Monitor logs regularly
- Set up MongoDB Atlas IP whitelist: `0.0.0.0/0` (or Render's IP range)
- Use Starter plan ($7/month) minimum for production

## 📊 Cost Estimate

### Free Tier (Testing)
- Render: Free (spins down after 15 min inactivity)
- MongoDB: Free (M0)
- Gemini: Pay-per-use (~$1-2/month)
- **Total: ~$2/month**

### Production
- Render Starter: $7/month
- MongoDB M10: $57/month
- Gemini: ~$10-20/month
- **Total: ~$75-85/month**

## 🎉 Success!

Once deployed, you have:
- ✅ Single command to start everything
- ✅ Shared environment configuration
- ✅ Production-ready deployment on Render
- ✅ Both services running together
- ✅ No manual port management
- ✅ Automatic service monitoring

## 📚 Next Steps

1. ✅ Test locally: `python start_services.py`
2. ✅ Set up environment variables
3. ✅ Deploy to Render
4. ✅ Configure your frontend to use the Render URL
5. ✅ Set up MongoDB Atlas
6. ✅ Monitor logs and performance
