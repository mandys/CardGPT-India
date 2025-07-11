# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a supavec clone built for RAG/OpenAI/LLM applications to query Indian credit card data. The project is designed to be extensible for loading multiple credit card JSON files and performing intelligent queries on the data.

## Data Structure

The project contains credit card data in JSON format in the `/data` directory:
- `axis-atlas.json` - Axis Bank Atlas credit card terms and conditions
- `icici-epm.json` - ICICI Bank credit card terms and conditions

Each JSON file contains structured data with:
- `common_terms` - Standard credit card terms like interest rates, fees, and policies
- Detailed information about finance charges, surcharge fees, cash withdrawal policies
- Reward points policies and card management rules

## Architecture

Based on the supavec project architecture, this clone should implement:
- Vector search capabilities for semantic querying of credit card data
- RAG (Retrieval-Augmented Generation) pipeline for intelligent responses
- API endpoints for querying credit card information
- Extensible data loading system for additional JSON files

## Key Features to Implement

1. **Data Ingestion**: Load and process credit card JSON files from the `/data` directory
2. **Vector Embeddings**: Create embeddings for credit card terms and conditions
3. **Semantic Search**: Enable natural language queries about credit card features
4. **RAG Pipeline**: Combine retrieved information with LLM responses
5. **Extensibility**: Easy addition of new credit card data files

## Development Commands

### Python Application
- `pip install -r requirements.txt` - Install Python dependencies
- `streamlit run app.py` - Run the modular RAG application
- `export OPENAI_API_KEY="your-key"` - Set OpenAI API key
- `python -m pytest tests/` - Run tests (if implemented)

## Data Query Examples

The system should support queries like:
- "What are the interest rates for Axis Atlas card?"
- "Compare cash withdrawal fees between ICICI and Axis cards"
- "What are the reward redemption policies?"
- "What surcharge fees apply to international transactions?"

## Extension Points

To add new credit card data:
1. Add JSON files to the `/data` directory
2. Follow the existing structure with `common_terms` and detailed policies
3. The system should automatically detect and ingest new files
4. Update vector embeddings to include new data

## Maintenance Tasks

- keep @CLAUDE.md @README.md @behind_the_scenes.md @claude-context.md updated at all times