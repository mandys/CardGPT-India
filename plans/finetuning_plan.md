# Credit Card Search Fine-Tuning Plan

## Overview
A systematic approach to improve search accuracy for the credit card RAG system using Vertex AI Search. This plan provides a repeatable process to diagnose and fix incorrect answers without repeated explanations.

## Quick Reference Checklist

When an answer is wrong, follow these steps in order:

1. ✅ **Check JSON source data** - Is the information in `/data/*.json`?
2. ✅ **Check JSONL chunking** - Is `/transform_to_jsonl.py` creating proper chunks?  
3. ✅ **Check JSONL output** - Does `/card_data.jsonl` contain the information?
4. ✅ **Check search results** - Is Vertex AI returning relevant documents?
5. ✅ **Check LLM prompt** - Is `/backend/services/llm.py` processing correctly?

## Detailed Diagnostic Workflow

### Step 1: Verify Source Data
**Files to check:**
- `/data/axis-atlas.json` 
- `/data/hsbc-premier.json`
- `/data/icici-epm.json`

**What to look for:**
- Does the specific information exist in the source JSON?
- Is the data structure correct (nested properly)?
- Are field names consistent?

**Actions:**
- ❌ **If data is missing:** Request additional sources to update JSON files
- ❌ **If data exists but is confusing/inconsistent:** Restructure JSON for clarity
- ✅ **If data exists and is clear:** Proceed to Step 2

### Step 2: Check Data Chunking  
**File to examine:** `/transform_to_jsonl.py`

**What to verify:**
- Is the `create_chunks_from_node()` function creating chunks that include the missing information?
- Are chunks too large/small/poorly formatted?
- Is Base64 encoding working correctly for Vertex AI format?

**Actions:**
- ❌ **If chunking is poor:** Modify chunk creation logic in `transform_to_jsonl.py`
- ✅ **If chunking looks good:** Proceed to Step 3

### Step 3: Verify JSONL Output
**File to inspect:** `/card_data.jsonl`

**What to check:**
- Search for keywords related to the missing information
- Verify chunks contain the expected content
- Check `cardName` and `section` metadata are correct
- Ensure Base64 content decodes properly

**Actions:**
- ❌ **If JSONL is incorrect:** Re-run `python transform_to_jsonl.py` after fixing Step 2
- ✅ **If JSONL contains info:** Proceed to Step 4

### Step 4: Test Search Results
**File to examine:** `/backend/services/vertex_retriever.py`

**What to debug:**
- Enable debug logging to see what documents Vertex AI returns
- Check if relevant chunks are being retrieved
- Verify search ranking and relevance scores
- Test different query formulations

**Actions:**
- ❌ **If wrong docs retrieved:** Enhance query preprocessing or update search parameters
- ❌ **If no docs retrieved:** Check Vertex AI data store upload/indexing
- ✅ **If correct docs retrieved:** Proceed to Step 5

### Step 5: Analyze LLM Prompt
**File to examine:** `/backend/services/llm.py`

**What to review:**
- Is the context being formatted correctly?
- Are the LLM instructions clear and specific?
- Is the prompt guiding toward the right type of answer?

**Actions:**
- ❌ **If prompt is inadequate:** Refine prompt template and instructions
- ❌ **If context formatting is wrong:** Fix context preparation logic

## Data Update Pipeline

When you need to update data:

```bash
# 1. Update JSON files with new/corrected data
vim /data/axis-atlas.json  # or relevant file

# 2. Regenerate JSONL
python transform_to_jsonl.py

# 3. Upload to Google Cloud (manual step via console)
# Upload new card_data.jsonl to Vertex AI data store

# 4. Wait for indexing (10-30 minutes)

# 5. Test improved results
```

## Search Enhancement Strategies

### Query Preprocessing
- Add relevant keywords before sending to Vertex AI
- Include card-specific terms and context  
- Implement category detection (hotel, utility, etc.)

### Chunk Optimization
- Review chunk size - not too big, not too small
- Ensure important information isn't split across chunks
- Add more granular section-based chunking if needed

### Metadata Filtering  
- Implement proper card-name filtering in Vertex AI Search
- Use structured metadata for better document targeting
- Map user-friendly names ("ICICI EPM") to actual card names

## Common Issues & Quick Fixes

### 🔍 **Issue:** Information exists but not retrieved by search
**Quick Fix:** Enhance query with better keywords in `vertex_retriever.py`
```python
# Add card-specific keywords to query
enhanced_query = f"{card_name} {category_keywords} {original_query}"
```

### 📊 **Issue:** Data exists but structure is confusing to LLM
**BEST FIX:** Restructure JSON data for clarity (NOT fat prompts)
```json
// WRONG: Confusing structure
"rewards": {"insurance": null}
"capping": {"insurance": "up to ₹1L monthly"}

// RIGHT: Clear structure  
"rewards": {"insurance": "3 points per ₹100 (up to ₹1,00,000 monthly)"}
```

### 📝 **Issue:** Information retrieved but answer is poorly formatted  
**Quick Fix:** Improve LLM prompt in `llm.py` (but prefer JSON fixes)

### 🧮 **Issue:** Calculation errors
**Quick Fix:** Add step-by-step calculation instructions to prompt
```python
prompt += "\nShow your calculation step-by-step with intermediate results."
```

### 🎯 **Issue:** Card-specific confusion (mixing up cards)
**Quick Fix:** Add card name filtering and context separation
```python
# Filter search results by card name
if card_filter:
    enhanced_query = f"cardName:{card_filter} {query}"
```

## Quality Assurance

### Test Query Examples
Keep these working correctly:
- "What are the annual fees for Axis Atlas?"
- "Cash withdrawal charges for HSBC Premier?"  
- "Hotel spending rewards on ICICI EPM?"
- "Compare fuel surcharge across all cards"

### Performance Monitoring
- Track answer accuracy over time
- Monitor search latency and costs
- Document successful prompt patterns

## Troubleshooting Log

Keep track of fixes in `/plans/troubleshooting_log.md`:
- Date of issue
- Query that failed  
- Root cause found
- Fix applied
- Test results

This systematic approach ensures you never have to re-explain the diagnostic process!