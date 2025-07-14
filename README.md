# Credit Card Assistant

A smart assistant for querying Indian credit card terms and conditions using AI. Get instant answers about rewards, fees, eligibility, and more. Built with Python and Streamlit.

## Features

- **Vector Search**: Semantic search through credit card terms and conditions
- **Multi-Model AI**: Choose from GPT-4, GPT-3.5, or Gemini 1.5 (Flash/Pro)
- **Ultra-Low Cost**: Gemini Flash costs 20x less than GPT-3.5 (~$0.0003/query)
- **Smart Model Selection**: Auto-upgrades complex calculations to better models  
- **Multi-Card Support**: Query individual cards or compare multiple cards
- **Category-Aware**: Correctly handles hotel/flight vs general spending rates
- **Extensible**: Easy to add new credit card data files
- **Real-Time Costs**: Live token usage and cost tracking

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (required)
- Gemini API key (optional, for 20x cheaper queries)

### Installation

1. Clone and install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"
export GEMINI_API_KEY="your-gemini-key-here"  # Optional but recommended
# Or add to your .streamlit/secrets.toml file
```

3. Run the application:
```bash
streamlit run app.py
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
│   ├── llm.py           # Multi-model LLM service (GPT-4/3.5, Gemini)
│   ├── query_enhancer.py # Smart query preprocessing
│   └── retriever.py     # Vector search & document management
├── data/                 # Credit card JSON files
└── requirements.txt

```

### 🔧 **Module Responsibilities**

#### `src/embedder.py` - Embedding Service
- Converts text to vectors using OpenAI embeddings
- Handles batch processing for multiple documents
- Tracks token usage and costs
- Provides embedding model information

#### `src/llm.py` - Multi-Model Language Service  
- Supports GPT-4, GPT-3.5-turbo, Gemini 1.5 Flash/Pro
- Smart model selection for complex calculations
- Real-time cost tracking across all models
- Optimized prompts for accurate credit card calculations

#### `src/query_enhancer.py` - Query Preprocessing
- Detects spending categories (hotels, utilities, etc.)
- Provides model-specific guidance for accuracy
- Handles spend distribution and comparison queries

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

### 🚀 **Running the Application**

```bash
# Run the modular Streamlit application
streamlit run app.py
```

### 🔧 **Development**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application in development mode
streamlit run app.py

# Git workflow
git status
git add .
git commit -m "Your changes"
```

## Usage

### Query Modes

1. **General Query**: Ask questions about any credit card
2. **Specific Card**: Focus on a particular card
3. **Compare Cards**: Compare multiple cards side-by-side

### Example Questions

- "What are the interest rates for credit cards?"
- "How many miles do I earn on ₹2 lakh flight spend with Axis Atlas?"
- "Compare cash withdrawal fees between cards"
- "What are the hotel booking rewards for ₹1 lakh spend?"
- "Are utilities capped for HSBC Premier card?"
- "What are the joining benefits of HSBC Premier?"

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


## Streamlit Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Choose `app.py` as your main file
5. Add your OpenAI API key to Streamlit secrets:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```
6. Deploy!

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Architecture

- **Data Loader**: Processes JSON files from `/data` directory
- **Embedding Service**: Generates vector embeddings using OpenAI
- **Vector Search**: Performs semantic search using cosine similarity
- **RAG Pipeline**: Combines search results with GPT-4 for intelligent answers
- **Streamlit UI**: Interactive chat interface with cost tracking

## How It Works: Enhanced RAG Pipeline

### 1. **Data Processing & Indexing** (One-time setup)
```
JSON Files → Document Chunks → OpenAI Embeddings → In-Memory Vector Store
```
- Each credit card JSON is split into sections (rewards, fees, etc.)
- Each section becomes a "document" with text content
- OpenAI `text-embedding-3-small` converts text to 1536-dimensional vectors
- Vectors stored in memory (no ChromaDB - just Python arrays)
- Supports 3 cards: Axis Atlas, ICICI EPM, HSBC Premier

### 2. **Smart Query Processing** (Per user question)
```
User Question → Query Enhancement → Vector Search → Model Selection → AI Answer
```

**Enhanced step by step:**
1. **User asks**: "What reward points for ₹50,000 insurance spend on ICICI EPM?"
2. **Query Enhancement**: Detect category (insurance), add guidance
3. **Query Embedding**: OpenAI converts question to vector (1 API call)
4. **Vector Search**: Cosine similarity against stored vectors (local, fast)
5. **Smart Model Selection**: Complex calculations → Gemini Pro, Simple → Gemini Flash
6. **Answer Generation**: Context + enhanced question sent to selected model

### 3. **Vector Database: In-Memory Only**
- **No ChromaDB/Pinecone**: Uses simple Python arrays with NumPy
- **Storage**: Session state in Streamlit (resets on restart)
- **Search**: Pure cosine similarity calculation
- **Speed**: Very fast once embeddings are generated

### 4. **Multi-Model API Costs**

#### **Embedding Generation** (One-time per document)
- **Model**: `text-embedding-3-small`
- **Cost**: $0.00002 per 1K tokens
- **When**: App startup (cached until restart)
- **Volume**: 46 documents × average 200 tokens = ~$0.0002

#### **Answer Generation** (Per query) - Choose Your Model

| Model | Cost per Query | Best For | Speed |
|-------|---------------|----------|-------|
| **Gemini 1.5 Flash** | **$0.0003** | Simple queries | ⚡ Fast |
| **GPT-3.5-turbo** | $0.002 | General queries | 🚀 Fast |
| **Gemini 1.5 Pro** | $0.005 | Complex calculations | ⚡ Fast |
| **GPT-4** | $0.06 | Premium accuracy | 🐌 Slow |

**💡 Recommendation**: Use Gemini Flash as default (20x cheaper than GPT-3.5!)

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

### 7. **Cost Optimization (Already Implemented)**
- ✅ **Gemini Flash default**: 20x cheaper than GPT-3.5
- ✅ **Smart auto-routing**: Complex calculations use better models
- ✅ **Optimized token usage**: Reduced from 3K to 1.2K tokens
- ✅ **Context truncation**: Long documents capped at 400 chars
- ✅ **Default top_k=4**: Balanced accuracy vs cost
- ✅ **Batch embedding**: Single API call for all documents

## 📚 **Technical Deep Dive**

For a detailed explanation of what happens behind the scenes, including:
- Why you see 46+ API calls during startup
- How vector search actually works
- What gets sent to OpenAI and why
- Cost breakdown and optimization opportunities

**Read: [Behind the Scenes Technical Guide](behind_the_scenes.md)** 🔍

This document explains every log message, API call, and processing step in detail.

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
streamlit run app.py

# Test the application
python -m pytest tests/  # (if you add tests)
```

## Credits

**Built by:** [@maharajamandy](https://x.com/maharajamandy) & [@jockaayush](https://x.com/jockaayush)  
**Powered by:** OpenAI (GPT-4/3.5) + Google Gemini (Flash/Pro)  
**Framework:** Streamlit + Python  
**Cost Optimized:** Gemini Flash queries cost only $0.0003 each!