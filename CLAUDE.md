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
- **Database**: Hybrid system - SQLite (local) + PostgreSQL (production)
- **Services**: LLM, Vertex AI Search, Query Enhancement, Calculator, Authentication

### Data Pipeline
1. **Source**: JSON files in `data/` directory (not committed)
2. **Transform**: `transform_to_jsonl.py` creates `card_data.jsonl` (1023 chunks with standardized category data)
3. **Upload**: Google Cloud Storage bucket
4. **Index**: Vertex AI Search data store
5. **Query**: Enterprise-grade search with enhanced context retrieval (top_k=10)

## Supported Credit Cards

- **Axis Atlas**: Premium miles card (10X travel, ₹1.5L milestone)
- **ICICI EPM**: Emeralde Private Metal (6 points per ₹200, category caps)
- **HSBC Premier**: Miles transfer and comprehensive travel benefits
- **HDFC Infinia**: Ultra-premium card (5 points per ₹150, luxury benefits)

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
- **Hybrid Database System**: Auto-detects environment (SQLite local, PostgreSQL production)
- **Enhanced Query Processing**: Fixed education fee queries, improved context retrieval
- **Cost Optimization**: 60% token reduction, 20x cheaper than traditional models
- **Calculation Accuracy**: Step-by-step math with milestone logic
- **Category Detection**: Hotel, utility, education, rent spending (with improved education handling)
- **Authentication System**: Google OAuth with session management and query limits
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

# Database (Auto-configured)
# DATABASE_URL="postgresql://..."  # Railway auto-sets for production
# AUTH_DB_PATH="backend/auth.db"   # Local SQLite path (auto-created)

# Authentication (Production only)
# JWT_SECRET="secure-secret-here"
# GOOGLE_CLIENT_ID="your-google-client-id"
```

### Data Pipeline Setup
```bash
# Transform data (now processes both card and common_terms sections + standardized categories)
python transform_to_jsonl.py
# Creates 1023 chunks with complete fee, surcharge, and category information

# Upload to Google Cloud
gsutil cp card_data.jsonl gs://your-bucket/

# Configure Vertex AI Search data store
# Mark cardName as Filterable, jsonData as Retrievable
```

## Query Examples & Capabilities

### Smart Category Detection
- "What rewards for ₹50K utility spend?" → detects utility category
- "For ₹1L hotel spend on Atlas?" → enhanced LLM with step-by-step math
- "Do education fees earn rewards on Atlas?" → correctly identifies education category (FIXED)
- "Which cards give points on gold purchases?" → standardized gold/jewellery category analysis
- "Compare government payment rewards across all cards" → detailed government/tax category breakdown
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
│   ├── main.py                # Entry point with hybrid database initialization
│   ├── auth.db                # SQLite database (local development)
│   ├── api/                   # Endpoints (chat, config, health, auth)
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat.py            # Enhanced chat with education fee fixes
│   │   └── ...
│   ├── services/              # Business logic services
│   │   ├── auth_service.py    # Hybrid database auth service
│   │   ├── llm.py             # Enhanced system prompts
│   │   ├── vertex_retriever.py # Enhanced search (top_k=10)
│   │   └── query_enhancer.py  # Education category enhancements
│   └── requirements.txt       # Python dependencies
├── cardgpt-ui/                # React Frontend
│   ├── src/components/        # React components
│   ├── src/services/          # API client
│   ├── src/hooks/            # State management
│   └── package.json          # Node.js dependencies
├── data/                      # Credit card JSON files (NOT committed)
├── transform_to_jsonl.py      # Enhanced data pipeline (v2.0 with versioning)
├── incremental_update.py      # Smart delta generation system
├── generate_faq.py           # FAQ system generator
├── faq-common-questions.jsonl # Pre-built comparison answers
└── README.md                  # Main documentation (KEEP UPDATED)
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
- **Database initialization errors**: Check if Railway PostgreSQL is properly configured or SQLite permissions for local dev
- **Education fee queries incorrect**: System now properly handles education spending (2 EDGE Miles per ₹100 with 1% surcharge on Atlas)
- **Search returns 0 results**: Check VERTEX_AI_DATA_STORE_ID configuration and verify JSONL has 1023 chunks
- **Authentication failures**: Verify JWT_SECRET and GOOGLE_CLIENT_ID are set in production
- **Frontend build errors**: Clear node_modules, reinstall dependencies
- **Backend not starting**: Verify GEMINI_API_KEY is set correctly
- **CORS errors**: Ensure backend is running before frontend

### Debug Commands
```bash
# Check models available
python backend/check_gemini_models.py

# Test API connectivity  
curl http://localhost:8000/api/health

# Test database connection
cd backend && python -c "from services.auth_service import AuthService; print(f'Database type: {AuthService().database_type}'); print(f'Tables exist: {AuthService().test_database_connection()}')"

# Test education fee query accuracy
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do education fees earn rewards on Axis Atlas?", "model": "gemini-2.5-flash-lite"}'

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

### 🎯 **Phase 4: Category Standardization Complete (CRITICAL - August 2025)**
- **Problem Solved**: Eliminated all hardcoded responses for category queries in query_enhancer.py
- **6 Categories Standardized**: education, fuel, utility, rent, gold/jewellery, government/tax
- **Data Architecture Transformation**: 1023 chunks (up from 173 chunks - 488% increase)
- **Pure RAG System**: All category queries now use retrieval-based answers with 8-12 granular chunks per category
- **Comprehensive Coverage**: Each spending category has complete earning rates, exclusions, surcharges, and caps data
- **Query Examples Working**: "Which cards give points on gold purchases?", "Compare government payment rewards"
- **Reference**: See `plans/category_standardization_plan.md` for complete implementation details

### 🚀 **Phase 5: Infrastructure Improvements Complete (CRITICAL - August 2025)**
- **Problem Solved**: 20-30 minute downtime for JSON file updates reduced to <5 minutes (83% reduction)
- **Incremental Update System**: Smart delta generation with hash-based change detection
- **FAQ System**: 8 pre-built comparison answers with 85-95% confidence for complex queries
- **Versioning Framework**: v2.0 format with comprehensive metadata tracking (updated_at, version, content_hash)
- **Smart Tools Created**:
  - `incremental_update.py`: Delta generation system with `--check-changes` preview
  - `generate_faq.py`: FAQ system generator with validation
  - Enhanced `transform_to_jsonl.py`: Version 2.0 with metadata
- **Zero-Downtime Updates**: Change single JSON file, system updates only affected chunks
- **Operational Benefits**: Automated change detection, selective updates, production-ready infrastructure

### 🗄️ **Hybrid Database System (CRITICAL - July 2025)**
- **Local Development**: SQLite database (`backend/auth.db`) - zero configuration required
- **Production (Railway)**: Automatic PostgreSQL detection and connection pooling
- **Auto-Detection**: Environment detection based on `DATABASE_URL` presence
- **Backward Compatibility**: Existing local setups continue working unchanged
- **Migration Path**: Seamless transition from SQLite-only to hybrid system

### 🎓 **Education Fee Query Fixes (CRITICAL)**
- **Root Cause Fixed**: LLM no longer incorrectly assumes education fees are excluded
- **Axis Atlas Accuracy**: 2 EDGE Miles per ₹100 with 1% surcharge properly documented
- **Enhanced System Prompt**: Added `AXIS ATLAS EDUCATION SPENDING` section with specific guidance
- **Query Enhancement**: Education category detection and enhancement rules

### 🔍 **Enhanced Search & Data Processing (Superseded by Phase 4)**
- **Increased Context**: Default `top_k` increased from 7 to 10 for better search results
- **Complete Data Pipeline**: `transform_to_jsonl.py` now processes both "card" and "common_terms" sections
- **Enhanced JSONL**: Now 1023 chunks (up from initial ~90) with complete category standardization
- **Fee Query Enhancement**: Better detection and retrieval of overlimit/late payment fees
- **System Prompt Updates**: Added `FEE AND CHARGE INFORMATION` section
- **Note**: This phase was succeeded by Phase 4 Category Standardization for comprehensive category coverage

### 🚀 **Previous Updates (July 2025)**
- **Gemini 2.5 Flash-Lite Integration**: Ultra-low cost model with increased token limits (1200-1800)
- **Documentation Consolidation**: Single comprehensive README.md
- **Token Limit Increases**: Enhanced capacity for complex multi-card comparisons
- **Query Enhancement Simplification**: Removed complex enhancements, focus on system prompt guidance
- **Streaming Architecture**: Real-time responses with status indicators

### 📊 Evolution Timeline  
- **Started**: Supavec clone with Node.js backend
- **Phase 1**: Pure Python with Streamlit frontend
- **Phase 2**: Added Gemini models (20x cost reduction)  
- **Phase 3**: Vertex AI Search integration (enterprise-grade)
- **Phase 4**: React + TypeScript frontend migration
- **Phase 5**: FastAPI backend with streaming responses
- **Phase 6**: Smart Tips System with contextual intelligence
- **Phase 7**: Hybrid database system with authentication
- **Phase 8**: Enhanced query processing and education fee fixes
- **Phase 9**: Category Standardization (6 categories, 1023 chunks, zero hardcoded responses)
- **Phase 10**: Infrastructure Improvements (incremental updates, FAQ system, 83% downtime reduction)
- **Current**: Production-ready full-stack with standardized categories, intelligent infrastructure, and zero-downtime updates

This project demonstrates successful implementation of modern RAG architecture with enterprise reliability and ultra-low operational costs.