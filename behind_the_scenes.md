# Behind the Scenes: Enhanced Multi-Model RAG Pipeline

## 🔍 What You're Seeing in the Logs

### **Phase 1: Initial Document Processing (One-time Setup)**
```
INFO:src.retriever:Loaded 71 documents from 3 files
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
... (repeated 71 times)
INFO:src.embedder:Generated 71/71 embeddings successfully
INFO:src.retriever:Stored 71 documents with embeddings
```

**What's happening:**
1. **JSON Parsing**: Load `axis-atlas.json`, `icici-epm.json`, and `hsbc-premier.json` files
2. **Document Creation**: Each JSON section becomes a separate "document"
3. **Individual Embedding Calls**: Each document sent separately to OpenAI embedding API
4. **Vector Storage**: Store 71 vectors in memory for future searches

### **Phase 2: User Query Processing (Per Question)**
```
User Query: "does icici epm give points on utility spends"

INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:src.retriever:Found 7 similar documents (threshold: 0.0)
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:src.llm:Generated answer using gemini-1.5-flash: ~1200 input + ~150 output tokens
```

**What's happening:**
1. **Query Embedding**: Convert user question to vector (1 API call)
2. **Local Vector Search**: Compare query vector against 46 stored vectors using cosine similarity
3. **Context Retrieval**: Found 7 most similar documents 
4. **Smart Model Selection**: Choose optimal model based on query complexity
5. **Answer Generation**: Send enhanced question + 4 documents to selected model (1 API call)

---

## 📋 Document Creation Process

### **How JSON Files Become Documents**

**Original JSON Structure:**
```json
{
  "common_terms": {
    "interest_free_grace_period": {...},
    "finance_charges": {...},
    "rewards": {...}
  },
  "card": {
    "rewards": {...},
    "milestones": [...],
    "fees": {...}
  }
}
```

**Becomes 44 Separate Documents:**
```python
Document 1: {
  "id": "Icici_Epm_common_interest_free_grace_period",
  "cardName": "Icici Epm", 
  "section": "common_terms_interest_free_grace_period",
  "content": "Interest Free Grace Period:\n  Duration: 18 to 48 days\n  Condition For Loss: Lost if Total Amount Due is not paid..."
}

Document 2: {
  "id": "Icici_Epm_card_rewards",
  "cardName": "Icici Epm",
  "section": "rewards", 
  "content": "Rewards:\n  Rate General: 6 ICICI Bank Reward Points on every ₹200...\n  Capping Per Statement Cycle:\n    Insurance: 5,000 Reward Points..."
}
```

**Why 71 Documents from 3 Files?**
- Each major JSON section becomes a document
- ICICI EPM: ~23 sections → 23 documents
- Axis Atlas: ~23 sections → 23 documents  
- HSBC Premier: ~25 sections → 25 documents
- **Total: 71 documents**

---

## 🚀 The RAG Pipeline Step-by-Step

### **1. Indexing Phase (Startup - One Time)**

```mermaid
JSON Files → Document Chunking → Individual Embedding Calls → Vector Storage
```

**Detailed Flow:**
1. **Load JSON**: Read axis-atlas.json, icici-epm.json, hsbc-premier.json
2. **Section Extraction**: Split each card into logical sections (rewards, fees, etc.)
3. **Document Formatting**: Convert each section to readable text
4. **Embedding Generation**: **71 separate API calls** to OpenAI embeddings
5. **Vector Storage**: Store 71 vectors (1536 dimensions each) in memory

**🔴 Inefficiency #1: Individual Embedding Calls**
- Current: 71 separate API calls
- Could be: 1-2 batch API calls (OpenAI supports up to 2048 inputs per batch)

### **2. Query Phase (Per User Question)**

```mermaid
User Question → Query Embedding → Vector Search → Context Selection → LLM Answer
```

**Detailed Flow:**
1. **Query Embedding**: "does icici epm give points on utility spends" → vector (1 API call)
2. **Similarity Search**: Compare query vector vs 71 stored vectors (local, fast)
3. **Ranking**: Calculate cosine similarity scores for all documents
4. **Top-K Selection**: Pick 7 most similar documents (threshold: 0.0)
5. **Context Building**: Combine 7 documents into context prompt
6. **Answer Generation**: Send context + question to selected model (1 API call)

---

## 💡 Understanding Vector Search

### **What Happens During "Local Search"**

**The 7 Documents Found:**
```
Document 1: ICICI EPM - Rewards (similarity: 0.87)
Document 2: ICICI EPM - Reward Capping (similarity: 0.84) 
Document 3: ICICI EPM - Surcharge Fees (similarity: 0.71)
Document 4: ICICI EPM - Accrual Exclusions (similarity: 0.68)
Document 5: Axis Atlas - Rewards (similarity: 0.45)
Document 6: ICICI EPM - Finance Charges (similarity: 0.42)
Document 7: ICICI EPM - Other Fees (similarity: 0.38)
```

**How Similarity Works:**
- Query: "utility spends points" → [0.2, 0.8, 0.1, 0.9, ...]
- Doc: "Utility: 1,000 Reward Points" → [0.3, 0.7, 0.2, 0.8, ...]
- Cosine similarity: 0.84 (high match)

### **Context Building for LLM**

**What Gets Sent to Selected Model (e.g., Gemini Flash):**
```
System: You are an expert assistant helping users understand Indian credit card terms...

User: Based on the following information, answer: "does icici epm give points on utility spends"

Context:
Card: Icici Epm
Section: rewards
Content: Rewards:
  Rate General: 6 ICICI Bank Reward Points on every ₹200 spent
  Capping Per Statement Cycle:
    Utility: 1,000 Reward Points (MCC 4900, 4899, 4901...)

Card: Icici Epm  
Section: reward_capping
Content: Reward Capping:
  Utility: 1,000 Reward Points
...
```

**Token Count Breakdown (Optimized):**
- Input: ~1,200 tokens (concise prompt + context + question)
- Output: ~150 tokens (AI's answer)
- **Cost: ~$0.0003** for this query (with Gemini Flash)

---

## 🎯 Why This Architecture?

### **Pros:**
✅ **Semantic Search**: Finds relevant info even with different wording
✅ **Contextual Answers**: LLM sees multiple related documents  
✅ **Scalable**: Can add more cards without changing code
✅ **Accurate**: Combines multiple data points for comprehensive answers

### **Cons:**
❌ **Slow Startup**: 44 individual embedding calls (30-60 seconds)
❌ **API Costs**: Each document embedding costs ~$0.000004
❌ **Memory Usage**: Stores all vectors in RAM
❌ **No Persistence**: Re-generates embeddings on restart

---

## 🚀 Optimization Opportunities

### **1. Batch Embedding Generation**
**Current:**
```python
for doc in documents:
    embedding = openai.embeddings.create(model="text-embedding-3-small", input=doc.content)
```

**Optimized:**
```python
# Send up to 2048 documents in one API call
all_content = [doc.content for doc in documents]
embeddings = openai.embeddings.create(model="text-embedding-3-small", input=all_content)
```

**Impact:** 46 API calls → 1 API call (46x faster startup)

### **2. Persistent Vector Storage**
**Current:** Re-generate embeddings every restart
**Better:** Save to disk (pickle/json) or use vector DB (ChromaDB, Pinecone)

### **3. Smarter Chunking**
**Current:** Split by JSON sections
**Better:** Semantic chunking (keep related info together)

---

## 🔬 Query Example Breakdown

**Query:** "does icici epm give points on utility spends"

**Step 1: Query Understanding**
- Embedding captures semantic meaning: utility payments, reward points, ICICI EPM card

**Step 2: Document Matching**
- High match: "Utility: 1,000 Reward Points (MCC 4900...)"
- Medium match: "Rate General: 6 points per ₹200"
- Low match: "Surcharge fees on utilities"

**Step 3: Answer Synthesis**
AI model combines information:
- Base rate: 6 points per ₹200
- Utility capping: 1,000 points per month
- Applicable MCCs: 4900, 4899, etc.

**Final Answer:** "Yes, ICICI EPM gives 6 points per ₹200 on utility spends, capped at 1,000 points per statement cycle..."

---

## 🧮 Cost Analysis

### **One-Time Costs (Startup):**
- 46 documents × ~200 tokens × $0.00002/1K = **$0.0002**

### **Per Query Costs (Multi-Model):**
- Query embedding: ~10 tokens × $0.00002/1K = **$0.0000002**

| Model | Per Query Cost | Use Case |
|-------|---------------|----------|
| **Gemini Flash** | **$0.0003** | Simple queries (default) |
| **GPT-3.5** | $0.002 | General queries |
| **Gemini Pro** | $0.005 | Complex calculations |
| **GPT-4** | $0.06 | Premium accuracy |

### **Daily Usage Example (Gemini Flash):**
- 100 queries × $0.0003 = **$0.03/day**
- Monthly cost: **~$1** (vs $15 with GPT-3.5)

### **Cost Comparison:**
- **Gemini Flash**: $0.0003 per query (20x cheaper than GPT-3.5!)
- **GPT-3.5**: $0.002 per query  
- **GPT-4**: $0.06 per query (200x more expensive than Gemini Flash)

---

This architecture prioritizes accuracy and semantic understanding over raw speed, which is why you see the multiple API calls and detailed processing steps!

---

## 🚀 Major Enhancements Implemented

### **1. Multi-Model Support**

**Added Support For:**
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Google Gemini**: 1.5 Flash (ultra-cheap), 1.5 Pro (complex calculations)

**Smart Model Selection:**
```python
if complex_calculation:
    model = "gemini-1.5-pro"  # Better accuracy
else:
    model = "gemini-1.5-flash"  # 20x cheaper
```

### **2. Query Enhancement System**

**Category Detection:**
```python
query = "What rewards for ₹50K utility spend?"
# Detected: category=utility, spend_amount=50000
# Enhanced: "IMPORTANT: Axis excludes utilities, ICICI caps at 1K points"
```

**Smart Guidance:**
- **Hotel/Flight**: Use accelerated rates (5 miles vs 2 base)
- **Utility**: Check exclusions (Axis=0, ICICI=capped)
- **Complex Calc**: Auto-route to better model

### **3. Token Optimization (60% Reduction)**

**Before Optimization:**
- System prompt: 1,400 tokens
- Context: 1,200 tokens (7 docs)
- Total: ~3,000 tokens

**After Optimization:**
- System prompt: 400 tokens (condensed)
- Context: 800 tokens (4 docs, truncated)
- Total: ~1,200 tokens

**Impact:** $0.005 → $0.0003 per query (with Gemini Flash)

### **4. Calculation Accuracy Fixes**

**Fixed Issues:**
- ✅ **Milestone Logic**: Cumulative bonuses (₹7.5L = ₹3L + ₹7.5L milestones)
- ✅ **Exclusion Rules**: ICICI utilities capped (not excluded)
- ✅ **Arithmetic**: (20000÷200)×6 = 600 (not 60)
- ✅ **Category Rates**: Hotels use 5 miles/₹100 (not 2)

**Enhanced Prompts:**
```
CRITICAL: For each ₹ spent, apply ONLY ONE earning rate
EXAMPLE: ₹7.5L general → (750000÷100)×2 = 15,000 + milestones 5,000 = 20,000
```