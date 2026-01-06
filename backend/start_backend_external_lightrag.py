"""
Simple backend starter - using external LightRAG
"""
import subprocess
import sys
import os

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("\n" + "="*50)
print("  Starting Backend with External LightRAG")
print("="*50)
print(f"\nLightRAG URL: https://convo-chatbot.onrender.com/query")
print(f"Backend will run on: http://localhost:8000\n")

# Start uvicorn
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000"
])
