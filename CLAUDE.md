# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an enhanced supavec clone built for RAG/Multi-Model LLM applications to query Indian credit card data. Features ultra-low cost Gemini integration (20x cheaper), smart query preprocessing, and production-ready accuracy improvements.

## Data Structure

The project contains credit card data in JSON format in the `/data` directory:
- `axis-atlas.json` - Axis Bank Atlas credit card terms and conditions
- `icici-epm.json` - ICICI Bank credit card terms and conditions

Each JSON file contains structured data with:
- `common_terms` - Standard credit card terms like interest rates, fees, and policies
- Detailed information about finance charges, surcharge fees, cash withdrawal policies
- Reward points policies and card management rules

## Architecture

Enhanced supavec architecture with modern improvements:
- **Multi-Model Support**: OpenAI (GPT-4/3.5) + Google Gemini (Flash/Pro)
- **Smart Query Enhancement**: Category detection and preprocessing
- **Vector search**: Semantic querying of credit card data
- **RAG Pipeline**: Intelligent responses with model auto-selection
- **Cost Optimization**: 20x cost reduction with Gemini Flash
- **Calculation Accuracy**: Fixed milestone and exclusion logic

## Key Features Implemented

1. ✅ **Multi-Model AI**: Support for GPT-4, GPT-3.5, Gemini Flash, Gemini Pro
2. ✅ **Data Ingestion**: Loads credit card JSON files from `/data` directory
3. ✅ **Vector Embeddings**: OpenAI embeddings with batch processing optimization
4. ✅ **Smart Query Enhancement**: Category detection and model routing
5. ✅ **Semantic Search**: Natural language queries with keyword boosting
6. ✅ **RAG Pipeline**: Context retrieval + intelligent model selection
7. ✅ **Cost Optimization**: 60% token reduction + 20x cheaper Gemini option
8. ✅ **Calculation Accuracy**: Fixed arithmetic, milestones, exclusions

## Development Commands

### Python Application
- `pip install -r requirements.txt` - Install Python dependencies (includes Gemini support)
- `streamlit run app.py` - Run the production-ready RAG application
- `export OPENAI_API_KEY="your-key"` - Set OpenAI API key (required)
- `export GEMINI_API_KEY="your-key"` - Set Gemini API key (optional, 20x cheaper)
- Default model: **Gemini 1.5 Flash** (ultra-low cost, good accuracy)

## Data Query Examples

The system supports enhanced queries with smart preprocessing:
- **Category Detection**: "What rewards for ₹50K utility spend?" → detects utility category
- **Calculation Queries**: "For ₹7.5L yearly spend on Atlas, how many miles?" → auto-routes to better model
- **Comparisons**: "Compare cash withdrawal fees between cards" → ensures both cards discussed
- **Spend Distribution**: "Split ₹1L across rent, food, travel - which card better?" → category-wise analysis
- **Complex Calculations**: Automatically uses Gemini Pro or GPT-4 for accuracy

## Extension Points

To add new credit card data:
1. Add JSON files to the `/data` directory
2. Follow the existing structure with `common_terms` and detailed policies
3. The system should automatically detect and ingest new files
4. Update vector embeddings to include new data

## Maintenance Tasks

- keep @CLAUDE.md @README.md @behind_the_scenes.md @claude-context.md updated at all times

## Commit Guidelines

- Do not mention Claude as a contributor in commit messages