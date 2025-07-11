# Behind the Scenes: RAG Pipeline Deep Dive

## 🔍 What You're Seeing in the Logs

### **Phase 1: Initial Document Processing (One-time Setup)**
```
INFO:src.retriever:Loaded 44 documents from 2 files
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
... (repeated 44 times)
INFO:src.embedder:Generated 44/44 embeddings successfully
INFO:src.retriever:Stored 44 documents with embeddings
```

**What's happening:**
1. **JSON Parsing**: Load `axis-atlas.json` and `icici-epm.json` files
2. **Document Creation**: Each JSON section becomes a separate "document"
3. **Individual Embedding Calls**: Each document sent separately to OpenAI embedding API
4. **Vector Storage**: Store 44 vectors in memory for future searches

### **Phase 2: User Query Processing (Per Question)**
```
User Query: "does icici epm give points on utility spends"

INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:src.retriever:Found 7 similar documents (threshold: 0.0)
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:src.llm:Generated answer using gpt-3.5-turbo: 2446 input + 183 output tokens
```

**What's happening:**
1. **Query Embedding**: Convert user question to vector (1 API call)
2. **Local Vector Search**: Compare query vector against 44 stored vectors using cosine similarity
3. **Context Retrieval**: Found 7 most similar documents 
4. **Answer Generation**: Send question + 7 documents to GPT-3.5 (1 API call)

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

**Why 44 Documents from 2 Files?**
- Each major JSON section becomes a document
- ICICI EPM: ~22 sections → 22 documents
- Axis Atlas: ~22 sections → 22 documents
- **Total: 44 documents**

---

## 🚀 The RAG Pipeline Step-by-Step

### **1. Indexing Phase (Startup - One Time)**

```mermaid
JSON Files → Document Chunking → Individual Embedding Calls → Vector Storage
```

**Detailed Flow:**
1. **Load JSON**: Read axis-atlas.json, icici-epm.json
2. **Section Extraction**: Split each card into logical sections (rewards, fees, etc.)
3. **Document Formatting**: Convert each section to readable text
4. **Embedding Generation**: **44 separate API calls** to OpenAI embeddings
5. **Vector Storage**: Store 44 vectors (1536 dimensions each) in memory

**🔴 Inefficiency #1: Individual Embedding Calls**
- Current: 44 separate API calls
- Could be: 1-2 batch API calls (OpenAI supports up to 2048 inputs per batch)

### **2. Query Phase (Per User Question)**

```mermaid
User Question → Query Embedding → Vector Search → Context Selection → LLM Answer
```

**Detailed Flow:**
1. **Query Embedding**: "does icici epm give points on utility spends" → vector (1 API call)
2. **Similarity Search**: Compare query vector vs 44 stored vectors (local, fast)
3. **Ranking**: Calculate cosine similarity scores for all documents
4. **Top-K Selection**: Pick 7 most similar documents (threshold: 0.0)
5. **Context Building**: Combine 7 documents into context prompt
6. **Answer Generation**: Send context + question to GPT-3.5 (1 API call)

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

**What Gets Sent to GPT-3.5:**
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

**Token Count Breakdown:**
- Input: 2,446 tokens (system prompt + context + question)
- Output: 183 tokens (GPT's answer)
- **Cost: ~$0.005** for this query

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

**Impact:** 44 API calls → 1 API call (44x faster startup)

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
GPT-3.5 combines information:
- Base rate: 6 points per ₹200
- Utility capping: 1,000 points per month
- Applicable MCCs: 4900, 4899, etc.

**Final Answer:** "Yes, ICICI EPM gives 6 points per ₹200 on utility spends, capped at 1,000 points per statement cycle..."

---

## 🧮 Cost Analysis

### **One-Time Costs (Startup):**
- 44 documents × ~200 tokens × $0.00002/1K = **$0.0002**

### **Per Query Costs:**
- Query embedding: ~10 tokens × $0.00002/1K = **$0.0000002**
- GPT-3.5 answer: (2446 + 183) tokens × $0.002/1K = **$0.005**
- **Total per query: ~$0.005**

### **Daily Usage Example:**
- 100 queries × $0.005 = **$0.50/day**
- Monthly cost: **~$15**

### **GPT-4 vs GPT-3.5:**
- GPT-4: ~$0.15 per query (30x more expensive)
- GPT-3.5: ~$0.005 per query

---

This architecture prioritizes accuracy and semantic understanding over raw speed, which is why you see the multiple API calls and detailed processing steps!