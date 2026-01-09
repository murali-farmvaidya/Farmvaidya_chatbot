# AGRICULTURAL CHATBOT - QUESTION TYPES & HANDLING ANALYSIS

## 📊 CURRENT QUESTION TYPES HANDLED

Based on code analysis of `chat_service.py` and `chat_rules.py`:

### 1. ✅ GREETINGS & ACKNOWLEDGMENTS
**Detection Function:** `is_greeting_or_acknowledgment()`
**Examples:**
- English: "hi", "hello", "good morning", "thanks", "ok"
- Telugu: "నమస్కారం", "హలో", "ధన్యవాదాలు"
- Hindi: "नमस्ते", "धन्यवाद"

**Current Handling:**
- **LightRAG Mode:** NOT USED (Direct response)
- **History:** No
- **Method:** Pre-defined contextual responses in 3 languages
- **Why:** Fast response, no need for knowledge base lookup

---

### 2. ✅ DOSAGE QUESTIONS
**Detection Function:** `is_dosage_question()`
**Examples:**
- "How much Invictus for 72 acres?"
- "ఇన్విక్టస్ మోతాదు ఎంత?"
- "K-Factor dosage per acre"
- Keywords: dosage, dose, quantity, per acre, మోతాదు, ఎంత వాడాలి

**Current Handling:**
- **LightRAG Mode:** `naive` ✅ (RECENTLY CHANGED FROM `mix`)
- **History:** No (prevents language contamination)
- **Translation:** Yes (domain-specific terms translated)
- **Why naive mode works best:** 
  - Direct retrieval from knowledge base
  - Better for specific product queries
  - No graph-based reasoning needed

---

### 3. ✅ FACTUAL/COMPANY QUESTIONS
**Detection Function:** `is_factual_company_question()`
**Examples:**
- "Who is the CEO of BioFactor?"
- "How many patents does BioFactor have?"
- "Where is FarmVaidya headquarters?"
- Keywords: who is, CEO, patents, founded, established

**Current Handling:**
- **LightRAG Mode:** `mix` (default)
- **History:** No (avoids entity confusion)
- **Special Flag:** `factual=True` (prevents forcing wrong answers)
- **Why mix mode:** Combines local and global context for company facts

---

### 4. ✅ DIRECT KNOWLEDGE/PRODUCT QUESTIONS
**Detection Function:** `is_direct_knowledge_question()`
**Examples:**
- "What is Poshak?"
- "Tell me about Aadhaar Gold"
- "Benefits of Bio NPK"
- Keywords: what is, tell me, explain, benefits, features

**Current Handling:**
- **LightRAG Mode:** `mix` (default)
- **History:** No (prevents language contamination)
- **Translation:** Yes (product names translated)
- **Why mix mode:** Good for general product information

---

### 5. ✅ PROBLEM DIAGNOSIS QUESTIONS (WITH FOLLOW-UPS)
**Detection Function:** `is_problem_diagnosis_question()`
**Examples:**
- "My coconut tree leaves are turning yellow"
- "నా కొబ్బరి చెట్టు ఆకులు పసుపు అవుతున్నాయి"
- "Pest problem in my crop"
- Keywords: problem, pest, disease, dying, yellow, poor growth

**Current Handling:**
- **LightRAG Mode:** `mix` (default) after collecting follow-ups
- **History:** Yes (full conversation context used)
- **Follow-up Flow:** 
  1. Asks for crop name & growth stage
  2. Asks for soil type & irrigation
  3. Asks for fertilizers already used
- **MAX_FOLLOWUPS:** 3 questions
- **Special Processing:** Builds comprehensive query with all context

**Why follow-ups are needed:**
- Diagnosis needs specific context (crop, soil, stage, etc.)
- Generic answers may not be accurate
- Collects farmer-specific information systematically

---

### 6. ✅ GENERAL AGRICULTURAL QUESTIONS
**Fallback for unclassified questions**
**Examples:**
- "Best time to plant coconut?"
- "How to increase coconut yield?"
- "What is drip irrigation?"

**Current Handling:**
- **LightRAG Mode:** `mix` (default)
- **History:** Yes (conversation context)
- **When:** Any question not matching above categories

---

## 🎯 LIGHTRAG MODES AVAILABLE

### Available Modes:
1. **`naive`** - Direct vector search without graph reasoning
2. **`local`** - Local graph traversal
3. **`global`** - Global graph analysis
4. **`hybrid`** - Combination of local and global
5. **`mix`** - Adaptive combination (DEFAULT)
6. **`bypass`** - Direct LLM without RAG (used internally)

---

## 📋 COMPREHENSIVE MODE RECOMMENDATIONS

### ✅ Current Optimal Settings:

| Question Type | Current Mode | History | Recommended Mode | Why |
|--------------|--------------|---------|------------------|-----|
| **Greetings** | N/A (Direct) | No | N/A | Pre-defined responses |
| **Dosage** | `naive` ✅ | No | `naive` or `local` | Direct product info retrieval |
| **Factual/Company** | `mix` | No | `mix` or `global` | Company facts need broad context |
| **Product Knowledge** | `mix` | No | `local` or `mix` | Product relationships matter |
| **Problem Diagnosis** | `mix` | Yes | `hybrid` or `local` | Needs context + relationships |
| **General Agricultural** | `mix` | Yes | `mix` | Adaptive to query type |

---

## 🚀 RECOMMENDED IMPROVEMENTS

### 1. Add More Question Types
Currently missing these common agricultural questions:

#### A. **Weather/Season Questions**
```python
def is_weather_season_question(text: str) -> bool:
    keywords = ["weather", "season", "rainfall", "temperature", 
                "climate", "monsoon", "వాతావరణం", "సీజన్", "मौसम"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `global` (seasonal patterns across regions)

#### B. **Market/Price Questions**
```python
def is_market_price_question(text: str) -> bool:
    keywords = ["price", "market", "rate", "cost", "sell",
                "ధర", "మార్కెట్", "कीमत", "बाजार"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `bypass` (needs real-time data, not in knowledge base)

#### C. **Crop Rotation/Planning Questions**
```python
def is_crop_planning_question(text: str) -> bool:
    keywords = ["rotation", "intercrop", "planning", "schedule",
                "when to plant", "best crop", "crop selection"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `global` (needs relationship understanding)

#### D. **Pest/Disease Identification**
```python
def is_pest_identification_question(text: str) -> bool:
    keywords = ["identify", "what pest", "which disease", "name of",
                "looks like", "symptoms", "గుర్తించండి", "पहचान"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `local` + follow-ups (needs symptom details)

#### E. **Soil Testing/Analysis Questions**
```python
def is_soil_testing_question(text: str) -> bool:
    keywords = ["soil test", "soil analysis", "pH", "EC", 
                "nutrient test", "నేల పరీక్ష", "मिट्टी परीक्षण"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `local` (soil-specific recommendations)

#### F. **Government Schemes/Subsidies**
```python
def is_government_scheme_question(text: str) -> bool:
    keywords = ["scheme", "subsidy", "government", "loan",
                "PM-KISAN", "యోజన", "సబ్సిడీ", "योजना"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `global` (broad policy knowledge)

#### G. **Equipment/Machinery Questions**
```python
def is_equipment_question(text: str) -> bool:
    keywords = ["equipment", "machine", "tractor", "tool",
                "sprayer", "యంత్రం", "उपकरण"]
    return any(k in text.lower() for k in keywords)
```
**Recommended Mode:** `local` (specific equipment recommendations)

---

## 🔍 WHAT TO DO IF ANSWER IS NOT FOUND

### Current Implementation:
```python
# In chat_service.py - for diagnosis questions
if "[no-context]" in answer or not answer:
    # Falls back to local knowledge base
    answer = synthesize_answer(soil_type, growth_stage, irrigation, fertilizers)
```

### Recommended Enhancements:

#### 1. **Try Multiple Modes Sequentially**
```python
def query_with_fallback(query, history, language):
    """Try multiple modes until answer is found"""
    modes_to_try = ["naive", "local", "hybrid", "global", "mix"]
    
    for mode in modes_to_try:
        print(f"🔍 Trying mode: {mode}")
        answer = query_lightrag(query, history, mode=mode, language=language)
        
        # Check if we got a valid answer
        if answer and "[no-context]" not in answer.lower() and len(answer) > 50:
            print(f"✅ Found answer using mode: {mode}")
            return answer
    
    print("⚠️ No answer found in any mode, using fallback")
    return None  # Use fallback logic
```

#### 2. **Query Reformulation**
```python
def reformulate_query(original_query, language):
    """Try different query formulations"""
    variations = [
        original_query,  # Original
        f"How to {original_query}",  # Add "how to"
        f"{original_query} in agriculture",  # Add context
        # Extract key terms and search
    ]
    return variations
```

#### 3. **Expand Search Scope**
```python
def expand_search(query, history, language):
    """Expand search by adding related terms"""
    # Add synonyms, related terms from domain dictionary
    expanded_query = add_synonyms(query)
    return query_lightrag(expanded_query, history, mode="global", language=language)
```

#### 4. **Ask Clarifying Questions**
```python
def ask_clarification(query, language):
    """If answer not found, ask for clarification"""
    clarification = {
        "english": "I couldn't find specific information about that. Could you provide more details or rephrase your question?",
        "telugu": "దాని గురించి నిర్దిష్ట సమాచారం కనుగొనలేకపోయాను. మరింత వివరాలు ఇవ్వగలరా లేదా మీ ప్రశ్నను మరొకసారి అడగగలరా?",
        "hindi": "मुझे इसके बारे में विशिष्ट जानकारी नहीं मिली। क्या आप अधिक विवरण दे सकते हैं या अपना प्रश्न फिर से पूछ सकते हैं?"
    }
    return clarification.get(language, clarification["english"])
```

---

## 📈 METRICS TO TRACK

### Add these to understand what's working:

```python
# In lightrag_service.py
import time

def query_lightrag_with_metrics(query, history, mode="mix", language="english"):
    start_time = time.time()
    
    response = query_lightrag(query, history, mode, language)
    
    # Track metrics
    metrics = {
        "mode": mode,
        "language": language,
        "query_length": len(query),
        "response_length": len(response),
        "time_taken": time.time() - start_time,
        "success": "[no-context]" not in response.lower() and len(response) > 20,
        "timestamp": datetime.utcnow()
    }
    
    # Log to database or file
    log_query_metrics(metrics)
    
    return response
```

---

## 🎯 SUMMARY

### Currently Handled: 6 Question Types
1. ✅ Greetings (Direct response)
2. ✅ Dosage (`naive` mode)
3. ✅ Factual/Company (`mix` mode)
4. ✅ Product Knowledge (`mix` mode)
5. ✅ Problem Diagnosis (`mix` mode + follow-ups)
6. ✅ General questions (`mix` mode)

### Missing: 7+ Important Types
- Weather/Season questions
- Market/Price questions
- Crop Planning questions
- Pest Identification questions
- Soil Testing questions
- Government Schemes questions
- Equipment questions

### Mode Usage Optimization:
- **`naive`**: Best for direct fact retrieval (dosage, specs)
- **`local`**: Best for related entities (pest-remedy, crop-fertilizer)
- **`global`**: Best for broad patterns (seasonal advice, regional practices)
- **`hybrid`**: Best for complex diagnosis (combines local + global)
- **`mix`**: Safe default (adaptive)

### Next Steps:
1. Add detection functions for missing question types
2. Implement multi-mode fallback strategy
3. Add query reformulation
4. Track metrics to optimize mode selection
5. Consider adding confidence scores
