#!/usr/bin/env python3
"""
Test script to verify auto-upgrade from Flash to Pro
"""

from src.llm import LLMService
from src.embedder import EmbeddingService
from src.retriever import DocumentRetriever
from src.query_enhancer import QueryEnhancer
from app import process_query
import os

# Initialize services
api_key = os.getenv('OPENAI_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')

embedder = EmbeddingService(api_key)
llm = LLMService(api_key, gemini_key)
retriever = DocumentRetriever()
query_enhancer = QueryEnhancer()

# Load data
print('🔄 Loading documents...')
documents = retriever.load_documents_from_json('data')
embeddings, _ = embedder.generate_batch_embeddings(documents)
retriever.store_documents_and_embeddings(documents, embeddings)

# Test the auto-upgrade functionality
question = 'What are the welcome benefits for Axis Atlas?'

print('\n🔄 Testing auto-upgrade from Flash to Pro...')
result = process_query(
    question=question,
    query_mode='General Query',
    selected_cards=[],
    top_k=5,
    selected_model='gemini-1.5-flash',  # User selected Flash
    retriever=retriever,
    embedder=embedder,
    llm=llm,
    query_enhancer=query_enhancer
)

print(f'\n📊 Results:')
print(f'Answer: {result["answer"][:200]}...')
print(f'Model used: {result["llm_usage"]["model"]}')
print(f'Cost: ${result["total_cost"]:.5f}')
print(f'Response time should be ~2-3 seconds (not 80+)')