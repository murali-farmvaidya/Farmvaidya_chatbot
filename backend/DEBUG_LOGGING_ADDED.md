# Debug Logging Added for Language Issues

## Issue Reported
1. **Language Persistence Problem**:
   - "what is k factor" (English) → Got English response ✓
   - "what is its dosage" (English) → Got Telugu response ✗ (should be English)
   - "Benefits of Bio NPK" (English) → Got Telugu response ✗ AND wrong content (K-Factor info)

2. **Content Contamination**:
   - "Benefits of Bio NPK" is giving K-Factor information instead of Bio NPK information
   - LightRAG WebUI directly gives correct answer about Bio NPK
   - But chatbot is mixing in K-Factor context

## Changes Made

### 1. Enhanced Logging in `chat_service.py`

Added detailed logging to trace language flow:

**For Direct Knowledge Questions (lines ~177):**
```python
print(f"🌐 Using detected language for KNOWLEDGE: {detected_language}")
print(f"🔍 Original question: {user_message}")
print(f"🔗 Is follow-up? {is_followup}")
```

**For Dosage Questions (lines ~207):**
```python
print(f"🌐 Using detected language for DOSAGE: {detected_language}")
print(f"🔍 Original question: {user_message}")
print(f"🔗 Is follow-up? {is_followup}")
```

### 2. Enhanced Logging in `lightrag_service.py`

Added comprehensive logging for the entire translation pipeline:

```python
print(f"🎯 query_lightrag called with:")
print(f"   📝 query: {query[:100]}...")
print(f"   📚 history length: {len(history)} messages")
print(f"   🔧 mode: {mode}")
print(f"   🌍 language: {language}")
print(f"   ℹ️ factual: {factual}")
```

Plus logging for:
- Domain term translation (Telugu ↔ English product names)
- Query translation to English
- LightRAG response
- Response translation back to target language

## How to Test

### Test Case 1: Language Consistency
```
1. Start new session
2. Send: "what is k factor"
   Expected: English response
   
3. Send: "what is its dosage"
   Expected: English response (NOT Telugu)
   
4. Send: "Benefits of Bio NPK"
   Expected: English response about Bio NPK (NOT K-Factor)
```

### What to Look For in Logs

**Step 1**: "what is k factor"
```
🌍 Detected language: english
✅ DIRECT KNOWLEDGE QUESTION
🌐 Using detected language for KNOWLEDGE: english
🔍 Original question: what is k factor
🔗 Is follow-up? False
📝 Direct question, no history
🎯 query_lightrag called with:
   🌍 language: english
✅ Query language is English, no translation needed
📥 LightRAG response (first 150 chars): K-Factor is...
✅ Language is English, returning response without translation
```

**Step 2**: "what is its dosage"
```
🌍 Detected language: english ← Should be 'english'
✅ DOSAGE BRANCH RETURNING LIGHTRAG ANSWER
🌐 Using detected language for DOSAGE: english ← Should be 'english'
🔍 Original question: what is its dosage
🔗 Is follow-up? True ← Should be True (correct)
🎯 query_lightrag called with:
   🌍 language: english ← Should be 'english'
✅ Query language is English, no translation needed ← Should NOT translate
📥 LightRAG response: ...
✅ Language is English, returning response without translation ← Should NOT translate
```

**Step 3**: "Benefits of Bio NPK"
```
🌍 Detected language: english ← Should be 'english'
✅ DIRECT KNOWLEDGE QUESTION
🌐 Using detected language for KNOWLEDGE: english ← Should be 'english'
🔍 Original question: Benefits of Bio NPK
🔗 Is follow-up? False ← Should be False (11 words > 7 word limit)
📝 Direct question, no history ← Should use empty history []
🎯 query_lightrag called with:
   📝 query: Benefits of Bio NPK
   📚 history length: 0 ← Should be 0 (no history)
   🌍 language: english
✅ Query language is English, no translation needed
📥 LightRAG response: Bio NPK... ← Should mention Bio NPK, NOT K-Factor
✅ Language is English, returning response without translation
```

## Potential Issues to Identify

### Issue 1: Language Detection
If logs show `🌍 Detected language: telugu` for "what is its dosage", then:
- Problem: `detect_language()` is incorrectly detecting language
- Solution: Review language detection logic in `language_detector.py`

### Issue 2: Translation Being Applied
If logs show:
```
🔄 Response language is telugu, translating from English...
✅ Response translated from English to telugu
```
Then:
- Problem: `language` parameter is being set to "telugu" somewhere
- Solution: Trace back to see where `detected_language` is being overridden

### Issue 3: History Contamination
If logs show for "Benefits of Bio NPK":
```
📚 history length: 4 messages ← Should be 0!
```
Or if response contains K-Factor info, then:
- Problem: Follow-up detection is incorrectly returning True
- Solution: Review `is_followup_reference()` in `chat_rules.py`

### Issue 4: LightRAG Response
If LightRAG itself returns K-Factor info for "Benefits of Bio NPK":
```
📥 LightRAG response: K-Factor is... ← Wrong!
```
Then:
- Problem: LightRAG's knowledge base or mode selection
- Solution: Try different mode (naive, local, global) or check if history is contaminating

## Next Steps

1. **Restart backend** to apply logging changes:
   ```powershell
   .\restart_clean.ps1
   ```

2. **Test the 3 questions** in order and capture full logs

3. **Analyze logs** to identify which of the 4 potential issues is occurring

4. **Fix identified issue** based on the specific problem found

## Expected Fix

Based on current code review, the issue is most likely one of:

1. **GoogleTranslator state persistence** - Translator might be caching previous language
2. **History bleeding** - Follow-up detection or history might be contaminating
3. **LightRAG mode** - Using "mix" mode might be causing entity confusion

Once we see the logs, we'll know exactly which issue to fix.
