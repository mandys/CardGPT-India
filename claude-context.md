# Claude Context - Supavec Clone Project

## Project Overview
A modular RAG (Retrieval-Augmented Generation) application for querying Indian credit card terms and conditions. Built as a clone of supavec with better organization and cost tracking.

## Key Architecture Changes
- **Refactored from monolithic** `streamlit_standalone.py` to modular structure
- **Four main modules**: embedder.py, llm.py, retriever.py, app.py
- **Improved calculation logic** for rewards/miles (base rate + milestone bonuses)
- **Token usage tracking** and cost optimization features

## Current Working Status
✅ **Functional**: Both modular (`app.py`) and legacy (`streamlit_standalone.py`) versions work
✅ **Data Processing**: Handles both `common_terms` and `card` sections from JSON files
✅ **Cost Tracking**: Real-time token usage and pricing display
✅ **Model Selection**: GPT-4 vs GPT-3.5-turbo cost optimization

## Recent Bug Fixes
- Fixed miles calculation issue: Now correctly combines base earning rate + milestone bonuses
- Enhanced prompts to force step-by-step calculations
- Added keyword boosting for spend-related queries to ensure retrieval of both reward and milestone data

## File Structure
```
├── app.py (new modular version)
├── streamlit_standalone.py (legacy working version)  
├── src/
│   ├── embedder.py (OpenAI embeddings)
│   ├── llm.py (GPT-4/3.5 responses)
│   ├── retriever.py (vector search)
├── data/ (credit card JSON files)
├── requirements.txt
└── README.md (updated with modular docs)
```

## Key Features
- **No ChromaDB**: Uses NumPy arrays for vector storage
- **In-memory search**: Cosine similarity calculations
- **Cost transparency**: Shows exact OpenAI API costs per query
- **Multiple query modes**: General, specific card, compare cards
- **Keyword boosting**: Better retrieval for calculation queries

## Next Steps (pending)
- Initialize git repository
- Commit with proper .gitignore
- Test modular version thoroughly