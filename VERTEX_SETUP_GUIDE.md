# 🔧 Vertex AI Search Setup Guide - JSONL Format

## 🚨 **Critical Fix Required**

Your current results are poor because we're using **unstructured JSON** instead of **structured JSONL**. This guide fixes the issue by implementing your AI/ML friend's solution.

## 📋 **Step-by-Step Setup**

### **Step 1: Upload the New JSONL Data**

1. **Upload to Google Cloud Storage:**
   ```bash
   # Upload the transformed JSONL file
   gsutil cp card_data.jsonl gs://your-bucket-name/
   ```

2. **Verify the upload:**
   ```bash
   gsutil ls gs://your-bucket-name/card_data.jsonl
   ```

### **Step 2: Delete and Recreate Data Store**

1. **Delete existing data store:**
   - Go to [Vertex AI Search Console](https://console.cloud.google.com/ai/search)
   - Find your current data store (cardgpt-engine_1752662874226)
   - Delete it completely

2. **Create new data store with structured data:**
   - Click "Create Data Store"
   - **Data Type**: Select "Structured data (JSONL)"
   - **Data Source**: Point to `gs://your-bucket-name/card_data.jsonl`
   - **Document ID field**: Select `id` from dropdown
   - **Important**: This tells Vertex to use our chunk IDs

### **Step 3: Configure Schema (Critical)**

1. **After data store creation, go to Schema settings**
2. **Mark `cardName` as Filterable:**
   - Find `cardName` field in schema
   - Enable "Filterable" checkbox
   - This enables precise metadata filtering

3. **Verify other fields:**
   - `jsonData` should be "Retrievable" (content)
   - `section` should be "Retrievable" (metadata)
   - `filename` should be "Retrievable" (metadata)

### **Step 4: Update Your Configuration**

Update your `.streamlit/secrets.toml` or environment variables:

```toml
# .streamlit/secrets.toml
GOOGLE_CLOUD_PROJECT = "your-project-id"
VERTEX_AI_LOCATION = "global"
VERTEX_AI_DATA_STORE_ID = "your-new-data-store-id"  # New data store ID
```

### **Step 5: Test the Fixed System**

Run the test script to verify the fix:

```bash
python test_vertex_search.py
```

## 🎯 **What This Fixes**

### **Before (Poor Results):**
- ❌ Google's auto-chunker made random cuts
- ❌ No metadata filtering (cardName, section)
- ❌ Retrieved wrong document sections
- ❌ LLM couldn't parse messy snippets

### **After (Fixed Results):**
- ✅ Precise chunk control (604 structured chunks)
- ✅ Metadata filtering: `cardName="Axis Atlas"`
- ✅ Clean, formatted content in each chunk
- ✅ LLM gets exactly the right information

## 🧪 **Testing Queries**

Test these queries to verify the fix:

1. **Welcome Benefits:**
   ```
   Query: "What are the welcome benefits of axis atlas"
   Expected: Should find welcome_benefits section with proper benefits
   ```

2. **Joining Fee:**
   ```
   Query: "What is the joining fee of atlas"
   Expected: Should find fees section with "₹5000 + GST"
   ```

3. **Card-Specific Filtering:**
   ```
   Query: "ICICI EPM utility rewards" (with card filter)
   Expected: Should only return ICICI EPM results
   ```

## 📊 **Data Structure**

Your new JSONL format provides:
- **604 total chunks** (vs 3 monolithic files)
- **Axis Atlas**: 203 chunks
- **ICICI EPM**: 231 chunks  
- **HSBC Premier**: 170 chunks
- **Perfect metadata** for each chunk

## 🚀 **Benefits of This Approach**

1. **Precise Retrieval**: Exact section targeting
2. **Metadata Filtering**: `cardName="Axis Atlas"` works perfectly
3. **Clean Content**: No more messy protobuf parsing
4. **Scalable**: Easy to add new cards
5. **Maintainable**: No more prompt tuning cycles

## 🔧 **Configuration Files Updated**

- ✅ `transform_to_jsonl.py` - Converts JSON to JSONL
- ✅ `src/vertex_retriever.py` - Uses metadata filtering
- ✅ `card_data.jsonl` - Structured data for Vertex AI

## 📞 **Support**

If you encounter issues:
1. Check the new data store configuration
2. Verify `cardName` is marked as filterable
3. Ensure you're using the new data store ID
4. Run the test script for validation

This fix addresses the core issue: **taking back control of chunking** and providing **structured metadata** that Vertex AI can use effectively!