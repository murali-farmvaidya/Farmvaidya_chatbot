# Deployment Guide: Diagnosis Follow-Up Fix

## What Was Changed

Two files have been modified to implement context-aware follow-up logic:

1. **app/services/followup_service.py**
   - Added `is_diagnosis` parameter to `generate_followup()` function
   - Implemented diagnosis-specific follow-up logic (lines 145-164)
   - Separated diagnosis flow from product recommendation flow

2. **app/services/chat_service.py**
   - Updated `generate_followup()` call to pass `is_diagnosis` flag (line 555)
   - Automatically detects question type and routes to appropriate follow-up strategy

## Deployment Steps

### 1. Backup Current Files (RECOMMENDED)
```powershell
# In PowerShell, from the backend directory:
cp app/services/followup_service.py app/services/followup_service.py.backup
cp app/services/chat_service.py app/services/chat_service.py.backup
```

### 2. Deploy Updated Files
The files are already in place. No additional files need to be deployed.

### 3. Syntax Validation (RUN BEFORE DEPLOYING)
```powershell
cd backend
python -m py_compile app/services/followup_service.py app/services/chat_service.py
```

✅ **Expected output:** No errors (silent success)

### 4. Restart Backend Service
```powershell
# If using the start_backend.ps1 script:
.\start_backend.ps1

# Or if running directly:
python app/main.py
```

### 5. Test the Changes
```powershell
# Test diagnosis question (should ask ONLY for crop, if needed)
python test_chat.py "My paddy leaves are turning yellow"

# Test product question (should ask full context)
python test_chat.py "What's the best fertilizer for my crop"
```

## Verification Checklist

- [ ] Files are modified (check git diff):
  ```powershell
  git diff app/services/followup_service.py
  git diff app/services/chat_service.py
  ```

- [ ] Syntax is valid:
  ```powershell
  python -m py_compile app/services/followup_service.py app/services/chat_service.py
  ```

- [ ] Backend starts without errors:
  ```powershell
  python app/main.py
  ```

- [ ] Test diagnosis question flows correctly
- [ ] Test product recommendation flows correctly
- [ ] Test multi-language support (Telugu, Hindi, etc.)

## Rollback Plan (If Needed)

If you need to revert the changes:

```powershell
# Restore from backup
cp app/services/followup_service.py.backup app/services/followup_service.py
cp app/services/chat_service.py.backup app/services/chat_service.py

# Restart backend
.\start_backend.ps1
```

## Expected Behavior After Deployment

### Diagnosis Questions (e.g., "leaves are yellow")
```
✅ FAST: Only 1 follow-up question max (asking for crop if needed)
✅ DETAILED: 7-10 sentence response with all diagnostic sections
✅ ACTIONABLE: Specific products, doses, timing, prevention
❌ NO: Asking about soil/irrigation/fertilizers
```

### Product Questions (e.g., "best fertilizer")
```
✅ UNCHANGED: Full context gathering (crop, stage, soil, irrigation, fertilizers)
✅ DETAILED: Comprehensive recommendations based on context
```

## Monitoring After Deployment

### Check Logs for Success Indicators
```
✅ "DIAGNOSIS MODE: All necessary information collected"
✅ "PRODUCT MODE: All essential information collected"
✅ "GENERATING FOLLOW-UP QUESTION"
✅ "GENERATING FINAL ANSWER WITH COLLECTED CONTEXT"
```

### Watch for Issues
```
❌ "DIAGNOSIS MODE" but still asking for soil/irrigation (bug)
❌ Product questions not asking enough follow-ups (bug)
❌ Short responses (1-2 lines) instead of comprehensive (symptom of LightRAG issue)
```

## Performance Impact

**Expected:**
- ✅ Faster diagnosis question resolution (fewer follow-ups)
- ✅ Same product recommendation quality
- ✅ Better user satisfaction
- ✅ No performance degradation

**Monitor:**
- Response time from user input to final answer
- Database query count (should be lower for diagnosis questions)
- User feedback on response quality

## Database Compatibility

No database schema changes required. Existing data will work with updated code.

## API Compatibility

No API changes. External integrations continue to work unchanged.

## Compatibility with Existing Features

- ✅ Multi-language support (all 10 languages) - WORKING
- ✅ LightRAG integration - UNCHANGED
- ✅ Local knowledge base fallback - UNCHANGED
- ✅ Session management - UNCHANGED
- ✅ Message history - UNCHANGED

## Contact Support If

1. **Diagnosis questions still ask for soil/irrigation**
   - Check: `is_problem_diagnosis_question()` in chat_rules.py
   - Verify: Question type detection is working correctly

2. **Responses are still 1-2 lines**
   - Check: LightRAG is returning full responses
   - Verify: `comprehensive_query` prompt is complete (lines 634-652 in chat_service.py)
   - Check: `clean_response()` in utils/cleaner.py is not truncating

3. **Product questions not getting enough context**
   - Verify: `is_diagnosis=False` is passed for product questions
   - Check: `is_problem_diagnosis_question()` returns False for the question type

## Version Information

- **Date Deployed:** [Today's Date]
- **Files Modified:** 2
  - app/services/followup_service.py
  - app/services/chat_service.py
- **Lines Changed:** ~30 lines
- **Breaking Changes:** None
- **Rollback Required:** Only if behavior doesn't meet expectations

## Success Metrics

After deployment, the system should show:

1. **Faster Diagnosis Resolution**
   - Diagnosis question: 1 follow-up (max)
   - Product question: 5 follow-ups (as before)

2. **Better Response Quality**
   - Diagnosis response: 7-10 sentences (was 2)
   - Product response: Unchanged quality

3. **Higher User Satisfaction**
   - Farmers get quick answers to problems
   - Farmers get detailed recommendations for products

## Technical Support

If you encounter issues:

1. Check syntax: `python -m py_compile app/services/followup_service.py app/services/chat_service.py`
2. Check logs for error messages
3. Review the DIAGNOSIS_FIX_QUICK_REFERENCE.md for troubleshooting
4. Compare with BEFORE_AFTER_COMPARISON.md to understand expected behavior
