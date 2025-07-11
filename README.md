# Supavec Clone - RAG API for Indian Credit Card Data

A modular Retrieval-Augmented Generation (RAG) application for querying Indian credit card terms and conditions using OpenAI and vector search.

## Features

- **Vector Search**: Semantic search through credit card terms and conditions
- **RAG Pipeline**: Intelligent question answering using OpenAI GPT-4
- **Multi-Card Support**: Query individual cards or compare multiple cards
- **Extensible**: Easy to add new credit card data files
- **RESTful API**: Clean HTTP endpoints for integration
- **Streamlit Frontend**: Interactive chat interface with deployment support

## Quick Start

### Prerequisites

- Node.js 18+
- OpenAI API key

### Installation

1. Clone and install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. Start the development server:
```bash
npm run dev
```

The API will be available at `http://localhost:3000`

### Streamlit Frontend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run Streamlit frontend:
```bash
# With backend API (recommended)
streamlit run streamlit_app.py

# Standalone version (no backend needed)
streamlit run streamlit_standalone.py
```

The Streamlit app will be available at `http://localhost:8501`

## Modular Architecture

The application is organized into focused modules for better maintainability:

### 📁 **Project Structure**
```
supavec-clone/
├── app.py                 # Main Streamlit application
├── src/
│   ├── __init__.py       # Package initialization
│   ├── embedder.py       # OpenAI embedding service
│   ├── llm.py           # OpenAI LLM service (GPT-4/3.5)
│   └── retriever.py     # Vector search & document management
├── data/                 # Credit card JSON files
├── streamlit_standalone.py  # Legacy monolithic version
└── requirements.txt

```

### 🔧 **Module Responsibilities**

#### `src/embedder.py` - Embedding Service
- Converts text to vectors using OpenAI embeddings
- Handles batch processing for multiple documents
- Tracks token usage and costs
- Provides embedding model information

#### `src/llm.py` - Language Model Service  
- Generates answers using GPT-4 or GPT-3.5-turbo
- Manages conversation context and prompts
- Calculates costs for different models
- Optimized prompts for credit card calculations

#### `src/retriever.py` - Document Retrieval Service
- Loads and processes JSON credit card data
- Performs vector similarity search
- Applies keyword boosting for better results
- Manages document storage and indexing

#### `app.py` - Main Application
- Streamlit user interface
- Orchestrates all services
- Handles user interactions and chat
- Displays costs, sources, and results

### 🚀 **Running the Modular Version**

```bash
# Use the new modular version (recommended)
streamlit run app.py

# Or use the legacy standalone version
streamlit run streamlit_standalone.py
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Get Available Cards
```bash
GET /api/cards
```

### Query All Cards
```bash
POST /api/query
{
  "question": "What are the interest rates?",
  "topK": 5
}
```

### Query Specific Card
```bash
POST /api/query/:cardName
{
  "question": "What are the cash withdrawal fees?",
  "topK": 5
}
```

### Compare Cards
```bash
POST /api/compare
{
  "question": "Compare interest rates",
  "cards": ["Axis Atlas", "Icici Epm"]
}
```

### Vector Search
```bash
POST /api/search
{
  "query": "interest rates",
  "topK": 5,
  "threshold": 0.3
}
```

## Adding New Credit Card Data

1. Create a JSON file in the `/data` directory
2. Follow the existing structure with `common_terms` containing:
   - `interest_free_grace_period`
   - `minimum_amount_due_logic`
   - `finance_charges`
   - `surcharge_fees`
   - `cash_withdrawal`
   - `other_fees`
   - etc.

3. Restart the application to load the new data

## Example Usage

```bash
# Query about interest rates
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the interest rates for credit cards?"}'

# Compare cash withdrawal fees
curl -X POST http://localhost:3000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare cash withdrawal fees", "cards": ["Axis Atlas", "Icici Epm"]}'
```

## Streamlit Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Choose `streamlit_standalone.py` as your main file
5. Add your OpenAI API key to Streamlit secrets:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```
6. Deploy!

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run standalone version (recommended for development)
streamlit run streamlit_standalone.py

# Run with backend API
npm run dev  # In one terminal
streamlit run streamlit_app.py  # In another terminal
```

## Architecture

- **Data Loader**: Processes JSON files from `/data` directory
- **Embedding Service**: Generates vector embeddings using OpenAI
- **Vector Search**: Performs semantic search using cosine similarity
- **RAG Pipeline**: Combines search results with GPT-4 for intelligent answers
- **API Layer**: Express.js REST API with comprehensive endpoints

## How It Works: RAG Pipeline Explained

### 1. **Data Processing & Indexing** (One-time setup)
```
JSON Files → Document Chunks → OpenAI Embeddings → In-Memory Vector Store
```
- Each credit card JSON is split into sections (rewards, fees, etc.)
- Each section becomes a "document" with text content
- OpenAI `text-embedding-3-small` converts text to 1536-dimensional vectors
- Vectors stored in memory (no ChromaDB - just Python arrays)

### 2. **Query Processing** (Per user question)
```
User Question → Query Embedding → Vector Search → Context Retrieval → GPT Answer
```

**Step by step:**
1. **User asks**: "What reward points for ₹50,000 insurance spend on ICICI EPM?"
2. **Query Embedding**: OpenAI converts question to vector (1 API call)
3. **Vector Search**: Cosine similarity against all stored vectors (local, fast)
4. **Context Retrieval**: Top 5 most similar documents retrieved
5. **Answer Generation**: Context + question sent to GPT-4 (1 API call)

### 3. **Vector Database: In-Memory Only**
- **No ChromaDB/Pinecone**: Uses simple Python arrays with NumPy
- **Storage**: Session state in Streamlit (resets on restart)
- **Search**: Pure cosine similarity calculation
- **Speed**: Very fast once embeddings are generated

### 4. **OpenAI API Calls & Costs**

#### **Embedding Generation** (One-time per document)
- **Model**: `text-embedding-3-small`
- **Cost**: $0.00002 per 1K tokens
- **When**: App startup (cached until restart)
- **Volume**: ~50-100 documents × average 200 tokens = ~$0.0002-0.0004

#### **Answer Generation** (Per query)
- **Model**: `gpt-4`
- **Cost**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **When**: Every user question
- **Volume**: Context (2,000-5,000 tokens) + Response (200-1,000 tokens) = ~$0.10-0.30 per query

### 5. **Why It's Slow**
1. **Embedding Generation**: First load takes 30-60 seconds (50+ OpenAI API calls)
2. **GPT-4 Calls**: Each answer takes 3-10 seconds
3. **Network Latency**: API round trips to OpenAI servers

### 6. **The Actual RAG Prompt Template**
```
System Prompt:
You are an expert assistant helping users understand Indian credit card terms and conditions.

Please provide accurate, helpful answers based on the provided context. If the context doesn't contain enough information to answer the question, say so clearly.

Format your response in a clear, easy-to-understand way. Use bullet points or numbered lists when appropriate.
Include specific details like fees, interest rates, and conditions when relevant.

User Prompt:
Based on the following credit card information, please answer this question: "{user_question}"

Context:
Card: ICICI EPM
Section: rewards
Content: Rewards:
  Rate General: 6 ICICI Bank Reward Points on every ₹200 spent at all eligible retail transactions
  Capping Per Statement Cycle:
    Insurance: 5,000 Reward Points (MCC 6300, 5960)
    Grocery: 1,000 Reward Points (MCC 5331, 5499, 5411)
    ...

Please provide a comprehensive answer based on the information provided.
```

### 7. **Cost Optimization Tips**
- Use `gpt-3.5-turbo` instead of `gpt-4` (10x cheaper)
- Reduce `top_k` from 5 to 3 documents
- Implement query caching for repeated questions
- Use `text-embedding-3-small` (already optimized)

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start
```