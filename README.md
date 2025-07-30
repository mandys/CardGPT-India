# CardGPT - Your Pocket-Sized Credit Card Expert ✨

A modern full-stack AI assistant for querying Indian credit card terms and conditions. Get instant answers about rewards, fees, eligibility, and spending optimization using natural language with ultra-low cost AI models.

**🚀 Live Demo**: [CardGPT India](https://card-gpt-india-vercel.app) | **📖 API Docs**: [Backend API](https://cardgpt-india-production.up.railway.app/docs)

## Table of Contents

- [Quick Start (3 Minutes)](#quick-start-3-minutes)
- [Architecture](#architecture)
- [Supported Credit Cards](#supported-credit-cards)
- [Features](#features)
- [Data Pipeline Setup](#data-pipeline-setup)
- [Development](#development)
- [Deployment](#deployment)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Cost Optimization](#cost-optimization)
- [Contributing](#contributing)

## Quick Start (3 Minutes)

### Prerequisites
- **Python 3.8+** and **Node.js 18+**
- **Gemini API Key** (required - ultra-low cost model)
- **Google Cloud Project** (for Vertex AI Search)
- **Database**: Auto-configured (SQLite locally, PostgreSQL in production)

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/credit-card-assistant.git
cd credit-card-assistant
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section)

./start_backend.sh
```

### 3. Frontend Setup
```bash
cd cardgpt-ui
npm install
./start_frontend.sh
```

### 4. Access Application
- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CardGPT                              │
├─────────────────────────────────────────────────────────────┤
│ React Frontend (Vercel)     │ FastAPI Backend (Railway)     │
│ • TypeScript + Tailwind     │ • Multi-model LLM service    │
│ • Responsive design         │ • Vertex AI Search           │
│ • Real-time streaming       │ • Smart query enhancement    │
│ • Cost tracking            │ • Hybrid database system     │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Data Pipeline     │
                    │ JSON → JSONL →    │
                    │ Google Cloud →    │
                    │ Vertex AI Search  │
                    └───────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Database Layer    │
                    │ SQLite (Local) +  │
                    │ PostgreSQL (Prod) │
                    └───────────────────┘
```

### Core Components

- **React Frontend**: Modern TypeScript React app with Tailwind CSS
- **FastAPI Backend**: RESTful API with automatic documentation
- **Hybrid Database System**: SQLite for local development, PostgreSQL for production
- **Vertex AI Search**: Enterprise-grade search with Google's managed infrastructure
- **Multi-Model LLM**: Gemini 2.5 Flash-Lite (ultra-low cost) + Pro models
- **Enhanced Query Processing**: Category detection, education fee fixes, improved context retrieval
- **Smart Calculator**: Precise calculations for rewards, milestones, and fees
- **Authentication System**: Google OAuth with session management and query limits

## Supported Credit Cards

| Card | Bank | Key Features | Best For |
|------|------|--------------|----------|
| **Atlas** | Axis Bank | 10X miles on travel, ₹1.5L milestone | Premium travel rewards |
| **EPM** | ICICI Bank | 6 points per ₹200, category caps | Reward points system |
| **Premier** | HSBC | Miles transfer, lounge access | Travel benefits |
| **Infinia** | HDFC Bank | 5 points per ₹150, luxury benefits | High-value spenders |

## Features

### 🤖 **AI-Powered Intelligence**
- **Gemini 2.5 Flash-Lite**: Ultra-low cost model (₹0.02/query)
- **Smart Comparisons**: AI-driven card recommendations
- **Complex Calculations**: Automatic milestone and spending analysis
- **Natural Language**: Ask questions in plain English

### 🎨 **Modern Interface**
- **Streaming Responses**: Real-time word-by-word generation
- **Mobile Responsive**: Collapsible sidebar, bottom navigation
- **Cost Transparency**: Live token usage and cost tracking
- **Dark/Light Theme**: Automatic theme switching

### 📊 **Advanced Analytics**
- **Category Detection**: Automatic spending category identification
- **Milestone Tracking**: Annual spend thresholds and bonuses
- **Multi-Card Comparison**: Side-by-side analysis
- **Optimization Suggestions**: Spending strategy recommendations

### 💡 **Smart Tips System**
- **Contextual Intelligence**: AI-powered tip suggestions based on user query context
- **12 Tip Categories**: Welcome, dining, travel, utility, insurance, rent, education, fuel, groceries, shopping, milestones, comparisons
- **Click-to-Query**: One-click tip activation - instantly turn suggestions into new queries
- **Smart Context Detection**: Advanced NLP analysis matches tips to user intent and interests
- **50+ Curated Tips**: Expert-crafted suggestions to help discover hidden features and optimization strategies
- **Beautiful UI**: Yellow gradient design with lightbulb icons for intuitive user experience
- **Responsive Design**: Seamlessly integrated with existing mobile-first interface

## Data Pipeline Setup

### 1. Prepare Credit Card Data
Place JSON files in the `data/` directory:
```
data/
├── axis-atlas.json      # Axis Bank Atlas card data
├── icici-epm.json       # ICICI EPM card data
├── hsbc-premier.json    # HSBC Premier card data
└── hdfc-infinia.json    # HDFC Infinia card data
```

### 2. Transform to JSONL Format
```bash
python transform_to_jsonl.py
# Creates: card_data.jsonl with complete data (card + common_terms sections)
# Enhanced with ~173 chunks (increased from ~90 chunks)
```

### 3. Upload to Google Cloud Storage
```bash
gsutil cp card_data.jsonl gs://your-bucket/card_data.jsonl
```

### 4. Configure Vertex AI Search
1. Go to [Vertex AI Search Console](https://console.cloud.google.com/ai/search)
2. Create new data store
3. Choose **Structured data (JSONL)** as data type
4. Import from your Cloud Storage bucket
5. Mark fields as **Filterable** (`cardName`) and **Retrievable** (`jsonData`)

### 5. Update Environment Variables
```bash
GOOGLE_CLOUD_PROJECT="your-project-id"
VERTEX_AI_DATA_STORE_ID="your-data-store-id"
```

## Development

### Environment Variables

Create `backend/.env`:
```bash
# Required
GEMINI_API_KEY="your-gemini-key-here"          # Ultra-low cost AI model
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"    # For Vertex AI Search
VERTEX_AI_DATA_STORE_ID="your-data-store-id"  # Search data store

# Database (Auto-configured)
# DATABASE_URL="postgresql://..."               # Railway auto-sets for production
# AUTH_DB_PATH="backend/auth.db"               # SQLite path for local dev

# Authentication (Production)
# JWT_SECRET="your-secure-jwt-secret"          # Required for production
# GOOGLE_CLIENT_ID="your-google-client-id"     # Required for Google OAuth

# Optional
VERTEX_AI_LOCATION="global"                    # Default: global
GUEST_DAILY_QUERY_LIMIT=5                     # Free queries for guests (default: 5)
```

### Local Development Commands

**Backend Development:**
```bash
cd backend
source venv/bin/activate

# Start with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_api.py

# Check models
python check_gemini_models.py
```

**Frontend Development:**
```bash
cd cardgpt-ui

# Development server
npm start

# Build for production
npm run build

# Type checking
npx tsc --noEmit
```

### File Structure

```
├── backend/                          # FastAPI Backend
│   ├── main.py                      # Application entry point
│   ├── auth.db                      # SQLite database (local development)
│   ├── api/                         # API endpoints
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── chat.py                  # Chat endpoint with streaming
│   │   ├── config.py                # Configuration endpoint
│   │   └── health.py                # Health check endpoint
│   ├── services/                    # Business logic services
│   │   ├── auth_service.py          # Hybrid database auth service
│   │   ├── llm.py                   # Multi-model LLM with enhanced prompts
│   │   ├── vertex_retriever.py      # Vertex AI Search service
│   │   ├── query_enhancer.py        # Enhanced query preprocessing
│   │   └── calculator.py            # Precise calculation engine
│   └── requirements.txt             # Python dependencies
├── cardgpt-ui/                      # React Frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── ChatInterface.tsx   # Main chat interface
│   │   │   ├── MessageBubble.tsx   # Chat message display
│   │   │   ├── TipDisplay.tsx      # Individual tip component
│   │   │   └── TipsContainer.tsx   # Smart tips container
│   │   ├── services/               # API and service layer
│   │   │   └── api.ts             # Backend API client
│   │   ├── hooks/                  # Custom React hooks
│   │   │   ├── useChat.ts         # Chat state management
│   │   │   └── useTips.ts         # Tips logic and state
│   │   ├── data/
│   │   │   └── tips.json          # Tips database (50+ contextual tips)
│   │   └── types/                  # TypeScript type definitions
│   └── package.json                # Node.js dependencies
├── data/                           # Credit card data (NOT committed)
│   ├── axis-atlas.json            # Axis Bank Atlas card data
│   ├── icici-epm.json             # ICICI EPM card data
│   ├── hsbc-premier.json          # HSBC Premier card data
│   └── hdfc-infinia.json          # HDFC Infinia card data
├── transform_to_jsonl.py           # Data pipeline transformation
└── README.md                       # Project documentation
```

### Adding New Credit Cards

1. **Create JSON file** in `data/` directory following the structure:
   ```json
   {
     "card": {
       "name": "Card Name",
       "bank": "Bank Name",
       "rewards": { /* reward structure */ },
       "milestones": { /* milestone benefits */ },
       "fees": { /* fee structure */ }
     }
   }
   ```

2. **Transform and upload**:
   ```bash
   python transform_to_jsonl.py
   gsutil cp card_data.jsonl gs://your-bucket/
   ```

3. **Update Vertex AI Search** data store with new JSONL file

4. **Restart application** to recognize new card

## Deployment

### Production Deployment

**Frontend (Vercel):**
```bash
cd cardgpt-ui
npm run build

# Deploy to Vercel
vercel --prod
```

**Backend (Railway):**
```bash
# Push to main branch - Railway auto-deploys
git push origin main
```

### Environment Variables (Production)

**Vercel Environment Variables:**
```
REACT_APP_API_URL=https://your-backend-url.up.railway.app
```

**Railway Environment Variables:**
```
GEMINI_API_KEY=your-gemini-key
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_DATA_STORE_ID=your-data-store-id
```

## Usage Examples

### Basic Queries
```
"What are the annual fees for credit cards?"
"Compare reward rates between Atlas and EPM"
"Which card has the best airport lounge access?"
```

### Calculation Queries
```
"How many miles for ₹2 lakh flight spend on Atlas?"
"Calculate rewards for ₹50K monthly expenses on EPM"
"Compare cash withdrawal fees across all cards"
```

### Complex Spending Analysis
```
"I spend ₹1L monthly: 20% rent, 30% groceries, 50% dining - which card is best?"
"Split ₹5L annual spend across travel and utilities for maximum rewards"
"What's the optimal card combination for ₹10L annual spend?"
```

### Expected Response Format
```
🧮 Detailed Calculation:

For ₹2L flight spend on Axis Atlas:
1. Base Rate: ₹2,00,000 ÷ ₹100 × 2 miles = 4,000 miles
2. Travel Bonus: ₹2,00,000 ÷ ₹100 × 10 miles = 20,000 miles  
3. Total: 24,000 EDGE Miles

Cost: ₹0.02 | Time: 2.3s | Model: Gemini 2.5 Flash-Lite
```

## API Reference

### Base URL
- **Local**: http://localhost:8000
- **Production**: https://cardgpt-india-production.up.railway.app

### Key Endpoints

```http
POST /api/chat
Content-Type: application/json

{
  "message": "How many miles for ₹1L spend?",
  "model": "gemini-2.5-flash-lite",
  "query_mode": "General Query",
  "top_k": 7
}
```

```http
GET /api/config
# Returns: Available models, supported cards, pricing

GET /api/health
# Returns: Service status, model availability
```

### Streaming API
```http
POST /api/chat/stream
Content-Type: application/json

# Returns: Server-Sent Events (SSE) stream
```

## Cost Optimization

### Model Cost Comparison (per 1K tokens)

| Model | Input Cost | Output Cost | Best For | Speed |
|-------|------------|-------------|----------|-------|
| **Gemini 2.5 Flash-Lite** | ₹0.008 | ₹0.03 | Simple queries | ⚡ Ultra Fast |
| Gemini 1.5 Flash | ₹0.006 | ₹0.02 | General queries | ⚡ Fast |
| Gemini 1.5 Pro | ₹0.10 | ₹0.40 | Complex analysis | 🚀 Powerful |

### Optimization Tips
- **Use Gemini 2.5 Flash-Lite** for 90% of queries (20x cheaper)
- **Adjust `top_k`** parameter (fewer docs = lower cost)
- **Batch similar questions** to reduce API calls
- **Monitor costs** with built-in tracking dashboard

## Contributing

### Development Workflow
```bash
# 1. Fork repository
git checkout -b feature/amazing-feature

# 2. Make changes
# Edit code, run tests, update docs

# 3. Test locally
cd backend && python test_api.py
cd cardgpt-ui && npm start

# 4. Submit PR
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

### Code Standards
- **TypeScript**: Strict mode enabled
- **Python**: Black formatting, type hints
- **API**: OpenAPI documentation required
- **Tests**: Add tests for new features

## Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check API keys
python -c "import os; print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY')[:10] + '...')"

# Test Vertex AI connection
python check_gemini_models.py

# Check database initialization
ls -la backend/auth.db  # Should exist after first run
```

**Database issues:**
```bash
# Local development - SQLite database missing
cd backend && python -c "from services.auth_service import AuthService; AuthService().test_database_connection()"

# Production - PostgreSQL connection issues
# Check Railway environment variables: DATABASE_URL, JWT_SECRET, GOOGLE_CLIENT_ID
```

**Education fee queries:**
```bash
# Test education fee accuracy
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do education fees earn rewards on Axis Atlas?", "model": "gemini-2.5-flash-lite"}'
# Should return: "2 EDGE Miles per ₹100 with 1% surcharge"
```

**Frontend build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

**Search returning 0 results:**
```bash
# Verify data store configuration
echo $VERTEX_AI_DATA_STORE_ID

# Check JSONL format and chunk count
wc -l card_data.jsonl  # Should show ~173 lines
head -n 1 card_data.jsonl | jq .
```

## Recent Major Improvements

### 🗄️ **Hybrid Database System (CRITICAL)**
- **Local Development**: Uses SQLite (`backend/auth.db`) - no PostgreSQL installation required
- **Production (Railway)**: Automatically uses PostgreSQL with connection pooling
- **Auto-Detection**: Environment automatically detected based on `DATABASE_URL` presence
- **Seamless Migration**: Zero-configuration transition from SQLite-only to hybrid system
- **Backward Compatibility**: Existing local development setups continue working unchanged

### 🎓 **Education Fee Query Fixes**
- **Critical Fix**: LLM no longer incorrectly assumes education fees are excluded
- **Axis Atlas Education**: 2 EDGE Miles per ₹100 with 1% surcharge (properly documented)
- **Enhanced System Prompt**: Added specific `AXIS ATLAS EDUCATION SPENDING` guidance
- **Query Enhancement**: Added education spending detection and enhancement rules

### 🔍 **Enhanced Search & Query Processing**
- **Increased Context**: Default `top_k` increased from 7 to 10 for better search retrieval
- **Complete Data Processing**: `transform_to_jsonl.py` now processes both "card" and "common_terms" sections
- **Improved JSONL**: 173 chunks (up from ~90) with complete fee and surcharge information
- **Fee Query Enhancement**: Better detection and retrieval of overlimit/late payment fees
- **System Prompt Strengthening**: Added `FEE AND CHARGE INFORMATION` section with explicit search instructions

### 🎯 **Smart Tips System**
- **Contextual Intelligence**: Advanced NLP-powered tip suggestions that analyze user queries for relevant follow-up questions
- **12 Tip Categories**: Comprehensive coverage across all credit card usage scenarios (dining, travel, utility, insurance, rent, education, fuel, groceries, shopping, milestones, comparisons, welcome)
- **Interactive UX**: Beautiful yellow gradient design with lightbulb icons and click-to-query functionality
- **Smart Integration**: Tips appear contextually after LLM responses with 50+ expert-curated suggestions
- **Performance Optimized**: Lightweight React components with efficient context detection algorithms

### 🚀 **Previous Updates (2025)**
- **Gemini 2.5 Flash-Lite Integration**: Ultra-low cost model with increased token limits (1200-1800 tokens)
- **Streaming Architecture**: Real-time word-by-word responses with status indicators
- **Token Limit Increases**: Enhanced capacity for complex multi-card comparisons
- **Query Enhancement Improvements**: Simplified approach focusing on system prompt guidance
- **Mobile-First Design**: Responsive interface with collapsible sidebar and bottom navigation

### 📊 **Evolution Timeline**
- **Started**: Supavec clone with Node.js backend
- **Phase 1**: Pure Python with Streamlit frontend
- **Phase 2**: Added Gemini models (20x cost reduction)
- **Phase 3**: Vertex AI Search integration (enterprise-grade)
- **Phase 4**: React + TypeScript frontend migration
- **Phase 5**: FastAPI backend with streaming responses
- **Phase 6**: Smart Tips System with contextual intelligence
- **Phase 7**: Hybrid database system with authentication
- **Phase 8**: Enhanced query processing and education fee fixes
- **Current**: Production-ready full-stack with hybrid database, enhanced AI accuracy, and intelligent user guidance

---

## Credits

**Built by:** [@maharajamandy](https://x.com/maharajamandy) & [@jockaayush](https://x.com/jockaayush)  
**Powered by:** Google Gemini + Vertex AI Search  
**Framework:** React + FastAPI + Python  

**🎯 Mission**: Experimenting with RAG and LLM technology for Indian fintech

---

*Get instant, AI-powered insights about Indian credit cards - compare, calculate, and optimize your spending strategy with intelligent contextual guidance!*