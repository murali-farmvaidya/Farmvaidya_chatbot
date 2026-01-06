"""Test if translation is working"""
from app.services.lightrag_service import query_lightrag

# Test Telugu query
telugu_query = "నాకు బయో ఫ్యాక్టర్లో వాడే ఎరువుల గురించి చెప్పండి"

print(f"Testing query: {telugu_query}")
print("\nCalling query_lightrag with language='telugu'...\n")

try:
    response = query_lightrag(telugu_query, [], language="telugu", factual=True)
    print(f"\nResponse: {response}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
