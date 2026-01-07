import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DB_NAME = "farmvaidya_chat"

# LightRAG URL - now running locally in the same deployment
LIGHTRAG_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:9621/query")

# Validate required environment variables
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in .env")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET not set in .env")
if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID not set in .env")
