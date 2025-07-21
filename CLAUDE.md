# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an enhanced supavec clone built for RAG/Multi-Model LLM applications to query Indian credit card data. Features enterprise-grade Vertex AI Search, ultra-low cost Gemini integration (20x cheaper), smart query preprocessing, and production-ready accuracy improvements with zero maintenance overhead.

## Data Structure

The project contains credit card data in JSON format in the `/data` directory:
- `axis-atlas.json` - Axis Bank Atlas credit card terms and conditions
- `icici-epm.json` - ICICI Bank credit card terms and conditions
- `hsbc-premier.json` - HSBC Premier credit card terms and conditions

Each JSON file contains structured data with:
- `common_terms` - Standard credit card terms like interest rates, fees, and policies
- `card` - Card-specific information including rewards, fees, milestones, renewal benefits
- Detailed information about finance charges, surcharge fees, cash withdrawal policies
- Reward points policies, renewal benefits, and card management rules

## Architecture

Enhanced supavec architecture with enterprise-grade improvements:
- **Vertex AI Search**: Google's managed search infrastructure (primary)
- **ChromaDB Fallback**: Reliable backup system with vector search
- **Multi-Model Support**: OpenAI (GPT-4/3.5) + Google Gemini (Flash/Pro)
- **Smart Query Enhancement**: Category detection and preprocessing
- **RAG Pipeline**: Intelligent responses with model auto-selection
- **Cost Optimization**: 20x cost reduction with Gemini Flash
- **Calculation Accuracy**: Fixed milestone and exclusion logic
- **Zero Maintenance**: Eliminated prompt tuning and chunking cycles

## Key Features Implemented

1. ✅ **Vertex AI Search**: Google's enterprise-grade search infrastructure
2. ✅ **Production-Ready Architecture**: No local file dependencies for deployment
3. ✅ **Multi-Model AI**: Support for Gemini Flash, Gemini Pro (Google-only architecture)
4. ✅ **Enhanced LLM Calculations**: Step-by-step math with detailed breakdowns
5. ✅ **Smart Query Enhancement**: Category detection and model routing
6. ✅ **Semantic Search**: Natural language queries with keyword boosting
7. ✅ **RAG Pipeline**: Context retrieval + intelligent calculation enhancement
8. ✅ **Cost Optimization**: 60% token reduction + 20x cheaper Gemini option
9. ✅ **Single Source of Truth**: All data from Vertex AI Search (no JSON dependencies)
10. ✅ **Zero Maintenance**: Eliminated prompt tuning and chunking strategy cycles
11. ✅ **Enterprise Reliability**: 99.9% uptime with Google's managed infrastructure
12. ✅ **Deployment Ready**: Works on Vercel/Railway without data file requirements

## Development Commands

### Python Application
- `pip install -r requirements.txt` - Install Python dependencies (includes Gemini + Vertex AI)
- `streamlit run app.py` - Run the production-ready RAG application
- `export OPENAI_API_KEY="your-key"` - Set OpenAI API key (required)
- `export GEMINI_API_KEY="your-key"` - Set Gemini API key (optional, 20x cheaper)
- `export GOOGLE_CLOUD_PROJECT="your-project"` - Set GCP project (optional, enables Vertex AI)
- `export VERTEX_AI_DATA_STORE_ID="your-data-store"` - Set Vertex AI data store ID
- `gcloud auth application-default login` - Authenticate with Google Cloud
- Default model: **Gemini 1.5 Flash** (ultra-low cost, good accuracy)
- Default search: **Vertex AI Search** (enterprise-grade, zero maintenance)

## Data Query Examples

The system supports enhanced queries with smart preprocessing:
- **Category Detection**: "What rewards for ₹50K utility spend?" → detects utility category
- **Calculation Queries**: "For ₹1L hotel spend on Atlas?" → enhanced LLM with step-by-step math
- **Comparisons**: "Compare cash withdrawal fees between cards" → ensures both cards discussed
- **Spend Distribution**: "Split ₹1L across rent, food, travel - which card better?" → category-wise analysis
- **Complex Calculations**: Enhanced LLM prompts with detailed calculation breakdowns

## LLM-Powered Calculations

Calculation queries now use enhanced LLM prompts instead of local calculator:
- **Step-by-step Math**: Detailed breakdown with arithmetic verification
- **Cap Handling**: Automatic detection and application of earning caps
- **Milestone Logic**: Annual spend thresholds and bonus calculations
- **Surcharge Calculation**: 1% fees on amounts above thresholds
- **Format**: "🧮 Detailed Calculation:" with numbered steps and final summary

## Extension Points

To add new credit card data:
1. Add JSON files to the `/data` directory
2. Follow the existing structure with `common_terms` and detailed policies
3. **Vertex AI Search**: Upload new data to Google Cloud Discovery Engine
4. **ChromaDB Fallback**: The system will automatically detect and ingest new files
5. **No maintenance required**: Vertex AI handles indexing and optimization automatically

## Data Files & Privacy Protection

### Data Files Not in Repository
- **data/*.json** - Credit card data files are NOT committed to git (IP protection)
- ***.jsonl** - Training data files are NOT committed to git  
- **backend/exports/** - Query log exports are NOT committed to git (privacy protection)

### Local Development Setup
- Data files must be present locally in `data/` directory for development
- See `data/README.md` for complete setup instructions
- Contact project maintainers for access to the cleaned data files

### Important: Never Commit
- Credit card JSON files (valuable cleaned data from PDFs)
- JSONL training files (used for Google bucket uploads)
- Export files from query logging (contain user data)

## Maintenance Tasks

- keep @CLAUDE.md @README.md @behind_the_scenes.md @claude-context.md updated at all times
- Always do a git add/commit of code when updating core functionality documentation files
- Ensure all memory files are consistently updated with new project features and changes
- Verify sensitive data files are not accidentally committed

## Commit Guidelines

- Do not mention Claude as a contributor in commit messages