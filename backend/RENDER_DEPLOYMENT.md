# Render Deployment Guide for Farm Vaidya

This guide explains how to deploy both the Backend API and LightRAG server together on Render.

## 📋 Prerequisites

1. A Render account (https://render.com)
2. Your code pushed to a GitHub repository
3. Required API keys and credentials ready

## 🚀 Deployment Steps

### 1. Create a New Web Service

1. Log in to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `farmvaidya-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`

### 2. Configure Build & Start Commands

#### Build Command
```bash
pip install -r requirements.txt && cd lightrag/Lightrag_main && pip install uv && uv sync --extra api && cd lightrag_webui && npm install -g bun && bun install --frozen-lockfile && bun run build && cd ../../..
```

#### Start Command
```bash
chmod +x start_render.sh && ./start_render.sh
```

**Alternative (using Python script):**
```bash
python start_services.py
```

### 3. Set Environment Variables

Go to **Environment** tab and add these variables:

#### Required Variables

##### Backend Configuration
```
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/farmvaidya
JWT_SECRET=<generate_with_openssl_rand_-hex_32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

##### Google OAuth (if used)
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

##### LightRAG Connection
```
LIGHTRAG_API_URL=http://localhost:9621
```

##### LightRAG Server Configuration
```
HOST=0.0.0.0
PORT=9621
WORKERS=1
TIMEOUT=300
LOG_LEVEL=INFO
```

##### Gemini API Configuration
```
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
EMBEDDING_MAX_TOKEN_SIZE=2048
```

##### RAG Configuration
```
ENABLE_LLM_CACHE=true
CHUNK_SIZE=1200
CHUNK_OVERLAP_SIZE=100
COSINE_THRESHOLD=0.2
TOP_K=40
```

#### Optional Variables

##### CORS Settings
```
CORS_ORIGINS=https://your-frontend-domain.com
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

##### WebUI Customization
```
WEBUI_TITLE=Farm Vaidya Knowledge Base
WEBUI_DESCRIPTION=Agricultural Knowledge Graph RAG System
```

### 4. Advanced Settings

#### Instance Type
- **Free Tier**: For testing (may be slow)
- **Starter ($7/month)**: Recommended for production
- **Standard+**: For high traffic

#### Auto-Deploy
- Enable auto-deploy from your main branch
- Render will rebuild on every git push

#### Health Check Path
Set to: `/docs` or create a custom health endpoint

### 5. Deploy!

Click **Create Web Service** and wait for deployment to complete.

## 🔍 Monitoring Deployment

### Check Logs
Go to **Logs** tab to see:
- Build progress
- LightRAG startup
- Backend startup
- Any errors

### Expected Log Output
```
Starting Farm Vaidya Services on Render
Setting up LightRAG environment...
Starting LightRAG Server on port 9621...
LightRAG started with PID: 1234
Starting Backend Server on port 10000...
INFO: Uvicorn running on http://0.0.0.0:10000
```

### Test Endpoints

Once deployed, test these URLs:
```
https://your-service.onrender.com/docs          # Backend API docs
https://your-service.onrender.com/health        # Health check (if implemented)
```

Note: LightRAG runs on internal port 9621 and is accessed by the backend via localhost.

## 🛠️ Troubleshooting

### Build Failures

#### "uv: command not found"
Add to build command: `pip install uv`

#### "bun: command not found"
Add to build command: `npm install -g bun`

#### Python version issues
Add `.python-version` file to your repo:
```
3.11
```

### Runtime Issues

#### Port binding errors
Ensure your start command uses `$PORT` environment variable:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### LightRAG not starting
Check logs for errors. Common issues:
- Missing GEMINI_API_KEY
- Incorrect embedding dimensions
- Insufficient memory (upgrade instance)

#### MongoDB connection failures
- Verify MONGODB_URI is correct
- Ensure MongoDB Atlas allows connections from Render IPs
- In MongoDB Atlas: Network Access → Add `0.0.0.0/0` (or Render's IP range)

#### Environment variables not loading
- Double-check spelling in Render dashboard
- Use exact names from .env.example
- Restart the service after adding variables

### Performance Issues

#### Slow responses
- Upgrade instance type
- Consider caching strategies
- Monitor LightRAG storage size

#### Out of memory
- Upgrade to larger instance
- Adjust RAG configuration:
  ```
  MAX_ENTITY_TOKENS=4000
  MAX_RELATION_TOKENS=6000
  TOP_K=30
  ```

## 📊 Scaling Considerations

### Horizontal Scaling
Render free/starter plans don't support multiple instances. For scaling:
1. Upgrade to Standard plan
2. Enable auto-scaling
3. Consider separating Backend and LightRAG into different services

### Separate Services Architecture

For better scalability, deploy as two services:

#### Service 1: LightRAG
- Root Directory: `backend/lightrag/Lightrag_main`
- Start Command: `source .venv/bin/activate && lightrag-server`
- Internal service (not publicly accessible)

#### Service 2: Backend
- Root Directory: `backend`
- Start Command: `source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Update `LIGHTRAG_API_URL` to LightRAG service's private URL

### Database Optimization

1. Use MongoDB Atlas M10+ for production
2. Enable indexes on frequently queried fields
3. Consider read replicas for heavy read workloads

## 🔒 Security Best Practices

1. **Never commit .env files** to your repository
2. **Rotate secrets regularly** (JWT_SECRET, API keys)
3. **Use strong passwords** for MongoDB
4. **Enable MongoDB Atlas IP whitelist** (or use VPC peering)
5. **Set up CORS properly** - don't use `*` in production
6. **Enable HTTPS** (Render provides this automatically)
7. **Consider API rate limiting** in your FastAPI app

## 💰 Cost Estimation

### Starter Deployment (~$7-10/month)
- Render Starter instance: $7/month
- MongoDB Atlas M0: Free
- Gemini API: Pay-per-use (~$2-3/month for moderate usage)

### Production Deployment (~$50-100/month)
- Render Standard instance: $25/month
- MongoDB Atlas M10: $57/month
- Gemini API: ~$10-20/month
- Additional Render service (if separated): $25/month

## 📝 Maintenance

### Updating Dependencies
Push changes to your repo, Render auto-deploys.

### Monitoring
Set up alerts in Render dashboard for:
- High CPU usage
- Memory issues
- Error rate spikes

### Backups
- MongoDB: Use Atlas automated backups
- LightRAG storage: Implement periodic backups of `rag_storage/` directory

## 🆘 Support & Resources

- **Render Docs**: https://render.com/docs
- **MongoDB Atlas**: https://docs.atlas.mongodb.com
- **LightRAG Docs**: https://github.com/HKUDS/LightRAG
- **FastAPI Docs**: https://fastapi.tiangolo.com

## 📞 Getting Help

If deployment fails:
1. Check Render logs for errors
2. Verify all environment variables are set
3. Test locally with `start_all_services.ps1` first
4. Check MongoDB Atlas network access settings
5. Verify API keys are valid
