#!/usr/bin/env python3
"""Quick test script for greeting detection and responses"""

# Test greeting detection
print("=" * 60)
print("TESTING GREETING DETECTION")
print("=" * 60)

from app.services.chat_rules import is_greeting_or_acknowledgment

test_cases = [
    "hi",
    "hii",
    "hello",
    "good morning",
    "good afternoon",
    "good evening",
    "ok",
    "thanks",
    "noted",
    "How many patents does Biofactor have?",  # Should be False
    "What is the dosage for P-Factor?",  # Should be False
]

for test in test_cases:
    result = is_greeting_or_acknowledgment(test)
    print(f"{test:40} -> {result}")

print("\n" + "=" * 60)
print("TESTING GREETING RESPONSES")
print("=" * 60)

from app.services.chat_service import handle_greeting

greetings = [
    ("hi", "english"),
    ("hello", "english"),
    ("good morning", "english"),
    ("good afternoon", "english"),
    ("thanks", "english"),
    ("ok", "english"),
]

for greeting, lang in greetings:
    response = handle_greeting(greeting, lang)
    print(f"\nInput: {greeting}")
    print(f"Response: {response[:100]}...")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
