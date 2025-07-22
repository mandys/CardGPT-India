#!/usr/bin/env python3
"""
Test the real search logic that was failing
"""
from services.query_enhancer import QueryEnhancer

# Test the exact query that failed
question = 'Compare Axis Atlas, ICICI EPM for: "I have monthly spends of 1L, split as 20% Rent, 10% Utility, 20% Grocery, 10% Uber, 20% on Food and Eating Out, 20% on Buying Gift cards... which card is bettter is which spend? How should i split my spending?"'

print(f"📝 Original question ({len(question)} chars):\n{question}\n")

# Step 1: Query Enhancement
enhancer = QueryEnhancer()
enhanced_question, metadata = enhancer.enhance_query(question)
print(f"🔧 Enhanced question ({len(enhanced_question)} chars):\n{enhanced_question}\n")

# Step 2: Chat Stream Logic - simulate what happens in chat_stream.py
question_for_search = enhanced_question

# Check if it's a comparison query
if "compare" in question_for_search.lower() and any(card in question_for_search.lower() for card in ["atlas", "icici", "epm", "hsbc", "premier"]):
    print("🔍 Detected as comparison query")
    
    # Boost search with actual card names
    card_names_to_boost = []
    question_lower = question_for_search.lower()
    if any(pattern in question_lower for pattern in ["axis", "atlas"]):
        card_names_to_boost.append("Axis Bank Atlas Credit Card")
    if any(pattern in question_lower for pattern in ["icici", "epm", "emeralde"]):
        card_names_to_boost.append("ICICI Bank Emeralde Private Metal Credit Card")
    if any(pattern in question_lower for pattern in ["hsbc", "premier"]):
        card_names_to_boost.append("HSBC Premier Credit Card")
        
    print(f"🏷️  Cards to boost: {card_names_to_boost}")
    
    # Add card names if query isn't too long
    if card_names_to_boost and len(question_for_search) < 200:
        question_for_search += f" {' '.join(card_names_to_boost[:2])}"
        print(f"✅ Added card names (query now {len(question_for_search)} chars)")
    else:
        print(f"⏭️  Skipped adding card names (query too long: {len(question_for_search)} >= 200)")

# Step 3: Milestone enhancement check
if (metadata.get('is_calculation_query', False) and 
    not ("compare" in question_for_search.lower() and len(question_for_search) > 100)):
    question_for_search += " milestone spend threshold bonus benefits"
    print(f"✅ Added milestone keywords")
else:
    print(f"⏭️  Skipped milestone keywords (complex comparison, {len(question_for_search)} > 100)")

# Step 4: Ultra-complex query simplification
if len(question_for_search) > 200 and "compare" in question_for_search.lower():
    print(f"🚨 Ultra-complex query detected ({len(question_for_search)} chars), simplifying...")
    
    # Extract just the card names and spending categories for search
    simplified_query = "compare cards spending rewards "
    question_lower = question_for_search.lower()
    
    # Add card names
    if any(pattern in question_lower for pattern in ["axis", "atlas"]):
        simplified_query += "Atlas "
    if any(pattern in question_lower for pattern in ["icici", "epm"]):
        simplified_query += "EPM "
    if any(pattern in question_lower for pattern in ["hsbc", "premier"]):
        simplified_query += "Premier "
    
    # Add key spending categories mentioned
    if "rent" in question_lower:
        simplified_query += "rent "
    if "utility" in question_lower:
        simplified_query += "utility "
    if "grocery" in question_lower:
        simplified_query += "grocery "
    if "food" in question_lower:
        simplified_query += "dining "
    if "gift" in question_lower:
        simplified_query += "gift "
        
    question_for_search = simplified_query.strip()
    print(f"✅ Simplified to: {question_for_search} ({len(question_for_search)} chars)")

print(f"\n🔍 Final search query ({len(question_for_search)} chars):")
print(question_for_search)

print(f"\n📊 Metadata: {metadata}")