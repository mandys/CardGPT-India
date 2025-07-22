# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 IMPORTANT RULES

### Commit Guidelines
- **NEVER mention Claude as a contributor in commit messages**
- Use neutral language like "Generated with [Claude Code](https://claude.ai/code)" in commit footers
- Focus commit messages on the actual changes, not the tool used

### Documentation Maintenance
- **Always keep README.md updated** after feature additions/editing
- Update this CLAUDE.md file when project architecture changes significantly
- Ensure documentation reflects current state, not historical implementations

## Project Overview

A modern full-stack RAG (Retrieval-Augmented Generation) application for querying Indian credit card terms and conditions. Built as an enhanced supavec clone with enterprise-grade Vertex AI Search, featuring React + TypeScript frontend with FastAPI backend.

**Current Architecture**: React frontend (Vercel) + FastAPI backend (Railway) + Vertex AI Search + Gemini 2.5 Flash-Lite

## Core Architecture

### Frontend: React + TypeScript
- **Location**: `cardgpt-ui/` directory
- **Deployment**: Vercel (https://card-gpt-india-vercel.app)
- **Features**: Responsive design, streaming responses, cost tracking
- **Tech Stack**: React 18, TypeScript, Tailwind CSS, Zustand

### Backend: FastAPI Python
- **Location**: `backend/` directory  
- **Deployment**: Railway (https://cardgpt-india-production.up.railway.app)
- **API Docs**: `/docs` endpoint with OpenAPI documentation
- **Services**: LLM, Vertex AI Search, Query Enhancement, Calculator

### Data Pipeline
1. **Source**: JSON files in `data/` directory (not committed)
2. **Transform**: `transform_to_jsonl.py` creates `card_data.jsonl`
3. **Upload**: Google Cloud Storage bucket
4. **Index**: Vertex AI Search data store
5. **Query**: Enterprise-grade search with auto-chunking

## Supported Credit Cards

- **Axis Atlas**: Premium miles card (10X travel, ₹1.5L milestone)
- **ICICI EPM**: Emeralde Private Metal (6 points per ₹200, category caps)
- **HSBC Premier**: Miles transfer and comprehensive travel benefits

## Key Features Implemented

### ✅ AI & Search Infrastructure
- **Gemini 2.5 Flash-Lite**: Ultra-low cost model (₹0.02/query)
- **Vertex AI Search**: Google's enterprise-grade search infrastructure
- **Smart Query Enhancement**: Category detection and preprocessing
- **Multi-Model Support**: Gemini Flash/Pro with automatic routing
- **Streaming Responses**: Real-time word-by-word text generation

### ✅ Full-Stack Architecture
- **React Frontend**: Complete UI control, responsive design
- **FastAPI Backend**: RESTful API with auto-documentation
- **TypeScript**: Full type safety and developer experience
- **Tailwind CSS**: Utility-first styling with mobile-first approach
- **Production Deployment**: Vercel + Railway with CI/CD

### ✅ Advanced Features
- **Cost Optimization**: 60% token reduction, 20x cheaper than traditional models
- **Calculation Accuracy**: Step-by-step math with milestone logic
- **Category Detection**: Hotel, utility, education, rent spending
- **Responsive Design**: Collapsible sidebar, bottom navigation
- **Debug Transparency**: Cost breakdown and source documents

## Development Commands

### Quick Start (3 Minutes)
```bash
# Backend
cd backend && pip install -r requirements.txt && ./start_backend.sh

# Frontend  
cd cardgpt-ui && npm install && ./start_frontend.sh
```

### Environment Variables Required
```bash
# Required
GEMINI_API_KEY="your-gemini-key-here"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
VERTEX_AI_DATA_STORE_ID="your-data-store-id"
```

### Data Pipeline Setup
```bash
# Transform data
python transform_to_jsonl.py

# Upload to Google Cloud
gsutil cp card_data.jsonl gs://your-bucket/

# Configure Vertex AI Search data store
# Mark cardName as Filterable, jsonData as Retrievable
```

## Query Examples & Capabilities

### Smart Category Detection
- "What rewards for ₹50K utility spend?" → detects utility category
- "For ₹1L hotel spend on Atlas?" → enhanced LLM with step-by-step math
- "Split ₹1L across rent, food, travel - which card better?" → category-wise analysis

### Complex Calculations  
- **Step-by-step Math**: Detailed breakdown with arithmetic verification
- **Cap Handling**: Automatic detection and application of earning caps
- **Milestone Logic**: Annual spend thresholds and bonus calculations
- **Format**: "🧮 Detailed Calculation:" with numbered steps and final summary

### Multi-Card Comparisons
- "Compare cash withdrawal fees between cards" → ensures all cards discussed
- "Axis Atlas vs ICICI EPM for ₹2L monthly spend" → side-by-side analysis

## File Structure

```
├── backend/                    # FastAPI Backend
│   ├── main.py                # Entry point
│   ├── api/                   # Endpoints (chat, config, health)
│   ├── services/              # Business logic (LLM, search, calculator)
│   └── requirements.txt       # Python dependencies
├── cardgpt-ui/                # React Frontend
│   ├── src/components/        # React components
│   ├── src/services/          # API client
│   ├── src/hooks/            # State management
│   └── package.json          # Node.js dependencies
├── data/                     # Credit card JSON files (NOT committed)
├── transform_to_jsonl.py     # Data pipeline script
└── README.md                 # Main documentation (KEEP UPDATED)
```

## Data Security & Privacy

### Files NOT Committed to Git
- **data/*.json** - Credit card data files (IP protection)
- ***.jsonl** - Training data files
- **backend/exports/** - Query log exports (privacy protection)

### Sensitive Data Handling
- Never commit API keys or credentials
- Credit card data files must be obtained separately
- Query logs contain user data - privacy protected

## Development Workflow

### Adding New Features
1. **Plan**: Update this CLAUDE.md if architecture changes
2. **Develop**: Make changes in appropriate frontend/backend
3. **Test**: Run local tests and verify functionality  
4. **Document**: **Always update README.md** with new features
5. **Commit**: Follow commit guidelines (no Claude mentions)
6. **Deploy**: Push triggers automatic deployment

### Adding New Credit Cards
1. Create JSON file in `data/` directory (follow existing structure)
2. Run `python transform_to_jsonl.py` 
3. Upload JSONL to Google Cloud Storage
4. Update Vertex AI Search data store
5. **Update README.md** with new card information
6. Restart application to recognize new card

## Current Status & Performance

### ✅ Production Ready
- **Frontend**: Deployed on Vercel with streaming UI
- **Backend**: Deployed on Railway with auto-scaling
- **Search**: Vertex AI Search with 99.9% uptime
- **Models**: Gemini 2.5 Flash-Lite default (ultra-low cost)

### Performance Metrics
- **Query Response**: 1-3 seconds average
- **Cost per Query**: ₹0.02 (Gemini 2.5 Flash-Lite)
- **Token Usage**: 60% reduction (3K → 1.2K per query)
- **Uptime**: 99.9% with Google's managed infrastructure

## Troubleshooting

### Common Issues
- **Search returns 0 results**: Check VERTEX_AI_DATA_STORE_ID configuration
- **Frontend build errors**: Clear node_modules, reinstall dependencies
- **Backend not starting**: Verify GEMINI_API_KEY is set correctly
- **CORS errors**: Ensure backend is running before frontend

### Debug Commands
```bash
# Check models available
python backend/check_gemini_models.py

# Test API connectivity  
curl http://localhost:8000/api/health

# Verify environment
echo $GEMINI_API_KEY | head -c 10
```

## Maintenance Tasks

### Regular Updates
- **README.md**: Update after every significant feature addition
- **API Documentation**: Ensure OpenAPI docs reflect current endpoints
- **Dependencies**: Keep requirements.txt and package.json updated
- **Environment**: Verify all required environment variables documented

### Code Quality
- **TypeScript**: Maintain strict mode, resolve all type errors
- **Python**: Use type hints, follow PEP 8 standards
- **Testing**: Add tests for new functionality
- **Documentation**: Keep inline comments updated

---

## Recent Major Improvements Archive

### 🚀 Latest Updates (July 2025)
- **Gemini 2.5 Flash-Lite Integration**: Ultra-low cost model with increased token limits
- **Documentation Consolidation**: Single comprehensive README.md
- **Token Limit Increases**: 1800 tokens for complex comparisons
- **Query Simplification**: Fixed complex query processing for Vertex AI
- **Streaming Architecture**: Real-time responses with status indicators

### 📊 Evolution Timeline  
- **Started**: Supavec clone with Node.js backend
- **Phase 1**: Pure Python with Streamlit frontend
- **Phase 2**: Added Gemini models (20x cost reduction)  
- **Phase 3**: Vertex AI Search integration (enterprise-grade)
- **Phase 4**: React + TypeScript frontend migration
- **Phase 5**: FastAPI backend with streaming responses
- **Current**: Production-ready full-stack with ultra-low cost AI

This project demonstrates successful implementation of modern RAG architecture with enterprise reliability and ultra-low operational costs.