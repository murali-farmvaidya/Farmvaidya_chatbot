#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Complete flow test for Telugu query processing
"""

import sys
from app.utils.language_detector import detect_language
from app.services.chat_rules import (
    is_direct_knowledge_question,
    is_greeting_or_acknowledgment,
    is_dosage_question,
    is_factual_company_question
)
from app.services.lightrag_service import query_lightrag
from deep_translator import GoogleTranslator

# Test query
telugu_query = "బయో ఫ్యాక్టర్‌లో ఎరువుల వాడకం గురించి చెప్పండి"

print("="*70)
print("TELUGU QUERY FLOW TEST")
print("="*70)
print(f"\n1. Original Query: {telugu_query}")

# Step 1: Language Detection
detected_lang = detect_language(telugu_query)
print(f"\n2. Language Detected: {detected_lang}")

# Step 2: Query Classification
print(f"\n3. Query Classification:")
print(f"   - is_greeting_or_acknowledgment: {is_greeting_or_acknowledgment(telugu_query)}")
print(f"   - is_dosage_question: {is_dosage_question(telugu_query)}")
print(f"   - is_factual_company_question: {is_factual_company_question(telugu_query)}")
print(f"   - is_direct_knowledge_question: {is_direct_knowledge_question(telugu_query)}")

# Step 3: Translation to English
try:
    translator = GoogleTranslator(source='auto', target='en')
    english_query = translator.translate(telugu_query)
    print(f"\n4. Translated to English: {english_query}")
except Exception as e:
    print(f"\n4. Translation Error: {e}")
    english_query = telugu_query

# Step 4: LightRAG Query
print(f"\n5. Querying LightRAG...")
print(f"   Query being sent: {english_query}")

try:
    response = query_lightrag(telugu_query, [], language=detected_lang)
    print(f"\n6. LightRAG Response (first 500 chars):")
    print(f"   {response[:500]}")
    print(f"\n   Response length: {len(response)} characters")
    
    # Check for common failure indicators
    if "క్షమించండి" in response or "sorry" in response.lower():
        print("\n   ⚠️ WARNING: Response contains 'sorry' - no information found")
    if "[no-context]" in response:
        print("\n   ⚠️ WARNING: Response contains [no-context]")
        
except Exception as e:
    print(f"\n6. LightRAG Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
