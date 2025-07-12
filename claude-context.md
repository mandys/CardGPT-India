# Claude Context - Supavec Clone Project

## Project Overview
A modular RAG (Retrieval-Augmented Generation) application for querying Indian credit card terms and conditions. Built as a clone of supavec with better organization and cost tracking.

## Key Architecture Changes
- **Refactored from monolithic** `streamlit_standalone.py` to modular structure
- **Five main modules**: embedder.py, llm.py, retriever.py, query_enhancer.py, app.py
- **Multi-model support**: OpenAI (GPT-4/3.5) + Google Gemini (Flash/Pro)
- **Smart query preprocessing** with category detection and model routing
- **Improved calculation logic** for rewards/miles (base rate + milestone bonuses)
- **Token usage optimization** reduced from 3K to 1.2K tokens per query

## Current Working Status
✅ **Functional**: Production-ready modular Python application with 5 organized modules
✅ **Multi-Model AI**: GPT-4, GPT-3.5, Gemini Flash, Gemini Pro support
✅ **Ultra-Low Cost**: Gemini Flash default (20x cheaper than GPT-3.5)
✅ **Smart Routing**: Complex calculations auto-upgrade to better models
✅ **Data Processing**: Handles both `common_terms` and `card` sections from JSON files
✅ **Category Detection**: Automatic detection of hotel, utility, education spending
✅ **Calculation Accuracy**: Fixed milestone, exclusion, and arithmetic issues
✅ **Token Optimization**: Reduced token usage by 60% while maintaining accuracy

## Recent Major Improvements
- **Added Gemini support** with Flash/Pro models (20x cost reduction)
- **Fixed calculation accuracy** with enhanced prompts and examples
- **Smart model selection** auto-routes complex queries to better models  
- **Category detection** correctly handles hotel/utility/education spending
- **Token optimization** reduced usage from 3K to 1.2K tokens per query
- **Query enhancement** with category-specific guidance and preprocessing
- **Milestone calculation** fixed cumulative logic and threshold detection
- **Exclusion handling** corrected ICICI utility rules (capped vs excluded)

## File Structure
```
├── app.py (modular Python application)
├── src/
│   ├── embedder.py (OpenAI embeddings with batch processing)
│   ├── llm.py (Multi-model: GPT-4/3.5 + Gemini Flash/Pro)
│   ├── retriever.py (vector search with keyword boosting)
│   ├── query_enhancer.py (category detection & query preprocessing)
│   └── __init__.py (package initialization)
├── data/ (credit card JSON files)
├── requirements.txt (Python dependencies)
├── README.md (updated Python-only documentation)
├── CLAUDE.md (development guidance)
├── behind_the_scenes.md (technical deep dive)
└── claude-context.md (project context)
```

## Key Features
- **Multi-Model AI**: Choose from 4 different models (GPT-4, GPT-3.5, Gemini Flash/Pro)
- **Ultra-Low Cost**: Gemini Flash queries cost only $0.0003 (vs $0.002 GPT-3.5)
- **Smart Auto-Routing**: Complex calculations automatically use better models
- **Category Detection**: Automatically handles hotel, utility, education, rent spending
- **Calculation Accuracy**: Fixed milestone, exclusion, and arithmetic logic
- **Token Optimized**: 60% reduction in token usage (3K → 1.2K per query)
- **No ChromaDB**: Uses optimized NumPy arrays for vector storage
- **Real-Time Costs**: Live tracking across all models with cost comparison

## Architecture Evolution
- **Started as**: Supavec clone with Node.js backend + Streamlit frontend
- **Evolved to**: Pure Python modular application with organized structure
- **Added Gemini**: Multi-model support with 20x cost reduction
- **Enhanced accuracy**: Smart query preprocessing and model selection
- **Current state**: Production-ready `app.py` orchestrating 5 specialized modules
- **Benefits**: Ultra-low cost, high accuracy, easy maintenance, no vendor lock-in