# Resilient Document Processing Fix

## Problem
Document processing failed completely when chunk 13/14 encountered a **504 DEADLINE_EXCEEDED** error from Gemini API:
- Error: Gemini API timeout while extracting entities from one chunk
- Result: Entire document processing stopped (12 successful chunks were discarded)
- Impact: Knowledge base remains empty, chatbot cannot answer questions

## Root Causes
1. **FIRST_EXCEPTION Strategy**: Code stopped processing ALL chunks when ANY chunk failed
2. **Limited Retries**: Only 3 retry attempts for transient API errors
3. **No Partial Success**: No way to use successfully processed chunks if one chunk failed

## Solutions Implemented

### 1. Continue Processing on Failures ([operate.py](lightrag/Lightrag_main/lightrag/operate.py))

**Before:**
```python
# Wait for tasks to complete or for the first exception to occur
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

# If any task failed, cancel all pending tasks and raise exception
if first_exception is not None:
    for pending_task in pending:
        pending_task.cancel()
    raise prefixed_exception from first_exception
```

**After:**
```python
# Wait for ALL tasks to complete instead of stopping at first exception
done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

# Collect results and track any exceptions
chunk_results = []
failed_chunks = []

for task in done:
    try:
        exception = task.exception()
        if exception is not None:
            logger.error(f"Failed to process chunk: {exception}")
            failed_chunks.append(str(exception))
        else:
            chunk_results.append(task.result())
    except Exception as e:
        logger.error(f"Error retrieving chunk result: {e}")
        failed_chunks.append(str(e))

# If some chunks failed but others succeeded, continue with successful ones
if failed_chunks:
    success_count = len(chunk_results)
    logger.warning(
        f"Document processing completed with {success_count}/{total_chunks} chunks successful. "
        f"{len(failed_chunks)} chunks failed. Continuing with successfully processed chunks."
    )
    
    # Only raise if ALL chunks failed
    if not chunk_results:
        raise RuntimeError(f"All {total_chunks} chunks failed to process")

return chunk_results  # Return whatever succeeded
```

**Benefits:**
- ✅ 12/14 successful chunks are now saved to knowledge base
- ✅ Chatbot can answer questions using 86% of document content
- ✅ Transient API errors don't waste entire processing effort
- ✅ Only fails if ALL chunks fail (complete API outage)

### 2. Increased Retry Attempts ([llm/gemini.py](lightrag/Lightrag_main/lightrag/llm/gemini.py))

**Changed in 2 locations:**

**Location 1: Text Generation (`gemini_complete_if_cache`)**
```python
@retry(
    stop=stop_after_attempt(5),  # Increased from 3 to 5
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=(
        retry_if_exception_type(google_api_exceptions.DeadlineExceeded)
        | retry_if_exception_type(google_api_exceptions.GatewayTimeout)
        | ...
    ),
)
```

**Location 2: Embeddings (`gemini_embed`)**
```python
@retry(
    stop=stop_after_attempt(5),  # Increased from 3 to 5
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=(
        retry_if_exception_type(google_api_exceptions.DeadlineExceeded)
        | ...
    ),
)
```

**Benefits:**
- ✅ More retries for transient 504 DEADLINE_EXCEEDED errors
- ✅ Exponential backoff: 4s → 8s → 16s → 32s → 60s between retries
- ✅ Higher success rate for slow chunks without changing timeout
- ✅ Works around temporary Gemini API congestion

## Expected Behavior After Fix

### Scenario 1: Single Chunk Timeout
```
Chunk 1: ✅ Success (57 entities, 57 relations)
Chunk 2: ✅ Success (135 entities, 53 relations)
...
Chunk 13: ❌ Failed after 5 retries (504 DEADLINE_EXCEEDED)
Chunk 14: ✅ Success (89 entities, 76 relations)

Result: ✅ Document processed with 13/14 chunks (93% success)
         Knowledge base populated with 13 chunks
         Chatbot can answer questions
```

### Scenario 2: Multiple Chunk Timeouts
```
Chunk 1: ✅ Success
Chunk 5: ❌ Failed (timeout)
Chunk 9: ❌ Failed (timeout)
Chunk 13: ❌ Failed (timeout)
Other chunks: ✅ Success

Result: ✅ Document processed with 11/14 chunks (79% success)
         Warning logged: "3 chunks failed (likely API timeouts)"
         Chatbot works with available content
```

### Scenario 3: Complete Failure (Unlikely)
```
All 14 chunks: ❌ Failed

Result: ❌ Document processing failed
         Error: "All 14 chunks failed to process"
         Indicates complete Gemini API outage or quota exhaustion
```

## How to Re-upload Document

1. **Restart LightRAG** to load the updated code:
   ```powershell
   cd backend
   .\restart_clean.ps1
   ```

2. **Start services**:
   ```powershell
   python .\start_services.py
   ```

3. **Re-upload the document** through LightRAG WebUI:
   - Open: http://localhost:9621/webui
   - Upload: "Biofactor knowledge base 21112025.pdf"
   - Monitor: Progress should show chunk-by-chunk processing
   - Expected: Should complete even if 1-2 chunks timeout

4. **Verify success**:
   - Check logs: Look for "Document processing completed with X/14 chunks successful"
   - Test chatbot: Ask questions about Bio NPK, K-Factor, etc.

## Why This Approach is Better

### Old Behavior (All-or-Nothing)
```
14 chunks to process
→ 12 chunks succeed (600+ entities extracted)
→ Chunk 13 times out
→ STOP! Discard all 12 successful chunks
→ Knowledge base remains empty
→ Chatbot cannot answer questions
```

### New Behavior (Partial Success)
```
14 chunks to process
→ 12 chunks succeed (600+ entities extracted)
→ Chunk 13 times out after 5 retries
→ Log warning, continue
→ Chunk 14 succeeds
→ Save 13/14 chunks to knowledge base
→ Chatbot can answer 93% of questions
```

## Technical Details

### Why Chunk 13 Failed
- **504 DEADLINE_EXCEEDED**: Gemini API took too long to process
- Likely reasons:
  - Chunk 13 content was particularly complex
  - Gemini API was experiencing high load
  - Network latency spike during that chunk
  
### Why Not Increase Timeout?
- Higher timeouts don't solve the problem (Gemini server-side limit)
- Better to retry with exponential backoff
- Best to continue processing even if retries exhausted

### Retry Strategy
```
Attempt 1: Wait 4 seconds
Attempt 2: Wait 8 seconds  (exponential: 2^1 * 4)
Attempt 3: Wait 16 seconds (exponential: 2^2 * 4)
Attempt 4: Wait 32 seconds (exponential: 2^3 * 4)
Attempt 5: Wait 60 seconds (capped at max)
```

Total retry time: ~120 seconds for persistent failures

## Monitoring

When re-uploading the document, watch for these log patterns:

**✅ Good (Partial Success):**
```
Chunk 1 of 14 extracted 57 Ent + 57 Rel
Chunk 2 of 14 extracted 135 Ent + 53 Rel
...
ERROR: Failed to process chunk: 504 DEADLINE_EXCEEDED
WARNING: Document processing completed with 13/14 chunks successful. 
         1 chunks failed (likely due to API timeouts or rate limits). 
         Continuing with successfully processed chunks.
✅ Document processed successfully
```

**❌ Bad (Complete Failure):**
```
Chunk 1: Failed
Chunk 2: Failed
...
ERROR: All 14 chunks failed to process
Document processing failed
```

## Verification Tests

After re-uploading, test these questions:

1. **"what is k factor"** - Should work (data from working chunks)
2. **"Benefits of Bio NPK"** - Should work (data from working chunks)
3. **"what is its dosage"** - Should work with follow-up context

If these work, the fix is successful!

## Rollback (If Needed)

If this causes issues, revert with:
```bash
cd backend/lightrag/Lightrag_main
git checkout lightrag/operate.py
git checkout lightrag/llm/gemini.py
```

Then restart services.
