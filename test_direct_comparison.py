#!/usr/bin/env python3
"""
Test direct comparison pattern matching
"""
import re

# Test patterns from vertex_retriever.py
direct_comparison_patterns = [
    r'\bbetween\s+(\w+).*?and\s+(\w+)', 
    r'(\w+)\s+vs\s+(\w+)', 
    r'(\w+)\s+versus\s+(\w+)',
    r'compare\s+(\w+).*?and\s+(\w+)',
    r'(\w+)\s+or\s+(\w+)',
    r'(\w+)\s+better\s+than\s+(\w+)'
]

card_name_mapping = {
    'axis atlas': 'Axis Bank Atlas Credit Card',
    'atlas': 'Axis Bank Atlas Credit Card', 
    'icici epm': 'ICICI Bank Emeralde Private Metal Credit Card',
    'epm': 'ICICI Bank Emeralde Private Metal Credit Card',
    'hsbc premier': 'HSBC Premier Credit Card',
    'premier': 'HSBC Premier Credit Card',
    'hdfc infinia': 'HDFC Infinia Credit Card',
    'infinia': 'HDFC Infinia Credit Card'
}

# Test the problematic query
query_text = "Between infinia and atlas which card is better"
print(f"Original query: '{query_text}'")

enhanced_query = query_text
direct_comparison_detected = False

print(f"\n=== DIRECT COMPARISON DEBUG ===")
for pattern in direct_comparison_patterns:
    match = re.search(pattern, query_text.lower())
    print(f"Pattern '{pattern}' -> Match: {match.groups() if match else 'No match'}")
    if match:
        # Extract the two card names and map them to full names
        card1, card2 = match.groups()
        full_card1 = card_name_mapping.get(card1, card1)
        full_card2 = card_name_mapping.get(card2, card2)
        
        # Add both full card names to enhance retrieval
        enhanced_query += f" {full_card1} {full_card2} comparison benefits features rewards rates fees"
        print(f"Enhanced direct comparison query: {card1} vs {card2} -> {full_card1} vs {full_card2}")
        direct_comparison_detected = True
        break

print(f"\nFinal enhanced query: '{enhanced_query}'")
print(f"Length: {len(enhanced_query)} chars")

# Test if the issue might be in QueryEnhancer
from backend.services.query_enhancer import QueryEnhancer
enhancer = QueryEnhancer()
enhanced_by_query_enhancer, metadata = enhancer.enhance_query(query_text)

print(f"\n=== QUERY ENHANCER TEST ===")
print(f"QueryEnhancer result: '{enhanced_by_query_enhancer}'")
print(f"Metadata: {metadata}")