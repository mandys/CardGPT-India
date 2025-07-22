# Credit Card Assistant - AI-Powered Indian Credit Card Advisor

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
│                     Credit Card Assistant                    │
├─────────────────────────────────────────────────────────────┤
│ React Frontend (Vercel)     │ FastAPI Backend (Railway)     │
│ • TypeScript + Tailwind     │ • Multi-model LLM service    │
│ • Responsive design         │ • Vertex AI Search           │
│ • Real-time streaming       │ • Smart query enhancement    │
│ • Cost tracking            │ • Precise calculations       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Data Pipeline     │
                    │ JSON → JSONL →    │
                    │ Google Cloud →    │
                    │ Vertex AI Search  │
                    └───────────────────┘
```

### Core Components

- **React Frontend**: Modern TypeScript React app with Tailwind CSS
- **FastAPI Backend**: RESTful API with automatic documentation
- **Vertex AI Search**: Enterprise-grade search with Google's managed infrastructure
- **Multi-Model LLM**: Gemini 2.5 Flash-Lite (ultra-low cost) + Pro models
- **Query Enhancement**: Automatic category detection and preprocessing
- **Smart Calculator**: Precise calculations for rewards, milestones, and fees

## Supported Credit Cards

| Card | Bank | Key Features | Best For |
|------|------|--------------|----------|
| **Atlas** | Axis Bank | 10X miles on travel, ₹1.5L milestone | Premium travel rewards |
| **EPM** | ICICI Bank | 6 points per ₹200, category caps | Reward points system |
| **Premier** | HSBC | Miles transfer, lounge access | Travel benefits |

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

## Data Pipeline Setup

### 1. Prepare Credit Card Data
Place JSON files in the `data/` directory:
```
data/
├── axis-atlas.json      # Axis Bank Atlas card data
├── icici-epm.json       # ICICI EPM card data
└── hsbc-premier.json    # HSBC Premier card data
```

### 2. Transform to JSONL Format
```bash
python transform_to_jsonl.py
# Creates: card_data.jsonl
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

# Optional
VERTEX_AI_LOCATION="global"                    # Default: global
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

# Check JSONL format
head -n 1 card_data.jsonl | jq .
```

---

## Credits

**Built by:** [@maharajamandy](https://x.com/maharajamandy) & [@jockaayush](https://x.com/jockaayush)  
**Powered by:** Google Gemini + Vertex AI Search  
**Framework:** React + FastAPI + Python  

**🎯 Mission**: Experimenting with RAG and LLM technology for Indian fintech

---

*Get instant, AI-powered insights about Indian credit cards - compare, calculate, and optimize your spending strategy!*