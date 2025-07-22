#!/usr/bin/env python3
"""
Test query enhancement for complex comparison queries
"""
from services.query_enhancer import QueryEnhancer

# Test the problematic query
query = 'Compare Axis Atlas, ICICI EPM for: "I have monthly spends of 1L, split as 20% Rent, 10% Utility, 20% Grocery, 10% Uber, 20% on Food and Eating Out, 20% on Buying Gift cards... which card is bettter is which spend? How should i split my spending?"'

enhancer = QueryEnhancer()
enhanced_query, metadata = enhancer.enhance_query(query)

print(f"Original query length: {len(query)}")
print(f"Enhanced query length: {len(enhanced_query)}")
print(f"Metadata: {metadata}")
print(f"\nEnhanced query:")
print(enhanced_query[:300] + "..." if len(enhanced_query) > 300 else enhanced_query)

# Simulate what chat_stream.py would do
question = enhanced_query

# Check if it would add card names
card_names_to_boost = []
question_lower = question.lower()
if any(pattern in question_lower for pattern in ["axis", "atlas"]):
    card_names_to_boost.append("Axis Bank Atlas Credit Card")
if any(pattern in question_lower for pattern in ["icici", "epm", "emeralde"]):
    card_names_to_boost.append("ICICI Bank Emeralde Private Metal Credit Card")

if card_names_to_boost and len(question) < 200:
    question += f" {' '.join(card_names_to_boost[:2])}"
    print(f"\nAfter adding card names: {len(question)} chars")

# Check milestone addition logic
if (metadata.get('is_calculation_query', False) and 
    not ("compare" in question.lower() and len(question) > 100)):
    question += " milestone spend threshold bonus benefits"
    print(f"Would add milestones: YES")
else:
    print(f"Would add milestones: NO (complex comparison)")

print(f"\nFinal search query length: {len(question)}")
print(f"Final query: {question}")