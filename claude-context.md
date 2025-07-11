# Claude Context - Supavec Clone Project

## Project Overview
A modular RAG (Retrieval-Augmented Generation) application for querying Indian credit card terms and conditions. Built as a clone of supavec with better organization and cost tracking.

## Key Architecture Changes
- **Refactored from monolithic** `streamlit_standalone.py` to modular structure
- **Four main modules**: embedder.py, llm.py, retriever.py, app.py
- **Improved calculation logic** for rewards/miles (base rate + milestone bonuses)
- **Token usage tracking** and cost optimization features

## Current Working Status
✅ **Functional**: Single modular Python application (`app.py`) with organized `src/` modules
✅ **Data Processing**: Handles both `common_terms` and `card` sections from JSON files
✅ **Cost Tracking**: Real-time token usage and pricing display
✅ **Model Selection**: GPT-4 vs GPT-3.5-turbo cost optimization
✅ **Category-specific rates**: Enhanced prompts for travel vs general spending calculations

## Recent Bug Fixes
- Fixed category-specific earning rates (hotels/flights get 5 EM vs 2 EM base rate)
- Enhanced prompts to handle travel vs general spending properly
- Fixed conservative category detection to avoid assuming travel spending
- Improved example questions with better templates
- Cleaned up repository by removing obsolete Node.js files

## File Structure
```
├── app.py (modular Python application)
├── src/
│   ├── embedder.py (OpenAI embeddings with batch processing)
│   ├── llm.py (GPT-4/3.5 responses with category-aware prompts)
│   ├── retriever.py (vector search with keyword boosting)
│   └── __init__.py (package initialization)
├── data/ (credit card JSON files)
├── requirements.txt (Python dependencies)
├── README.md (updated Python-only documentation)
├── CLAUDE.md (development guidance)
├── behind_the_scenes.md (technical deep dive)
└── claude-context.md (project context)
```

## Key Features
- **No ChromaDB**: Uses NumPy arrays for vector storage
- **In-memory search**: Cosine similarity calculations
- **Cost transparency**: Shows exact OpenAI API costs per query
- **Multiple query modes**: General, specific card, compare cards
- **Category-aware calculations**: Proper handling of travel vs general spending rates
- **Improved UI**: Better example questions and fixed interaction bugs

## Architecture Evolution
- **Started as**: Supavec clone with Node.js backend + Streamlit frontend
- **Evolved to**: Pure Python modular application with organized structure
- **Current state**: Single `app.py` orchestrating three focused modules
- **Benefits**: Easier maintenance, better organization, no duplicate code