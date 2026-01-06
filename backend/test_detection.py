#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.services.chat_rules import is_direct_knowledge_question

# Test Telugu query
telugu_query = "బయో ఫ్యాక్టర్‌లో ఎరువుల వాడకం గురించి చెప్పండి"

print(f"Testing query: {telugu_query}")
print(f"Lower: {telugu_query.lower()}")
print()

# Check keywords
keywords = ['గురించి', 'చెప్పండి', 'ఎరువుల', 'వాడకం']
print("Keyword matches:")
for k in keywords:
    print(f"  '{k}' in text: {k in telugu_query}")
    print(f"  '{k}' in lower: {k in telugu_query.lower()}")

print()

# Check products
products = ['బయోఫ్యాక్టర్', 'బయో ఫ్యాక్టర్', 'biofactor']
print("Product matches:")
for p in products:
    print(f"  '{p}' in text: {p in telugu_query}")
    print(f"  '{p}' in lower: {p in telugu_query.lower()}")

print()

# Test detection
result = is_direct_knowledge_question(telugu_query)
print(f"is_direct_knowledge_question result: {result}")

# Also test English version
english_query = "tell me about fertilizers usage in bio factor"
english_result = is_direct_knowledge_question(english_query)
print(f"\nEnglish query detection: {english_result}")
