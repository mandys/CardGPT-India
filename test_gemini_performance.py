#!/usr/bin/env python3
"""
Test script to compare Gemini Flash vs Pro performance
"""

from src.llm import LLMService
from src.embedder import EmbeddingService
from src.retriever import DocumentRetriever
from src.query_enhancer import QueryEnhancer
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

# Test with both models
question = 'What transfer partners does HSBC Premier support?'

# Enhance query to get card detection
enhanced_question, metadata = query_enhancer.enhance_query(question)

# Generate query embedding
query_embedding, _ = embedder.generate_single_embedding(question)

# Search with card filter
relevant_docs = retriever.search_similar_documents(
    query_embedding=query_embedding,
    top_k=3,
    card_filter=metadata.get('card_detected'),
    boost_keywords=['transfer', 'partners', 'airlines', 'hotels', 'miles']
)

print(f'\n📊 Testing performance for: "{question}"')
print(f'Card detected: {metadata.get("card_detected")}')
print(f'Documents found: {len(relevant_docs)}')

print('\n🔥 Testing Gemini 1.5 Flash:')
answer_flash, usage_flash = llm.generate_answer(
    question=enhanced_question,
    context_documents=relevant_docs,
    card_name=metadata.get('card_detected'),
    model_choice='gemini-1.5-flash',
    max_tokens=1500
)

print('\n🚀 Testing Gemini 1.5 Pro:')
answer_pro, usage_pro = llm.generate_answer(
    question=enhanced_question,
    context_documents=relevant_docs,
    card_name=metadata.get('card_detected'),
    model_choice='gemini-1.5-pro',
    max_tokens=1500
)

print('\n📈 Results Summary:')
print(f'Flash cost: ${usage_flash.get("cost", 0):.5f}')
print(f'Pro cost: ${usage_pro.get("cost", 0):.5f}')
print(f'Flash tokens: {usage_flash.get("total_tokens", 0)}')
print(f'Pro tokens: {usage_pro.get("total_tokens", 0)}')

print('\n🎯 Flash Answer:')
print(answer_flash)

print('\n🎯 Pro Answer:')
print(answer_pro)