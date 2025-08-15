# Backend README

## Overview
**Role**: Python FastAPI backend that serves the React frontend with credit card query processing capabilities. This is a modern REST API with enterprise-grade Vertex AI Search integration, Gemini LLM processing, and Supabase PostgreSQL database.

**Architecture**: FastAPI + Vertex AI Search + Gemini 2.5 Flash-Lite + Supabase PostgreSQL + Clerk Authentication

## Key Files & Descriptions

### Core Application Files
- **`main.py`** - FastAPI application entry point, service initialization, CORS configuration, and environment management
- **`models.py`** - Pydantic data models for API requests/responses, input validation, and type safety
- **`requirements.txt`** - Python package dependencies including FastAPI, Google Cloud, Supabase, and ML libraries

### API Endpoints (`api/` folder)
- **`chat_stream.py`** - Main chat endpoint with streaming responses, query processing, and cost tracking
- **`preferences.py`** - User preference management with Clerk authentication and Supabase storage
- **`config.py`** - System configuration endpoints for frontend (models, cards, features)
- **`health.py`** - Health check and system status endpoints for monitoring
- **`query_limits.py`** - Rate limiting and usage tracking for guest/authenticated users
- **`admin.py`** - Administrative endpoints for system management
- **`cards.py`** - Credit card information and metadata endpoints

### Core Business Logic (`services/` folder)
- **`llm.py`** - **🎯 LLM prompts and text generation** - Modify system prompts, model selection, and response formatting here
- **`vertex_retriever.py`** - **🔍 Search results debug** - Vertex AI Search integration, document retrieval, and search result processing
- **`query_enhancer.py`** - **⚡ Query preprocessing** - Query enhancement, category detection, and search optimization before Vertex AI
- **`supabase_service.py`** - Database service for user data, preferences, analytics, and query logging
- **`preference_service.py`** - User preference management, personalization, and recommendation logic
- **`clerk_auth.py`** - Authentication service for JWT validation and user management
- **`card_config.py`** - Credit card configuration, aliases, and metadata management
- **`query_logger.py`** - GDPR-compliant query logging with data retention and anonymization

### Database & Configuration
- **`supabase_schema.sql`** - Complete database schema for Supabase PostgreSQL with RLS policies
- **`SUPABASE_MIGRATION_GUIDE.md`** - Database setup and migration instructions
- **`.env.local`** - Development environment variables (Supabase, Gemini, Clerk keys)
- **`.env.production`** - Production environment configuration

### Scripts & Utilities
- **`start_backend.sh`** - Development server startup script with environment loading
- **`check_gemini_models.py`** - Utility to test Gemini API connectivity and list available models
- **`test_clerk_auth.py`** - Authentication testing and JWT validation verification

## Quick Access Tips

### For Prompt Engineering & LLM Behavior
- **System prompts**: `services/llm.py` (lines 252-325) - Modify the `_create_system_prompt()` method
- **Model selection**: `services/llm.py` (lines 42-47) - Update model pricing and specifications
- **Response formatting**: `services/llm.py` (lines 327-344) - Adjust user prompt and calculation instructions

### For Search & Retrieval Issues
- **Search debugging**: `services/vertex_retriever.py` (lines 90-310) - Enable detailed search logging and result analysis
- **Query enhancement**: `services/query_enhancer.py` (lines 128-181) - Modify category detection and query preprocessing
- **Card mapping**: `services/card_config.py` - Update credit card aliases and display names

### For Database & User Management
- **User preferences**: `services/preference_service.py` - Modify preference storage and retrieval logic
- **Authentication**: `services/clerk_auth.py` - JWT validation and user ID extraction
- **Database queries**: `services/supabase_service.py` - Raw SQL operations and connection management

### For API Endpoints & Features
- **Chat functionality**: `api/chat_stream.py` - Main query processing and streaming response logic
- **Rate limiting**: `api/query_limits.py` - Guest/user query limits and usage tracking
- **Configuration**: `api/config.py` - Frontend configuration and feature flags

## Environment Setup

### Required Environment Variables
```bash
# Supabase Database (Required)
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-service-role-key"
ENVIRONMENT="development"  # or "production"

# Google AI & Search (Required)
GEMINI_API_KEY="your-gemini-api-key"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
VERTEX_AI_DATA_STORE_ID="your-vertex-data-store-id"

# Clerk Authentication (Required)
CLERK_SECRET_KEY="sk_test_your-clerk-secret"
REACT_APP_CLERK_PUBLISHABLE_KEY="pk_test_your-clerk-key"

# Optional Configuration
GUEST_DAILY_QUERY_LIMIT=2
ENABLE_QUERY_LOGGING=true
GDPR_COMPLIANCE_MODE=true
```

### Quick Start (3 Minutes)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env.local
# Edit .env.local with your actual keys

# 3. Initialize Supabase database
# Follow SUPABASE_MIGRATION_GUIDE.md

# 4. Start development server
./start_backend.sh
# OR
python main.py
```

### Development Commands
```bash
# Start server with auto-reload
python main.py

# Test API connectivity
curl http://localhost:8000/api/health

# Test Gemini models
python check_gemini_models.py

# Test authentication
python test_clerk_auth.py

# Check database connection
python -c "from services.supabase_service import SupabaseService; s=SupabaseService(); print(f'Connected: {s.test_connection()}')"
```

## API Documentation
- **Interactive docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)
- **Health check**: http://localhost:8000/api/health

## Common Issues & Troubleshooting

### Authentication Issues
- **"Clerk authentication not configured"**: Check CLERK_SECRET_KEY in .env.local
- **JWT validation errors**: Verify REACT_APP_CLERK_PUBLISHABLE_KEY matches frontend

### Database Connection Issues
- **Supabase connection failed**: Verify SUPABASE_URL and SUPABASE_KEY
- **Environment detection**: Ensure ENVIRONMENT="development" is set

### Search & AI Issues
- **No search results**: Check VERTEX_AI_DATA_STORE_ID and Google Cloud authentication
- **Gemini API errors**: Verify GEMINI_API_KEY and run check_gemini_models.py
- **Query enhancement issues**: Enable logging in query_enhancer.py for debugging

### Performance Issues
- **Slow responses**: Check Vertex AI Search logs in vertex_retriever.py
- **Memory usage**: Monitor Supabase connection pooling
- **Rate limiting**: Review query_limits.py for usage patterns

## Architecture Notes

### Request Flow
1. **Frontend** → FastAPI endpoint (`api/chat_stream.py`)
2. **Authentication** → Clerk JWT validation (`services/clerk_auth.py`)
3. **Query Enhancement** → Category detection and preprocessing (`services/query_enhancer.py`)
4. **Search** → Vertex AI Search document retrieval (`services/vertex_retriever.py`)
5. **LLM Processing** → Gemini 2.5 Flash-Lite generation (`services/llm.py`)
6. **Response** → Streaming JSON response to frontend

### Database Design
- **PostgreSQL** with Supabase managed infrastructure
- **Row Level Security (RLS)** for user data protection
- **GDPR compliance** with automatic data anonymization
- **Real-time capabilities** for future features

### Cost Optimization
- **Gemini 2.5 Flash-Lite**: Ultra-low cost model (₹0.02/query)
- **Vertex AI Search**: Enterprise-grade with predictable pricing
- **Supabase**: Managed PostgreSQL with generous free tier

This backend provides a production-ready foundation for credit card query processing with enterprise-grade reliability and cost optimization.