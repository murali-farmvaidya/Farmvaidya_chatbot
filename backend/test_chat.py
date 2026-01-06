"""
Quick test of chat endpoint
"""
import requests
import json

# Test data
url = "http://localhost:8000/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test_token_123"  # You'll need a real token from login
}
payload = {
    "session_id": "test-session-123",
    "message": "Hello, what crops can I grow?"
}

print("Testing chat endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")
