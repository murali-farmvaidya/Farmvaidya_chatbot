"""
Quick diagnostic script to check if services are running
"""
import requests
import time

print("=" * 50)
print("  Service Health Check")
print("=" * 50)
print()

# Check Backend
print("[1/3] Checking Backend (port 8000)...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"  ✓ Backend: {response.json()}")
except Exception as e:
    print(f"  ✗ Backend ERROR: {e}")

print()

# Check LightRAG
print("[2/3] Checking LightRAG (port 9621)...")
try:
    response = requests.get("http://localhost:9621/docs", timeout=5)
    if response.status_code == 200:
        print(f"  ✓ LightRAG: Running (status {response.status_code})")
    else:
        print(f"  ✗ LightRAG: Error (status {response.status_code})")
except Exception as e:
    print(f"  ✗ LightRAG ERROR: {e}")

print()

# Test LightRAG query
print("[3/3] Testing LightRAG Query...")
try:
    payload = {
        "query": "test",
        "mode": "mix",
        "conversation_history": [],
        "response_type": "Multiple Paragraphs"
    }
    response = requests.post(
        "http://localhost:9621/query",
        json=payload,
        timeout=10
    )
    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ LightRAG Query: Success")
        print(f"    Response: {result.get('response', 'N/A')[:100]}...")
    else:
        print(f"  ✗ LightRAG Query: Error (status {response.status_code})")
        print(f"    {response.text[:200]}")
except Exception as e:
    print(f"  ✗ LightRAG Query ERROR: {e}")

print()
print("=" * 50)
print("  Check Complete")
print("=" * 50)
